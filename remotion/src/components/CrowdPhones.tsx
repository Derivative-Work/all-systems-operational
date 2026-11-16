// M7c (the coordinator's Part B; decisions 28 left them blank): what the live room's crowd phones show in the wides,
// in place of blank glowing screens. Plausible and generic, unreadable at that distance, nothing branded: a lock
// screen with the #it-help notification, a camera recording the band (a crop of a rendered live-room frame, no UI
// of any real camera app), and the #it-help chat (PhoneChat.tsx, M5's thread). Screen textures (PW x PH) mapped onto
// the Blender phones by blender/look.py (crowd_phones).
import React from 'react';
import {Img, staticFile} from 'remotion';
import {PH, PW} from '../config';
import {UI} from '../Fonts';
import {T} from '../theme';
import {StatusBar} from './Phone';

/** A lock screen at 1:04 p.m. Thursday: a dim generic wallpaper, the clock, the #it-help notification. */
export const CrowdLock: React.FC = () => (
  <div style={{position: 'absolute', inset: 0, fontFamily: UI, color: '#fff',
    background: 'radial-gradient(ellipse at 30% 25%, #4b6a63 0%, #23383a 45%, #121b1f 100%)'}}>
    <StatusBar time="" dark />
    <div style={{textAlign: 'center', marginTop: 120, fontSize: 64, fontWeight: 500, opacity: 0.9}}>Thursday, November 12</div>
    <div style={{textAlign: 'center', fontSize: 300, fontWeight: 600, letterSpacing: -6, lineHeight: 1.05}}>1:04</div>
    <div style={{position: 'absolute', left: 50, right: 50, top: 1280, display: 'flex', flexDirection: 'column', gap: 26}}>
      {[['#it-help', 'Dana: is email down for anyone else?', 'now'], ['mail', "couldn't refresh · 3 tries", '2m ago']].map(([a, b, c]) => (
        <div key={a} style={{background: 'rgba(235,240,240,0.2)', borderRadius: 52, padding: '36px 44px'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 40, opacity: 0.8}}><span>{a}</span><span>{c}</span></div>
          <div style={{fontSize: 50, fontWeight: 600, marginTop: 10}}>{b}</div>
        </div>
      ))}
    </div>
    <div style={{position: 'absolute', left: PW / 2 - 140, bottom: 40, width: 280, height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.8)'}} />
  </div>
);

/** Recording the band: the viewfinder (a crop of a rendered live-room frame), a red dot and timer, a shutter ring. */
export const CrowdCamera: React.FC<{photo?: string}> = ({photo = 'gen/m7c_viewfinder.jpg'}) => (
  <div style={{position: 'absolute', inset: 0, background: '#000', fontFamily: UI, color: '#fff'}}>
    <Img src={staticFile(photo)} style={{position: 'absolute', left: 0, top: 260, width: PW, height: PH - 640, objectFit: 'cover'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 120, display: 'flex', justifyContent: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 20, background: 'rgba(0,0,0,0.5)', borderRadius: 30, padding: '10px 30px', fontSize: 50,
        fontVariantNumeric: 'tabular-nums'}}>
        <div style={{width: 30, height: 30, borderRadius: 15, background: T.bad}} />0:41
      </div>
    </div>
    <div style={{position: 'absolute', left: PW / 2 - 110, bottom: 110, width: 220, height: 220, borderRadius: 110, border: '14px solid #fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{width: 90, height: 90, borderRadius: 18, background: T.bad}} />
    </div>
  </div>
);

export const CROWD_PHONE = {w: PW, h: PH};
