// O13's technical-difficulties card and the end sequence (disclosure, fact card, end card, final card), in the
// station's look. Every sentence below is the brief's, verbatim; only the headings are the kit's own.
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {INCIDENT} from '../config';
import {STATION, UI} from '../Fonts';
import {T} from '../theme';
import {clamp, Frame} from './Common';

export const BRB = 'We’ll be right back.';

export const TechnicalDifficulties: React.FC = () => {
  const f = useCurrentFrame();
  const stripe = ['#2e5e4e', '#e2643e', '#f3ede2', '#8fb8a8', '#1e4237'];
  return (
    <Frame bg={T.evergreenDeep}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 26, display: 'flex'}}>
        {stripe.map((c) => <div key={c} style={{flex: 1, background: c}} />)}
      </div>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        fontFamily: STATION, color: T.paper}}>
        <div style={{fontSize: 140, fontWeight: 600, letterSpacing: -2, opacity: interpolate(f, [0, 6], [0, 1], clamp)}}>{BRB}</div>
        <div style={{marginTop: 36, fontSize: 38, fontWeight: 500, letterSpacing: 6, textTransform: 'uppercase', color: '#f6b49d'}}>Session 503 · 50.3 FM</div>
      </div>
    </Frame>
  );
};

const Card: React.FC<{heading?: string; children: React.ReactNode; dark?: boolean}> = ({heading, children, dark}) => {
  const f = useCurrentFrame();
  return (
    <Frame bg={dark ? T.evergreenDeep : T.paper}>
      <div style={{position: 'absolute', inset: '100px 150px', display: 'flex', flexDirection: 'column', justifyContent: 'center',
        color: dark ? T.paper : T.ink, opacity: interpolate(f, [0, 10], [0, 1], clamp)}}>
        {heading && <div style={{fontFamily: STATION, fontSize: 30, fontWeight: 600, letterSpacing: 4, textTransform: 'uppercase', color: T.coral,
          marginBottom: 30}}>{heading}</div>}
        {children}
      </div>
    </Frame>
  );
};

export const DISCLOSURE = 'Lyrics by Claude, made by Anthropic. Anthropic’s Microsoft 365 connector broke during this outage, and Claude had outages of its own this year. The creator worked on Outlook and Word at Microsoft between 2014 and 2017, and the treehouse meeting room in the bridge is inspired by those years; it doesn’t depict how this incident was handled. Audited by models from other labs: [models, dates].';

export const DisclosureCard: React.FC = () => (
  <Card heading="Conflict-of-interest disclosure">
    <div style={{fontFamily: STATION, fontSize: 50, lineHeight: 1.4, fontWeight: 450}}>{DISCLOSURE}</div>
  </Card>
);

/** [text, source names] per line (brief, "Fact card"); sources are named, URLs go in the description. */
export const FACTS: [string, string][] = [
  ['Exchange Online problems began around 11:17 a.m. ET on Thursday, Nov 12, and the wider outage followed at 1:26 p.m. (Digital Trends). It hit Outlook, Teams, SharePoint, Copilot and Defender in at least 74 countries', '(Wire).'],
  ['Almost 130,000 Outlook problem reports came from U.S. users just after 1 p.m.', '(Washington Post).'],
  ['Some businesses fell back on fax machines to confirm trades', '(Crypto Briefing).'],
  ['Restored servers kept going unresponsive once traffic returned', '(Azure Blog UK).'],
  ['Anthropic and OpenAI both reported their Microsoft 365 connectors failing', '(Cybersecurity News).'],
  ['Microsoft’s cause: an issue from an earlier network capacity upgrade, “not related to cyber or AI / agents” (MacRumors). Microsoft confirmed full restoration on Saturday, Nov 14 (Digital Trends). Full post-incident report:', '[link once published].'],
];
export const FORMAT_LINE = '“Session 503” is a fictional broadcast and is not affiliated with KEXP or any real radio station.';

export const FactCard: React.FC = () => (
  <Card heading="What happened">
    <div style={{fontFamily: UI, fontSize: 31, lineHeight: 1.42, display: 'flex', flexDirection: 'column', gap: 16}}>
      {[...FACTS, ...INCIDENT.factCardQuotes.map((q) => [q, ''] as [string, string])].map(([t, s], i) => (
        <div key={i} style={{display: 'flex', gap: 22}}>
          <div style={{width: 10, height: 10, borderRadius: '50%', background: T.evergreen, marginTop: 17, flexShrink: 0}} />
          <div>{t} <span style={{color: T.inkSoft}}>{s}</span></div>
        </div>
      ))}
      <div style={{display: 'flex', gap: 22, marginTop: 8, color: T.inkSoft, fontSize: 27}}>
        <div style={{width: 10, flexShrink: 0}} />
        <div><b style={{color: T.ink}}>Format:</b> {FORMAT_LINE}</div>
      </div>
    </div>
  </Card>
);

export const END_TITLE = 'All Systems Operational.';
export const END_BODY = 'Lyrics by Claude, music by [generator], video by Claude Code. Human interventions are listed in the production log. Audit log: [repo link].';

export const EndCard: React.FC = () => (
  <Card dark>
    <div style={{fontFamily: STATION, fontSize: 96, fontWeight: 650, letterSpacing: -1.5}}>{END_TITLE}</div>
    <div style={{fontFamily: STATION, fontSize: 46, lineHeight: 1.45, marginTop: 30, maxWidth: 1450, color: '#e9e2d4'}}>{END_BODY}</div>
    {/* branch C (no report, or no clear cause): the end card says so (brief, branches) */}
    {INCIDENT.branch === 'C' && (
      <div style={{fontFamily: STATION, fontSize: 40, marginTop: 30, color: '#f6b49d'}}>Root cause: final report pending as of {INCIDENT.asOf}</div>
    )}
  </Card>
);

export const NEXT = 'Next incident: TBD';
export const FinalCard: React.FC = () => (
  <Card dark>
    <div style={{fontFamily: STATION, fontSize: 110, fontWeight: 600, textAlign: 'center'}}>{NEXT}</div>
  </Card>
);
