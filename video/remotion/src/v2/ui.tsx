import React from 'react';
import {AbsoluteFill, Audio, Easing, Freeze, Img, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, FPS, shots, type Laid, type Rect, type ShotName} from './theme';

export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const ramp = (f: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(f, [a, b], [from, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});

export type Theme = 'dark' | 'light';
export const ink = (t: Theme) => (t === 'dark' ? C.paper : C.ink);
export const ink2 = (t: Theme) => (t === 'dark' ? '#A9B7B2' : C.ink2);
export const accent = (t: Theme) => (t === 'dark' ? C.emeraldBright : C.emerald);

const rnd = (i: number, k: number) => {
  const x = Math.sin(i * 127.1 + k * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** Seeded vesicles drifting slowly upward: deterministic per frame, low opacity so text always wins. */
export const VesicleDrift: React.FC<{n?: number; seed?: number; theme: Theme}> = ({n = 30, seed = 1, theme}) => {
  const f = useCurrentFrame();
  const tint = theme === 'dark' ? C.emeraldBright : C.emerald;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      {Array.from({length: n}, (_, i) => {
        const r = 4 + rnd(i, seed) * 16;
        const speed = 0.18 + rnd(i, seed + 1) * 0.4;
        const x = rnd(i, seed + 2) * 1920 + Math.sin(f / (50 + rnd(i, seed + 4) * 60) + i) * 26;
        const y = (((rnd(i, seed + 3) * 1080 - f * speed) % 1080) + 1080) % 1080;
        const a = (theme === 'dark' ? 0.10 : 0.09) + rnd(i, seed + 5) * 0.12;
        return (
          <g key={i} opacity={a}>
            <circle cx={x} cy={y} r={r} fill="none" stroke={tint} strokeWidth={2} />
            <circle cx={x} cy={y} r={r * 0.45} fill={tint} opacity={0.5} />
          </g>
        );
      })}
    </svg>
  );
};

export const SceneSeed = React.createContext(1);

/** Scene ground (obsidian or warm lab paper) with drifting vesicles and a slow camera drift. */
export const Stage: React.FC<{theme: Theme; children?: React.ReactNode; drift?: number}> = ({theme, children, drift = 0.02}) => {
  const f = useCurrentFrame();
  const seed = React.useContext(SceneSeed);
  const k = 1 + drift * Math.min(1, f / 600);
  return (
    <AbsoluteFill style={{background: theme === 'dark' ? C.obsidian : C.paper, fontFamily: F.sans, color: ink(theme)}}>
      <VesicleDrift seed={seed * 7} theme={theme} />
      <AbsoluteFill style={{transform: `scale(${k})`, transformOrigin: '50% 45%'}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Root-level slide wipe at every scene change, with a soft whoosh (short Sequence at each boundary). */
const WIPE_H = 9;
export const SlideWipes: React.FC<{scenes: Laid[]}> = ({scenes}) => {
  const f = useCurrentFrame();
  const cuts = scenes.slice(1);
  const active = cuts.find((s) => f >= s.at - WIPE_H && f < s.at + WIPE_H);
  const t = active ? (f - (active.at - WIPE_H)) / (2 * WIPE_H) : 0;
  const e = Easing.inOut(Easing.cubic)(t);
  const x = 1920 - e * (1920 + 2200);
  const dark = active?.theme === 'dark';
  return (
    <>
      {cuts.map((s) => (
        <Sequence key={s.id} from={Math.max(0, s.at - WIPE_H)} durationInFrames={2 * WIPE_H + 6} layout="none">
          <Audio src={staticFile('v2/sfx/wipe_soft.mp3')} volume={0.07} />
        </Sequence>
      ))}
      {active ? (
        <div style={{position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none'}}>
          <div style={{position: 'absolute', top: 0, bottom: 0, left: x, width: 2000, background: dark ? C.obsidian2 : C.paper2}}>
            <div style={{position: 'absolute', top: 0, bottom: 0, left: 0, width: 14, background: dark ? C.emeraldBright : C.emerald}} />
          </div>
        </div>
      ) : null}
    </>
  );
};

/** Scene title: top-left, at most 5 words, arrives with a short rise. */
export const Title: React.FC<{text: string; theme: Theme; at?: number; sub?: React.ReactNode; x?: number; y?: number}> = ({
  text, theme, at = 0, sub, x = 120, y = 70,
}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, at + 10);
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o}}>
      <div style={{fontSize: 64, fontWeight: 800, letterSpacing: -1.5, lineHeight: 1.05, color: ink(theme)}}>
        {text.split(' ').map((w, i) => {
          const wo = ramp(f, at + i * 3, at + i * 3 + 10);
          return <span key={i} style={{display: 'inline-block', marginRight: '0.26em', opacity: wo, transform: `translateY(${(1 - wo) * 24}px)`}}>{w}</span>;
        })}
      </div>
      {sub ? <div style={{fontSize: 30, fontWeight: 500, color: ink2(theme), marginTop: 12}}>{sub}</div> : null}
    </div>
  );
};

export const Mono: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <span style={{fontFamily: F.mono, fontVariantNumeric: 'tabular-nums', ...style}}>{children}</span>
);

/**
 * A real capture of docs/index.html at 3x, placed by its css box and scaled so 1 css px = `zoom` video px.
 * Children are laid out in css px of the element (e.g. <Mark/>), so callouts follow the zoom and crop exactly.
 */
export const Shot: React.FC<{
  name: ShotName; x: number; y: number; zoom: number; opacity?: number; shadow?: boolean; theme?: Theme;
  crop?: Rect; children?: React.ReactNode;
}> = ({name, x, y, zoom, opacity = 1, shadow = true, theme = 'light', crop, children}) => {
  const m = shots[name];
  const c = crop ?? {x: 0, y: 0, w: m.cssW, h: m.cssH};
  return (
    <div style={{
      position: 'absolute', left: x, top: y, width: c.w * zoom, height: c.h * zoom, overflow: 'hidden', opacity,
      borderRadius: 14, background: C.card,
      boxShadow: shadow ? (theme === 'dark' ? '0 0 0 1px rgba(255,255,255,.08), 0 24px 70px rgba(0,0,0,.5)' : '0 1px 0 rgba(16,32,27,.06), 0 18px 50px rgba(16,32,27,.12)') : undefined,
    }}>
      <div style={{position: 'absolute', left: -c.x * zoom, top: -c.y * zoom, width: m.cssW, height: m.cssH, transform: `scale(${zoom})`, transformOrigin: '0 0'}}>
        <Img src={staticFile(`v2/shots/${name}.png`)} style={{position: 'absolute', left: 0, top: 0, width: m.cssW, height: m.cssH}} />
        {children}
      </div>
    </div>
  );
};

/** Highlight box in css px of the shot; grows in from nothing. `color` defaults to emerald. */
export const Mark: React.FC<{r: Rect; at: number; color?: string; pad?: number; label?: string}> = ({r, at, color = C.emeraldBright, pad = 3, label}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, at + 8);
  return (
    <div style={{
      position: 'absolute', left: r.x - pad, top: r.y - pad, width: (r.w + pad * 2) * o, height: r.h + pad * 2, opacity: o,
      border: `2px solid ${color}`, borderRadius: 4, background: `${color}22`, boxSizing: 'border-box', pointerEvents: 'none',
    }}>
      {label ? <div style={{position: 'absolute', left: 0, top: r.h + pad * 2 + 2, fontFamily: F.mono, fontSize: 13, fontWeight: 700, color, whiteSpace: 'nowrap'}}>{label}</div> : null}
    </div>
  );
};

/** Burned captions from the normalized script text, timed by the voice alignment. Root level. */
export const Captions: React.FC<{scenes: Laid[]}> = ({scenes}) => {
  const f = useCurrentFrame();
  let text = '';
  let dark = false;
  for (const s of scenes) {
    if (f < s.at || f >= s.at + s.frames) continue;
    dark = s.theme === 'dark';
    const t = (f - s.at) / FPS;
    const c = s.captions.find((x, i) => t >= x.start - 0.05 && t < (s.captions[i + 1]?.start ?? x.end + 0.6) - 0.05);
    text = c && t < c.end + 0.6 ? c.text : '';
  }
  if (!text) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 34, display: 'flex', justifyContent: 'center'}}>
      <div style={{
        fontFamily: F.sans, fontSize: 36, fontWeight: 600, color: dark ? C.paper : C.ink,
        background: dark ? 'rgba(11,18,21,.86)' : 'rgba(255,255,255,.92)', padding: '10px 26px', borderRadius: 12,
        border: `1px solid ${dark ? C.obsidianRule : C.rule}`, maxWidth: 1500, textAlign: 'center',
      }}>{text}</div>
    </div>
  );
};

export const Progress: React.FC<{total: number}> = ({total}) => {
  const f = useCurrentFrame();
  return <div style={{position: 'absolute', left: 0, bottom: 0, height: 6, width: `${(f / total) * 100}%`, background: C.emeraldBright}} />;
};

/** Spring-eased counter that lands exactly on `to` at frame b (no overshoot: damping 200). */
export const Count: React.FC<{to: number; a: number; b: number; decimals?: number}> = ({to, a, b, decimals = 0}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (f >= b) return <>{to.toFixed(decimals)}</>;
  const p = spring({frame: Math.max(0, f - a), fps, durationInFrames: Math.max(1, b - a), config: {damping: 200}});
  const v = f < a ? 0 : to * p;
  return <>{(decimals ? v : Math.round(v)).toFixed(decimals)}</>;
};

export const BROLL_LABEL = 'AI-generated b-roll · Google Flow — illustrative only';

/** Google Flow b-roll: full-frame, muted, always labelled. Fade it out from the parent via `opacity`. */
export const Broll: React.FC<{src: string; opacity?: number; theme: Theme; scrim?: 'left' | 'center' | 'none'}> = ({src, opacity = 1, theme, scrim = 'none'}) => {
  if (opacity <= 0) return null;
  const bg = theme === 'dark' ? '11,18,21' : '246,244,238';
  return (
    <AbsoluteFill style={{opacity}}>
      <OffthreadVideo src={staticFile(src)} muted style={{width: 1920, height: 1080, objectFit: 'cover'}} />
      {scrim === 'left' ? <AbsoluteFill style={{background: `linear-gradient(90deg, rgba(${bg},.92) 0%, rgba(${bg},.7) 45%, rgba(${bg},0) 80%)`}} /> : null}
      {scrim === 'center' ? <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 50%, rgba(${bg},.82) 0%, rgba(${bg},.5) 60%, rgba(${bg},.2) 100%)`}} /> : null}
      <div style={{
        position: 'absolute', right: 36, top: 30, fontFamily: F.sans, fontSize: 24, fontWeight: 600, color: ink2(theme),
        background: `rgba(${bg},.88)`, padding: '6px 16px', borderRadius: 10,
      }}>{BROLL_LABEL}</div>
    </AbsoluteFill>
  );
};

/**
 * A short real clip (the live Mol* rotation) that starts at `start`, never runs past its last frame, and
 * freezes on the frame reached at `freezeAt`. Both are scene-local frames.
 */
export const Clip: React.FC<{src: string; frames: number; start?: number; freezeAt?: number; style?: React.CSSProperties}> = ({
  src, frames, start = 0, freezeAt = Infinity, style,
}) => {
  const f = useCurrentFrame();
  const t = Math.max(0, Math.min(f, freezeAt) - start);
  return (
    <Freeze frame={Math.min(t, frames - 1)}>
      <OffthreadVideo src={staticFile(src)} muted style={style} />
    </Freeze>
  );
};

/** Pop-in tag/badge. */
export const Badge: React.FC<{at: number; color: string; children: React.ReactNode; fg?: string; style?: React.CSSProperties}> = ({at, color, children, fg = '#fff', style}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, at + 10);
  return (
    <div style={{
      display: 'inline-block', opacity: o, transform: `translateY(${(1 - o) * 12}px)`, background: color, color: fg,
      fontWeight: 700, borderRadius: 10, padding: '8px 18px', ...style,
    }}>{children}</div>
  );
};
