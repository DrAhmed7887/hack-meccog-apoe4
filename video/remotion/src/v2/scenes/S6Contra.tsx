import React from 'react';
import {useCurrentFrame} from 'remotion';
import {C, D, F, cue, rectOf, scene} from '../theme';
import {Badge, Mark, Mono, Shot, Stage, Title, ramp} from '../ui';

const s = scene('s6');
const F12 = D.featured['H2-P2.F12'];
const F6 = D.featured['H2-P3.F6'];
const F4 = D.featured['H2-P5.F4'];
const ZOOM = 1.35;

const Card: React.FC<{at: number; x: number; w: number; fid: typeof F6; badge: string; line: string}> = ({at, x, w, fid, badge, line}) => {
  const f = useCurrentFrame();
  const o = ramp(f, at, at + 12);
  return (
    <div style={{position: 'absolute', left: x, top: 715, width: w, opacity: o, transform: `translateY(${(1 - o) * 18}px)`,
      background: '#fff', border: `3px solid ${C.burnt}`, borderRadius: 14, padding: '12px 18px'}}>
      <div style={{display: 'inline-block', background: C.burnt, color: '#fff', fontWeight: 800, fontSize: 20, borderRadius: 8, padding: '3px 12px'}}>{badge}</div>
      <div style={{fontSize: 25, fontWeight: 700, marginTop: 8, lineHeight: 1.2}}>{line}</div>
      <Mono style={{fontSize: 16, color: C.ink2}}>{fid.id} · PMID {fid.pmid} · {fid.location}</Mono>
    </div>
  );
};

export const S6Contra: React.FC = () => {
  const f = useCurrentFrame();
  const row = rectOf('drawer_h2_29946028', 'row');
  const hit = rectOf('drawer_h2_29946028', 'text:decreased by');
  const t45 = cue(s, '~45%');
  const tYet = cue(s, 'Yet');
  const tNeur = cue(s, 'neurons');
  const tKo = cue(s, 'deleting');
  return (
    <Stage theme="light">
      <Title theme="light" text="Cell-type contradictions kept intact" />
      {/* left: astrocytes, NHE6 ~45% lower */}
      <Shot name="drawer_h2_29946028" x={100} y={235} zoom={ZOOM} opacity={ramp(f, t45 - 20, t45 - 6)}
        crop={{x: 0, y: row.y - 10, w: 628, h: row.h + 10}}>
        <Mark r={hit} at={t45} label="~45% lower NHE6" />
      </Shot>
      <Mono style={{position: 'absolute', left: 100, top: 235 + (row.h + 10) * ZOOM + 10, fontSize: 21, color: C.ink2, opacity: ramp(f, t45, t45 + 10)}}>
        astrocytes · {F12.id} · PMID {F12.pmid} · {F12.location}
      </Mono>
      {/* right: the real Contradicts filter for NHE6 */}
      <Shot name="drawer_h2_contra" x={972} y={235} zoom={ZOOM} opacity={ramp(f, tYet - 6, tYet + 8)}
        crop={{x: 0, y: 130, w: 628, h: 335}}>
        <div style={{position: 'absolute', left: 0, top: 0, right: 0, bottom: 0, boxShadow: `inset 0 0 0 4px ${C.burnt}`, borderRadius: 14}} />
      </Shot>
      <div style={{position: 'absolute', left: 972, top: 190, opacity: ramp(f, tYet, tYet + 10)}}>
        <Badge at={tYet} color={C.burnt} style={{fontSize: 22}}>Filter: Contradicts · NHE6</Badge>
      </div>
      <Card at={tNeur} x={972} w={410} fid={F6} badge="neurons · shRNA" line="NHE6 knockdown restores cell-surface Apoer2" />
      <Card at={tKo} x={1410} w={410} fid={F4} badge="knock-in slices · KO" line="Conditional NHE6 knockout restores Reelin-enhanced LTP" />
      {/* honest boundaries */}
      <div style={{position: 'absolute', left: 100, top: 722, display: 'flex', flexDirection: 'column', gap: 10}}>
        <Badge at={cue(s, '0 Tier 1')} color={C.ink} style={{fontSize: 28, padding: '6px 16px'}}>{`H2: ${D.counts.H2.n_tier1} Tier 1 papers`}<div style={{fontFamily: F.mono, fontSize: 18, fontWeight: 600, color: '#A9B7B2'}}>{`Tier 1 = ${D.counts.tier1Def} · H2 uses Tier 2 models`}</div></Badge>
        <Badge at={cue(s, '4 paywalled')} color={C.paper2} fg={C.ink} style={{fontSize: 28, padding: '6px 16px', border: `2px solid ${C.ink}`}}>{`${D.counts.paywalled} paywalled: abstract-only`}<div style={{fontFamily: F.mono, fontSize: 18, fontWeight: 600, color: C.ink2}}>{`H2 ${D.counts.H2.n_unavailable} + H5 ${D.counts.H5.n_unavailable} · gates never bypassed`}</div></Badge>
      </div>
    </Stage>
  );
};
