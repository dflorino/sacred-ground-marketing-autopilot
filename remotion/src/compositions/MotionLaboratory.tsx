import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {ART_H, FEED_H, FEED_W} from '../constants';
import {CoffeeSteam} from '../components/CoffeeSteam';
import {IncenseSmoke} from '../components/IncenseSmoke';
import {CandleFlame} from '../components/CandleFlame';
import {CrystalSparkle} from '../components/CrystalSparkle';
import {HangingJewelry} from '../components/HangingJewelry';
import {CardFlip} from '../components/CardFlip';
import {DoorFlip, DrawerSlide} from '../components/DoorFlip';
import {EventPanelDavinci} from '../components/EventPanelDavinci';
import {DiagnosticsOverlay} from '../components/DiagnosticsOverlay';
import {PreviewProvider, usePreviewMode} from '../context/PreviewContext';
import type {PreviewMode} from '../types/daily';
import {crystalMorningDaily} from '../data/crystal-morning-machine-2026-08-24';
import {
  LAB_CARD_BACK,
  LAB_CARD_FRONT,
  LAB_CRYSTAL,
  LAB_DRAWER,
  LAB_OPEN_SIGN,
  LAB_PENDANT,
} from '../data/motion-lab-assets';

export type MotionLaboratoryProps = {
  previewMode?: PreviewMode;
};

const LabZone: React.FC<{
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
  children: React.ReactNode;
}> = ({label, x, y, w, h, children}) => {
  const mode = usePreviewMode();
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        border: mode.showLayerBounds ? '1px solid rgba(255,0,255,0.5)' : undefined,
        background: 'rgba(255,255,255,0.04)',
      }}
    >
      {mode.showLayerBounds ? (
        <div
          style={{
            position: 'absolute',
            top: 4,
            left: 6,
            fontSize: 11,
            color: '#ccc',
            fontFamily: 'monospace',
          }}
        >
          {label}
        </div>
      ) : null}
      {children}
    </div>
  );
};

const MotionLabInner: React.FC = () => {
  const frame = useCurrentFrame();
  const mode = usePreviewMode();

  let phase = 'idle';
  if (frame < 30) phase = 'steam + smoke';
  else if (frame < 60) phase = 'candle + crystal';
  else if (frame < 90) phase = 'jewelry + card';
  else if (frame < 120) phase = 'door + drawer';
  else phase = 'event panel';

  return (
    <AbsoluteFill style={{background: 'linear-gradient(160deg, #2a1f14 0%, #4a3520 50%, #1a1208 100%)'}}>
      <LabZone label="CoffeeSteam" x={40} y={60} w={240} h={200}>
        <div
          style={{
            position: 'absolute',
            bottom: 20,
            left: 80,
            width: 70,
            height: 50,
            background: '#8b6914',
            borderRadius: '0 0 12px 12px',
          }}
        />
        <CoffeeSteam anchorX={115} anchorY={100} />
      </LabZone>

      <LabZone label="IncenseSmoke" x={300} y={60} w={200} h={280}>
        <div
          style={{
            position: 'absolute',
            bottom: 30,
            left: 90,
            width: 8,
            height: 60,
            background: '#5c4030',
          }}
        />
        <IncenseSmoke tipX={94} tipY={90} />
      </LabZone>

      <LabZone label="CandleFlame+Glow" x={520} y={60} w={200} h={220}>
        <div
          style={{
            position: 'absolute',
            bottom: 20,
            left: 70,
            width: 36,
            height: 80,
            background: '#f5e6c8',
            borderRadius: 4,
          }}
        />
        <CandleFlame wickX={88} wickY={120} igniteFrame={15} />
      </LabZone>

      <LabZone label="CrystalSparkle" x={740} y={60} w={280} h={220}>
        <CrystalSparkle
          crystalSrc={LAB_CRYSTAL}
          x={140}
          y={110}
          width={72}
          height={72}
        />
      </LabZone>

      <LabZone label="HangingJewelry" x={40} y={300} w={200} h={200}>
        <div
          style={{
            position: 'absolute',
            top: 20,
            left: 95,
            width: 2,
            height: 40,
            background: '#aaa',
          }}
        />
        <HangingJewelry
          src={LAB_PENDANT}
          pivotX={100}
          pivotY={60}
          width={48}
          height={80}
          maxSwingDeg={3}
        />
      </LabZone>

      <LabZone label="CardFlip" x={260} y={300} w={200} h={220}>
        <CardFlip
          frontSrc={LAB_CARD_FRONT}
          backSrc={LAB_CARD_BACK}
          x={100}
          y={110}
          width={88}
          height={128}
          flipStartFrame={30}
          flipEndFrame={75}
        />
      </LabZone>

      <LabZone label="DoorFlip" x={480} y={300} w={220} h={200}>
        <DoorFlip
          src={LAB_OPEN_SIGN}
          hingeX={30}
          hingeY={100}
          width={80}
          height={100}
          flipStartFrame={40}
          flipEndFrame={90}
        />
      </LabZone>

      <LabZone label="DrawerSlide" x={720} y={300} w={300} h={200}>
        <div
          style={{
            position: 'absolute',
            left: 40,
            top: 80,
            width: 200,
            height: 80,
            background: '#3d2817',
            borderRadius: 4,
          }}
        />
        <DrawerSlide
          src={LAB_DRAWER}
          trackX={80}
          trackY={95}
          width={120}
          height={50}
          slideStartFrame={50}
          slideEndFrame={100}
        />
      </LabZone>

      <div
        style={{
          position: 'absolute',
          left: 0,
          top: ART_H - 40,
          width: FEED_W,
          height: FEED_H - ART_H + 40,
        }}
      >
        <EventPanelDavinci
          {...crystalMorningDaily}
          top={0}
          height={FEED_H - ART_H}
          enterStartFrame={120}
          enterEndFrame={150}
        />
      </div>

      <DiagnosticsOverlay
        phase={phase}
        width={FEED_W}
        height={FEED_H}
        anchors={[
          {label: 'cup', x: 155, y: 160, color: '#0ff'},
          {label: 'wick', x: 608, y: 180, color: '#fa0'},
          {label: 'pivot', x: 140, y: 360, color: '#f0f'},
        ]}
      />
    </AbsoluteFill>
  );
};

export const MotionLaboratory: React.FC<MotionLaboratoryProps> = ({
  previewMode = {},
}) => (
  <PreviewProvider mode={previewMode}>
    <MotionLabInner />
  </PreviewProvider>
);
