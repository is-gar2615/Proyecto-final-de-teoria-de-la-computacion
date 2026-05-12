# Proyecto Final - Teoria Computación (Frontend)

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from main import SistemaGimnasio


class VitalCoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vital Core")
        self.root.geometry("1100x750")
        self.root.configure(bg="#DCCBB8")

        self.sistema = SistemaGimnasio()

        self.rojo = "#7A1010"
        self.beige = "#DCCBB8"
        self.negro = "#000000"

        self.logo = None

        self.cargar_logo()
        self.pantalla_bienvenida()

    def limpiar(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def cargar_logo(self):
        try:
            img = Image.open("Vital Core.png")
            img = img.resize((220, 220))
            self.logo = ImageTk.PhotoImage(img)
        except:
            self.logo = None
    # BIENVENIDA
    def pantalla_bienvenida(self):
        self.limpiar()

        frame = tk.Frame(self.root, bg=self.beige)
        frame.pack(expand=True)

        if self.logo:
            tk.Label(frame, image=self.logo, bg=self.beige).pack(pady=20)

        tk.Label(
            frame,
            text="VITAL CORE",
            font=("Bebas Neue", 36, "bold"),
            bg=self.beige,
            fg=self.rojo
        ).pack()

        tk.Label(
            frame,
            text="Sistema de Gestión de Gimnasio",
            font=("Arial", 16),
            bg=self.beige
        ).pack(pady=10)

        tk.Button(
            frame,
            text="ENTRAR",
            font=("Arial", 16, "bold"),
            bg=self.rojo,
            fg="white",
            width=18,
            command=self.pantalla_login
        ).pack(pady=30)
    # LOGIN
    def pantalla_login(self):
        self.limpiar()

        frame = tk.Frame(self.root, bg=self.beige)
        frame.pack(expand=True)

        tk.Label(frame, text="Iniciar Sesión", font=("Arial", 26, "bold"),
                 bg=self.beige, fg=self.rojo).pack(pady=20)

        tk.Label(frame, text="Usuario", bg=self.beige).pack()
        self.user_entry = tk.Entry(frame, width=30)
        self.user_entry.pack()

        tk.Label(frame, text="Contraseña", bg=self.beige).pack(pady=(10, 0))
        self.pass_entry = tk.Entry(frame, width=30, show="*")
        self.pass_entry.pack()

        tk.Button(
            frame,
            text="Ingresar",
            bg=self.rojo,
            fg="white",
            width=20,
            command=self.login
        ).pack(pady=20)

        tk.Button(
            frame,
            text="Volver",
            command=self.pantalla_bienvenida
        ).pack()

    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        usuario = self.sistema.gestor_usuarios.login(username, password)

        if usuario:
            self.sistema.usuario_actual = usuario
            self.menu_principal()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
    # MENU
    def menu_principal(self):
        self.limpiar()

        frame = tk.Frame(self.root, bg=self.beige)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=f"Bienvenido {self.sistema.usuario_actual.nombre}",
            font=("Arial", 22, "bold"),
            bg=self.beige,
            fg=self.rojo
        ).pack(pady=20)

        botones = [
            ("Gestión Clientes", self.gestion_clientes),
            ("Control de Acceso", self.validar_acceso),
            ("Exportar CSV", self.exportar_csv)
        ]

        if self.sistema.usuario_actual.rol == "admin":
            botones.extend([
                ("Gestión Usuarios", self.gestion_usuarios),
                ("Ver Auditoría", self.ver_auditoria)
            ])

        botones.append(("Cerrar Sesión", self.logout))

        for texto, comando in botones:
            tk.Button(
                frame,
                text=texto,
                width=25,
                height=2,
                bg=self.rojo,
                fg="white",
                command=comando
            ).pack(pady=10)

    def logout(self):
        self.sistema.usuario_actual = None
        self.pantalla_login()
    # CLIENTES
    def gestion_clientes(self):
        self.limpiar()

        frame = tk.Frame(self.root, bg=self.beige)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Gestión de Clientes",
                 font=("Arial", 22, "bold"),
                 bg=self.beige, fg=self.rojo).pack(pady=20)

        tk.Button(frame, text="Registrar Cliente",
                  command=self.registrar_cliente).pack(pady=10)

        tk.Button(frame, text="Listar Clientes",
                  command=self.listar_clientes).pack(pady=10)

        tk.Button(frame, text="Volver",
                  command=self.menu_principal).pack(pady=20)

    def registrar_cliente(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Cliente")

        tk.Label(ventana, text="Nombre").pack()
        nombre = tk.Entry(ventana)
        nombre.pack()

        tk.Label(ventana, text="Fecha Inicio (YYYY-MM-DD)").pack()
        inicio = tk.Entry(ventana)
        inicio.pack()

        tk.Label(ventana, text="Fecha Vencimiento").pack()
        venc = tk.Entry(ventana)
        venc.pack()

        def guardar():
            try:
                self.sistema.gestor_clientes.registrar_cliente(
                    nombre.get(),
                    inicio.get(),
                    venc.get(),
                    self.sistema.usuario_actual
                )
                messagebox.showinfo("Éxito", "Cliente registrado")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)

    def listar_clientes(self):
        clientes = self.sistema.gestor_clientes.listar_clientes()

        ventana = tk.Toplevel(self.root)
        ventana.title("Clientes")

        tree = ttk.Treeview(
            ventana,
            columns=("ID", "Nombre", "Inicio", "Vencimiento"),
            show="headings"
        )

        for col in ("ID", "Nombre", "Inicio", "Vencimiento"):
            tree.heading(col, text=col)

        for c in clientes:
            tree.insert("", "end", values=c)

        tree.pack(fill="both", expand=True)
    # ACCESO
    def validar_acceso(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Control de Acceso")

        tk.Label(ventana, text="ID Cliente").pack()
        entrada = tk.Entry(ventana)
        entrada.pack()

        def validar():
            try:
                resultado = self.sistema.control_acceso.validar_acceso(
                    int(entrada.get())
                )
                messagebox.showinfo("Resultado", resultado["mensaje"])
            except:
                messagebox.showerror("Error", "ID inválido")

        tk.Button(ventana, text="Validar", command=validar).pack(pady=10)
    # CSV
    def exportar_csv(self):
        try:
            self.sistema.gestor_clientes.exportar_csv()
            messagebox.showinfo("Éxito", "CSV exportado")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    # USUARIOS
    def gestion_usuarios(self):
        messagebox.showinfo(
            "Usuarios",
            "Gestión completa disponible en backend.\nPuede ampliarse fácilmente."
        )
    # AUDITORIA
    def ver_auditoria(self):
        registros = self.sistema.db.consultar("""
            SELECT * FROM auditoria
            ORDER BY fecha_hora DESC
            LIMIT 30
        """)

        ventana = tk.Toplevel(self.root)
        ventana.title("Auditoría")

        tree = ttk.Treeview(
            ventana,
            columns=("ID", "Tipo", "Tabla", "Fecha"),
            show="headings"
        )

        for c in ("ID", "Tipo", "Tabla", "Fecha"):
            tree.heading(c, text=c)

        for r in registros:
            tree.insert("", "end", values=(r[0], r[1], r[2], r[4]))

        tree.pack(fill="both", expand=True)


root = tk.Tk()
app = VitalCoreApp(root)
root.mainloop()