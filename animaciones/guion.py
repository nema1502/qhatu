"""Guion del pitch de tres minutos. Una línea por beat visual.

Es el único lugar donde vive el texto hablado. De acá salen la voz, el tiempo de
cada escena y el guion.md que se puede leer para grabar con voz propia.

Cada línea es (id, texto, voz). `texto` es lo que lee una persona. `voz` es lo
mismo con las cifras en letras, para que la voz sintética no se tropiece; si no
hace falta, se deja en None.
"""

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = json.loads((RAIZ / "datos" / "proyecto.json").read_text(encoding="utf-8"))

# Si ya hay transacciones reales en testnet (datos/proyecto.json), el relato cambia
# de «maqueta» a «lo que pasó». Lo que no existe no se cuenta como hecho.
REAL = DATOS["testnet"]["estado"] == "real"

# Cómo suena cada palabra rara en una voz española. Solo afecta a la voz sintética.
PRONUNCIACION = {
    "Qhatu": "Katu",
    "Trustless Work": "Trastles Uork",
    "escrow": "escrou",
    "Stellar": "Stelar",
    "mainnet": "meinnet",
}

ORDEN = ["S1", "S2", "S3", "S4", "S5", "S6", "S8"]

TITULOS = {
    "S1": "Apertura", "S2": "El problema", "S3": "La solución", "S4": "El flujo",
    "S5": "Por qué Stellar", "S6": "Modelo de negocio", "S8": "Plan y cierre",
}

# Quién lee cada escena. Es una propuesta: se cambia acá y el guion.md se regenera.
# Un nombre por escena; `QUIEN_LINEA` pisa una línea suelta.
QUIEN = {"S1": "María", "S2": "María", "S3": "Nicolás", "S4": "Nicolás",
         "S5": "Nicolás", "S6": "María", "S8": "María"}
QUIEN_LINEA = {"s8_c": "Nicolás", "s8_d": "Nicolás"}

ESCENAS = {
    "S1": [
        ("s1_a", "Pensemos en una exportadora boliviana que cierra una venta con un comprador del exterior.", None),
        ("s1_b", "El comprador no quiere pagar antes de recibir, y la exportadora no quiere despachar sin saber si le van a pagar.", None),
        ("s1_c", "Hoy, uno de los dos se arriesga a ciegas.", None),
        ("s1_d", "Por eso existe Qhatu: tu proveedor cobra cuando cumple.", None),
    ],
    "S2": [
        ("s2_a", "En Bolivia, las operaciones con activos virtuales pasaron de 46 a 294 millones de dólares en un año.",
         "En Bolivia, las operaciones con activos virtuales pasaron de cuarenta y seis a doscientos noventa y cuatro millones de dólares en un año."),
        ("s2_b", "Muchos pagan por adelantado y sin protección.", None),
        ("s2_c", "En el mundo faltan 2,5 billones de dólares de financiamiento al comercio, y a las pymes les rechazan cuatro de cada diez solicitudes.",
         "En el mundo faltan dos coma cinco billones de dólares de financiamiento al comercio, y a las pymes les rechazan cuatro de cada diez solicitudes."),
        ("s2_d", "El pago ya existe. La confianza, no.", None),
    ],
    "S3": [
        ("s3_a", "Qhatu es un pago condicionado por hitos: el exportador arma el trato y le manda un link al comprador.", None),
        ("s3_b", "El comprador deposita el 100% en un escrow en Stellar, antes de producir.",
         "El comprador deposita el cien por ciento en un escrow en Stellar, antes de producir."),
        ("s3_c", "Reglas automáticas revisan los documentos y el contenedor.", None),
        ("s3_d", "Se libera el 30% al confirmar el pedido y el 70% contra la guía de embarque verificada.",
         "Se libera el treinta por ciento al confirmar el pedido y el setenta por ciento contra la guía de embarque verificada."),
        ("s3_e", "Y Qhatu nunca controla la plata.", None),
    ],
    "S4": [
        ("s4_a", "Así funciona, paso por paso, en la red de pruebas de Stellar." if REAL
         else "Así funciona, paso por paso: una maqueta.", None),
        ("s4_b", "El comprador deposita mil dólares digitales en el escrow.", None),
        ("s4_c", "Se confirma el pedido y se libera el 30%.",
         "Se confirma el pedido y se libera el treinta por ciento."),
        ("s4_d", "Se suben los documentos y una regla detecta un contenedor inválido: el pago queda retenido.", None),
        ("s4_e", "Se corrige, el comprador aprueba y se libera el 70%.",
         "Se corrige, el comprador aprueba y se libera el setenta por ciento."),
    ],
    "S5": [
        ("s5_b", "Pollar abre la puerta: una cuenta de Google o de correo, sin cripto.", None),
        ("s5_c", "Trustless Work guarda la plata en un escrow no custodial, ya activo en mainnet.", None),
        ("s5_d", "Y Qhatu arma el trato, revisa los documentos y señala cuándo se cumple cada hito.", None),
        ("s5_e", "Frente a una carta de crédito: sin línea de crédito, sin trámite bancario, y con pago en segundos.", None),
    ],
    "S6": [
        ("s6_a", "Cobramos entre 1 y 1,5% de cada trato, con un mínimo de 75 dólares.",
         "Cobramos entre uno y uno coma cinco por ciento de cada trato, con un mínimo de setenta y cinco dólares."),
        ("s6_b", "Es del mismo orden que una carta de crédito; cambian el acceso y la rapidez.", None),
        ("s6_c", "Después sumamos Kipu: facturas y contabilidad automáticas, como suscripción.", None),
        ("s6_d", "Despachantes y agentes de carga son un canal: ganan una parte por cada cliente.", None),
        ("s6_e", "Son hipótesis. Las vamos a validar en un piloto de 30 días.",
         "Son hipótesis. Las vamos a validar en un piloto de treinta días."),
    ],
    "S8": [
        ("s8_a", "Empezamos con exportadores bolivianos y sus compradores.", None),
        ("s8_b", "Seguimos con Latinoamérica, y de ahí a cualquier pyme del mundo que hoy paga a ciegas.", None),
        ("s8_c", "Somos dos. Primero, la demo en testnet; después, tratos reales en mainnet.", None),
        ("s8_d", "Qhatu: tu proveedor cobra cuando cumple.", None),
    ],
}


def quien(escena, ident):
    return QUIEN_LINEA.get(ident, QUIEN[escena])


def lineas():
    """Todas las líneas en el orden en que se dicen: [(escena, id, texto, voz)]."""
    return [(esc, i, t, v) for esc in ORDEN for (i, t, v) in ESCENAS[esc]]


def para_voz(texto, voz=None):
    """El texto tal como lo va a leer la voz sintética."""
    salida = voz or texto
    for palabra, suena in PRONUNCIACION.items():
        salida = salida.replace(palabra, suena)
    return salida
