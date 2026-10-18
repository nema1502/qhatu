# El auditor

Antes de que algo llegue a GitHub, un script revisa tres cosas: los archivos, los mensajes de commit y los textos de los pull requests. Busca las huellas que dejan las herramientas de IA y los descuidos que suelen venir con ellas.

No decide si un texto «suena a IA», porque eso no se puede saber. Busca marcas concretas.

## Qué bloquea

- Firmas de IA en commits y PR: líneas de coautoría con una IA, «generado con…», el emoji de robot, enlaces a herramientas.
- Autor o committer con identidad de IA.
- Archivos de herramientas de IA: carpetas de configuración y archivos de instrucciones.
- Restos de conversación pegados en un archivo: frases de asistente, cierres de chat, vallas de Markdown dentro de un archivo de código y marcas que indican que el código quedó cortado.
- Placeholders entre corchetes que nadie completó.
- Secretos: claves secretas de Stellar, claves privadas, tokens de GitHub y de APIs.
- Basura: `node_modules`, cachés de render, archivos `.env`, archivos de más de 50 MB.

## Qué solo avisa

- Texto inflado o de relleno, del estilo de los folletos de marketing.
- Títulos y viñetas con emojis.
- Palabras que prometen más de lo que Qhatu es en lo legal: las que sugieren aval, seguro, guarda de fondos o préstamos (el motivo está en [estado y límites](estado-y-limites.md)).
- Marcas de pendiente.

Con `--strict` los avisos también bloquean.

## Dónde corre

1. `pre-commit`: los archivos que entran al commit.
2. `commit-msg`: el mensaje y la identidad del autor.
3. `pre-push`: todos los commits que se van a subir y el árbol completo, por si alguno se hizo salteando los hooks.
4. GitHub Actions: lo mismo en cada push y en cada pull request, incluidos su título y su descripción. El workflow está en `scripts/ci/auditoria.yml`. Para activarlo se copia a `.github/workflows/`; GitHub exige el permiso `workflow` para subir ese tipo de archivos (`gh auth refresh -s workflow`).

Los hooks viven en la máquina de quien trabaja y se pueden saltear. El CI no. Por eso están los dos.

## Instalarlo

```bash
git config core.hooksPath .githooks
```

Hace falta Node 18 o más nuevo y git. Sin dependencias.

## Probarlo y ajustarlo

```bash
node scripts/audit.mjs --autotest        # casos conocidos: tienen que dar todos bien
node scripts/audit.mjs --all             # el repo entero y todo el historial
node scripts/audit.mjs --texto "..."     # un texto suelto, por ejemplo el cuerpo de un PR
```

Los patrones están en `scripts/audit.reglas.mjs`. Cada regla tiene un nivel (error o aviso), un mensaje y una ayuda. Agregar una regla y un caso en `PRUEBAS` es todo.

## Límites

- Un texto de IA bien editado no deja marcas, y el auditor no lo detecta. Lo que sí hace es evitar los descuidos más comunes.
- Una línea con `audit-ok` se saltea. El resumen cuenta cuántas se saltearon, para que no sea un punto ciego en silencio.
- Los únicos archivos que no se escanean son los dos del propio auditor, porque contienen los patrones, y el `package-lock.json`.
