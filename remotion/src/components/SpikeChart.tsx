// O01, beat 1: the outage-report spike as a made-up, unlabeled chart (brief). Drawn from reported outage-tracker
// counts for Thu Nov 12, Pacific time (production log 4): GV Wire's rolling update 9:50-10:17 a.m. and Al Jazeera's
// 43,000 at about 07:00 GMT Friday (11:00 p.m. PT Thursday, 2 a.m. ET Friday). Labels are ET (see clock). GV Wire's 550,000/600,000 are uncorroborated: left out.
// No tracker's branding, colours or layout: a dark chart, one orange line, a broken time axis (the climb is 27
// minutes, the tail 13 hours), and no counts between 10:17 a.m. and 11 p.m., so that stretch is a straight dashed
// line. Counts are shown as reported ("2,400+"), never interpolated.
import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {STATION, UI} from '../Fonts';
import {T} from '../theme';
import {clamp, Frame} from './Common';

/** [minutes after midnight PT, reported count] */
export const CLIMB: [number, number][] = [
  [9 * 60 + 50, 2400], [9 * 60 + 53, 5500], [9 * 60 + 58, 13000], [10 * 60 + 3, 25000], [10 * 60 + 8, 65000], [10 * 60 + 17, 130000],
];
export const TAIL: [number, number] = [23 * 60, 43000];

const X0 = 230, X_BREAK = 1330, X1 = 1700, Y0 = 250, Y1 = 900, YMAX = 150000;
const T0 = 9 * 60 + 45, T_BREAK = 10 * 60 + 25;
const xOf = (m: number) => (m <= T_BREAK ? X0 + ((m - T0) / (T_BREAK - T0)) * (X_BREAK - X0) : X1 - 60);
const yOf = (v: number) => Y1 - (v / YMAX) * (Y1 - Y0);
const fmt = (v: number) => Math.round(v).toLocaleString('en-US');
// Data stay in PT as reported; labels show ET (+3 h), like every other timestamp in the opening (the screenshot
// captions, the creator's thread from 12:57 p.m. ET) and the fact card's Washington Post line ("just after 1 p.m.").
const ET = 180;
const clock = (pt: number) => { const m = pt + ET, h = Math.floor(m / 60) % 24; return `${h > 12 ? h - 12 : h}:${String(m % 60).padStart(2, '0')}`; };

const valueAt = (m: number) => {
  if (m <= CLIMB[0][0]) return CLIMB[0][1];
  for (let i = 1; i < CLIMB.length; i++) {
    const [ta, va] = CLIMB[i - 1], [tb, vb] = CLIMB[i];
    if (m <= tb) return va + ((m - ta) / (tb - ta)) * (vb - va);
  }
  return CLIMB[CLIMB.length - 1][1];
};

export const SpikeChart: React.FC = () => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  // the climb draws over the first ~60% of the beat, the dashed tail after it
  const climbEnd = Math.round(d * 0.62);
  const tNow = interpolate(f, [3, climbEnd], [CLIMB[0][0], CLIMB[CLIMB.length - 1][0]], {...clamp, easing: Easing.in(Easing.quad)});
  const tail = interpolate(f, [climbEnd + 2, d - 6], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const pts = CLIMB.filter(([t]) => t <= tNow).map(([t, v]) => [xOf(t), yOf(v)]);
  const head = [xOf(tNow), yOf(valueAt(tNow))];
  const path = [...pts, head].map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
  const last = CLIMB[CLIMB.length - 1];
  const [lx, ly] = [xOf(last[0]), yOf(last[1])];
  const [tx, ty] = [xOf(TAIL[0]), yOf(TAIL[1])];
  // the hero number only ever shows a reported count (the last one the line has passed), never an interpolation
  const hero = CLIMB.filter(([t]) => t <= tNow + 1e-6).slice(-1)[0][1];
  const xTicks = [9 * 60 + 50, 10 * 60, 10 * 60 + 10, 10 * 60 + 20];
  return (
    <Frame bg={T.chartBg}>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {/* recessive grid */}
        {[0, 50000, 100000, 150000].map((v) => (
          <g key={v}>
            <line x1={X0} x2={X1} y1={yOf(v)} y2={yOf(v)} stroke={T.chartGrid} strokeWidth={v ? 1.5 : 2.5} />
            <text x={X0 - 22} y={yOf(v) + 9} textAnchor="end" fill={T.chartAxis} fontFamily={UI} fontSize={26}>{v ? `${v / 1000}k` : '0'}</text>
          </g>
        ))}
        {xTicks.map((m) => (
          <text key={m} x={xOf(m)} y={Y1 + 48} textAnchor="middle" fill={T.chartAxis} fontFamily={UI} fontSize={26}>{clock(m)}</text>
        ))}
        {/* the axis break */}
        <g stroke={T.chartAxis} strokeWidth={2.5}>
          <line x1={X_BREAK + 4} y1={Y1 + 14} x2={X_BREAK + 18} y2={Y1 - 14} />
          <line x1={X_BREAK + 18} y1={Y1 + 14} x2={X_BREAK + 32} y2={Y1 - 14} />
        </g>
        <text x={tx} y={Y1 + 48} textAnchor="middle" fill={T.chartAxis} fontFamily={UI} fontSize={26}>2 a.m. Fri</text>
        {/* the dashed tail: no counts between 10:17 a.m. and 11 p.m. */}
        {tail > 0 && (
          <path d={`M${lx},${ly} L${tx},${ty}`} fill="none" stroke={T.chartLine} strokeWidth={4}
            strokeDasharray="12 12" opacity={0.7} clipPath="url(#tailclip)" />
        )}
        <defs>
          <clipPath id="tailclip"><rect x={lx} y={0} width={(tx - lx + 20) * tail} height={1080} /></clipPath>
          <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor={T.chartLine} stopOpacity={0.28} />
            <stop offset="1" stopColor={T.chartLine} stopOpacity={0} />
          </linearGradient>
        </defs>
        <path d={`${path} L${head[0]},${Y1} L${xOf(CLIMB[0][0])},${Y1} Z`} fill="url(#fill)" />
        <path d={path} fill="none" stroke={T.chartLine} strokeWidth={5} strokeLinejoin="round" strokeLinecap="round" />
        {pts.map(([x, y], i) => <circle key={i} cx={x} cy={y} r={7} fill={T.chartLine} stroke={T.chartBg} strokeWidth={3} />)}
        {tail > 0.98 && <circle cx={tx} cy={ty} r={8} fill={T.chartLine} stroke={T.chartBg} strokeWidth={3} />}
        {tail > 0.98 && <text x={tx} y={ty - 26} textAnchor="middle" fill="#e9ecef" fontFamily={UI} fontSize={28} fontWeight={600}>43,000+</text>}
      </svg>
      {/* hero number */}
      <div style={{position: 'absolute', left: X0, top: 70, color: '#f4f5f6', fontFamily: STATION}}>
        <div style={{fontSize: 30, fontWeight: 500, color: T.chartAxis, letterSpacing: 0.5}}>Outage reports · Thursday, Nov 12 · Eastern time</div>
        <div style={{fontSize: 108, fontWeight: 700, lineHeight: 1.05, fontVariantNumeric: 'tabular-nums'}}>{fmt(hero)}+</div>
      </div>
      <div style={{position: 'absolute', left: X0, bottom: 44, color: T.chartAxis, fontFamily: UI, fontSize: 24}}>
        Reconstructed from reported outage-tracker counts (GV Wire, Al Jazeera)
      </div>
    </Frame>
  );
};
