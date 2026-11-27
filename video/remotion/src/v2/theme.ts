import {staticFile} from 'remotion';
import data from './data.json';
import shotsJson from '../../public/v2/shots/shots.json';

export const D = data;
export const FPS = data.fps;
export const shots = shotsJson;

export const C = {
  obsidian: '#0B1215',
  obsidian2: '#121D22',
  obsidianRule: '#22343B',
  paper: '#F6F4EE',
  paper2: '#EDEAE1',
  card: '#FFFFFF',
  ink: '#10201B',
  ink2: '#4A544F',
  mute: '#8A8F86',
  rule: '#D8D3C6',
  emerald: '#0D8A6F', // on paper
  emeraldBright: '#10B981', // on obsidian
  teal: '#0B5F54', // refusal stamps
  amber: '#F59E0B',
  /** Burnt orange: reserved for contradicting items (S5Proof dots, S6Contra) and nothing else. */
  burnt: '#EA580C',
};

export const F = {
  sans: "'InterV2', Inter, system-ui, sans-serif",
  mono: "'JBMonoV2', 'JetBrains Mono', ui-monospace, monospace",
};

export const fontCss = `
@font-face { font-family: 'InterV2'; src: url('${staticFile('v2/fonts/Inter-var.woff2')}') format('woff2'); font-weight: 100 900; font-display: block; }
@font-face { font-family: 'JBMonoV2'; src: url('${staticFile('v2/fonts/JetBrainsMono-var.woff2')}') format('woff2'); font-weight: 100 800; font-display: block; }
`;

export type Scene = (typeof data.scenes)[number];
/** A scene placed on a timeline: `at` is its first frame in the composition that shows it. */
export type Laid = Scene & {at: number};

export const scene = (id: string): Scene => {
  const s = data.scenes.find((x) => x.id === id);
  if (!s) throw new Error('no scene ' + id);
  return s;
};

/** Re-base the chosen scenes (default: all) back to back. Used by the film and by the derived teaser. */
export const layout = (ids?: readonly string[]): {scenes: Laid[]; total: number} => {
  let at = 0;
  const scenes = data.scenes
    .filter((s) => !ids || ids.includes(s.id))
    .map((s) => {
      const laid = {...s, at};
      at += s.frames;
      return laid;
    });
  return {scenes, total: at};
};

export const TEASER_IDS = ['s1', 's3', 's5', 's7'] as const;
export const FILM_FRAMES = layout().total;
export const TEASER_FRAMES = layout(TEASER_IDS).total;

const strip = (w: string) => w.toLowerCase().replace(/[,.;:?!]+$/, '');

/**
 * Frame (inside a scene) at which the n-th spoken occurrence of `word` starts. `word` is the normalized
 * token ("2.53 Å", "Arg112", "0 Tier 1"); a bare "2.53" also matches the merged token "2.53 Å".
 */
export const cue = (s: Scene, word: string, nth = 0, offset = 0): number => {
  const target = word.toLowerCase();
  const hits = s.words.filter((w) => {
    const t = strip(w.w);
    return t === target || t.startsWith(target + ' ') || t.replace(/'s$/, '') === target;
  });
  if (!hits[nth]) throw new Error(`cue '${word}'#${nth} not in ${s.id}`);
  return Math.round((hits[nth].start + offset) * FPS);
};

export type ShotName = keyof typeof shotsJson;
export type Rect = {x: number; y: number; w: number; h: number};
/** Callout rect (css px, relative to the shot) recorded by capture.mjs. */
export const rectOf = (name: ShotName, key: string): Rect => {
  const r = (shotsJson[name] as {rects?: Record<string, Rect | null>}).rects?.[key];
  if (!r) throw new Error(`no rect '${key}' in shot ${name}`);
  return r;
};
