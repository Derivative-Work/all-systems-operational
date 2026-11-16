// M5 overlays (transparent, composited over the Blender shots):
// - LiveOverlay (O11, "everybody at once"): the livestream's viewer count spins up and the chat floods on the Hey!s;
//   Switch strains in a small inset (he's on the wall by the door, out of this shot's frame).
// - DisclosurePanel (O17): withdrawn (decisions 18); the full card plays at the end only.
// Chat handles and lines are invented and generic (brief guardrails: invented names, no real people or quotes).
import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {rng} from '../config';
import {STATION, UI} from '../Fonts';
import {T} from '../theme';
import {DISCLOSURE} from './Cards';
import {clamp, Frame} from './Common';
import {SwitchPlane} from './Switch';

const HANDLES = ['mossgrl', 'teapot_ty', 'drizzle_dad', 'cedar.k', 'tinyumbrella', 'lo-fi_lou', 'kettlebrew', 'pinecone88',
  'stompclap_sam', 'grey_sky_jo', 'banjo_fan', 'rainjacket', 'oatmilk_al', 'hilltop_h', 'quietcar'];
const LINES = ['HEY!', 'hey!!', 'turn it up', 'everybody sing', 'this is the one', 'HEY', 'is the stream lagging?', 'hey from the office',
  'same here', 'audio cutting out?', 'HEY!!!', 'singing along at my desk', 'refresh?', 'still loading', 'lol everyone at once'];

export const LiveOverlay: React.FC<{heys: number[]; strainAt: number}> = ({heys, strainAt}) => {
  const f = useCurrentFrame();
  // viewer count: a steady climb that jumps on each Hey! and spins (digits blur) after the second
  const base = 4120 + f * 9;
  const jumps = heys.reduce((n, h, i) => n + interpolate(f, [h, h + 12], [0, i === 0 ? 2600 : 9800], clamp), 0);
  const spin = f >= heys[1] ? (f * 7919) % 997 : 0;
  const viewers = Math.round(base + jumps + spin);
  // chat: one line every 10 frames, then every 4 after the first Hey!, every frame after the second
  const times: number[] = [];
  for (let t = 0, k = 0; t <= f; k++) {
    times.push(t);
    t += t < heys[0] ? 10 : t < heys[1] ? 4 : 1;
  }
  const pick = rng(77);
  const msgs = times.map((t, i) => ({t, h: HANDLES[Math.floor(pick() * HANDLES.length)], l: LINES[Math.floor(pick() * LINES.length)], i}));
  const shown = msgs.slice(-9);
  return (
    <Frame>
      <div style={{position: 'absolute', left: 70, top: 56, display: 'flex', gap: 16, alignItems: 'center', fontFamily: STATION}}>
        <div style={{background: T.coral, color: '#fff', fontWeight: 700, fontSize: 34, padding: '6px 18px', borderRadius: 8, letterSpacing: 2}}>LIVE</div>
        <div style={{background: 'rgba(15,18,20,0.72)', color: '#fff', fontSize: 34, fontWeight: 600, padding: '6px 18px', borderRadius: 8,
          fontVariantNumeric: 'tabular-nums'}}>{viewers.toLocaleString('en-US')} watching</div>
      </div>
      <div style={{position: 'absolute', right: 60, top: 180, width: 520, height: 500, overflow: 'hidden', display: 'flex', flexDirection: 'column',
        justifyContent: 'flex-end', gap: 10, fontFamily: UI, fontSize: 28}}>
        {shown.map((m) => (
          <div key={m.i} style={{background: 'rgba(15,18,20,0.62)', color: '#f1f1ee', padding: '8px 16px', borderRadius: 10,
            opacity: interpolate(f - m.t, [0, 3], [0, 1], clamp)}}>
            <span style={{color: '#9fd8c2', fontWeight: 600}}>{m.h}</span> {m.l}
          </div>
        ))}
      </div>
      <div style={{position: 'absolute', right: 60, bottom: 60, width: 300, height: 300, borderRadius: 18, overflow: 'hidden',
        background: 'rgba(25,22,20,0.8)', border: '3px solid rgba(255,255,255,0.5)'}}>
        <div style={{position: 'absolute', left: -50, top: -40, width: 1080, height: 1080, transform: 'scale(0.36)', transformOrigin: 'top left'}}>
          <SwitchPlane state="straining" strainAt={strainAt} />
        </div>
      </div>
    </Frame>
  );
};

// DisclosurePanel (O17) withdrawn: the disclosure plays at the end only (decisions 18; human interventions 16).
