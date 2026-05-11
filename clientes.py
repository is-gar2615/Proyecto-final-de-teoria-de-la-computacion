import csv
from datetime import datetime


class Membresia:
    """Representa la membresía de un cliente"""

    def __init__(self, fecha_inicio, fecha_vencimiento):
        self.fecha_inicio = fecha_inicio
        self.fecha_vencimiento = fecha_vencimiento

    def esta_vigente(self):
        """Determina si la membresía está vigente"""
        return self.fecha_vencimiento >= datetime.now().date()

    def esta_proxima_a_vencer(self):
        """Determina si vence en los próximos 3 días"""
        dias = (self.fecha_vencimiento - datetime.now().date()).days
        return 0 <= dias <= 3

    def estado(self):
        """Retorna el estado de la membresía"""
        if not self.esta_vigente():
            return "Vencida"
        elif self.esta_proxima_a_vencer():
            return "Próxima a vencer"
        return "Vigente"


class Cliente:
    """Representa un cliente del gimnasio"""

    def __init__(self, id=None, nombre=None, membresia=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.membresia = membresia
        self.activo = activo


class GestorClientes:
    """Gestiona clientes y membresías"""

    def __init__(self, db):
        self.db = db

    def generar_id(self):
        """Genera un ID único"""
        query = "SELECT MAX(id) FROM clientes"
        resultado = self.db.consultar(query)
        ultimo_id = resultado[0][0] if resultado[0][0] else 0
        return ultimo_id + 1

    def validar_fechas(self, fecha_inicio, fecha_vencimiento):
        """Valida formato y coherencia de fechas"""
        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()

            if vencimiento < inicio:
                raise Exception("La fecha de vencimiento no puede ser anterior al inicio")

            return inicio, vencimiento

        except ValueError:
            raise Exception("Formato de fecha inválido. Use YYYY-MM-DD")

    def registrar_cliente(self, nombre, fecha_inicio, fecha_vencimiento, trabajador_responsable):
        """Registra un nuevo cliente"""

        nombre = nombre.strip()

        if not nombre:
            raise Exception("El nombre es obligatorio")

        inicio, vencimiento = self.validar_fechas(fecha_inicio, fecha_vencimiento)

        id_cliente = self.generar_id()

        query_cliente = "INSERT INTO clientes (id, nombre, activo) VALUES (?, ?, ?)"
        self.db.ejecutar(query_cliente, (id_cliente, nombre, 1))

        query_membresia = """INSERT INTO membresias (id_cliente, fecha_inicio, fecha_vencimiento) 
                           VALUES (?, ?, ?)"""

        self.db.ejecutar(query_membresia, (id_cliente, fecha_inicio, fecha_vencimiento))
        self.db.commit()

        self._registrar_auditoria(
            "INSERT",
            "clientes",
            trabajador_responsable.id,
            f"Registro de cliente: {nombre} (ID: {id_cliente})"
        )

        membresia_obj = Membresia(inicio, vencimiento)

        return Cliente(id_cliente, nombre, membresia_obj, True)

    def buscar_cliente(self, id_cliente):
        """Busca cliente por ID"""

        query = """
            SELECT c.id, c.nombre, m.fecha_inicio, m.fecha_vencimiento, c.activo 
            FROM clientes c 
            LEFT JOIN membresias m ON c.id = m.id_cliente 
            WHERE c.id = ?
        """

        resultado = self.db.consultar(query, (id_cliente,))

        if not resultado:
            return None

        data = resultado[0]

        fecha_inicio = datetime.strptime(data[2], '%Y-%m-%d').date() if data[2] else None
        fecha_vencimiento = datetime.strptime(data[3], '%Y-%m-%d').date() if data[3] else None

        membresia = Membresia(fecha_inicio, fecha_vencimiento) if fecha_inicio else None

        return Cliente(data[0], data[1], membresia, data[4])

    def actualizar_cliente(self, id_cliente, nombre=None, fecha_inicio=None,
                           fecha_vencimiento=None, trabajador_responsable=None):
        """Actualiza cliente"""

        cliente = self.buscar_cliente(id_cliente)

        if not cliente:
            raise Exception("Cliente no encontrado")

        if nombre and nombre.strip():
            query = "UPDATE clientes SET nombre = ? WHERE id = ?"
            self.db.ejecutar(query, (nombre.strip(), id_cliente))

        if fecha_inicio or fecha_vencimiento:
            if not (fecha_inicio and fecha_vencimiento):
                raise Exception("Debe proporcionar ambas fechas")

            self.validar_fechas(fecha_inicio, fecha_vencimiento)

            query = """UPDATE membresias 
                      SET fecha_inicio = ?, fecha_vencimiento = ? 
                      WHERE id_cliente = ?"""

            self.db.ejecutar(query, (fecha_inicio, fecha_vencimiento, id_cliente))

        self.db.commit()

        if trabajador_responsable:
            self._registrar_auditoria(
                "UPDATE",
                "clientes",
                trabajador_responsable.id,
                f"Actualización de cliente ID {id_cliente}"
            )

    def eliminar_cliente(self, id_cliente, trabajador_responsable):
        """Elimina cliente"""

        cliente = self.buscar_cliente(id_cliente)

        if not cliente:
            raise Exception("Cliente no encontrado")

        query_membresia = "DELETE FROM membresias WHERE id_cliente = ?"
        self.db.ejecutar(query_membresia, (id_cliente,))

        query_cliente = "DELETE FROM clientes WHERE id = ?"
        self.db.ejecutar(query_cliente, (id_cliente,))

        self.db.commit()

        self._registrar_auditoria(
            "DELETE",
            "clientes",
            trabajador_responsable.id,
            f"Eliminación de cliente ID {id_cliente}"
        )

    def listar_clientes(self):
        """Lista clientes activos"""

        query = """
            SELECT c.id, c.nombre, m.fecha_inicio, m.fecha_vencimiento 
            FROM clientes c 
            LEFT JOIN membresias m ON c.id = m.id_cliente 
            WHERE c.activo = 1
        """

        return self.db.consultar(query)

    def exportar_csv(self, nombre_archivo="clientes.csv"):
        """Exporta clientes a CSV"""

        clientes = self.listar_clientes()

        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(['ID', 'Nombre', 'Fecha Inicio', 'Fecha Vencimiento', 'Estado'])

            for c in clientes:
                cliente = self.buscar_cliente(c[0])
                estado = cliente.membresia.estado() if cliente.membresia else "Sin membresía"

                writer.writerow([
                    c[0],
                    c[1],
                    c[2],
                    c[3],
                    estado
                ])

    def _registrar_auditoria(self, tipo, tabla, trabajador_id, descripcion):
        """Registra auditoría"""

        query = """INSERT INTO auditoria 
                  (tipo_operacion, tabla_afectada, trabajador_id, fecha_hora, descripcion) 
                  VALUES (?, ?, ?, ?, ?)"""

        self.db.ejecutar(query, (
            tipo,
            tabla,
            trabajador_id,
            datetime.now(),
            descripcion
        ))

        self.db.commit()