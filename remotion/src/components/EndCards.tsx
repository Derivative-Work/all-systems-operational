// M7's end sequence, over the human's instrumental (human interventions 25-26: "don't worry about length, just make it
// readable"; decisions 44-45; config/end_cards_m7.json). The brief's cards in the brief's order (end card, "Next
// incident: TBD", the fact card, the disclosure), each held for at least its reading time; the fact card split into
// pages of the brief's lines, verbatim, at a larger size. With snap set, each change moves later onto the
// instrumental's music (timing/credits_grid.json, scripts/m7_credits.py): the strongest section change within window_s
// of the reading time, else the next downbeat; the last card ends at the first fade-out point after its reading time.
// The M5 cards in Cards.tsx are unchanged.
import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import cfg from '../../../config/end_cards_m7.json';
import grid from '../../../timing/credits_grid.json';
import {FPS, INCIDENT} from '../config';
import {STATION, UI} from '../Fonts';
import {T} from '../theme';
import {clamp} from './Common';
import {Card, DISCLOSURE, DisclosureCard, END_BODY, END_TITLE, EndCard, FACTS, FinalCard, FORMAT_LINE, NEXT} from './Cards';

type Line = [string, string];
const ALL: Line[] = [...FACTS, ...INCIDENT.factCardQuotes.map((q) => [q, ''] as Line)];
const PAGES: (number | 'format')[][] = cfg.fact_pages as (number | 'format')[][];
const HEADING = 'What happened';
const NB = '\u00a0';
/** Display only (the words are the brief's): no line break inside a source's name, a time, a date or a percentage. */
const nb = (t: string) => t
  .replace(/\(([^()]+)\)/g, (m) => m.replace(/ /g, NB))
  .replace(/ (a\.m\.|p\.m\.|ET\b)/g, `${NB}$1`)
  .replace(/\b(Nov|July) (\d)/g, `$1${NB}$2`)
  .replace(/\[([^\]]+)\]/g, (m) => m.replace(/ /g, NB));
/** The pages' content sits at one height, so the heading doesn't move from page to page. */
const PAGE_BOX = 540;

const words = (...t: string[]) => t.join(' ').split(/\s+/).filter(Boolean).length;
/** Reading time in seconds: words at wpm, plus the settle, at least min_s. */
const readS = (n: number) => Math.max(cfg.min_s, (n / cfg.wpm) * 60 + cfg.settle_s);
/** Unsnapped hold in frames: the reading time rounded up to whole seconds. */
const hold = (n: number) => Math.ceil(readS(n)) * FPS;
const pageText = (p: (number | 'format')[]) => p.flatMap((k) => (k === 'format' ? ['Format:', FORMAT_LINE] : ALL[k]));

/** A fact-card page: the brief's lines on it, the heading, and dots for where it sits among the pages. */
export const FactPage: React.FC<{page: number}> = ({page}) => (
  <Card>
    <div style={{height: PAGE_BOX}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 28, marginBottom: 34}}>
      <div style={{fontFamily: STATION, fontSize: 30, fontWeight: 600, letterSpacing: 4, textTransform: 'uppercase', color: T.coral}}>{HEADING}</div>
      <div style={{display: 'flex', gap: 12}}>
        {PAGES.map((_, i) => (
          <div key={i} style={{width: 13, height: 13, borderRadius: '50%', boxSizing: 'border-box',
            background: i === page ? T.coral : 'transparent', border: `2px solid ${i === page ? T.coral : T.inkFaint}`}} />
        ))}
      </div>
    </div>
    <div style={{fontFamily: UI, fontSize: 44, lineHeight: 1.45, display: 'flex', flexDirection: 'column', gap: 34, maxWidth: 1560}}>
      {PAGES[page].map((k) => k === 'format' ? (
        <div key="format" style={{display: 'flex', gap: 26, marginTop: 6, color: T.inkSoft, fontSize: 36}}>
          <div style={{width: 12, flexShrink: 0}} />
          <div><b style={{color: T.ink}}>Format:</b> {nb(FORMAT_LINE)}</div>
        </div>
      ) : (
        <div key={k} style={{display: 'flex', gap: 26}}>
          <div style={{width: 12, height: 12, borderRadius: '50%', background: T.evergreen, marginTop: 26, flexShrink: 0}} />
          <div>{nb(ALL[k][0])} <span style={{color: T.inkSoft}}>{nb(ALL[k][1])}</span></div>
        </div>
      ))}
    </div>
    </div>
  </Card>
);

export type EndItem = {id: string; words: number; read: number; frames: number; from: number; dark: boolean; el: React.ReactNode};

type Snap = {window_s: number; window_frac: number; picture_fade_s: number; music_fade_s: number};
const SNAP = cfg.snap as Snap | null;
const G = grid as unknown as {sections: {t: number; strength: number}[]; downbeats_s: number[]; ends_s: number[]};
/** The card change for a reading time ending at need (s): the strongest section change in [need, need + window], else the
 * next downbeat, else need itself. The window is window_s, or window_frac of the card's reading time if less, so a
 * short card doesn't wait long for a section change. */
const snapTo = (need: number, read: number) => {
  const w = Math.min(SNAP!.window_s, SNAP!.window_frac * read);
  const near = G.sections.filter((c) => c.t >= need - 1e-6 && c.t <= need + w);
  if (near.length) return near.reduce((a, b) => (b.strength > a.strength ? b : a)).t;
  return G.downbeats_s.find((t) => t >= need - 1e-6) ?? need;
};

/** The plan: each card's words, reading time, start and visible length (frames). Cards overlap the next by fade_frames:
 * onto a different background the incoming card cross-fades; onto the same one it covers the outgoing card and its words
 * fade in (Card's own fade), so two pages of text never show through each other. Unsnapped, a card's change starts
 * fade_frames before its hold ends; snapped, it starts on the music. */
const ITEMS: Omit<EndItem, 'from' | 'frames'>[] = (() => {
  const items: Omit<EndItem, 'from' | 'frames'>[] = [];
  const add = (id: string, n: number, dark: boolean, el: React.ReactNode) => items.push({id, words: n, read: readS(n), dark, el});
  for (const k of cfg.order) {
    if (k === 'end') {
      const extra = INCIDENT.branch === 'C' ? `Root cause: final report pending as of ${INCIDENT.asOf}` : '';
      add('end', words(END_TITLE, END_BODY, extra), true, <EndCard />);
    } else if (k === 'final') {
      add('final', words(NEXT), true, <FinalCard />);
    } else if (k === 'fact') {
      PAGES.forEach((p, i) => add(`fact${i + 1}`, words(HEADING, ...pageText(p)), false, <FactPage page={i} />));
    } else if (k === 'disclosure') {
      add('disclosure', words('Conflict-of-interest disclosure', DISCLOSURE), false, <DisclosureCard />);
    }
  }
  return items;
})();

const plan = (): {items: EndItem[]; total: number; blackFrom: number} => {
  if (!SNAP) {
    let t = 0;
    const items = ITEMS.map((it, i) => {
      const frames = hold(it.words);
      const from = t;
      t += frames - (i < ITEMS.length - 1 ? cfg.fade_frames : 0);
      return {...it, frames, from};
    });
    const last = items[items.length - 1];
    return {items, total: last.from + last.frames + 2 * cfg.fade_frames, blackFrom: last.from + last.frames};
  }
  const starts: number[] = [0];
  ITEMS.slice(0, -1).forEach((it, i) => starts.push(snapTo(starts[i] + it.read, it.read)));
  const need = starts[starts.length - 1] + ITEMS[ITEMS.length - 1].read;
  const end = G.ends_s.find((e) => e - SNAP.picture_fade_s >= need - 1e-6) ?? need + SNAP.picture_fade_s;
  const fr = [...starts, end].map((t) => Math.round(t * FPS));
  const items = ITEMS.map((it, i) => ({...it, from: fr[i], frames: fr[i + 1] - fr[i]}));
  return {items, total: fr[fr.length - 1], blackFrom: fr[fr.length - 1] - Math.round(SNAP.picture_fade_s * FPS)};
};
const PLAN = plan();
export const END_PLAN: EndItem[] = PLAN.items;
export const END_FRAMES = PLAN.total;
/** For the audio (scripts/m7_end.sh): the music fades out over this many seconds, ending with the sequence. */
export const MUSIC_FADE_S = SNAP ? SNAP.music_fade_s : 0;

const FadeIn: React.FC<{on: boolean; children: React.ReactNode}> = ({on, children}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: on ? interpolate(f, [0, cfg.fade_frames], [0, 1], clamp) : 1}}>{children}</AbsoluteFill>;
};

export const EndSequence: React.FC = () => {
  const f = useCurrentFrame();
  const out = interpolate(f, [PLAN.blackFrom, END_FRAMES], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {END_PLAN.map((it, i) => {
        const last = i === END_PLAN.length - 1;
        // unsnapped, a card's frames include the overlap; snapped, the next card starts on the music, so this one stays
        // under it while it fades in
        const len = last ? END_FRAMES - it.from : it.frames + (SNAP ? cfg.fade_frames : 0);
        return (
          <Sequence key={it.id} from={it.from} durationInFrames={len}>
            <FadeIn on={i > 0 && it.dark !== END_PLAN[i - 1].dark}>{it.el}</FadeIn>
          </Sequence>
        );
      })}
      <AbsoluteFill style={{background: '#000', opacity: out}} />
    </AbsoluteFill>
  );
};
