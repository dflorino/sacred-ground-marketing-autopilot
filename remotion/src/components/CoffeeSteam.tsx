import React from 'react';
import {useCurrentFrame} from 'remotion';
import {periodSin} from '../lib/loop';
import {usePreviewMode} from '../context/PreviewContext';

export type SteamWispConfig = {
  id: string;
  offsetX: number;
  startY: number;
  width: number;
  height: number;
  periodFrames: number;
  phaseFrames: number;
  risePx: number;
  driftPx: number;
  opacityPeak: number;
};

export type CoffeeSteamProps = {
  anchorX: number;
  anchorY: number;
  wisps?: SteamWispConfig[];
};

const DEFAULT_WISPS: SteamWispConfig[] = [
  {
    id: 'a',
    offsetX: -14,
    startY: 0,
    width: 28,
    height: 52,
    periodFrames: 70,
    phaseFrames: 0,
    risePx: 90,
    driftPx: 10,
    opacityPeak: 0.42,
  },
  {
    id: 'b',
    offsetX: 6,
    startY: 4,
    width: 22,
    height: 48,
    periodFrames: 84,
    phaseFrames: 28,
    risePx: 110,
    driftPx: 14,
    opacityPeak: 0.35,
  },
  {
    id: 'c',
    offsetX: 20,
    startY: 2,
    width: 18,
    height: 44,
    periodFrames: 63,
    phaseFrames: 42,
    risePx: 75,
    driftPx: 8,
    opacityPeak: 0.3,
  },
];

/**
 * Coffee steam — 3 wisps, each completes fade-in → rise → drift → stretch → blur → fade-out → invisible reset.
 * Progress uses cycleProgress on per-wisp period; never visible during reset.
 */
export const CoffeeSteam: React.FC<CoffeeSteamProps> = ({
  anchorX,
  anchorY,
  wisps = DEFAULT_WISPS,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  if (reducedMotion) {
    return null;
  }

  return (
    <>
      {wisps.map((w) => {
        const localFrame = (frame + w.phaseFrames) % w.periodFrames;
        const t = localFrame / w.periodFrames;

        // Opacity: invisible at 0, peak mid-rise, invisible before reset
        let opacity = 0;
        if (t < 0.12) {
          opacity = (t / 0.12) * w.opacityPeak;
        } else if (t < 0.72) {
          opacity = w.opacityPeak * (1 - (t - 0.12) * 0.15);
        } else if (t < 0.95) {
          opacity = w.opacityPeak * (1 - (t - 0.72) / 0.23);
        }

        if (opacity < 0.01) {
          return null;
        }

        const rise = -t * w.risePx;
        const drift = periodSin(localFrame, w.periodFrames, 0.5) * w.driftPx;
        const stretchY = 1 + t * 0.55;
        const blur = 2 + t * 5;

        return (
          <div
            key={w.id}
            style={{
              position: 'absolute',
              left: anchorX + w.offsetX + drift,
              top: anchorY + w.startY + rise,
              width: w.width,
              height: w.height * stretchY,
              borderRadius: '50% 50% 42% 42%',
              background:
                'radial-gradient(ellipse at 50% 85%, rgba(255,252,245,0.65) 0%, rgba(235,228,215,0.15) 45%, rgba(255,255,255,0) 72%)',
              opacity,
              filter: `blur(${blur}px)`,
              transform: `rotate(${drift * 0.4}deg)`,
              pointerEvents: 'none',
            }}
          />
        );
      })}
    </>
  );
};
