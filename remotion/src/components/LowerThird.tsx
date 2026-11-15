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

export const LowerThird: React.FC<{variant: LowerThirdVariant; echoEvery?: number}> = ({variant, echoEvery = 72}) => {
  const f = useCurrentFrame();
  const inP = interpolate(f, [0, 10], [0, 1], clamp);
  let body: React.ReactNode, kicker: string | undefined, right: React.ReactNode;
  if (variant === 'title' || variant === 'uptime') {
    body = <div style={{fontSize: 48, fontWeight: 600}}>{TITLE}<span style={{fontWeight: 400, color: T.inkSoft}}> · {SUBTITLE}</span></div>;
    if (variant === 'uptime') {
      // the ticker rolls up and settles at 99.9%
      const v = interpolate(f, [8, 40], [98.2, 99.9], clamp);
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
    const i = Math.min(ECHOES.length - 1, Math.floor(f / echoEvery));
    const pop = interpolate(f - i * echoEvery, [0, 6], [0, 1], clamp);
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
  return (
    <Frame>
      <Bug />
      <Panel inP={inP} kicker={kicker} right={right}>{body}</Panel>
    </Frame>
  );
};
