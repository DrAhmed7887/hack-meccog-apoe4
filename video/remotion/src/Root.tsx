import React from "react";
import { Composition } from "remotion";
import timeline from "./timeline.json";
import { Film, Teaser } from "./Film";

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
        durationInFrames={timeline.teaserTotalFrames}
        fps={timeline.fps}
        width={timeline.width}
        height={timeline.height}
      />
    </>
  );
};
