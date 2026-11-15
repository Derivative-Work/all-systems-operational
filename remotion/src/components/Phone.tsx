// A generic phone: a screen texture (PW x PH, for Blender's phone screens) and the same screen in a plain black-bezel
// phone for full-frame shots, held large and cropped by the frame's bottom edge.
import React from 'react';
import {PH, PW} from '../config';
import {UI} from '../Fonts';
import {Frame} from './Common';

export const StatusBar: React.FC<{time: string; dark?: boolean}> = ({time, dark}) => {
  const c = dark ? '#fff' : '#1d2427';
  return (
    <div style={{height: 120, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '20px 80px 0', fontFamily: UI,
      fontSize: 44, fontWeight: 600, color: c}}>
      <span>{time}</span>
      <svg width={170} height={44} viewBox="0 0 170 44">
        {[0, 1, 2, 3].map((i) => <rect key={i} x={i * 16} y={30 - i * 8} width={11} height={12 + i * 8} rx={2} fill={c} />)}
        <rect x={86} y={8} width={68} height={30} rx={8} fill="none" stroke={c} strokeWidth={3} />
        <rect x={91} y={13} width={44} height={20} rx={4} fill={c} />
        <rect x={156} y={17} width={5} height={12} rx={2} fill={c} />
      </svg>
    </div>
  );
};

/** The screen texture: PW x PH, no frame. */
export const Screen: React.FC<{bg: string; children: React.ReactNode}> = ({bg, children}) => (
  <div style={{position: 'absolute', left: 0, top: 0, width: PW, height: PH, background: bg, overflow: 'hidden'}}>{children}</div>
);

/** The screen inside a phone body, filling a 1920 x 1080 frame (top of the phone in view, bottom cropped). */
export const FramedPhone: React.FC<{bg?: string; scale?: number; top?: number; children: React.ReactNode; overlay?: React.ReactNode}> = ({
  bg = 'radial-gradient(ellipse at 50% 30%, #5d5a55 0%, #2b2a28 70%)', scale = 0.66, top = 70, children, overlay,
}) => {
  const bez = 46;
  return (
    <Frame bg={bg}>
      <div style={{position: 'absolute', left: 960 - ((PW + 2 * bez) * scale) / 2, top, width: PW + 2 * bez, height: PH + 2 * bez,
        transform: `scale(${scale})`, transformOrigin: 'top left', background: '#111', borderRadius: 150, boxShadow: '0 40px 120px rgba(0,0,0,0.6)'}}>
        <div style={{position: 'absolute', left: bez, top: bez, width: PW, height: PH, borderRadius: 110, overflow: 'hidden'}}>
          {children}
          <div style={{position: 'absolute', left: PW / 2 - 60, top: 34, width: 120, height: 36, borderRadius: 18, background: '#111'}} />
        </div>
      </div>
      {overlay}
    </Frame>
  );
};
