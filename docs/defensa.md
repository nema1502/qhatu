# Guía para la defensa

Para quien expone en vivo: el pitch dura 3 minutos y después vienen unas 2 de preguntas. Con el video sin voz de fondo, el orden y el tiempo de cada frase están en [`video/guion.md`](../video/guion.md).

## Si no te acordás de nada más

1. Alguien siempre paga a ciegas. El pago en dólares digitales ya existe; la confianza, no.
2. Qhatu es un pago condicionado por hitos: el comprador deposita el 100% en un escrow, y se libera 30% al confirmar el pedido y 70% contra la guía de embarque verificada.
3. Qhatu nunca controla la plata.
4. Hoy es una idea con una maqueta. Lo que sigue es correrlo en testnet y hacer 3 tratos reales.

## Preguntas probables

**¿No es lo mismo que Trustless Work?**
No. Trustless Work es la caja fuerte: un escrow genérico y no custodial. Qhatu es el producto de comercio exterior que va encima: arma el trato, revisa los documentos y el contenedor, y define los hitos. Es como la relación entre Stripe y una tienda en línea.

**¿Y CashAbroad, Eascrow o Tazapay?**
Existen, y eso muestra que el mercado es real. Nuestra diferencia, que todavía hay que demostrar, es el autoservicio por link, las reglas sobre los documentos y el seguimiento del contenedor, empezando desde Bolivia.

**¿Funcionaría igual sin Stellar?**
No con las mismas condiciones. El escrow es no custodial y programable, la liquidación tarda segundos y el dólar digital (USDC) es nativo de la red. Sin eso volvemos a depender de un banco que custodie y a esperar días.

**¿Es más barato que una carta de crédito?**
No lo vamos a afirmar. Las guías públicas ponen la carta de crédito entre 0,75% y 3%; nosotros cobraríamos 1% a 1,5%. Es del mismo orden. La mejora que buscamos es el acceso (sin línea de crédito) y la rapidez. Lo medimos con cotizaciones reales en el piloto.

**¿Por qué un comprador dejaría el 100% depositado antes de producir?**
Es la mayor duda del diseño, y la decimos de frente. La plata queda inmovilizada, y una carta de crédito no pide eso. Por eso el pago se libera en dos hitos y no al final. Si los compradores no aceptan, lo vamos a ver en el piloto.

**¿Es legal en Bolivia?**
Falta una opinión legal formal. El DS 5384 y la Resolución ASFI 540/2025 regulan a los proveedores de servicios de activos virtuales. Por eso diseñamos Qhatu sin tocar los fondos: escrow no custodial, sin llaves y con un tercero independiente que resuelve las disputas. Por eso hablamos de pago condicionado por hitos. Y no prestamos ni financiamos.

**¿Cómo entra y sale el dinero en bolivianos?**
Hoy no encontramos una rampa con licencia verificada que entregue en Stellar en Bolivia. Empezamos con quienes ya operan con dólares digitales. La conversión a bolivianos es un paso posterior, con socios con licencia.

**¿Hicieron entrevistas?**
No formalmente. La evidencia es pública: prensa, datos del BCB e informes del Banco Asiático de Desarrollo. Lo que sigue es validar con entrevistas y con 3 tratos reales. Si hicieron entrevistas antes de exponer, se agregan en `datos/proyecto.json`.

**¿Qué hay hecho de verdad?**
El diseño, el deck, el video y una maqueta animada de la pantalla. No hay producto ni transacciones reales todavía. Lo próximo es la demo en testnet sobre Trustless Work.

**¿Y si hay una disputa?**
Decide un tercero independiente. Qhatu no tiene ese rol, justamente para no controlar los fondos.

**¿Cómo ganan plata?**
1% a 1,5% por trato, con mínimo de 75 dólares. Después Kipu (facturas y contabilidad automáticas, por suscripción) y una parte para los despachantes que traen clientes. Las cifras son hipótesis.

**¿Por qué el contenedor?**
Porque se puede verificar con reglas, sin inteligencia artificial: el número de contenedor lleva un dígito verificador (norma ISO 6346) que se calcula. Es un chequeo simple que ya detecta errores y fraudes de papel.
