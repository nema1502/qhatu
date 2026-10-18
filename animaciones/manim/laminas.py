"""Las láminas del deck de Qhatu como escenas de Manim.

Se renderizan una por una. Las siete que están en el video llevan voz; la de
validación (S7) es solo para el deck y para las preguntas del jurado.

    NEMAXYZ_MOTOR=<carpeta del motor> python -m manim render laminas.py S2Problema

La vista fija de cada lámina (la que va al PDF del deck) se saca con
QHATU_SNAPSHOT=1 y la opción -s.
"""

import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qhatu_base import *  # noqa: E402,F403

DATOS = guion.DATOS
EQUIPO = DATOS["equipo"]


# ===================================================================== S1
class S1Portada(Lamina):
    tema = OSCURO
    numero = 1
    nombre = "S1Portada"
    con_marca = False

    def cuerpo(self):
        if not self.instantanea:
            self.historia()
        self.portada()

    def historia(self):
        """Una exportadora y un comprador que no se animan a ser el primero en confiar."""
        tm = self.tema

        def lado(nombre_icono, rotulo, detalle, x):
            ic = icono(nombre_icono, alto=1.3, color=tm.tinta)
            r = t_titulo(rotulo, tm.tinta, 34)
            d = t_cuerpo(detalle, tm.suave, 26)
            return VGroup(ic, r, d).arrange(DOWN, buff=0.18).move_to([x, 0.4, 0])

        exportadora = lado("warehouse", "Exportadora", "Bolivia", -4.8)
        comprador = lado("globe", "Comprador", "en el exterior", 4.8)
        y = exportadora[0].get_center()[1]
        enlace = DashedLine([-3.7, y, 0], [3.7, y, 0], dash_length=0.18,
                            stroke_color=tm.borde, stroke_width=4)
        enlace.auditor_ignorar = True   # raya decorativa: cada trazo corto se leería como un conector
        paquete = icono("box", alto=0.85, color=tm.acento).move_to([-3.0, y, 0])
        dinero = moneda(0.4, tm).move_to([3.0, y, 0])
        candado = icono("lock", alto=0.45, color=tm.alerta)

        def pregunta(cadena, x):
            p = parrafo(cadena, tm.tinta, 4.7, 28)
            c = caja(p.width + 0.8, p.height + 0.5, tm)
            return VGroup(c, p.move_to(c.get_center())).move_to([x, -1.75, 0])

        q_izq = pregunta("¿Despachar sin saber si le van a pagar?", -3.6)
        q_der = pregunta("¿Pagar por adelantado a alguien que nunca vio?", 3.6)
        titular = t_titulo("Hoy, uno de los dos paga a ciegas.", tm.acento, 52).move_to([0, 2.85, 0])

        with self.linea("s1_a"):
            self.play(FadeIn(exportadora, shift=RIGHT * 0.3), FadeIn(comprador, shift=LEFT * 0.3), run_time=0.9)
            self.play(Create(enlace), run_time=0.8)
            self.play(FadeIn(paquete, scale=0.4), FadeIn(dinero, scale=0.4), run_time=0.6)
        with self.linea("s1_b"):
            self.play(FadeIn(q_der, shift=UP * 0.2), dinero.animate.move_to([0.5, y, 0]), run_time=1.5)
            candado.move_to([0.5, y + 0.8, 0])
            self.play(FadeIn(candado, scale=0.4), Wiggle(dinero, scale_value=1.15, rotation_angle=0.06 * TAU),
                      run_time=0.9)
            self.play(FadeOut(candado), dinero.animate.move_to([3.0, y, 0]), run_time=1.0)
            self.play(FadeIn(q_izq, shift=UP * 0.2), paquete.animate.move_to([-0.5, y, 0]), run_time=1.5)
            candado.move_to([-0.5, y + 0.8, 0])
            self.play(FadeIn(candado, scale=0.4), Wiggle(paquete, scale_value=1.15, rotation_angle=0.06 * TAU),
                      run_time=0.9)
            self.play(FadeOut(candado), paquete.animate.move_to([-3.0, y, 0]), run_time=1.0)
        with self.linea("s1_c"):
            self.play(FadeIn(titular, scale=1.15), Indicate(paquete), Indicate(dinero), run_time=1.0)

    def portada(self):
        tm = self.tema
        kicker = a_izq(t_titulo("IDEATÓN STELLAR BOLIVIA · PAGOS Y REMESAS", tm.kicker, 28), IZQ, 3.0)
        nombre = a_izq(t_titulo("Qhatu", tm.tinta, 150), IZQ, 1.45)
        lema = a_izq(t_titulo("Tu proveedor cobra cuando cumple.", tm.acento, 52), IZQ, 0.1)
        sub = parrafo("Pagos condicionados por hitos en dólares digitales, para pymes que compran y "
                      "venden al exterior. Autoservicio, sobre Stellar.", tm.suave, 10.2, 30)
        sub.move_to([IZQ + sub.width / 2, -1.2, 0])
        equipo = a_izq(t_cuerpo(" · ".join(p["nombre"] for p in EQUIPO), tm.tinta, 28, peso=BOLD), IZQ, -2.95)
        sig = a_izq(t_cuerpo("Qhatu significa «mercado» en quechua", tm.suave, 26), IZQ, -3.45)
        motivo = VGroup(moneda(0.45, tm), icono("lock", alto=0.5, color=tm.tinta),
                        icono("box", alto=0.9, color=tm.acento)).arrange(RIGHT, buff=0.55).move_to([4.3, 1.5, 0])

        if self.instantanea:
            self.add(kicker, nombre, lema, sub, equipo, sig, motivo)
            return
        with self.linea("s1_d"):
            self.salir(0.5)
            self.play(FadeIn(kicker), run_time=0.4)
            self.play(LaggedStart(FadeIn(nombre, shift=UP * 0.3), FadeIn(lema, shift=UP * 0.2), FadeIn(sub),
                                  lag_ratio=0.35), run_time=1.6)
            self.play(FadeIn(motivo, scale=0.8), FadeIn(equipo), FadeIn(sig), run_time=0.8)


# ===================================================================== S2
class S2Problema(Lamina):
    tema = CLARO
    numero = 2
    nombre = "S2Problema"

    def cuerpo(self):
        tm = self.tema
        self.encabezado("El problema", "Alguien siempre paga a ciegas")

        ancho, alto, cy = 6.15, 3.5, -0.1
        izq = caja(ancho, alto, tm).move_to([IZQ + ancho / 2, cy, 0])
        der = caja(ancho, alto, tm).move_to([DER - ancho / 2, cy, 0])
        cx_i, cx_d = izq.get_center()[0], der.get_center()[0]
        arriba = cy + alto / 2
        margen_i, margen_d = cx_i - ancho / 2 + 0.4, cx_d - ancho / 2 + 0.4

        # ---------------------------------------------- Bolivia
        k_bo = a_izq(t_titulo("EN BOLIVIA", tm.kicker, 28), margen_i, arriba - 0.4)
        c_bo = a_izq(t_cuerpo("operaciones con activos virtuales", tm.suave, 26), margen_i, arriba - 0.85)

        base, h_max, ancho_b = -1.0, 1.0, 1.3
        x1, x2 = cx_i - 1.3, cx_i + 1.3
        h1 = h_max * 46.5 / 294
        barra1 = Rectangle(width=ancho_b, height=h1, stroke_width=0, fill_color="#CDBFA6", fill_opacity=1)
        barra2 = Rectangle(width=ancho_b, height=h_max, stroke_width=0, fill_color=tm.acento, fill_opacity=1)
        barra1.move_to([x1, base + h1 / 2, 0])
        barra2.move_to([x2, base + h_max / 2, 0])
        anio1 = t_cuerpo("S1 2024", tm.suave, 26).move_to([x1, base - 0.32, 0])
        anio2 = t_cuerpo("S1 2025", tm.suave, 26).move_to([x2, base - 0.32, 0])
        v1 = Contador([x1, base + h1 + 0.35, 0], 0, 46.5, lambda v: f"{coma(v)} M", tm.suave, 40)
        v2 = Contador([x2, base + h_max + 0.35, 0], 0, 294, lambda v: f"{v:.0f} M", tm.tinta, 40)

        # ---------------------------------------------- mundo
        k_mu = a_izq(t_titulo("EN EL MUNDO", tm.kicker, 28), margen_d, arriba - 0.4)
        n_mu = Contador([margen_d, arriba - 1.02, 0], 0, 2.5, lambda v: f"US$ {coma(v)} billones",
                        tm.tinta, 50, borde=LEFT)
        c_mu = VGroup(t_cuerpo("de brecha de financiamiento", tm.suave, 26),
                      t_cuerpo("al comercio", tm.suave, 26)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        a_izq(c_mu, margen_d, arriba - 1.78)
        centro = [margen_d + 0.5, arriba - 2.75, 0]
        pista = Circle(radius=0.45, stroke_width=11, stroke_color=tm.borde).move_to(centro)
        arco = Arc(radius=0.45, start_angle=PI / 2, angle=-2 * PI * 0.41, stroke_width=11,
                   stroke_color=tm.acento).move_arc_center_to(centro)
        pct = t_titulo("41%", tm.tinta, 24).move_to(centro)
        c_pct = parrafo("de las solicitudes de las pymes son rechazadas", tm.suave, 4.0, 26)
        c_pct.move_to([centro[0] + 0.75 + c_pct.width / 2, centro[1], 0])

        # ---------------------------------------------- pie
        alerta = icono("triangle-exclamation", alto=0.4, color=tm.alerta)
        aviso = t_cuerpo("Muchos pagan por adelantado y sin protección", tm.alerta, 28, peso=BOLD)
        fila = VGroup(alerta, aviso).arrange(RIGHT, buff=0.25)
        fila.move_to([IZQ + fila.width / 2, -2.3, 0])
        cierre = t_titulo("El pago ya existe. La confianza, no.", tm.tinta, 40)
        cierre.move_to([IZQ + cierre.width / 2, -2.95, 0])
        fuentes = etiqueta_pie("Fuentes: BCB (S1 = primer semestre, 2024 vs. 2025) · Banco Asiático de Desarrollo (ene-2026)", tm)

        if self.instantanea:
            self.add(izq, der, k_bo, c_bo, barra1, barra2, anio1, anio2, k_mu, c_mu,
                     pista, arco, pct, c_pct, fila, cierre, fuentes)
            for c in (v1, v2, n_mu):          # encima de las tarjetas, no debajo
                self.add(c.fijar(final=True))
            return

        with self.linea("s2_a"):
            self.play(FadeIn(izq, shift=UP * 0.2), FadeIn(k_bo), FadeIn(c_bo), run_time=0.7)
            self.add(v1.m, v2.m)
            self.play(FadeIn(anio1), FadeIn(anio2), run_time=0.4)
            self.play(GrowFromEdge(barra1, DOWN), GrowFromEdge(barra2, DOWN), v1.anim(), v2.anim(),
                      run_time=2.6, rate_func=rate_functions.ease_out_cubic)
            v1.fijar(), v2.fijar()
        with self.linea("s2_b"):
            self.play(FadeIn(fila, shift=UP * 0.15), run_time=0.6)
        with self.linea("s2_c"):
            self.play(FadeIn(der, shift=UP * 0.2), FadeIn(k_mu), run_time=0.7)
            self.add(n_mu.m)
            self.play(n_mu.anim(), FadeIn(c_mu), run_time=2.0, rate_func=rate_functions.ease_out_cubic)
            n_mu.fijar()
            self.play(FadeIn(pista), Create(arco), FadeIn(pct), FadeIn(c_pct), run_time=2.0)
        with self.linea("s2_d"):
            self.play(FadeIn(cierre, shift=UP * 0.2), FadeIn(fuentes), run_time=0.8)


# ===================================================================== S3
class S3Solucion(Lamina):
    tema = CLARO
    numero = 3
    nombre = "S3Solucion"

    PASOS = [
        ("01", "file-contract", "Trato con link", "Define monto, hitos y documentos."),
        ("02", "vault", "Depósito en escrow", "Deposita el 100% antes de producir."),
        ("03", "check-double", "Documentos verificados", "Reglas revisan documentos y contenedor."),
        ("04", "money-bill-wave", "Pago por hitos", "30% con el pedido y 70% con la guía."),
    ]

    def cuerpo(self):
        tm = self.tema
        self.encabezado("La solución", "Así funciona Qhatu", tamano=50)

        ancho, alto, hueco, cy = 2.95, 3.4, 0.267, 0.1
        tarjetas = []
        for i, (num, nombre_icono, titulo, desc) in enumerate(self.PASOS):
            cx = IZQ + ancho / 2 + i * (ancho + hueco)
            c = caja(ancho, alto, tm).move_to([cx, cy, 0])
            x = cx - ancho / 2 + 0.3
            n = a_izq(t_titulo(num, tm.kicker, 34), x, cy + alto / 2 - 0.5)
            ico = icono(nombre_icono, alto=0.5, color=tm.acento).move_to([cx + ancho / 2 - 0.55, n.get_center()[1], 0])
            texto_ = VGroup(parrafo(titulo, tm.tinta, 2.35, 28, peso=BOLD), parrafo(desc, tm.suave, 2.35, 26)) \
                .arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            texto_.next_to(n, DOWN, aligned_edge=LEFT, buff=0.3)
            tarjetas.append(VGroup(c, n, ico, texto_))

        # barra del escrow: se llena con el depósito y se libera por hitos
        y, h, w30 = -2.05, 0.46, ANCHO * 0.3
        pista = Rectangle(width=ANCHO, height=h, stroke_color=tm.borde, stroke_width=3, fill_opacity=0).move_to([0, y, 0])
        relleno = Rectangle(width=ANCHO, height=h, stroke_width=0, fill_color=tm.acento, fill_opacity=1).move_to(pista)
        ok30 = Rectangle(width=w30, height=h, stroke_width=0, fill_color=tm.ok, fill_opacity=1).move_to([IZQ + w30 / 2, y, 0])
        ok70 = Rectangle(width=ANCHO - w30, height=h, stroke_width=0, fill_color=tm.ok, fill_opacity=1) \
            .move_to([IZQ + w30 + (ANCHO - w30) / 2, y, 0])
        corte = Line([IZQ + w30, y + h / 2, 0], [IZQ + w30, y - h / 2, 0], stroke_color=tm.fondo, stroke_width=4)
        txt_dep = a_izq(t_cuerpo("Escrow en Stellar · 100% depositado", CREMA, 26, peso=BOLD), IZQ + 0.25, y)
        txt_30 = a_izq(t_cuerpo("30% liberado", CREMA, 26, peso=BOLD), IZQ + 0.25, y)
        txt_70 = a_izq(t_cuerpo("70% liberado", CREMA, 26, peso=BOLD), IZQ + w30 + 0.25, y)
        etq_30 = a_izq(t_cuerpo("pedido confirmado", tm.suave, 26), IZQ + 0.05, y - 0.5)
        etq_70 = a_izq(t_cuerpo("guía de embarque verificada", tm.suave, 26), IZQ + w30 + 0.05, y - 0.5)

        fila = VGroup(icono("lock", alto=0.42, color=tm.acento),
                      t_cuerpo("Qhatu nunca controla la plata", tm.acento, 30, peso=BOLD)).arrange(RIGHT, buff=0.25)
        fila.move_to([IZQ + fila.width / 2, -3.3, 0])

        if self.instantanea:
            self.add(*tarjetas, pista, relleno, ok30, ok70, corte, txt_30, txt_70, etq_30, etq_70, fila)
            return

        with self.linea("s3_a"):
            self.play(FadeIn(tarjetas[0], shift=UP * 0.25), run_time=0.8)
        with self.linea("s3_b"):
            self.play(FadeIn(tarjetas[1], shift=UP * 0.25), run_time=0.8)
            self.play(Create(pista), run_time=0.4)
            self.play(GrowFromEdge(relleno, LEFT), FadeIn(txt_dep), run_time=1.6)
        with self.linea("s3_c"):
            self.play(FadeIn(tarjetas[2], shift=UP * 0.25), run_time=0.8)
        with self.linea("s3_d"):
            self.play(FadeIn(tarjetas[3], shift=UP * 0.25), run_time=0.8)
            self.play(FadeOut(txt_dep), FadeIn(ok30), FadeIn(txt_30), FadeIn(corte), FadeIn(etq_30), run_time=0.9)
            self.pausar(1.5)
            self.play(FadeIn(ok70), FadeIn(txt_70), FadeIn(etq_70), run_time=0.9)
        with self.linea("s3_e"):
            self.play(FadeIn(fila, shift=UP * 0.2), run_time=0.6)


# ===================================================================== S5
class S5Stellar(Lamina):
    tema = OSCURO
    numero = 5
    nombre = "S5Stellar"

    def cuerpo(self):
        tm = self.tema
        self.encabezado("Por qué Stellar", "Construido sobre piezas que ya funcionan", tamano=46)

        ancho, alto, hueco, cy = 4.0, 2.15, 0.3, 0.7
        datos = [("Pollar", "La puerta", "Cuenta con Google o correo, sin cripto."),
                 ("Trustless Work", "La caja fuerte", "Escrow no custodial en mainnet."),
                 ("Qhatu", "Comercio exterior", "Arma el trato y revisa documentos.")]
        tarjetas = []
        for i, (nombre, rol, desc) in enumerate(datos):
            propia = nombre == "Qhatu"
            cx = IZQ + ancho / 2 + i * (ancho + hueco)
            c = caja(ancho, alto, tm, relleno=TERRA if propia else None, borde=TERRA if propia else None)
            c.move_to([cx, cy, 0])
            x = cx - ancho / 2 + 0.3
            n = a_izq(t_titulo(nombre, CREMA if propia else tm.acento, 34), x, cy + alto / 2 - 0.4)
            r = a_izq(t_cuerpo(rol, tm.tinta, 28, peso=BOLD), x, cy + alto / 2 - 0.9)
            d = parrafo(desc, CREMA if propia else tm.suave, 3.4, 26)
            d.next_to(r, DOWN, aligned_edge=LEFT, buff=0.15)
            tarjetas.append(VGroup(c, n, r, d))

        x2, x3, y0 = IZQ + 2.4, IZQ + 7.2, -0.8
        encabezado = VGroup(a_izq(t_titulo("HOY: CARTA DE CRÉDITO", tm.suave, 26), x2, y0),
                            a_izq(t_titulo("QHATU EN STELLAR", tm.acento, 26), x3, y0))
        filas = []
        for k, (concepto, hoy, qhatu) in enumerate([
                ("Acceso", "Línea de crédito aprobada", "Depósito del 100%, sin línea"),
                ("Trámite", "Papeleo bancario por etapa", "Un link y documentos subidos"),
                ("Liquidación", "Días entre bancos", "Segundos, en Stellar")]):
            y = y0 - 0.5 * (k + 1)
            filas.append(VGroup(
                raya([IZQ, y + 0.25, 0], [DER, y + 0.25, 0], tm),
                a_izq(t_cuerpo(concepto, tm.tinta, 26, peso=BOLD), IZQ, y),
                a_izq(t_cuerpo(hoy, tm.suave, 26), x2, y),
                a_izq(t_cuerpo(qhatu, tm.tinta, 26, peso=BOLD), x3, y)))
        eco = parrafo("Y queremos devolver algo al ecosistema: casos de uso reales para CAP-84 "
                      "(discusión #1950), SEP-59 (#1902) y CCTP (#2032).", tm.suave, 12.4, 26)
        eco.move_to([IZQ + eco.width / 2, -3.2, 0])

        if self.instantanea:
            self.add(*tarjetas, encabezado, *filas, eco)
            return

        with self.linea("s5_b"):
            self.play(FadeIn(tarjetas[0], shift=UP * 0.25), run_time=0.8)
        with self.linea("s5_c"):
            self.play(FadeIn(tarjetas[1], shift=UP * 0.25), run_time=0.8)
        with self.linea("s5_d"):
            self.play(FadeIn(tarjetas[2], shift=UP * 0.25), run_time=0.8)
        with self.linea("s5_e"):
            self.play(FadeIn(encabezado), run_time=0.5)
            for fila in filas:
                self.pausar(0.9)
                self.play(FadeIn(fila, shift=UP * 0.1), run_time=0.5)
            self.play(FadeIn(eco), run_time=0.6)


# ===================================================================== S6
class S6Modelo(Lamina):
    tema = TERRACOTA
    numero = 6
    nombre = "S6Modelo"

    def cuerpo(self):
        tm = self.tema
        kicker = a_izq(t_titulo("MODELO DE NEGOCIO", tm.kicker, 28), IZQ, 3.0)
        grande = a_izq(t_titulo("1–1,5%", tm.tinta, 140), IZQ, 1.75)
        de = a_izq(t_titulo("de cada trato", tm.tinta, 46), IZQ + 7.0, 2.05)
        minimo = parrafo("Mínimo US$ 75. Lo paga el comprador o se reparte.", tm.suave, 5.3, 28)
        minimo.move_to([IZQ + 7.0 + minimo.width / 2, 1.2, 0])

        # el costo frente a una carta de crédito, en la misma escala
        x0, largo = -3.0, 9.0           # de 0% a 3%

        def x_de(p):
            return x0 + largo * p / 3.0

        ya, yb, h = 0.3, -0.35, 0.42
        etq_a = a_izq(t_cuerpo("Carta de crédito", tm.tinta, 26), IZQ, ya)
        etq_b = a_izq(t_cuerpo("Qhatu", tm.tinta, 26, peso=BOLD), IZQ, yb)
        barra_a = Rectangle(width=x_de(3.0) - x_de(0.75), height=h, stroke_width=0, fill_color=tm.borde,
                            fill_opacity=1).move_to([(x_de(0.75) + x_de(3.0)) / 2, ya, 0])
        barra_b = Rectangle(width=x_de(1.5) - x_de(1.0), height=h, stroke_width=0, fill_color=CREMA,
                            fill_opacity=1).move_to([(x_de(1.0) + x_de(1.5)) / 2, yb, 0])
        val_a = t_cuerpo("0,75% a 3%", CREMA, 26, peso=BOLD).move_to(barra_a)
        val_b = a_izq(t_cuerpo("1–1,5%", CREMA, 26, peso=BOLD), x_de(1.5) + 0.2, yb)
        eje = raya([x0, -0.62, 0], [x_de(3.0), -0.62, 0], tm)
        marcas = VGroup(*[t_cuerpo(f"{p}%", tm.suave, 26).move_to([x_de(p), -0.9, 0]) for p in (0, 1, 2, 3)])

        filas = []
        for k, (titulo, desc) in enumerate([
                ("Kipu · fase 2", "Facturas y contabilidad automáticas, por suscripción."),
                ("Canales", "Despachantes y agentes de carga ganan por cada cliente."),
                ("Escenario base", "Hipótesis: ~US$ 37 mil el año 1 y ~US$ 446 mil el año 3.")]):
            y = -1.65 - 0.6 * k
            filas.append(VGroup(
                raya([IZQ, y + 0.3, 0], [DER, y + 0.3, 0], tm),
                a_izq(t_titulo(titulo, tm.tinta, 28), IZQ, y),
                a_izq(t_cuerpo(desc, tm.tinta, 26), IZQ + 3.4, y)))
        pie = etiqueta_pie("Escrow (Trustless Work): 0,3% por operación · Rangos de guías públicas · Cifras: hipótesis", tm)

        if self.instantanea:
            self.add(kicker, grande, de, minimo, etq_a, etq_b, barra_a, barra_b, val_a, val_b, eje, marcas, *filas, pie)
            return

        with self.linea("s6_a"):
            self.play(FadeIn(kicker), run_time=0.4)
            self.play(FadeIn(grande, scale=0.85), run_time=1.0)
            self.play(FadeIn(de, shift=LEFT * 0.2), FadeIn(minimo, shift=LEFT * 0.2), run_time=0.8)
        with self.linea("s6_b"):
            self.play(FadeIn(etq_a), FadeIn(etq_b), Create(eje), FadeIn(marcas), run_time=0.8)
            self.play(GrowFromEdge(barra_a, LEFT), FadeIn(val_a), run_time=1.0)
            self.play(GrowFromEdge(barra_b, LEFT), FadeIn(val_b), run_time=1.0)
        with self.linea("s6_c"):
            self.play(FadeIn(filas[0], shift=UP * 0.15), run_time=0.6)
        with self.linea("s6_d"):
            self.play(FadeIn(filas[1], shift=UP * 0.15), run_time=0.6)
        with self.linea("s6_e"):
            self.play(FadeIn(filas[2], shift=UP * 0.15), FadeIn(pie), run_time=0.6)


# ===================================================================== S7
class S7Validacion(Lamina):
    """Para el deck y para las preguntas del jurado: no va en el video."""

    tema = CLARO
    numero = 7
    nombre = "S7Validacion"

    def cuerpo(self):
        tm = self.tema
        self.encabezado("Validación y competencia", "Lo que sabemos y quién más está", tamano=46)

        ent = DATOS["entrevistas"]
        if ent["cantidad"]:
            charlas = f"{ent['cantidad']} entrevistas: {ent['hallazgo']}"
        else:
            charlas = "Entrevistas: todavía no. Evidencia de fuentes públicas."
        puntos = ["Hay uso real: el USDT «alivia a algunos importadores» en Bolivia.",
                  "Hay fraude documental: Trafigura perdió US$ 577 M.",
                  charlas,
                  "Sigue: 3 tratos reales en un piloto de 30 días."]

        k1 = a_izq(t_titulo("Lo que ya sabemos", tm.tinta, 32), IZQ, 1.5)
        lista = VGroup()
        y = 1.0
        for p in puntos:
            par = parrafo(p, tm.suave, 5.5, 26)
            par.move_to([IZQ + 0.4 + par.width / 2, y - par.height / 2, 0])
            punto = Dot(radius=0.07, color=tm.acento).move_to([IZQ + 0.1, par[0].get_center()[1], 0])
            lista.add(VGroup(punto, par))
            y -= par.height + 0.28

        x_der = 0.3
        k2 = a_izq(t_titulo("Competencia", tm.tinta, 32), x_der, 1.5)
        filas = []
        for k, (nombre, desc, propia) in enumerate([
                ("Trade Assurance", "Solo dentro de Alibaba", False),
                ("Tazapay", "Escrow B2B que valida documentos", False),
                ("CashAbroad y Eascrow", "Crédito y escrow en Stellar", False),
                ("Qhatu", "Por link, con reglas y tracking", True)]):
            yc = 0.62 - 0.95 * k
            fondo = caja(DER - x_der, 0.85, tm, relleno="#F3E3D6" if propia else tm.fondo, radio=0.15, grosor=2)
            fondo.move_to([x_der + (DER - x_der) / 2, yc, 0])
            n = a_izq(t_cuerpo(nombre, tm.tinta, 26, peso=BOLD), x_der + 0.25, yc + 0.19)
            d = a_izq(t_cuerpo(desc, tm.tinta if propia else tm.suave, 26), x_der + 0.25, yc - 0.19)
            filas.append(VGroup(fondo, n, d))
        fuentes = etiqueta_pie("Fuentes: El País, Maritime Executive, NextBillion, Stellar Community Fund", tm)

        if self.instantanea:
            self.add(k1, lista, k2, *filas, fuentes)
            return
        self.play(FadeIn(k1), FadeIn(k2), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in lista], lag_ratio=0.3), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in filas], lag_ratio=0.3), run_time=1.6)
        self.play(FadeIn(fuentes), run_time=0.5)
        self.wait(3)


# ===================================================================== S8
class S8Plan(Lamina):
    tema = OSCURO
    numero = 8
    nombre = "S8Plan"

    def cuerpo(self):
        tm = self.tema
        self.encabezado("Equipo y plan", "De Bolivia al mundo")

        # hacia dónde: tres etapas con anillos que crecen
        etapas = []
        for k, (titulo, desc) in enumerate([("Bolivia", "Exportadores y compradores"),
                                            ("Latinoamérica", "Corredores y pymes"),
                                            ("El mundo", "Pymes que pagan a ciegas")]):
            y = 1.35 - 1.05 * k
            c = caja(6.0, 0.95, tm).move_to([IZQ + 3.0, y, 0])
            anillos = VGroup(*[Circle(radius=0.12 + 0.12 * j, stroke_width=3, stroke_color=tm.acento)
                               for j in range(k + 1)]).move_to([IZQ + 0.6, y, 0])
            t = a_izq(t_titulo(titulo, tm.tinta, 28), IZQ + 1.2, y + 0.2)
            d = a_izq(t_cuerpo(desc, tm.suave, 26), IZQ + 1.2, y - 0.22)
            etapas.append(VGroup(c, anillos, t, d))

        # cuándo: la línea de tiempo del plan
        x_linea = 0.4
        eje = raya([x_linea, 1.6, 0], [x_linea, -1.9, 0], tm, grosor=3)
        hitos = []
        for k, (cuando, que) in enumerate([("Octubre · Ideatón", "Demo de punta a punta en testnet"),
                                           ("3 sprints · Instaward", "Mainnet, tratos reales y Kipu v0"),
                                           ("Después · SCF Build", "Escrow, anchors y rampa sin cripto"),
                                           ("Escala · Canales", "Despachantes y corredores")]):
            y = 1.35 - 0.9 * k
            nodo = Circle(radius=0.11, stroke_width=3, stroke_color=tm.acento,
                          fill_color=tm.acento if k == 0 else tm.fondo, fill_opacity=1).move_to([x_linea, y, 0])
            hitos.append(VGroup(nodo, a_izq(t_titulo(cuando, tm.tinta, 28), x_linea + 0.4, y + 0.2),
                                a_izq(t_cuerpo(que, tm.suave, 26), x_linea + 0.4, y - 0.22)))

        equipo = []
        for k, p in enumerate(EQUIPO):
            x = IZQ + k * 6.1
            usuario = unquote(p["linkedin"].split("/in/")[1].rstrip("/"))
            segunda = p["rol"] or f"LinkedIn: {usuario}"
            bloque = VGroup(t_cuerpo(p["nombre"], tm.tinta, 28, peso=BOLD), t_cuerpo(segunda, tm.suave, 26))                 .arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            bloque.move_to([x + bloque.width / 2, -3.2, 0])
            equipo.append(bloque)
        sello = a_izq(t_titulo("EQUIPO DE 2", tm.kicker, 26), IZQ, -2.55)

        if self.instantanea:
            self.add(*etapas, eje, *hitos, sello, *equipo)
            return

        with self.linea("s8_a"):
            self.play(FadeIn(etapas[0], shift=UP * 0.2), run_time=0.8)
        with self.linea("s8_b"):
            self.play(FadeIn(etapas[1], shift=UP * 0.2), run_time=0.8)
            self.pausar(1.2)
            self.play(FadeIn(etapas[2], shift=UP * 0.2), run_time=0.8)
        with self.linea("s8_c"):
            self.play(Create(eje), run_time=0.5)
            self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in hitos], lag_ratio=0.35), run_time=1.8)
            self.play(FadeIn(sello), *[FadeIn(e) for e in equipo], run_time=0.8)
        with self.linea("s8_d"):
            self.salir(0.5)
            nombre = t_titulo("Qhatu", tm.tinta, 130).move_to([0, 1.2, 0])
            lema = t_titulo("Tu proveedor cobra cuando cumple.", tm.acento, 50).move_to([0, -0.15, 0])
            repo = t_cuerpo(DATOS["repo"], tm.tinta, 32, peso=BOLD).move_to([0, -1.3, 0])
            firma = t_cuerpo(" · ".join(p["nombre"] for p in EQUIPO), tm.suave, 26).move_to([0, -2.3, 0])
            self.play(FadeIn(nombre, scale=0.9), FadeIn(lema, shift=UP * 0.15), FadeIn(repo), FadeIn(firma),
                      run_time=1.2)
