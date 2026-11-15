// O10/O11/O12/O20/O21: Little Switch from Default On, the switch that runs the ON AIR sign. A wrapper only: the
// cameo and rig in ../defaultOn are used unchanged (README there), silent, flat 2D, never restyled. SwitchCameo's
// `flip` frame rocks the paddle ON -> OFF; the wrapper adds motion only (the strain's shudder, the sag's droop).
import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {BEAT, rng} from '../config';
import {SwitchCameo} from '../defaultOn/SwitchCameo';
import {clamp, Frame} from './Common';

export type SwitchState = 'on' | 'off' | 'straining' | 'sagging';
export const SW = 1080; // square transparent plane for Blender

const jit = (() => { const r = rng(11); return Array.from({length: 64}, () => [r() - 0.5, r() - 0.5]); })();

/** `sagAt`: frame the sag starts; `hold`: frames he holds before the paddle drops (O21 holds a beat longer than O12). */
export const SwitchPlane: React.FC<{state: SwitchState; sagAt?: number; hold?: number}> = ({state, sagAt = 6, hold = BEAT}) => {
  const f = useCurrentFrame();
  const NEVER = 1e9;
  const flip = state === 'off' ? -100 : state === 'sagging' ? sagAt + hold : NEVER;
  let tx = 0, ty = 0, rot = 0, sx = 1, sy = 1;
  if (state === 'straining') {
    const [a, b] = jit[f % jit.length];
    tx = a * 10; ty = b * 8; sy = 0.97 + 0.02 * Math.sin(f * 1.7); sx = 2 - sy;
  }
  if (state === 'sagging') {
    // he sinks and leans while holding on, then drops with the paddle
    const k = interpolate(f, [sagAt, sagAt + hold], [0, 0.6], {...clamp, easing: Easing.inOut(Easing.sin)});
    const drop = interpolate(f, [sagAt + hold, sagAt + hold + 6], [0, 0.4], {...clamp, easing: Easing.in(Easing.quad)});
    ty = (k + drop) * 90; rot = (k + drop) * 9;
    const [a] = jit[f % jit.length];
    tx = f < sagAt + hold ? a * 6 * k : 0;
  }
  return (
    <Frame>
      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080,
        transform: `translate(${tx}px, ${ty}px) rotate(${rot}deg) scale(${sx}, ${sy})`, transformOrigin: `${SW / 2}px ${SW / 2}px`}}>
        <SwitchCameo enter={-100} flip={flip} x={SW / 2} y={SW / 2 + 20} scale={1.45} />
      </div>
    </Frame>
  );
};
