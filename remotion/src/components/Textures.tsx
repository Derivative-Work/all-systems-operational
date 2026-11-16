// Textures for the Blender sets, each at its own size (Root.tsx): the kick-drum head (O09), the cafe table tent
// (O14), the band Polaroid (O14), the ON AIR sign (O10/O12), the station sign, and the treehouse whiteboard (O18).
import React from 'react';
import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Branch, INCIDENT} from '../config';
import {HAND, STATION, UI} from '../Fonts';
import {T} from '../theme';
import {clamp, Frame} from './Common';

/* ---------- kick-drum head, round, transparent outside the head ---------- */
export const KICK = 2048;
export const KickDrumHead: React.FC<{lgtm?: boolean}> = ({lgtm = INCIDENT.branch === 'B'}) => (
  <Frame>
    <div style={{position: 'absolute', inset: 0, borderRadius: '50%', overflow: 'hidden',
      background: 'radial-gradient(circle at 45% 40%, #fbf6ea 0%, #f1e8d6 60%, #e2d6bf 100%)', fontFamily: STATION, color: T.ink}}>
      <div style={{position: 'absolute', inset: 70, borderRadius: '50%', border: `14px solid ${T.evergreen}`}} />
      <div style={{position: 'absolute', inset: 110, borderRadius: '50%', border: `4px solid ${T.coral}`}} />
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{fontSize: 210, fontWeight: 600, letterSpacing: 40, marginRight: -40, color: T.evergreen}}>SESSION</div>
        <div style={{fontSize: 620, fontWeight: 700, lineHeight: 0.9, letterSpacing: -20, color: T.ink}}>503</div>
        <div style={{width: 760, height: 14, background: T.coral, borderRadius: 7, marginTop: 50}} />
      </div>
      {lgtm && (
        <div style={{position: 'absolute', left: 1240, top: 1380, transform: 'rotate(-14deg)', background: '#fff', border: '10px solid #2b6cb0',
          borderRadius: 40, padding: '20px 56px', fontFamily: UI, fontSize: 150, fontWeight: 800, color: '#2b6cb0'}}>LGTM</div>
      )}
    </div>
  </Frame>
);

/* ---------- table tent (one face) ---------- */
export const TENT = {w: 1600, h: 1100};
export const TableTent: React.FC = () => (
  <Frame bg={T.paper}>
    <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 60, background: T.evergreen}} />
    <div style={{position: 'absolute', inset: '60px 0 0', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      fontFamily: STATION, color: T.ink}}>
      {/* an unplugged plug */}
      <svg width={260} height={130} viewBox="0 0 260 130">
        <g fill="none" stroke={T.coral} strokeWidth={12} strokeLinecap="round" strokeLinejoin="round">
          <path d="M10 65 H70" /><rect x={70} y={35} width={50} height={60} rx={10} /><path d="M120 50 H138 M120 80 H138" />
          <path d="M250 65 H190" /><rect x={150} y={35} width={40} height={60} rx={10} />
        </g>
      </svg>
      <div style={{fontSize: 150, fontWeight: 600, lineHeight: 1.05, textAlign: 'center', marginTop: 40, letterSpacing: -2}}>connector<br />unavailable</div>
      <div style={{fontSize: 44, fontWeight: 500, letterSpacing: 6, textTransform: 'uppercase', color: T.evergreen, marginTop: 60}}>Session 503 · on the road</div>
    </div>
  </Frame>
);

/* ---------- Polaroid of the band (frame + caption; the photo is a Blender render later) ---------- */
export const POLAROID = {w: 1200, h: 1440};
export const Polaroid: React.FC<{photo?: string}> = ({photo}) => (
  <Frame bg="#fbfaf6">
    <div style={{position: 'absolute', left: 60, top: 60, width: 1080, height: 1080, overflow: 'hidden',
      background: photo ? '#000' : 'repeating-linear-gradient(45deg, #cfc8bc 0 40px, #c6bfb2 40px 80px)'}}>
      {photo && <Img src={staticFile(photo)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />}
    </div>
    <div style={{position: 'absolute', left: 0, right: 0, top: 1170, textAlign: 'center', fontFamily: HAND, fontSize: 170, fontWeight: 600,
      color: '#2d3a8c', transform: 'rotate(-2deg)'}}>Wed 11/11</div>
  </Frame>
);

/* ---------- ON AIR sign (lit and unlit) ---------- */
export const ONAIR = {w: 1600, h: 640};
export const OnAirSign: React.FC<{lit: boolean}> = ({lit}) => (
  <Frame bg={lit ? 'radial-gradient(ellipse at 50% 50%, #ff5a46 0%, #d8352a 55%, #a3221b 100%)' : 'linear-gradient(#3c1916, #2c1210)'}>
    <div style={{position: 'absolute', inset: 30, border: `8px solid ${lit ? 'rgba(255,230,220,0.55)' : 'rgba(120,70,64,0.5)'}`, borderRadius: 30}} />
    <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: STATION, fontSize: 330,
      fontWeight: 700, letterSpacing: 24, color: lit ? '#fff7ef' : '#6e3d37',
      textShadow: lit ? '0 0 30px rgba(255,240,220,0.9), 0 0 80px rgba(255,180,150,0.8)' : 'none'}}>ON AIR</div>
  </Frame>
);

/* ---------- station sign ---------- */
export const SIGN = {w: 2000, h: 1000};
export const StationSign: React.FC = () => (
  <Frame bg={T.evergreen}>
    <div style={{position: 'absolute', inset: 40, border: `6px solid ${T.paper}`, borderRadius: 40, opacity: 0.5}} />
    <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      fontFamily: STATION, color: T.paper}}>
      <div style={{display: 'flex', alignItems: 'baseline', gap: 40}}>
        <span style={{fontSize: 440, fontWeight: 700, letterSpacing: -14, lineHeight: 1}}>50.3</span>
        <span style={{fontSize: 200, fontWeight: 600, color: '#f6b49d'}}>FM</span>
      </div>
      <div style={{fontSize: 70, fontWeight: 500, letterSpacing: 10, textTransform: 'uppercase', marginTop: 40}}>listener-supported radio</div>
    </div>
  </Frame>
);

/* ---------- whiteboard (O18), handwriting that fills in ---------- */
export const BOARD = {w: 2400, h: 1500};
/** Lyrics v1.3 (brief rev 141): the board paraphrases Microsoft's preliminary report (Nov 15) in a few words, in the
 * order of the bridge's lines; the report's own words are never copied onto it. Microsoft's Nov 13 line is quoted
 * (MacRumors), and the on-screen denial tags (DenialTags, LowerThird.tsx) credit and date it. */
export const DENIAL = 'not related to cyber or AI / agents';
export const TESTED = 'tested on smaller machines';
export const REPORT_DUE = 'Nov 20';
/** Branch A circles this phrase of the root cause: "the whole singalong over one fix" (brief, report branches). */
export const CIRCLED = 'July fix';

type Seg = {text: string; color: string; size: number; indent?: number; key: string};
export const boardSegments = (inc = INCIDENT, branch: Branch = inc.branch): Seg[] => {
  const ink = '#1f3f8f', red = '#b8322a', black = '#24282c';
  const segs: Seg[] = [
    {key: 'rc-l', text: 'Root cause: ', color: red, size: 100},
    {key: 'rc', text: inc.rootCause, color: ink, size: 90},
    {key: 'rt', text: `↳ ${TESTED}`, color: ink, size: 80, indent: 60},
    {key: 'cf-l', text: 'Contributing factors:', color: red, size: 100},
  ];
  inc.contributingFactors.forEach((cf, i) => segs.push({key: `cf${i}`, text: `– ${cf}`, color: ink, size: 86, indent: 60}));
  // branch B cuts the denial line from the bridge (brief), so the board drops it too
  if (branch !== 'B') segs.push({key: 'nr', text: `“${DENIAL}”`, color: black, size: 86, indent: 60});
  segs.push({key: 'll', text: 'Lessons learned:', color: red, size: 100});
  segs.push({key: 'fr-l', text: 'Full report: ', color: red, size: 100});
  segs.push({key: 'fr', text: branch === 'C' ? 'to follow' : REPORT_DUE, color: ink, size: 90});
  return segs;
};

/** `fill` 0..1 writes the board in, character by character; branch C ends the root cause in a blinking cursor;
 * branch A circles CIRCLED in the root cause once it is written (reveal key 'circle', else when the board is full).
 * `reveal` maps a segment key to [start frame, end frame]: that segment is written in over its own window, on the
 * sung line's cue (the board's order isn't the bridge's: lessons learned is sung after the full report). With
 * `reveal`, segments without a window stay blank. `only` (review) shows just those segments, fully written. */
export const Whiteboard: React.FC<{fill: number; branch?: Branch; caption?: boolean; reveal?: Record<string, [number, number]>; only?: string[]}> = ({
  fill, branch = INCIDENT.branch, caption = true, reveal, only,
}) => {
  const f = useCurrentFrame();
  const segs = boardSegments(INCIDENT, branch);
  const total = segs.reduce((n, s) => n + s.text.length, 0);
  let budget = Math.round(fill * total);
  const shown = only
    ? segs.map((s) => (only.includes(s.key) ? s.text.length : 0))
    : reveal
      ? segs.map((s) => { const w = reveal[s.key]; return w ? Math.round(interpolate(f, w, [0, s.text.length], clamp)) : 0; })
      : segs.map((s) => { const n = Math.max(0, Math.min(s.text.length, budget)); budget -= s.text.length; return n; });
  const blink = Math.floor(f / 12) % 2 === 0;
  const idx = (k: string) => segs.findIndex((s) => s.key === k);
  const span = (i: number) => {
    if (i < 0) return null;
    const s = segs[i];
    return <span key={s.key} style={{color: s.color, fontSize: s.size}}>{s.text.slice(0, shown[i])}</span>;
  };
  // the root cause, with CIRCLED drawn round in red marker (branch A) once its words are written
  const rcI = idx('rc');
  const rc = segs[rcI], rcN = shown[rcI], at = rc.text.indexOf(CIRCLED);
  const rcDone = rcN === rc.text.length;
  const circleP = branch !== 'A' || at < 0 ? 0
    : only ? (only.includes('circle') ? 1 : 0)
      : reveal ? (reveal.circle ? interpolate(f, reveal.circle, [0, 1], clamp) : 0)
        : (fill >= 1 ? 1 : 0);
  const rcSpan = at < 0 ? span(rcI) : (
    <span key="rc" style={{color: rc.color, fontSize: rc.size}}>
      {rc.text.slice(0, Math.min(rcN, at))}
      <span style={{position: 'relative', display: 'inline-block'}}>
        {rc.text.slice(at, Math.max(at, Math.min(rcN, at + CIRCLED.length)))}
        {circleP > 0 && (() => {
          // a hand-drawn loop round the words, in pixels (Caveat runs about 0.33 em a character): an ellipse that
          // overshoots its start, drawn in as the marker moves
          const w = CIRCLED.length * 0.33 * rc.size + 44, h = rc.size * 1.35;
          const P = (x: number, y: number) => `${(x / 100 * w).toFixed(1)} ${(y / 100 * h).toFixed(1)}`;
          const d = `M ${P(10, 22)} C ${P(34, -4)}, ${P(90, -2)}, ${P(98, 40)} C ${P(102, 86)}, ${P(36, 104)}, ${P(8, 80)} `
            + `C ${P(-4, 62)}, ${P(0, 30)}, ${P(28, 10)}`;
          return (
            <svg style={{position: 'absolute', left: -24, top: -0.16 * rc.size, overflow: 'visible'}} width={w} height={h}>
              <path d={d} fill="none" stroke="#b8322a" strokeWidth={7} strokeLinecap="round" pathLength={1}
                strokeDasharray="1 1" strokeDashoffset={1 - circleP} />
            </svg>
          );
        })()}
      </span>
      {rcN > at + CIRCLED.length ? rc.text.slice(at + CIRCLED.length, rcN) : ''}
    </span>
  );
  const lines: React.ReactNode[] = [];
  lines.push(<div key="l-rc">{span(idx('rc-l'))}{rcSpan}
    {branch === 'C' && rcDone && <span style={{display: 'inline-block', width: 10, height: 80, background: '#1f3f8f', marginLeft: 10,
      verticalAlign: '-8px', opacity: blink ? 1 : 0}} />}</div>);
  lines.push(<div key="l-rt" style={{paddingLeft: segs[idx('rt')].indent}}>{span(idx('rt'))}</div>);
  lines.push(<div key="l-cf" style={{marginTop: 30}}>{span(idx('cf-l'))}</div>);
  segs.forEach((s, i) => {
    if (/^cf\d/.test(s.key)) lines.push(<div key={`l-${s.key}`} style={{paddingLeft: s.indent}}>{span(i)}</div>);
  });
  if (idx('nr') >= 0) lines.push(<div key="l-nr" id="board-nr" style={{paddingLeft: segs[idx('nr')].indent}}>{span(idx('nr'))}</div>);
  lines.push(<div key="l-ll" style={{marginTop: 30}}>{span(idx('ll'))}</div>);
  lines.push(<div key="l-fr" style={{marginTop: 30}}>{span(idx('fr-l'))}{span(idx('fr'))}</div>);
  return (
    <Frame bg="#b9bdc0">
      <div style={{position: 'absolute', inset: 34, background: 'linear-gradient(160deg, #fdfdfb 0%, #f2f3f1 60%, #e9ebe9 100%)', borderRadius: 8,
        boxShadow: 'inset 0 0 40px rgba(0,0,0,0.08)'}}>
        <div style={{position: 'absolute', inset: '80px 130px', fontFamily: HAND, fontWeight: 600, lineHeight: 1.1}}>{lines}</div>
        {caption && (
          <div style={{position: 'absolute', right: 40, bottom: 34, fontFamily: UI, fontSize: 40, fontWeight: 500, color: '#3b4146',
            background: '#fff', border: '2px solid #c9cdd0', borderRadius: 10, padding: '6px 18px'}}>dramatization</div>
        )}
      </div>
      {/* marker tray */}
      <div style={{position: 'absolute', left: 300, right: 300, bottom: 0, height: 24, background: '#9a9fa3', borderRadius: '6px 6px 0 0'}} />
    </Frame>
  );
};
