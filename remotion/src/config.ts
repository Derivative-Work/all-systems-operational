import seeds from '../../config/seeds.json';
import incidentJson from '../../config/incident.json';
import cues from '../../config/shot_cues.json';
import shotTimes from '../../timing/shot_times.json';

export const SEED: number = seeds.main;
export const FPS = 30;
export const W = 1920;
export const H = 1080;
/** Portrait phone screen texture (generic 9:19.5). */
export const PW = 1080;
export const PH = 2340;

/** Song tempo 100.0 bpm (M2 timing map): one beat = 0.6 s = 18 frames (shot_cues.json remotion.BEAT_frames). */
export const BEAT = Math.round(0.6 * FPS);
export const sec = (s: number) => Math.round(s * FPS);

// Durations (seconds) from config/shot_cues.json: the M2 "remotion" block (DUR_s, approved at the M2 gate, human
// interventions 9) and the post-roll (end card, final card). Set at M5 (production log 13); the placeholders before
// that were guesses. Exact shot lengths in frames are in SHOT below (timing/shot_times.json).
const C = cues.remotion.DUR_s;
export const DUR = {
  ...C,
  card: cues.post_roll.O24_end_card_s,
  finalCard: cues.post_roll.O24_final_card_s,
  factCard: cues.post_roll.fact_card_s,
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

/* ---------- M5: exact shot lengths and in-shot cue frames (timing/shot_times.json, scripts/shot_times.py) ---------- */
type ShotT = {start_frame: number; end_frame: number; marks?: {what: string; frame_in_shot: number}[]};
const SH = shotTimes.shots as unknown as Record<string, ShotT>;
/** A shot's length in frames (end_frame - start_frame), as the edit cuts it. */
export const shotFrames = (id: string) => SH[id].end_frame - SH[id].start_frame;
/** The frame (from the shot's start) of the i-th mark of a shot. */
export const mark = (id: string, i: number) => (SH[id].marks ?? [])[i].frame_in_shot;
/** The disclosure card's length (config/shot_cues.json cards; the withdrawn O17 overlay's, decisions 7 and 18). */
export const DISCLOSURE_FRAMES = (shotTimes as unknown as {cards: {disclosure_frames: number}}).cards.disclosure_frames;
