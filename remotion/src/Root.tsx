import React from 'react';
import {AbsoluteFill, Composition, Sequence, useCurrentFrame, useVideoConfig} from 'remotion';
import {BEAT, DISCLOSURE_FRAMES, dur, FPS, H, mark, O01_TOTAL, PH, PW, shotFrames, W} from './config';
import {DisclosurePanel, LiveOverlay} from './components/M5';
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
const FramedCal: React.FC<{drainStart?: number; drainEnd?: number}> = (p) => <FramedPhone scale={0.72} top={40}><CalendarScreen {...p} /></FramedPhone>;
const BareCal: React.FC = () => <Frame><Screen bg="#fcfbf8"><CalendarScreen /></Screen></Frame>;

/* ---------- whiteboard: fill runs 0 -> 1 over the shot (placeholder: line cues come at M2) ---------- */
const BoardAnim: React.FC<{branch?: 'A' | 'B' | 'C'; configDiff?: string | null; reveal?: Record<string, [number, number]>}> = ({branch, configDiff, reveal}) => {
  const f = useCurrentFrame();
  const {durationInFrames: d} = useVideoConfig();
  return <Whiteboard fill={Math.min(1, f / (d * 0.8))} branch={branch} configDiff={configDiff} reveal={reveal} />;
};
// review only: what branch A looks like once the report gives a diff; the real line comes from incident.json
const DIFF_PREVIEW = '[one-line config diff from the report]';

const full = {fps: FPS, width: W, height: H};

/* ---------- M5: the animatic's compositions, each its shot's exact length, events on the M2 cue frames ---------- */
const O18_REVEAL: Record<string, [number, number]> = {
  'rc-l': [mark('O18', 0), mark('O18', 0) + 12], // "Root cause"
  rc: [mark('O18', 1), mark('O18', 3) - 6], // "an earlier upgrade ... met a recent change"
  'cf-l': [mark('O18', 3), mark('O18', 3) + 24], // "Contributing factors"
  cf0: [mark('O18', 4), mark('O18', 4) + 60], // "not related to cyber, AI or agents"
  cr0: [mark('O18', 4) + 60, mark('O18', 4) + 72], // its credit
  'fr-l': [mark('O18', 5), mark('O18', 5) + 24], // "Full report"
  fr: [mark('O18', 6), mark('O18', 6) + 14], // "to follow"
  ll: [mark('O18', 7), mark('O18', 7) + 24], // "Lessons learned"
};
const M5: React.FC = () => (
  <>
    {/* full-frame shots (h264) */}
    <Composition id="M5-O01" component={Bookend} durationInFrames={O01_TOTAL} {...full} />
    <Composition id="M5-O02" component={StatusPage} defaultProps={{state: 'investigating' as StatusState, flipAt: mark('O02', 0)}} durationInFrames={shotFrames('O02')} {...full} />
    <Composition id="M5-O05" component={FramedCal} defaultProps={{drainStart: 4, drainEnd: mark('O05', 0) + 6}} durationInFrames={shotFrames('O05')} {...full} />
    <Composition id="M5-O08-Phone" component={FramedChat} defaultProps={{base: 10, reply: true, replyAt: 3}} durationInFrames={4 * BEAT} {...full} />
    <Composition id="M5-O13-Card" component={TechnicalDifficulties} durationInFrames={mark('O13', 0)} {...full} />
    <Composition id="M5-O13-Status" component={StatusPage} defaultProps={{state: 'renewedErrors' as StatusState}} durationInFrames={shotFrames('O13') - mark('O13', 0)} {...full} />
    <Composition id="M5-O23" component={StatusPage} defaultProps={{state: 'flicker' as StatusState}} durationInFrames={shotFrames('O23')} {...full} />
    <Composition id="M5-O24-EndCard" component={EndCard} durationInFrames={dur('card')} {...full} />
    <Composition id="M5-O24-FinalCard" component={FinalCard} durationInFrames={dur('finalCard')} {...full} />
    <Composition id="M5-FactCard" component={FactCard} durationInFrames={dur('factCard')} {...full} />
    <Composition id="M5-DisclosureCard" component={DisclosureCard} durationInFrames={DISCLOSURE_FRAMES} {...full} />
    {/* transparent overlays (ProRes 4444) */}
    <Composition id="M5-O03-LT" component={LowerThird} defaultProps={{variant: 'title' as LowerThirdVariant, inAt: mark('O03', 0)}} durationInFrames={shotFrames('O03')} {...full} />
    <Composition id="M5-O08-LT" component={LowerThird} defaultProps={{variant: 'echo' as LowerThirdVariant, echoAt: [mark('O08', 0), mark('O08', 3), mark('O08', 5), mark('O08', 7)]}} durationInFrames={shotFrames('O08')} {...full} />
    <Composition id="M5-O09-LT" component={LowerThird} defaultProps={{variant: 'uptime' as LowerThirdVariant, tickAt: mark('O09', 4)}} durationInFrames={shotFrames('O09')} {...full} />
    <Composition id="M5-O19-LT" component={LowerThird} defaultProps={{variant: 'restored' as LowerThirdVariant, inAt: mark('O19', 0)}} durationInFrames={shotFrames('O19')} {...full} />
    <Composition id="M5-O22-LT" component={LowerThird} defaultProps={{variant: 'sorry' as LowerThirdVariant, inAt: mark('O22', 1)}} durationInFrames={shotFrames('O22')} {...full} />
    <Composition id="M5-O07-Caption" component={CaptionOverlay} defaultProps={{text: '[background failed to load]', at: mark('O07', 0), size: 40}} durationInFrames={shotFrames('O07')} {...full} />
    <Composition id="M5-Dramatization" component={CaptionOverlay} defaultProps={{text: 'dramatization'}} durationInFrames={shotFrames('O18')} {...full} />
    <Composition id="M5-O11-Live" component={LiveOverlay} defaultProps={{heys: [mark('O11', 0), mark('O11', 1)], strainAt: mark('O11', 1)}} durationInFrames={shotFrames('O11')} {...full} />
    <Composition id="M5-O12-Freeze" component={BufferingFreeze} defaultProps={{}} durationInFrames={shotFrames('O12')} {...full} />
    <Composition id="M5-O21-Freeze" component={BufferingFreeze} defaultProps={{caption: 'Incident reopened'}} durationInFrames={shotFrames('O21')} {...full} />
    <Composition id="M5-O17-Disclosure" component={DisclosurePanel} durationInFrames={DISCLOSURE_FRAMES} {...full} />
    {/* textures for the Blender shots and the O04 screen (h264) */}
    <Composition id="M5-O04-PhoneScreen" component={BareChat} defaultProps={{base: 6, heys: [mark('O04', 1)], askAt: mark('O04', 0)}} durationInFrames={shotFrames('O04')} fps={FPS} width={PW} height={PH} />
    <Composition id="M5-O18-Whiteboard" component={BoardAnim} defaultProps={{reveal: O18_REVEAL}} durationInFrames={shotFrames('O18')} fps={FPS} width={BOARD.w} height={BOARD.h} />
  </>
);


export const Root: React.FC = () => (
  <>
    <M5 />
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
