#!/usr/bin/env node
// Auditor de lo que se sube a GitHub.
// Busca firmas de IA, restos de chat, secretos, placeholders y basura.
// Sin dependencias: Node 18+ y git. Ayuda: node scripts/audit.mjs --help

import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as R from './audit.reglas.mjs';

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..');
const PROPIOS = new Set(['scripts/audit.mjs', 'scripts/audit.reglas.mjs']);
const CEROS = '0'.repeat(40);
const MB = 1048576;

const color = Boolean(process.stderr.isTTY || process.env.FORCE_COLOR);
const pintar = (codigo, s) => (color ? `\x1b[${codigo}m${s}\x1b[0m` : s);

const AYUDA = `Auditor de lo que se sube

  node scripts/audit.mjs --staged            lo que está en el índice (pre-commit)
  node scripts/audit.mjs --msg <archivo>     el mensaje de un commit (commit-msg)
  node scripts/audit.mjs --push              lo que está por subirse (pre-push, lee stdin)
  node scripts/audit.mjs --ci                el repo entero y los mensajes (GitHub Actions)
  node scripts/audit.mjs --all               el repo entero y todo el historial
  node scripts/audit.mjs --texto "..."       un texto suelto, p. ej. el cuerpo de un PR ("-" lee stdin)
  node scripts/audit.mjs --autotest          prueba el auditor contra casos conocidos

  --strict   los avisos también bloquean
  --json     salida en JSON

Salida 0 = limpio, 1 = hay hallazgos que bloquean, 2 = el auditor no pudo correr.`;

// ---------------------------------------------------------------------------
// Utilidades
// ---------------------------------------------------------------------------
function git(args, { buffer = false, input } = {}) {
  return execFileSync('git', args, {
    cwd: RAIZ,
    encoding: buffer ? 'buffer' : 'utf8',
    input,
    maxBuffer: 1024 * MB,
    stdio: ['pipe', 'pipe', 'pipe'],
  });
}

const hallazgos = [];
const vistos = new Set();
let suprimidos = 0;

function registrar(regla, tipo, donde, linea, extracto) {
  const clave = `${regla.id}|${donde}|${linea}`;
  if (vistos.has(clave)) return;
  vistos.add(clave);
  hallazgos.push({
    id: regla.id, nivel: regla.nivel, tipo, donde, linea,
    msg: regla.msg, ayuda: regla.ayuda, extracto,
  });
}

const cache = new Map();
function compilar(re) {
  let c = cache.get(re);
  if (!c) {
    c = new RegExp(re.source, [...new Set([...re.flags, 'g', 'u'])].join(''));
    cache.set(re, c);
  }
  return c;
}

function indiceLineas(texto) {
  const inicios = [0];
  for (let i = 0; i < texto.length; i++) {
    if (texto.charCodeAt(i) === 10) inicios.push(i + 1);
  }
  return inicios;
}

function lineaDe(inicios, pos) {
  let lo = 0;
  let hi = inicios.length - 1;
  while (lo < hi) {
    const medio = (lo + hi + 1) >> 1;
    if (inicios[medio] <= pos) lo = medio;
    else hi = medio - 1;
  }
  return lo;
}

function aplicar(reglas, tipo, donde, texto) {
  if (!texto) return;
  const inicios = indiceLineas(texto);
  for (const regla of reglas) {
    if (regla.excepto && regla.excepto.test(donde)) continue;
    for (const m of texto.matchAll(compilar(regla.re))) {
      const ln = lineaDe(inicios, m.index);
      const fin = ln + 1 < inicios.length ? inicios[ln + 1] - 1 : texto.length;
      const fila = texto.slice(inicios[ln], fin).replace(/\r$/, '');
      if (fila.includes('audit-ok')) { suprimidos++; continue; }
      registrar(regla, tipo, donde, ln + 1, fila.trim().slice(0, 160));
    }
  }
}

// ---------------------------------------------------------------------------
// Qué se revisa
// ---------------------------------------------------------------------------
function reglasDeContenido(ext) {
  const grupos = [R.ATRIBUCION, R.MENCION_IA_CONTENIDO, R.RESTOS_CHAT, R.TRUNCADO, R.PLACEHOLDERS, R.SECRETOS];
  if (R.EXT_CODIGO.has(ext)) grupos.push(R.FENCE);
  if (R.EXT_PROSA.has(ext)) grupos.push(R.ESTILO, R.LENGUAJE_PROYECTO, R.PLACEHOLDERS_PROSA);
  if (ext === '.md') grupos.push(R.EMOJI);
  return grupos.flat();
}

function auditarMensaje(donde, texto, tipo = 'commit') {
  const limpio = tipo === 'commit'
    ? texto.split('\n').filter((l) => !l.startsWith('#')).join('\n')
    : texto;
  aplicar([...R.ATRIBUCION, ...R.MENSAJE_EXTRA, ...R.RESTOS_CHAT], tipo, donde, limpio);
}

function auditarIdentidad(donde, nombre, correo) {
  if (R.IDENTIDAD.test(`${nombre} ${correo}`)) {
    registrar({
      id: 'IA-IDENTIDAD', nivel: 'error',
      msg: `Autor o committer con identidad de IA: ${nombre} <${correo}>`,
      ayuda: 'Cambiá user.name y user.email.',
    }, 'commit', donde, 0, `${nombre} <${correo}>`);
  }
}

function auditarRuta(ruta, bytes) {
  for (const regla of R.ARCHIVOS) {
    if (regla.re.test(ruta) && !(regla.excepto && regla.excepto.test(ruta))) registrar(regla, 'archivo', ruta, 0, ruta);
  }
  const mb = bytes / MB;
  if (mb > R.TAMANO.errorMB) {
    registrar({ id: 'TAMANO', nivel: 'error', msg: `Pesa ${mb.toFixed(1)} MB (límite ${R.TAMANO.errorMB})`,
      ayuda: 'GitHub rechaza más de 100 MB. Comprimilo o subilo como release.' }, 'archivo', ruta, 0, ruta);
  } else if (mb > R.TAMANO.avisoMB) {
    registrar({ id: 'TAMANO', nivel: 'warn', msg: `Pesa ${mb.toFixed(1)} MB`,
      ayuda: 'Un repo liviano se clona rápido. ¿Se puede comprimir?' }, 'archivo', ruta, 0, ruta);
  }
}

function auditarContenido(ruta, leer) {
  if (PROPIOS.has(ruta) || R.SALTAR_CONTENIDO.test(ruta)) return;
  const ext = extname(ruta).toLowerCase();
  if (R.EXT_BINARIA.has(ext)) return;
  const buf = leer();
  if (buf.length > 3 * MB || buf.subarray(0, 8000).includes(0)) return;
  aplicar(reglasDeContenido(ext), 'archivo', ruta, buf.toString('utf8'));
}

function auditarIndice() {
  const nombres = git(['diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z'])
    .split('\0').filter(Boolean);
  for (const ruta of nombres) {
    auditarRuta(ruta, Number(git(['cat-file', '-s', `:${ruta}`]).trim()));
    auditarContenido(ruta, () => git(['show', `:${ruta}`], { buffer: true }));
  }
  return nombres.length;
}

function auditarArbol(ref) {
  try { git(['rev-parse', '--verify', '--quiet', `${ref}^{commit}`]); } catch { return 0; }
  const salida = git(['ls-tree', '-r', '-z', '--long', ref]);
  let n = 0;
  for (const entrada of salida.split('\0').filter(Boolean)) {
    const tab = entrada.indexOf('\t');
    const [, tipo, sha, tam] = entrada.slice(0, tab).trim().split(/\s+/);
    if (tipo !== 'blob') continue;
    const ruta = entrada.slice(tab + 1);
    n++;
    auditarRuta(ruta, Number(tam));
    auditarContenido(ruta, () => git(['cat-file', 'blob', sha], { buffer: true }));
  }
  return n;
}

function auditarCommits(rango) {
  if (rango.length === 1 && !rango[0].includes('..')) {
    try { git(['rev-parse', '--verify', '--quiet', `${rango[0]}^{commit}`]); } catch { return 0; }
  }
  const SEP = '\x1e';
  const CAMPO = '\x1f';
  const salida = git(['log', `--format=%H${CAMPO}%an${CAMPO}%ae${CAMPO}%cn${CAMPO}%ce${CAMPO}%B${SEP}`, ...rango]);
  let n = 0;
  for (const registro of salida.split(SEP)) {
    const t = registro.replace(/^\n/, '');
    if (!t.trim()) continue;
    const [sha, an, ae, cn, ce, cuerpo] = t.split(CAMPO);
    const donde = `commit ${sha.slice(0, 7)}`;
    n++;
    auditarIdentidad(donde, an, ae);
    auditarIdentidad(donde, cn, ce);
    auditarMensaje(donde, cuerpo ?? '');
  }
  return n;
}

function auditarPush(entrada) {
  const refs = entrada.split('\n').map((l) => l.trim().split(/\s+/)).filter((p) => p.length >= 4);
  const arboles = new Set();
  let commits = 0;
  for (const [, local, , remoto] of refs) {
    if (local === CEROS) continue;
    const rango = remoto === CEROS ? [local, '--not', '--remotes'] : [`${remoto}..${local}`];
    try {
      commits += auditarCommits(rango);
    } catch {
      commits += auditarCommits([local]);
    }
    arboles.add(local);
  }
  let archivos = 0;
  for (const sha of arboles) archivos += auditarArbol(sha);
  return { commits, archivos };
}

// ---------------------------------------------------------------------------
// Autoprueba
// ---------------------------------------------------------------------------
function autotest() {
  let fallos = 0;
  for (const p of R.PRUEBAS) {
    hallazgos.length = 0;
    vistos.clear();
    const texto = typeof p.texto === 'function' ? p.texto() : p.texto;
    if (p.tipo === 'mensaje') auditarMensaje('prueba', texto, 'pr');
    else if (p.tipo === 'contenido') aplicar(reglasDeContenido(p.ext), 'archivo', `prueba${p.ext}`, texto);
    else auditarRuta(p.ruta, p.bytes ?? 100);

    const ids = new Set(hallazgos.map((h) => h.id));
    const faltan = (p.espera ?? []).filter((id) => !ids.has(id));
    const sobran = (p.noEspera ?? []).filter((id) => ids.has(id));
    const ensuciado = p.limpio && ids.size > 0 ? [...ids] : [];
    const bien = !faltan.length && !sobran.length && !ensuciado.length;
    if (!bien) fallos++;
    const detalle = bien ? '' : `  (faltan: ${faltan.join(', ') || '-'}; sobran: ${[...sobran, ...ensuciado].join(', ') || '-'})`;
    console.error(`${bien ? pintar(32, 'ok   ') : pintar(31, 'FALLA')} ${p.nombre}${detalle}`);
  }
  console.error(`\n${R.PRUEBAS.length - fallos}/${R.PRUEBAS.length} casos bien`);
  return fallos ? 1 : 0;
}

// ---------------------------------------------------------------------------
// Informe
// ---------------------------------------------------------------------------
function informar({ strict, json, alcance }) {
  const errores = hallazgos.filter((h) => h.nivel === 'error');
  const avisos = hallazgos.filter((h) => h.nivel !== 'error');

  if (json) {
    console.log(JSON.stringify({ errores, avisos, suprimidos, alcance }, null, 2));
  } else {
    const orden = [...errores, ...avisos];
    for (const h of orden) {
      const etiqueta = h.nivel === 'error' ? pintar(31, 'ERROR') : pintar(33, 'AVISO');
      const lugar = h.linea ? `${h.donde}:${h.linea}` : h.donde;
      console.error(`${etiqueta} ${pintar(1, h.id)}  ${lugar}`);
      console.error(`       ${h.msg}`);
      if (h.extracto && h.extracto !== h.donde) console.error(pintar(90, `       > ${h.extracto}`));
      if (h.ayuda) console.error(`       -> ${h.ayuda}`);
    }
    const partes = [`${errores.length} errores`, `${avisos.length} avisos`];
    if (suprimidos) partes.push(`${suprimidos} saltados con audit-ok`);
    const linea = `Auditor: ${partes.join(', ')}${alcance ? ` (${alcance})` : ''}`;
    console.error(errores.length ? pintar(31, linea) : pintar(32, linea));
  }

  if (process.env.GITHUB_ACTIONS === 'true') {
    for (const h of hallazgos) {
      const tipo = h.nivel === 'error' ? 'error' : 'warning';
      const sitio = h.tipo === 'archivo' ? `file=${h.donde}${h.linea ? `,line=${h.linea}` : ''},` : '';
      console.log(`::${tipo} ${sitio}title=${h.id}::${h.tipo === 'archivo' ? '' : `${h.donde}: `}${h.msg}`);
    }
  }
  return errores.length || (strict && avisos.length) ? 1 : 0;
}

// ---------------------------------------------------------------------------
// Principal
// ---------------------------------------------------------------------------
function principal() {
  const args = process.argv.slice(2);
  const opciones = { strict: args.includes('--strict'), json: args.includes('--json') };
  const modo = args.find((a) => a.startsWith('--') && !['--strict', '--json'].includes(a));
  const siguiente = args[args.indexOf(modo) + 1];
  let alcance = '';

  switch (modo) {
    case '--staged': {
      const n = auditarIndice();
      if (n === 0) return 0;
      alcance = `${n} archivos del índice`;
      break;
    }
    case '--msg': {
      if (!siguiente) throw new Error('Falta el archivo del mensaje');
      auditarMensaje('mensaje del commit', readFileSync(siguiente, 'utf8'));
      const ident = git(['var', 'GIT_AUTHOR_IDENT']).trim().match(/^(.*) <(.*)> \d+ [+-]\d{4}$/);
      if (ident) auditarIdentidad('mensaje del commit', ident[1], ident[2]);
      alcance = 'mensaje del commit';
      break;
    }
    case '--push': {
      const { commits, archivos } = auditarPush(readFileSync(0, 'utf8'));
      alcance = `${commits} commits, ${archivos} archivos`;
      break;
    }
    case '--ci': {
      const archivos = auditarArbol('HEAD');
      const base = process.env.AUDIT_BASE;
      let rango = ['HEAD'];
      if (base && base !== CEROS) {
        try { git(['cat-file', '-e', `${base}^{commit}`]); rango = [`${base}..HEAD`]; } catch { /* sin base: todo el historial */ }
      }
      const commits = auditarCommits(rango);
      if (process.env.PR_TITLE) auditarMensaje('título del PR', process.env.PR_TITLE, 'pr');
      if (process.env.PR_BODY) auditarMensaje('descripción del PR', process.env.PR_BODY, 'pr');
      alcance = `${commits} commits, ${archivos} archivos`;
      break;
    }
    case '--all': {
      const archivos = auditarArbol('HEAD');
      const commits = auditarCommits(['HEAD']);
      alcance = `${commits} commits, ${archivos} archivos`;
      break;
    }
    case '--texto': {
      if (siguiente === undefined) throw new Error('Falta el texto');
      auditarMensaje('texto', siguiente === '-' ? readFileSync(0, 'utf8') : siguiente, 'pr');
      alcance = 'texto';
      break;
    }
    case '--autotest':
      return autotest();
    case '--help':
    case undefined:
      console.error(AYUDA);
      return modo ? 0 : 2;
    default:
      console.error(`Opción desconocida: ${modo}\n\n${AYUDA}`);
      return 2;
  }
  return informar({ ...opciones, alcance });
}

try {
  process.exitCode = principal();
} catch (error) {
  console.error(pintar(31, `El auditor no pudo correr: ${error.message}`));
  process.exitCode = 2;
}
