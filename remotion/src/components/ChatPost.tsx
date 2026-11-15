// O01, beat 3: the creator's #it-self-help post sharing this song, recreated in the generic chat UI with the creator's
// real name and photo (the one approved real-person exception, brief guardrails; the photo is cropped from his own
// message in assets/screenshots/slack-5.png). Captioned "recreation". "(my last meme about this, I promise)" is struck
// through, then "no video yet as this is breaking news"; then the cursor clicks play and the song starts on the cut.
import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {UI} from '../Fonts';
import {T} from '../theme';
import {ChannelHeader, Message} from './Chat';
import {clamp, Frame, Tag} from './Common';

export const POST = {
  channel: '#it-self-help',
  author: {name: 'Albert Armea', avatar: 'real/creator_avatar.png'},
  time: '9:39 AM',
  lines: [
    '(my last meme about this, I promise)',
    '(slop warning)',
    '“All Systems Operational” — a singalong for the M365 services, as a mid-2010s stomp-clap song',
    'lyrics in thread',
    'no video yet as this is breaking news',
  ],
  file: 'All Systems Operational.mp3',
  meta: '3:59 (5.9 MB)',
  transcript: 'We’re investigating reports. That some of you can’t reach anything. The inbox went still. The calendar was empty and the queue began to fill…',
  replies: '2 replies',
};

/** Text with a strike-through line drawn across it left to right (p 0..1). */
const Strike: React.FC<{p: number; children: React.ReactNode}> = ({p, children}) => (
  <span style={{position: 'relative', display: 'inline-block'}}>
    {children}
    <span style={{position: 'absolute', left: -4, top: '54%', height: 4, width: `calc(${p * 100}% + ${p * 8}px)`, background: T.chatText,
      borderRadius: 2}} />
  </span>
);

const Cursor: React.FC = () => (
  <svg width={44} height={58} viewBox="0 0 22 29">
    <path d="M1 1 L1 23 L6.5 18 L10.5 27 L14 25.5 L10 17 L17.5 17 Z" fill="#111" stroke="#fff" strokeWidth={1.6} strokeLinejoin="round" />
  </svg>
);

export type ChatPostTiming = {strike1: number; strike2: number; cursorIn: number; click: number};

export const ChatPost: React.FC<{timing?: Partial<ChatPostTiming>}> = ({timing}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  // defaults scale with the composition: hold, strike, strike, move, click near the end (the song starts on the cut)
  const t: ChatPostTiming = {strike1: Math.round(d * 0.2), strike2: Math.round(d * 0.4), cursorIn: Math.round(d * 0.55), click: d - 10, ...timing};
  const s1 = interpolate(f, [t.strike1, t.strike1 + 9], [0, 1], clamp);
  const s2 = interpolate(f, [t.strike2, t.strike2 + 11], [0, 1], clamp);
  const move = interpolate(f, [t.cursorIn, t.click - 4], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const press = interpolate(f, [t.click, t.click + 2, t.click + 5], [0, 1, 0], clamp);
  const playing = f >= t.click + 1;
  const elapsed = Math.max(0, (f - t.click - 1) / 30); // the progress runs at the song's real rate (3:59)
  const prog = Math.min(1, elapsed / 239);
  const ring = interpolate(f, [t.click, t.click + 9], [0, 1], clamp);
  return (
    <Frame bg={T.chatBg}>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column'}}>
        <ChannelHeader channel={POST.channel} />
        <div style={{flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{width: 1240, transform: 'scale(1.17)'}}>
          <Message p={POST.author} time={POST.time}
            footer={<div style={{marginTop: 22, fontSize: 25, fontWeight: 600, color: T.chatAccent, display: 'flex', alignItems: 'center', gap: 10}}>
              <svg width={26} height={26} viewBox="0 0 24 24"><path d="M4 5h16v10H9l-5 4z" fill="none" stroke={T.chatAccent} strokeWidth={2.2} strokeLinejoin="round" /></svg>
              {POST.replies}</div>}>
            <div><Strike p={s1}>{POST.lines[0]}</Strike></div>
            <div>{POST.lines[1]}</div>
            <div style={{marginTop: 14}}>{POST.lines[2]}</div>
            <div>{POST.lines[3]}</div>
            <div><Strike p={s2}>{POST.lines[4]}</Strike></div>
            {/* the audio attachment */}
            <div style={{marginTop: 22, width: 900, border: `1px solid ${T.chatLine}`, borderRadius: 16, padding: '22px 26px', background: '#fbfcfc'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
                <div style={{position: 'relative', width: 76, height: 76, flexShrink: 0}}>
                  <div style={{position: 'absolute', inset: 0, borderRadius: '50%', background: T.chatAccent, transform: `scale(${1 - 0.08 * press})`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
                    {playing
                      ? <svg width={30} height={30} viewBox="0 0 10 10"><rect x={1.5} y={1} width={2.4} height={8} rx={0.5} fill="#fff" /><rect x={6.1} y={1} width={2.4} height={8} rx={0.5} fill="#fff" /></svg>
                      : <svg width={32} height={32} viewBox="0 0 10 10"><path d="M3 1.2 L9 5 L3 8.8 Z" fill="#fff" /></svg>}
                  </div>
                  {ring > 0 && ring < 1 && <div style={{position: 'absolute', inset: -14 * ring, borderRadius: '50%', border: `3px solid ${T.chatAccent}`, opacity: 1 - ring}} />}
                  {/* the cursor travels in the play button's own coordinates, from the lower right */}
                  {f >= t.cursorIn - 2 && (
                    <div style={{position: 'absolute', left: 46 + (1 - move) * 760, top: 46 + (1 - move) * 230, transform: `scale(${1 - 0.12 * press})`,
                      transformOrigin: 'top left'}}><Cursor /></div>
                  )}
                </div>
                <div style={{flex: 1}}>
                  <div style={{fontSize: 27, fontWeight: 650}}>{POST.file}</div>
                  <div style={{fontSize: 22, color: T.chatMuted, marginTop: 2}}>{POST.meta}</div>
                  <div style={{position: 'relative', height: 8, borderRadius: 4, background: T.chatLine, marginTop: 14}}>
                    <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${prog * 100}%`, background: T.chatAccent, borderRadius: 4}} />
                    {playing && <div style={{position: 'absolute', left: `calc(${prog * 100}% - 8px)`, top: -4, width: 16, height: 16, borderRadius: '50%', background: T.chatAccent}} />}
                  </div>
                </div>
              </div>
              <div style={{marginTop: 18, fontSize: 22, color: T.chatMuted, fontStyle: 'italic', lineHeight: 1.45}}>
                <span style={{fontStyle: 'normal', fontWeight: 600, fontSize: 18, letterSpacing: 1, textTransform: 'uppercase', marginRight: 12}}>Transcript</span>
                {POST.transcript}
              </div>
            </div>
          </Message>
        </div>
        </div>
      </div>
      <Tag text="recreation" corner="tr" inset={32} />
    </Frame>
  );
};
