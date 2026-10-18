# Estado y límites

Qhatu está en etapa de idea y maqueta. Esta página dice qué existe de verdad, qué no, y dónde están los riesgos.

## Qué hay hoy

- El diseño del flujo, con sus reglas de pago por hitos.
- Una maqueta animada de la pantalla del trato (ver `video/` y `deck/`).
- El deck de 8 láminas y el video de 3 minutos.
- El plan de validación y los criterios para abandonar (ver [plan](plan.md)).

## Qué no hay todavía

- **No hay producto.** No hay contratos propios ni una aplicación funcionando.
- **No hay transacciones reales en testnet.** La maqueta lo dice en pantalla. El primer paso es correr el flujo de punta a punta sobre el escrow de Trustless Work en la testnet de Stellar.
- **No hicimos entrevistas formales.** La evidencia de hoy sale de fuentes públicas (prensa, datos del BCB, informes del Banco Asiático de Desarrollo). Está dicho en la lámina de validación.
- **No hay acuerdo con Pollar ni con Trustless Work.** Los usamos como piezas abiertas; no somos sus socios.
- **Las cifras de ingresos son hipótesis**, no mediciones.

## El costo frente a una carta de crédito

Las guías públicas de bancos ponen el costo de una carta de crédito entre 0,75% y 3% del valor, con diferencias entre bancos y países. Qhatu cobraría entre 1% y 1,5%. Es un costo del mismo orden: **la ventaja que buscamos no es el precio, sino el acceso y la rapidez** (sin línea de crédito ni trámite bancario, y liquidación en segundos). Hay que confirmarlo con cotizaciones reales durante el piloto.

## La debilidad del diseño

El comprador deposita el 100% antes de que se produzca la mercadería, y esa plata queda inmovilizada. Una carta de crédito no le pide eso. Por eso el pago se libera en dos hitos (30% al confirmar el pedido, 70% contra la guía de embarque verificada) y por eso la aceptación por parte de los compradores es la principal pregunta abierta.

## Riesgo regulatorio

- En Bolivia, el DS 5384 y la Resolución ASFI 540/2025 regulan a los proveedores de servicios de activos virtuales. Revisamos que una plataforma que custodie, administre o controle los fondos podría caer en ese régimen.
- Por eso Qhatu **no toca los fondos**: el escrow es no custodial, Qhatu no tiene llaves ni decide la liberación, y las disputas las resuelve un tercero independiente.
- Por la misma razón el producto se llama **pago condicionado por hitos**. No lo llamamos aval ni seguro, porque esos términos tienen otro significado legal.
- Qhatu tampoco presta ni financia: prestar sin licencia es un delito en Bolivia (Ley 393).
- Falta una opinión legal formal. Es un criterio de abandono (ver [plan](plan.md)).

## Entrada y salida de dinero local

Hoy no encontramos en Bolivia una rampa con licencia verificada que entregue en Stellar. Por eso el primer corredor parte de personas que ya operan con dólares digitales (USDT o USDC) y de compradores en países donde sí hay rampas. Convertir a bolivianos es un problema que dejamos para después y que depende de socios con licencia.

## Competencia

Existen CashAbroad y Eascrow (cartas de crédito y escrow sobre Stellar), Tazapay (escrow B2B con validación de documentos) y Trade Assurance (dentro de Alibaba). Que ya existan prueba que el mercado es real; nuestra diferencia, que hay que demostrar, es el autoservicio por link, las reglas sobre los documentos y el tracking del contenedor, empezando desde Bolivia.
