import React from 'react';
import {interpolate, useCurrentFrame, Easing} from 'remotion';
import {C, D, F, cue, scene} from '../theme';
import {Count, Mono, Stage, Title, ramp} from '../ui';

const s = scene('s5');
const N = D.counts;
const COLS = 15; // 15 x 8 = 120 findings
const PITCH = 56;
const GX = 985;
const GY = 330;

/** 120 dots, row by row: the first `sup` fill emerald, the rest burnt orange (contradicting). */
const Grid: React.FC<{appear: number; supFilled: number; conFilled: number}> = ({appear, supFilled, conFilled}) => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
    {Array.from({length: N.findings}, (_, i) => {
      const col = i % COLS;
      const row = Math.floor(i / COLS);
      const isSup = i < N.supporting;
      const on = isSup ? i < supFilled : i - N.supporting < conFilled;
      const color = isSup ? C.emeraldBright : C.burnt;
      return (
        <circle key={i} cx={GX + col * PITCH + PITCH / 2} cy={GY + row * PITCH + PITCH / 2} r={on ? 19 : 17}
          fill={on ? color : 'none'} stroke={on ? color : C.obsidianRule} strokeWidth={on ? 0 : 2.5}
          opacity={appear > (col + row) / (COLS + 8) ? 1 : 0} />
      );
    })}
  </svg>
);

const Big: React.FC<{y: number; at: number; end: number; to: number; label: string; suffix?: React.ReactNode}> = ({y, at, end, to, label, suffix}) => {
  const f = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: 120, top: y, opacity: 0.25 + 0.75 * ramp(f, at - 6, at + 4)}}>
      <Mono style={{fontSize: 132, fontWeight: 700, letterSpacing: -4, lineHeight: 1, color: C.paper}}>
        <Count to={to} a={at} b={end} />
        {suffix}
      </Mono>
      <div style={{fontSize: 28, color: '#A9B7B2', marginTop: 2}}>{label}</div>
    </div>
  );
};

export const S5Proof: React.FC = () => {
  const f = useCurrentFrame();
  const t120 = cue(s, '120');
  const t91 = cue(s, '91');
  const t29 = cue(s, '29');
  const fill = (a: number, to: number) =>
    Math.round(interpolate(f, [a, a + 26], [0, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)}));
  const t0a = cue(s, '0 retracted');
  const t0b = cue(s, '0 validator');
  return (
    <Stage theme="dark">
      <Title theme="dark" text="28 papers, 0 invented stats" />
      <Big y={210} at={cue(s, '28')} end={cue(s, '28') + 22} to={N.uniquePapers} label={`unique papers · ${N.entries} entries`} />
      <Big y={420} at={t120} end={t120 + 26} to={N.findings} label="findings, each with its verbatim quote" />
      <Big y={630} at={cue(s, '126')} end={cue(s, '126') + 24} to={N.printedStats} label="printed-in-text statistics" />
      <div style={{position: 'absolute', left: 120, top: 840, opacity: 0.25 + 0.75 * ramp(f, t0a - 6, t0a + 4)}}>
        <Mono style={{fontSize: 96, fontWeight: 700, letterSpacing: -3, color: C.paper}}>
          <Count to={0} a={t0a} b={t0a + 1} /> / <Count to={0} a={t0b} b={t0b + 1} />
        </Mono>
        <span style={{fontSize: 26, color: '#A9B7B2', marginLeft: 22}}>retracted or review · validator errors</span>
      </div>
      <Grid appear={ramp(f, t120 - 4, t120 + 28)} supFilled={fill(t91 - 2, N.supporting)} conFilled={fill(t29 - 2, N.contradicting)} />
      <div style={{position: 'absolute', left: GX, top: 215, display: 'flex', gap: 56}}>
        <div style={{opacity: ramp(f, t91 - 6, t91 + 4)}}>
          <Mono style={{fontSize: 76, fontWeight: 700, color: C.emeraldBright, lineHeight: 1}}><Count to={N.supporting} a={t91 - 2} b={t91 + 24} /></Mono>
          <div style={{fontSize: 26, color: '#A9B7B2'}}>supporting</div>
        </div>
        <div style={{opacity: ramp(f, t29 - 6, t29 + 4)}}>
          <Mono style={{fontSize: 76, fontWeight: 700, color: C.burnt, lineHeight: 1}}><Count to={N.contradicting} a={t29 - 2} b={t29 + 24} /></Mono>
          <div style={{fontSize: 26, color: '#A9B7B2'}}>contradicting</div>
        </div>
      </div>
      <Mono style={{position: 'absolute', left: GX, top: GY + 8 * PITCH + 24, fontSize: 22, color: '#A9B7B2', opacity: ramp(f, t29 + 20, t29 + 34)}}>
        H5 {D.counts.H5.n_findings} + H2 {D.counts.H2.n_findings} = {N.findings} findings · {D.counts.H5.n_contradicting} + {D.counts.H2.n_contradicting} contradicting
      </Mono>
    </Stage>
  );
};
