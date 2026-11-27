import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, F, cue, scene} from '../theme';
import {Broll, Mono, Shot, Stage, Title, ramp} from '../ui';

const s = scene('s2');

const Stamp: React.FC<{at: number; x: number; y: number; rot: number; children: React.ReactNode; sub: string}> = ({at, x, y, rot, children, sub}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = f < at ? 0 : spring({frame: f - at, fps, config: {damping: 14, stiffness: 190}});
  return (
    <div style={{
      position: 'absolute', left: x, top: y, width: 800, opacity: Math.min(1, p * 2), transform: `rotate(${rot}deg) scale(${0.7 + 0.3 * p})`,
      border: `5px solid ${C.teal}`, borderRadius: 16, padding: '16px 28px', color: C.teal, background: 'rgba(11,95,84,.06)',
    }}>
      <div style={{fontSize: 44, fontWeight: 800, letterSpacing: -0.5}}>{children}</div>
      <Mono style={{fontSize: 22, fontWeight: 600, opacity: 0.85}}>{sub}</Mono>
    </div>
  );
};

export const S2Refuse: React.FC = () => {
  const f = useCurrentFrame();
  const bFade = 1 - ramp(f, 40, 66); // 2.2 s of Flow lab crystal
  const tBanner = cue(s, 'Rule C5', 0, -0.3);
  const tBar = cue(s, 'panels');
  const ZOOM = 1.28;
  return (
    <Stage theme="light">
      <Broll src="v2/flow/lab_crystal.mp4" theme="light" opacity={bFade} scrim="center" />
      <Title theme="light" text="Built on what it refuses" sub="Frozen Step 1 sheets: H2 (11 papers) · H5 (19 papers)" />
      <Stamp at={cue(s, '0 estimated')} x={110} y={250} rot={-1.2} sub="no visual or estimated P values">No estimated P-values</Stamp>
      <Stamp at={cue(s, '0 review-paper')} x={1010} y={262} rot={1}  sub="no review articles as evidence">No review hearsay</Stamp>
      <Stamp at={cue(s, '0 predicted')} x={110} y={420} rot={0.8} sub="Rule C5: 3D models stay out of the sheets">No predicted structures</Stamp>
      <Stamp at={tBar} x={1010} y={432} rot={-0.8} sub="panel or Abstract location on every row">No missing panel ID</Stamp>
      <div style={{position: 'absolute', left: 110, top: 585, opacity: ramp(f, tBanner, tBanner + 8), fontFamily: F.mono, fontSize: 20, color: C.ink2}}>
        live docs/index.html · Rule C5 banner
      </div>
      <Shot name="c5_banner" x={110} y={615} zoom={ZOOM} opacity={ramp(f, tBanner, tBanner + 12)} />
      <div style={{position: 'absolute', left: 110, top: 722, opacity: ramp(f, tBar, tBar + 8), fontFamily: F.mono, fontSize: 20, color: C.ink2}}>
        live docs/index.html · hypothesis selector and metrics
      </div>
      <Shot name="controls_bar" x={110} y={752} zoom={ZOOM} opacity={ramp(f, tBar, tBar + 12)} />
    </Stage>
  );
};
