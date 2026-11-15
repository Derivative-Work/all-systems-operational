// The generic chat app, used for both chat pieces (O01's recreated post, O04/O08's #it-help thread). Its own light
// design: a centred message column of white cards, round avatars, a teal accent, no sidebar. Nothing from Slack (no
// logo, no aubergine sidebar, no Slack colours or full-width message rows) or Teams (no purple, no bubbles).
import React from 'react';
import {Img, staticFile} from 'remotion';
import {UI} from '../Fonts';
import {T} from '../theme';

export type Person = {name: string; initials?: string; avatar?: string; tint?: string};

export const Avatar: React.FC<{p: Person; size: number}> = ({p, size}) => (
  p.avatar
    ? <Img src={staticFile(p.avatar)} style={{width: size, height: size, borderRadius: '50%', flexShrink: 0, objectFit: 'cover'}} />
    : <div style={{width: size, height: size, borderRadius: '50%', flexShrink: 0, background: p.tint ?? '#9bb5ad', color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: UI, fontWeight: 600, fontSize: size * 0.4}}>
      {p.initials ?? p.name[0]}</div>
);

/** One message card: avatar, name, time, body. `s` scales the whole card (1 = desktop 1080p). */
export const Message: React.FC<{p: Person; time: string; s?: number; children: React.ReactNode; footer?: React.ReactNode}> = ({
  p, time, s = 1, children, footer,
}) => (
  <div style={{display: 'flex', gap: 22 * s, background: T.chatCard, borderRadius: 18 * s, padding: `${26 * s}px ${30 * s}px`,
    boxShadow: '0 1px 2px rgba(20,30,35,0.06), 0 6px 18px rgba(20,30,35,0.05)', border: `1px solid ${T.chatLine}`}}>
    <Avatar p={p} size={64 * s} />
    <div style={{flex: 1, minWidth: 0, fontFamily: UI, color: T.chatText}}>
      <div style={{display: 'flex', alignItems: 'baseline', gap: 14 * s}}>
        <span style={{fontSize: 28 * s, fontWeight: 650}}>{p.name}</span>
        <span style={{fontSize: 22 * s, color: T.chatMuted}}>{time}</span>
      </div>
      <div style={{fontSize: 30 * s, lineHeight: 1.42, marginTop: 6 * s}}>{children}</div>
      {footer}
    </div>
  </div>
);

/** A chat header bar: the channel name and an optional line under it. */
export const ChannelHeader: React.FC<{channel: string; sub?: string; s?: number; back?: boolean}> = ({channel, sub, s = 1, back}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 18 * s, padding: `${22 * s}px ${36 * s}px`, background: T.chatCard,
    borderBottom: `1px solid ${T.chatLine}`, fontFamily: UI}}>
    {back && (
      <svg width={30 * s} height={30 * s} viewBox="0 0 24 24"><path d="M15 4 L7 12 L15 20" fill="none" stroke={T.chatAccent} strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" /></svg>
    )}
    <div style={{width: 46 * s, height: 46 * s, borderRadius: 12 * s, background: T.chatAccentSoft, color: T.chatAccent, display: 'flex',
      alignItems: 'center', justifyContent: 'center', fontSize: 28 * s, fontWeight: 700}}>#</div>
    <div>
      <div style={{fontSize: 30 * s, fontWeight: 700, color: T.chatText}}>{channel.replace(/^#/, '')}</div>
      {sub && <div style={{fontSize: 21 * s, color: T.chatMuted, marginTop: 2 * s}}>{sub}</div>}
    </div>
  </div>
);

/** A "+1 n" reaction pill (text, not an emoji). `bump` 0..1 pops it when the count changes. */
export const PlusOne: React.FC<{count: number; s?: number; bump?: number}> = ({count, s = 1, bump = 0}) => (
  <div style={{display: 'inline-flex', alignItems: 'center', gap: 10 * s, marginTop: 14 * s, padding: `${6 * s}px ${16 * s}px`,
    borderRadius: 999, background: T.chatAccentSoft, border: `2px solid ${T.chatAccent}`, color: T.chatAccent, fontFamily: UI,
    fontSize: 26 * s, fontWeight: 650, transform: `scale(${1 + 0.18 * bump})`, transformOrigin: 'left center'}}>
    <span>+1</span><span style={{fontVariantNumeric: 'tabular-nums'}}>{count}</span>
  </div>
);
