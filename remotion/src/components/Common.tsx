import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Fonts, UI} from '../Fonts';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** Every composition renders inside this: fonts first, then an optional background (none = transparent). */
export const Frame: React.FC<{bg?: string; children: React.ReactNode}> = ({bg, children}) => (
  <AbsoluteFill style={{background: bg}}>
    <Fonts />
    {children}
  </AbsoluteFill>
);

/** A small on-screen label: "real screenshot", "recreation", "dramatization". */
export const Tag: React.FC<{text: string; corner?: 'tl' | 'tr' | 'bl' | 'br'; dark?: boolean; size?: number; inset?: number}> = ({
  text, corner = 'br', dark = true, size = 26, inset = 40,
}) => {
  const pos: React.CSSProperties = {
    position: 'absolute',
    [corner[0] === 't' ? 'top' : 'bottom']: inset,
    [corner[1] === 'l' ? 'left' : 'right']: inset,
  };
  return (
    <div style={{
      ...pos, fontFamily: UI, fontSize: size, fontWeight: 500, letterSpacing: 0.3, padding: `${size * 0.3}px ${size * 0.6}px`,
      borderRadius: size * 0.35, background: dark ? 'rgba(15,18,20,0.72)' : 'rgba(255,255,255,0.85)', color: dark ? '#f1f1ee' : '#1d2427',
    }}>{text}</div>
  );
};
