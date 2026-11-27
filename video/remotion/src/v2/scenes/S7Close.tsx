import React from 'react';
import {Audio, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, D, F, cue, scene} from '../theme';
import {Count, Mono, Stage, Title, ramp} from '../ui';

const s = scene('s7');
const N = D.counts;

const Cell: React.FC<{at: number; end: number; to: number; label: string; color: string; suffix?: string}> = ({at, end, to, label, color, suffix = ''}) => {
  const f = useCurrentFrame();
  return (
    <div style={{flex: 1, textAlign: 'center', opacity: 0.2 + 0.8 * ramp(f, at - 6, at + 4)}}>
      <Mono style={{fontSize: 104, fontWeight: 700, letterSpacing: -3, lineHeight: 1, color}}>
        <Count to={to} a={at} b={end} />{suffix}
      </Mono>
      <div style={{fontSize: 28, color: '#A9B7B2', marginTop: 8}}>{label}</div>
    </div>
  );
};

const Lock: React.FC<{p: number}> = ({p}) => (
  <svg width={64} height={78} viewBox="0 0 64 78">
    <path d={`M16 34 V22 a16 16 0 0 1 32 0 V${34 - (1 - p) * 12}`} fill="none" stroke={C.emeraldBright} strokeWidth={7} strokeLinecap="round" />
    <rect x={8} y={34} width={48} height={38} rx={8} fill={C.emeraldBright} />
    <circle cx={32} cy={52} r={5} fill={C.obsidian} />
  </svg>
);

export const S7Close: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tOpen = cue(s, 'Open');
  const t3d = cue(s, '3D');
  const lockAt = t3d + 14;
  const lockP = f < lockAt ? 0 : spring({frame: f - lockAt, fps, config: {damping: 18, stiffness: 160}});
  const cardGlow = ramp(f, lockAt, lockAt + 12);
  return (
    <Stage theme="dark" drift={0.01}>
      <Title theme="dark" text="Inspect every quote live" />
      <Sequence from={lockAt} layout="none"><Audio src={staticFile('v2/sfx/lock_click.mp3')} volume={0.1} /></Sequence>
      <div style={{position: 'absolute', left: 110, top: 250, width: 1700, padding: '56px 40px 48px', borderRadius: 24,
        background: C.obsidian2, border: `2px solid ${cardGlow > 0.5 ? C.emeraldBright : C.obsidianRule}`,
        boxShadow: `0 0 ${60 * cardGlow}px rgba(16,185,129,${0.25 * cardGlow}), 0 30px 80px rgba(0,0,0,.5)`}}>
        <div style={{display: 'flex'}}>
          <Cell at={cue(s, '28')} end={cue(s, '28') + 20} to={N.uniquePapers} label="papers" color={C.paper} />
          <Cell at={cue(s, '120')} end={cue(s, '120') + 24} to={N.findings} label="findings" color={C.paper} />
          <Cell at={cue(s, '29')} end={cue(s, '29') + 20} to={N.contradicting} label="contradictions" color={C.amber} />
          <Cell at={cue(s, '74')} end={cue(s, '74') + 20} to={N.tests} label="checks" color={C.emeraldBright} />
        </div>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18, marginTop: 40, opacity: cardGlow}}>
          <Lock p={lockP} />
          <Mono style={{fontSize: 28, color: C.emeraldBright, letterSpacing: 3, fontWeight: 700}}>FROZEN · EVERY NUMBER SOURCED</Mono>
        </div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 740, textAlign: 'center', opacity: ramp(f, tOpen, tOpen + 14)}}>
        <Mono style={{fontSize: 44, fontWeight: 700, color: C.paper}}>{D.urls.site}</Mono>
        <div style={{height: 14}} />
        <Mono style={{fontSize: 30, color: '#A9B7B2'}}>{D.urls.repo}</Mono>
      </div>
      <div style={{position: 'absolute', right: 110, top: 100, fontFamily: F.sans, fontSize: 26, color: '#A9B7B2', opacity: ramp(f, tOpen, tOpen + 14)}}>Team Khepri</div>
    </Stage>
  );
};
