// O04/O08: a crowd member's phone showing the #it-help thread, a dramatization with invented first names (brief
// guardrails). The +1 count climbs on each Hey!; O08 adds IT's reply, "we are aware". Text style after the creator's
// captures (casual, lowercase, short); no message is copied from them.
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {PW} from '../config';
import {UI} from '../Fonts';
import {T} from '../theme';
import {Avatar, ChannelHeader, Message, PlusOne} from './Chat';
import {clamp} from './Common';
import {StatusBar} from './Phone';

export const IT_HELP = {
  channel: '#it-help',
  sub: '214 members',
  clock: '1:02',
  earlier: [
    {p: {name: 'Jordan', tint: '#c98b5b'}, time: '12:41 PM', text: 'printer on 4 is jammed again'},
    {p: {name: 'Jordan', tint: '#c98b5b'}, time: '12:44 PM', text: 'nvm someone fixed it'},
  ],
  ask: {p: {name: 'Dana', tint: '#6f8fb5'}, time: '12:57 PM', text: 'is email down for anyone else?'},
  reply: {p: {name: 'Ren (IT)', initials: 'R', tint: T.evergreen}, time: '1:02 PM', text: 'we are aware'},
};

export type PhoneChatProps = {
  base?: number; // the +1 count before the first Hey!
  heys?: number[]; // frames on which the count goes up by one (each Hey!; placeholder until M2)
  reply?: boolean; // O08: IT's reply
  replyAt?: number;
  askAt?: number; // M5: the frame the question arrives (O04: on 'is email down'); default: already there
};

/** The screen content (PW wide). */
export const PhoneChatScreen: React.FC<PhoneChatProps> = ({base = 6, heys = [], reply = false, replyAt = 0, askAt = -100}) => {
  const f = useCurrentFrame();
  const n = heys.filter((h) => f >= h).length;
  const lastHey = [...heys].reverse().find((h) => f >= h);
  const bump = lastHey === undefined ? 0 : interpolate(f - lastHey, [0, 3, 8], [0, 1, 0], clamp);
  const rIn = interpolate(f, [replyAt, replyAt + 6], [0, 1], clamp);
  const s = 1.6;
  return (
    <div style={{position: 'absolute', inset: 0, background: T.chatBg, fontFamily: UI}}>
      <div style={{background: T.chatCard}}><StatusBar time={IT_HELP.clock} /></div>
      <ChannelHeader channel={IT_HELP.channel} sub={IT_HELP.sub} s={s} back />
      <div style={{padding: '40px 40px', display: 'flex', flexDirection: 'column', gap: 30}}>
        <div style={{textAlign: 'center', fontSize: 34, color: T.chatMuted, fontWeight: 500}}>Today</div>
        {IT_HELP.earlier.map((m, i) => <Message key={i} p={m.p} time={m.time} s={s}>{m.text}</Message>)}
        {f >= askAt && <div style={{opacity: interpolate(f, [askAt, askAt + 6], [0, 1], clamp), transform: `translateY(${interpolate(f, [askAt, askAt + 6], [30, 0], clamp)}px)`}}>
          <Message p={IT_HELP.ask.p} time={IT_HELP.ask.time} s={s}
            footer={<PlusOne count={base + n} s={s} bump={bump} />}>{IT_HELP.ask.text}</Message></div>}
        {reply && rIn > 0 && (
          <div style={{opacity: rIn, transform: `translateY(${(1 - rIn) * 30}px)`}}>
            <Message p={IT_HELP.reply.p} time={IT_HELP.reply.time} s={s}>{IT_HELP.reply.text}</Message>
          </div>
        )}
      </div>
      {/* composer */}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 230, background: T.chatCard, borderTop: `1px solid ${T.chatLine}`,
        padding: '36px 40px'}}>
        <div style={{height: 100, borderRadius: 50, border: `2px solid ${T.chatLine}`, display: 'flex', alignItems: 'center', padding: '0 44px',
          fontSize: 40, color: T.chatMuted}}>Message #it-help</div>
      </div>
      {/* the caption sits on the screen itself, so it survives the Blender shot */}
      <div style={{position: 'absolute', left: PW / 2, transform: 'translateX(-50%)', top: 1500, fontSize: 36, fontWeight: 500, color: '#fff',
        background: 'rgba(20,26,29,0.7)', padding: '10px 26px', borderRadius: 14}}>dramatization</div>
    </div>
  );
};

/** M7b (human interventions 18: "make sure that the phone's Slack messages are readable when it is visible"): the
 * O04 screen for the Blender phone, built to be read at about 350 px wide in a 1080p frame. One message, the +1
 * count and the caption, in big type; same thread, names and cue frames as PhoneChatScreen (no earlier messages, no
 * composer). The question arrives on 'inbox' (askAt); the count steps on each Hey!. */
export const PhoneChatBig: React.FC<PhoneChatProps> = ({base = 6, heys = [], askAt = -100}) => {
  // the holder's thumb hovers over the screen's right half from about 33% of its height down (the library pose), so
  // the message sits high, above it, with the sender on one small line
  const f = useCurrentFrame();
  const n = heys.filter((h) => f >= h).length;
  const lastHey = [...heys].reverse().find((h) => f >= h);
  const bump = lastHey === undefined ? 0 : interpolate(f - lastHey, [0, 3, 9], [0, 1, 0], clamp);
  const aIn = interpolate(f, [askAt, askAt + 6], [0, 1], clamp);
  const p = IT_HELP.ask.p;
  return (
    <div style={{position: 'absolute', inset: 0, background: T.chatBg, fontFamily: UI, color: T.chatText}}>
      <div style={{background: T.chatCard}}><StatusBar time={IT_HELP.clock} /></div>
      <ChannelHeader channel={IT_HELP.channel} s={2.0} back />
      {f >= askAt && (
        <div style={{margin: '34px 34px 0', opacity: aIn, transform: `translateY(${(1 - aIn) * 60}px)`, background: T.chatCard,
          borderRadius: 40, border: `3px solid ${T.chatLine}`, boxShadow: '0 4px 10px rgba(20,30,35,0.08)', padding: '30px 44px 44px'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
            <Avatar p={p} size={84} />
            <span style={{fontSize: 54, fontWeight: 700}}>{p.name}</span>
            <span style={{fontSize: 42, color: T.chatMuted}}>{IT_HELP.ask.time}</span>
          </div>
          <div style={{fontSize: 124, fontWeight: 650, lineHeight: 1.1, letterSpacing: -1.5, marginTop: 22}}>{IT_HELP.ask.text}</div>
          <div style={{display: 'inline-flex', alignItems: 'center', gap: 28, marginTop: 40, padding: '14px 44px', borderRadius: 999,
            background: T.chatAccentSoft, border: `6px solid ${T.chatAccent}`, color: T.chatAccent, fontSize: 100, fontWeight: 750,
            transform: `scale(${1 + 0.16 * bump})`, transformOrigin: 'left center'}}>
            <span>+1</span><span style={{fontVariantNumeric: 'tabular-nums'}}>{base + n}</span>
          </div>
        </div>
      )}
      <div style={{position: 'absolute', left: PW / 2, transform: 'translateX(-50%)', bottom: 150, fontSize: 64, fontWeight: 600, color: '#fff',
        background: 'rgba(20,26,29,0.78)', padding: '16px 44px', borderRadius: 22}}>dramatization</div>
    </div>
  );
};
