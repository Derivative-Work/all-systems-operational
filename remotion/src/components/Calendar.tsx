// O05: full-frame phone, a work-week calendar on Thursday, Nov 12, its events draining away one box at a time
// ("the calendar was empty"). Invented meeting names; a generic look (no Outlook blue).
import React from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {PW, rng} from '../config';
import {UI} from '../Fonts';
import {T} from '../theme';
import {clamp} from './Common';
import {StatusBar} from './Phone';

type Ev = {day: number; start: number; end: number; title: string; tint: string};
const G = '#d7ebe3', C_ = '#f8dccf', B = '#d9e6f0', Y = '#f3ead0';
export const EVENTS: Ev[] = [
  {day: 0, start: 9, end: 9.5, title: 'Standup', tint: G}, {day: 0, start: 11, end: 12, title: 'Roadmap review', tint: B},
  {day: 0, start: 14, end: 14.5, title: '1:1', tint: C_},
  {day: 1, start: 9, end: 9.5, title: 'Standup', tint: G}, {day: 1, start: 10, end: 11.5, title: 'Design crit', tint: Y},
  {day: 1, start: 12, end: 13, title: 'Lunch & learn', tint: C_}, {day: 1, start: 15, end: 16, title: 'Vendor call', tint: B},
  {day: 2, start: 9, end: 9.5, title: 'Standup', tint: G}, {day: 2, start: 10, end: 12, title: 'Sprint planning', tint: B},
  {day: 2, start: 12, end: 13, title: 'Team lunch', tint: C_}, {day: 2, start: 14, end: 15, title: 'Customer call', tint: Y},
  {day: 3, start: 9, end: 9.5, title: 'Standup', tint: G}, {day: 3, start: 10, end: 11, title: 'Interview', tint: C_},
  {day: 3, start: 11, end: 12.5, title: 'Quarterly review', tint: B}, {day: 3, start: 13, end: 14, title: 'All-hands', tint: Y},
  {day: 3, start: 14.5, end: 15, title: '1:1', tint: C_}, {day: 3, start: 15.5, end: 17, title: 'Launch prep', tint: G},
  {day: 4, start: 9, end: 9.5, title: 'Standup', tint: G}, {day: 4, start: 11, end: 12, title: 'Retro', tint: Y},
  {day: 4, start: 14, end: 16, title: 'Focus time', tint: B},
];
const DAYS = [['Mon', 9], ['Tue', 10], ['Wed', 11], ['Thu', 12], ['Fri', 13]] as const;
const THU = 3, H0 = 9, H1 = 17; // 9 to 5, so the whole day fits the framed phone (O05)

// drain order: Thursday's afternoon first (the outage starts at 1 p.m.), then everything else in a seeded order
const r = rng(5);
const ORDER = EVENTS.map((e, i) => ({i, k: e.day === THU && e.start >= 13 ? -1 + e.start / 100 : r()}))
  .sort((a, b) => a.k - b.k).map((o) => o.i);

export const CalendarScreen: React.FC<{drainStart?: number; drainEnd?: number}> = ({drainStart, drainEnd}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  const ds = drainStart ?? 10, de = drainEnd ?? d - 14;
  const step = (de - ds) / EVENTS.length;
  const left = 150, colW = (PW - left - 30) / 5, top = 470, hourH = 112;
  return (
    <div style={{position: 'absolute', inset: 0, background: '#fcfbf8', fontFamily: UI, color: T.ink}}>
      <StatusBar time="1:04" />
      <div style={{padding: '30px 60px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
        <div style={{fontSize: 76, fontWeight: 700}}>November</div>
        <div style={{fontSize: 40, color: T.inkSoft}}>Week 46</div>
      </div>
      {/* day header */}
      <div style={{position: 'absolute', top: 300, left, display: 'flex'}}>
        {DAYS.map(([n, dt], i) => (
          <div key={n} style={{width: colW, textAlign: 'center'}}>
            <div style={{fontSize: 32, color: i === THU ? T.coral : T.inkSoft, fontWeight: 600}}>{n}</div>
            <div style={{margin: '8px auto 0', width: 82, height: 82, borderRadius: '50%', lineHeight: '82px', fontSize: 44, fontWeight: 600,
              background: i === THU ? T.coral : 'transparent', color: i === THU ? '#fff' : T.ink}}>{dt}</div>
          </div>
        ))}
      </div>
      {/* grid */}
      {Array.from({length: H1 - H0 + 1}, (_, k) => (
        <div key={k} style={{position: 'absolute', top: top + k * hourH, left: 0, right: 0}}>
          <div style={{position: 'absolute', left: 20, top: -18, width: left - 40, textAlign: 'right', fontSize: 28, color: T.inkFaint}}>
            {((H0 + k - 1) % 12) + 1} {H0 + k < 12 ? 'AM' : 'PM'}</div>
          <div style={{position: 'absolute', left, right: 30, top: 0, height: 2, background: '#e8e4dc'}} />
        </div>
      ))}
      {DAYS.map((_, i) => <div key={i} style={{position: 'absolute', top, left: left + i * colW, width: 2, height: (H1 - H0) * hourH, background: '#efebe4'}} />)}
      <div style={{position: 'absolute', top, left: left + THU * colW, width: colW, height: (H1 - H0) * hourH, background: 'rgba(226,100,62,0.05)'}} />
      {EVENTS.map((e, i) => {
        const at = ds + ORDER.indexOf(i) * step;
        const k = interpolate(f, [at, at + 6], [1, 0], clamp);
        if (k <= 0) return null;
        return (
          <div key={i} style={{position: 'absolute', left: left + e.day * colW + 6, top: top + (e.start - H0) * hourH + 4, width: colW - 12,
            height: (e.end - e.start) * hourH - 8, background: e.tint, borderRadius: 12, padding: '5px 12px', fontSize: 24, fontWeight: 600,
            lineHeight: 1.2, overflow: 'hidden', opacity: k, transform: `scale(${0.85 + 0.15 * k})`, color: '#26343a',
            borderLeft: `6px solid rgba(31,42,46,0.25)`}}>{e.title}</div>
        );
      })}
    </div>
  );
};
