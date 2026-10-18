// Reglas del auditor. Acá se editan los patrones; el motor está en audit.mjs.
//
// Estos dos archivos son lo único que el auditor no escanea, porque contienen
// los patrones que busca. Todo lo demás pasa por las reglas.
//
//   nivel 'error' -> bloquea el commit o el push y hace fallar el CI
//   nivel 'warn'  -> se muestra; con --strict también bloquea
//
// Una línea que lleva «audit-ok» se saltea. Queda contada en el resumen para
// que no sea un punto ciego silencioso.

const e = 'error';
const w = 'warn';

// ---------------------------------------------------------------------------
// Atribución a IA. Vale para mensajes de commit, textos de PR y archivos.
// ---------------------------------------------------------------------------
export const ATRIBUCION = [
  {
    id: 'IA-COAUTOR', nivel: e,
    re: /^[ \t>*-]*co-?authored-?by:.*(claude|anthropic|copilot|chatgpt|openai|gemini|cursor|codeium|devin|windsurf|aider|\bai\b|\bia\b|\bbot\b)/im,
    msg: 'Línea de coautoría con una IA',
    ayuda: 'Borrala. Los commits de este repo van a nombre de personas.',
  },
  {
    id: 'IA-GENERADO', nivel: e,
    re: /\b(generated|created|written|made|authored|assisted|co-?written)\s+(with|by|using|via)\s+[[*_`]*(claude|chatgpt|gpt-?\d*|copilot|gemini|cursor|an?\s+ai|ai|llms?)\b/i,
    msg: 'Firma de «generado con» una IA',
    ayuda: 'Sacala.',
  },
  {
    id: 'IA-GENERADO-ES', nivel: e,
    re: /\b(generad[oa]s?|cread[oa]s?|escrit[oa]s?|hech[oa]s?|redactad[oa]s?|asistid[oa]s?|armad[oa]s?|programad[oa]s?)\s+(con|por|usando|mediante|gracias a)\s+[[*_`]*(claude|chatgpt|gpt-?\d*|copilot|gemini|cursor|ia|inteligencia artificial|un modelo de lenguaje)\b/iu,
    msg: 'Firma de «generado con» una IA',
    ayuda: 'Sacala.',
  },
  {
    id: 'IA-ROBOT', nivel: e,
    re: /🤖/u,
    msg: 'Emoji de robot (firma típica de herramientas de IA)',
    ayuda: 'Sacalo.',
  },
  {
    id: 'IA-HERRAMIENTA', nivel: e,
    re: /\bclaude[ -]?code\b|claude\.(?:com|ai)\/|anthropic\.com|noreply@anthropic\.com/i,
    msg: 'Referencia a una herramienta de IA',
    ayuda: 'Sacala: este repo no lleva firmas de herramientas.',
  },
];

// En un mensaje de commit o de PR, nombrar una herramienta de IA ya es sospechoso.
export const MENSAJE_EXTRA = [
  {
    id: 'IA-MENCION-MSG', nivel: e,
    re: /\b(claude|chatgpt|copilot|gemini|anthropic|openai)\b/i,
    msg: 'El mensaje nombra una herramienta de IA',
    ayuda: 'Un commit cuenta qué cambió en el proyecto, no con qué se escribió.',
  },
];

// En archivos es solo un aviso: puede ser parte legítima del producto.
export const MENCION_IA_CONTENIDO = [
  {
    id: 'IA-MENCION', nivel: w,
    excepto: /(^|\/)\.gitignore$/, // ahí se nombran justamente para excluirlas
    re: /\b(claude|chatgpt|copilot|gemini|anthropic|openai)\b/i,
    msg: 'Nombra una herramienta de IA: ¿es parte del producto?',
    ayuda: 'Si es un resto de la herramienta con que se escribió, sacalo.',
  },
];

// ---------------------------------------------------------------------------
// Restos de conversación: frases que solo existen en un chat.
// ---------------------------------------------------------------------------
export const RESTOS_CHAT = [
  {
    id: 'CHAT-IA', nivel: e,
    re: /\bas an? (?:ai|artificial intelligence|language model|llm)\b|\bcomo (?:un )?(?:modelo de lenguaje|asistente de ia|asistente virtual)\b|\bi(?:'m| am) sorry\b|\bi cannot (?:assist|help|comply)\b|\blo siento,? pero no (?:puedo|tengo)\b/iu,
    msg: 'Frase de un asistente de chat',
    ayuda: 'Es un resto de conversación pegado en el archivo.',
  },
  {
    id: 'CHAT-CIERRE', nivel: e,
    re: /\bhope (?:this|that|it) helps\b|\bespero que (?:esto )?(?:te )?(?:ayude|sirva)\b|\blet me know if\b|\bav[ií]same si\b|\bd[ií]me si (?:quer[eé]s|quieres|necesit[aá]s|necesitas)\b|\bwould you like me to\b|¿quer[eé]s que (?:te|lo|la|le) |¿quieres que (?:te|lo|la|le) /iu,
    msg: 'Cierre típico de una respuesta de chat',
    ayuda: 'Sacalo.',
  },
  {
    id: 'CHAT-APERTURA', nivel: w,
    re: /^[ \t]*(?:certainly|sure|absolutely|of course)[!,.]|^[ \t]*(?:here'?s|here is|here are)\b.{0,50}\b(?:code|version|updated|implementation|file|example|summary)\b|^[ \t]*(?:aqu[ií] (?:tienes|est[aá]n?|va|te dejo)|claro que s[ií]|¡?claro!|por supuesto[!,.])/imu,
    msg: 'Apertura típica de una respuesta de chat',
    ayuda: 'Si es parte del texto, reescribila; si es un resto, sacala.',
  },
  {
    id: 'CHAT-INFORME', nivel: w,
    re: /\bi(?:'ve| have) (?:updated|added|implemented|created|fixed|refactored)\b|\bhe (?:actualizado|agregado|a[ñn]adido|implementado|creado|corregido|refactorizado)\b/iu,
    msg: 'Informe en primera persona, típico de una respuesta de chat',
    ayuda: 'Un archivo describe el proyecto, no cuenta lo que hizo quien lo escribió.',
  },
];

// ---------------------------------------------------------------------------
// Código cortado o relleno.
// ---------------------------------------------------------------------------
export const TRUNCADO = [
  {
    id: 'TRUNCADO', nivel: e,
    re: /^[ \t]*(?:\/\/|#|\/\*|<!--|--)[ \t]*\.\.\.[ \t]*(?:existing|rest|remaining|same|unchanged|previous|other|resto|c[oó]digo|igual|anterior)|\b(?:rest|remainder) of (?:the |your )?(?:code|file|implementation|function)\b|\bresto del (?:c[oó]digo|archivo|contenido)\b|\b(?:your|tu) (?:code|c[oó]digo) (?:goes )?(?:here|aqu[ií])\b|\.\.\.[ \t]*\((?:rest|resto|omitted|omitido|truncated|truncado)/imu,
    msg: 'Marca de código cortado («resto del código…»)',
    ayuda: 'Completalo o sacalo: el archivo quedó a medias.',
  },
];

// Vallas de Markdown dentro de archivos que no son Markdown: se pegó el chat entero.
export const FENCE = [
  {
    id: 'VALLA-MD', nivel: e,
    re: /^[ \t]*```/m,
    msg: 'Valla de Markdown dentro de un archivo que no es Markdown',
    ayuda: 'Se copió la respuesta de un chat con sus vallas. Dejá solo el contenido.',
  },
];

// ---------------------------------------------------------------------------
// Placeholders sin completar.
// ---------------------------------------------------------------------------
export const PLACEHOLDERS = [
  {
    id: 'PLACEHOLDER', nivel: e,
    re: /\blorem ipsum\b|<(?:tu|your)[-_ ][a-z_ -]+>|\b(?:tu|your)-(?:usuario|username|user|repo)\b/iu,
    msg: 'Placeholder sin completar',
    ayuda: 'Completalo o sacalo antes de subir.',
  },
  {
    id: 'PENDIENTE', nivel: w,
    re: /\b(?:TODO|FIXME|XXX|HACK)\b/,
    msg: 'Marca de pendiente',
    ayuda: 'Resolvela o pasala a un issue.',
  },
];

// Corchetes sin completar. Solo en prosa: en código «[nombre]» o «[n]» es un índice.
export const PLACEHOLDERS_PROSA = [
  {
    id: 'PLACEHOLDER', nivel: e,
    re: /\[(?:nombre(?:\s*\d)?|rol|role|n|hash(?:\s*\d(?:\s*[–-]\s*\d)?)?|hallazgo[^\]]{0,40}|completar[^\]]{0,40}|confirmar[^\]]{0,60}|insertar[^\]]{0,30}|insert[^\]]{0,30}|tu [^\]]{1,30}|your [^\]]{1,30})\]/iu,
    msg: 'Placeholder sin completar',
    ayuda: 'Completalo o sacalo antes de subir.',
  },
];

// ---------------------------------------------------------------------------
// Secretos.
// ---------------------------------------------------------------------------
export const SECRETOS = [
  {
    id: 'SECRETO-STELLAR', nivel: e,
    re: /(?<![A-Z2-7])S[A-Z2-7]{55}(?![A-Z2-7])/,
    msg: 'Parece una clave secreta de Stellar (empieza con S, 56 caracteres)',
    ayuda: 'Si es real, ya está comprometida: generá otra. Nunca se sube.',
  },
  {
    id: 'SECRETO-CLAVE-PRIVADA', nivel: e,
    re: /-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----/,
    msg: 'Clave privada',
    ayuda: 'Sacala del repo y rotala.',
  },
  {
    id: 'SECRETO-GITHUB', nivel: e,
    re: /\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b/,
    msg: 'Token de GitHub',
    ayuda: 'Revocalo en GitHub y sacalo del repo.',
  },
  {
    id: 'SECRETO-API', nivel: e,
    re: /\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}\b|\bAIza[0-9A-Za-z_-]{35}\b|\bxox[baprs]-[A-Za-z0-9-]{10,}/,
    msg: 'Clave de API',
    ayuda: 'Revocala en el servicio y sacala del repo.',
  },
  {
    id: 'SECRETO-ASIGNADO', nivel: w,
    re: /\b(?:api[_-]?key|secret|token|password|passwd|clave|contrase[ñn]a)\b['"]?\s*[:=]\s*['"][^'"\s]{16,}['"]/iu,
    msg: 'Parece un secreto escrito en el código',
    ayuda: 'Va en una variable de entorno, no en el archivo.',
  },
];

// ---------------------------------------------------------------------------
// Estilo: texto inflado, de relleno o con aire de generado. Solo prosa. Solo aviso.
// ---------------------------------------------------------------------------
export const ESTILO = [
  {
    id: 'ESTILO-ES', nivel: w,
    re: /(?<![\p{L}])(?:revolucion\p{L}*|disruptiv\p{L}*|sin precedentes|de vanguardia|de [uú]ltima generaci[oó]n|de clase mundial|l[ií]der del mercado|[uú]nic[oa] en su (?:tipo|clase)|100 ?% seguro|sin riesgos?|infalible\p{L}*|incre[ií]ble\p{L}*|sin fisuras|hol[ií]stic\p{L}*|sinergia\p{L}*|desbloque\p{L}*|en la era (?:digital|de la ia)|en el mundo (?:actual|de hoy|acelerado)|juega un papel (?:crucial|clave|fundamental)|cabe (?:destacar|se[ñn]alar|mencionar)|es importante (?:destacar|se[ñn]alar|recordar)|en conclusi[oó]n|sum[eé]rgete|tapiz|ecosistema din[aá]mico|soluci[oó]n integral)(?![\p{L}])/iu,
    msg: 'Frase de marketing inflado o de relleno',
    ayuda: 'Acá contamos lo que hay, sin adjetivos. Si no se puede medir, sobra.',
  },
  {
    id: 'ESTILO-EN', nivel: w,
    re: /(?<![\p{L}])(?:cutting[- ]edge|game[- ]chang\p{L}*|world[- ]class|best[- ]in[- ]class|seamless\p{L}*|leverag\p{L}*|unlock\p{L}* the|delve\p{L}*|tapestry|in today'?s (?:fast[- ]paced|digital)|it'?s worth noting|in conclusion|next[- ]gen\p{L}*|empower\p{L}*|revolutioniz\p{L}*)(?![\p{L}])/iu,
    msg: 'Frase de marketing inflado o de relleno',
    ayuda: 'Acá contamos lo que hay, sin adjetivos.',
  },
];

// Reglas propias de Qhatu: el lenguaje cuida lo legal.
export const LENGUAJE_PROYECTO = [
  {
    id: 'LEG-GARANTIA', nivel: w,
    re: /(?<![\p{L}])(?:garant[ií]as?|garantiz\p{L}*)(?![\p{L}])/iu,
    msg: '«Garantía» o «garantiza» suenan a seguro o aval',
    ayuda: 'Decí «pago condicionado por hitos» (ver docs/estado-y-limites.md).',
  },
  {
    id: 'LEG-CUSTODIA', nivel: w,
    re: /(?<!\bno\s)(?<!\bsin\s)(?<![\p{L}])custodi(?:a|amos)(?![\p{L}])/iu,
    msg: 'Decir que Qhatu «custodia» choca con el diseño: Qhatu no toca los fondos',
    ayuda: 'Los fondos los guarda el escrow, no Qhatu.',
  },
  {
    id: 'LEG-PRESTAMO', nivel: w,
    re: /\b(?:otorgamos|damos|ofrecemos|hacemos|financiamos)\b.{0,25}(?:pr[eé]stamos?|cr[eé]ditos?|financiamiento)/iu,
    msg: 'Qhatu no presta ni financia',
    ayuda: 'Ver docs/estado-y-limites.md.',
  },
];

// Markdown decorado con emojis.
export const EMOJI = [
  {
    id: 'EMOJI-TITULO', nivel: w,
    re: /^#{1,6}[ \t]*\p{Extended_Pictographic}/mu,
    msg: 'Título con emoji (decoración típica de texto generado)',
    ayuda: 'Un título limpio se lee mejor.',
  },
  {
    id: 'EMOJI-LISTA', nivel: w,
    re: /^[ \t]*(?:[-*+]|\d+\.)[ \t]+\p{Extended_Pictographic}/mu,
    msg: 'Lista con emojis de viñeta (decoración típica de texto generado)',
    ayuda: 'Una viñeta común alcanza.',
  },
];

// ---------------------------------------------------------------------------
// Nombres de archivo y tamaño.
// ---------------------------------------------------------------------------
export const ARCHIVOS = [
  {
    id: 'IA-ARCHIVO', nivel: e,
    re: /(^|\/)(?:\.claude|\.cursor|\.windsurf|\.aider[^/]*|\.continue|\.codeium|\.copilot)(\/|$)|(^|\/)(?:CLAUDE|GEMINI)\.md$|\.cursorrules$|\.windsurfrules$|copilot-instructions\.md$/i,
    msg: 'Archivo o carpeta de una herramienta de IA',
    ayuda: 'No se sube. Agregalo al .gitignore.',
  },
  {
    id: 'IA-AGENTS', nivel: w,
    re: /(^|\/)AGENTS\.md$/,
    msg: 'AGENTS.md: instrucciones para agentes de IA',
    ayuda: 'Si no es intencional, sacalo.',
  },
  {
    id: 'SECRETO-ARCHIVO', nivel: e,
    re: /(^|\/)\.env(\.(?!example$|sample$)[^/]*)?$|\.(?:pem|p12|pfx|key)$|(^|\/)id_(?:rsa|ed25519)(\.pub)?$|(^|\/)secretos?\.json$/i,
    msg: 'Archivo de secretos o claves',
    ayuda: 'No se sube. Agregalo al .gitignore.',
  },
  {
    id: 'BASURA', nivel: e,
    re: /(^|\/)(?:node_modules|__pycache__|\.venv|venv|\.next|\.turbo|\.idea)(\/|$)|(^|\/)\.vscode\/settings\.json$|\.pyc$|(^|\/)\.DS_Store$|(^|\/)Thumbs\.db$|\.log$|\.tmp$|(^|\/)~\$/i,
    msg: 'Archivo generado o del sistema',
    ayuda: 'Agregalo al .gitignore.',
  },
  {
    id: 'RENDER-INTERMEDIO', nivel: e,
    re: /partial_movie_files|(^|\/)media\/(?:videos|images|texts|Tex)\/|(^|\/)\.mezcla_|\.aux$|\.synctex\.gz$|\.fdb_latexmk$|\.fls$/i,
    msg: 'Archivo intermedio de un render',
    ayuda: 'Solo van los resultados finales.',
  },
  {
    id: 'DESCARGAS', nivel: w,
    re: /\.(?:zip|7z|rar|tar|gz|pptx|potx|docx|xlsx)$/i,
    msg: 'Archivo comprimido u ofimática',
    ayuda: '¿Tiene que estar en el repo?',
  },
  {
    id: 'CARPETA-TEMPORAL', nivel: w,
    re: /(^|\/)(?:borrar|tmp|temp|old|viejo|backup|copia)(\/|$)/i,
    msg: 'Carpeta que parece temporal',
    ayuda: '¿Tiene que estar en el repo?',
  },
];

export const TAMANO = { avisoMB: 20, errorMB: 50 };

export const EXT_BINARIA = new Set([
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm', '.mov', '.mp3',
  '.wav', '.ogg', '.pdf', '.ttf', '.otf', '.woff', '.woff2', '.ico', '.zip',
  '.7z', '.gz', '.pptx', '.docx', '.xlsx',
]);
export const EXT_CODIGO = new Set([
  '.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.json', '.yml',
  '.yaml', '.sh', '.tex', '.html', '.css', '.rs', '.toml',
]);
export const EXT_PROSA = new Set(['.md', '.txt', '.tex', '.html']);

// Un lockfile es una lista de hashes: no tiene prosa y confunde a los patrones.
export const SALTAR_CONTENIDO = /(^|\/)package-lock\.json$/;

// Autor o committer con identidad de IA.
export const IDENTIDAD = /(claude|anthropic|copilot|chatgpt|openai|gemini|\bbot\b|\[bot\])/i;

// ---------------------------------------------------------------------------
// Pruebas del propio auditor: node scripts/audit.mjs --autotest
// Cada caso dice qué reglas DEBEN saltar (espera) y qué reglas NO (noEspera).
// `texto` puede ser una función para no dejar un secreto de ejemplo escrito.
// ---------------------------------------------------------------------------
export const PRUEBAS = [
  { nombre: 'coautoría de IA en un commit', tipo: 'mensaje',
    texto: 'Agrega animaciones\n\nCo-Authored-By: Claude Opus <noreply@anthropic.com>',
    espera: ['IA-COAUTOR', 'IA-HERRAMIENTA', 'IA-MENCION-MSG'] },
  { nombre: 'firma de robot en un PR', tipo: 'mensaje',
    texto: 'Resumen\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)',
    espera: ['IA-ROBOT', 'IA-GENERADO', 'IA-HERRAMIENTA'] },
  { nombre: 'firma en español', tipo: 'mensaje',
    texto: 'Documentación creada con ChatGPT',
    espera: ['IA-GENERADO-ES'] },
  { nombre: 'coautor humano permitido', tipo: 'mensaje',
    texto: 'Ajusta la comisión mínima\n\nCo-authored-by: María Pérez <maria@example.org>',
    limpio: true },
  { nombre: 'mensaje normal', tipo: 'mensaje',
    texto: 'Corrige el cálculo de la comisión mínima',
    limpio: true },
  { nombre: 'resto de chat', tipo: 'contenido', ext: '.md',
    texto: 'Como modelo de lenguaje, no puedo verificar esto.\nEspero que esto te ayude.',
    espera: ['CHAT-IA', 'CHAT-CIERRE'] },
  { nombre: 'apertura de chat', tipo: 'contenido', ext: '.md',
    texto: 'Claro que sí, aquí tienes el resumen del proyecto.',
    espera: ['CHAT-APERTURA'] },
  { nombre: 'código cortado', tipo: 'contenido', ext: '.py',
    texto: 'def a():\n    pass\n# ... resto del código igual\n',
    espera: ['TRUNCADO'] },
  { nombre: 'valla de Markdown en un .py', tipo: 'contenido', ext: '.py',
    texto: '```python\nprint(1)\n```\n',
    espera: ['VALLA-MD'] },
  { nombre: 'valla de Markdown en un .md es normal', tipo: 'contenido', ext: '.md',
    texto: 'Ejemplo:\n\n```bash\nnode scripts/audit.mjs\n```\n',
    noEspera: ['VALLA-MD'] },
  { nombre: 'placeholder de equipo', tipo: 'contenido', ext: '.md',
    texto: 'Equipo: [Nombre 1] y [Nombre 2]. Hash: [hash 1–3]. Charlas: [N].',
    espera: ['PLACEHOLDER'] },
  { nombre: 'indexar en código no es un placeholder', tipo: 'contenido', ext: '.py',
    texto: 'ETAPAS[nombre]()\nx = lista[n]\n',
    noEspera: ['PLACEHOLDER'] },
  { nombre: 'clave secreta de Stellar', tipo: 'contenido', ext: '.ts',
    texto: () => `const clave = "S${'A'.repeat(55)}";`,
    espera: ['SECRETO-STELLAR'] },
  { nombre: 'clave pública de Stellar es normal', tipo: 'contenido', ext: '.ts',
    texto: () => `const cuenta = "G${'A'.repeat(55)}";`,
    noEspera: ['SECRETO-STELLAR'] },
  { nombre: 'token de GitHub', tipo: 'contenido', ext: '.sh',
    texto: () => `TOKEN=ghp_${'a'.repeat(36)}`,
    espera: ['SECRETO-GITHUB'] },
  { nombre: 'marketing inflado', tipo: 'contenido', ext: '.md',
    texto: 'Una solución revolucionaria, sin precedentes, de vanguardia.',
    espera: ['ESTILO-ES'] },
  { nombre: 'lenguaje legal del proyecto', tipo: 'contenido', ext: '.md',
    texto: 'Qhatu garantiza el pago y custodiamos tus fondos.',
    espera: ['LEG-GARANTIA', 'LEG-CUSTODIA'] },
  { nombre: '«no custodial» y «sin custodia» son correctos', tipo: 'contenido', ext: '.md',
    texto: 'Es un escrow no custodial, sin custodia de fondos.',
    noEspera: ['LEG-CUSTODIA'] },
  { nombre: 'título con emoji', tipo: 'contenido', ext: '.md',
    texto: '## 🚀 Características\n- ✅ Rápido\n',
    espera: ['EMOJI-TITULO', 'EMOJI-LISTA'] },
  { nombre: 'carpeta de herramienta de IA', tipo: 'archivo', ruta: '.claude/settings.json',
    espera: ['IA-ARCHIVO'] },
  { nombre: 'archivo de instrucciones de IA', tipo: 'archivo', ruta: 'CLAUDE.md',
    espera: ['IA-ARCHIVO'] },
  { nombre: 'archivo .env', tipo: 'archivo', ruta: 'animaciones/.env',
    espera: ['SECRETO-ARCHIVO'] },
  { nombre: '.env.example es normal', tipo: 'archivo', ruta: '.env.example',
    limpio: true },
  { nombre: 'caché de Manim', tipo: 'archivo', ruta: 'media/videos/x/1080p30/partial_movie_files/a.mp4',
    espera: ['RENDER-INTERMEDIO'] },
  { nombre: 'archivo normal', tipo: 'archivo', ruta: 'docs/como-funciona.md',
    limpio: true },
  { nombre: 'archivo enorme', tipo: 'archivo', ruta: 'video/x.mp4', bytes: 80 * 1048576,
    espera: ['TAMANO'] },
];
