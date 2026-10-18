"""Orquestador del pitch: voz -> láminas (Manim y Remotion) -> video -> mezcla -> deck.

    python animaciones/producir_pitch.py                 # todo, en orden
    python animaciones/producir_pitch.py voz laminas     # solo esas etapas

Etapas: voz, laminas, flujo, video, mezcla, deck.

Hace falta el motor de animación (NEMAXYZ_MOTOR, ver docs/animaciones.md), Manim,
Node, ffmpeg y edge-tts. El trabajo intermedio va a una carpeta corta
(QHATU_TRABAJO, por defecto ~/qh): Windows corta las rutas de más de 260 caracteres.
Los resultados finales se copian a video/ y deck/.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))

import guion  # noqa: E402

TRABAJO = Path(os.environ.get("QHATU_TRABAJO", Path.home() / "qh"))
MOTOR = Path(os.environ.get("NEMAXYZ_MOTOR", ""))
RETARDO, PAUSA = 0.20, 0.20            # los mismos de qhatu_base.py
VIDEO_ORDEN = ["S1Portada", "S2Problema", "S3Solucion", "S4Flujo", "S5Stellar", "S6Modelo", "S8Plan"]
LAMINAS_MANIM = ["S1Portada", "S2Problema", "S3Solucion", "S5Stellar", "S6Modelo", "S7Validacion", "S8Plan"]
ESCENA_DE = {"S1": "S1Portada", "S2": "S2Problema", "S3": "S3Solucion", "S4": "S4Flujo",
             "S5": "S5Stellar", "S6": "S6Modelo", "S8": "S8Plan"}
CLIMAS = ["misterio", "tension", "revelacion", "dato", "revelacion", "dato", "cierre"]


def ejecutar(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def entorno(**extra):
    env = dict(os.environ)
    env.update({"PYTHONIOENCODING": "utf-8", "NEMAXYZ_MOTOR": str(MOTOR),
                "QHATU_VOZ": str(TRABAJO / "voz" / "voz.json"),
                "QHATU_TIEMPOS": str(TRABAJO / "tiempos"), "GODEBUG": "tlsmlkem=0"})
    env.update({k: str(v) for k, v in extra.items()})
    return env


def duracion(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


# ------------------------------------------------------------------ etapas
def etapa_voz():
    from produccion import sintetizar
    sintetizar.main(TRABAJO / "voz")


def _render_manim(escenas, snapshot=False):
    """Una escena por proceso y cada una con su caché: compartirla las pisa entre sí."""
    procesos = []
    for e in escenas:
        carpeta = TRABAJO / ("fijas" if snapshot else "manim") / e
        cmd = [sys.executable, "-m", "manim", "render"] + (["-s"] if snapshot else []) + \
              ["--media_dir", str(carpeta), "laminas.py", e]
        env = entorno(**({"QHATU_SNAPSHOT": "1"} if snapshot else {}))
        if snapshot:
            env.pop("QHATU_TIEMPOS", None)
        registro = TRABAJO / "logs"
        registro.mkdir(exist_ok=True)
        log = open(registro / f"{'fija_' if snapshot else ''}{e}.log", "w", encoding="utf-8")
        procesos.append((e, log, subprocess.Popen(cmd, cwd=AQUI / "manim", env=env, stdout=log, stderr=log)))
    for e, log, p in procesos:
        p.wait()
        log.close()
        if p.returncode:
            cola = Path(log.name).read_text(encoding="utf-8", errors="replace")[-1500:]
            raise SystemExit(f"[{e}] falló el render:\n{cola}")


def etapa_laminas():
    (TRABAJO / "tiempos").mkdir(parents=True, exist_ok=True)
    _render_manim(LAMINAS_MANIM)


def tiempos_s4():
    """Cuándo entra cada paso de la maqueta: se calcula igual que en las escenas de Manim."""
    d = json.loads((TRABAJO / "voz" / "voz.json").read_text(encoding="utf-8"))["duraciones"]
    t, marcas, inicios = 0.5, {}, {}
    for ident in [i for i, _, _ in guion.ESCENAS["S4"]]:
        inicios[ident[-1]] = t
        marcas[ident] = t + RETARDO
        t += RETARDO + d[ident] + PAUSA
    return {"escena": "S4Flujo", "duracion": round(t + 0.6, 3), "marcas": marcas}, inicios


def etapa_flujo():
    tiempos, inicios = tiempos_s4()
    (TRABAJO / "tiempos").mkdir(parents=True, exist_ok=True)
    (TRABAJO / "tiempos" / "S4Flujo.json").write_text(json.dumps(tiempos, indent=2), encoding="utf-8")
    t = guion.DATOS["testnet"]
    props = {"duracion": tiempos["duracion"], "inicios": inicios, "estado": t["estado"],
             "hashes": {"deposito": t["deposito"], "liberacion30": t["liberacion_30"], "liberacion70": t["liberacion_70"]}}
    (TRABAJO / "s4").mkdir(parents=True, exist_ok=True)
    ruta_props = TRABAJO / "s4" / "props.json"
    ruta_props.write_text(json.dumps(props), encoding="utf-8")
    ejecutar(["npx", "remotion", "render", "src/index.ts", "Flujo", str(TRABAJO / "s4" / "S4Flujo.mp4"),
              f"--props={ruta_props}", "--crf=18"], cwd=AQUI / "remotion", env=entorno(), shell=(os.name == "nt"))


def ruta_clip(escena):
    if escena == "S4Flujo":
        return TRABAJO / "s4" / "S4Flujo.mp4"
    return next((TRABAJO / "manim" / escena).rglob(f"{escena}.mp4"))


def etapa_video():
    """Une las láminas con el filtro concat: los clips de Manim y de Remotion tienen
    bases de tiempo distintas y el concat por archivos repetía cuadros."""
    entradas = []
    for e in VIDEO_ORDEN:
        entradas += ["-i", str(ruta_clip(e))]
    filtro = "".join(f"[{i}:v:0]" for i in range(len(VIDEO_ORDEN))) + \
        f"concat=n={len(VIDEO_ORDEN)}:v=1:a=0,fps=30,format=yuv420p[v]"
    ejecutar(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", filtro, "-map", "[v]",
              "-c:v", "libx264", "-crf", "20", "-preset", "medium", str(TRABAJO / "pitch_mudo.mp4")])


def linea_de_tiempo():
    """Frases y cortes de sección sobre el video ya unido."""
    inicio, t0 = {}, 0.0
    for e in VIDEO_ORDEN:
        inicio[e] = t0
        t0 += duracion(ruta_clip(e))
    frases = []
    for esc, ident, texto, _ in guion.lineas():
        escena = ESCENA_DE[esc]
        marcas = json.loads((TRABAJO / "tiempos" / f"{escena}.json").read_text(encoding="utf-8"))["marcas"]
        frases.append({"t": round(inicio[escena] + marcas[ident], 3), "texto": texto})
    return {"frases": frases, "secciones": [round(inicio[e], 3) for e in VIDEO_ORDEN[1:]], "total": t0}


def etapa_mezcla():
    """La mezcla la hace el motor: voz por frase, música por clima y -14 LUFS."""
    sys.path.insert(0, str(MOTOR / "produccion"))
    import producir as motor
    lt = linea_de_tiempo()
    salida = MOTOR / "salida"
    salida.mkdir(exist_ok=True)
    datos = {"video": str(TRABAJO / "pitch_mudo.mp4"), "salida": "salida/qhatu-pitch-3min.mp4",
             "voz": "es-BO-MarceloNeural", "bpm": 110, "climas": CLIMAS,
             "secciones": lt["secciones"], "frases": lt["frases"]}
    ruta = MOTOR / "salida" / "qhatu_linea.json"
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    motor.producir(ruta, clips=str(TRABAJO / "voz" / "clips"))
    (RAIZ / "video").mkdir(exist_ok=True)
    for nombre in ("qhatu-pitch-3min.mp4", "qhatu-pitch-3min_SIN_VOZ.mp4"):
        shutil.copy2(salida / nombre, RAIZ / "video" / nombre)
    print(f"Video listo: {lt['total']:.1f} s")


def etapa_deck():
    """Una imagen fija por lámina (Manim y Remotion) y el PDF que las junta."""
    _render_manim(LAMINAS_MANIM, snapshot=True)
    destino = RAIZ / "deck" / "laminas"
    destino.mkdir(parents=True, exist_ok=True)
    nombres = {"S1Portada": "01-portada", "S2Problema": "02-problema", "S3Solucion": "03-solucion",
               "S4Flujo": "04-flujo", "S5Stellar": "05-stellar", "S6Modelo": "06-modelo",
               "S7Validacion": "07-validacion", "S8Plan": "08-plan"}
    for e in LAMINAS_MANIM:
        png = next((TRABAJO / "fijas" / e).rglob(f"{e}_ManimCE_*.png"))
        shutil.copy2(png, destino / f"{nombres[e]}.png")
    props = json.loads((TRABAJO / "s4" / "props.json").read_text(encoding="utf-8"))
    ejecutar(["npx", "remotion", "still", "src/index.ts", "Flujo", str(destino / f"{nombres['S4Flujo']}.png"),
              f"--props={TRABAJO / 's4' / 'props.json'}", f"--frame={round(props['duracion'] * 30) - 2}"],
             cwd=AQUI / "remotion", env=entorno(), shell=(os.name == "nt"))
    from PIL import Image
    paginas = [Image.open(destino / f"{n}.png").convert("RGB") for n in sorted(nombres.values())]
    paginas[0].save(RAIZ / "deck" / "qhatu-deck.pdf", save_all=True, append_images=paginas[1:], resolution=144.0, quality=95)
    print("Deck:", RAIZ / "deck" / "qhatu-deck.pdf")


def etapa_guion():
    """video/guion.md: cada frase con su tiempo en el video y quién la lee."""
    lt = linea_de_tiempo()
    tiempo = lambda s: f"{int(s // 60)}:{s % 60:04.1f}".replace(".", ",")
    salida = [f"# Guion del pitch\n",
              f"Duración total: {tiempo(lt['total'])}. Cada frase trae su tiempo en el video. "
              "Quien lee cada escena es una propuesta: se cambia en `animaciones/guion.py`.\n"]
    i = 0
    for esc in guion.ORDEN:
        salida.append(f"\n## {guion.TITULOS[esc]}\n\n| Tiempo | Lee | Frase |\n|---|---|---|")
        for ident, texto, _ in guion.ESCENAS[esc]:
            salida.append(f"| {tiempo(lt['frases'][i]['t'])} | {guion.quien(esc, ident)} | {texto} |")
            i += 1
    (RAIZ / "video" / "guion.md").write_text("\n".join(salida) + "\n", encoding="utf-8")


def etapa_pptx():
    """deck/qhatu-deck.pptx con las animaciones y las notas del orador."""
    from produccion import armar_pptx
    armar_pptx.main(TRABAJO)


ETAPAS = {"voz": etapa_voz, "laminas": etapa_laminas, "flujo": etapa_flujo, "video": etapa_video,
          "mezcla": etapa_mezcla, "deck": etapa_deck, "guion": etapa_guion, "pptx": etapa_pptx}

if __name__ == "__main__":
    if not (MOTOR / "comun" / "estilo.py").is_file():
        raise SystemExit("Falta el motor: definí NEMAXYZ_MOTOR con la carpeta de nemaxyz-motor.")
    TRABAJO.mkdir(parents=True, exist_ok=True)
    elegidas = sys.argv[1:] or list(ETAPAS)
    for nombre in elegidas:
        print(f"== {nombre}")
        ETAPAS[nombre]()
