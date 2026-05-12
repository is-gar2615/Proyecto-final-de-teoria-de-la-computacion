import sqlite3
from datetime import datetime
from usuarios import GestorUsuarios
from clientes import GestorClientes
from acceso import ControlAcceso

class BaseDeDatos:
    def __init__(self, nombre_bd="gimnasio.db"):
        self.nombre_bd = nombre_bd
        self.conexion = None
        self.cursor = None
    
    def conectar(self):
        self.conexion = sqlite3.connect(self.nombre_bd)
        self.conexion.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conexion.cursor()
        self.crear_tablas()
    
    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT CHECK(rol IN ('admin', 'empleado')) NOT NULL,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS membresias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                fecha_inicio DATE NOT NULL,
                fecha_vencimiento DATE NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id) ON DELETE CASCADE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accesos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER,
                fecha_hora DATETIME NOT NULL,
                resultado TEXT NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_operacion TEXT NOT NULL,
                tabla_afectada TEXT NOT NULL,
                trabajador_id INTEGER,
                fecha_hora DATETIME NOT NULL,
                descripcion TEXT,
                FOREIGN KEY (trabajador_id) REFERENCES trabajadores (id)
            )
        ''')
        
        self.conexion.commit()
    
    def ejecutar(self, query, parametros=None):
        if parametros:
            self.cursor.execute(query, parametros)
        else:
            self.cursor.execute(query)
    
    def consultar(self, query, parametros=None):
        if parametros:
            self.cursor.execute(query, parametros)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def commit(self):
        self.conexion.commit()
    
    def cerrar(self):
        if self.conexion:
            self.conexion.close()

class SistemaGimnasio:
    def __init__(self):
        self.db = BaseDeDatos()
        self.db.conectar()
        self.gestor_usuarios = GestorUsuarios(self.db)
        self.gestor_clientes = GestorClientes(self.db)
        self.control_acceso = ControlAcceso(self.db, self.gestor_clientes)
        self.usuario_actual = None
        
        # Crear admin por defecto
        self.gestor_usuarios.crear_admin_defecto()
    
    def iniciar(self):
        """Inicia el sistema con login"""
        print("\n" + "="*50)
        print("   SISTEMA DE GESTIÓN DE GIMNASIO")
        print("="*50)
        
        while True:
            if not self.usuario_actual:
                self.pantalla_login()
            else:
                self.menu_principal()
    
    def pantalla_login(self):
        """Pantalla de inicio de sesión"""
        print("\n--- INICIO DE SESIÓN ---")

        username = input("Usuario: ").strip()
        password = input("Contraseña: ").strip()

        if not username or not password:
            print("\n✗ Usuario y contraseña obligatorios")
            return

        self.usuario_actual = self.gestor_usuarios.login(username, password)

        if self.usuario_actual:
            print(f"\nBienvenido {self.usuario_actual.nombre} ({self.usuario_actual.rol})")
        else:
            print("\nCredenciales incorrectas")
    
    def menu_principal(self):
        """Menú principal del sistema"""
        while self.usuario_actual:
            print("\n" + "="*50)
            print(f"   MENÚ PRINCIPAL - {self.usuario_actual.nombre}")
            print(f"   Rol: {self.usuario_actual.rol}")
            print("="*50)
            print("\n1. Gestión de Clientes")
            print("2. Control de Acceso")
            
            if self.usuario_actual.rol == 'admin':
                print("3. Gestión de Usuarios")
                print("4. Ver Auditoría")
            
            print("\n0. Cerrar Sesión")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == '0':
                self.usuario_actual = None
                print("\n✓ Sesión cerrada")
                break
            elif opcion == '1':
                self.menu_clientes()
            elif opcion == '2':
                self.menu_acceso()
            elif opcion == '3' and self.usuario_actual.rol == 'admin':
                self.menu_usuarios()
            elif opcion == '4' and self.usuario_actual.rol == 'admin':
                self.menu_auditoria()
            else:
                print("\n✗ Opción no válida")
    
    def menu_clientes(self):
        """Menú de gestión de clientes"""
        while True:
            print("\n--- GESTIÓN DE CLIENTES ---")
            print("1. Registrar Cliente")
            print("2. Actualizar Cliente")
            print("3. Listar Clientes")
            print("4. Exportar a CSV")
            
            if self.usuario_actual.rol == 'admin':
                print("5. Eliminar Cliente")
            
            print("\n0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == '0':
                break
            elif opcion == '1':
                self.registrar_cliente()
            elif opcion == '2':
                self.actualizar_cliente()
            elif opcion == '3':
                self.listar_clientes()
            elif opcion == '4':
                self.exportar_csv()
            elif opcion == '5' and self.usuario_actual.rol == 'admin':
                self.eliminar_cliente()
            else:
                print("\n✗ Opción no válida o sin permisos")
    
    def registrar_cliente(self):
        """Registra un nuevo cliente"""
        print("\n--- REGISTRAR CLIENTE ---")

        try:
            nombre = input("Nombre del cliente: ").strip()

            if not nombre:
                print("\n✗ Nombre obligatorio")
                return

            fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
            fecha_vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ").strip()

            datetime.strptime(fecha_inicio, "%Y-%m-%d")
            datetime.strptime(fecha_vencimiento, "%Y-%m-%d")

            cliente = self.gestor_clientes.registrar_cliente(
                nombre,
                fecha_inicio,
                fecha_vencimiento,
                self.usuario_actual
            )

            print(f"\nCliente registrado exitosamente")
            print(f"  ID: {cliente.id}")
            print(f"  Nombre: {cliente.nombre}")
            print(f"  Membresía: {fecha_inicio} hasta {fecha_vencimiento}")

        except ValueError:
            print("\n✗ Formato de fecha inválido. Use YYYY-MM-DD")
        except Exception as e:
            print(f"\nError: {e}")
    
    def actualizar_cliente(self):
        """Actualiza datos de un cliente"""
        print("\n--- ACTUALIZAR CLIENTE ---")
        try:
            id_cliente = input("ID del cliente: ")
            
            cliente = self.gestor_clientes.buscar_cliente(int(id_cliente))
            if not cliente:
                print("\n✗ Cliente no encontrado")
                return
            
            print(f"\nCliente actual: {cliente.nombre}")
            if cliente.membresia:
                print(f"Membresía: {cliente.membresia.fecha_inicio} hasta {cliente.membresia.fecha_vencimiento}")
            
            nombre = input("\nNuevo nombre (Enter para no cambiar): ").strip()
            fecha_inicio = input("Nueva fecha inicio (Enter para no cambiar): ").strip()
            fecha_vencimiento = input("Nueva fecha vencimiento (Enter para no cambiar): ").strip()
            
            self.gestor_clientes.actualizar_cliente(
                int(id_cliente),
                nombre if nombre else None,
                fecha_inicio if fecha_inicio else None,
                fecha_vencimiento if fecha_vencimiento else None,
                self.usuario_actual
            )
            print("\n✓ Cliente actualizado exitosamente")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def listar_clientes(self):
        """Lista todos los clientes"""
        print("\n--- LISTA DE CLIENTES ---")
        clientes = self.gestor_clientes.listar_clientes()
        
        if not clientes:
            print("No hay clientes registrados")
            return
        
        print(f"\n{'ID':<5} {'Nombre':<25} {'Estado':<20} {'Vencimiento'}")
        print("-" * 75)
        
        for c in clientes:
            cliente = self.gestor_clientes.buscar_cliente(c[0])
            estado = cliente.membresia.estado() if cliente and cliente.membresia else "Sin membresía"
            vencimiento = c[3] if c[3] else "N/A"
            print(f"{c[0]:<5} {c[1]:<25} {estado:<20} {vencimiento}")
    
    def eliminar_cliente(self):
        """Elimina un cliente (solo admin)"""
        print("\n--- ELIMINAR CLIENTE ---")
        try:
            id_cliente = input("ID del cliente a eliminar: ")
            
            cliente = self.gestor_clientes.buscar_cliente(int(id_cliente))
            if not cliente:
                print("\nCliente no encontrado")
                return
            
            print(f"\nCliente a eliminar: {cliente.nombre}")
            confirmacion = input("¿Está seguro? (s/n): ")
            
            if confirmacion.lower() == 's':
                self.gestor_clientes.eliminar_cliente(int(id_cliente), self.usuario_actual)
                print("\nCliente eliminado exitosamente")
        except Exception as e:
            print(f"\nError: {e}")
    
    def exportar_csv(self):
        """Exporta clientes a CSV"""
        try:
            self.gestor_clientes.exportar_csv()
            print("\nArchivo 'clientes.csv' generado exitosamente")
        except Exception as e:
            print(f"\nError al exportar: {e}")
    
    def menu_acceso(self):
        """Menú de control de acceso"""
        while True:
            print("\n--- CONTROL DE ACCESO ---")
            print("1. Validar Acceso")
            print("\n0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == '0':
                break
            elif opcion == '1':
                self.validar_acceso()
            else:
                print("\n✗ Opción no válida")
    
    def validar_acceso(self):
        """Valida el acceso de un cliente"""
        print("\n--- VALIDAR ACCESO ---")
        id_cliente = input("ID del cliente: ")
        
        try:
            resultado = self.control_acceso.validar_acceso(int(id_cliente))
            
            print("\n" + "="*50)
            if resultado['acceso'] == 'PERMITIDO':
                print("ACCESO PERMITIDO")
            elif resultado['acceso'] == 'PERMITIDO_CON_ADVERTENCIA':
                print("ACCESO PERMITIDO CON ADVERTENCIA")
            else:
                print("ACCESO DENEGADO")
            
            print(f"\n{resultado['mensaje']}")
            print("="*50)
        except ValueError:
            print("\n✗ ID inválido")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def menu_usuarios(self):
        """Menú de gestión de usuarios (solo admin)"""
        while True:
            print("\n--- GESTIÓN DE USUARIOS ---")
            print("1. Registrar Usuario")
            print("2. Listar Usuarios")
            print("3. Actualizar Usuario")
            print("4. Eliminar Usuario")
            print("\n0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == '0':
                break
            elif opcion == '1':
                self.registrar_usuario()
            elif opcion == '2':
                self.listar_usuarios()
            elif opcion == '3':
                self.actualizar_usuario()
            elif opcion == '4':
                self.eliminar_usuario()
            else:
                print("\n✗ Opción no válida")
    
    def registrar_usuario(self):
        """Registra un nuevo usuario"""
        print("\n--- REGISTRAR USUARIO ---")

        try:
            nombre = input("Nombre completo: ").strip()
            username = input("Nombre de usuario: ").strip()
            password = input("Contraseña: ").strip()
            rol = input("Rol (admin/empleado): ").lower().strip()

            if not nombre or not username or not password:
                print("\n✗ Todos los campos son obligatorios")
                return

            usuario = self.gestor_usuarios.registrar_usuario(
                nombre,
                username,
                password,
                rol,
                self.usuario_actual
            )

            print(f"\n✓ Usuario registrado exitosamente")
            print(f"  ID: {usuario.id}")
            print(f"  Username: {usuario.username}")
            print(f"  Rol: {usuario.rol}")

        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def listar_usuarios(self):
        """Lista todos los usuarios"""
        print("\n--- LISTA DE USUARIOS ---")
        usuarios = self.gestor_usuarios.listar_usuarios()
        
        if not usuarios:
            print("No hay usuarios registrados")
            return
        
        print(f"\n{'ID':<5} {'Nombre':<25} {'Username':<20} {'Rol'}")
        print("-" * 60)
        
        for u in usuarios:
            print(f"{u[0]:<5} {u[1]:<25} {u[2]:<20} {u[3]}")
    
    def actualizar_usuario(self):
        """Actualiza datos de un usuario"""
        print("\n--- ACTUALIZAR USUARIO ---")
        try:
            id_usuario = input("ID del usuario: ")
            nombre = input("Nuevo nombre (Enter para no cambiar): ").strip()
            password = input("Nueva contraseña (Enter para no cambiar): ").strip()
            
            self.gestor_usuarios.actualizar_usuario(
                int(id_usuario),
                nombre if nombre else None,
                password if password else None,
                self.usuario_actual
            )
            print("\n✓ Usuario actualizado exitosamente")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def eliminar_usuario(self):
        """Elimina un usuario"""
        print("\n--- ELIMINAR USUARIO ---")
        try:
            id_usuario = input("ID del usuario a eliminar: ")
            
            confirmacion = input("\n¿Está seguro? (s/n): ")
            if confirmacion.lower() == 's':
                self.gestor_usuarios.eliminar_usuario(int(id_usuario), self.usuario_actual)
                print("\n✓ Usuario eliminado exitosamente")
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def menu_auditoria(self):
        """Menú de consulta de auditoría (solo admin)"""
        while True:
            print("\n--- CONSULTA DE AUDITORÍA ---")
            print("1. Ver toda la auditoría")
            print("2. Filtrar por tabla")
            print("3. Filtrar por trabajador")
            print("\n0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            
            if opcion == '0':
                break
            elif opcion == '1':
                self.ver_auditoria()
            elif opcion == '2':
                self.filtrar_auditoria_tabla()
            elif opcion == '3':
                self.filtrar_auditoria_trabajador()
            else:
                print("\n✗ Opción no válida")
    
    def ver_auditoria(self):
        """Muestra todos los registros de auditoría"""
        query = """
            SELECT a.id, a.tipo_operacion, a.tabla_afectada, t.nombre, a.fecha_hora, a.descripcion
            FROM auditoria a
            LEFT JOIN trabajadores t ON a.trabajador_id = t.id
            ORDER BY a.fecha_hora DESC
            LIMIT 50
        """
        registros = self.db.consultar(query)
        self._mostrar_auditoria(registros)
    
    def filtrar_auditoria_tabla(self):
        """Filtra auditoría por tabla"""
        tabla = input("Nombre de la tabla: ")
        query = """
            SELECT a.id, a.tipo_operacion, a.tabla_afectada, t.nombre, a.fecha_hora, a.descripcion
            FROM auditoria a
            LEFT JOIN trabajadores t ON a.trabajador_id = t.id
            WHERE a.tabla_afectada = ?
            ORDER BY a.fecha_hora DESC
            LIMIT 50
        """
        registros = self.db.consultar(query, (tabla,))
        self._mostrar_auditoria(registros)
    
    def filtrar_auditoria_trabajador(self):
        """Filtra auditoría por trabajador"""
        try:
            id_trab = int(input("ID del trabajador: "))
        except ValueError:
            print("\n✗ ID inválido")
            return

        query = """
            SELECT a.id, a.tipo_operacion, a.tabla_afectada, t.nombre, a.fecha_hora, a.descripcion
            FROM auditoria a
            LEFT JOIN trabajadores t ON a.trabajador_id = t.id
            WHERE a.trabajador_id = ?
            ORDER BY a.fecha_hora DESC
            LIMIT 50
        """

        registros = self.db.consultar(query, (id_trab,))
        self._mostrar_auditoria(registros)
    
    def _mostrar_auditoria(self, registros):
        """Muestra los registros de auditoría formateados"""

        if not registros:
            print("\nNo hay registros de auditoría")
            return

        print(f"\n{'ID':<5} {'Tipo':<10} {'Tabla':<15} {'Trabajador':<20} {'Fecha':<20} Descripción")
        print("-" * 100)

        for r in registros:
            trabajador = r[3] if r[3] else "Sistema"
            fecha = r[4][:19] if r[4] else "N/A"
            descripcion = r[5][:30] if r[5] else "Sin descripción"

            print(f"{r[0]:<5} {r[1]:<10} {r[2]:<15} {trabajador:<20} {fecha:<20} {descripcion}")
    
    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        self.db.cerrar()

if __name__ == "__main__":
    sistema = SistemaGimnasio()
    try:
        sistema.iniciar()
    except KeyboardInterrupt:
        print("\n\nSistema cerrado por el usuario")
    finally:
        sistema.cerrar()