# Descripción para Stellar APEX

Texto para pegar en el campo **Description** del proyecto en stellarapex.org, con los títulos de la plantilla de la guía del participante. Track: **Pagos y remesas**. Project stage: **Idea**.

Antes de pegar, reemplaza los tres textos entre llaves `{...}`: son datos que solo ustedes tienen (links públicos y, si las hicieron, las entrevistas).

## Campos sueltos de APEX

- **Project name:** Qhatu
- **Project tagline:** Tu proveedor cobra cuando cumple. Pago por hitos en dólares digitales para pymes que comercian con el exterior.
- **Project stage:** Idea

## Texto de la descripción

```
Resumen:
Qhatu es un pago condicionado por hitos para pymes que compran y venden al exterior. El exportador arma el trato y le manda un link al comprador; el comprador deposita el 100% en USDC en un escrow no custodial sobre Stellar, y el pago se libera por hitos a medida que se verifican los documentos. Primer corredor: exportador boliviano y comprador en Estados Unidos o México.

Problema:
En una venta al exterior alguien paga a ciegas: el comprador no quiere pagar antes de recibir y el proveedor no quiere despachar sin saber si le van a pagar. En Bolivia las operaciones con activos virtuales pasaron de 46,5 a 294 millones de dólares entre el primer semestre de 2024 y el de 2025 (BCB), y muchas se pagan por adelantado y sin protección. En el mundo la brecha de financiamiento al comercio es de 2,5 billones de dólares y a las pymes les rechazan el 41% de las solicitudes (Banco Asiático de Desarrollo, enero de 2026). El pago en dólares digitales ya existe; la confianza entre las partes, no.

Solución:
1) Trato con link: el exportador define monto, hitos y documentos. 2) El comprador deposita el 100% en el escrow antes de producir. 3) Reglas revisan que los documentos cuadren y que el contenedor exista (dígito verificador ISO 6346 y seguimiento de la naviera). 4) Se libera 30% al confirmar el pedido y 70% contra la guía de embarque verificada. Si hay un reclamo, decide un tercero independiente. Qhatu nunca controla la plata. Se construiría sobre Trustless Work (escrow) y Pollar (ingreso sin cripto).

Por qué Stellar:
El escrow es no custodial y programable, la liquidación tarda segundos y el USDC es nativo de la red, con costos por transacción de fracciones de centavo. Sin eso volveríamos a depender de un banco que custodie los fondos y a esperar días. Los anchors permitirán más adelante entrar y salir de moneda local con socios con licencia.

Modelo de negocio:
Comisión de 1% a 1,5% por trato, con un mínimo de 75 dólares. Es del mismo orden que una carta de crédito (0,75% a 3% según guías públicas de bancos); la ventaja que buscamos es el acceso y la rapidez, no el precio. El escrow de Trustless Work cobra 0,3% por operación. Las cifras de ingresos son hipótesis que se validan en un piloto de 30 días con 3 tratos reales.

Entrevistas ({N}):
{Si hicieron entrevistas: con quién hablaron y qué aprendieron, una línea por persona. Si no hicieron ninguna: "Todavía no hicimos entrevistas formales. La evidencia de hoy sale de fuentes públicas (BCB, Banco Asiático de Desarrollo, prensa) y el plan de validación son 15 entrevistas a exportadores y 5 a despachantes, con criterios de abandono definidos en el repositorio."}

Equipo y plan:
Nicolás Emir Mejía Agreda: desarrollo en Rust y Soroban. María Aguilera: marketing, comunicación y diseño. Próximos pasos: demo de punta a punta en testnet sobre Trustless Work; piloto de 30 días con 3 tratos reales; luego mainnet. Estado, límites y riesgos dichos de frente (sin producto, sin transacciones, riesgo regulatorio en Bolivia): github.com/nema1502/qhatu/blob/main/docs/estado-y-limites.md

Deck: {link público al deck, "cualquiera con el enlace puede ver"}
Video: {link público al video de 3 minutos}
Evidencia: https://github.com/nema1502/qhatu
Testnet: (sin transacción todavía)
```

## Lista para antes de las 12:00

La inscripción al evento en APEX cerró el sábado a las 12:00; el envío cierra hoy domingo a las 12:00.

1. Sube `deck/qhatu-deck.pdf` a Drive y `video/qhatu-pitch-3min.mp4` a YouTube, Loom o Drive. Pon ambos en **cualquiera con el enlace puede ver** y ábrelos en una ventana de incógnito para comprobarlo.
2. Pega esos dos links en `Deck:` y `Video:`.
3. Resuelve `Entrevistas`: no pongas un número que no sea real. Un 0 dicho con honestidad puntúa mejor que una cifra inventada, y el jurado puede preguntar.
4. En APEX: My projects, abre el proyecto, pega el texto, guarda y confirma que Nicolás y María están en Members (cada persona participa en un solo proyecto).
5. En la página de la ideatón: Choose your project, marca el proyecto en Your projects y elige el track **Pagos y remesas**.
6. Si el repositorio es privado, hazlo público o el jurado no podrá abrir el link de Evidencia.
7. Dudas: Diego, WhatsApp o Telegram 77701350.

## Cumplimiento de la guía (revisado)

| Entregable | Pide la guía | Estado en el repo |
|---|---|---|
| Deck | 8 slides, PDF o Slides | `deck/qhatu-deck.pdf`: 8 páginas. `deck/qhatu-deck.pptx`: 8 láminas con notas del orador |
| Video pitch | 3 minutos | `video/qhatu-pitch-3min.mp4`: 2:47, con voz y sin voz |
| Problema, solución, Stellar, negocio | Obligatorio | Texto listo arriba |
| Entrevistas | Meta de 5 | Pendiente: hoy hay 0 formales (ver `datos/proyecto.json`) |
| Evidencia de entrevistas | Link a carpeta | Pendiente: depende de las entrevistas |
| Equipo y plan | Recomendado | Texto listo arriba y en [plan](plan.md) |
| Testnet | Opcional, +10 | Sin transacción todavía; el entorno donde se preparó esto no alcanzaba la testnet |

Para regenerar el deck y el video hace falta el motor privado `nemaxyz-motor`, que no está en este repo (ver [animaciones](animaciones.md)). Nada del proyecto usa LaTeX.
