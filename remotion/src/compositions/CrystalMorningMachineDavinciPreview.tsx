import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {FEED_H, FEED_W} from '../constants';
import {CoffeeSteam} from '../components/CoffeeSteam';
import {CandleFlame} from '../components/CandleFlame';
import {IncenseSmoke} from '../components/IncenseSmoke';
import {EventPanelDavinci} from '../components/EventPanelDavinci';
import {
  crystalMachineAnchors as A,
  crystalMorningDaily,
} from '../data/crystal-morning-machine-2026-08-24';

/** Machine scene only — no cream void from AI scene (745px crop @ 1024 source) */
const MACHINE_ART_H = 785;

/**
 * Founder preview — real machine art on top + Da Vinci panel on bottom.
 * No purple test grid. Motion is procedural until layer cutouts exist.
 */
export const CrystalMorningMachineDavinciPreview: React.FC = () => {
  const frame = useCurrentFrame();
  const daily = crystalMorningDaily;

  return (
    <AbsoluteFill style={{backgroundColor: '#1a1208'}}>
      <AbsoluteFill style={{height: MACHINE_ART_H, overflow: 'hidden'}}>
        <Img
          src={staticFile('previews/crystal-machine-art-band.png')}
          style={{
            width: FEED_W,
            height: MACHINE_ART_H,
            objectFit: 'fill',
          }}
        />
        {/* Soft edge into parchment panel */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 24,
            background: 'linear-gradient(180deg, transparent 0%, rgba(235,224,204,0.95) 100%)',
          }}
        />
        {frame >= 0 ? (
          <>
            <CoffeeSteam anchorX={A.cup.x} anchorY={A.cup.y - 30} />
            <CandleFlame
              wickX={A.candleWick.x}
              wickY={A.candleWick.y}
              igniteFrame={0}
            />
            {frame >= 90 ? (
              <IncenseSmoke tipX={A.incenseTip.x} tipY={A.incenseTip.y} />
            ) : null}
          </>
        ) : null}
      </AbsoluteFill>

      <EventPanelDavinci
        {...daily}
        logoSrc={staticFile('brand/sacred-ground-logo-circle-transparent.png')}
        top={MACHINE_ART_H}
        height={FEED_H - MACHINE_ART_H}
        enterStartFrame={0}
        enterEndFrame={1}
        prideLine="Chicagoland's Premier Crystal Store & Holistic Destination"
        callToAction="Book · Visit · Explore"
      />
    </AbsoluteFill>
  );
};
