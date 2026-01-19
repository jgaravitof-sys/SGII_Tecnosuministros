# SIGIV - TecnoSuministros
# Juan Felipe Garavito Feo - Esteban Girón Herrera - Carlos Alberto Mancilla Valle

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import os
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

def recurso_path(ruta_relativa):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, ruta_relativa)

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = recurso_path("sigivbd.db")

usuarios = {
    "admin": ["admin123", "Administrador"],
    "vendedor": ["venta123", "Vendedor"],
    "bodega": ["bodega123", "Bodega"],
    "gerente": ["gerente123", "Gerente"]
}

productos = []
ventas = []

class SIGIVApp(tk.Tk):
  
    print(os.path.abspath(DB_PATH))

    def __init__(self):
        super().__init__()
        self.title("SIGIV - Sistema de Gestión de Inventarios y Ventas")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.usuario_actual = None
        self.productos = []  
        self.clientes = [] 
        self.proveedores = [] 
        self.ingresos = {"dia": {}, "semana": {}, "mes": {}, "año": {}}      
        self.cargar_productos_desde_db()
        self.login_frame()
        self.alertas = []

    def get_carpeta_path(self, filename):
        carpeta = os.path.join(os.path.expanduser("~"), "TecnoSuministros")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            return os.path.join(carpeta, filename)

    def registrar_alerta(self, mensaje):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO alertas (mensaje) VALUES (?)", (mensaje,))
        conn.commit()
        conn.close()

    def validar_correo(self, correo):
        """Valida que el correo tenga el formato local@dominio"""
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, correo) is not None

    def cargar_productos_desde_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, cantidad, precio, proveedor, categoria FROM productos")
        rows = cursor.fetchall()
        conn.close()

        self.productos = [
            {
                "codigo": r[0],
                "nombre": r[1],
                "cantidad": r[2],
                "precio": r[3],
                "proveedor": r[4],
                "categoria": r[5]
            }
            for r in rows
        ]

    def login_frame(self):
        self.clear()
        frame = tk.Frame(self, bg="#1e1e2f")
        frame.place(relwidth=1, relheight=1)

        login_container = tk.Frame(frame, bg="#2e2e42", bd=2, relief="ridge")
        login_container.place(relx=0.5, rely=0.5, anchor="center", width=350, height=320)

        tk.Label(login_container, text="Iniciar Sesión", font=("Trebuchet MS", 20, "bold"), bg="#2e2e42", fg="white").pack(pady=(20, 15))

        user_frame = tk.Frame(login_container, bg="#2e2e42")
        user_frame.pack(pady=10, fill="x", padx=30)
        tk.Label(user_frame, text="👤", font=("Trebuchet MS Emoji", 14), bg="#2e2e42", fg="white").pack(side="left")
        user_entry = tk.Entry(user_frame, font=("Trebuchet MS", 14), bg="#44475a", fg="white", insertbackground="white")
        user_entry.pack(side="left", fill="x", expand=True, padx=(10,0))
        user_entry.focus()

        pass_frame = tk.Frame(login_container, bg="#2e2e42")
        pass_frame.pack(pady=10, fill="x", padx=30)
        tk.Label(pass_frame, text="🔒", font=("Trebuchet MSI Emoji", 14), bg="#2e2e42", fg="white").pack(side="left")
        pass_entry = tk.Entry(pass_frame, font=("Trebuchet MS", 14), show="*", bg="#44475a", fg="white", insertbackground="white")
        pass_entry.pack(side="left", fill="x", expand=True, padx=(10,0))

        def login():
            usuario = user_entry.get()
            contraseña = pass_entry.get()
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT rol FROM usuarios WHERE usuario = ? AND contraseña = ?", (usuario, contraseña))
            resultado = cursor.fetchone()
            conn.close()

            if resultado:
                self.usuario_actual = resultado[0]
                self.main_app()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")

        btn_frame = tk.Frame(login_container, bg="#2e2e42")
        btn_frame.pack(pady=25, fill="x", padx=30)

        tk.Button(btn_frame, text="Ingresar", font=("Trebuchet MS", 14), bg="#50fa7b", fg="#282a36", activebackground="#45e765",
        activeforeground="#282a36", relief="flat", command=login).pack(fill="x")

        tk.Button(btn_frame, text="Registrarse", font=("Trebuchet MS", 12), bg="#6272a4", fg="white", relief="flat",
        command=self.registro_usuario).pack(fill="x", pady=(10,0))

    def registro_usuario(self):
        self.clear()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TCombobox",
                        fieldbackground="#44475a",
                        background="#44475a",
                        foreground="white",
                        bordercolor="#2e2e42",
                        selectbackground="#6272a4",
                        selectforeground="white",
                        font=("Trebuchet MS", 12))

        frame = tk.Frame(self, bg="#1e1e2f")
        frame.place(relwidth=1, relheight=1)

        reg_container = tk.Frame(frame, bg="#2e2e42", bd=2, relief="ridge")
        reg_container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=530)

        tk.Label(reg_container, text="Registro de Usuario", font=("Trebuchet MS", 20, "bold"), bg="#2e2e42", fg="white").pack(pady=(20, 10))

        def crear_campo(parent, label_text, show=None):
            campo_frame = tk.Frame(parent, bg="#2e2e42")
            campo_frame.pack(pady=6, fill="x", padx=35)
            tk.Label(campo_frame, text=label_text, font=("Trebuchet MS", 12), bg="#2e2e42", fg="white").pack(anchor="w")
            entry = tk.Entry(campo_frame, font=("Trebuchet MS", 14), bg="#44475a", fg="white", insertbackground="white", show=show)
            entry.pack(fill="x")
            return entry

        usuario_entry = crear_campo(reg_container, "Usuario:")
        correo_entry = crear_campo(reg_container, "Correo:")

        style = ttk.Style()
        style.theme_use('clam')

        style.configure("Dark.TCombobox",
        fieldbackground="#44475a",
        background="#44475a",
        foreground="white", 
        arrowcolor="white",
        bordercolor="#2e2e42",
        relief="flat",
        font=("Trebuchet MS", 12)
        )

        style.map("Dark.TCombobox",
        fieldbackground=[('readonly', '#44475a')],
        foreground=[('readonly', 'white')],
        background=[('readonly', '#44475a')],
        arrowcolor=[('active', 'white'), ('!active', 'white')]
        )

        rol_frame = tk.Frame(reg_container, bg="#2e2e42")
        rol_frame.pack(pady=6, fill="x", padx=35)
        tk.Label(rol_frame, text="Rol:", font=("Trebuchet MS", 12), bg="#2e2e42", fg="white").pack(anchor="w")
        rol_var = tk.StringVar()
        rol_combo = ttk.Combobox(rol_frame, textvariable=rol_var, style="Dark.TCombobox", state="readonly")
        rol_combo["values"] = ["Gerente", "Administrador", "Bodega", "Vendedor"]
        rol_combo.pack(fill="x")
        rol_combo.current(0)

        contraseña_entry = crear_campo(reg_container, "Contraseña:", show="*")
        confirmar_entry = crear_campo(reg_container, "Confirmar Contraseña:", show="*")

        def es_correo_valido(correo):
            patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            return re.match(patron, correo)

        def registrar():
            usuario = usuario_entry.get().strip()
            correo = correo_entry.get().strip()
            rol = rol_var.get().strip()
            contraseña = contraseña_entry.get()
            confirmar = confirmar_entry.get()

            if not usuario or not correo or not rol or not contraseña or not confirmar:
                messagebox.showwarning("Atención", "Por favor, complete todos los campos.")
                return

            if not es_correo_valido(correo):
                messagebox.showerror("Error", "Formato de correo inválido.")
                return

            if contraseña != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT usuario FROM usuarios WHERE usuario = ?", (usuario,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "El usuario ya existe.")
                    conn.close()
                    return

                cursor.execute("INSERT INTO usuarios (usuario, correo, rol, contraseña) VALUES (?, ?, ?, ?)",
                               (usuario, correo, rol, contraseña))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
                self.login_frame()
                self.registrar_alerta(f"Nuevo usuario creado: '{usuario}'")
            except Exception as e:
                messagebox.showerror("Error", f"Ocurrió un error al registrar: {str(e)}")

        # Botones
        btn_frame = tk.Frame(reg_container, bg="#2e2e42")
        btn_frame.pack(pady=20, fill="x", padx=35)

        tk.Button(btn_frame, text="Registrar", font=("Lato", 14), bg="#50fa7b", fg="#282a36", relief="flat",
        activebackground="#45e765", activeforeground="#282a36", command=registrar).pack(fill="x", pady=(0, 10))

        tk.Button(btn_frame, text="Volver", font=("Lato", 14), bg="#6272a4", fg="white", relief="flat",
        activebackground="#535c90", activeforeground="white", command=self.login_frame).pack(fill="x")

    def main_app(self):
        self.clear()
        self.sidebar = tk.Frame(self, bg="#2e2e42", width=220)
        self.sidebar.pack(side="left", fill="y")

        self.panel = tk.Frame(self, bg="#282a36")
        self.panel.pack(side="right", expand=True, fill="both")

        tk.Label(
            self.sidebar, 
            text=f"👤 {self.usuario_actual}", 
            fg="white", 
            bg="#2e2e42", 
            font=("Trebuchet MS", 16, "bold")
        ).pack(pady=25)

        botones = []

        if self.usuario_actual == "Administrador":
            botones = [
                ("📦 Inventario", "Inventario"),
                ("👥 Usuarios", "Usuarios"),
                ("📊 Reportes", "Reportes"),
                ("💰 Ventas", "Ventas"),
                ("⚠️ Alertas", "Alertas"),
                ("📈 Ver Métricas", "Ver Métricas")
            ]
        elif self.usuario_actual == "Vendedor":
            botones = [
                ("💰 Ventas", "Ventas"),
                ("📦 Consultar Stock", "Consultar Stock"),
                ("📊 Reportes", "Reportes")
            ]
        elif self.usuario_actual == "Bodega":
            botones = [
                ("📦 Inventario", "Inventario"),
                ("⚠️ Alertas", "Alertas")
            ]
        elif self.usuario_actual == "Gerente":
            botones = [
                ("📈 Ver Métricas", "Ver Métricas"),
                ("📊 Reportes", "Reportes"),
                ("⚠️ Alertas", "Alertas")
            ]

        for texto, comando in botones:
            tk.Button(
                self.sidebar,
                text=texto,
                font=("Trebuchet MS", 13),
                bg="#44475a",
                fg="white",
                activebackground="#6272a4",
                activeforeground="white",
                relief="flat",
                command=lambda t=comando: self.mostrar_panel(t)
            ).pack(pady=8, fill="x", padx=15)

        tk.Button(
            self.sidebar,
            text="🚪 Cerrar Sesión",
            font=("Trebuchet MS", 13, "bold"),
            bg="#ff5555",
            fg="white",
            activebackground="#ff4444",
            activeforeground="white",
            relief="flat",
            command=self.login_frame
        ).pack(side="bottom", pady=15, padx=15, fill="x")

    def mostrar_panel(self, texto):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text=f"Módulo: {texto}",
            font=("Trebuchet MS", 22, "bold"),
            bg="#282a36",
            fg="white",
            pady=20
        ).pack()

        if texto == "Inventario":
            self.mostrar_inventario()
        elif texto == "Ventas":
            self.registrar_venta()
        elif texto == "Usuarios":
            self.gestionar_usuarios()
        elif texto == "Reportes":
            self.generar_reportes()
        elif texto == "Ver Métricas":
            self.ver_metricas()
        elif texto == "Alertas":
            self.mostrar_alertas()
        elif texto == "Consultar Stock":
            self.mostrar_stock()

    def mostrar_inventario(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="Inventario de Productos",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        table_frame = tk.Frame(self.panel, bg="#282a36")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#44475a",
                        foreground="white",
                        fieldbackground="#44475a",
                        font=("Trebuchet MS", 12),
                        rowheight=30)
        style.map("Treeview", background=[('selected', '#50fa7b')],
                                foreground=[('selected', '#282a36')])
        style.configure("Treeview.Heading",
                        background="#6272a4",
                        foreground="white",
                        font=("Trebuchet MS", 13, "bold"))

        columns = ("codigo", "nombre", "cantidad", "precio", "proveedor", "categoria")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        tree.heading("codigo", text="🆔 Código")
        tree.heading("nombre", text="📦 Nombre")
        tree.heading("cantidad", text="🔢 Cantidad")
        tree.heading("precio", text="💲 Precio")
        tree.heading("proveedor", text="🏭 Proveedor")
        tree.heading("categoria", text="📂 Categoría")

        tree.column("codigo", width=100, anchor="center")
        tree.column("nombre", width=190, anchor="w")
        tree.column("cantidad", width=130, anchor="center")
        tree.column("precio", width=90, anchor="center")
        tree.column("proveedor", width=150, anchor="w")
        tree.column("categoria", width=130, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for prod in self.productos:
            tree.insert("", "end", values=(
                prod.get("codigo", ""),
                prod.get("nombre", ""),
                prod.get("cantidad", 0),
                f"${prod.get('precio', 0):.2f}",
                prod.get("proveedor", ""),
                prod.get("categoria", "")
            ))

        acciones_frame = tk.Frame(self.panel, bg="#282a36")
        acciones_frame.pack(pady=20)

        tk.Button(
            acciones_frame,
            text="➕ Agregar Producto",
            command=self.agregar_producto,
            font=("Trebuchet MS", 12, "bold"),
            bg="#50fa7b",
            fg="#282a36",
            relief="flat",
            activebackground="#45e765",
            activeforeground="#282a36",
            padx=10,
            pady=8
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            acciones_frame,
            text="✏️ Editar Producto",
            font=("Trebuchet MS", 12, "bold"),
            bg="#f1fa8c",
            fg="#282a36",
            relief="flat",
            command=self.editar_producto,
            padx=10,
            pady=8
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            acciones_frame,
            text="❌ Eliminar Producto",
            font=("Trebuchet MS", 12, "bold"),
            bg="#ff5555",
            fg="white",
            relief="flat",
            command=self.eliminar_producto,
            padx=10,
            pady=8
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            acciones_frame,
            text="🔍 Consultas",
            font=("Trebuchet MS", 12, "bold"),
            bg="#8be9fd",
            fg="#282a36",
            relief="flat",
            command=self.consultar_productos,
            padx=10,
            pady=8
        ).grid(row=0, column=3, padx=10)

    def agregar_producto(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="➕ Agregar Nuevo Producto",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        campos = ["Nombre", "Cantidad", "Precio", "Proveedor", "Categoría"]
        entradas = {}

        form_frame = tk.Frame(self.panel, bg="#282a36")
        form_frame.pack(padx=40, pady=10, fill="x")

        for campo in campos:
            tk.Label(
                form_frame,
                text=f"{campo}:",
                font=("Trebuchet MS", 13),
                bg="#282a36",
                fg="white",
                anchor="w"
            ).pack(fill="x", pady=(10, 3))

            entry = tk.Entry(
                form_frame,
                font=("Trebuchet MS", 14),
                bg="#44475a",
                fg="white",
                insertbackground="white",
                relief="flat",
                highlightthickness=1,
                highlightcolor="#50fa7b",
                highlightbackground="#6272a4",
                borderwidth=0,
                width=30
            )
            entry.pack(fill="x")
            entradas[campo] = entry

        def guardar_producto():
            nombre = entradas["Nombre"].get().strip()
            cantidad = entradas["Cantidad"].get().strip()
            precio = entradas["Precio"].get().strip()
            proveedor = entradas["Proveedor"].get().strip()
            categoria = entradas["Categoría"].get().strip()

            if not nombre or not cantidad or not precio:
                messagebox.showwarning(
                    "Campos requeridos",
                    "Nombre, cantidad y precio son obligatorios."
                )
                return

            try:
                cantidad = int(cantidad)
                precio = float(precio)
            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Cantidad debe ser un número entero y precio un número decimal."
                )
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT codigo FROM productos ORDER BY id DESC LIMIT 1")
            ultimo = cursor.fetchone()

            numero = int(ultimo[0][1:]) + 1 if ultimo else 1
            codigo = f"P{numero:03}"

            cursor.execute("""
                INSERT INTO productos (codigo, nombre, cantidad, precio, proveedor, categoria)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (codigo, nombre, cantidad, precio, proveedor, categoria))
            conn.commit()
            conn.close()
            self.cargar_productos_desde_db()
            messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado.")
            self.mostrar_inventario()
            self.registrar_alerta(f"Nuevo producto creado: '{nombre}'")

        btn_frame = tk.Frame(self.panel, bg="#282a36")
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="💾 Guardar Producto",
            bg="#50fa7b",
            fg="#282a36",
            font=("Trebuchet MS", 14, "bold"),
            relief="flat",
            activebackground="#45e765",
            activeforeground="#282a36",
            command=guardar_producto,
            width=20,
            pady=8
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="⬅️ Cancelar",
            bg="#6272a4",
            fg="white",
            font=("Trebuchet MS", 14, "bold"),
            relief="flat",
            activebackground="#535c90",
            activeforeground="white",
            command=self.mostrar_inventario,
            width=20,
            pady=8
        ).pack(side="left", padx=10)

    def editar_producto(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="Editar Producto",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        if not self.productos:
            tk.Label(
                self.panel,
                text="⚠️ No hay productos para editar.",
                font=("Trebuchet MS", 14),
                bg="#282a36",
                fg="#f8f8f2"
            ).pack(pady=20)
            return

        sel_frame = tk.Frame(self.panel, bg="#282a36")
        sel_frame.pack(pady=10)

        tk.Label(sel_frame, text="Selecciona el producto:", font=("Trebuchet MS", 12), bg="#282a36", fg="white").pack()

        selected_codigo = tk.StringVar()
        opciones = [f"{prod['codigo']} - {prod['nombre']}" for prod in self.productos]

        from tkinter import ttk
        combo = ttk.Combobox(sel_frame, values=opciones, textvariable=selected_codigo, state="readonly",
                             font=("Trebuchet MS", 13))
        combo.pack(pady=5)

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TCombobox',
                        fieldbackground='#44475a',
                        background='#44475a',
                        foreground='white',
                        selectbackground='#50fa7b',
                        selectforeground='black',
                        bordercolor='#6272a4',
                        lightcolor='#50fa7b',
                        darkcolor='#6272a4',
                        arrowcolor='white',
                        padding=5,
                        relief='flat',
                        font=("Trebuchet MS", 13))

        form_frame = tk.Frame(self.panel, bg="#282a36")
        form_frame.pack(pady=10)

        entradas = {}
        campos = ["nombre", "cantidad", "precio", "proveedor", "categoria"]

        for campo in campos:
            tk.Label(form_frame, text=campo.capitalize() + ":", font=("Trebuchet MS", 13), bg="#282a36", fg="white",
                     anchor="w").pack(fill="x", padx=15, pady=(10, 3))
            entrada = tk.Entry(
                form_frame,
                font=("Trebuchet MS", 14),
                bg="#44475a",
                fg="white",
                insertbackground="white",
                relief="flat",
                highlightthickness=1,
                highlightcolor="#50fa7b",
                highlightbackground="#6272a4",
                borderwidth=0,
                width=30
            )
            entrada.pack(padx=15, fill="x")
            entradas[campo] = entrada

        def cargar_datos(*args):
            seleccion = selected_codigo.get()
            if not seleccion:
                return
            codigo = seleccion.split(" - ")[0]
            producto = next((p for p in self.productos if p["codigo"] == codigo), None)
            if producto:
                entradas["nombre"].delete(0, tk.END)
                entradas["nombre"].insert(0, producto["nombre"])
                entradas["cantidad"].delete(0, tk.END)
                entradas["cantidad"].insert(0, producto["cantidad"])
                entradas["precio"].delete(0, tk.END)
                entradas["precio"].insert(0, producto["precio"])
                entradas["proveedor"].delete(0, tk.END)
                entradas["proveedor"].insert(0, producto["proveedor"])
                entradas["categoria"].delete(0, tk.END)
                entradas["categoria"].insert(0, producto["categoria"])

        combo.bind("<<ComboboxSelected>>", cargar_datos)

        def guardar_cambios():
            seleccion = selected_codigo.get()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Selecciona un producto.")
                return

            codigo = seleccion.split(" - ")[0]
            nuevos_datos = {campo: entradas[campo].get() for campo in campos}

            if not nuevos_datos["nombre"] or not nuevos_datos["cantidad"] or not nuevos_datos["precio"]:
                messagebox.showwarning("Campos requeridos", "Nombre, cantidad y precio son obligatorios.")
                return

            try:
                nuevos_datos["cantidad"] = int(nuevos_datos["cantidad"])
                nuevos_datos["precio"] = float(nuevos_datos["precio"])
            except ValueError:
                messagebox.showerror("Error", "Cantidad debe ser número entero y precio un número decimal.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE productos
                SET nombre = ?, cantidad = ?, precio = ?, proveedor = ?, categoria = ?
                WHERE codigo = ?
            """, (
                nuevos_datos["nombre"],
                nuevos_datos["cantidad"],
                nuevos_datos["precio"],
                nuevos_datos["proveedor"],
                nuevos_datos["categoria"],
                codigo
            ))
            conn.commit()
            conn.close()
            self.cargar_productos_desde_db()
            messagebox.showinfo("Éxito", f"Producto '{codigo}' actualizado.")
            self.mostrar_inventario()
            self.registrar_alerta(f"Producto: '{nuevos_datos['nombre']}', de código: '{codigo}', ha sido editado.")

        btn_frame = tk.Frame(self.panel, bg="#282a36")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="💾 Guardar Cambios", font=("Trebuchet MS", 12), bg="#50fa7b", fg="#282a36",
        command=guardar_cambios).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="⬅️ Cancelar", font=("Trebuchet MS", 12), bg="#ff5555", fg="white",
        command=self.mostrar_inventario).grid(row=0, column=1, padx=10)
        
    def eliminar_producto(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="❌ Eliminar Producto",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        campos = ["Código del Producto"]
        entradas = {}

        form_frame = tk.Frame(self.panel, bg="#282a36")
        form_frame.pack(padx=40, pady=10, fill="x")

        for campo in campos:
            tk.Label(
                form_frame,
                text=f"{campo}:",
                font=("Trebuchet MS", 13),
                bg="#282a36",
                fg="white",
                anchor="w"
            ).pack(fill="x", pady=(10, 3))

            entry = tk.Entry(
                form_frame,
                font=("Trebuchet MS", 14),
                bg="#44475a",
                fg="white",
                insertbackground="white",
                relief="flat",
                highlightthickness=1,
                highlightcolor="#50fa7b",
                highlightbackground="#6272a4",
                borderwidth=0,
                width=30
            )
            entry.pack(fill="x")
            entradas[campo] = entry

        def confirmar_eliminacion():
            codigo = entradas["Código del Producto"].get().strip()

            if not codigo:
                messagebox.showwarning("Advertencia", "Debe ingresar un código de producto.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
            producto = cursor.fetchone()

            if not producto:
                conn.close()
                messagebox.showerror("Error", f"No se encontró el producto con código '{codigo}'.")
                return

            confirmar = messagebox.askyesno(
                "Confirmar",
                f"¿Está seguro que desea eliminar el producto '{producto[2]}'?"
            )
            if confirmar:
                cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
                conn.commit()
                conn.close()
                self.cargar_productos_desde_db()
                messagebox.showinfo("Éxito", f"Producto '{producto[2]}' eliminado.")
                self.mostrar_inventario()
                self.registrar_alerta(f"Producto: '{producto[2]}', de código: '{codigo}', ha sido eliminado")
            else:
                conn.close()

        tk.Button(
            self.panel,
            text="❌ Eliminar",
            font=("Trebuchet MS", 12, "bold"),
            bg="#ff5555",
            fg="white",
            relief="flat",
            command=confirmar_eliminacion
        ).pack(pady=10)

        tk.Button(
            self.panel,
            text="⬅️ Cancelar",
            font=("Trebuchet MS", 12, "bold"),
            bg="#6c757d",
            fg="white",
            relief="flat",
            command=self.mostrar_inventario
        ).pack()

    def consultar_productos(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="🔍 Consultar Productos",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        consultas_frame = tk.Frame(self.panel, bg="#282a36")
        consultas_frame.pack(pady=20)

        botones = [
            ("🆔 Por Código (ID)", self.consulta_por_codigo),
            ("📂 Por Categoría", self.consulta_por_categoria),
            ("🏭 Por Proveedor", self.consulta_por_proveedor),
            ("💲 Por Rango de Precios", self.consulta_por_precio),
            ("📦 Por Rango de Cantidades", self.consulta_por_cantidad),
        ]

        for i, (texto, comando) in enumerate(botones):
            tk.Button(
                consultas_frame,
                text=texto,
                font=("Trebuchet MS", 13),
                bg="#8be9fd",
                fg="#282a36",
                relief="flat",
                command=comando,
                width=25
            ).grid(row=i, column=0, pady=8)

        tk.Button(
            self.panel,
            text="↩️ Volver al Inventario",
            font=("Trebuchet MS", 12),
            bg="#6c757d",
            fg="white",
            relief="flat",
            command=self.mostrar_inventario
        ).pack(pady=10)

    def consulta_por_codigo(self):
        self.mostrar_formulario_consulta("🆔 Consultar por Código", "Código del Producto", "codigo")

    def consulta_por_categoria(self):
        self.mostrar_formulario_consulta("📂 Consultar por Categoría", "Categoría", "categoria")

    def consulta_por_proveedor(self):
        self.mostrar_formulario_consulta("🏭 Consultar por Proveedor", "Proveedor", "proveedor")

    def consulta_por_precio(self):
        self.mostrar_rango_consulta("💲 Consultar por Rango de Precios", "precio", float)

    def consulta_por_cantidad(self):
        self.mostrar_rango_consulta("📦 Consultar por Rango de Cantidades", "cantidad", int)

    def mostrar_formulario_consulta(self, titulo, label_text, campo_db):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text=titulo,
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        form_frame = tk.Frame(self.panel, bg="#282a36")
        form_frame.pack(padx=40, pady=10, fill="x")

        tk.Label(
            form_frame,
            text=label_text + ":",
            font=("Trebuchet MS", 13),
            bg="#282a36",
            fg="white",
            anchor="w"
        ).pack(fill="x", pady=(10, 3))

        use_combobox = campo_db in ["codigo", "categoria", "proveedor"]
        entry = None

        if use_combobox:
            from tkinter import ttk
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if campo_db == "codigo":
                cursor.execute("SELECT codigo FROM productos")
            elif campo_db == "categoria":
                cursor.execute("SELECT DISTINCT categoria FROM productos")
            elif campo_db == "proveedor":
                cursor.execute("SELECT DISTINCT proveedor FROM productos")

            valores = [row[0] for row in cursor.fetchall()]
            conn.close()

            entry = ttk.Combobox(
                form_frame,
                values=valores,
                font=("Trebuchet MS", 13),
                state="readonly"
            )
            entry.pack(fill="x")
        else:
            entry = tk.Entry(
                form_frame,
                font=("Trebuchet MS", 14),
                bg="#44475a",
                fg="white",
                insertbackground="white",
                relief="flat",
                highlightthickness=1,
                highlightcolor="#50fa7b",
                highlightbackground="#6272a4",
                borderwidth=0,
                width=30
            )
            entry.pack(fill="x")

        def ejecutar_busqueda():
            valor = entry.get().strip()
            if not valor:
                messagebox.showerror("Error", "Debe ingresar un valor para consultar.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM productos WHERE {campo_db} LIKE ?", (f"%{valor}%",))
            resultados = cursor.fetchall()
            conn.close()

            self.mostrar_resultados_consulta(resultados)

        tk.Button(
            self.panel,
            text="🔍 Buscar",
            font=("Trebuchet MS", 12),
            bg="#8be9fd",
            fg="#282a36",
            relief="flat",
            command=ejecutar_busqueda
        ).pack(pady=10)

        tk.Button(
            self.panel,
            text="↩️ Volver",
            font=("Trebuchet MS", 12),
            bg="#6c757d",
            fg="white",
            relief="flat",
            command=self.consultar_productos
        ).pack()

    def mostrar_rango_consulta(self, titulo, campo_db, tipo_dato):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text=titulo,
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        tk.Label(
            self.panel,
            text="Mínimo:",
            font=("Trebuchet MS", 13),
            bg="#282a36",
            fg="white",
            anchor="w"
        ).pack(fill="x", padx=40, pady=(10, 3))

        min_entry = tk.Entry(
            self.panel,
            font=("Trebuchet MS", 14),
            bg="#44475a",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#50fa7b",
            highlightbackground="#6272a4",
            borderwidth=0,
            width=30
        )
        min_entry.pack(padx=40, fill="x")

        tk.Label(
            self.panel,
            text="Máximo:",
            font=("Trebuchet MS", 13),
            bg="#282a36",
            fg="white",
            anchor="w"
        ).pack(fill="x", padx=40, pady=(10, 3))

        max_entry = tk.Entry(
            self.panel,
            font=("Trebuchet MS", 14),
            bg="#44475a",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#50fa7b",
            highlightbackground="#6272a4",
            borderwidth=0,
            width=30
        )
        max_entry.pack(padx=40, fill="x")

        def ejecutar_busqueda():
            try:
                min_val = tipo_dato(min_entry.get().strip())
                max_val = tipo_dato(max_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM productos WHERE {campo_db} BETWEEN ? AND ?", (min_val, max_val))
            resultados = cursor.fetchall()
            conn.close()

            self.mostrar_resultados_consulta(resultados)

        tk.Button(
            self.panel,
            text="🔍 Buscar",
            font=("Trebuchet MS", 12),
            bg="#8be9fd",
            fg="#282a36",
            relief="flat",
            command=ejecutar_busqueda
        ).pack(pady=10)

        tk.Button(
            self.panel,
            text="↩️ Volver",
            font=("Trebuchet MS", 12),
            bg="#6c757d",
            fg="white",
            relief="flat",
            command=self.consultar_productos
        ).pack()

    def mostrar_resultados_consulta(self, resultados):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="📋 Resultados de la Consulta",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        frame_tabla = tk.Frame(self.panel, bg="#282a36")
        frame_tabla.pack(padx=20, pady=10, fill="both", expand=True)

        columnas = ("codigo", "nombre", "categoria", "proveedor", "precio", "cantidad")

        tabla = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            style="Custom.Treeview"
        )

        tabla.heading("codigo", text="🆔 Código")
        tabla.heading("nombre", text="📦 Nombre")
        tabla.heading("categoria", text="🏷️ Categoría")
        tabla.heading("proveedor", text="🧾 Proveedor")
        tabla.heading("precio", text="💲 Precio")
        tabla.heading("cantidad", text="📦 Cantidad")

        tabla.column("codigo", anchor="center", width=100)
        tabla.column("nombre", anchor="center", width=150)
        tabla.column("categoria", anchor="center", width=130)
        tabla.column("proveedor", anchor="center", width=130)
        tabla.column("precio", anchor="center", width=100)
        tabla.column("cantidad", anchor="center", width=130)

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)

        tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        if not resultados:
            messagebox.showinfo("Sin resultados", "No se encontraron productos que coincidan.")
            self.consultar_productos()
            return

        for fila in resultados:
            tabla.insert("", "end", values=(fila[1], fila[2], fila[6], fila[5], fila[4], fila[3]))

        tk.Button(
            self.panel,
            text="↩️ Volver a Consultas",
            font=("Trebuchet MS", 12),
            bg="#6c757d",
            fg="white",
            relief="flat",
            command=self.consultar_productos
        ).pack(pady=15)

    def registrar_venta(self):
        venta = []
        total = 0

        def agregar_al_carrito():
            seleccion = lista.curselection()
            if not seleccion:
                return
            index = seleccion[0]
            producto = self.productos[index]

            cantidad = cantidad_entry.get()
            try:
                cantidad = int(cantidad)
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
                return

            if cantidad > producto["cantidad"]:
                messagebox.showwarning("Stock insuficiente", f"Solo hay {producto['cantidad']} unidades disponibles.")
                return

            venta.append((producto, cantidad))
            total_carrito = sum(p["precio"] * c for p, c in venta)
            resumen_var.set(f"{len(venta)} productos - Total: ${total_carrito}")

        def finalizar_venta():
            nonlocal total
            if not venta:
                messagebox.showinfo("Venta vacía", "No se ha agregado ningún producto.")
                return

            cliente = cliente_entry.get()
            if not cliente:
                messagebox.showwarning("Falta información", "Debe ingresar el nombre del cliente.")
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            for producto, cantidad in venta:
                producto["cantidad"] -= cantidad
                total += producto["precio"] * cantidad

                cursor.execute("UPDATE productos SET cantidad = ? WHERE codigo = ?", (producto["cantidad"], producto["codigo"]))
                if producto["cantidad"] <= 3:
                    self.registrar_alerta(f"Stock crítico tras venta: '{producto['nombre']}' tiene solo {producto['cantidad']} unidades.")

            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO ventas (cliente, total, fecha) VALUES (?, ?, ?)", (cliente, total, fecha))
            venta_id = cursor.lastrowid

            for producto, cantidad in venta:
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, producto_codigo, cantidad, precio_unitario)
                    VALUES (?, ?, ?, ?)
                """, (venta_id, producto["codigo"], cantidad, producto["precio"]))

            self.actualizar_ingresos(total)

            conn.commit()
            conn.close()

            self.registrar_alerta(f"Venta realizada para cliente '{cliente}': total ${total}")

            messagebox.showinfo("Venta registrada", f"Total de la venta: ${total}")
            self.cargar_productos_desde_db()
            self.mostrar_panel("Ventas")

        for widget in self.panel.winfo_children():
            widget.destroy()

        self.panel.config(bg="#282a36")

        tk.Label(
            self.panel,
            text="🛒 Registrar Venta",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        tk.Label(
            self.panel,
            text="Nombre del Cliente:",
            font=("Trebuchet MS", 12),
            bg="#282a36",
            fg="white",
            anchor="w"
        ).pack(fill="x", padx=20)
        cliente_entry = tk.Entry(
            self.panel,
            font=("Trebuchet MS", 12),
            bg="#44475a",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#50fa7b",
            highlightbackground="#6272a4",
            borderwidth=0,
            width=30
        )
        cliente_entry.pack(pady=10, padx=20, fill="x")

        tk.Label(
            self.panel,
            text="Seleccione el producto a vender:",
            font=("Trebuchet MS", 14, "bold"),
            bg="#282a36",
            fg="white",
            pady=10
        ).pack()

        lista_frame = tk.Frame(self.panel, bg="#282a36")
        lista_frame.pack(padx=20, pady=10, fill="x")

        scrollbar = tk.Scrollbar(lista_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        lista = tk.Listbox(
            lista_frame,
            font=("Trebuchet MS", 12),
            width=60,
            height=8,
            bg="#44475a",
            fg="white",
            selectbackground="#50fa7b",
            selectforeground="#282a36",
            highlightthickness=1,
            highlightcolor="#50fa7b",
            highlightbackground="#6272a4",
            borderwidth=0,
            relief="flat",
            yscrollcommand=scrollbar.set
        )
        for prod in self.productos:
            lista.insert(tk.END, f"{prod['nombre']} - ${prod['precio']} - Stock: {prod['cantidad']}")
        lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=lista.yview)

        tk.Label(
            self.panel,
            text="Cantidad:",
            font=("Trebuchet MS", 12),
            bg="#282a36",
            fg="white",
            anchor="w"
        ).pack(fill="x", padx=20)
        cantidad_entry = tk.Entry(
            self.panel,
            font=("Trebuchet MS", 12),
            bg="#44475a",
            fg="white",
            insertbackground="white",
            relief="flat",
            highlightthickness=1,
            highlightcolor="#50fa7b",
            highlightbackground="#6272a4",
            borderwidth=0,
            width=30
        )
        cantidad_entry.pack(pady=10, padx=20, fill="x")

        resumen_var = tk.StringVar()
        resumen_var.set("0 productos - Total: $0")
        tk.Label(
            self.panel,
            textvariable=resumen_var,
            font=("Trebuchet MS", 14),
            bg="#282a36",
            fg="#f8f8f2",
            pady=10
        ).pack()

        botones_frame = tk.Frame(self.panel, bg="#282a36")
        botones_frame.pack(pady=8)

        tk.Button(
            botones_frame,
            text="➕ Agregar al carrito",
            command=agregar_al_carrito,
            font=("Trebuchet MS", 14, "bold"),
            bg="#50fa7b",
            fg="#282a36",
            relief="flat",
            padx=15,
            pady=8,
            activebackground="#45e765",
            activeforeground="#282a36"
        ).grid(row=0, column=0, padx=15)

        tk.Button(
            botones_frame,
            text="✔️ Finalizar venta",
            command=finalizar_venta,
            font=("Trebuchet MS", 14, "bold"),
            bg="#8be9fd",
            fg="#282a36",
            relief="flat",
            padx=15,
            pady=8,
            activebackground="#6fd7f1",
            activeforeground="#282a36"
        ).grid(row=0, column=1, padx=15)

    def actualizar_ingresos(self, total_venta):
        fecha = datetime.now()
        dia = fecha.strftime("%Y-%m-%d")
        semana = fecha.strftime("%Y-%W")
        mes = fecha.strftime("%Y-%m")
        año = fecha.year

        self.ingresos["dia"][dia] = self.ingresos["dia"].get(dia, 0) + total_venta
        self.ingresos["semana"][semana] = self.ingresos["semana"].get(semana, 0) + total_venta
        self.ingresos["mes"][mes] = self.ingresos["mes"].get(mes, 0) + total_venta
        self.ingresos["año"][año] = self.ingresos["año"].get(año, 0) + total_venta
    
    def crear_grafica_ingresos(self):
        self.fig_ingresos = plt.Figure(figsize=(5,4), dpi=100)
        self.ax_ingresos = self.fig_ingresos.add_subplot(111)
        self.canvas_ingresos = FigureCanvasTkAgg(self.fig_ingresos, master=self.panel_graficas)  # panel donde se muestra
        self.canvas_ingresos.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def gestionar_usuarios(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        self.panel.config(bg="#282a36")

        tk.Label(
            self.panel,
            text="👥 Gestión de Usuarios",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=20
        ).pack()

        contenedor_scroll = tk.Frame(self.panel, bg="#282a36")
        contenedor_scroll.pack(fill="both", expand=True, padx=30, pady=10)

        canvas = tk.Canvas(contenedor_scroll, bg="#282a36", highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#282a36")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, rol FROM usuarios")
        usuarios_bd = cursor.fetchall()
        conn.close()

        for user in usuarios_bd:
            uid, nombre, rol_actual = user

            card = tk.Frame(scrollable_frame, bg="#44475a", bd=1, relief="flat", padx=15, pady=10)
            card.pack(fill="x", pady=8)

            info_frame = tk.Frame(card, bg="#44475a")
            info_frame.pack(side="left", fill="x", expand=True)

            tk.Label(
                info_frame,
                text=f"👤 {nombre}",
                font=("Trebuchet MS", 14, "bold"),
                bg="#44475a",
                fg="white"
            ).pack(anchor="w")

            tk.Label(
                info_frame,
                text=f"🔐 Rol actual: {rol_actual}",
                font=("Trebuchet MS", 12),
                bg="#44475a",
                fg="#f1fa8c"
            ).pack(anchor="w", pady=(2, 0))

            def cambiar_rol(uid=uid, usuario=nombre):
                nuevo_rol = simpledialog.askstring(
                    "Cambiar Rol",
                    f"Ingrese nuevo rol para {usuario}:\n(Admin, Vendedor, Bodega, Gerente)"
                )
                if nuevo_rol:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (nuevo_rol, uid))
                    conn.commit()
                    conn.close()
                    self.registrar_alerta(f"Rol de '{usuario}' cambiado a: {nuevo_rol}")
                    messagebox.showinfo("Éxito", f"Rol de '{usuario}' actualizado a {nuevo_rol}.")
                    self.gestionar_usuarios()

            tk.Button(
                card,
                text="✏️ Cambiar Rol",
                command=cambiar_rol,
                font=("Trebuchet MS", 11, "bold"),
                bg="#ffb86c",
                fg="#282a36",
                relief="flat",
                padx=10,
                pady=4,
                activebackground="#ffa94d",
                activeforeground="white"
            ).pack(side="right", padx=10, anchor="e")

    def generar_reportes(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        self.panel.config(bg="#282a36")

        tk.Label(
            self.panel,
            text="🧾 Historial de Ventas",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=20
        ).pack()

        contenedor_scroll = tk.Frame(self.panel, bg="#282a36")
        contenedor_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(contenedor_scroll, bg="#282a36", highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#282a36")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente, total, fecha FROM ventas ORDER BY id DESC")
        ventas_db = cursor.fetchall()

        for i, (venta_id, cliente, total, fecha) in enumerate(ventas_db):
            card = tk.Frame(scrollable_frame, bg="#44475a", bd=1, relief="flat", padx=15, pady=10)
            card.pack(fill="x", pady=8)

            tk.Label(
                card,
                text=f"🧾 Venta #{venta_id}",
                font=("Trebuchet MS", 14, "bold"),
                bg="#44475a",
                fg="white"
            ).pack(anchor="w")

            tk.Label(
                card,
                text=f"👤 Cliente: {cliente}",
                font=("Trebuchet MS", 12),
                bg="#44475a",
                fg="#f8f8f2"
            ).pack(anchor="w")

            tk.Label(
                card,
                text=f"💰 Total: ${total}     📅 Fecha: {fecha}",
                font=("Trebuchet MS", 12),
                bg="#44475a",
                fg="#f1fa8c"
            ).pack(anchor="w", pady=(2, 0))

            def exportar_pdf(vid=venta_id, vcliente=cliente, vtotal=total, vfecha=fecha): 
                try: 
                    if getattr(sys, 'frozen', False):
                        BASE_DIR = os.path.dirname(sys.executable) 
                    else:
                        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

                    nombre_archivo = f"ticket_venta_{vid}_{vcliente.replace(' ', '_')}.pdf"
                    ruta_archivo = os.path.join(BASE_DIR, nombre_archivo)

                    c = Canvas(ruta_archivo, pagesize=letter)
                    width, height = letter

                    c.setFont("Helvetica-Bold", 16)
                    c.drawCentredString(width / 2, height - 60, f"FACTURA DE VENTA #{vid}")

                    c.setFont("Helvetica", 12)
                    c.line(40, height - 70, width - 40, height - 70)

                    c.drawString(50, height - 100, f"Cliente: {vcliente}")
                    c.drawString(50, height - 120, f"Fecha: {vfecha}")
                    c.drawString(50, height - 140, f"Total: ${vtotal}")
                    c.drawString(50, height - 170, "Detalle de productos:")

                    y = height - 200
                    c.setFont("Helvetica-Bold", 11)
                    c.drawString(60, y, "Producto")
                    c.drawString(300, y, "Cantidad")
                    c.drawString(400, y, "Precio Unitario")
                    c.line(40, y - 5, width - 40, y - 5)

                    conn_detalle = sqlite3.connect(DB_PATH)
                    cursor_detalle = conn_detalle.cursor()
                    cursor_detalle.execute("""
                        SELECT p.nombre, dv.cantidad, dv.precio_unitario
                        FROM detalle_ventas dv
                        JOIN productos p ON p.codigo = dv.producto_codigo
                        WHERE dv.venta_id = ?
                    """, (vid,))
                    detalles = cursor_detalle.fetchall()
                    conn_detalle.close()

                    y -= 30
                    c.setFont("Helvetica", 10)
                    for nombre, cantidad, precio in detalles:
                        if y < 100:
                            c.showPage()
                            y = height - 100
                        c.drawString(60, y, nombre)
                        c.drawString(300, y, str(cantidad))
                        c.drawString(400, y, f"${precio}")
                        y -= 20

                    c.save()
                    messagebox.showinfo("PDF generado", f"Se creó el archivo:\n{ruta_archivo}")
                    print(f"Ruta del PDF: {ruta_archivo}")

                except Exception as e:
                    messagebox.showerror("Error al generar PDF", str(e))
                    print("Error al generar PDF:", e)

            tk.Button(
                card,
                text="💾 Guardar Ticket",
                command=exportar_pdf,
                font=("Trebuchet MS", 11, "bold"),
                bg="#50fa7b",
                fg="#282a36",
                relief="flat",
                padx=10,
                pady=4,
                activebackground="#3ee577",
                activeforeground="white"
            ).pack(side="right", padx=10)

        conn.close()

    def ver_metricas(self):
        self.panel.configure(bg="#282a36")

        for widget in self.panel.winfo_children():
            widget.destroy()

        titulo = tk.Label(
            self.panel,
            text="📈 Métricas y Estadísticas",
            font=("Trebuchet MS", 22, "bold"),
            bg="#282a36",
            fg="white",
            pady=20
        )
        titulo.pack()

        botones_frame = tk.Frame(self.panel, bg="#282a36")
        botones_frame.pack(pady=10)

        resumen_label = tk.Label(
            self.panel,
            text="Selecciona una métrica para ver detalles",
            font=("Trebuchet MS", 14),
            bg="#282a36",
            fg="#f8f8f2",
            wraplength=600,
            justify="center",
            pady=15
        )
        resumen_label.pack()

        grafica_frame = tk.Frame(self.panel, bg="#282a36")
        grafica_frame.pack(expand=True, fill="both", padx=20, pady=10)

        def limpiar_grafica():
            for widget in grafica_frame.winfo_children():
                widget.destroy()

        def graficar_barras(etiquetas, valores, titulo_grafica, color="#50fa7b"):
            limpiar_grafica()
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
            ax.bar(etiquetas, valores, color=color)
            ax.set_title(titulo_grafica, fontsize=14)
            ax.set_ylabel("Cantidad")
            ax.tick_params(axis='x', rotation=90)
            plt.tight_layout()

            canvas_fig = FigureCanvasTkAgg(fig, master=grafica_frame)
            canvas_fig.draw()
            canvas_fig.get_tk_widget().pack(expand=True, fill='both')

        def mostrar_mas_vendidos():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.nombre, SUM(dv.cantidad) as total_vendidos
                    FROM detalle_ventas dv
                    JOIN productos p ON dv.producto_codigo = p.codigo
                    GROUP BY dv.producto_codigo
                    ORDER BY total_vendidos DESC
                    LIMIT 10
                """)
                resultados = cursor.fetchall()
                conn.close()

                if not resultados:
                    resumen_label.config(text="No hay ventas registradas.")
                    limpiar_grafica()
                    return

                resumen_label.config(text="📊 Gráfica de Productos más vendidos (top 10)")

                nombres = [r[0] for r in resultados]
                cantidades = [r[1] for r in resultados]

                graficar_barras(nombres, cantidades, "Ventas por Producto")

            except Exception as e:
                resumen_label.config(text=f"Error al obtener ventas: {str(e)}")
                limpiar_grafica()

        def mostrar_costosos():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT nombre, precio
                    FROM productos
                    ORDER BY precio DESC
                    LIMIT 10
                """)
                resultados = cursor.fetchall()
                conn.close()

                if not resultados:
                    resumen_label.config(text="No hay datos de productos.")
                    limpiar_grafica()
                    return

                resumen_label.config(text="📊 Gráfica de Productos más costosos (top 10)")

                nombres = [r[0] for r in resultados]
                precios = [r[1] for r in resultados]

                graficar_barras(nombres, precios, "Precio por Producto", color="#ff79c6")

            except Exception as e:
                resumen_label.config(text=f"Error al obtener precios: {str(e)}")
                limpiar_grafica()

        def mostrar_ingresos():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT date(fecha) as dia, SUM(total) 
                    FROM ventas
                    WHERE fecha >= date('now', '-7 day')
                    GROUP BY dia
                    ORDER BY dia
                """)
                ingresos_dia = cursor.fetchall()

                cursor.execute("""
                    SELECT strftime('%Y-%W', fecha) as semana, SUM(total)
                    FROM ventas
                    WHERE fecha >= date('now', '-28 day')
                    GROUP BY semana
                    ORDER BY semana
                """)
                ingresos_semana = cursor.fetchall()

                cursor.execute("""
                    SELECT strftime('%Y-%m', fecha) as mes, SUM(total)
                    FROM ventas
                    WHERE fecha >= date('now', '-365 day')
                    GROUP BY mes
                    ORDER BY mes
                """)
                ingresos_mes = cursor.fetchall()

                cursor.execute("""
                    SELECT strftime('%Y', fecha) as año, SUM(total)
                    FROM ventas
                    GROUP BY año
                    ORDER BY año
                """)
                ingresos_año = cursor.fetchall()

                conn.close()

                total_dia = sum([v[1] for v in ingresos_dia]) if ingresos_dia else 0
                total_semana = sum([v[1] for v in ingresos_semana]) if ingresos_semana else 0
                total_mes = sum([v[1] for v in ingresos_mes]) if ingresos_mes else 0
                total_año = sum([v[1] for v in ingresos_año]) if ingresos_año else 0

                periodos = ["Día (7d)", "Semana (4s)", "Mes (12m)", "Año"]
                valores = [total_dia, total_semana, total_mes, total_año]

                if all(v == 0 for v in valores):
                    resumen_label.config(text="No hay datos de ingresos para mostrar.")
                    limpiar_grafica()
                    return

                resumen_label.config(text="📊 Gráfica de Ingresos Totales")

                graficar_barras(periodos, valores, "Ingresos por Periodo", color="#bd93f9")

            except Exception as e:
                resumen_label.config(text=f"Error al obtener ingresos: {str(e)}")
                limpiar_grafica()

        botones = [
            ("Productos más vendidos", mostrar_mas_vendidos),
            ("Productos más costosos", mostrar_costosos),
            ("Ingresos totales", mostrar_ingresos)
        ]

        for texto, comando in botones:
            tk.Button(
                botones_frame,
                text=texto,
                font=("Trebuchet MS", 12, "bold"),
                bg="#44475a",
                fg="white",
                activebackground="#6272a4",
                activeforeground="white",
                relief="flat",
                command=comando,
                width=25
            ).pack(side="left", padx=5, pady=5)

    def mostrar_alertas(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        # Título
        tk.Label(
            self.panel,
            text="📢 Alertas del Sistema",
            font=("Trebuchet MS", 22, "bold"),
            bg="#282a36",
            fg="white",
            pady=20
        ).pack()

        # Contenedor principal de alertas
        alertas_frame = tk.Frame(self.panel, bg="#282a36")
        alertas_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Alerta de stock bajo (consultando directamente la BD)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, cantidad FROM productos WHERE cantidad <= 3")
        productos_bajo_stock = cursor.fetchall()

        for nombre, cantidad in productos_bajo_stock:
            tk.Label(
                alertas_frame,
                text=f"⚠️ ¡Stock bajo! Producto: {nombre} ({cantidad} unidades)",
                fg="#ff5555",
                bg="#282a36",
                font=("Trebuchet MS", 14, "bold"),
                anchor="w"
            ).pack(fill="x", pady=5)

        # Alertas registradas en la tabla 'alertas'
        cursor.execute("SELECT mensaje, fecha FROM alertas ORDER BY fecha DESC LIMIT 50")
        alertas_guardadas = cursor.fetchall()
        conn.close()

        if alertas_guardadas:
            for mensaje, fecha in alertas_guardadas:
                tk.Label(
                    alertas_frame,
                    text=f"🔔 [{fecha}] {mensaje}",
                    fg="#50fa7b",
                    bg="#282a36",
                    font=("Trebuchet MS", 13),
                    anchor="w",
                    wraplength=600,
                    justify="left"
                ).pack(fill="x", pady=3)
        else:
            tk.Label(
                alertas_frame,
                text="No hay alertas registradas en el sistema.",
                fg="#bd93f9",
                bg="#282a36",
                font=("Trebuchet MS", 14, "italic"),
                anchor="center",
                pady=30
            ).pack()

        # Botón para recargar
        tk.Button(
            self.panel,
            text="🔄 Actualizar Alertas",
            font=("Trebuchet MS", 12, "bold"),
            bg="#6272a4",
            fg="white",
            relief="flat",
            command=self.mostrar_alertas,
            padx=10,
            pady=8
        ).pack(pady=20)

    def mostrar_stock(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        tk.Label(
            self.panel,
            text="📊 Stock Disponible",
            font=("Trebuchet MS", 20, "bold"),
            bg="#282a36",
            fg="white",
            pady=15
        ).pack()

        table_frame = tk.Frame(self.panel, bg="#282a36")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#44475a",
                        foreground="white",
                        fieldbackground="#44475a",
                        font=("Trebuchet MS", 12),
                        rowheight=30)
        style.map("Treeview", background=[('selected', '#50fa7b')],
                                foreground=[('selected', '#282a36')])
        style.configure("Treeview.Heading",
                        background="#6272a4",
                        foreground="white",
                        font=("Trebuchet MS", 13, "bold"))

        columns = ("nombre", "cantidad")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        tree.heading("nombre", text="📦 Producto")
        tree.heading("cantidad", text="🔢 Cantidad en Stock")

        tree.column("nombre", width=300, anchor="w")
        tree.column("cantidad", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for prod in self.productos:
            tree.insert("", "end", values=(
                prod.get("nombre", ""),
                prod.get("cantidad", 0)
            ))

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = SIGIVApp()
    app.mainloop()