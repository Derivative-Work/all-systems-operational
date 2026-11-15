// O02/O13/O23: the made-up, unlabeled status page (brief). No company name, logo or real layout; generic service
// names. Every row is stamped with the same stale time ("a page that can't load can't update"), and the banner never
// changes, whatever the rows say. Status words come from config/incident.json (statusPhrases).
import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {INCIDENT, rng, STAMP} from '../config';
import {UI} from '../Fonts';
import {T} from '../theme';
import {clamp, Frame} from './Common';

export const SERVICES = ['Mail', 'Calendar', 'Chat', 'Meetings', 'Files', 'Sign-in', 'Assistant'];
export const BANNER = 'All systems operational';
export const OPERATIONAL = 'Operational';

export type StatusState = 'allGreen' | 'investigating' | 'renewedErrors' | 'flicker';
type Look = {label: string; c: string; soft: string};
const GREEN: Look = {label: OPERATIONAL, c: T.ok, soft: T.okSoft};

const Check: React.FC<{size: number; c?: string}> = ({size, c = '#fff'}) => (
  <svg width={size} height={size} viewBox="0 0 24 24"><circle cx={12} cy={12} r={11} fill="none" stroke={c} strokeWidth={2} />
    <path d="M7 12.5 L10.5 16 L17 8.5" fill="none" stroke={c} strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" /></svg>
);

const Pill: React.FC<{look: Look; dim?: number}> = ({look, dim = 0}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 14, padding: '10px 22px', borderRadius: 999, background: look.soft,
    color: look.c, fontSize: 26, fontWeight: 600, opacity: 1 - dim}}>
    <div style={{width: 16, height: 16, borderRadius: '50%', background: look.c, boxShadow: dim ? 'none' : `0 0 10px ${look.c}`}} />
    {look.label}
  </div>
);

export const StatusPage: React.FC<{state: StatusState; flipAt?: number; row?: number}> = ({state, flipAt, row = 0}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  const at = flipAt ?? Math.round(d / 2);
  const flicker = rng(23);
  // a seeded flicker: the green row stutters in short dips (O23)
  const dips = Array.from({length: 40}, () => flicker() < 0.3);
  return (
    <Frame bg="#eef0ec">
      <div style={{position: 'absolute', inset: 0, fontFamily: UI, color: T.ink}}>
        <div style={{height: 92, background: '#fff', borderBottom: '1px solid #dfe2dc', display: 'flex', alignItems: 'center', padding: '0 120px', gap: 22}}>
          <svg width={42} height={42} viewBox="0 0 42 42"><circle cx={21} cy={21} r={17} fill="none" stroke={T.ink} strokeWidth={5} /><circle cx={21} cy={21} r={6} fill={T.ink} /></svg>
          <div style={{fontSize: 36, fontWeight: 700}}>Service status</div>
        </div>
        <div style={{width: 1500, margin: '36px auto 0'}}>
          <div style={{background: T.ok, color: '#fff', borderRadius: 18, padding: '26px 40px', display: 'flex', alignItems: 'center', gap: 24,
            fontSize: 46, fontWeight: 700}}><Check size={54} />{BANNER}</div>
          <div style={{marginTop: 26, background: '#fff', borderRadius: 18, border: '1px solid #dfe2dc', overflow: 'hidden'}}>
            {SERVICES.map((name, i) => {
              let look = GREEN, dim = 0, flash = 0;
              if (i === row) {
                if (state === 'investigating' && f >= at) {
                  look = {label: INCIDENT.statusPhrases[0], c: T.warn, soft: T.warnSoft};
                  flash = interpolate(f, [at, at + 8], [1, 0], clamp);
                }
                if (state === 'renewedErrors') {
                  look = {label: INCIDENT.statusPhrases[2], c: T.bad, soft: T.badSoft};
                  flash = interpolate(f, [4, 12], [1, 0], clamp);
                }
                if (state === 'flicker') dim = dips[Math.floor(f / 3) % dips.length] ? 0.75 : 0;
              }
              return (
                <div key={name} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '13px 40px',
                  borderTop: i ? '1px solid #eceee9' : 'none', background: flash ? `rgba(255,214,120,${0.45 * flash})` : undefined}}>
                  <div>
                    <div style={{fontSize: 32, fontWeight: 600}}>{name}</div>
                    <div style={{fontSize: 21, color: T.inkSoft, marginTop: 2}}>{STAMP}</div>
                  </div>
                  <Pill look={look} dim={dim} />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </Frame>
  );
};
