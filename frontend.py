import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import pygame
import os
from datetime import datetime

from main import SistemaGimnasio

# =========================
# CONFIG
# =========================

ROJO = "#7A1010"
BEIGE = "#DCCBB8"
NEGRO = "#111111"

ANCHO = 1400
ALTO = 800

# =========================
# APP
# =========================

class FrontendGym:

    def __init__(self, root):

        self.root = root
        self.root.title("Vital Core")
        self.root.geometry(f"{ANCHO}x{ALTO}")
        self.root.resizable(False, False)
        self.root.configure(bg=BEIGE)

        pygame.mixer.init()

        self.sistema = SistemaGimnasio()

        self.usuario_actual = None

        self.musica = [
            "AUDIO/lofi.mp3",
            "AUDIO/ippo.mp3",
            "AUDIO/rocky.mp3"
        ]

        self.indice_musica = 0
        self.muteado = False

        self.reproducir_musica()

        self.pantalla_bienvenida()

    # =========================
    # SONIDOS
    # =========================

    def sonido_click(self):
        try:
            s = pygame.mixer.Sound("ASSETS/click.wav")
            s.play(maxtime=1000)
        except:
            pass

    def sonido_success(self):
        try:
            s = pygame.mixer.Sound("ASSETS/success.wav")
            s.play(maxtime=1000)
        except:
            pass

    def sonido_error(self):
        try:
            s = pygame.mixer.Sound("ASSETS/error.wav")
            s.play(maxtime=1000)
        except:
            pass

    # =========================
    # MUSICA
    # =========================

    def reproducir_musica(self):

        try:
            pygame.mixer.music.load(self.musica[self.indice_musica])
            pygame.mixer.music.play(-1)
        except:
            pass

    def siguiente_cancion(self):

        self.sonido_click()

        self.indice_musica += 1

        if self.indice_musica >= len(self.musica):
            self.indice_musica = 0

        self.reproducir_musica()

    def mutear(self):

        self.sonido_click()

        if self.muteado:
            pygame.mixer.music.set_volume(1)
            self.muteado = False
        else:
            pygame.mixer.music.set_volume(0)
            self.muteado = True

    # =========================
    # UTIL
    # =========================

    def limpiar(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    # =========================
    # BIENVENIDA
    # =========================

    def pantalla_bienvenida(self):

        self.limpiar()

        frame = tk.Frame(self.root, bg=BEIGE)
        frame.pack(fill="both", expand=True)

        try:
            img = Image.open("ASSETS/logo.png")
            img = img.resize((250, 250))
            self.logo = ImageTk.PhotoImage(img)

            tk.Label(
                frame,
                image=self.logo,
                bg=BEIGE
            ).pack(pady=30)

        except:
            pass

        tk.Label(
            frame,
            text="VITAL CORE",
            font=("Teko", 40, "bold"),
            bg=BEIGE,
            fg=ROJO
        ).pack()

        tk.Label(
            frame,
            text="Sistema de Gestión de Gimnasio",
            font=("Arial", 16),
            bg=BEIGE,
            fg=NEGRO
        ).pack(pady=10)

        tk.Button(
            frame,
            text="ENTRAR",
            font=("Teko", 22),
            bg=ROJO,
            fg="white",
            width=15,
            command=self.pantalla_login
        ).pack(pady=30)

    # =========================
    # LOGIN
    # =========================

    def pantalla_login(self):

        self.sonido_click()

        self.limpiar()

        frame = tk.Frame(self.root, bg=BEIGE)
        frame.pack(expand=True)

        try:
            img = Image.open("ASSETS/logo.png")
            img = img.resize((180, 180))
            self.logo_login = ImageTk.PhotoImage(img)

            tk.Label(
                frame,
                image=self.logo_login,
                bg=BEIGE
            ).pack(pady=10)

        except:
            pass

        tk.Label(
            frame,
            text="INICIAR SESIÓN",
            font=("Teko", 30),
            bg=BEIGE,
            fg=ROJO
        ).pack(pady=20)

        tk.Label(frame, text="Usuario", bg=BEIGE).pack()
        self.user_entry = tk.Entry(frame, width=30)
        self.user_entry.pack(pady=5)

        tk.Label(frame, text="Contraseña", bg=BEIGE).pack()
        self.pass_entry = tk.Entry(frame, show="*", width=30)
        self.pass_entry.pack(pady=5)

        tk.Button(
            frame,
            text="INGRESAR",
            bg=ROJO,
            fg="white",
            width=20,
            command=self.login
        ).pack(pady=20)

    def login(self):

        self.sonido_click()

        username = self.user_entry.get()
        password = self.pass_entry.get()

        usuario = self.sistema.gestor_usuarios.login(username, password)

        if usuario:

            self.usuario_actual = usuario
            self.sistema.usuario_actual = usuario

            self.sonido_success()

            self.menu_principal()

        else:

            self.sonido_error()

            messagebox.showerror(
                "Error",
                "Credenciales incorrectas"
            )

    # =========================
    # MENU
    # =========================

    def menu_principal(self):

        self.limpiar()

        sidebar = tk.Frame(
            self.root,
            bg=ROJO,
            width=250
        )

        sidebar.pack(side="left", fill="y")

        content = tk.Frame(
            self.root,
            bg=BEIGE
        )

        content.pack(side="right", fill="both", expand=True)

        self.content = content

        try:
            img = Image.open("ASSETS/logo.png")
            img = img.resize((120, 120))
            self.logo_menu = ImageTk.PhotoImage(img)

            tk.Label(
                sidebar,
                image=self.logo_menu,
                bg=ROJO
            ).pack(pady=20)

        except:
            pass

        tk.Label(
            sidebar,
            text=self.usuario_actual.nombre,
            bg=ROJO,
            fg="white",
            font=("Teko", 22)
        ).pack()

        tk.Label(
            sidebar,
            text=self.usuario_actual.rol.upper(),
            bg=ROJO,
            fg=BEIGE,
            font=("Arial", 10)
        ).pack()

        botones = [

            ("Clientes", self.vista_clientes),
            ("Acceso", self.vista_acceso),
            ("Usuarios", self.vista_usuarios),
            ("Auditoría", self.vista_auditoria),
            ("Siguiente canción", self.siguiente_cancion),
            ("Mutear", self.mutear),
            ("Cerrar sesión", self.logout)

        ]

        for texto, comando in botones:

            if texto in ["Usuarios", "Auditoría"] and self.usuario_actual.rol != "admin":
                continue

            tk.Button(
                sidebar,
                text=texto,
                bg=BEIGE,
                fg=NEGRO,
                font=("Teko", 18),
                width=18,
                command=comando
            ).pack(pady=10)

        self.vista_clientes()

    # =========================
    # LOGOUT
    # =========================

    def logout(self):

        self.sonido_click()

        self.usuario_actual = None
        self.pantalla_login()

    # =========================
    # CLIENTES
    # =========================

    def vista_clientes(self):

        self.sonido_click()

        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(
            self.content,
            text="GESTIÓN DE CLIENTES",
            bg=BEIGE,
            fg=ROJO,
            font=("Teko", 32)
        ).pack(pady=20)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background=BEIGE,
            foreground=NEGRO,
            rowheight=30,
            fieldbackground=BEIGE
        )

        style.configure(
            "Treeview.Heading",
            background=ROJO,
            foreground="white",
            font=("Arial", 11, "bold")
        )

        columnas = ("ID", "Nombre", "Estado", "Vencimiento")

        self.tree = ttk.Treeview(
            self.content,
            columns=columnas,
            show="headings",
            height=12
        )

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

        self.tree.pack(pady=10)

        clientes = self.sistema.gestor_clientes.listar_clientes()

        for i, c in enumerate(clientes):

            cliente = self.sistema.gestor_clientes.buscar_cliente(c[0])

            if cliente and cliente.membresia:
                estado = cliente.membresia.estado()
                venc = cliente.membresia.fecha_vencimiento
            else:
                estado = "Sin membresía"
                venc = "N/A"

            tag = "par" if i % 2 == 0 else "impar"

            self.tree.insert(
                "",
                "end",
                values=(c[0], c[1], estado, venc),
                tags=(tag,)
            )

        self.tree.tag_configure("par", background=BEIGE)
        self.tree.tag_configure("impar", background="#cdb9a2")

        botones = tk.Frame(self.content, bg=BEIGE)
        botones.pack()

        tk.Button(
            botones,
            text="Registrar",
            bg=ROJO,
            fg="white",
            width=15,
            command=self.popup_registrar_cliente
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            botones,
            text="Actualizar",
            bg=ROJO,
            fg="white",
            width=15,
            command=self.popup_actualizar_cliente
        ).grid(row=0, column=1, padx=10)

        if self.usuario_actual.rol == "admin":

            tk.Button(
                botones,
                text="Eliminar",
                bg=ROJO,
                fg="white",
                width=15,
                command=self.eliminar_cliente
            ).grid(row=0, column=2, padx=10)

        tk.Button(
            botones,
            text="Exportar CSV",
            bg=ROJO,
            fg="white",
            width=15,
            command=self.exportar_csv
        ).grid(row=0, column=3, padx=10)

    # =========================
    # REGISTRAR CLIENTE
    # =========================

    def popup_registrar_cliente(self):

        self.sonido_click()

        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Cliente")
        ventana.geometry("400x350")
        ventana.configure(bg=BEIGE)

        tk.Label(ventana, text="Nombre", bg=BEIGE).pack(pady=5)
        nombre = tk.Entry(ventana)
        nombre.pack()

        tk.Label(ventana, text="Fecha inicio YYYY-MM-DD", bg=BEIGE).pack(pady=5)
        inicio = tk.Entry(ventana)
        inicio.pack()

        tk.Label(ventana, text="Fecha vencimiento YYYY-MM-DD", bg=BEIGE).pack(pady=5)
        venc = tk.Entry(ventana)
        venc.pack()

        def guardar():

            try:

                self.sistema.gestor_clientes.registrar_cliente(
                    nombre.get(),
                    inicio.get(),
                    venc.get(),
                    self.usuario_actual
                )

                self.sonido_success()

                messagebox.showinfo(
                    "Éxito",
                    "Cliente registrado"
                )

                ventana.destroy()
                self.vista_clientes()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        tk.Button(
            ventana,
            text="Guardar",
            bg=ROJO,
            fg="white",
            command=guardar
        ).pack(pady=20)

    # =========================
    # ACTUALIZAR CLIENTE
    # =========================

    def popup_actualizar_cliente(self):

        seleccion = self.tree.selection()

        if not seleccion:

            messagebox.showwarning(
                "Aviso",
                "Selecciona un cliente"
            )
            return

        datos = self.tree.item(seleccion[0])["values"]

        id_cliente = datos[0]

        cliente = self.sistema.gestor_clientes.buscar_cliente(id_cliente)

        ventana = tk.Toplevel(self.root)
        ventana.title("Actualizar Cliente")
        ventana.geometry("400x350")
        ventana.configure(bg=BEIGE)

        tk.Label(ventana, text="Nombre", bg=BEIGE).pack()

        nombre = tk.Entry(ventana)
        nombre.insert(0, cliente.nombre)
        nombre.pack()

        tk.Label(ventana, text="Fecha inicio", bg=BEIGE).pack()

        inicio = tk.Entry(ventana)
        inicio.insert(0, cliente.membresia.fecha_inicio)
        inicio.pack()

        tk.Label(ventana, text="Fecha vencimiento", bg=BEIGE).pack()

        venc = tk.Entry(ventana)
        venc.insert(0, cliente.membresia.fecha_vencimiento)
        venc.pack()

        def actualizar():

            try:

                self.sistema.gestor_clientes.actualizar_cliente(
                    id_cliente,
                    nombre.get(),
                    inicio.get(),
                    venc.get(),
                    self.usuario_actual
                )

                self.sonido_success()

                messagebox.showinfo(
                    "Éxito",
                    "Cliente actualizado"
                )

                ventana.destroy()
                self.vista_clientes()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        tk.Button(
            ventana,
            text="Actualizar",
            bg=ROJO,
            fg="white",
            command=actualizar
        ).pack(pady=20)

    # =========================
    # ELIMINAR CLIENTE
    # =========================

    def eliminar_cliente(self):

        seleccion = self.tree.selection()

        if not seleccion:

            messagebox.showwarning(
                "Aviso",
                "Selecciona un cliente"
            )
            return

        datos = self.tree.item(seleccion[0])["values"]

        id_cliente = datos[0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Eliminar cliente?"
        )

        if confirmar:

            try:

                self.sistema.gestor_clientes.eliminar_cliente(
                    id_cliente,
                    self.usuario_actual
                )

                self.sonido_success()

                self.vista_clientes()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

    # =========================
    # CSV
    # =========================

    def exportar_csv(self):

        self.sonido_click()

        try:

            self.sistema.gestor_clientes.exportar_csv()

            self.sonido_success()

            messagebox.showinfo(
                "Éxito",
                "CSV exportado"
            )

        except Exception as e:

            self.sonido_error()

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =========================
    # ACCESO
    # =========================

    def vista_acceso(self):

        self.sonido_click()

        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(
            self.content,
            text="CONTROL DE ACCESO",
            bg=BEIGE,
            fg=ROJO,
            font=("Teko", 32)
        ).pack(pady=20)

        entry = tk.Entry(
            self.content,
            font=("Arial", 22),
            justify="center"
        )

        entry.pack(pady=20)

        resultado = tk.Label(
            self.content,
            text="",
            bg=BEIGE,
            font=("Arial", 20, "bold")
        )

        resultado.pack(pady=20)

        def validar():

            try:

                r = self.sistema.control_acceso.validar_acceso(
                    int(entry.get())
                )

                resultado.config(text=r["mensaje"])

                if "PERMITIDO" in r["acceso"]:
                    self.sonido_success()
                else:
                    self.sonido_error()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        tk.Button(
            self.content,
            text="VALIDAR",
            bg=ROJO,
            fg="white",
            font=("Teko", 24),
            command=validar
        ).pack(pady=20)

    # =========================
    # USUARIOS
    # =========================

    def vista_usuarios(self):

        self.sonido_click()

        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(
            self.content,
            text="GESTIÓN DE USUARIOS",
            bg=BEIGE,
            fg=ROJO,
            font=("Teko", 32)
        ).pack(pady=20)

        self.tree_users = ttk.Treeview(
            self.content,
            columns=("ID", "Nombre", "Username", "Rol"),
            show="headings",
            height=14
        )

        columnas = [
            ("ID", 80),
            ("Nombre", 250),
            ("Username", 200),
            ("Rol", 120)
        ]

        for c, w in columnas:
            self.tree_users.heading(c, text=c)
            self.tree_users.column(c, width=w)

        self.tree_users.pack(pady=20)

        usuarios = self.sistema.gestor_usuarios.listar_usuarios()

        for u in usuarios:
            self.tree_users.insert("", "end", values=u)

        botones = tk.Frame(self.content, bg=BEIGE)
        botones.pack(pady=10)

        tk.Button(
            botones,
            text="Registrar",
            bg=ROJO,
            fg="white",
            width=15,
            command=self.popup_registrar_usuario
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            botones,
            text="Actualizar",
            bg=ROJO,
            fg="white",
            width=15,
            command=self.popup_actualizar_usuario
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            botones,
            text="Eliminar",
            bg=ROJO,
            fg="white",
            width=15,
            command=self.eliminar_usuario_front
        ).grid(row=0, column=2, padx=10)

    def popup_registrar_usuario(self):

        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Usuario")
        ventana.geometry("400x400")
        ventana.configure(bg=BEIGE)

        tk.Label(ventana, text="Nombre", bg=BEIGE).pack()
        nombre = tk.Entry(ventana)
        nombre.pack()

        tk.Label(ventana, text="Username", bg=BEIGE).pack()
        username = tk.Entry(ventana)
        username.pack()

        tk.Label(ventana, text="Password", bg=BEIGE).pack()
        password = tk.Entry(ventana)
        password.pack()

        tk.Label(ventana, text="Rol", bg=BEIGE).pack()
        rol = ttk.Combobox(
            ventana,
            values=["admin", "empleado"]
        )
        rol.pack()

        def guardar():

            try:

                self.sistema.gestor_usuarios.registrar_usuario(
                    nombre.get(),
                    username.get(),
                    password.get(),
                    rol.get(),
                    self.usuario_actual
                )

                self.sonido_success()

                ventana.destroy()

                self.vista_usuarios()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        tk.Button(
            ventana,
            text="Guardar",
            bg=ROJO,
            fg="white",
            command=guardar
        ).pack(pady=20)

    def popup_actualizar_usuario(self):

        seleccion = self.tree_users.selection()

        if not seleccion:
            messagebox.showwarning(
                "Aviso",
                "Selecciona un usuario"
            )
            return

        datos = self.tree_users.item(seleccion[0])["values"]

        id_usuario = datos[0]

        ventana = tk.Toplevel(self.root)
        ventana.title("Actualizar Usuario")
        ventana.geometry("400x300")
        ventana.configure(bg=BEIGE)

        tk.Label(ventana, text="Nuevo nombre", bg=BEIGE).pack()
        nombre = tk.Entry(ventana)
        nombre.insert(0, datos[1])
        nombre.pack()

        tk.Label(ventana, text="Nueva contraseña", bg=BEIGE).pack()
        password = tk.Entry(ventana)
        password.pack()

        def actualizar():

            try:

                self.sistema.gestor_usuarios.actualizar_usuario(
                    id_usuario,
                    nombre.get(),
                    password.get(),
                    self.usuario_actual
                )

                self.sonido_success()

                ventana.destroy()

                self.vista_usuarios()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

        tk.Button(
            ventana,
            text="Actualizar",
            bg=ROJO,
            fg="white",
            command=actualizar
        ).pack(pady=20)

    def eliminar_usuario_front(self):

        seleccion = self.tree_users.selection()

        if not seleccion:

            messagebox.showwarning(
                "Aviso",
                "Selecciona un usuario"
            )
            return

        datos = self.tree_users.item(seleccion[0])["values"]

        id_usuario = datos[0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Eliminar usuario?"
        )

        if confirmar:

            try:

                self.sistema.gestor_usuarios.eliminar_usuario(
                    id_usuario,
                    self.usuario_actual
                )

                self.sonido_success()

                self.vista_usuarios()

            except Exception as e:

                self.sonido_error()

                messagebox.showerror(
                    "Error",
                    str(e)
                )

    # =========================
    # AUDITORIA
    # =========================

    def vista_auditoria(self):

        self.sonido_click()

        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(
            self.content,
            text="AUDITORÍA",
            bg=BEIGE,
            fg=ROJO,
            font=("Teko", 32)
        ).pack(pady=20)

        query = """
        SELECT a.id, a.tipo_operacion, a.tabla_afectada,
        t.nombre, a.fecha_hora, a.descripcion
        FROM auditoria a
        LEFT JOIN trabajadores t
        ON a.trabajador_id = t.id
        ORDER BY a.fecha_hora DESC
        """

        registros = self.sistema.db.consultar(query)

        tree = ttk.Treeview(
            self.content,
            columns=("ID", "Tipo", "Tabla", "Trabajador", "Fecha", "Descripcion"),
            show="headings",
            height=18
        )

        columnas = [
            ("ID", 50),
            ("Tipo", 100),
            ("Tabla", 100),
            ("Trabajador", 150),
            ("Fecha", 180),
            ("Descripcion", 400)
        ]

        for c, w in columnas:
            tree.heading(c, text=c)
            tree.column(c, width=w)

        tree.pack(pady=20)

        for r in registros:

            trabajador = r[3] if r[3] else "Sistema"

            tree.insert(
                "",
                "end",
                values=(
                    r[0],
                    r[1],
                    r[2],
                    trabajador,
                    r[4],
                    r[5]
                )
            )

# =========================
# RUN
# =========================

root = tk.Tk()

app = FrontendGym(root)

root.mainloop()