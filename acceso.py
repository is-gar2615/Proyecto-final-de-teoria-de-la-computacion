from datetime import datetime, timedelta


class ControlAcceso:
    """Controla y valida los accesos de los clientes al gimnasio.

    Gestiona el bloqueo temporal de clientes tras intentos fallidos,
    verifica el estado de la membresía y registra cada intento en la BD.

    Attributes:
        db (BaseDeDatos): Conexión a la base de datos.
        gestor_clientes (GestorClientes): Para obtener datos de clientes.
        bloqueos (dict): Almacena IDs de clientes bloqueados con timestamp.
    """

    def __init__(self, db, gestor_clientes):
        self.db = db
        self.gestor_clientes = gestor_clientes
        self.bloqueos = {}

    def validar_acceso(self, id_cliente):
        """Valida si un cliente puede ingresar al gimnasio.

            Comprueba si el ID es válido, si el cliente está bloqueado,
            si existe y el estado de su membresía. Devuelve un diccionario
            con el resultado y un mensaje.

            Args:
                id_cliente (int): Identificador único del cliente.

            Returns:
                dict: Contiene las claves:
                    - "acceso" (str): "PERMITIDO", "PERMITIDO_CON_ADVERTENCIA" o "DENEGADO".
                    - "mensaje" (str): Texto explicativo.
                    - "bloqueado" (bool): True si el cliente está bloqueado.
            """

        if not isinstance(id_cliente, int) or id_cliente <= 0:
            return {
                "acceso": "DENEGADO",
                "mensaje": "ID de cliente inválido",
                "bloqueado": False
            }

        if self.esta_bloqueado(id_cliente):
            self._registrar_intento(
                id_cliente,
                "DENEGADO",
                "Cliente bloqueado temporalmente"
            )

            return {
                "acceso": "DENEGADO",
                "mensaje": "Cliente bloqueado temporalmente. Espere 1 minuto.",
                "bloqueado": True
            }

        cliente = self.verificar_existencia_cliente(id_cliente)

        if not cliente:
            self._registrar_intento(
                id_cliente,
                "FALLIDO",
                "Cliente no encontrado"
            )

            return {
                "acceso": "DENEGADO",
                "mensaje": "Cliente no encontrado",
                "bloqueado": False
            }

        estado = self.verificar_estado_membresia(cliente)

        if estado == "Vigente":
            self.bloquear_cliente(id_cliente)

            self._registrar_intento(
                id_cliente,
                "EXITOSO",
                "Acceso permitido"
            )

            return {
                "acceso": "PERMITIDO",
                "mensaje": "✓ Acceso permitido. Membresía vigente.",
                "bloqueado": False
            }

        elif estado == "Próxima a vencer":
            self.bloquear_cliente(id_cliente)

            dias = self.calcular_dias_restantes(cliente)

            self._registrar_intento(
                id_cliente,
                "EXITOSO",
                f"Acceso con advertencia. Vence en {dias} días"
            )

            return {
                "acceso": "PERMITIDO_CON_ADVERTENCIA",
                "mensaje": f"⚠ Acceso permitido. Su membresía vence en {dias} días.",
                "bloqueado": False
            }

        else:
            self._registrar_intento(
                id_cliente,
                "DENEGADO",
                "Membresía vencida"
            )

            return {
                "acceso": "DENEGADO",
                "mensaje": "✗ Acceso denegado. Membresía vencida.",
                "bloqueado": False
            }

    def verificar_existencia_cliente(self, id_cliente):
        """Verifica si un cliente existe en el sistema.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            Cliente or None: Objeto Cliente si existe, None en caso contrario.
       """
        return self.gestor_clientes.buscar_cliente(id_cliente)

    def verificar_estado_membresia(self, cliente):
        """Obtiene el estado textual de la membresía de un cliente.

            Args:
                cliente (Cliente): Objeto cliente.

            Returns:
                str: "Vigente", "Próxima a vencer" o "Vencida".
            """

        if not cliente or not cliente.membresia:
            return "Vencida"

        return cliente.membresia.estado()

    def calcular_dias_restantes(self, cliente):
        """Calcula los días que faltan para el vencimiento de la membresía.

            Args:
                cliente (Cliente): Objeto cliente.

            Returns:
                int: Días restantes (puede ser negativo si ya venció).
            """

        if not cliente or not cliente.membresia:
            return 0

        return (cliente.membresia.fecha_vencimiento - datetime.now().date()).days

    def bloquear_cliente(self, id_cliente):
        """Bloquea a un cliente por 1 minuto.

            Registra el momento actual en el diccionario de bloqueos.

        Args:
            id_cliente (int): ID del cliente a bloquear.
        """
        self.bloqueos[id_cliente] = datetime.now()

    def esta_bloqueado(self, id_cliente):
        """Comprueba si un cliente está actualmente bloqueado.

            Si el tiempo de bloqueo supera 1 minuto, lo desbloquea automáticamente.

            Args:
                id_cliente (int): ID del cliente.

            Returns:
                bool: True si sigue bloqueado, False en caso contrario.
            """

        if id_cliente in self.bloqueos:
            tiempo_transcurrido = datetime.now() - self.bloqueos[id_cliente]

            if tiempo_transcurrido < timedelta(minutes=1):
                return True

            del self.bloqueos[id_cliente]

        return False

    def _registrar_intento(self, id_cliente, resultado, descripcion):
        """Registra un intento de acceso en la base de datos y en auditoría.

    Es un método interno (prefijo _).

    Args:
        id_cliente (int): ID del cliente.
        resultado (str): "EXITOSO", "FALLIDO" o "DENEGADO".
        descripcion (str): Texto adicional del resultado.
    """

        ahora = datetime.now()

        query = """INSERT INTO accesos 
                  (id_cliente, fecha_hora, resultado, descripcion) 
                  VALUES (?, ?, ?, ?)"""

        self.db.ejecutar(query, (
            id_cliente,
            ahora,
            resultado,
            descripcion
        ))

        self.db.commit()

        query_aud = """INSERT INTO auditoria 
                      (tipo_operacion, tabla_afectada, trabajador_id, fecha_hora, descripcion) 
                      VALUES (?, ?, ?, ?, ?)"""

        self.db.ejecutar(query_aud, (
            "INSERT",
            "accesos",
            None,
            ahora,
            f"Intento de acceso cliente ID {id_cliente}: {resultado}"
        ))

        self.db.commit()