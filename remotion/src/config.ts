import seeds from '../../config/seeds.json';
import incidentJson from '../../config/incident.json';

export const SEED: number = seeds.main;
export const FPS = 30;
export const W = 1920;
export const H = 1080;
/** Portrait phone screen texture (generic 9:19.5). */
export const PW = 1080;
export const PH = 2340;

/** Song tempo about 100 bpm (M0 tracker: 99.4): one beat = 0.6 s = 18 frames. */
export const BEAT = Math.round(0.6 * FPS);
export const sec = (s: number) => Math.round(s * FPS);

// PLACEHOLDER durations (seconds). No timing map exists yet: M2 replaces these from timing/shot_times.json
// (as Ever Present's config.ts reads SHOTS[id].start_frame/end_frame). Lengths are sensible guesses only.
export const DUR = {
  O01_spike: 2.0, // the line shoots up (quick beat)
  O01_real: 2.6, // two real screenshots, <= 3 s together (brief)
  O01_chat: 3.6, // strike, strike, cursor, click; the song starts on the cut
  O02: 6.0,
  O03: 5.0,
  O04: 5.0,
  O05: 4.8,
  O08: 9.6, // four echoes, two bars apart
  O09: 6.0,
  O10: 3.0,
  O11: 3.0,
  O12: 2.4,
  O13: 3.0,
  O18: 12.0,
  O19: 5.0,
  O20: 4.0,
  O21: 2.4,
  O22: 6.0,
  O23: 4.0,
  card: 6.0,
  finalCard: 3.0,
} as const;
export const dur = (k: keyof typeof DUR) => sec(DUR[k]);
export const O01_TOTAL = dur('O01_spike') + dur('O01_real') + dur('O01_chat');

export type Branch = 'A' | 'B' | 'C';
export type Incident = {
  asOf: string;
  statusPhrases: string[];
  rootCause: string;
  contributingFactors: string[];
  configDiff: string | null;
  branch: Branch;
  factCardQuotes: string[];
  sources: string[];
};
/** config/incident.json: every changeable incident detail (brief). */
export const INCIDENT = incidentJson as unknown as Incident;

/** The stale stamp on every status row (brief, O02/O23): a page that can't load can't update. */
export const STAMP = 'Last updated: Thu 12:58 p.m.';

/** Deterministic PRNG (mulberry32) seeded from config/seeds.json. */
export const rng = (salt: number) => {
  let a = (SEED * 1000003 + salt) >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};
