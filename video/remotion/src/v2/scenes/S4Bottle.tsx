import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, D, type ShotName, cue, rectOf, scene} from '../theme';
import {Broll, Mark, Mono, Shot, Stage, Title, ramp} from '../ui';

const s = scene('s4');
const FEAT = D.featured['H5-P4.F1'];
const FEAT_P6 = D.featured['H5-P6.F3'];
const FOLD = FEAT.effect.replace('x', '-fold');
const DRAWER = `drawer_h5_${FEAT.pmid}` as ShotName;

const Node: React.FC<{x: number; y: number; w: number; at: number; title: string; sub: string; color: string}> = ({x, y, w, at, title, sub, color}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, at + 12);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, opacity: o, transform: `translateX(${(1 - o) * -24}px)`,
      background: '#fff', border: `3px solid ${color}`, borderRadius: 16, padding: '14px 22px', boxShadow: '0 12px 30px rgba(16,32,27,.08)'}}>
      <div style={{fontSize: 34, fontWeight: 800, color}}>{title}</div>
      <Mono style={{fontSize: 21, color: C.ink2}}>{sub}</Mono>
    </div>
  );
};

const Arrow: React.FC<{x: number; y: number; at: number}> = ({x, y, at}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, at + 10);
  return (
    <svg width={110} height={30} style={{position: 'absolute', left: x, top: y, opacity: o}}>
      <line x1={4} x2={90 * o + 4} y1={15} y2={15} stroke={C.ink2} strokeWidth={4} />
      <path d="M86 5 L104 15 L86 25 Z" fill={C.ink2} opacity={o} />
    </svg>
  );
};

export const S4Bottle: React.FC = () => {
  const f = useCurrentFrame();
  const bOut = 1 - ramp(f, 55, 75); // 2.5 s of Flow endosome membrane
  const tH2 = cue(s, 'H2');
  const tApoer = cue(s, 'ApoER2');
  const tNhe = cue(s, 'NHE6');
  const tH5 = cue(s, 'H5');
  const tFold = cue(s, FOLD);
  const t53 = cue(s, FEAT_P6.cardTitle);

  // single 3x zoom: whole drawer pane -> the H5-P4.F1 row, crisp because the capture is 3x
  const row = rectOf(DRAWER, 'row');
  const quoteHit = rectOf(DRAWER, `text:${FOLD}, p${FEAT.pValue}`);
  const figHit = rectOf(DRAWER, 'text:Fig 6H');
  const z = ramp(f, tFold - 24, tFold + 14);
  const full = {x: 0, y: 0, w: 628, h: 777};
  const tight = {x: 8, y: row.y - 10, w: 612, h: row.h + 20};
  const crop = {x: full.x + (tight.x - full.x) * z, y: full.y + (tight.y - full.y) * z, w: full.w + (tight.w - full.w) * z, h: full.h + (tight.h - full.h) * z};
  const zoom = 1.25 + (3 - 1.25) * z;
  const sx = (1920 - crop.w * zoom) / 2;
  const sy = 40 + (940 - crop.h * zoom) / 2;
  const schem = 1 - ramp(f, tFold - 14, tFold + 4);
  const card53 = ramp(f, t53 - 6, t53 + 10);

  return (
    <Stage theme="light">
      <Broll src="v2/flow/endosome_membrane.mp4" theme="light" opacity={bOut} scrim="center" />
      <div style={{opacity: schem}}>
        <Title theme="light" text="Two hypotheses, one trace click" sub="Two tracks, one shared question: where does APOE4 stall?" />
        <div style={{position: 'absolute', left: 120, top: 320, opacity: ramp(f, tH2, tH2 + 10), fontSize: 30, fontWeight: 800, color: C.emerald}}>H2 · early endosome</div>
        <Node x={120} y={372} w={430} at={tH2} title="APOE4" sub="vs APOE3 · recycling" color={C.emerald} />
        <Arrow x={565} y={420} at={tApoer - 6} />
        <Node x={690} y={372} w={430} at={tApoer} title="ApoER2" sub="receptor recycling" color={C.emerald} />
        <Arrow x={1135} y={420} at={tNhe - 6} />
        <Node x={1260} y={372} w={540} at={tNhe} title="NHE6" sub="exchanger · sets endosomal pH" color={C.emerald} />
        <div style={{position: 'absolute', left: 120, top: 585, opacity: ramp(f, tH5, tH5 + 10), fontSize: 30, fontWeight: 800, color: C.ink}}>H5 · lysosome</div>
        <Node x={120} y={637} w={430} at={tH5} title="APOE4" sub="astrocytes · microglia" color={C.ink} />
        <Arrow x={565} y={685} at={tH5 + 8} />
        <Node x={690} y={637} w={430} at={tH5 + 14} title={FEAT.cardTitle} sub={FEAT.cardSub} color={C.ink} />
        <Arrow x={1135} y={685} at={t53 - 8} />
        <Node x={1260} y={637} w={540} at={t53 - 2} title={FEAT_P6.cardTitle} sub={FEAT_P6.cardSub} color={C.ink} />
      </div>
      <Shot name={DRAWER} x={sx} y={sy} zoom={zoom} crop={crop} opacity={ramp(f, tFold - 24, tFold - 8)}>
        <Mark r={quoteHit} at={tFold} />
        <Mark r={figHit} at={tFold + 18} color={C.amber} />
      </Shot>
      <div style={{position: 'absolute', left: 0, right: 0, top: 22, display: 'flex', justifyContent: 'center', opacity: ramp(f, tFold + 10, tFold + 24)}}>
        <Mono style={{fontSize: 24, fontWeight: 700, color: C.ink, background: 'rgba(255,255,255,.92)', padding: '6px 18px', borderRadius: 10, border: `1px solid ${C.rule}`}}>
          {FEAT.id} · PMID {FEAT.pmid} · {FEAT.location} · {FEAT.effect} · p {FEAT.pValue}
        </Mono>
      </div>
      <div style={{position: 'absolute', left: 90, top: 735, width: 1740, opacity: card53, transform: `translateY(${(1 - card53) * 14}px)`,
        display: 'flex', alignItems: 'center', gap: 24, background: '#fff', border: `3px solid ${C.emerald}`, borderRadius: 14, padding: '12px 22px', boxSizing: 'border-box'}}>
        <Mono style={{fontSize: 22, fontWeight: 800, color: '#fff', background: C.emerald, padding: '6px 14px', borderRadius: 8, whiteSpace: 'nowrap'}}>
          {FEAT_P6.id} · PMID {FEAT_P6.pmid} · {FEAT_P6.location}
        </Mono>
        <div>
          <div style={{fontSize: 30, fontWeight: 800, color: C.ink}}>{FEAT_P6.description}</div>
          <Mono style={{fontSize: 19, color: C.ink2}}>{FEAT_P6.id} · PMID {FEAT_P6.pmid}</Mono>
        </div>
      </div>
    </Stage>
  );
};
