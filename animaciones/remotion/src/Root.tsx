import React from "react";
import { Composition } from "remotion";
import { Flujo, FlujoProps } from "./Flujo";

const FPS = 30;

// Valores de ejemplo para el estudio de Remotion. Los de verdad los escribe
// animaciones/produccion/linea_s4.py a partir de la duración de cada frase.
const porDefecto: FlujoProps = {
  duracion: 26,
  inicios: { a: 0.7, b: 4.6, c: 8.6, d: 12.5, e: 18.7 },
  estado: "maqueta",
  hashes: { deposito: "", liberacion30: "", liberacion70: "" },
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Flujo"
    component={Flujo}
    width={1920}
    height={1080}
    fps={FPS}
    durationInFrames={Math.round(porDefecto.duracion * FPS)}
    defaultProps={porDefecto}
    calculateMetadata={({ props }) => ({ durationInFrames: Math.round(props.duracion * FPS) })}
  />
);
