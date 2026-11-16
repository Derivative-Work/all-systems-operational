// M7b (human interventions 19): invented incident-night content for the treehouse laptops and phones (O08c's night
// cutaway and the O18 bridge), mapped onto the Blender screens as image sequences (blender/look.py). The creator's
// guess at a plausible night, not inside information: "someone struggling to 2FA in, someone with a robo-call from a
// fake number as a stand-in for a page looking at an invented dashboard, invented code and agent screens, the generic
// video call".
// Guardrails (decisions 30): generic UIs in the video's own palette (theme.ts), no real product's name, logo, colours
// or layout; invented names; the caller ID is in the 555-0100..0199 fiction range; nothing ties AI-written code to the
// outage (the code screen is a health check, the agent only reads logs and is blocked); no cause beyond the brief's
// sources; times follow the brief (Thu Nov 12, the wider outage from 10:26 a.m. PT).
// Every screen takes `night` (O08c: late Thursday night; O18: Thursday afternoon) and `phase` (frames: where its loop
// starts, so each build's shots land on a readable beat).
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {rng} from '../config';
import {MONO, UI} from '../Fonts';
import {T} from '../theme';
import {clamp} from './Common';
import {StatusBar} from './Phone';

export type ScreenProps = {night?: boolean; phase?: number};
export const LAP = {w: 1280, h: 800};

// the clock on every screen: O08c is late Thursday night, the bridge (O18) is Thursday afternoon
const CLOCK = {night: {h: 23, m: 47}, day: {h: 14, m: 52}};
const clockAt = (night: boolean | undefined, secs: number, ampm = true) => {
  const c = night ? CLOCK.night : CLOCK.day;
  const tot = c.h * 3600 + c.m * 60 + Math.floor(secs);
  const h = Math.floor(tot / 3600) % 24;
  const m = Math.floor(tot / 60) % 60;
  const s = tot % 60;
  if (!ampm) return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  return `${((h + 11) % 12) + 1}:${String(m).padStart(2, '0')} ${h < 12 ? 'AM' : 'PM'}`;
};

// the video's palette for dark screens (theme.ts: ink, paper, evergreen, coral, the status lights)
const D = {
  bg: '#141b1e', panel: '#1c2529', panel2: '#232e33', line: '#2e3a40', text: '#e9e4da', muted: '#8e989c',
  green: '#4fb985', amber: '#e3a43a', red: '#e0574b', coral: T.coral, teal: '#5fb3b0',
};

const Spinner: React.FC<{size: number; color: string; f: number}> = ({size, color, f}) => (
  <svg width={size} height={size} viewBox="0 0 40 40" style={{transform: `rotate(${f * 18}deg)`}}>
    <circle cx={20} cy={20} r={16} fill="none" stroke={D.line} strokeWidth={5} />
    <path d="M20 4 A16 16 0 0 1 36 20" fill="none" stroke={color} strokeWidth={5} strokeLinecap="round" />
  </svg>
);

/* ---------- 1. a phone: a second-factor sign-in prompt that keeps timing out (held, seat 0) ---------- */
// One loop of 108 frames: enter the number shown on the other screen, "Verifying...", "Request timed out", Retry.
// A generic shield, no real authenticator's look.
export const TwoFactor: React.FC<ScreenProps> = ({night, phase = 0}) => {
  const f = useCurrentFrame() + phase;
  const L = 108;
  const k = Math.floor(f / L);
  const t = f % L;
  const codes = ['47', '82', '15', '63', '29', '91', '36', '58'];
  const code = codes[k % codes.length];
  const typed = t < 12 ? '' : t < 22 ? code[0] : code;
  const verifying = t >= 40 && t < 66;
  const failed = t >= 66;
  const pressed = t >= 98 && t < 104;
  const fIn = interpolate(t, [66, 72], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', inset: 0, background: D.bg, fontFamily: UI, color: D.text}}>
      <StatusBar time={clockAt(night, f / 30)} dark />
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 120}}>
        <svg width={170} height={200} viewBox="0 0 34 40">
          <path d="M17 2 L31 7 V18 C31 28 25 35 17 38 C9 35 3 28 3 18 V7 Z" fill="none" stroke={D.teal} strokeWidth={2.6} strokeLinejoin="round" />
          <circle cx={17} cy={17} r={4} fill={D.teal} /><path d="M17 20 V27" stroke={D.teal} strokeWidth={3} strokeLinecap="round" />
        </svg>
        <div style={{fontSize: 84, fontWeight: 700, marginTop: 50}}>Sign-in request</div>
        <div style={{fontSize: 48, color: D.muted, marginTop: 14}}>work account · attempt {3 + k}</div>
      </div>
      {!failed && (
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 120}}>
          <div style={{fontSize: 58, textAlign: 'center', lineHeight: 1.3, padding: '0 90px'}}>Enter the number shown on your other screen</div>
          <div style={{display: 'flex', gap: 40, marginTop: 70}}>
            {[0, 1].map((i) => (
              <div key={i} style={{width: 230, height: 280, borderRadius: 36, background: D.panel2, border: `5px solid ${verifying ? D.line : D.teal}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 190, fontWeight: 700}}>{typed[i] ?? ''}</div>
            ))}
          </div>
          {verifying && (
            <div style={{display: 'flex', alignItems: 'center', gap: 34, marginTop: 110, fontSize: 70, color: D.muted}}>
              <Spinner size={90} color={D.teal} f={f} />Verifying…
            </div>
          )}
        </div>
      )}
      {failed && (
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 130, opacity: fIn}}>
          <svg width={210} height={210} viewBox="0 0 40 40">
            <circle cx={20} cy={20} r={17} fill="none" stroke={D.red} strokeWidth={3.5} />
            <path d="M20 10 V22" stroke={D.red} strokeWidth={4} strokeLinecap="round" /><circle cx={20} cy={28.5} r={2.4} fill={D.red} />
          </svg>
          <div style={{fontSize: 118, fontWeight: 800, color: D.red, marginTop: 60, textAlign: 'center', lineHeight: 1.05}}>Request<br />timed out</div>
          <div style={{fontSize: 54, color: D.muted, marginTop: 44, textAlign: 'center', lineHeight: 1.3, padding: '0 100px'}}>
            No response from the sign-in service.
          </div>
          <div style={{marginTop: 110, width: 700, height: 170, borderRadius: 85, background: pressed ? '#3e8f8c' : D.teal, color: D.bg,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 76, fontWeight: 750,
            transform: `scale(${pressed ? 0.96 : 1})`}}>Try again</div>
        </div>
      )}
    </div>
  );
};

/* ---------- 2. a phone face up on the table, ringing: an automated alert call (the page) ---------- */
export const AlertCall: React.FC<ScreenProps> = ({night, phase = 0}) => {
  const f = useCurrentFrame() + phase;
  const ring = (f % 36) / 36;
  return (
    <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(180deg, #22302f 0%, #121a1c 70%)', fontFamily: UI, color: D.text}}>
      <StatusBar time={clockAt(night, f / 30)} dark />
      <div style={{textAlign: 'center', marginTop: 150, fontSize: 56, color: D.muted, letterSpacing: 2}}>incoming call</div>
      <div style={{textAlign: 'center', marginTop: 40, fontSize: 128, fontWeight: 800, lineHeight: 1.05}}>Automated<br />alert</div>
      <div style={{textAlign: 'center', marginTop: 50, fontSize: 84, fontWeight: 600, fontVariantNumeric: 'tabular-nums'}}>(206) 555-0147</div>
      <div style={{textAlign: 'center', marginTop: 18, fontSize: 52, color: D.muted}}>Seattle, WA</div>
      {/* the pulsing rings round a bell */}
      <div style={{position: 'absolute', left: 540, top: 1290, width: 0, height: 0}}>
        {[0, 1, 2].map((i) => {
          const r = ((ring + i / 3) % 1);
          return <div key={i} style={{position: 'absolute', left: -(120 + 260 * r), top: -(120 + 260 * r), width: 2 * (120 + 260 * r),
            height: 2 * (120 + 260 * r), borderRadius: '50%', border: `8px solid ${D.coral}`, opacity: 0.8 * (1 - r)}} />;
        })}
        <div style={{position: 'absolute', left: -120, top: -120, width: 240, height: 240, borderRadius: '50%', background: D.coral,
          display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `rotate(${12 * Math.sin(f * 1.1)}deg)`}}>
          <svg width={130} height={130} viewBox="0 0 24 24"><path d="M12 3 C8 3 6 6 6 9 V14 L4 17 H20 L18 14 V9 C18 6 16 3 12 3 Z M10 19 A2 2 0 0 0 14 19 Z"
            fill={D.bg} /></svg>
        </div>
      </div>
      {/* decline and accept */}
      {[[270, D.red, 'Decline', 135], [810, D.green, 'Accept', 0]].map(([x, c, label, rot]) => (
        <div key={label as string} style={{position: 'absolute', left: (x as number) - 115, top: 1880, width: 230, textAlign: 'center'}}>
          <div style={{width: 230, height: 230, borderRadius: '50%', background: c as string, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <svg width={120} height={120} viewBox="0 0 24 24" style={{transform: `rotate(${rot}deg)`}}>
              <path d="M6.6 10.8 C8 13.6 10.4 16 13.2 17.4 L15.4 15.2 C15.7 14.9 16.1 14.8 16.4 15 C17.5 15.4 18.7 15.6 20 15.6 C20.6 15.6 21 16 21 16.6 V20 C21 20.6 20.6 21 20 21 C10.6 21 3 13.4 3 4 C3 3.4 3.4 3 4 3 H7.5 C8.1 3 8.5 3.4 8.5 4 C8.5 5.3 8.7 6.5 9.1 7.6 C9.2 7.9 9.1 8.3 8.9 8.6 Z" fill="#fff" />
            </svg>
          </div>
          <div style={{fontSize: 50, marginTop: 24, color: D.text}}>{label}</div>
        </div>
      ))}
    </div>
  );
};

/* ---------- 3. a laptop: an invented service-health dashboard, the 5xx rate spiking, tiles going red ---------- */
const TILES: [string, 'down' | 'degraded' | 'ok', number][] = [
  // [service, final state, frame it turns (from phase 0), before that: degraded]
  ['mailflow-west', 'down', -1], ['authn-edge', 'down', 40], ['cal-sync', 'down', 150],
  ['files-api', 'ok', -1], ['connector-hub', 'down', 300], ['search-idx', 'degraded', -1],
];
export const Dashboard: React.FC<ScreenProps> = ({night, phase = 0}) => {
  const f = useCurrentFrame() + phase;
  const r = rng(503);
  // the 5xx rate from 09:00 to now, one point per 5 minutes: ~0.3% before 09:50, a climb to 10:26, then high with noise
  const endMin = night ? (23 - 9) * 60 + 47 : (14 - 9) * 60 + 52;
  const pts: [number, number][] = [];
  for (let m = 0; m <= endMin; m += 5) {
    const climb = interpolate(m, [50, 86, 92], [0.3, 18, 36], clamp);
    const tail = m > 92 ? 30 + 7 * Math.sin(m / 23) + 4 * Math.sin(m / 7.3) : climb;
    pts.push([m, Math.max(0.2, tail + (r() - 0.5) * (m > 50 ? 5 : 0.3))]);
  }
  const live = 31 + 4 * Math.sin(f / 9) + 2.5 * Math.sin(f / 3.7);
  pts.push([endMin + 2, live]);
  const W = 780, H = 470, X0 = 70, Y0 = 70;
  const xs = (m: number) => X0 + (m / (endMin + 2)) * (W - X0 - 20);
  const ys = (v: number) => Y0 + H - 50 - (v / 40) * (H - 90);
  const path = pts.map(([m, v], i) => `${i ? 'L' : 'M'}${xs(m).toFixed(1)} ${ys(v).toFixed(1)}`).join(' ');
  const ticks = [];
  for (let h = 9; h * 60 - 540 <= endMin; h += night ? 3 : 1) ticks.push(h);
  return (
    <div style={{position: 'absolute', inset: 0, background: D.bg, fontFamily: UI, color: D.text}}>
      <div style={{height: 70, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 34px', background: D.panel,
        borderBottom: `2px solid ${D.line}`}}>
        <div style={{fontSize: 30, fontWeight: 700}}>service health <span style={{color: D.muted, fontWeight: 500}}>· prod-west</span></div>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, fontSize: 26}}>
          <span style={{background: D.red, color: '#fff', borderRadius: 999, padding: '4px 16px', fontWeight: 700}}>sev 1 open</span>
          <span style={{color: D.muted}}>{clockAt(night, f / 30)} PT</span>
        </div>
      </div>
      <svg width={820} height={560} style={{position: 'absolute', left: 20, top: 90}}>
        <text x={X0} y={44} fill={D.text} fontSize={34} fontWeight={700} fontFamily={UI}>5xx error rate</text>
        <text x={X0 + 300} y={44} fill={D.red} fontSize={46} fontWeight={800} fontFamily={UI}>{live.toFixed(1)}%</text>
        {[0, 10, 20, 30, 40].map((v) => (
          <g key={v}><line x1={X0} x2={W} y1={ys(v)} y2={ys(v)} stroke={D.line} strokeWidth={1.5} />
            <text x={X0 - 12} y={ys(v) + 8} fill={D.muted} fontSize={22} textAnchor="end" fontFamily={UI}>{v}%</text></g>
        ))}
        <line x1={X0} x2={W} y1={ys(5)} y2={ys(5)} stroke={D.amber} strokeWidth={2} strokeDasharray="8 8" />
        <path d={`${path} L${xs(endMin + 2)} ${ys(0)} L${xs(0)} ${ys(0)} Z`} fill={D.coral} opacity={0.18} />
        <path d={path} fill="none" stroke={D.coral} strokeWidth={4.5} strokeLinejoin="round" />
        <circle cx={xs(endMin + 2)} cy={ys(live)} r={9} fill={D.coral} opacity={0.6 + 0.4 * Math.sin(f / 4)} />
        {ticks.map((h) => (
          <text key={h} x={xs(h * 60 - 540)} y={ys(0) + 34} fill={D.muted} fontSize={22} textAnchor="middle" fontFamily={UI}>
            {String(h).padStart(2, '0')}:00</text>
        ))}
      </svg>
      <div style={{position: 'absolute', left: 860, top: 100, width: 390, display: 'grid', gridTemplateColumns: '1fr', gap: 14}}>
        {TILES.map(([name, fin, at]) => {
          const st = at < 0 || f >= at ? fin : 'degraded';
          const c = st === 'down' ? D.red : st === 'degraded' ? D.amber : D.green;
          const flash = at >= 0 && f >= at && f < at + 12 ? 1 : 0;
          return (
            <div key={name} style={{height: 96, borderRadius: 14, background: flash ? '#3a2422' : D.panel, borderLeft: `14px solid ${c}`,
              display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px'}}>
              <span style={{fontSize: 30, fontWeight: 650}}>{name}</span>
              <span style={{fontSize: 26, fontWeight: 750, color: c, textTransform: 'uppercase', letterSpacing: 1}}>{st}</span>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 90, top: 680, fontSize: 24, color: D.muted}}>
        retries per minute <span style={{color: D.text, fontWeight: 700}}>{Math.round(41000 + 3000 * Math.sin(f / 11))}</span>
        <span style={{marginLeft: 46}}>p95 latency <span style={{color: D.amber, fontWeight: 700}}>{(4.6 + 0.4 * Math.sin(f / 7)).toFixed(1)} s</span></span>
      </div>
    </div>
  );
};

/* ---------- 4. a laptop: a terminal running a health check against the mail tier (503s, timeouts, retries) ---------- */
const SVCS = ['mailflow-west', 'mailflow-west', 'mailflow-west', 'authn-edge', 'cal-sync', 'connector-hub'];
export const Terminal: React.FC<ScreenProps> = ({night, phase = 0}) => {
  const f = useCurrentFrame() + phase;
  const every = 9;                                     // a new line every 9 frames (0.3 s)
  const shown = Math.floor(f / every) + 14;
  const lines: React.ReactNode[] = [];
  const first = Math.max(0, shown - 20);
  for (let i = first; i < shown; i++) {
    const r = rng(1000 + i);
    const a = r(), b = r(), c = r();
    const svc = SVCS[Math.floor(a * SVCS.length)];
    const msTot = i * 300 + Math.floor(b * 90) - 30000;      // one probe every 0.3 s, a little jitter, in order
    const ts = clockAt(night, Math.floor(msTot / 1000), false) + '.' + String(((msTot % 1000) + 1000) % 1000).padStart(3, '0');
    let res: React.ReactNode;
    const ms = Math.floor(900 + c * 4000);
    if (svc === 'authn-edge' && b > 0.4) res = <span style={{color: D.green}}>200 OK            {String(60 + Math.floor(c * 90)).padStart(4)} ms</span>;
    else if (c > 0.62) res = <span style={{color: D.amber}}>timeout after 5000 ms     retry {1 + (i % 3)}/3</span>;
    else res = <span><span style={{color: D.red, fontWeight: 700}}>503 Service Unavailable</span> {String(ms).padStart(5)} ms  retry {1 + (i % 3)}/3</span>;
    lines.push(<div key={i}><span style={{color: D.muted}}>{ts}</span>  GET /healthz  {svc.padEnd(14)}{res}</div>);
  }
  const cursorOn = Math.floor(f / 15) % 2 === 0;
  return (
    <div style={{position: 'absolute', inset: 0, background: '#0f1416', fontFamily: MONO, color: '#cfd8d3', fontSize: 21, lineHeight: 1.42}}>
      <div style={{height: 46, background: D.panel, display: 'flex', alignItems: 'center', padding: '0 20px', gap: 12, fontFamily: UI, fontSize: 22,
        color: D.muted}}>
        {[D.line, D.line, D.line].map((c, i) => <div key={i} style={{width: 16, height: 16, borderRadius: 8, background: c}} />)}
        <span style={{marginLeft: 16}}>ops@bastion-2: ~/runbooks/mail</span>
      </div>
      <div style={{padding: '16px 24px', whiteSpace: 'pre'}}>
        <div><span style={{color: D.teal}}>ops@bastion-2</span>:<span style={{color: '#8fb0d8'}}>~/runbooks/mail</span>$ ./health-check --tier mail --region west --every 0.3s</div>
        <div style={{color: D.muted}}>probing 4 services · 3 retries · 5000 ms timeout</div>
        <div style={{height: 10}} />
        {lines}
        <div><span style={{background: cursorOn ? '#cfd8d3' : 'transparent'}}> </span></div>
      </div>
      <div style={{position: 'absolute', right: 24, top: 64, fontFamily: UI, fontSize: 30, fontWeight: 800, color: D.red, background: '#2a1c1b',
        padding: '8px 18px', borderRadius: 10}}>503 × {120 + Math.floor(shown * 0.7)}</div>
    </div>
  );
};

/* ---------- 5. a laptop: a generic, unbranded assistant that can't reach the mail connector and reads logs ---------- */
// The agent is "Kestrel" (invented). It only reads: it is blocked on the connector (O14's table tent) and summarises
// the health-check log. It never writes, commits or deploys anything.
// a cool light theme in the video's evergreen and teal (not a warm cream with a coral accent: no real assistant's look)
const A = {bg: '#eaf0ef', head: '#f7faf9', line: '#cfdcda', accent: '#2f8f8a'};
const AGENT_TEXT = 'Reading the health-check log instead: mailflow-west has returned 503s and timeouts since 10:26 a.m. PT, ' +
  'and sign-in retries are timing out too. Nothing in the log says why yet.';
export const Agent: React.FC<ScreenProps> = ({night, phase = 0}) => {
  const f = useCurrentFrame() + phase;
  const chars = Math.floor(interpolate(f, [30, 30 + AGENT_TEXT.length * 0.9], [0, AGENT_TEXT.length], clamp));
  const retry = Math.max(0, 30 - Math.floor(f / 30) % 31);
  return (
    <div style={{position: 'absolute', inset: 0, background: A.bg, fontFamily: UI, color: T.ink}}>
      <div style={{height: 76, display: 'flex', alignItems: 'center', gap: 18, padding: '0 34px', borderBottom: `2px solid ${A.line}`,
        background: A.head}}>
        <div style={{width: 46, height: 46, borderRadius: 12, background: T.evergreen, color: '#fff', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: 28, fontWeight: 800}}>K</div>
        <div style={{fontSize: 32, fontWeight: 750}}>Kestrel</div>
        <div style={{fontSize: 22, color: T.inkSoft, border: `2px solid ${A.line}`, borderRadius: 999, padding: '3px 14px'}}>read-only · logs</div>
        <div style={{marginLeft: 'auto', fontSize: 24, color: T.inkSoft}}>{clockAt(night, f / 30)}</div>
      </div>
      <div style={{padding: '30px 46px', display: 'flex', flexDirection: 'column', gap: 24}}>
        <div style={{alignSelf: 'flex-end', maxWidth: 760, background: T.evergreen, color: '#fff', fontSize: 30, padding: '16px 26px',
          borderRadius: '22px 22px 6px 22px'}}>summarize the mail errors since 10:26</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 16, background: '#fff', border: `2px solid ${A.line}`, borderRadius: 14,
          padding: '12px 20px', fontSize: 26, width: 'fit-content'}}>
          <span style={{color: T.inkSoft}}>mail connector</span>
          <span style={{color: T.bad, fontWeight: 750}}>connector unavailable</span>
          <span style={{color: T.inkSoft}}>· retry in {retry} s</span>
          <Spinner size={30} color={A.accent} f={f} />
        </div>
        <div style={{fontSize: 52, fontWeight: 800, lineHeight: 1.1, letterSpacing: -0.5}}>I can't reach the mail connector.</div>
        <div style={{fontSize: 30, lineHeight: 1.45, maxWidth: 1120, color: T.ink}}>
          {AGENT_TEXT.slice(0, chars)}{chars < AGENT_TEXT.length && <span style={{color: A.accent}}>▍</span>}
        </div>
      </div>
      <div style={{position: 'absolute', left: 46, right: 46, bottom: 34, height: 74, borderRadius: 37, border: `2px solid ${A.line}`,
        background: '#fff', display: 'flex', alignItems: 'center', padding: '0 30px', fontSize: 26, color: T.inkFaint}}>Ask Kestrel about the logs…</div>
    </div>
  );
};

/* ---------- 6. a laptop: a generic video call, dark tiles with initials and invented names, some muted ---------- */
const PEOPLE: [string, string, boolean][] = [
  ['Tess', '#c98b5b', false], ['Ren', T.evergreen, true], ['Marco', '#6f8fb5', true],
  ['Ola', '#8a6f9e', true], ['Sam', '#5f8f6a', false], ['Priya', '#b5706f', true],
];
const MicOff: React.FC = () => (
  <svg width={30} height={30} viewBox="0 0 24 24"><rect x={9} y={3} width={6} height={11} rx={3} fill="#fff" />
    <path d="M6 11 A6 6 0 0 0 18 11 M12 17 V21" stroke="#fff" strokeWidth={2} fill="none" />
    <path d="M4 3 L20 21" stroke={D.red} strokeWidth={2.6} /></svg>
);
export const VideoCall: React.FC<ScreenProps> = ({night, phase = 0}) => {
  const f = useCurrentFrame() + phase;
  const elapsed = (night ? 13 * 3600 + 21 * 60 : 4 * 3600 + 26 * 60) + f / 30;     // since 10:26 a.m.
  const hh = Math.floor(elapsed / 3600), mm = Math.floor(elapsed / 60) % 60, ss = Math.floor(elapsed) % 60;
  const talk = 0.5 + 0.5 * Math.sin(f / 2.3) * Math.sin(f / 5.1);
  return (
    <div style={{position: 'absolute', inset: 0, background: '#11171a', fontFamily: UI, color: D.text}}>
      <div style={{height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 30px', fontSize: 28}}>
        <span style={{fontWeight: 700}}>sev 1 bridge · mail</span>
        <span style={{color: D.muted, fontVariantNumeric: 'tabular-nums'}}>{hh}:{String(mm).padStart(2, '0')}:{String(ss).padStart(2, '0')}</span>
      </div>
      <div style={{position: 'absolute', left: 24, right: 24, top: 70, bottom: 120, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
        gridTemplateRows: 'repeat(2, 1fr)', gap: 16}}>
        {PEOPLE.map(([name, tint, muted], i) => {
          const speaking = i === 0;
          return (
            <div key={name} style={{position: 'relative', borderRadius: 18, background: '#1e272b',
              boxShadow: speaking ? `0 0 0 ${4 + 5 * talk}px ${D.coral}` : 'none', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div style={{width: 150, height: 150, borderRadius: '50%', background: tint, display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 72, fontWeight: 700, color: '#fff'}}>{name[0]}</div>
              <div style={{position: 'absolute', left: 16, bottom: 14, display: 'flex', alignItems: 'center', gap: 10, fontSize: 26,
                background: 'rgba(0,0,0,0.45)', padding: '4px 12px', borderRadius: 10}}>
                {muted && <MicOff />}{name}{i === 0 ? ' · on call' : ''}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 22, display: 'flex', justifyContent: 'center', gap: 34}}>
        {['#2e3a40', '#2e3a40', '#2e3a40', D.red].map((c, i) => (
          <div key={i} style={{width: 78, height: 78, borderRadius: '50%', background: c, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <div style={{width: i === 3 ? 38 : 26, height: i === 3 ? 12 : 26, borderRadius: i === 3 ? 6 : 13, background: '#e9e4da'}} />
          </div>
        ))}
      </div>
    </div>
  );
};
