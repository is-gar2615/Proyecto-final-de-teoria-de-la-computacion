from datetime import datetime, timedelta

class ControlAcceso:
    def __init__(self, db, gestor_clientes):
        self.db = db
        self.gestor_clientes = gestor_clientes
        self.bloqueos = {}
    
    def validar_acceso(self, id_cliente):
        """Valida el acceso de un cliente al gimnasio"""
        if self.esta_bloqueado(id_cliente):
            return {
                "acceso": "DENEGADO",
                "mensaje": "Cliente bloqueado temporalmente. Espere 1 minuto.",
                "bloqueado": True
            }
        
        cliente = self.verificar_existencia_cliente(id_cliente)
        if not cliente:
            self._registrar_intento(id_cliente, "FALLIDO", "Cliente no encontrado")
            return {
                "acceso": "DENEGADO",
                "mensaje": "Cliente no encontrado",
                "bloqueado": False
            }
        
        estado = self.verificar_estado_membresia(cliente)
        
        if estado == "Vigente":
            self.bloquear_cliente(id_cliente)
            self._registrar_intento(id_cliente, "EXITOSO", "Acceso permitido")
            return {
                "acceso": "PERMITIDO",
                "mensaje": "✓ Acceso permitido. Membresía vigente.",
                "bloqueado": False
            }
        elif estado == "Próxima a vencer":
            self.bloquear_cliente(id_cliente)
            dias = self.calcular_dias_restantes(cliente)
            self._registrar_intento(id_cliente, "EXITOSO", f"Acceso con advertencia. Vence en {dias} días")
            return {
                "acceso": "PERMITIDO_CON_ADVERTENCIA",
                "mensaje": f"⚠ Acceso permitido. Su membresía vence en {dias} días.",
                "bloqueado": False
            }
        else:
            self._registrar_intento(id_cliente, "DENEGADO", "Membresía vencida")
            return {
                "acceso": "DENEGADO",
                "mensaje": "✗ Acceso denegado. Membresía vencida.",
                "bloqueado": False
            }
    
    def verificar_existencia_cliente(self, id_cliente):
        """Verifica si el cliente existe"""
        return self.gestor_clientes.buscar_cliente(id_cliente)
    
    def verificar_estado_membresia(self, cliente):
        """Verifica el estado de la membresía"""
        if not cliente or not cliente.membresia:
            return "Vencida"
        return cliente.membresia.estado()
    
    def calcular_dias_restantes(self, cliente):
        """Calcula los días restantes de la membresía"""
        if not cliente or not cliente.membresia:
            return 0
        return (cliente.membresia.fecha_vencimiento - datetime.now().date()).days
    
    def bloquear_cliente(self, id_cliente):
        """Bloquea al cliente por 1 minuto"""
        self.bloqueos[id_cliente] = datetime.now()
    
    def esta_bloqueado(self, id_cliente):
        """Verifica si el cliente está bloqueado"""
        if id_cliente in self.bloqueos:
            if datetime.now() - self.bloqueos[id_cliente] < timedelta(minutes=1):
                return True
            else:
                del self.bloqueos[id_cliente]
        return False
    
    def _registrar_intento(self, id_cliente, resultado, descripcion):
        """Registra el intento de acceso"""
        query = """INSERT INTO accesos (id_cliente, fecha_hora, resultado, descripcion) 
                  VALUES (?, ?, ?, ?)"""
        self.db.ejecutar(query, (id_cliente, datetime.now(), resultado, descripcion))
        self.db.commit()
        
        query_aud = """INSERT INTO auditoria (tipo_operacion, tabla_afectada, trabajador_id, 
                      fecha_hora, descripcion) VALUES (?, ?, ?, ?, ?)"""
        self.db.ejecutar(query_aud, ("INSERT", "accesos", None, datetime.now(), 
                                     f"Intento de acceso cliente ID {id_cliente}: {resultado}"))
        self.db.commit()