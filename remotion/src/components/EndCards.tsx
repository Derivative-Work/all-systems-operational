// M7's end sequence, over the human's instrumental (human interventions 25: "don't worry about length, just make it
// readable"; decisions 44; config/end_cards_m7.json). The brief's cards in the brief's order (end card, "Next incident:
// TBD", the fact card, the disclosure), each held for its reading time; the fact card split into pages of the brief's
// lines, verbatim, at a larger size. The M5 cards in Cards.tsx are unchanged.
import React from 'react';
import {AbsoluteFill, interpolate, Sequence, useCurrentFrame} from 'remotion';
import cfg from '../../../config/end_cards_m7.json';
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
/** Reading time in frames: words at wpm, plus the settle, at least min_s, rounded up to whole seconds. */
const hold = (n: number) => Math.max(cfg.min_s, Math.ceil((n / cfg.wpm) * 60 + cfg.settle_s)) * FPS;
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

export type EndItem = {id: string; words: number; frames: number; from: number; dark: boolean; el: React.ReactNode};

/** The plan: each card's words, hold and start. Cards overlap by fade_frames: onto a different background the incoming
 * card cross-fades; onto the same one it covers the outgoing card and its words fade in (Card's own fade), so two
 * pages of text never show through each other. */
export const END_PLAN: EndItem[] = (() => {
  const items: Omit<EndItem, 'from'>[] = [];
  for (const k of cfg.order) {
    if (k === 'end') {
      const extra = INCIDENT.branch === 'C' ? `Root cause: final report pending as of ${INCIDENT.asOf}` : '';
      const n = words(END_TITLE, END_BODY, extra);
      items.push({id: 'end', words: n, frames: hold(n), dark: true, el: <EndCard />});
    } else if (k === 'final') {
      const n = words(NEXT);
      items.push({id: 'final', words: n, frames: hold(n), dark: true, el: <FinalCard />});
    } else if (k === 'fact') {
      PAGES.forEach((p, i) => {
        const n = words(HEADING, ...pageText(p));
        items.push({id: `fact${i + 1}`, words: n, frames: hold(n), dark: false, el: <FactPage page={i} />});
      });
    } else if (k === 'disclosure') {
      const n = words('Conflict-of-interest disclosure', DISCLOSURE);
      items.push({id: 'disclosure', words: n, frames: hold(n), dark: false, el: <DisclosureCard />});
    }
  }
  let t = 0;
  return items.map((it, i) => {
    const from = t;
    t += it.frames - (i < items.length - 1 ? cfg.fade_frames : 0);
    return {...it, from};
  });
})();
/** The last card fades to black over this many frames after its hold. */
export const END_TAIL = 2 * cfg.fade_frames;
export const END_FRAMES = END_PLAN[END_PLAN.length - 1].from + END_PLAN[END_PLAN.length - 1].frames + END_TAIL;

const FadeIn: React.FC<{on: boolean; children: React.ReactNode}> = ({on, children}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{opacity: on ? interpolate(f, [0, cfg.fade_frames], [0, 1], clamp) : 1}}>{children}</AbsoluteFill>;
};

export const EndSequence: React.FC = () => {
  const f = useCurrentFrame();
  const last = END_PLAN[END_PLAN.length - 1];
  const out = interpolate(f, [last.from + last.frames, END_FRAMES], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {END_PLAN.map((it, i) => (
        <Sequence key={it.id} from={it.from} durationInFrames={it.frames + (i === END_PLAN.length - 1 ? END_TAIL : 0)}>
          <FadeIn on={i > 0 && it.dark !== END_PLAN[i - 1].dark}>{it.el}</FadeIn>
        </Sequence>
      ))}
      <AbsoluteFill style={{background: '#000', opacity: out}} />
    </AbsoluteFill>
  );
};
