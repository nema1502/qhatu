"""Base visual de Qhatu sobre el motor de animación nemaxyz (Manim).

El motor (comun/estilo.py y los auditores) no vive en este repo: se indica con la
variable de entorno NEMAXYZ_MOTOR. Acá está solo lo que es de Qhatu: la paleta,
el tema y los pocos elementos que arman cada lámina.

Una lámina del deck es una escena. Cada frase del guion es un «beat»: la imagen
se queda en pantalla lo que dura su frase (ver `Lamina.linea`).
"""

import json
import os
import sys
import textwrap
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent

MOTOR = Path(os.environ.get("NEMAXYZ_MOTOR", ""))
if not (MOTOR / "comun" / "estilo.py").is_file():
    raise SystemExit("Falta el motor de animación: definí NEMAXYZ_MOTOR con la carpeta de nemaxyz-motor.")
sys.path.insert(0, str(MOTOR))
sys.path.insert(0, str(AQUI.parent))

from manim import *  # noqa: E402,F401,F403
from comun import estilo  # noqa: E402
from comun.estilo import conectar, configurar_horizontal, encajar, icono, texto  # noqa: E402,F401

import guion  # noqa: E402,F401

# ---------------------------------------------------------------- paleta
MARINO = "#13203A"
MARINO_2 = "#1C2C4C"
CREMA = "#F6F2EA"
CREMA_2 = "#FFFCF6"
TERRA = "#A84A24"
TERRA_OSC = "#8F3E1E"
NARANJA = "#F0915A"
AZUL_GRIS = "#C9D2E3"
TINTA_SUAVE = "#3D4757"
BORDE_CLARO = "#E2D8C5"


@dataclass(frozen=True)
class Tema:
    fondo: str
    tinta: str      # texto principal
    suave: str      # texto secundario
    acento: str     # figuras de énfasis
    kicker: str     # color de la etiqueta de sección
    tarjeta: str
    borde: str
    ok: str
    alerta: str


OSCURO = Tema(MARINO, CREMA, AZUL_GRIS, NARANJA, NARANJA, MARINO_2, "#2E4270", "#3DDC84", "#FF7A6B")
CLARO = Tema(CREMA, MARINO, TINTA_SUAVE, TERRA, TERRA, CREMA_2, BORDE_CLARO, "#1F8A5B", "#C0392B")
TERRACOTA = Tema(TERRA, CREMA, "#F6E2D4", CREMA, CREMA, TERRA_OSC, "#C26A43", "#C8F2D2", "#FFD9B0")

configurar_horizontal(MARINO)
if os.environ.get("QHATU_BAJA"):          # vista previa rápida: misma imagen, menos píxeles
    config.pixel_width, config.pixel_height = 960, 540

FUENTE_TITULO = "Bahnschrift"
FUENTE_CUERPO = "Segoe UI"

IZQ = -6.3          # margen izquierdo del contenido
DER = 6.3
ANCHO = DER - IZQ   # 12.6 unidades útiles
Y_PIE = -3.45       # línea de fuentes
# Ancho medio de un carácter en español, por punto de fuente (medido sobre una lámina renderizada).
K_NORMAL = 0.0062
K_BOLD = 0.0068

RUTA_VOZ = Path(os.environ.get("QHATU_VOZ", RAIZ / "animaciones" / "render" / "voz" / "voz.json"))
DUR = json.loads(RUTA_VOZ.read_text(encoding="utf-8"))["duraciones"] if RUTA_VOZ.is_file() else {}
RETARDO = 0.20      # la voz entra un instante después de la imagen: el ojo ve y después el oído oye
PAUSA = 0.20        # aire entre una frase y la siguiente


# ---------------------------------------------------------------- texto
@contextmanager
def fuente(nombre):
    anterior = estilo.FUENTE
    estilo.FUENTE = nombre
    try:
        yield
    finally:
        estilo.FUENTE = anterior


def t_titulo(cadena, color, tamano=56):
    with fuente(FUENTE_TITULO):
        return texto(cadena, tamano=tamano, color=color)


def t_cuerpo(cadena, color, tamano=30, peso=NORMAL, max_ancho=None):
    return texto(cadena, tamano=tamano, color=color, peso=peso, max_ancho=max_ancho)


def parrafo(cadena, color, ancho, tamano=28, peso=NORMAL, buff=0.12, alineado=LEFT):
    """Texto en varias líneas que cabe en `ancho` unidades."""
    por_linea = max(8, int(ancho / ((K_BOLD if peso == BOLD else K_NORMAL) * tamano)))
    lineas = textwrap.wrap(cadena, width=por_linea)
    return VGroup(*[t_cuerpo(l, color, tamano, peso, max_ancho=ancho + 2.0) for l in lineas]) \
        .arrange(DOWN, aligned_edge=alineado, buff=buff)


def a_izq(m, x, y):
    """Coloca `m` con su borde izquierdo en x y su centro vertical en y."""
    return m.move_to([x + m.width / 2, y, 0])


def raya(a, b, tema, grosor=2):
    """Línea decorativa (separador, eje). Va marcada: el auditor no la toma por un conector."""
    linea = Line(a, b, stroke_color=tema.borde, stroke_width=grosor)
    linea.auditor_ignorar = True
    return linea


def caja(ancho, alto, tema, relleno=None, borde=None, radio=0.25, grosor=2.5):
    return RoundedRectangle(corner_radius=radio, width=ancho, height=alto,
                            fill_color=relleno or tema.tarjeta, fill_opacity=1,
                            stroke_color=borde or tema.borde, stroke_width=grosor)


def moneda(radio, tema, simbolo="$"):
    disco = Circle(radius=radio, fill_color=tema.acento, fill_opacity=1,
                   stroke_color=tema.fondo, stroke_width=3)
    marca = t_titulo(simbolo, tema.fondo, tamano=int(radio * 85))
    marca.auditor_ignorar = True    # va sobre el disco, no sobre el fondo: el auditor mediría mal el contraste
    return VGroup(disco, marca.move_to(disco.get_center()))


def etiqueta_pie(cadena, tema):
    """Línea de fuentes al pie, discreta pero legible."""
    t = t_cuerpo(cadena, tema.suave, tamano=26, max_ancho=ANCHO)
    return t.move_to([IZQ + t.width / 2, Y_PIE, 0])


class Contador:
    """Número que sube de `desde` a `hasta`.

    Se agrega `.m` a la escena, se reproduce `.anim()` junto con lo demás y al
    terminar se llama a `.fijar()`: sin eso el texto se rearma en cada cuadro
    mientras dure la lámina, y el render se arrastra.
    """

    def __init__(self, pos, desde, hasta, formato, color, tamano=96, borde=ORIGIN):
        self.v = ValueTracker(desde)
        self.hasta = hasta
        self.m = always_redraw(
            lambda: t_titulo(formato(self.v.get_value()), color, tamano).move_to(pos, aligned_edge=borde))

    def anim(self):
        return self.v.animate.set_value(self.hasta)

    def fijar(self, final=False):
        """`final=True` salta al valor de llegada (para la vista fija de la lámina)."""
        if final:
            self.v.set_value(self.hasta)
            self.m.update(0)
        self.m.clear_updaters()
        return self.m


def coma(x, decimales=1):
    """Decimal con coma, como se escribe en Bolivia."""
    return f"{x:.{decimales}f}".replace(".", ",")


# ---------------------------------------------------------------- escena
class Lamina(Scene):
    """Una lámina del deck. Cada subclase define `cuerpo()`, `numero` y `tema`."""

    tema = OSCURO
    numero = 1          # lugar en el deck (1 a 8)
    nombre = "Lamina"
    con_marca = True    # la portada ya tiene el nombre en grande

    def __init__(self, *args, **kwargs):
        # El fondo es de la lámina: lo leen el render y también los auditores
        # (el de contraste mide contra config.background_color).
        config.background_color = self.tema.fondo
        super().__init__(*args, **kwargs)

    def setup(self):
        super().setup()
        self.marcas = {}
        self.instantanea = bool(os.environ.get("QHATU_SNAPSHOT"))
        self.add(self.cromo())

    def cromo(self):
        """Marca de Qhatu arriba a la izquierda y los puntos de avance a la derecha."""
        palabra = t_titulo("Qhatu", self.tema.kicker, tamano=30)
        palabra.move_to([IZQ + palabra.width / 2, 3.55, 0])
        palabra.auditor_ignorar = True
        palabra.es_marca_agua = True
        if not self.con_marca:
            palabra = VGroup()
        puntos = VGroup(*[
            Circle(radius=0.07, stroke_width=2, stroke_color=self.tema.kicker,
                   fill_color=self.tema.kicker, fill_opacity=1 if i + 1 == self.numero else 0)
            for i in range(8)
        ]).arrange(RIGHT, buff=0.22)
        puntos.move_to([DER - puntos.width / 2, 3.55, 0])
        puntos.auditor_ignorar = True
        grupo = VGroup(palabra, puntos)
        grupo.es_cromo = True
        grupo.auditor_ignorar = True
        return grupo

    def construct(self):
        self.cuerpo()
        self.salir()

    def cuerpo(self):
        raise NotImplementedError

    def encabezado(self, kicker, titulo, tamano=54):
        """Etiqueta de sección y título, alineados a la izquierda bajo la marca."""
        k = t_titulo(kicker.upper(), self.tema.kicker, tamano=28)
        t = t_titulo(titulo, self.tema.tinta, tamano=tamano)
        k.move_to([IZQ + k.width / 2, 3.0, 0])
        t.move_to([IZQ + t.width / 2, 2.4, 0])
        grupo = VGroup(k, t)
        self.play(FadeIn(grupo, shift=DOWN * 0.15), run_time=0.6)
        return grupo

    @contextmanager
    def linea(self, ident, pausa=PAUSA):
        """Un beat: lo que se anima adentro dura al menos lo que dura la frase.

        La voz de `ident` arranca RETARDO segundos después de entrar al bloque, y el
        bloque termina cuando la frase acabó más una pausa corta. La marca queda
        anotada para ubicar la voz en la línea de tiempo del video.
        """
        t0 = self.renderer.time
        self.marcas[ident] = t0 + RETARDO
        yield
        falta = RETARDO + DUR.get(ident, 3.0) + pausa - (self.renderer.time - t0)
        if falta > 0.01 and not self.instantanea:
            self.wait(falta)

    def pausar(self, segundos):
        if not self.instantanea:
            self.wait(segundos)

    def salir(self, run_time=0.5):
        if self.instantanea:
            return
        vivos = [m for m in self.mobjects if not getattr(m, "es_cromo", False)]
        if vivos:
            self.play(*[FadeOut(m) for m in vivos], run_time=run_time)

    def tear_down(self):
        super().tear_down()
        # Los tiempos solo se anotan cuando se renderiza de verdad (los pide el
        # orquestador con QHATU_TIEMPOS); los auditores y las vistas fijas no los tocan.
        if not os.environ.get("QHATU_TIEMPOS") or self.instantanea:
            return
        carpeta = Path(os.environ["QHATU_TIEMPOS"])
        carpeta.mkdir(parents=True, exist_ok=True)
        datos = {"escena": self.nombre, "duracion": round(self.renderer.time, 3),
                 "marcas": {k: round(v, 3) for k, v in self.marcas.items()}}
        (carpeta / f"{self.nombre}.json").write_text(json.dumps(datos, indent=2), encoding="utf-8")
