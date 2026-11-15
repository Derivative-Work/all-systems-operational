// O12/O21: the livestream freezes under a buffering spinner (transparent overlay over the Blender frame). O21 adds
// the caption "Incident reopened". Also the "dramatization" caption overlay for shots that need one.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {STATION, UI} from '../Fonts';
import {Frame, Tag} from './Common';

export const BufferingFreeze: React.FC<{caption?: string; dim?: number}> = ({caption, dim = 0.5}) => {
  const f = useCurrentFrame();
  const rot = (f * 12) % 360;
  return (
    <Frame>
      <div style={{position: 'absolute', inset: 0, background: `rgba(8,10,12,${dim})`}} />
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 44}}>
        <svg width={150} height={150} viewBox="0 0 100 100" style={{transform: `rotate(${rot}deg)`}}>
          <circle cx={50} cy={50} r={40} fill="none" stroke="rgba(255,255,255,0.22)" strokeWidth={8} />
          <circle cx={50} cy={50} r={40} fill="none" stroke="#fff" strokeWidth={8} strokeLinecap="round" strokeDasharray="70 182" />
        </svg>
        {caption && <div style={{fontFamily: STATION, fontSize: 56, fontWeight: 600, color: '#fff', textShadow: '0 2px 12px rgba(0,0,0,0.5)'}}>{caption}</div>}
      </div>
    </Frame>
  );
};

/** A transparent overlay with one caption in the lower right, e.g. "dramatization" (O08 cutaway, O18). */
export const CaptionOverlay: React.FC<{text: string; at?: number; corner?: 'tl' | 'tr' | 'bl' | 'br'; size?: number}> = ({text, at = 0, corner = 'br', size = 30}) => {
  const f = useCurrentFrame();
  return <Frame><span style={{fontFamily: UI}} />{f >= at && <Tag text={text} corner={corner} inset={48} size={size} />}</Frame>;
};
