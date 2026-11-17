// O01, beat 2: the creator's real screenshot, the only real interface in the video, captioned "real screenshot" with
// its time (brief: no more than 3 s of real screenshots). Microsoft's service status page that wouldn't load (Thursday
// 1:07 p.m. ET, when the creator posted it).
// Human interventions 32: the "No license found" capture is cut (it was a placeholder, human interventions 6); the
// shot opens close on the tab and the address bar, the tab's loading indicator turning, then pulls back to the whole
// window. The screenshot froze the indicator as a grey dot; it is drawn over the dot, turning, in the same grey. Nothing
// else in the screenshot is changed.
import React from 'react';
import {Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {UI} from '../Fonts';
import {clamp, Frame} from './Common';

export const STATUS_CAPTION = 'real screenshot · Thu, Nov 12, 1:07 p.m. ET';

const SRC = 'real/status-page-broken.png';
const IMG = {w: 1349, h: 984};
const CROP = {x: 50, y: 32, w: 1250, h: 884}; // the window, without the screenshot's shadow margin
const BASE = 0.98; // screen pixels per screenshot pixel, pulled back
const FAV = {x: 183.5, y: 58.5}; // the tab's loading indicator (frozen as a dot in the screenshot)
const FOCUS = {x: 372, y: 78}; // screenshot point held at the frame's centre, zoomed: the tab and the address bar
const ZOOM = 2.75; // zoomed scale, relative to BASE
const CAPTION_H = 62;
const GAP = 34;

/** The tab's loading indicator: a grey arc turning clockwise, about 1.2 turns a second (screenshot pixels). */
const Spinner: React.FC<{f: number}> = ({f}) => {
  const turn = (f / 30) * 1.2 * 360;
  return (
    <>
      <div style={{position: 'absolute', left: FAV.x - 9, top: FAV.y - 9, width: 18, height: 18, background: '#fff'}} />
      <svg style={{position: 'absolute', left: FAV.x - 7, top: FAV.y - 7, width: 14, height: 14, transform: `rotate(${turn}deg)`}}
        viewBox="0 0 14 14">
        <path d="M7 1.4 A5.6 5.6 0 1 1 1.4 7" fill="none" stroke="#5d5a58" strokeWidth={1.7} strokeLinecap="round" />
      </svg>
    </>
  );
};

export const RealScreens: React.FC<{hold?: number; pull?: number}> = ({hold, pull}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d, width: W, height: H} = useVideoConfig();
  // zoomed for about a third of the shot, the pull-back over the middle, the whole window to the cut
  const h0 = hold ?? Math.round(d * 0.33);
  const p0 = pull ?? Math.round(d * 0.46);
  const t = interpolate(f, [h0, h0 + p0], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  // pulled back: the window centred above its caption
  const boxW = CROP.w * BASE;
  const boxH = CROP.h * BASE;
  const top1 = (H - (boxH + GAP + CAPTION_H)) / 2;
  const left1 = (W - boxW) / 2;
  const at1 = {x: left1 + (FOCUS.x - CROP.x) * BASE, y: top1 + (FOCUS.y - CROP.y) * BASE};
  const at0 = {x: W / 2, y: H * 0.36};
  const z = Math.pow(ZOOM, 1 - t); // a steady zoom (equal ratios per frame)
  const s = BASE * z;
  const ax = at0.x + (at1.x - at0.x) * t;
  const ay = at0.y + (at1.y - at0.y) * t;
  const left = ax - (FOCUS.x - CROP.x) * s;
  const top = ay - (FOCUS.y - CROP.y) * s;
  const shadow = interpolate(t, [0.5, 1], [0, 0.55], clamp);
  return (
    <Frame bg="#2a2d31">
      <div style={{position: 'absolute', left, top, width: CROP.w * s, height: CROP.h * s, overflow: 'hidden', borderRadius: 10 * z,
        boxShadow: `0 30px 80px rgba(0,0,0,${shadow})`}}>
        <div style={{position: 'absolute', left: -CROP.x * s, top: -CROP.y * s, width: IMG.w, height: IMG.h, transform: `scale(${s})`,
          transformOrigin: '0 0'}}>
          <Img src={staticFile(SRC)} style={{position: 'absolute', left: 0, top: 0, width: IMG.w, height: IMG.h}} />
          <Spinner f={f} />
        </div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: top1 + boxH + GAP, display: 'flex', justifyContent: 'center'}}>
        <div style={{fontFamily: UI, fontSize: 32, fontWeight: 500, color: '#eceae6', background: 'rgba(42,45,49,0.92)',
          padding: '10px 22px', borderRadius: 10, letterSpacing: 0.3, boxShadow: '0 0 0 1px rgba(255,255,255,0.08) inset'}}>{STATUS_CAPTION}</div>
      </div>
    </Frame>
  );
};
