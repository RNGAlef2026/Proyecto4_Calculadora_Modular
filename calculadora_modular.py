
import ast
import tkinter as tk
from tkinter import ttk


# ============================================================
# 1. OPERACIONES MATEMATICAS
# ============================================================

def es_primo(n):
    """Verifica si un numero es primo."""

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
    """Calcula el inverso multiplicativo modulo p."""

    a = a % p

    if a == 0:
        raise ValueError(
            "No existe inverso modular para cero."
        )

    return pow(a, -1, p)


def evaluar_exponente(nodo, p):
    """
    Calcula exponentes enteros sin reducirlos
    modulo p antes de realizar la potencia.
    """

    if isinstance(nodo, ast.Constant):
        if type(nodo.value) is not int:
            raise ValueError("Solo se permiten enteros.")
        return nodo.value

    if isinstance(nodo, ast.UnaryOp):
        valor = evaluar_exponente(nodo.operand, p)

        if isinstance(nodo.op, ast.USub):
            return -valor

        if isinstance(nodo.op, ast.UAdd):
            return valor

    if isinstance(nodo, ast.BinOp):
        a = evaluar_exponente(nodo.left, p)
        b = evaluar_exponente(nodo.right, p)

        if isinstance(nodo.op, ast.Add):
            return a + b

        if isinstance(nodo.op, ast.Sub):
            return a - b

        if isinstance(nodo.op, ast.Mult):
            return a * b

        if isinstance(nodo.op, ast.Pow):
            if b < 0:
                raise ValueError(
                    "El exponente debe ser entero no negativo."
                )
            if b > 10000:
                raise ValueError(
                    "Exponente demasiado grande."
                )
            return a ** b

    raise ValueError(
        "Exponente no valido."
    )


def evaluar_nodo(nodo, p):
    """Evalua expresiones mediante AST."""

    if isinstance(nodo, ast.Constant):

        if type(nodo.value) is not int:
            raise ValueError(
                "Solo se permiten numeros enteros."
            )

        return nodo.value % p

    if isinstance(nodo, ast.UnaryOp):

        valor = evaluar_nodo(nodo.operand, p)

        if isinstance(nodo.op, ast.USub):
            return (-valor) % p

        if isinstance(nodo.op, ast.UAdd):
            return valor

        raise ValueError("Operador no permitido.")

    if isinstance(nodo, ast.BinOp):

        izquierda = evaluar_nodo(nodo.left, p)

        # Potencias
        if isinstance(nodo.op, ast.Pow):

            exponente = evaluar_exponente(
                nodo.right, p
            )

            if exponente < 0:
                if izquierda == 0:
                    raise ValueError(
                        "Cero no admite exponentes negativos."
                    )
                return pow(izquierda, exponente, p)

            return pow(izquierda, exponente, p)

        derecha = evaluar_nodo(nodo.right, p)

        # Suma
        if isinstance(nodo.op, ast.Add):
            return (izquierda + derecha) % p

        # Resta
        if isinstance(nodo.op, ast.Sub):
            return (izquierda - derecha) % p

        # Multiplicacion
        if isinstance(nodo.op, ast.Mult):
            return (izquierda * derecha) % p

        # Division modular
        if isinstance(nodo.op, ast.Div):

            inverso = inverso_modular(
                derecha, p
            )

            return (izquierda * inverso) % p

        raise ValueError(
            "Operacion no permitida."
        )

    raise ValueError(
        "Expresion matematica no valida."
    )


def calcular_modular(expresion, p):
    """Valida y resuelve una expresion modular."""

    if not es_primo(p):
        raise ValueError(
            "El modulo p debe ser un numero primo."
        )

    expresion = expresion.strip()

    if not expresion:
        raise ValueError(
            "Debes ingresar una expresion."
        )

    expresion = expresion.replace("^", "**")

    try:
        arbol = ast.parse(
            expresion,
            mode="eval"
        )

    except SyntaxError:
        raise ValueError(
            "La expresion tiene un error de sintaxis."
        )

    return evaluar_nodo(arbol.body, p)


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

        self.ventana.geometry("850x590")
        self.ventana.minsize(680, 650)

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

        principal = tk.Frame(
            self.ventana,
            bg=self.fondo,
            padx=28,
            pady=20
        )

        principal.pack(
            fill="both",
            expand=True
        )

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

    # --------------------------------------------------------
    # LIMPIAR
    # --------------------------------------------------------

    def limpiar(self):

        self.expresion.set("")
        self.resultado.set("--")

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

            respuesta = calcular_modular(
                expresion, p
            )

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
