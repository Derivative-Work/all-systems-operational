import React, {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

// Variable fonts, all SIL OFL 1.1 (remotion/public/fonts, SOURCES.md has URL and sha256 for each).
const FACES: [string, string, string][] = [
  ['Inter', 'fonts/Inter-VF.ttf', '100 900'], // generic UI: status page, chat, calendar, chart
  ['Work Sans', 'fonts/WorkSans-VF.ttf', '100 900'], // the station's look; also the Switch rig's ON/OFF marks
  ['Caveat', 'fonts/Caveat-VF.ttf', '400 700'], // handwriting: whiteboard, Polaroid caption
  ['Noto Sans Mono', 'fonts/NotoSansMono-Regular.ttf', '400'], // M7b: the treehouse terminal
  ['Noto Sans Mono', 'fonts/NotoSansMono-Bold.ttf', '700'],
];

export const UI = "'Inter', sans-serif";
export const STATION = "'Work Sans', sans-serif";
export const HAND = "'Caveat', cursive";
export const MONO = "'Noto Sans Mono', monospace";

/** Loads the fonts and holds the render until they are ready. */
export const Fonts: React.FC = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FACES.map(([family, file, weight]) => {
      const f = new FontFace(family, `url(${staticFile(file)})`, {weight});
      return f.load().then((loaded) => document.fonts.add(loaded));
    })).then(() => continueRender(handle)).catch((e) => { console.error(e); continueRender(handle); });
  }, [handle]);
  return null;
};
