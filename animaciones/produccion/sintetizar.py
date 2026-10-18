"""Sintetiza una línea de voz por beat y mide cuánto dura cada una.

Las escenas leen esas duraciones para dejar cada imagen en pantalla exactamente
lo que dura su frase. Así la voz nunca habla de algo que ya salió de cuadro.

    python animaciones/produccion/sintetizar.py <carpeta_de_salida>

Deja <salida>/clips/01.mp3, 02.mp3… (uno por frase, en orden) y <salida>/voz.json.
Los clips no se vuelven a pedir si el texto no cambió.
"""

import asyncio
import hashlib
import json
import sys
from pathlib import Path

import edge_tts
from pydub import AudioSegment

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from guion import lineas, para_voz  # noqa: E402

VOZ = "es-BO-MarceloNeural"
RATE = "+8%"


async def pedir(texto, destino):
    await edge_tts.Communicate(texto, VOZ, rate=RATE).save(str(destino))


def main(salida):
    salida = Path(salida)
    clips = salida / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    previo = {}
    ruta_json = salida / "voz.json"
    if ruta_json.exists():
        previo = json.loads(ruta_json.read_text(encoding="utf-8")).get("huellas", {})

    orden, duraciones, huellas = [], {}, {}
    for n, (_, ident, texto, voz) in enumerate(lineas(), start=1):
        hablado = para_voz(texto, voz)
        huella = hashlib.sha1(f"{VOZ}|{RATE}|{hablado}".encode("utf-8")).hexdigest()
        mp3 = clips / f"{n:02d}.mp3"
        if not mp3.exists() or previo.get(ident) != huella:
            asyncio.run(pedir(hablado, mp3))
        duraciones[ident] = round(AudioSegment.from_file(str(mp3)).duration_seconds, 3)
        huellas[ident] = huella
        orden.append(ident)
        print(f"{n:02d} {ident:6s} {duraciones[ident]:5.2f} s  {len(hablado):3d} car.")

    ruta_json.write_text(json.dumps(
        {"voz": VOZ, "rate": RATE, "orden": orden, "duraciones": duraciones, "huellas": huellas},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nHabla en total {sum(duraciones.values()):.1f} s en {len(orden)} frases")


if __name__ == "__main__":
    main(sys.argv[1])
