import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {ART_H, FEED_H, FEED_W} from '../constants';
import {CoffeeSteam} from '../components/CoffeeSteam';
import {IncenseSmoke} from '../components/IncenseSmoke';
import {CandleFlame} from '../components/CandleFlame';
import {CrystalSparkle} from '../components/CrystalSparkle';
import {HangingJewelry} from '../components/HangingJewelry';
import {CardFlip} from '../components/CardFlip';
import {DoorFlip} from '../components/DoorFlip';
import {EventPanelDavinci} from '../components/EventPanelDavinci';
import {DiagnosticsOverlay} from '../components/DiagnosticsOverlay';
import {GearTurn, KettlePour, MachineLever} from '../components/MachineParts';
import {LayerImage} from '../components/LayerImage';
import {PreviewProvider} from '../context/PreviewContext';
import {loopSin, windowProgress} from '../lib/loop';
import type {DailyContent, PreviewMode} from '../types/daily';
import {
  crystalMachineAnchors as A,
  crystalMachineLayers as L,
  crystalMorningDaily,
  smokeSafeRegion,
  textSafeRegion,
} from '../data/crystal-morning-machine-2026-08-24';

export type CrystalMorningMachineProps = DailyContent & {
  previewMode?: PreviewMode;
};

/**
 * Crystal Morning Machine — layered Remotion template.
 * Requires decomposed transparent layers (see docs/LIVING-WORLDS-LAYER-PREP.md).
 * All motion from frame index; no flat-image pan/zoom.
 */
const CrystalMorningMachineInner: React.FC<DailyContent> = (daily) => {
  const frame = useCurrentFrame();

  const steamBoost = frame >= 75 && frame < 110 ? 1.25 : 1;
  const phase =
    frame < 20
      ? 'rest + steam'
      : frame < 50
        ? 'crystal roll'
        : frame < 90
          ? 'lever + kettle'
          : frame < 120
            ? 'gear + candle'
            : frame < 160
              ? 'incense + jewelry'
              : frame < 185
                ? 'card + sign'
                : 'settle + loop cover';

  // Soft steam crossing frames 195–209 reconnects loop (no full-scene reverse)
  const loopCoverOpacity =
    frame >= 195 ? windowProgress(frame, 195, 209) * 0.35 * (1 - loopSin(frame, 1) * 0.5 + 0.5) : 0;

  return (
    <AbsoluteFill style={{backgroundColor: '#1a1208'}}>
      {/* Art band */}
      <AbsoluteFill style={{height: ART_H, overflow: 'hidden'}}>
        <Img
          src={staticFile(L.backgroundPlate)}
          style={{width: FEED_W, height: ART_H, objectFit: 'cover'}}
        />

        <CrystalSparkle
          crystalSrc={staticFile(L.heroCrystal)}
          x={A.crystalPath[0].x}
          y={A.crystalPath[0].y}
          width={72}
          height={72}
          path={A.crystalPath}
          rollStartFrame={20}
          rollEndFrame={50}
          radiusPx={28}
        />

        <MachineLever
          src={staticFile(L.lever)}
          hingeX={A.leverHinge.x}
          hingeY={A.leverHinge.y}
          width={90}
          height={40}
          startFrame={45}
          endFrame={70}
        />

        <KettlePour
          kettleSrc={staticFile(L.kettle)}
          streamMaskX={A.pourStream.x}
          streamMaskY={A.pourStream.y}
          streamHeight={100}
          hingeX={A.kettleHinge.x}
          hingeY={A.kettleHinge.y}
          width={100}
          height={80}
          tiltStartFrame={60}
          tiltEndFrame={90}
          pourStartFrame={68}
          pourEndFrame={95}
        />

        <LayerImage
          src={staticFile(L.coffeeCup)}
          x={A.cup.x - 40}
          y={A.cup.y - 35}
          width={80}
          height={70}
        />
        <div style={{opacity: steamBoost}}>
          <CoffeeSteam anchorX={A.cup.x} anchorY={A.cup.y - 20} />
        </div>

        <LayerImage
          src={staticFile(L.candleBody)}
          x={A.candleWick.x - 20}
          y={A.candleWick.y - 70}
          width={40}
          height={80}
        />
        <GearTurn
          src={staticFile(L.gear)}
          cx={A.gear.x}
          cy={A.gear.y}
          size={48}
          startFrame={90}
          endFrame={120}
        />
        <CandleFlame
          wickX={A.candleWick.x}
          wickY={A.candleWick.y}
          flameSrc={staticFile(L.candleFlame)}
          glowSrc={staticFile(L.candleGlow)}
          igniteFrame={96}
        />

        <LayerImage
          src={staticFile(L.incenseHolder)}
          x={A.incenseTip.x - 14}
          y={A.incenseTip.y - 50}
          width={28}
          height={55}
        />
        {frame >= 105 ? <IncenseSmoke tipX={A.incenseTip.x} tipY={A.incenseTip.y} /> : null}

        <HangingJewelry
          src={staticFile(L.jewelry)}
          pivotX={A.pendantPivot.x}
          pivotY={A.pendantPivot.y}
          width={64}
          height={120}
          maxSwingDeg={2.5}
          swingStartFrame={120}
          swingEndFrame={160}
        />

        <CardFlip
          frontSrc={staticFile(L.cardFront)}
          backSrc={staticFile(L.cardBack)}
          x={A.card.x}
          y={A.card.y}
          width={88}
          height={128}
          flipStartFrame={140}
          flipEndFrame={175}
        />

        <DoorFlip
          src={staticFile(L.openSign)}
          hingeX={A.openSignHinge.x}
          hingeY={A.openSignHinge.y}
          width={100}
          height={48}
          flipStartFrame={155}
          flipEndFrame={185}
        />

        {/* Loop-cover steam — natural wipe, not scene reverse */}
        {loopCoverOpacity > 0 ? (
          <div style={{opacity: loopCoverOpacity, pointerEvents: 'none'}}>
            <CoffeeSteam anchorX={FEED_W * 0.5} anchorY={ART_H * 0.45} />
          </div>
        ) : null}
      </AbsoluteFill>

      <EventPanelDavinci
        {...daily}
        logoSrc={staticFile(L.logo)}
        top={ART_H}
        height={FEED_H - ART_H}
        enterStartFrame={170}
        enterEndFrame={190}
      />

      <DiagnosticsOverlay
        phase={phase}
        width={FEED_W}
        height={FEED_H}
        smokeSafe={smokeSafeRegion}
        textSafe={textSafeRegion}
        anchors={[
          {label: 'crystal', x: A.crystalPath[0].x, y: A.crystalPath[0].y},
          {label: 'wick', x: A.candleWick.x, y: A.candleWick.y},
          {label: 'incense', x: A.incenseTip.x, y: A.incenseTip.y},
          {label: 'pendant', x: A.pendantPivot.x, y: A.pendantPivot.y},
          {label: 'card', x: A.card.x, y: A.card.y},
        ]}
      />
    </AbsoluteFill>
  );
};

export const CrystalMorningMachine: React.FC<CrystalMorningMachineProps> = ({
  previewMode = {},
  ...daily
}) => (
  <PreviewProvider mode={previewMode}>
    <CrystalMorningMachineInner {...daily} />
  </PreviewProvider>
);

export const CrystalMorningMachineDefault = crystalMorningDaily;
