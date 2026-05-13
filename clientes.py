import csv
from datetime import datetime


class Membresia:
    """Representa la membresía de un cliente con fechas de inicio y vencimiento.

        Permite consultar si está vigente, si está próxima a vencer (3 días)
        y obtener un estado textual.

        Attributes:
            fecha_inicio (date): Fecha de inicio de la membresía.
            fecha_vencimiento (date): Fecha de vencimiento.
        """

    def __init__(self, fecha_inicio, fecha_vencimiento):
        self.fecha_inicio = fecha_inicio
        self.fecha_vencimiento = fecha_vencimiento

    def esta_vigente(self):
        """Indica si la membresía aún es válida.

            Returns:
                bool: True si la fecha de vencimiento es hoy o posterior.
            """
        return self.fecha_vencimiento >= datetime.now().date()

    def esta_proxima_a_vencer(self):
        """Indica si la membresía vence en los próximos 3 días.

            Returns:
                bool: True si faltan 0, 1, 2 o 3 días para vencer.
            """
        dias = (self.fecha_vencimiento - datetime.now().date()).days
        return 0 <= dias <= 3

    def estado(self):
        """Retorna el estado de la membresía como texto.

            Returns:
                str: "Vigente", "Próxima a vencer" o "Vencida".
            """
        if not self.esta_vigente():
            return "Vencida"
        elif self.esta_proxima_a_vencer():
            return "Próxima a vencer"
        return "Vigente"


class Cliente:
    """Representa un cliente del gimnasio con sus datos personales y membresía.

        Attributes:
            id (int): Identificador único.
            nombre (str): Nombre completo.
            membresia (Membresia or None): Objeto membresía asociada.
            activo (bool): Estado del cliente (activo/inactivo).
        """

    def __init__(self, id=None, nombre=None, membresia=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.membresia = membresia
        self.activo = activo


class GestorClientes:
    """Gestiona las operaciones CRUD de clientes y membresías.

        Interactúa con la base de datos para registrar, buscar,
        actualizar, eliminar, listar y exportar clientes.

        Attributes:
            db (BaseDeDatos): Conexión a la base de datos.
        """

    def __init__(self, db):
        self.db = db

    def generar_id(self):
        """Genera un nuevo ID autoincremental para un cliente.

            Returns:
                int: Siguiente ID disponible basado en el máximo existente + 1.
            """
        query = "SELECT MAX(id) FROM clientes"
        resultado = self.db.consultar(query)
        ultimo_id = resultado[0][0] if resultado[0][0] else 0
        return ultimo_id + 1

    def validar_fechas(self, fecha_inicio, fecha_vencimiento):
        """Valida el formato y coherencia de las fechas de membresía.

         Args:
             fecha_inicio (str): Fecha en formato YYYY-MM-DD.
             fecha_vencimiento (str): Fecha en formato YYYY-MM-DD.

         Returns:
             tuple: (inicio_date, vencimiento_date) como objetos date.

         Raises:
            Exception: Si el formato es inválido o la fecha de vencimiento es anterior al inicio.
        """
        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()

            if vencimiento < inicio:
                raise Exception("La fecha de vencimiento no puede ser anterior al inicio")

            return inicio, vencimiento

        except ValueError:
            raise Exception("Formato de fecha inválido. Use YYYY-MM-DD")

    def registrar_cliente(self, nombre, fecha_inicio, fecha_vencimiento, trabajador_responsable):
        """Registra un nuevo cliente y su membresía en la base de datos.

            Args:
                nombre (str): Nombre del cliente.
                fecha_inicio (str): Fecha de inicio (YYYY-MM-DD).
                fecha_vencimiento (str): Fecha de vencimiento (YYYY-MM-DD).
                trabajador_responsable (Usuario): Usuario que realiza la operación.

            Returns:
                Cliente: Objeto Cliente recién creado.

            Raises:
                Exception: Si el nombre está vacío o las fechas son inválidas.
            """

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
        """Busca un cliente por su ID y reconstruye su objeto con membresía.

            Args:
                id_cliente (int): ID del cliente.

            Returns:
                Cliente or None: Objeto Cliente si existe, None en caso contrario.
            """

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
        """Actualiza los datos de un cliente existente.

            Puede cambiar el nombre y/o las fechas de membresía.

            Args:
                id_cliente (int): ID del cliente a actualizar.
                nombre (str, optional): Nuevo nombre (si se proporciona).
                fecha_inicio (str, optional): Nueva fecha de inicio (requiere fecha_vencimiento).
                fecha_vencimiento (str, optional): Nueva fecha de vencimiento (requiere fecha_inicio).
                trabajador_responsable (Usuario, optional): Usuario que realiza la operación.

            Raises:
                Exception: Si el cliente no existe, o si se proporciona solo una de las fechas.
            """

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
        """Elimina un cliente y toda su información relacionada (accesos, membresía).

            Args:
                id_cliente (int): ID del cliente a eliminar.
                trabajador_responsable (Usuario): Usuario que realiza la operación.
            """

        query_accesos = "DELETE FROM accesos WHERE id_cliente = ?"
        self.db.ejecutar(query_accesos, (id_cliente,))

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
        """Lista los clientes activos con sus datos básicos.

            Returns:
                list of tuple: Cada tupla contiene (id, nombre, fecha_inicio, fecha_vencimiento).
            """

        query = """
            SELECT c.id, c.nombre, m.fecha_inicio, m.fecha_vencimiento 
            FROM clientes c 
            LEFT JOIN membresias m ON c.id = m.id_cliente 
            WHERE c.activo = 1
        """

        return self.db.consultar(query)

    def exportar_csv(self, nombre_archivo="clientes.csv"):
        """Exporta la lista de clientes a un archivo CSV.

            Incluye columnas: ID, Nombre, Fecha Inicio, Fecha Vencimiento, Estado.

            Args:
                nombre_archivo (str): Nombre del archivo de salida.
            """

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
        """Registra una operación en la tabla de auditoría.

            Args:
                tipo (str): Tipo de operación (INSERT, UPDATE, DELETE).
                tabla (str): Nombre de la tabla afectada.
                trabajador_id (int): ID del trabajador que ejecuta la operación.
                descripcion (str): Detalle de la operación.
            """

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