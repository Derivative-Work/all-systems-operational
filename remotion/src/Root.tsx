import React from 'react';
import {AbsoluteFill, Composition, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {BEAT, dur, FPS, H, O01_TOTAL, PH, PW, W} from './config';
import {SpikeChart} from './components/SpikeChart';
import {RealScreens} from './components/RealScreens';
import {ChatPost} from './components/ChatPost';
import {StatusPage, StatusState} from './components/StatusPage';
import {LowerThird, LowerThirdVariant} from './components/LowerThird';
import {PhoneChatProps, PhoneChatScreen} from './components/PhoneChat';
import {FramedPhone, Screen} from './components/Phone';
import {CalendarScreen} from './components/Calendar';
import {BufferingFreeze, CaptionOverlay} from './components/Freeze';
import {DisclosureCard, EndCard, FactCard, FinalCard, TechnicalDifficulties} from './components/Cards';
import {
  BOARD, KICK, KickDrumHead, ONAIR, OnAirSign, POLAROID, Polaroid, SIGN, StationSign, TableTent, TENT, Whiteboard,
} from './components/Textures';
import {SW, SwitchPlane, SwitchState} from './components/Switch';
import {Frame, Tag} from './components/Common';
import {T} from './theme';

/* ---------- O01: the opening bookend, three beats in sequence ---------- */
const Bookend: React.FC = () => (
  <AbsoluteFill>
    <Sequence durationInFrames={dur('O01_spike')}><SpikeChart /></Sequence>
    <Sequence from={dur('O01_spike')} durationInFrames={dur('O01_real')}><RealScreens /></Sequence>
    <Sequence from={dur('O01_spike') + dur('O01_real')} durationInFrames={dur('O01_chat')}><ChatPost /></Sequence>
  </AbsoluteFill>
);

/* ---------- phones: a framed full-frame shot and the bare screen texture ---------- */
// PLACEHOLDER cue frames until M2: the +1 count steps on each Hey! (two beats apart here only for review).
const O04: PhoneChatProps = {base: 6, heys: [24, 60, 96, 132]};
const O08: PhoneChatProps = {base: 10, reply: true, replyAt: 14};
const FramedChat: React.FC<PhoneChatProps> = (p) => (
  <FramedPhone overlay={<Tag text="dramatization" corner="br" inset={48} size={30} />}><PhoneChatScreen {...p} /></FramedPhone>
);
const BareChat: React.FC<PhoneChatProps> = (p) => <Frame><Screen bg={T.chatBg}><PhoneChatScreen {...p} /></Screen></Frame>;
const FramedCal: React.FC = () => <FramedPhone scale={0.72} top={40}><CalendarScreen /></FramedPhone>;
const BareCal: React.FC = () => <Frame><Screen bg="#fcfbf8"><CalendarScreen /></Screen></Frame>;

/* ---------- whiteboard: fill runs 0 -> 1 over the shot (placeholder: line cues come at M2) ---------- */
const BoardAnim: React.FC<{branch?: 'A' | 'B' | 'C'; configDiff?: string | null}> = ({branch, configDiff}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  return <Whiteboard fill={Math.min(1, f / (d * 0.8))} branch={branch} configDiff={configDiff} />;
};
// review only: what branch A looks like once the report gives a diff; the real line comes from incident.json
const DIFF_PREVIEW = '[one-line config diff from the report]';

const full = {fps: FPS, width: W, height: H};

export const Root: React.FC = () => (
  <>
    {/* O01 */}
    <Composition id="O01-Bookend" component={Bookend} durationInFrames={O01_TOTAL} {...full} />
    <Composition id="O01a-SpikeChart" component={SpikeChart} durationInFrames={dur('O01_spike')} {...full} />
    <Composition id="O01b-RealScreens" component={RealScreens} durationInFrames={dur('O01_real')} {...full} />
    <Composition id="O01c-ChatPost" component={ChatPost} durationInFrames={dur('O01_chat')} {...full} />

    {/* status page */}
    {([['O02-StatusPage', 'investigating', 'O02'], ['StatusPage-allGreen', 'allGreen', 'O02'], ['O13-StatusPage', 'renewedErrors', 'O13'],
      ['O23-StatusPage', 'flicker', 'O23']] as [string, StatusState, 'O02' | 'O13' | 'O23'][]).map(([id, state, k]) => (
      <Composition key={id} id={id} component={StatusPage} defaultProps={{state}} durationInFrames={dur(k)} {...full} />
    ))}

    {/* lower thirds (transparent) */}
    {([['O03-LowerThird', 'title', 'O03'], ['O08-LowerThird', 'echo', 'O08'], ['O09-LowerThird', 'uptime', 'O09'],
      ['O19-LowerThird', 'restored', 'O19'], ['O22-LowerThird', 'sorry', 'O22']] as [string, LowerThirdVariant, 'O03' | 'O08' | 'O09' | 'O19' | 'O22'][]).map(
      ([id, variant, k]) => <Composition key={id} id={id} component={LowerThird} defaultProps={{variant}} durationInFrames={dur(k)} {...full} />,
    )}

    {/* phones */}
    <Composition id="O04-PhoneChat" component={FramedChat} defaultProps={O04} durationInFrames={dur('O04')} {...full} />
    <Composition id="O04-PhoneChatScreen" component={BareChat} defaultProps={O04} durationInFrames={dur('O04')} fps={FPS} width={PW} height={PH} />
    <Composition id="O08-PhoneChat" component={FramedChat} defaultProps={O08} durationInFrames={dur('O08')} {...full} />
    <Composition id="O08-PhoneChatScreen" component={BareChat} defaultProps={O08} durationInFrames={dur('O08')} fps={FPS} width={PW} height={PH} />
    <Composition id="O05-Calendar" component={FramedCal} durationInFrames={dur('O05')} {...full} />
    <Composition id="O05-CalendarScreen" component={BareCal} durationInFrames={dur('O05')} fps={FPS} width={PW} height={PH} />

    {/* freezes and cards */}
    <Composition id="O12-BufferingFreeze" component={BufferingFreeze} defaultProps={{}} durationInFrames={dur('O12')} {...full} />
    <Composition id="O21-BufferingFreeze" component={BufferingFreeze} defaultProps={{caption: 'Incident reopened'}} durationInFrames={dur('O21')} {...full} />
    <Composition id="Caption-dramatization" component={CaptionOverlay} defaultProps={{text: 'dramatization'}} durationInFrames={dur('O18')} {...full} />
    <Composition id="O13-TechnicalDifficulties" component={TechnicalDifficulties} durationInFrames={dur('O13')} {...full} />

    {/* Switch (transparent square planes) */}
    {([['O10-Switch', 'on', 'O10', {}], ['Switch-off', 'off', 'O10', {}], ['O11-Switch', 'straining', 'O11', {}],
      ['O12-Switch', 'sagging', 'O12', {sagAt: 6, hold: BEAT}], ['O20-Switch', 'on', 'O20', {}],
      ['O21-Switch', 'sagging', 'O21', {sagAt: 6, hold: 2 * BEAT}]] as [string, SwitchState, 'O10' | 'O11' | 'O12' | 'O20' | 'O21', object][]).map(
      ([id, state, k, extra]) => (
        <Composition key={id} id={id} component={SwitchPlane} defaultProps={{state, ...extra}} durationInFrames={dur(k)} fps={FPS} width={SW} height={SW} />
      ),
    )}

    {/* textures */}
    <Composition id="O09-KickDrumHead" component={KickDrumHead} defaultProps={{}} durationInFrames={1} fps={FPS} width={KICK} height={KICK} />
    <Composition id="KickDrumHead-branchB" component={KickDrumHead} defaultProps={{lgtm: true}} durationInFrames={1} fps={FPS} width={KICK} height={KICK} />
    <Composition id="O14-TableTent" component={TableTent} durationInFrames={1} fps={FPS} width={TENT.w} height={TENT.h} />
    <Composition id="O14-Polaroid" component={Polaroid} defaultProps={{}} durationInFrames={1} fps={FPS} width={POLAROID.w} height={POLAROID.h} />
    <Composition id="OnAirSign-lit" component={OnAirSign} defaultProps={{lit: true}} durationInFrames={1} fps={FPS} width={ONAIR.w} height={ONAIR.h} />
    <Composition id="OnAirSign-unlit" component={OnAirSign} defaultProps={{lit: false}} durationInFrames={1} fps={FPS} width={ONAIR.w} height={ONAIR.h} />
    <Composition id="StationSign" component={StationSign} durationInFrames={1} fps={FPS} width={SIGN.w} height={SIGN.h} />
    <Composition id="O18-Whiteboard" component={BoardAnim} defaultProps={{}} durationInFrames={dur('O18')} fps={FPS} width={BOARD.w} height={BOARD.h} />
    <Composition id="O18-Whiteboard-branchC" component={BoardAnim} defaultProps={{branch: 'C' as const}} durationInFrames={dur('O18')} fps={FPS} width={BOARD.w} height={BOARD.h} />
    <Composition id="O18-Whiteboard-diffPreview" component={BoardAnim} defaultProps={{branch: 'A' as const, configDiff: DIFF_PREVIEW}} durationInFrames={dur('O18')} fps={FPS} width={BOARD.w} height={BOARD.h} />

    {/* end sequence */}
    <Composition id="O15-Disclosure" component={DisclosureCard} durationInFrames={dur('card')} {...full} />
    <Composition id="O24-EndCard" component={EndCard} durationInFrames={dur('card')} {...full} />
    <Composition id="O24-FinalCard" component={FinalCard} durationInFrames={dur('finalCard')} {...full} />
    <Composition id="O24-FactCard" component={FactCard} durationInFrames={dur('card')} {...full} />
  </>
);
