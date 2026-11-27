import React from "react";
import { Composition } from "remotion";
import timeline from "./timeline.json";
import { Film, Teaser, TEASER_TOTAL_FRAMES } from "./Film";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MecCogFilm"
        component={Film}
        durationInFrames={timeline.totalFrames}
        fps={timeline.fps}
        width={timeline.width}
        height={timeline.height}
      />
      <Composition
        id="MecCogTeaser"
        component={Teaser}
        durationInFrames={TEASER_TOTAL_FRAMES}
        fps={timeline.fps}
        width={timeline.width}
        height={timeline.height}
      />
    </>
  );
};
