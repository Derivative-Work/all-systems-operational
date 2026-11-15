// O01, beat 2: the creator's real screenshots, the only real interfaces in the video, each captioned "real
// screenshot" with its time (brief: no more than 3 s together). The license error comes first (Friday), then the
// status page that wouldn't load (Thursday 1:07 p.m. ET, when the creator posted it).
import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {UI} from '../Fonts';
import {clamp, Frame} from './Common';

// PLACEHOLDER: the "No license found" capture stands in until the creator has permission or a new capture (brief, O01);
// its caption date must follow whichever capture replaces it.
export const LICENSE_CAPTION = 'real screenshot · Fri, Nov 13';
export const STATUS_CAPTION = 'real screenshot · Thu, Nov 12, 1:07 p.m. ET';

const Shot: React.FC<{src: string; w: number; h: number; crop?: [number, number, number, number]; scale: number; caption: string; start: number}> = ({
  src, w, h, crop = [0, 0, w, h], scale, caption, start,
}) => {
  const f = useCurrentFrame() - start;
  const [cx, cy, cw, ch] = crop;
  const push = interpolate(f, [0, 45], [1, 1.025], clamp);
  return (
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 34}}>
      <div style={{width: cw * scale, height: ch * scale, overflow: 'hidden', position: 'relative', transform: `scale(${push})`,
        boxShadow: '0 30px 80px rgba(0,0,0,0.55)', borderRadius: 10}}>
        <Img src={staticFile(src)} style={{position: 'absolute', left: -cx * scale, top: -cy * scale, width: w * scale, height: h * scale}} />
      </div>
      <div style={{fontFamily: UI, fontSize: 32, fontWeight: 500, color: '#eceae6', background: 'rgba(255,255,255,0.08)',
        padding: '10px 22px', borderRadius: 10, letterSpacing: 0.3}}>{caption}</div>
    </div>
  );
};

export const RealScreens: React.FC<{split?: number}> = ({split}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  const s = split ?? Math.round(d / 2);
  return (
    <Frame bg="#2a2d31">
      {f < s
        ? <Shot src="real/m365-license-failed-outage.png" w={487} h={580} crop={[20, 26, 456, 528]} scale={1.55} caption={LICENSE_CAPTION} start={0} />
        : <Shot src="real/status-page-broken.png" w={1349} h={984} crop={[50, 32, 1250, 884]} scale={0.98} caption={STATUS_CAPTION} start={s} />}
    </Frame>
  );
};
