import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, D, F, cue, scene} from '../theme';
import {Clip, Mono, Stage, Title, ramp} from '../ui';

const s = scene('s3');
const SPIN_FRAMES = 194;
const G = D.geometry;
const PX_PER_A = 112; // caliper scale: 1 angstrom = 112 video px, same for all three rows (5.34 A = 598 px)

type Row = {struct: string; a: string; b: string; d: number; color: string; at: number; note: string};

const Caliper: React.FC<{row: Row; y: number}> = ({row, y}) => {
  const f = useCurrentFrame();
  const p = ramp(f, row.at, row.at + 26);
  const len = row.d * PX_PER_A * p;
  const x0 = 60;
  const shown = row.d.toFixed(2); // fixed from first appearance: never count through fake intermediate values
  return (
    <div style={{position: 'absolute', left: 1110, top: y, width: 780, opacity: ramp(f, row.at - 6, row.at + 6)}}>
      <Mono style={{fontSize: 26, fontWeight: 700, color: C.paper}}>
        <span style={{color: row.color}}>{row.struct}</span> {row.a}–{row.b}
      </Mono>
      <svg width={780} height={136} style={{display: 'block', marginTop: 6}}>
        <line x1={x0} x2={x0 + len} y1={64} y2={64} stroke={row.color} strokeWidth={4} />
        {[0, 1].map((k) => (
          <line key={k} x1={x0 + (k ? len : 0)} x2={x0 + (k ? len : 0)} y1={44} y2={84} stroke={row.color} strokeWidth={4} />
        ))}
        <circle cx={x0} cy={64} r={13} fill={C.paper} stroke={row.color} strokeWidth={4} />
        <circle cx={x0 + len} cy={64} r={13} fill={row.color} opacity={p} />
        <text x={x0} y={30} textAnchor="middle" fontFamily={F.mono} fontSize={20} fill="#A9B7B2">{row.a}</text>
        <text x={x0 + len} y={30} textAnchor="middle" fontFamily={F.mono} fontSize={20} fill="#A9B7B2" opacity={p}>{row.b}</text>
        <text x={x0 + Math.max(len / 2, 90)} y={126} textAnchor="middle" fontFamily={F.mono} fontSize={38} fontWeight={700} fill={row.color}>{shown} Å</text>
      </svg>
      <div style={{fontSize: 22, color: '#A9B7B2', marginTop: -4}}>{row.note}</div>
    </div>
  );
};

export const S3Switch: React.FC = () => {
  const f = useCurrentFrame();
  const tCal = cue(s, '2.53 Å'); // the clip is timed to END here: freeze on the cue as the first caliper draws
  const start = Math.max(0, tCal - (SPIN_FRAMES - 1));
  const frozen = f >= tCal;
  const rows: Row[] = [
    {struct: G.arg112.struct, a: G.arg112.res1, b: G.arg112.res2, d: G.arg112.distance_A, color: C.emeraldBright, at: tCal, note: 'APOE4 salt bridge'},
    {struct: G.arg61Apoe4.struct, a: G.arg61Apoe4.res1, b: G.arg61Apoe4.res2, d: G.arg61Apoe4.distance_A, color: C.amber, at: cue(s, 'Arg61'), note: 'APOE4: Arg61 displaced from Glu109'},
    {struct: G.arg61Apoe3.struct, a: G.arg61Apoe3.res1, b: G.arg61Apoe3.res2, d: G.arg61Apoe3.distance_A, color: '#A9B7B2', at: cue(s, 'displaced'), note: 'APOE3 (Cys112): distinct closest-atom pair'},
  ];
  return (
    <Stage theme="dark">
      <Title theme="dark" text="The 2.53 Å salt-bridge switch" sub="Crystal geometry from the PDB files in docs/structures" />
      <div style={{position: 'absolute', left: 100, top: 250, width: 960, height: 540, borderRadius: 18, overflow: 'hidden',
        boxShadow: `0 0 0 ${frozen ? 3 : 1}px ${frozen ? C.emeraldBright : 'rgba(255,255,255,.12)'}, 0 30px 80px rgba(0,0,0,.55)`}}>
        <Clip src="v2/shots/molstar_spin.mp4" frames={SPIN_FRAMES} start={start} freezeAt={tCal} style={{width: 960, height: 540}} />
      </div>
      <Mono style={{position: 'absolute', left: 100, top: 808, fontSize: 22, color: '#A9B7B2'}}>
        live Mol* WebGL · 1B68 {frozen ? '· frozen at the salt bridge' : '· rotating'}
      </Mono>
      {rows.map((r, i) => <Caliper key={i} row={r} y={250 + i * 235} />)}
    </Stage>
  );
};
