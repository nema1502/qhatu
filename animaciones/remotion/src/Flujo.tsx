import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// Maqueta animada de la pantalla del trato. Cada paso del guion entra en el segundo
// que le toca (`inicios`, en segundos), medido sobre la voz.

export type FlujoProps = {
  duracion: number;
  inicios: { a: number; b: number; c: number; d: number; e: number };
  estado: "maqueta" | "real";
  hashes: { deposito: string; liberacion30: string; liberacion70: string };
};

const C = {
  marino: "#13203A", marino2: "#1C2C4C", crema: "#F6F2EA", crema2: "#FFFCF6", terra: "#A84A24",
  naranja: "#F0915A", borde: "#E2D8C5", tinta: "#13203A", suave: "#3D4757", ok: "#1F8A5B", alerta: "#C0392B",
};
const TITULO = "Bahnschrift, 'Segoe UI', system-ui, sans-serif";
const CUERPO = "'Segoe UI', system-ui, sans-serif";
const MONO = "Consolas, 'Courier New', monospace";

// geometría fija: así el cursor y las monedas saben adónde ir
const WX = 160, WY = 110, WW = 1600, WH = 860;
const BX = 192, BY = 206;               // origen del cuerpo de la ventana
const LW = 500;                          // ancho de la columna izquierda
const RX = 724, RW = 1004;               // columna derecha
const BARRA_X = RX + 28, BARRA_W = RW - 56, BARRA_Y = BY + 168;

const miles = (n: number) => {
  const e = Math.round(n);
  return e >= 1000 ? `${Math.floor(e / 1000)}.${String(e % 1000).padStart(3, "0")}` : String(e);
};
const corto = (h: string) => (h ? `${h.slice(0, 8)}…${h.slice(-6)}` : "");

const Txt: React.FC<{
  x: number; y: number; size?: number; color?: string; bold?: boolean; font?: string; w?: number;
  align?: "left" | "right" | "center"; opacity?: number; children: React.ReactNode;
}> = ({ x, y, size = 28, color = C.tinta, bold = false, font = CUERPO, w, align = "left", opacity = 1, children }) => (
  <div style={{
    position: "absolute", left: x, top: y, width: w, textAlign: align, fontSize: size, color,
    fontWeight: bold ? 700 : 400, fontFamily: font, whiteSpace: "nowrap", lineHeight: 1.2, opacity,
  }}>{children}</div>
);

const Panel: React.FC<{ x: number; y: number; w: number; h: number; fondo?: string; children?: React.ReactNode }> =
  ({ x, y, w, h, fondo = C.crema2, children }) => (
    <div style={{
      position: "absolute", left: x, top: y, width: w, height: h, background: fondo, borderRadius: 22,
      border: `2px solid ${C.borde}`,
    }}>{children}</div>
  );

const Chip: React.FC<{ x: number; y: number; texto: string; tipo: "pendiente" | "deposito" | "ok" | "alerta" }> =
  ({ x, y, texto, tipo }) => {
    const col = { pendiente: [C.borde, C.suave], deposito: [C.terra, C.crema], ok: [C.ok, C.crema], alerta: [C.alerta, C.crema] }[tipo];
    return (
      <div style={{
        position: "absolute", left: x, top: y, padding: "6px 16px", borderRadius: 999, background: col[0], color: col[1],
        fontFamily: CUERPO, fontWeight: 700, fontSize: 24, whiteSpace: "nowrap",
      }}>{texto}</div>
    );
  };

export const Flujo: React.FC<FlujoProps> = ({ inicios, estado, hashes }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  const fA = f(inicios.a), fB = f(inicios.b), fC = f(inicios.c), fD = f(inicios.d), fE = f(inicios.e);
  const sube = (ini: number, dur = 20) =>
    interpolate(frame, [ini, ini + dur], [0, 1], {
      extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
    });
  const real = estado === "real";

  // ------------------------------------------------------------ línea de tiempo
  const entrada = sube(fA - f(0.3), 24);
  const pDep = sube(fB + 6, 48);
  const p30 = sube(fC + 12, 34);
  const filaDoc = [0, 1, 2, 3].map((i) => sube(fD + 8 + i * 22, 14));
  const fError = fD + 8 + 3 * 22 + 28;
  const enError = frame >= fError && frame < fE + 36;
  const corregido = frame >= fE + 36;
  const fClic = fE + 74;
  const clic = frame >= fClic;
  const p70 = sube(fClic + 8, 40);

  const enEscrow = 1000 * pDep - 300 * p30 - 700 * p70;
  const recibido = 300 * p30 + 700 * p70;
  const paso = frame >= fE ? 4 : frame >= fD ? 3 : frame >= fB ? (frame >= fC ? 2 : 1) : 0;

  // ------------------------------------------------------------ monedas que viajan al exportador
  const meta = { x: BX + 250, y: BY + 500 + 24 + 70 };
  const moneda = (p: number, desdeX: number) => {
    if (p <= 0 || p >= 1) return null;
    const x = desdeX + (meta.x - desdeX) * p;
    const y = BARRA_Y + 14 + (meta.y - (BARRA_Y + 14)) * p - Math.sin(p * Math.PI) * 60;
    return (
      <div style={{
        position: "absolute", left: x - 26, top: y - 26, width: 52, height: 52, borderRadius: 26, background: C.naranja,
        border: `4px solid ${C.marino}`, color: C.marino, fontFamily: TITULO, fontWeight: 700, fontSize: 30, textAlign: "center",
        lineHeight: "44px",
      }}>$</div>
    );
  };

  // ------------------------------------------------------------ cursor que aprueba
  const cursor = (() => {
    const ini = fE + 36;
    if (frame < ini || frame > fClic + 26) return null;
    const objetivo = { x: BX + LW - 28 - 60, y: BY + 326 + 80 + 22 };
    const p = interpolate(frame, [ini, ini + 30], [0, 1], { extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    const x = 1150 + (objetivo.x - 1150) * p;
    const y = 700 + (objetivo.y - 700) * p;
    const op = interpolate(frame, [fClic + 12, fClic + 26], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return (
      <svg style={{ position: "absolute", left: x, top: y, opacity: op }} width="44" height="44" viewBox="0 0 24 24">
        <path d="M4 2 L4 19 L8.5 15 L11.5 22 L14 21 L11 14 L17 14 Z" fill={C.marino} stroke={C.crema} strokeWidth="1.4" />
      </svg>
    );
  })();

  // ------------------------------------------------------------ estados de los hitos
  const ms1: [string, "pendiente" | "ok"] = frame >= fC + 12 + 30 ? ["Liberado", "ok"] : ["Pendiente", "pendiente"];
  const ms2: [string, "pendiente" | "alerta" | "deposito" | "ok"] =
    p70 >= 1 ? ["Liberado", "ok"] : clic ? ["Aprobado", "deposito"] : enError ? ["Retenido", "alerta"] : ["Pendiente", "pendiente"];

  const docs: { nombre: string; msg: string; estado: "ok" | "error" | "espera" }[] = [
    { nombre: "Factura comercial", msg: "Recibida", estado: "ok" },
    { nombre: "Lista de empaque", msg: "Recibida", estado: "ok" },
    { nombre: "Guía de embarque (B/L)", msg: "Recibida", estado: "ok" },
    corregido
      ? { nombre: "Contenedor CSQU 305438 3", msg: "Dígito verificador válido", estado: "ok" }
      : { nombre: "Contenedor CSQU 305438 4", msg: enError ? "Dígito verificador inválido" : "Revisando…", estado: enError ? "error" : "espera" },
  ];

  const registro = [
    { n: "1", t: "Depósito · 1.000 USDC", h: hashes.deposito, visible: sube(fB + 50, 14) },
    { n: "2", t: "Liberación 30% · 300 USDC", h: hashes.liberacion30, visible: sube(fC + 46, 14) },
    { n: "3", t: "Liberación 70% · 700 USDC", h: hashes.liberacion70, visible: sube(fClic + 48, 14) },
  ];

  const pasos = ["Depósito", "Pedido confirmado", "Documentos", "Aprobación"];

  return (
    <AbsoluteFill style={{ background: `linear-gradient(135deg, ${C.marino}, ${C.marino2})` }}>
      {/* guía de pasos arriba */}
      <Txt x={WX} y={34} size={34} color={C.naranja} bold font={TITULO}>El flujo, paso por paso</Txt>
      <div style={{ position: "absolute", right: WX, top: 34, display: "flex", gap: 12 }}>
        {pasos.map((p, i) => {
          const activo = paso === i + 1;
          const hecho = paso > i + 1;
          return (
            <div key={p} style={{
              padding: "6px 16px", borderRadius: 999, fontFamily: CUERPO, fontSize: 22, fontWeight: 700, whiteSpace: "nowrap",
              background: activo ? C.naranja : "transparent", color: activo ? C.marino : hecho ? C.crema : "#8FA0BF",
              border: `2px solid ${activo ? C.naranja : "#3A4C75"}`,
            }}>{i + 1} · {p}</div>
          );
        })}
      </div>

      {/* ventana */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, opacity: entrada, transform: `translateY(${(1 - entrada) * 40}px)` }}>
        <div style={{
          position: "absolute", left: WX, top: WY, width: WW, height: WH, background: C.crema, borderRadius: 28,
          boxShadow: "0 40px 100px rgba(0,0,0,0.45)", overflow: "hidden",
        }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: WW, height: 64, background: "#EDE6DA" }} />
          {[C.alerta, "#E8B14A", C.ok].map((c, i) => (
            <div key={i} style={{ position: "absolute", left: 28 + i * 28, top: 25, width: 14, height: 14, borderRadius: 7, background: c }} />
          ))}
          <Txt x={0} y={18} w={WW} align="center" size={26} color={C.suave} bold font={TITULO}>Qhatu · Trato A-031</Txt>
          <div style={{
            position: "absolute", right: 28, top: 14, padding: "4px 18px", borderRadius: 999, border: `2px solid ${C.terra}`,
            color: C.terra, fontFamily: TITULO, fontWeight: 700, fontSize: 24,
          }}>{real ? "TESTNET" : "MAQUETA"}</div>
        </div>

        {/* columna izquierda: el trato */}
        <Panel x={BX} y={BY} w={LW} h={500}>
          <Txt x={28} y={20} size={28} color={C.terra} bold font={TITULO}>TRATO A-031</Txt>
          {[["Exportadora", "Bolivia"], ["Comprador", "EE. UU."], ["Mercadería", "Quinua, 20 t"], ["Monto", "1.000 USDC"]].map(([a, b], i) => (
            <React.Fragment key={a}>
              <Txt x={28} y={72 + i * 46} size={24} color={C.suave}>{a}</Txt>
              <Txt x={LW - 28 - 300} y={70 + i * 46} w={300} align="right" size={28} bold>{b}</Txt>
            </React.Fragment>
          ))}
          <div style={{ position: "absolute", left: 28, top: 262, width: LW - 56, height: 2, background: C.borde }} />
          <Txt x={28} y={276} size={24} color={C.terra} bold font={TITULO}>HITOS</Txt>

          <Txt x={28} y={318} size={28} bold>Pedido confirmado</Txt>
          <Txt x={28} y={354} size={24} color={C.suave}>30% · 300 USDC</Txt>
          <Chip x={LW - 28 - 150} y={346} texto={ms1[0]} tipo={ms1[1]} />

          <Txt x={28} y={400} size={28} bold>Guía de embarque</Txt>
          <Txt x={28} y={436} size={24} color={C.suave}>70% · 700 USDC</Txt>
          <Chip x={LW - 28 - 150} y={428} texto={ms2[0]} tipo={ms2[1]} />
          {corregido && !clic ? (
            <div style={{
              position: "absolute", left: LW - 28 - 130, top: 392, width: 130, height: 44, borderRadius: 12, background: C.terra,
              color: C.crema, fontFamily: CUERPO, fontWeight: 700, fontSize: 26, textAlign: "center", lineHeight: "44px",
              transform: `scale(${1 + 0.03 * Math.sin(frame / 4)})`,
            }}>Aprobar</div>
          ) : null}
        </Panel>

        <Panel x={BX} y={BY + 524} w={LW} h={140} fondo={C.crema2}>
          <Txt x={28} y={20} size={24} color={C.terra} bold font={TITULO}>EXPORTADORA RECIBE</Txt>
          <Txt x={28} y={58} size={62} color={C.ok} bold font={TITULO}>{miles(recibido)} <span style={{ fontSize: 30 }}>USDC</span></Txt>
        </Panel>

        {/* columna derecha: escrow, documentos y registro */}
        <Panel x={RX} y={BY} w={RW} h={246}>
          <Txt x={28} y={20} size={24} color={C.terra} bold font={TITULO}>ESCROW EN STELLAR · NO CUSTODIAL</Txt>
          <Txt x={28} y={52} size={72} bold font={TITULO}>{miles(enEscrow)} <span style={{ fontSize: 34, color: C.suave }}>USDC</span></Txt>
          <div style={{ position: "absolute", left: 28, top: 168 - 0, width: BARRA_W, height: 30, borderRadius: 15, background: C.borde, overflow: "hidden" }}>
            <div style={{ position: "absolute", left: 0, top: 0, width: BARRA_W * pDep, height: 30, background: C.terra }} />
            <div style={{ position: "absolute", left: 0, top: 0, width: BARRA_W * 0.3 * p30, height: 30, background: C.ok }} />
            <div style={{ position: "absolute", left: BARRA_W * 0.3, top: 0, width: BARRA_W * 0.7 * p70, height: 30, background: C.ok }} />
            <div style={{ position: "absolute", left: BARRA_W * 0.3 - 2, top: 0, width: 4, height: 30, background: C.crema2 }} />
          </div>
          <Txt x={28} y={204} size={24} color={C.suave}>30% · pedido confirmado</Txt>
          <Txt x={28 + BARRA_W * 0.3 + 14} y={204} size={24} color={C.suave}>70% · guía de embarque verificada</Txt>
        </Panel>

        <Panel x={RX} y={BY + 270} w={RW} h={286}>
          <Txt x={28} y={18} size={24} color={C.terra} bold font={TITULO}>DOCUMENTOS</Txt>
          {docs.map((d, i) => {
            const col = d.estado === "ok" ? C.ok : d.estado === "error" ? C.alerta : "#B8AE9B";
            return (
              <div key={i} style={{ opacity: filaDoc[i], transform: `translateY(${(1 - filaDoc[i]) * 12}px)` }}>
                <div style={{
                  position: "absolute", left: 28, top: 62 + i * 54, width: 38, height: 38, borderRadius: 19, background: col, color: C.crema,
                  fontFamily: CUERPO, fontWeight: 700, fontSize: 26, textAlign: "center", lineHeight: "38px",
                }}>{d.estado === "ok" ? "✓" : d.estado === "error" ? "✗" : "…"}</div>
                <Txt x={84} y={62 + i * 54 + 2} size={28} bold>{d.nombre}</Txt>
                <Txt x={RW - 28 - 400} y={62 + i * 54 + 4} w={400} align="right" size={26} color={d.estado === "error" ? C.alerta : C.suave} bold={d.estado === "error"}>{d.msg}</Txt>
              </div>
            );
          })}
        </Panel>

        <Panel x={RX} y={BY + 580} w={RW} h={152} fondo={C.crema2}>
          <Txt x={28} y={14} size={24} color={C.terra} bold font={TITULO}>REGISTRO EN STELLAR</Txt>
          {registro.map((r, i) => (
            <div key={r.n} style={{ opacity: r.visible }}>
              <Txt x={28} y={46 + i * 32} size={24} bold>{r.n} · {r.t}</Txt>
              <Txt x={RW - 28 - 420} y={46 + i * 32} w={420} align="right" size={24} font={MONO} color={r.h ? C.ok : C.suave}>
                {r.h ? corto(r.h) : "pendiente de testnet"}
              </Txt>
            </div>
          ))}
        </Panel>

        {moneda(p30, BARRA_X + BARRA_W * 0.15)}
        {moneda(p70, BARRA_X + BARRA_W * 0.65)}
        {cursor}
      </div>
    </AbsoluteFill>
  );
};
