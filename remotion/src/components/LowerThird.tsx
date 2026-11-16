// O03/O08/O09/O19/O22: Session 503's lower thirds (transparent), with the station bug "50.3 FM" (the impossible
// frequency is the wink; never a real station's name, call letters, frequency or lower-third design).
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {INCIDENT} from '../config';
import {STATION} from '../Fonts';
import {T} from '../theme';
import {clamp, Frame} from './Common';

export const TITLE = 'All Systems Operational';
export const SUBTITLE = 'Live at Session 503';
export const KICKER = 'Session 503 · Live';
export const ECHOES = ['We are aware', 'Some users may', 'Be experiencing', 'Everything'];
export const SORRY = 'We are deeply sorry for the disruption';

export const Bug: React.FC<{opacity?: number}> = ({opacity = 0.9}) => (
  <div style={{position: 'absolute', right: 70, top: 56, width: 132, height: 132, borderRadius: '50%', background: T.evergreen, opacity,
    border: `4px solid ${T.paper}`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: T.paper,
    fontFamily: STATION, lineHeight: 1}}>
    <div style={{fontSize: 44, fontWeight: 700, letterSpacing: -1}}>50.3</div>
    <div style={{fontSize: 22, fontWeight: 600, letterSpacing: 4, marginTop: 4, color: '#f6b49d'}}>FM</div>
  </div>
);

/** The panel: a coral tab, then a paper card. `inP` 0..1 slides it in. */
const Panel: React.FC<{inP: number; kicker?: string; children: React.ReactNode; right?: React.ReactNode}> = ({inP, kicker, children, right}) => (
  <div style={{position: 'absolute', left: 110, bottom: 110, display: 'flex', alignItems: 'stretch', opacity: inP,
    transform: `translateX(${(1 - inP) * -40}px)`, boxShadow: '0 10px 30px rgba(0,0,0,0.25)', borderRadius: 10, overflow: 'hidden'}}>
    <div style={{width: 16, background: T.coral}} />
    <div style={{background: T.paper, padding: '20px 36px 22px', fontFamily: STATION, color: T.ink}}>
      {kicker && <div style={{fontSize: 22, fontWeight: 600, letterSpacing: 3, textTransform: 'uppercase', color: T.evergreen, marginBottom: 4}}>{kicker}</div>}
      {children}
    </div>
    {right}
  </div>
);

export type LowerThirdVariant = 'title' | 'uptime' | 'echo' | 'restored' | 'sorry';

/** M5: `inAt` delays the panel to a cue frame; `echoAt` gives each echo's frame (else every `echoEvery`); `tickAt` is
 * the frame the uptime ticker settles at 99.9% (cues: timing/shot_times.json marks). */
export const LowerThird: React.FC<{variant: LowerThirdVariant; echoEvery?: number; inAt?: number; echoAt?: number[]; tickAt?: number}> = ({
  variant, echoEvery = 72, inAt = 0, echoAt, tickAt = 40,
}) => {
  const f = useCurrentFrame() - inAt;
  const inP = interpolate(f, [0, 10], [0, 1], clamp);
  let body: React.ReactNode, kicker: string | undefined, right: React.ReactNode;
  if (variant === 'title' || variant === 'uptime') {
    body = <div style={{fontSize: 48, fontWeight: 600}}>{TITLE}<span style={{fontWeight: 400, color: T.inkSoft}}> · {SUBTITLE}</span></div>;
    if (variant === 'uptime') {
      // the ticker rolls up and settles at 99.9%
      const v = interpolate(f + inAt, [Math.max(8, tickAt - 32), tickAt], [98.2, 99.9], clamp);
      right = (
        <div style={{background: T.evergreen, color: T.paper, fontFamily: STATION, display: 'flex', alignItems: 'center', gap: 14, padding: '0 32px',
          fontSize: 40, fontWeight: 600}}>
          <div style={{width: 16, height: 16, borderRadius: '50%', background: '#7fe0a8', opacity: (Math.floor(f / 9) % 2) ? 0.5 : 1}} />
          Uptime <span style={{fontVariantNumeric: 'tabular-nums'}}>{v.toFixed(1)}%</span>
        </div>
      );
    }
  } else if (variant === 'echo') {
    // the host's echoes, one per call; each one pops in (placeholder spacing until M2)
    const at = echoAt ?? ECHOES.map((_, k) => k * echoEvery);
    const fa = f + inAt;
    const i = Math.max(0, at.filter((a) => fa >= a).length - 1);
    const pop = interpolate(fa - at[i], [0, 6], [0, 1], clamp);
    kicker = KICKER;
    body = <div style={{fontSize: 60, fontWeight: 600, opacity: pop, transform: `translateY(${(1 - pop) * 10}px)`, minWidth: 520}}>{ECHOES[i]}</div>;
  } else if (variant === 'restored') {
    kicker = KICKER;
    body = (
      <div style={{fontSize: 52, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 20}}>
        <div style={{width: 26, height: 26, borderRadius: '50%', background: T.ok, boxShadow: `0 0 12px ${T.ok}`}} />
        {INCIDENT.statusPhrases[3]}
      </div>
    );
  } else {
    kicker = KICKER;
    body = <div style={{fontSize: 52, fontWeight: 500}}>{SORRY}</div>;
  }
  if (f < 0) return <Frame><Bug /></Frame>;
  return (
    <Frame>
      <Bug />
      <Panel inP={inP} kicker={kicker} right={right}>{body}</Panel>
    </Frame>
  );
};

/** O18 (brief rev 141): on "(Not related to cyber, AI or agents)" a tag in the lower thirds' panel style pins to that
 * line on the whiteboard; the second line follows a beat later (`at`: the two cue frames). The panel sits where the
 * lower thirds do; a leader runs from it to the pin, the denial line's left end on screen per frame (`track`, string
 * keys, null when out of frame; timing/o18_pins.json from blender/o18_pins.py). Both lines go at `outAt`, the cut to
 * O18e. With an empty track (no projection yet) the pin is `fallback`. */
export const DenialTags: React.FC<{at: [number, number]; outAt: number; track: Record<string, [number, number] | null>;
  bottoms?: Record<string, number>; fallback?: [number, number]}> = ({at, outAt, track, bottoms = {0: 110}, fallback = [540, 500]}) => {
  const f = useCurrentFrame();
  if (f < at[0] || f >= outAt) return <Frame>{null}</Frame>;
  const pin = Object.keys(track).length ? track[String(f)] ?? null : fallback;
  const inP = interpolate(f - at[0], [0, 8], [0, 1], clamp);
  const in2 = interpolate(f - at[1], [0, 8], [0, 1], clamp);
  const lines = INCIDENT.denialTag;
  const [fs, lh, padT, padB, gap] = [38, 48, 18, 20, 10];
  // the panel's distance from the bottom edge: the latest entry of `bottoms` at or before this frame
  const left = 110;
  const bottom = Object.entries(bottoms).map(([k, v]) => [Number(k), v]).filter(([k]) => k <= f).sort((a, b) => a[0] - b[0]).pop()?.[1] ?? 110;
  const h = padT + lh + in2 * (gap + lh) + padB;   // the panel grows as the second line arrives
  const top = 1080 - bottom - h;
  return (
    <Frame>
      {pin && (
        <svg style={{position: 'absolute', inset: 0, opacity: inP}} width={1920} height={1080}>
          <line x1={pin[0]} y1={pin[1]} x2={left + 48} y2={top} stroke={T.paper} strokeWidth={3} />
          <circle cx={pin[0]} cy={pin[1]} r={10} fill="none" stroke={T.paper} strokeWidth={3} />
          <circle cx={pin[0]} cy={pin[1]} r={4} fill={T.coral} />
        </svg>
      )}
      <div style={{position: 'absolute', left, bottom, height: h, display: 'flex', alignItems: 'stretch', opacity: inP,
        transform: `translateX(${(1 - inP) * -40}px)`, boxShadow: '0 10px 30px rgba(0,0,0,0.25)', borderRadius: 10, overflow: 'hidden'}}>
        <div style={{width: 16, background: T.coral, flexShrink: 0}} />
        <div style={{background: T.paper, padding: `${padT}px 34px ${padB}px`, fontFamily: STATION, color: T.ink, whiteSpace: 'nowrap',
          fontSize: fs, lineHeight: `${lh}px`, overflow: 'hidden'}}>
          <div style={{fontWeight: 600}}>{lines[0]}</div>
          <div style={{fontWeight: 500, marginTop: gap, opacity: in2}}>{lines[1]}</div>
        </div>
      </div>
    </Frame>
  );
};
