import sqlite3
from datetime import datetime

class Usuario:
    def __init__(self, id=None, nombre=None, username=None, password=None, rol=None, activo=True):
        self.id = id
        self.nombre = nombre
        self.username = username
        self.password = password
        self.rol = rol
        self.activo = activo

class GestorUsuarios:
    def __init__(self, db):
        self.db = db
    
    def crear_admin_defecto(self):
        """Crea el usuario administrador por defecto si no existe"""
        if not self.username_existe("admin"):
            query = """INSERT INTO trabajadores (nombre, username, password, rol, activo) 
                      VALUES (?, ?, ?, ?, ?)"""
            self.db.ejecutar(query, ("Administrador", "admin", "admin123", "admin", 1))
            self.db.commit()
            print("✓ Usuario administrador por defecto creado")
    
    def generar_id(self):
        """Genera un ID único para el trabajador"""
        query = "SELECT MAX(id) FROM trabajadores"
        resultado = self.db.consultar(query)
        ultimo_id = resultado[0][0] if resultado[0][0] else 0
        return ultimo_id + 1
    
    def username_existe(self, username):
        """Verifica si un nombre de usuario ya existe"""
        query = "SELECT COUNT(*) FROM trabajadores WHERE username = ?"
        resultado = self.db.consultar(query, (username,))
        return resultado[0][0] > 0
    
    def registrar_usuario(self, nombre, username, password, rol, trabajador_responsable):
        """Registra un nuevo usuario"""
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
        
        self._registrar_auditoria("INSERT", "trabajadores", trabajador_responsable.id, 
                                 f"Registro de usuario: {username} (rol: {rol})")
        
        return Usuario(id, nombre, username, password, rol, True)
    
    def login(self, username, password):
        """Valida credenciales e inicia sesión"""
        query = "SELECT * FROM trabajadores WHERE username = ? AND password = ? AND activo = 1"
        resultado = self.db.consultar(query, (username, password))
        
        if not resultado:
            return None
        
        data = resultado[0]
        return Usuario(data[0], data[1], data[2], data[3], data[4], data[5])
    
    def actualizar_usuario(self, id_usuario, nombre=None, password=None, trabajador_responsable=None):
        """Actualiza datos del empleado"""
        updates = []
        params = []
        
        if nombre:
            updates.append("nombre = ?")
            params.append(nombre)
        if password:
            updates.append("password = ?")
            params.append(password)
        
        if not updates:
            raise Exception("No hay datos para actualizar")
        
        params.append(id_usuario)
        query = f"UPDATE trabajadores SET {', '.join(updates)} WHERE id = ?"
        self.db.ejecutar(query, tuple(params))
        self.db.commit()
        
        if trabajador_responsable:
            self._registrar_auditoria("UPDATE", "trabajadores", trabajador_responsable.id, 
                                     f"Actualización de usuario ID {id_usuario}")
    
    def eliminar_usuario(self, id_usuario, trabajador_responsable):
        """Elimina un usuario (solo empleados)"""
        if id_usuario == trabajador_responsable.id:
            raise Exception("No puedes eliminar tu propio usuario")
        
        query = "DELETE FROM trabajadores WHERE id = ? AND rol = 'empleado'"
        self.db.ejecutar(query, (id_usuario,))
        self.db.commit()
        
        self._registrar_auditoria("DELETE", "trabajadores", trabajador_responsable.id, 
                                 f"Eliminación de usuario ID {id_usuario}")
    
    def listar_usuarios(self):
        """Lista todos los usuarios"""
        query = "SELECT id, nombre, username, rol FROM trabajadores WHERE activo = 1"
        return self.db.consultar(query)
    
    def _registrar_auditoria(self, tipo, tabla, trabajador_id, descripcion):
        """Registra operación en auditoría"""
        query = """INSERT INTO auditoria (tipo_operacion, tabla_afectada, trabajador_id, 
                  fecha_hora, descripcion) VALUES (?, ?, ?, ?, ?)"""
        self.db.ejecutar(query, (tipo, tabla, trabajador_id, datetime.now(), descripcion))
        self.db.commit()