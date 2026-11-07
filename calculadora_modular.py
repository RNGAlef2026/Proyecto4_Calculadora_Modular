
import ast
import tkinter as tk
from tkinter import ttk


# ============================================================
# 1. OPERACIONES MATEMATICAS
# ============================================================

# Limites practicos para mantener la GUI responsiva.
MAX_MODULO = 1_000_000_000
MAX_CARACTERES = 300
MAX_NODOS = 100
MAX_PROFUNDIDAD = 25
MAX_EXPONENTE = 100_000
MAX_BITS_EXPONENTE = 32


def es_primo(n):
    """Prueba de primalidad por divisores hasta sqrt(n)."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def inverso_modular(a, p):
    """Inverso multiplicativo en Zp; cero no tiene inverso."""
    a %= p
    if a == 0:
        raise ValueError("Division modular indefinida: el divisor equivale a 0 (mod p).")
    return pow(a, -1, p)


def validar_arbol(nodo):
    """Rechaza construcciones ajenas a la gramatica y arboles complejos."""
    permitidos = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                  ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
                  ast.UAdd, ast.USub, ast.Load)
    pila = [(nodo, 0)]
    cantidad = 0
    while pila:
        actual, profundidad = pila.pop()
        cantidad += 1
        if cantidad > MAX_NODOS or profundidad > MAX_PROFUNDIDAD:
            raise ValueError("Expresion demasiado compleja (longitud o anidamiento).")
        if not isinstance(actual, permitidos):
            raise ValueError("La expresion contiene nombres u operaciones no permitidas.")
        if isinstance(actual, ast.Constant) and type(actual.value) is not int:
            raise ValueError("Solo se permiten numeros enteros.")
        pila.extend((hijo, profundidad + 1) for hijo in ast.iter_child_nodes(actual))


def evaluar_exponente(nodo):
    """Evalua exponentes enteros acotados, sin reducirlos modulo p."""
    if isinstance(nodo, ast.Constant):
        valor = nodo.value
    elif isinstance(nodo, ast.UnaryOp):
        a = evaluar_exponente(nodo.operand)
        if isinstance(nodo.op, ast.USub):
            valor = -a
        elif isinstance(nodo.op, ast.UAdd):
            valor = a
        else:
            raise ValueError("Signo no permitido en el exponente.")
    elif isinstance(nodo, ast.BinOp):
        a = evaluar_exponente(nodo.left)
        b = evaluar_exponente(nodo.right)
        if isinstance(nodo.op, ast.Add):
            valor = a + b
        elif isinstance(nodo.op, ast.Sub):
            valor = a - b
        elif isinstance(nodo.op, ast.Mult):
            valor = a * b
        elif isinstance(nodo.op, ast.Pow):
            if b < 0:
                raise ValueError("No se permiten exponentes fraccionarios en exponentes anidados.")
            if b > MAX_EXPONENTE or (abs(a) > 1 and b * abs(a).bit_length() > MAX_BITS_EXPONENTE + 32):
                raise ValueError("Exponente intermedio demasiado grande.")
            valor = a ** b
        else:
            raise ValueError("El exponente debe ser una expresion entera sin division.")
    else:
        raise ValueError("Exponente no valido.")
    if abs(valor) > MAX_EXPONENTE:
        raise ValueError(f"Exponente demasiado grande (maximo {MAX_EXPONENTE}).")
    return valor


def evaluar_nodo(nodo, p, pasos=None):
    """Evalua el AST de manera segura y registra los pasos de calculo."""
    def registrar(texto):
        if pasos is not None:
            pasos.append(texto)

    if isinstance(nodo, ast.Constant):
        valor = nodo.value % p
        registrar(f"Reducir {nodo.value} modulo {p} = {valor}")
        return valor

    if isinstance(nodo, ast.UnaryOp):
        valor = evaluar_nodo(nodo.operand, p, pasos)
        if isinstance(nodo.op, ast.USub):
            resultado = (-valor) % p
            registrar(f"Negacion: (-{valor}) mod {p} = {resultado}")
            return resultado
        if isinstance(nodo.op, ast.UAdd):
            return valor
        raise ValueError("Operador unario no permitido.")

    if isinstance(nodo, ast.BinOp):
        izquierda = evaluar_nodo(nodo.left, p, pasos)
        if isinstance(nodo.op, ast.Pow):
            exponente = evaluar_exponente(nodo.right)
            if izquierda == 0 and exponente < 0:
                raise ValueError("Cero no admite exponentes negativos.")
            resultado = pow(izquierda, exponente, p)
            if exponente < 0:
                inverso = inverso_modular(izquierda, p)
                registrar(f"Inverso de {izquierda} modulo {p} = {inverso}")
                registrar(f"Potencia negativa: {izquierda}^{exponente} = {inverso}^{-exponente} mod {p} = {resultado}")
            else:
                registrar(f"Potencia: {izquierda}^{exponente} mod {p} = {resultado}")
            return resultado

        derecha = evaluar_nodo(nodo.right, p, pasos)
        if isinstance(nodo.op, ast.Add):
            resultado = (izquierda + derecha) % p
            registrar(f"Suma: ({izquierda} + {derecha}) mod {p} = {resultado}")
        elif isinstance(nodo.op, ast.Sub):
            resultado = (izquierda - derecha) % p
            registrar(f"Resta: ({izquierda} - {derecha}) mod {p} = {resultado}")
        elif isinstance(nodo.op, ast.Mult):
            resultado = (izquierda * derecha) % p
            registrar(f"Multiplicacion: ({izquierda} x {derecha}) mod {p} = {resultado}")
        elif isinstance(nodo.op, ast.Div):
            inverso = inverso_modular(derecha, p)
            registrar(f"Inverso de {derecha} modulo {p} = {inverso}, porque ({derecha} x {inverso}) mod {p} = 1")
            resultado = (izquierda * inverso) % p
            registrar(f"Division: ({izquierda} / {derecha}) mod {p} = ({izquierda} x {inverso}) mod {p} = {resultado}")
        else:
            raise ValueError("Operacion no permitida.")
        return resultado
    raise ValueError("Expresion matematica no valida.")


def calcular_con_procedimiento(expresion, p):
    """Devuelve (resultado, lista de pasos) para mostrar en la GUI."""
    if type(p) is not int or not 2 <= p <= MAX_MODULO:
        raise ValueError(f"El modulo debe ser un entero entre 2 y {MAX_MODULO}.")
    if not es_primo(p):
        raise ValueError(f"El modulo {p} no es primo.")
    expresion = expresion.strip()
    if not expresion:
        raise ValueError("Debes ingresar una expresion.")
    if len(expresion) > MAX_CARACTERES:
        raise ValueError(f"La expresion no debe superar {MAX_CARACTERES} caracteres.")
    permitidos = set("0123456789+-*/^() \t")
    for caracter in expresion:
        if caracter not in permitidos:
            raise ValueError(f"Caracter no permitido: {caracter!r}.")
    try:
        arbol = ast.parse(expresion.replace("^", "**"), mode="eval")
    except (SyntaxError, ValueError) as error:
        raise ValueError("Error de sintaxis: revisa los parentesis y operadores.") from error
    validar_arbol(arbol)
    pasos = [f"Expresion: {expresion}", f"Trabajamos en Z_{p} (modulo primo {p})."]
    resultado = evaluar_nodo(arbol.body, p, pasos)
    pasos.append(f"RESULTADO FINAL: {resultado} (mod {p})")
    return resultado, pasos


def calcular_modular(expresion, p):
    """Compatibilidad con la funcion original."""
    return calcular_con_procedimiento(expresion, p)[0]


# ============================================================
# 2. EJEMPLOS DE LA TAREA
# ============================================================

EJEMPLOS = {
    "Ejemplo 1 - mod 23": (
        "(7^3 + 4 * 5) * 2",
        23
    ),

    "Ejemplo 2 - mod 29": (
        "((15 + 7) * 3 - 2^4) / 5",
        29
    ),

    "Ejemplo 3 - mod 31": (
        "(3^4 * 2 + 7) / (11 - 5^2)",
        31
    ),

    "Ejemplo 4 - mod 37": (
        "(8 * (13 + 5^2) - 3^3) / (2^4 + 1)",
        37
    ),

    "Ejemplo 5 - mod 41": (
        "((6^2 * 3 + 7) / (2^3 - 5)) * "
        "(11 + 4^3) - 9",
        41
    )
}


# ============================================================
# 3. INTERFAZ GRAFICA
# ============================================================

class CalculadoraModular:

    def __init__(self, ventana):

        self.ventana = ventana

        self.ventana.title(
            "Calculadora de Aritmetica Modular"
        )

        self.ventana.geometry("900x850")
        self.ventana.minsize(700, 680)

        # Colores
        self.fondo = "#0F172A"
        self.panel = "#1E293B"
        self.entrada = "#334155"
        self.azul = "#6366F1"
        self.azul_hover = "#818CF8"
        self.texto = "#F8FAFC"
        self.secundario = "#94A3B8"
        self.verde = "#34D399"
        self.rojo = "#FB7185"

        self.ventana.configure(
            bg=self.fondo
        )

        # Variables de la interfaz
        self.expresion = tk.StringVar()
        self.modulo = tk.StringVar(value="23")
        self.resultado = tk.StringVar(value="--")

        self.estado = tk.StringVar(
            value="Ingresa una expresion para comenzar."
        )

        self.crear_estilos()
        self.crear_interfaz()

        # Atajos
        self.ventana.bind(
            "<Return>",
            lambda evento: self.calcular()
        )

        self.ventana.bind(
            "<Escape>",
            lambda evento: self.limpiar()
        )

    # --------------------------------------------------------
    # ESTILOS
    # --------------------------------------------------------

    def crear_estilos(self):

        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Modular.TCombobox",
            fieldbackground=self.entrada,
            background=self.entrada,
            foreground=self.texto,
            arrowcolor=self.texto,
            padding=8
        )

        estilo.map(
            "Modular.TCombobox",
            fieldbackground=[
                ("readonly", self.entrada)
            ],
            foreground=[
                ("readonly", self.texto)
            ]
        )

    # --------------------------------------------------------
    # BOTONES
    # --------------------------------------------------------

    def crear_boton(
        self, padre, texto, comando,
        color, ancho
    ):

        boton = tk.Button(
            padre,
            text=texto,
            command=comando,
            bg=color,
            fg=self.texto,
            activebackground=self.azul_hover,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            width=ancho,
            height=2,
            cursor="hand2"
        )

        return boton

    # --------------------------------------------------------
    # CONSTRUCCION DE LA INTERFAZ
    # --------------------------------------------------------

    def crear_interfaz(self):

        # Contenido desplazable: los paneles nunca quedan inaccesibles
        # en pantallas pequenas o con escalado de fuentes.
        contenedor = tk.Frame(self.ventana, bg=self.fondo)
        contenedor.pack(fill="both", expand=True)

        self.canvas_principal = tk.Canvas(
            contenedor, bg=self.fondo, highlightthickness=0, bd=0
        )
        barra_principal = ttk.Scrollbar(
            contenedor, orient="vertical",
            command=self.canvas_principal.yview
        )
        self.canvas_principal.configure(yscrollcommand=barra_principal.set)
        barra_principal.pack(side="right", fill="y")
        self.canvas_principal.pack(side="left", fill="both", expand=True)

        principal = tk.Frame(
            self.canvas_principal, bg=self.fondo, padx=28, pady=20
        )
        self.contenido_principal = principal
        self.id_contenido = self.canvas_principal.create_window(
            (0, 0), window=principal, anchor="nw"
        )

        def actualizar_region(evento=None):
            self.canvas_principal.configure(
                scrollregion=self.canvas_principal.bbox("all")
            )

        def ajustar_ancho(evento):
            self.canvas_principal.itemconfigure(
                self.id_contenido, width=evento.width
            )

        principal.bind("<Configure>", actualizar_region)
        self.canvas_principal.bind("<Configure>", ajustar_ancho)

        # Desplazamiento con rueda en el area principal, sin interferir
        # con el desplazamiento propio del campo de procedimiento.
        def rueda(evento):
            widget = self.ventana.winfo_containing(evento.x_root, evento.y_root)
            if widget is self.campo_pasos:
                return
            if evento.num == 4:
                unidades = -3
            elif evento.num == 5:
                unidades = 3
            else:
                unidades = -int(evento.delta / 120) * 3
            if unidades:
                self.canvas_principal.yview_scroll(unidades, "units")

        self.canvas_principal.bind("<MouseWheel>", rueda)
        self.canvas_principal.bind("<Button-4>", rueda)
        self.canvas_principal.bind("<Button-5>", rueda)

        # ENCABEZADO

        tk.Label(
            principal,
            text="CALCULADORA MODULAR",
            bg=self.fondo,
            fg=self.texto,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")

        tk.Label(
            principal,
            text="Operaciones en Zp | p es un numero primo",
            bg=self.fondo,
            fg=self.secundario,
            font=("Segoe UI", 11)
        ).pack(
            anchor="w",
            pady=(5, 18)
        )

        # ----------------------------------------------------
        # PANEL DE ENTRADA
        # ----------------------------------------------------

        panel_entrada = tk.Frame(
            principal,
            bg=self.panel,
            padx=20,
            pady=16
        )

        panel_entrada.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            panel_entrada,
            text="EXPRESION MATEMATICA",
            bg=self.panel,
            fg=self.secundario,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.campo_expresion = tk.Entry(
            panel_entrada,
            textvariable=self.expresion,
            bg=self.entrada,
            fg=self.texto,
            insertbackground=self.texto,
            font=("Consolas", 16),
            relief="flat",
            bd=0
        )

        self.campo_expresion.pack(
            fill="x",
            ipady=11,
            pady=(9, 15)
        )

        tk.Label(
            panel_entrada,
            text="MODULO PRIMO (p)",
            bg=self.panel,
            fg=self.secundario,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.campo_modulo = tk.Entry(
            panel_entrada,
            textvariable=self.modulo,
            bg=self.entrada,
            fg=self.texto,
            insertbackground=self.texto,
            font=("Consolas", 15),
            relief="flat",
            bd=0,
            width=12
        )

        self.campo_modulo.pack(
            anchor="w",
            ipady=7,
            pady=(9, 14)
        )

        acciones = tk.Frame(
            panel_entrada,
            bg=self.panel
        )

        acciones.pack(fill="x")

        self.crear_boton(
            acciones,
            "CALCULAR",
            self.calcular,
            self.azul,
            14
        ).pack(
            side="left",
            padx=(0, 12)
        )

        self.crear_boton(
            acciones,
            "LIMPIAR",
            self.limpiar,
            self.entrada,
            12
        ).pack(side="left")

        # ----------------------------------------------------
        # PANEL DE RESULTADOS
        # ----------------------------------------------------

        panel_resultado = tk.Frame(
            principal,
            bg=self.panel,
            padx=20,
            pady=15
        )

        panel_resultado.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            panel_resultado,
            text="RESULTADO",
            bg=self.panel,
            fg=self.secundario,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.etiqueta_resultado = tk.Label(
            panel_resultado,
            textvariable=self.resultado,
            bg=self.panel,
            fg=self.verde,
            font=("Consolas", 28, "bold"),
            anchor="w"
        )

        self.etiqueta_resultado.pack(
            fill="x",
            pady=(7, 5)
        )

        self.etiqueta_estado = tk.Label(
            panel_resultado,
            textvariable=self.estado,
            bg=self.panel,
            fg=self.secundario,
            font=("Segoe UI", 10),
            anchor="w",
            wraplength=650,
            justify="left"
        )

        self.etiqueta_estado.pack(fill="x")

        # PANEL DE PROCEDIMIENTO (se crea antes de los callbacks)
        panel_pasos = tk.Frame(
            principal, bg=self.panel, padx=20, pady=15
        )
        panel_pasos.pack(fill="both", expand=True, pady=(0, 10))

        tk.Label(
            panel_pasos, text="PROCEDIMIENTO MATEMATICO",
            bg=self.panel, fg=self.secundario,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 10))

        contenedor_pasos = tk.Frame(panel_pasos, bg=self.panel)
        contenedor_pasos.pack(fill="both", expand=True)

        scroll_pasos = tk.Scrollbar(contenedor_pasos)
        scroll_pasos.pack(side="right", fill="y")

        self.campo_pasos = tk.Text(
            contenedor_pasos, bg=self.entrada, fg=self.texto,
            font=("Consolas", 11), relief="flat", bd=0,
            padx=12, pady=12, wrap="word", height=9,
            state="disabled", yscrollcommand=scroll_pasos.set
        )
        self.campo_pasos.pack(side="left", fill="both", expand=True)
        scroll_pasos.configure(command=self.campo_pasos.yview)
        self.panel_pasos = panel_pasos


        # ----------------------------------------------------
        # PANEL DE EJEMPLOS
        # ----------------------------------------------------

        panel_ejemplos = tk.Frame(
            principal,
            bg=self.panel,
            padx=20,
            pady=15
        )

        panel_ejemplos.pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            panel_ejemplos,
            text="EJEMPLOS DE LA TAREA",
            bg=self.panel,
            fg=self.secundario,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        self.combo_ejemplos = ttk.Combobox(
            panel_ejemplos,
            values=list(EJEMPLOS.keys()),
            state="readonly",
            style="Modular.TCombobox",
            font=("Segoe UI", 11)
        )

        self.combo_ejemplos.pack(
            fill="x",
            ipady=5
        )

        self.combo_ejemplos.set(
            "Selecciona un ejemplo para cargarlo..."
        )

        self.combo_ejemplos.bind(
            "<<ComboboxSelected>>",
            self.cargar_ejemplo
        )

        
        # ----------------------------------------------------
        # AYUDA PARA ESCRIBIR EXPRESIONES
        # ----------------------------------------------------

        tk.Label(
            panel_ejemplos,
            text="¿COMO ESCRIBIR UNA EXPRESION?",
            bg=self.panel,
            fg=self.secundario,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w",
            pady=(18, 7)
        )

        tk.Label(
            panel_ejemplos,
            text=(
                "Usa ^ para potencias, * para multiplicar, "
                "/ para division modular y ( ) para agrupar."
            ),
            bg=self.panel,
            fg=self.texto,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            wraplength=700
        ).pack(
            fill="x",
            pady=(0, 10)
        )

        tk.Label(
            panel_ejemplos,
            text="Ejemplo: (2^3 + 5) / 7",
            bg=self.panel,
            fg=self.verde,
            font=("Consolas", 12, "bold"),
            anchor="w"
        ).pack(fill="x")


        self.campo_expresion.focus_set()

    def mostrar_pasos(self, pasos):
        """Actualiza el panel desplazable de solo lectura."""
        self.campo_pasos.configure(state="normal")
        self.campo_pasos.delete("1.0", "end")
        if pasos:
            self.campo_pasos.insert("end", "\n\n".join(
                f"{indice}. {paso}" for indice, paso in enumerate(pasos, 1)
            ))
        self.campo_pasos.configure(state="disabled")
        self.campo_pasos.yview_moveto(0)
        if pasos:
            self.ventana.after_idle(self.enfocar_procedimiento)

    def enfocar_procedimiento(self):
        """Asegura que el panel de pasos sea accesible tras calcular."""
        self.ventana.update_idletasks()
        alto_total = self.contenido_principal.winfo_reqheight()
        alto_visible = self.canvas_principal.winfo_height()
        if alto_total <= alto_visible:
            return
        # Desplaza solo lo necesario para mostrar el borde inferior del panel.
        inferior = self.panel_pasos.winfo_y() + self.panel_pasos.winfo_height()
        superior = self.panel_pasos.winfo_y()
        desplazamiento = self.canvas_principal.canvasy(0)
        if inferior > desplazamiento + alto_visible:
            destino = (inferior - alto_visible + 12) / alto_total
            self.canvas_principal.yview_moveto(max(0, min(1, destino)))
        elif superior < desplazamiento:
            self.canvas_principal.yview_moveto(max(0, superior / alto_total))

    # --------------------------------------------------------
    # LIMPIAR
    # --------------------------------------------------------

    def limpiar(self):

        self.expresion.set("")
        self.resultado.set("--")
        self.mostrar_pasos([])

        self.estado.set(
            "Ingresa una expresion para comenzar."
        )

        self.etiqueta_resultado.configure(
            fg=self.verde
        )

        self.combo_ejemplos.set(
            "Selecciona un ejemplo para cargarlo..."
        )

        self.campo_expresion.focus_set()

    # --------------------------------------------------------
    # CARGAR EJEMPLOS
    # --------------------------------------------------------

    def cargar_ejemplo(self, evento=None):

        seleccion = self.combo_ejemplos.get()

        if seleccion in EJEMPLOS:

            expresion, p = EJEMPLOS[seleccion]

            self.expresion.set(expresion)
            self.modulo.set(str(p))

            self.resultado.set("--")
            self.mostrar_pasos([])

            self.estado.set(
                "Ejemplo cargado. Presiona CALCULAR."
            )

            self.etiqueta_resultado.configure(
                fg=self.verde
            )

            self.campo_expresion.focus_set()

    # --------------------------------------------------------
    # CALCULAR
    # --------------------------------------------------------

    def calcular(self):

        try:

            texto_modulo = self.modulo.get().strip()

            if not texto_modulo:
                raise ValueError(
                    "Debes ingresar un modulo primo."
                )

            try:
                p = int(texto_modulo)

            except ValueError:
                raise ValueError(
                    "El modulo debe ser un numero entero."
                )

            expresion = self.expresion.get()

            respuesta, pasos = calcular_con_procedimiento(
                expresion, p
            )
            self.mostrar_pasos(pasos)

            self.resultado.set(
                f"{respuesta} (mod {p})"
            )

            self.estado.set(
                "Operacion realizada correctamente."
            )

            self.etiqueta_resultado.configure(
                fg=self.verde
            )

        except (
            ValueError,
            ZeroDivisionError,
            OverflowError,
            RecursionError
        ) as error:

            self.resultado.set("ERROR")
            self.mostrar_pasos([])

            self.estado.set(str(error))

            self.etiqueta_resultado.configure(
                fg=self.rojo
            )


# ============================================================
# 4. EJECUCION
# ============================================================

if __name__ == "__main__":

    ventana = tk.Tk()

    aplicacion = CalculadoraModular(ventana)

    ventana.mainloop()
