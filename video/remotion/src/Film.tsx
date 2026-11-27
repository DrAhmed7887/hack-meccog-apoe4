import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  Loop,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import timeline from "./timeline.json";

type CaptionCue = { text: string; start: number; end: number };
type SceneMeta = {
  id: string;
  theme: string;
  title: string;
  caption: string;
  from: number;
  durationInFrames: number;
  audioSec: number;
  captions: CaptionCue[];
};

const BG_DARK = "#0B1215";
const BG_LIGHT = "#F6F4EE";
const INK_DARK = "#121B18";
const INK_LIGHT = "#F6F4EE";
const ACCENT = "#0D8A6F";
const AMBER = "#F59E0B";
const CONTRA = "#EA580C";

const CaptionBar: React.FC<{ captions: CaptionCue[]; theme: string }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;
  const active =
    captions.find((c) => sec >= c.start - 0.05 && sec <= c.end + 0.35) || captions[captions.length - 1];
  if (!active) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: 120,
        right: 120,
        bottom: 42,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          background: "rgba(11, 18, 21, 0.88)",
          color: "#F6F4EE",
          padding: "14px 28px",
          borderRadius: 10,
          border: "1px solid rgba(255,255,255,0.14)",
          fontFamily: "Inter, -apple-system, sans-serif",
          fontSize: 32,
          fontWeight: 600,
          lineHeight: 1.32,
          textAlign: "center",
          maxWidth: 1480,
          boxShadow: "0 12px 32px rgba(0,0,0,0.35)",
        }}
      >
        {active.text}
      </div>
    </div>
  );
};

const SceneHeader: React.FC<{ title: string; tag: string; theme: string }> = ({ title, tag, theme }) => {
  const frame = useCurrentFrame();
  const isDark = theme === "dark";
  const op = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  const ty = interpolate(frame, [0, 18], [16, 0], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div
      style={{
        opacity: op,
        transform: `translateY(${ty}px)`,
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <span
        style={{
          fontFamily: "Inter, sans-serif",
          fontSize: 20,
          fontWeight: 700,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: isDark ? "#5EEAD4" : ACCENT,
        }}
      >
        {tag}
      </span>
      <h2
        style={{
          margin: 0,
          fontFamily: "Georgia, serif",
          fontSize: 54,
          lineHeight: 1.1,
          color: isDark ? INK_LIGHT : INK_DARK,
        }}
      >
        {title}
      </h2>
    </div>
  );
};

const SceneS1: React.FC<{ s: SceneMeta }> = ({ s }) => {
  const frame = useCurrentFrame();
  const fade = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: BG_DARK }}>
      <AbsoluteFill style={{ opacity: 0.72 }}>
        <Loop durationInFrames={360}>
          <OffthreadVideo
            src={staticFile("clips/shot1_apoe_fold.mp4")}
            muted
            playbackRate={0.33}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </Loop>
      </AbsoluteFill>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(90deg, rgba(11,18,21,0.92) 0%, rgba(11,18,21,0.58) 56%, rgba(11,18,21,0.22) 100%)",
        }}
      />
      <div
        style={{
          position: "relative",
          padding: "76px 96px",
          width: 1020,
          display: "flex",
          flexDirection: "column",
          gap: 28,
          opacity: fade,
        }}
      >
        <SceneHeader tag="MecCog APOE4 Challenge" title={s.title} theme="dark" />
        <div
          style={{
            display: "flex",
            gap: 24,
            marginTop: 12,
          }}
        >
          <div style={{ background: "rgba(18,27,24,0.86)", border: "1px solid rgba(94,234,212,0.35)", borderRadius: 12, padding: "22px 28px", minWidth: 260 }}>
            <div style={{ fontSize: 48, fontWeight: 800, color: AMBER, fontFamily: "Inter, sans-serif" }}>Cys112Arg</div>
            <div style={{ fontSize: 24, color: "#CBD5E1", marginTop: 6 }}>Single residue risk variant</div>
          </div>
          <div style={{ background: "rgba(18,27,24,0.86)", border: "1px solid rgba(255,255,255,0.18)", borderRadius: 12, padding: "22px 28px", minWidth: 260 }}>
            <div style={{ fontSize: 48, fontWeight: 800, color: INK_LIGHT, fontFamily: "Inter, sans-serif" }}>38 Agents</div>
            <div style={{ fontSize: 24, color: "#CBD5E1", marginTop: 6 }}>Prior Step 1 extraction bottleneck</div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneS2: React.FC<{ s: SceneMeta }> = ({ s }) => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, s.durationInFrames], [1.0, 1.07], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: BG_LIGHT, padding: "56px 72px" }}>
      <SceneHeader tag="Rule C5 Architecture" title={s.title} theme="light" />
      <div style={{ display: "flex", gap: 36, marginTop: 34, alignItems: "center", flex: 1 }}>
        <div
          style={{
            flex: 1.55,
            borderRadius: 14,
            overflow: "hidden",
            border: "2px solid #D7D1C3",
            boxShadow: "0 20px 50px rgba(18,27,24,0.12)",
            background: "#FFF",
          }}
        >
          <Img
            src={staticFile("screens/ui_overview.png")}
            style={{ width: "100%", height: "auto", display: "block", transform: `scale(${zoom})`, transformOrigin: "50% 42%" }}
          />
        </div>
        <div style={{ flex: 0.75, display: "flex", flexDirection: "column", gap: 20, marginBottom: 48 }}>
          {[
            { k: "Step 1 Sheets Only", v: "Verbatim primary quotes, panel IDs, and printed_in_text statistics (Rule C5)" },
            { k: "Zero In-Sheet AI Models", v: "3D PDB & AlphaFold v6 models live strictly in the companion Mol* workbench" },
            { k: "Reproducible Git Gate", v: "Pinned PRs, CI validation, and two-channel adversarial scientific review" },
          ].map((c, idx) => (
            <div
              key={c.k}
              style={{
                background: "#FFFFFF",
                border: "1px solid #D7D1C3",
                borderLeft: `6px solid ${idx === 0 ? ACCENT : "#334E46"}`,
                borderRadius: 10,
                padding: "20px 24px",
              }}
            >
              <div style={{ fontSize: 26, fontWeight: 700, color: INK_DARK }}>{c.k}</div>
              <div style={{ fontSize: 22, color: "#4B5A55", marginTop: 6, lineHeight: 1.35 }}>{c.v}</div>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneS3: React.FC<{ s: SceneMeta }> = ({ s }) => {
  const frame = useCurrentFrame();
  const slide = interpolate(frame, [10, 35], [24, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: BG_DARK, padding: "56px 72px" }}>
      <SceneHeader tag="PDB 1B68 vs 1NFN" title={s.title} theme="dark" />
      <div style={{ display: "flex", gap: 36, marginTop: 34, flex: 1, alignItems: "center", marginBottom: 44 }}>
        <div style={{ position: "relative", flex: 1.35, height: 670, borderRadius: 14, overflow: "hidden", border: "1px solid rgba(255,255,255,0.16)" }}>
          <Loop layout="none" durationInFrames={360}>
            <OffthreadVideo
              src={staticFile("clips/shot1_apoe_fold.mp4")}
              muted
              playbackRate={0.33}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </Loop>
        </div>
        <div style={{ flex: 0.85, display: "flex", flexDirection: "column", gap: 20, transform: `translateY(${slide}px)` }}>
          {[
            { label: "Arg112–Glu109 (1B68)", metric: "2.53 A", note: "ARG112.NH1 to GLU109.OE2 salt bridge" },
            { label: "Arg61–Glu109 (APOE4)", metric: "5.34 A", note: "Outward sidechain displacement in 1B68" },
            { label: "Arg61–Glu109 (APOE3)", metric: "3.53 A", note: "Compact WT helical packing in 1NFN" },
            { label: "Arg61–Glu255 (2L7B M1)", metric: "25.87 A", note: "N/C-terminal baseline distance" },
          ].map((row, idx) => (
            <div
              key={row.label}
              style={{
                background: "rgba(18,27,24,0.92)",
                border: "1px solid rgba(255,255,255,0.18)",
                borderLeft: `6px solid ${idx === 0 ? AMBER : "#5EEAD4"}`,
                borderRadius: 10,
                padding: "18px 22px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontSize: 25, fontWeight: 700, color: INK_LIGHT }}>{row.label}</div>
                <div style={{ fontSize: 20, color: "#94A3B8", marginTop: 4 }}>{row.note}</div>
              </div>
              <div style={{ fontSize: 36, fontWeight: 800, color: idx === 0 ? AMBER : "#5EEAD4", fontVariantNumeric: "tabular-nums" }}>
                {row.metric}
              </div>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneS4: React.FC<{ s: SceneMeta }> = ({ s }) => {
  const frame = useCurrentFrame();
  const dashOffset = interpolate(frame, [0, 120], [160, 0]);
  return (
    <AbsoluteFill style={{ backgroundColor: BG_LIGHT, padding: "56px 72px" }}>
      <SceneHeader tag="Convergent H2 + H5 Mechanism" title={s.title} theme="light" />
      <div style={{ marginTop: 28, display: "flex", flexDirection: "column", gap: 26, flex: 1, marginBottom: 44 }}>
        <svg viewBox="0 0 1760 150" style={{ width: "100%", height: 150 }}>
          {[
            { x: 10, t: "1. Arg112 Fold", sub: "PDB 1B68", c: "#121B18" },
            { x: 365, t: "2. Receptors (H2)", sub: "ApoER2 / LRP1 / LDLR", c: ACCENT },
            { x: 720, t: "3. Early Endosome (H2)", sub: "NHE6 9R8L / Rab5+", c: ACCENT },
            { x: 1075, t: "4. Lipid Efflux (H5)", sub: "ABCA1 5XJY / NPC1 3GKH", c: "#B45309" },
            { x: 1430, t: "5. Lysosome (H5)", sub: "pH rise & Abeta42 lag", c: CONTRA },
          ].map((b, i) => (
            <g key={b.t}>
              <rect x={b.x} y={14} width={315} height={116} rx={12} fill="#FFFFFF" stroke={b.c} strokeWidth={3} />
              <text x={b.x + 22} y={62} fontFamily="Inter, sans-serif" fontSize={26} fontWeight="700" fill={INK_DARK}>{b.t}</text>
              <text x={b.x + 22} y={100} fontFamily="Inter, sans-serif" fontSize={21} fill="#4B5A55">{b.sub}</text>
              {i < 4 && (
                <line
                  x1={b.x + 318}
                  y1={72}
                  x2={b.x + 362}
                  y2={72}
                  stroke={ACCENT}
                  strokeWidth={5}
                  strokeDasharray="10 6"
                  strokeDashoffset={dashOffset}
                />
              )}
            </g>
          ))}
        </svg>

        <div style={{ display: "flex", gap: 28, flex: 1, minHeight: 0, height: 540 }}>
          <div style={{ position: "relative", flex: 1, height: "100%", borderRadius: 14, overflow: "hidden", border: "2px solid #D7D1C3" }}>
            <Loop layout="none" durationInFrames={360}>
              <OffthreadVideo
                src={staticFile("clips/shot2_endosome_jam.mp4")}
                muted
                playbackRate={0.33}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </Loop>
          </div>
          <div style={{ flex: 1, height: "100%", borderRadius: 14, overflow: "hidden", border: "2px solid #D7D1C3", background: "#FFF" }}>
            <Img src={staticFile("screens/ui_h5_npc1.png")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "50% 62%" }} />
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneS5: React.FC<{ s: SceneMeta }> = ({ s }) => {
  const frame = useCurrentFrame();
  const cards = [
    { val: "30", title: "Primary papers", sub: "19 in H5 (10 Tier 1 iPSC) + 11 in H2" },
    { val: "120", title: "Experimental findings", sub: "67 in H5 + 53 in H2 (supports + contradicts)" },
    { val: "126", title: "Printed-in-text stats", sub: "62 in H5 + 64 in H2 (zero estimated P-values)" },
    { val: "0", title: "Retracted / Review / Errors", sub: "doi-check clean & --strict validator PASS" },
  ];
  return (
    <AbsoluteFill style={{ backgroundColor: BG_DARK, padding: "70px 88px" }}>
      <SceneHeader tag="Frozen Step 1 Evidence" title={s.title} theme="dark" />
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 28, marginTop: 46, marginBottom: 60, flex: 1 }}>
        {cards.map((c, idx) => {
          const op = interpolate(frame, [idx * 10, idx * 10 + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div
              key={c.title}
              style={{
                opacity: op,
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(94,234,212,0.28)",
                borderRadius: 14,
                padding: "32px 38px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
              }}
            >
              <div style={{ fontSize: 92, fontWeight: 800, color: idx === 3 ? "#5EEAD4" : AMBER, lineHeight: 1, fontVariantNumeric: "tabular-nums" }}>
                {c.val}
              </div>
              <div style={{ fontSize: 32, fontWeight: 700, color: INK_LIGHT, marginTop: 14 }}>{c.title}</div>
              <div style={{ fontSize: 24, color: "#CBD5E1", marginTop: 8 }}>{c.sub}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const SceneS6: React.FC<{ s: SceneMeta }> = ({ s }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: BG_LIGHT, padding: "56px 72px" }}>
      <SceneHeader tag="Adversarial Scientific Honesty" title={s.title} theme="light" />
      <div style={{ display: "flex", gap: 36, marginTop: 34, flex: 1, alignItems: "center", marginBottom: 48 }}>
        <div style={{ flex: 1.35, borderRadius: 14, overflow: "hidden", border: "2px solid #D7D1C3", background: "#FFF" }}>
          <Img src={staticFile("screens/ui_h2_contra.png")} style={{ width: "100%", height: "auto", display: "block", objectPosition: "50% 70%" }} />
        </div>
        <div style={{ flex: 0.9, display: "flex", flexDirection: "column", gap: 20 }}>
          {[
            { k: "29 Contradicting Findings", v: "14 in H5 + 15 in H2 explicitly marked CONTRADICTING:, never hidden." },
            { k: "NHE6 Lineage Divergence", v: "Ablation rescues neuronal ApoER2 in vivo (30089905) yet fails in APOE4 astrocytes (40504691)." },
            { k: "Tier & Full-Text Limits", v: "H2 is 100% Tier 2 non-human/cell models; 4 gated/paywalled papers kept abstract-only." },
          ].map((item) => (
            <div
              key={item.k}
              style={{
                background: "#FFFFFF",
                border: "1px solid #D7D1C3",
                borderLeft: `6px solid ${CONTRA}`,
                borderRadius: 10,
                padding: "22px 26px",
              }}
            >
              <div style={{ fontSize: 27, fontWeight: 700, color: CONTRA }}>{item.k}</div>
              <div style={{ fontSize: 22, color: INK_DARK, marginTop: 6, lineHeight: 1.35 }}>{item.v}</div>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const SceneS7: React.FC<{ s: SceneMeta }> = ({ s }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: BG_DARK, padding: "86px 96px", justifyContent: "space-between" }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
        <SceneHeader tag="Team Khepri · Open Evidence" title={s.title} theme="dark" />
        <div style={{ display: "flex", gap: 24, marginTop: 18 }}>
          {[
            { k: "30", v: "Verified papers (H5 + H2)" },
            { k: "120", v: "Step 1 findings (29 contradicting)" },
            { k: "14", v: "Staged PDB & AlphaFold 3D models" },
          ].map((x) => (
            <div key={x.k} style={{ flex: 1, background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.16)", borderRadius: 12, padding: "26px 30px" }}>
              <div style={{ fontSize: 58, fontWeight: 800, color: AMBER }}>{x.k}</div>
              <div style={{ fontSize: 24, color: "#CBD5E1", marginTop: 8 }}>{x.v}</div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 22, background: "rgba(13,138,111,0.18)", border: "1px solid #5EEAD4", borderRadius: 12, padding: "28px 34px" }}>
          <div style={{ fontSize: 22, color: "#5EEAD4", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Live Interactive Workbench &amp; Code
          </div>
          <div style={{ fontSize: 38, fontWeight: 700, color: INK_LIGHT, marginTop: 8 }}>
            drahmed7887.github.io/hack-meccog-apoe4
          </div>
          <div style={{ fontSize: 26, color: "#CBD5E1", marginTop: 6 }}>
            github.com/DrAhmed7887/hack-meccog-apoe4
          </div>
        </div>
      </div>
      <div style={{ height: 60 }} />
    </AbsoluteFill>
  );
};

const SCENE_MAP: Record<string, React.FC<{ s: SceneMeta }>> = {
  s1: SceneS1,
  s2: SceneS2,
  s3: SceneS3,
  s4: SceneS4,
  s5: SceneS5,
  s6: SceneS6,
  s7: SceneS7,
};

export const Film: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = Math.min(1, Math.max(0, frame / Math.max(1, durationInFrames - 1)));

  return (
    <AbsoluteFill style={{ backgroundColor: BG_DARK }}>
      {timeline.scenes.map((s) => {
        const Comp = SCENE_MAP[s.id] || SceneS1;
        return (
          <Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}>
            <Audio src={staticFile(`vo/${s.id}.mp3`)} />
            <Comp s={s} />
            <CaptionBar captions={s.captions} theme={s.theme} />
          </Sequence>
        );
      })}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: 6,
          background: "rgba(255,255,255,0.15)",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${(progress * 100).toFixed(2)}%`,
            background: ACCENT,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
