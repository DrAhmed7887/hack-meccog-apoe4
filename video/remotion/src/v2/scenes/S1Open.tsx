import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, F, cue, scene} from '../theme';
import {Badge, Broll, Clip, Mono, Stage, ramp} from '../ui';

const s = scene('s1');
const SPIN_FRAMES = 194; // molstar_spin.mp4 at 30 fps

export const S1Open: React.FC = () => {
  const f = useCurrentFrame();
  const bFade = 1 - ramp(f, 70, 105); // Flow b-roll gone by ~3.5 s
  const live = ramp(f, 72, 105);
  const tApoe = cue(s, 'APOE4');
  const tKhepri = cue(s, 'Khepri');
  const tStep = cue(s, 'Step 1');
  return (
    <Stage theme="dark">
      <Broll src="v2/flow/neurons_vesicles.mp4" theme="dark" opacity={bFade} scrim="left" />
      {/* the real thing, from ~3.5 s: live Mol* WebGL, structure 1B68 */}
      <div style={{position: 'absolute', left: 940, top: 190, width: 880, height: 495, borderRadius: 18, overflow: 'hidden', opacity: live,
        boxShadow: '0 0 0 1px rgba(255,255,255,.1), 0 30px 80px rgba(0,0,0,.6)', transform: `translateY(${(1 - live) * 24}px)`}}>
        <Clip src="v2/shots/molstar_spin.mp4" frames={SPIN_FRAMES} start={72} style={{width: 880, height: 495}} />
      </div>
      <div style={{position: 'absolute', left: 940, top: 706, width: 880, opacity: live, fontFamily: F.mono, fontSize: 22, color: '#A9B7B2'}}>
        live Mol* WebGL · PDB 1B68 · APOE4 crystal structure
      </div>
      {/* frame 0 headline: five words, visible from the first frame */}
      <div style={{position: 'absolute', left: 120, top: 250, width: 800}}>
        <div style={{fontSize: 104, fontWeight: 800, letterSpacing: -3, lineHeight: 1.02, color: C.paper}}>
          One residue.
          <br />
          <span style={{color: C.emeraldBright}}>Every number sourced.</span>
        </div>
        <div style={{display: 'flex', gap: 14, marginTop: 44, flexWrap: 'wrap'}}>
          <Badge at={tApoe} color={C.emerald} style={{fontSize: 28}}>APOE4 vs APOE3</Badge>
          <Badge at={tStep} color={C.obsidian2} fg={C.paper} style={{fontSize: 28, border: `1px solid ${C.obsidianRule}`}}>Step 1 sheets · H2 · H5</Badge>
          <Badge at={tKhepri} color={C.obsidian2} fg={C.emeraldBright} style={{fontSize: 28, border: `1px solid ${C.emerald}`}}>Team Khepri</Badge>
        </div>
      </div>
      <AbsoluteFill style={{pointerEvents: 'none'}}>
        <Mono style={{position: 'absolute', left: 120, top: 84, fontSize: 24, color: '#A9B7B2', letterSpacing: 2}}>MECCOG · APOE4</Mono>
      </AbsoluteFill>
    </Stage>
  );
};
