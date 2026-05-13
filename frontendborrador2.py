# frontend.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pygame
import os

from main import SistemaGimnasio

# =========================================================
# CONFIGURACIÓN
# =========================================================

COLOR_ROJO = "#7A1010"
COLOR_BEIGE = "#DCCBB8"
COLOR_NEGRO = "#111111"
COLOR_CLARO = "#F5EFE8"

FUENTE_TITULO = ("Teko", 28, "bold")
FUENTE_SUB = ("Teko", 16)
FUENTE_NORMAL = ("Teko", 13)

ANCHO = 1280
ALTO = 720

# =========================================================
# FRONTEND
# =========================================================

class FrontendVitalCore:

    def __init__(self, root):

        self.root = root
        self.root.title("Vital Core")
        self.root.geometry(f"{ANCHO}x{ALTO}")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BEIGE)

        # ===============================
        # BACKEND
        # ===============================

        self.sistema = SistemaGimnasio()

        # ===============================
        # AUDIO
        # ===============================

        pygame.mixer.init()

        self.canciones = [
            "AUDIO/lofi.mp3",
            "AUDIO/ippo.mp3",
            "AUDIO/rocky.mp3"
        ]

        self.cancion_actual = 0
        self.musica_muted = False

        self.play_music()

        # ===============================
        # SONIDOS
        # ===============================

        self.sonido_click = pygame.mixer.Sound("ASSETS/click.wav")
        self.sonido_success = pygame.mixer.Sound("ASSETS/success.wav")
        self.sonido_error = pygame.mixer.Sound("ASSETS/error.wav")

        self.sonido_click.set_volume(0.4)
        self.sonido_success.set_volume(0.5)
        self.sonido_error.set_volume(0.5)

        # ==================================================
        # CONTENEDOR PRINCIPAL
        # ==================================================

        self.main_frame = tk.Frame(root, bg=COLOR_BEIGE)
        self.main_frame.pack(fill="both", expand=True)

        self.pantalla_bienvenida()

    # =====================================================
    # AUDIO
    # =====================================================

    def play_click(self):
        self.sonido_click.play(maxtime=1000)

    def play_success(self):
        self.sonido_success.play(maxtime=1000)

    def play_error(self):
        self.sonido_error.play(maxtime=1000)

    def play_music(self):

        pygame.mixer.music.load(self.canciones[self.cancion_actual])
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)

    def siguiente_cancion(self):

        self.play_click()

        self.cancion_actual += 1

        if self.cancion_actual >= len(self.canciones):
            self.cancion_actual = 0

        self.play_music()

    def mutear(self):

        self.play_click()

        if self.musica_muted:
            pygame.mixer.music.set_volume(0.35)
            self.musica_muted = False
        else:
            pygame.mixer.music.set_volume(0)
            self.musica_muted = True

    # =====================================================
    # UTILIDADES
    # =====================================================

    def limpiar_pantalla(self):

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def cargar_logo(self, tamaño):

        imagen = Image.open("ASSETS/logo.png")
        imagen = imagen.resize((tamaño, tamaño))
        return ImageTk.PhotoImage(imagen)

    def boton_estilo(self, parent, texto, comando):

        boton = tk.Button(
            parent,
            text=texto,
            font=FUENTE_SUB,
            bg=COLOR_ROJO,
            fg="white",
            activebackground="#5A0C0C",
            activeforeground="white",
            bd=0,
            cursor="hand2",
            width=20,
            command=lambda: [self.play_click(), comando()]
        )

        return boton

    # =====================================================
    # PANTALLA BIENVENIDA
    # =====================================================

    def pantalla_bienvenida(self):

        self.limpiar_pantalla()

        frame = tk.Frame(self.main_frame, bg=COLOR_BEIGE)
        frame.pack(expand=True)

        self.logo_inicio = self.cargar_logo(220)

        logo = tk.Label(
            frame,
            image=self.logo_inicio,
            bg=COLOR_BEIGE
        )
        logo.pack(pady=20)

        titulo = tk.Label(
            frame,
            text="VITAL CORE",
            font=("Teko", 42, "bold"),
            bg=COLOR_BEIGE,
            fg=COLOR_NEGRO
        )
        titulo.pack()

        subtitulo = tk.Label(
            frame,
            text="Sistema de Gestión de Gimnasio",
            font=("Teko", 18),
            bg=COLOR_BEIGE,
            fg=COLOR_ROJO
        )
        subtitulo.pack(pady=5)

        boton = self.boton_estilo(
            frame,
            "ENTRAR",
            self.pantalla_login
        )

        boton.pack(pady=40)

    # =====================================================
    # LOGIN
    # =====================================================

    def pantalla_login(self):

        self.limpiar_pantalla()

        frame = tk.Frame(
            self.main_frame,
            bg=COLOR_CLARO,
            width=450,
            height=500
        )

        frame.place(relx=0.5, rely=0.5, anchor="center")

        frame.pack_propagate(False)

        self.logo_login = self.cargar_logo(120)

        logo = tk.Label(
            frame,
            image=self.logo_login,
            bg=COLOR_CLARO
        )
        logo.pack(pady=15)

        titulo = tk.Label(
            frame,
            text="INICIAR SESIÓN",
            font=FUENTE_TITULO,
            bg=COLOR_CLARO,
            fg=COLOR_NEGRO
        )

        titulo.pack(pady=10)

        tk.Label(
            frame,
            text="Usuario",
            font=FUENTE_SUB,
            bg=COLOR_CLARO
        ).pack()

        self.entry_user = tk.Entry(
            frame,
            font=FUENTE_NORMAL,
            width=25
        )
        self.entry_user.pack(pady=5)

        tk.Label(
            frame,
            text="Contraseña",
            font=FUENTE_SUB,
            bg=COLOR_CLARO
        ).pack()

        self.entry_pass = tk.Entry(
            frame,
            font=FUENTE_NORMAL,
            show="*",
            width=25
        )
        self.entry_pass.pack(pady=5)

        boton = self.boton_estilo(
            frame,
            "INGRESAR",
            self.login
        )

        boton.pack(pady=25)

    def login(self):

        username = self.entry_user.get()
        password = self.entry_pass.get()

        usuario = self.sistema.gestor_usuarios.login(username, password)

        if usuario:

            self.play_success()

            self.sistema.usuario_actual = usuario
            self.menu_principal()

        else:

            self.play_error()

            messagebox.showerror(
                "Error",
                "Credenciales incorrectas"
            )

    # =====================================================
    # MENU PRINCIPAL
    # =====================================================

    def menu_principal(self):

        self.limpiar_pantalla()

        # =================================================
        # SIDEBAR
        # =================================================

        sidebar = tk.Frame(
            self.main_frame,
            bg=COLOR_ROJO,
            width=250
        )

        sidebar.pack(side="left", fill="y")

        self.logo_sidebar = self.cargar_logo(120)

        logo = tk.Label(
            sidebar,
            image=self.logo_sidebar,
            bg=COLOR_ROJO
        )

        logo.pack(pady=20)

        nombre = tk.Label(
            sidebar,
            text=self.sistema.usuario_actual.nombre,
            font=FUENTE_SUB,
            bg=COLOR_ROJO,
            fg="white"
        )

        nombre.pack()

        rol = tk.Label(
            sidebar,
            text=f"Rol: {self.sistema.usuario_actual.rol}",
            font=FUENTE_NORMAL,
            bg=COLOR_ROJO,
            fg=COLOR_BEIGE
        )

        rol.pack(pady=(0, 20))

        # ================================================
        # BOTONES SIDEBAR
        # ================================================

        botones = [

            ("Clientes", self.pantalla_clientes),
            ("Control Acceso", self.pantalla_acceso),
            ("Auditoría", self.pantalla_auditoria),
            ("CSV", self.exportar_csv),
            ("Siguiente canción", self.siguiente_cancion),
            ("Mutear", self.mutear),
            ("Cerrar sesión", self.logout)
        ]

        if self.sistema.usuario_actual.rol == "admin":

            botones.insert(2, ("Usuarios", self.pantalla_usuarios))

        for texto, comando in botones:

            b = tk.Button(
                sidebar,
                text=texto,
                font=FUENTE_SUB,
                bg=COLOR_ROJO,
                fg="white",
                activebackground="#5A0C0C",
                bd=0,
                cursor="hand2",
                command=lambda c=comando: [self.play_click(), c()]
            )

            b.pack(fill="x", pady=5, padx=10)

        # =================================================
        # PANEL DERECHO
        # =================================================

        self.panel = tk.Frame(
            self.main_frame,
            bg=COLOR_BEIGE
        )

        self.panel.pack(fill="both", expand=True)

        titulo = tk.Label(
            self.panel,
            text="Bienvenido a Vital Core",
            font=("Teko", 36, "bold"),
            bg=COLOR_BEIGE,
            fg=COLOR_NEGRO
        )

        titulo.pack(pady=80)

    # =====================================================
    # CLIENTES
    # =====================================================

    def pantalla_clientes(self):

        for widget in self.panel.winfo_children():
            widget.destroy()

        titulo = tk.Label(
            self.panel,
            text="GESTIÓN DE CLIENTES",
            font=FUENTE_TITULO,
            bg=COLOR_BEIGE
        )

        titulo.pack(pady=10)

        botones_frame = tk.Frame(
            self.panel,
            bg=COLOR_BEIGE
        )

        botones_frame.pack(pady=10)

        tk.Button(
            botones_frame,
            text="Registrar Cliente",
            font=FUENTE_SUB,
            bg=COLOR_ROJO,
            fg="white",
            command=lambda: [self.play_click(), self.popup_registrar_cliente()]
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            botones_frame,
            text="Actualizar Cliente",
            font=FUENTE_SUB,
            bg=COLOR_ROJO,
            fg="white",
            command=lambda: [self.play_click(), self.popup_actualizar_cliente()]
        ).grid(row=0, column=1, padx=10)

        if self.sistema.usuario_actual.rol == "admin":

            tk.Button(
                botones_frame,
                text="Eliminar Cliente",
                font=FUENTE_SUB,
                bg=COLOR_ROJO,
                fg="white",
                command=lambda: [self.play_click(), self.popup_eliminar_cliente()]
            ).grid(row=0, column=2, padx=10)

        # =================================================
        # TABLA
        # =================================================

        columnas = ("ID", "Nombre", "Estado", "Vencimiento")

        tabla = ttk.Treeview(
            self.panel,
            columns=columnas,
            show="headings",
            height=18
        )

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=180)

        tabla.pack(pady=20)

        style = ttk.Style()

        style.theme_use("default")

        style.configure(
            "Treeview",
            background=COLOR_BEIGE,
            foreground=COLOR_NEGRO,
            rowheight=30,
            fieldbackground=COLOR_BEIGE,
            font=FUENTE_NORMAL
        )

        style.configure(
            "Treeview.Heading",
            background=COLOR_ROJO,
            foreground="white",
            font=FUENTE_SUB
        )

        style.map(
            "Treeview",
            background=[("selected", COLOR_ROJO)]
        )

        clientes = self.sistema.gestor_clientes.listar_clientes()

        contador = 0

        for c in clientes:

            cliente = self.sistema.gestor_clientes.buscar_cliente(c[0])

            estado = cliente.membresia.estado()

            color = "par" if contador % 2 == 0 else "impar"

            tabla.insert(
                "",
                "end",
                values=(
                    c[0],
                    c[1],
                    estado,
                    c[3]
                ),
                tags=(color,)
            )

            contador += 1

        tabla.tag_configure("par", background="#EADFD2")
        tabla.tag_configure("impar", background="#DCCBB8")

    # =====================================================
    # POPUPS CLIENTES
    # =====================================================

    def popup_registrar_cliente(self):

        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Cliente")
        ventana.geometry("400x350")
        ventana.configure(bg=COLOR_BEIGE)

        tk.Label(
            ventana,
            text="Nombre",
            font=FUENTE_SUB,
            bg=COLOR_BEIGE
        ).pack()

        nombre = tk.Entry(ventana, font=FUENTE_NORMAL)
        nombre.pack()

        tk.Label(
            ventana,
            text="Fecha inicio (YYYY-MM-DD)",
            font=FUENTE_SUB,
            bg=COLOR_BEIGE
        ).pack()

        inicio = tk.Entry(ventana, font=FUENTE_NORMAL)
        inicio.pack()

        tk.Label(
            ventana,
            text="Fecha vencimiento",
            font=FUENTE_SUB,
            bg=COLOR_BEIGE
        ).pack()

        venc = tk.Entry(ventana, font=FUENTE_NORMAL)
        venc.pack()

        def registrar():

            try:

                self.sistema.gestor_clientes.registrar_cliente(
                    nombre.get(),
                    inicio.get(),
                    venc.get(),
                    self.sistema.usuario_actual
                )

                self.play_success()

                messagebox.showinfo(
                    "Éxito",
                    "Cliente registrado"
                )

                ventana.destroy()
                self.pantalla_clientes()

            except Exception as e:

                self.play_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        tk.Button(
            ventana,
            text="Registrar",
            font=FUENTE_SUB,
            bg=COLOR_ROJO,
            fg="white",
            command=registrar
        ).pack(pady=20)

    # =====================================================
    # CONTROL ACCESO
    # =====================================================

    def pantalla_acceso(self):

        for widget in self.panel.winfo_children():
            widget.destroy()

        titulo = tk.Label(
            self.panel,
            text="CONTROL DE ACCESO",
            font=FUENTE_TITULO,
            bg=COLOR_BEIGE
        )

        titulo.pack(pady=40)

        tk.Label(
            self.panel,
            text="ID Cliente",
            font=FUENTE_SUB,
            bg=COLOR_BEIGE
        ).pack()

        entry = tk.Entry(
            self.panel,
            font=("Teko", 24),
            justify="center"
        )

        entry.pack(pady=20)

        resultado_label = tk.Label(
            self.panel,
            text="",
            font=("Teko", 24, "bold"),
            bg=COLOR_BEIGE
        )

        resultado_label.pack(pady=30)

        def validar():

            try:

                resultado = self.sistema.control_acceso.validar_acceso(
                    int(entry.get())
                )

                if "PERMITIDO" in resultado["acceso"]:

                    self.play_success()

                    resultado_label.config(
                        text=resultado["mensaje"],
                        fg="green"
                    )

                else:

                    self.play_error()

                    resultado_label.config(
                        text=resultado["mensaje"],
                        fg="red"
                    )

            except:

                self.play_error()

                resultado_label.config(
                    text="ID inválido",
                    fg="red"
                )

        tk.Button(
            self.panel,
            text="VALIDAR",
            font=("Teko", 20),
            bg=COLOR_ROJO,
            fg="white",
            command=lambda: [self.play_click(), validar()]
        ).pack()

    # =====================================================
    # USUARIOS
    # =====================================================

    def pantalla_usuarios(self):

        messagebox.showinfo(
            "Usuarios",
            "Aquí irá gestión completa de usuarios.\n\n"
            "La estructura ya está conectada al backend."
        )

    # =====================================================
    # AUDITORÍA
    # =====================================================

    def pantalla_auditoria(self):

        messagebox.showinfo(
            "Auditoría",
            "Aquí irá la tabla visual de auditoría.\n\n"
            "La conexión backend ya está lista."
        )

    # =====================================================
    # CSV
    # =====================================================

    def exportar_csv(self):

        try:

            self.sistema.gestor_clientes.exportar_csv()

            self.play_success()

            messagebox.showinfo(
                "Éxito",
                "CSV exportado correctamente"
            )

        except Exception as e:

            self.play_error()

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(self):

        self.sistema.usuario_actual = None
        self.pantalla_login()

# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = FrontendVitalCore(root)

    root.mainloop()