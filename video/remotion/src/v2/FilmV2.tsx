import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {C, FPS, fontCss, layout, TEASER_IDS} from './theme';
import {Captions, Progress, SceneSeed, SlideWipes} from './ui';
import {S1Open} from './scenes/S1Open';
import {S2Refuse} from './scenes/S2Refuse';
import {S3Switch} from './scenes/S3Switch';
import {S4Bottle} from './scenes/S4Bottle';
import {S5Proof} from './scenes/S5Proof';
import {S6Contra} from './scenes/S6Contra';
import {S7Close} from './scenes/S7Close';

const SCENES: Record<string, React.FC> = {s1: S1Open, s2: S2Refuse, s3: S3Switch, s4: S4Bottle, s5: S5Proof, s6: S6Contra, s7: S7Close};

/** Shared timeline: lays the chosen scenes back to back with voice, wipes, captions and progress. */
export const SequenceTimeline: React.FC<{ids?: readonly string[]; withSound?: boolean}> = ({ids, withSound = true}) => {
  const {scenes, total} = layout(ids);
  return (
    <AbsoluteFill style={{background: C.obsidian}}>
      <style>{fontCss}</style>
      {scenes.map((s, idx) => {
        const Comp = SCENES[s.id];
        return (
          <Sequence key={s.id} from={s.at} durationInFrames={s.frames} name={s.id}>
            <SceneSeed.Provider value={idx + 1}>
              <Comp />
            </SceneSeed.Provider>
            {withSound ? (
              <Sequence from={Math.round(s.voiceAt * FPS)} layout="none">
                <Audio src={staticFile(s.audio)} />
              </Sequence>
            ) : null}
          </Sequence>
        );
      })}
      <SlideWipes scenes={scenes} />
      <Captions scenes={scenes} />
      <Progress total={total} />
    </AbsoluteFill>
  );
};

export const FilmV2: React.FC<{withSound?: boolean}> = ({withSound = true}) => <SequenceTimeline withSound={withSound} />;

/** Teaser derived from the film: s1 + s3 + s5 + s7, same scenes, same cues. */
export const TeaserV2: React.FC<{withSound?: boolean}> = ({withSound = true}) => <SequenceTimeline ids={TEASER_IDS} withSound={withSound} />;
