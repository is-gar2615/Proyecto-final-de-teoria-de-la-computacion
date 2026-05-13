from datetime import datetime

class Usuario:
    """Representa un trabajador del sistema con credenciales y rol.

    Attributes:
        id (int): Identificador único.
        nombre (str): Nombre completo.
        username (str): Nombre de usuario para login.
        password (str): Contraseña (sin encriptar en este ejemplo).
        rol (str): "admin" o "empleado".
        activo (bool): Estado del usuario (activo/inactivo).
    """

    def __init__(self, id=None, nombre=None, username=None, password=None, rol=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.username = username
        self.password = password
        self.rol = rol
        self.activo = activo


class GestorUsuarios:
    """Gestiona los trabajadores del sistema (CRUD y login).

    Attributes:
        db (BaseDeDatos): Conexión a la base de datos.
    """

    def __init__(self, db):
        self.db = db

    def crear_admin_defecto(self):
        """Crea un usuario administrador por defecto (admin/admin123) si no existe."""
        if not self.username_existe("admin"):
            query = """INSERT INTO trabajadores (nombre, username, password, rol, activo) 
                      VALUES (?, ?, ?, ?, ?)"""
            self.db.ejecutar(query, ("Administrador", "admin", "admin123", "admin", 1))
            self.db.commit()
            print("✓ Usuario administrador por defecto creado")

    def generar_id(self):
        """Genera un nuevo ID autoincremental para un trabajador.

            Returns:
                 int: Siguiente ID disponible.
        """
        query = "SELECT MAX(id) FROM trabajadores"
        resultado = self.db.consultar(query)
        ultimo_id = resultado[0][0] if resultado[0][0] else 0
        return ultimo_id + 1

    def username_existe(self, username):
        """Verifica si un nombre de usuario ya está registrado.

           Returns:
               bool: True si ya existe.
        """
        query = "SELECT COUNT(*) FROM trabajadores WHERE username = ?"
        resultado = self.db.consultar(query, (username,))
        return resultado[0][0] > 0

    def usuario_existe(self, id_usuario):
        """Verifica si existe un trabajador con el ID dado.

           Returns:
              bool: True si existe.
        """
        query = "SELECT COUNT(*) FROM trabajadores WHERE id = ?"
        resultado = self.db.consultar(query, (id_usuario,))
        return resultado[0][0] > 0

    def registrar_usuario(self, nombre, username, password, rol, trabajador_responsable):
        """Registra un nuevo usuario en el sistema.

           Args:
             nombre (str): Nombre completo.
             username (str): Nombre de usuario único.
             password (str): Contraseña.
             rol (str): "admin" o "empleado".
             trabajador_responsable (Usuario): Usuario que realiza la operación.

          Returns:
             Usuario: Objeto del nuevo usuario.

          Raises:
            Exception: Si faltan datos, username duplicado, rol inválido o permisos insuficientes.
        """

        nombre = nombre.strip()
        username = username.strip()
        password = password.strip()

        if not nombre or not username or not password:
            raise Exception("Todos los campos son obligatorios")

        if self.username_existe(username):
            raise Exception("El nombre de usuario ya existe")

        if rol not in ['admin', 'empleado']:
            raise Exception("Rol no válido")

        if rol == 'admin' and trabajador_responsable.rol != 'admin':
            raise Exception("Solo administradores pueden crear otros administradores")

        id = self.generar_id()

        query = """INSERT INTO trabajadores (id, nombre, username, password, rol, activo) 
                  VALUES (?, ?, ?, ?, ?, ?)"""

        self.db.ejecutar(query, (id, nombre, username, password, rol, 1))
        self.db.commit()

        self._registrar_auditoria(
            "INSERT",
            "trabajadores",
            trabajador_responsable.id,
            f"Registro de usuario: {username} (rol: {rol})"
        )

        return Usuario(id, nombre, username, password, rol, True)

    def login(self, username, password):
        """Autentica un usuario por username y contraseña.

            Args:
                username (str): Nombre de usuario.
                password (str): Contraseña.

            Returns:
                Usuario or None: Objeto Usuario si las credenciales son correctas y está activo.
            """

        username = username.strip()
        password = password.strip()

        query = "SELECT * FROM trabajadores WHERE username = ? AND password = ? AND activo = 1"
        resultado = self.db.consultar(query, (username, password))

        if not resultado:
            return None

        data = resultado[0]
        return Usuario(data[0], data[1], data[2], data[3], data[4], data[5])

    def actualizar_usuario(self, id_usuario, nombre=None, password=None, trabajador_responsable=None):
        """Actualiza el nombre y/o contraseña de un usuario.

            Args:
                id_usuario (int): ID del usuario a modificar.
                nombre (str, optional): Nuevo nombre (si se proporciona).
                password (str, optional): Nueva contraseña (si se proporciona).
                trabajador_responsable (Usuario, optional): Usuario que realiza la operación.

            Raises:
                Exception: Si el usuario no existe o no hay datos para actualizar.
            """

        if not self.usuario_existe(id_usuario):
            raise Exception("Usuario no encontrado")

        updates = []
        params = []

        if nombre and nombre.strip():
            updates.append("nombre = ?")
            params.append(nombre.strip())

        if password and password.strip():
            updates.append("password = ?")
            params.append(password.strip())

        if not updates:
            raise Exception("No hay datos para actualizar")

        params.append(id_usuario)

        query = f"UPDATE trabajadores SET {', '.join(updates)} WHERE id = ?"
        self.db.ejecutar(query, tuple(params))
        self.db.commit()

        if trabajador_responsable:
            self._registrar_auditoria(
                "UPDATE",
                "trabajadores",
                trabajador_responsable.id,
                f"Actualización de usuario ID {id_usuario}"
            )

    def eliminar_usuario(self, id_usuario, trabajador_responsable):
        """Elimina un usuario (solo empleados, no administradores, no a sí mismo).

            Args:
                id_usuario (int): ID del usuario a eliminar.
                trabajador_responsable (Usuario): Usuario que realiza la operación.

            Raises:
                Exception: Si el usuario no existe, es admin, o se intenta eliminar a sí mismo.
            """

        if not self.usuario_existe(id_usuario):
            raise Exception("Usuario no encontrado")

        if id_usuario == trabajador_responsable.id:
            raise Exception("No puedes eliminar tu propio usuario")

        query_validacion = "SELECT rol FROM trabajadores WHERE id = ?"
        resultado = self.db.consultar(query_validacion, (id_usuario,))

        if resultado[0][0] == 'admin':
            raise Exception("No se puede eliminar un administrador")

        query = "DELETE FROM trabajadores WHERE id = ?"
        self.db.ejecutar(query, (id_usuario,))
        self.db.commit()

        self._registrar_auditoria(
            "DELETE",
            "trabajadores",
            trabajador_responsable.id,
            f"Eliminación de usuario ID {id_usuario}"
        )

    def listar_usuarios(self):
        """Lista los usuarios activos con sus datos básicos.

            Returns:
                list of tuple: (id, nombre, username, rol)
         """
        query = "SELECT id, nombre, username, rol FROM trabajadores WHERE activo = 1"
        return self.db.consultar(query)

    def _registrar_auditoria(self, tipo, tabla, trabajador_id, descripcion):
        """Registra una operación en la tabla de auditoría.

            Args:
                tipo (str): Tipo de operación (INSERT, UPDATE, DELETE).
                tabla (str): Tabla afectada.
                trabajador_id (int): ID del trabajador responsable.
                descripcion (str): Detalle.
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