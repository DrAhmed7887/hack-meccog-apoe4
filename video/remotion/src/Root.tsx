import React from "react";
import { Composition } from "remotion";
import timeline from "./timeline.json";
import { Film, Teaser, TEASER_TOTAL_FRAMES } from "./Film";
import { FilmV2, TeaserV2 } from "./v2/FilmV2";
import { FILM_FRAMES, FPS, TEASER_FRAMES } from "./v2/theme";

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
      <Composition id="MecCogFilmV2" component={FilmV2} durationInFrames={FILM_FRAMES} fps={FPS} width={1920} height={1080} />
      <Composition
        id="MecCogTeaserV2"
        component={TeaserV2}
        durationInFrames={TEASER_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
    </>
  );
};
