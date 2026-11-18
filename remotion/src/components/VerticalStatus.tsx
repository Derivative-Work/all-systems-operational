// The vertical cut's status panel (human interventions 47): the made-up status page at phone width, its rows following
// the song (config/vertical_status.json): "We are aware ... everything" turns them to Investigating one by one, "Early
// signs of stabilization" turns them all, the mail comes back on "open up the mail", and "We're seeing renewed errors"
// turns them red. The banner never changes. Frame 0 is the cut's first frame (video time t0).
import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {INCIDENT, STAMP} from '../config';
import {UI} from '../Fonts';
import {T} from '../theme';
import {clamp, Frame} from './Common';
import {BANNER, Check, OPERATIONAL, SERVICES} from './StatusPage';
import plan from '../../../config/vertical_status.json';

type State = 'ok' | 'investigating' | 'stabilizing' | 'renewed';
const LOOK: Record<State, {label: string; c: string; soft: string}> = {
  ok: {label: OPERATIONAL, c: T.ok, soft: T.okSoft},
  investigating: {label: INCIDENT.statusPhrases[0], c: T.warn, soft: T.warnSoft},
  stabilizing: {label: INCIDENT.statusPhrases[1], c: T.warn, soft: T.warnSoft},
  renewed: {label: INCIDENT.statusPhrases[2], c: T.bad, soft: T.badSoft},
};

// each row's changes: [time, state], in order
const CHANGES: Record<string, [number, State][]> = Object.fromEntries(SERVICES.map((name) => {
  const out: [number, State][] = [[-1e9, ((plan.initial as Record<string, string>)[name] ?? 'ok') as State]];
  for (const e of plan.events) {
    const rows = e.rows === 'all' ? SERVICES : (e.rows as string[]);
    const i = rows.indexOf(name);
    if (i >= 0) out.push([e.t + i * ((e as {stagger_s?: number}).stagger_s ?? 0), e.state as State]);
  }
  return [name, out];
}));

const Tile: React.FC<{name: string; t: number; wide?: boolean}> = ({name, t, wide}) => {
  const {fps} = useVideoConfig();
  const ch = CHANGES[name].filter(([at]) => at <= t);
  const [at, state] = ch[ch.length - 1];
  const look = LOOK[state];
  const flash = ch.length > 1 ? interpolate((t - at) * fps, [0, 8], [1, 0], clamp) : 0;
  return (
    <div style={{gridColumn: wide ? '1 / span 2' : undefined, background: flash ? `rgba(255,214,120,${0.55 * flash})` : '#fff',
      borderRadius: 12, border: '1px solid #dfe2dc', padding: '6px 14px', display: 'flex', flexDirection: wide ? 'row' : 'column',
      alignItems: wide ? 'center' : 'flex-start', justifyContent: wide ? 'space-between' : 'center', gap: wide ? 0 : 2}}>
      <div style={{fontSize: 19, fontWeight: 600}}>{name}</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 7, color: look.c, fontSize: 15, fontWeight: 600}}>
        <div style={{width: 9, height: 9, borderRadius: '50%', background: look.c, boxShadow: `0 0 6px ${look.c}`}} />
        {look.label}
      </div>
    </div>
  );
};

export const VerticalStatus: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = plan.t0 + f / fps;
  return (
    <Frame bg="#eef0ec">
      <div style={{position: 'absolute', inset: 0, fontFamily: UI, color: T.ink}}>
        <div style={{height: 40, background: '#fff', borderBottom: '1px solid #dfe2dc', display: 'flex', alignItems: 'center',
          padding: '0 24px', gap: 12}}>
          <svg width={24} height={24} viewBox="0 0 42 42"><circle cx={21} cy={21} r={17} fill="none" stroke={T.ink} strokeWidth={5} /><circle cx={21} cy={21} r={6} fill={T.ink} /></svg>
          <div style={{fontSize: 21, fontWeight: 700}}>Service status</div>
          <div style={{marginLeft: 'auto', fontSize: 14, color: T.inkSoft}}>{STAMP}</div>
        </div>
        <div style={{width: 672, margin: '10px auto 0'}}>
          <div style={{background: T.ok, color: '#fff', borderRadius: 14, padding: '14px 22px', display: 'flex', alignItems: 'center', gap: 16,
            fontSize: 36, fontWeight: 700}}><Check size={42} />{BANNER}</div>
          <div style={{marginTop: 10, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 7}}>
            {SERVICES.map((name, i) => <Tile key={name} name={name} t={t} wide={i === SERVICES.length - 1} />)}
          </div>
        </div>
      </div>
    </Frame>
  );
};
