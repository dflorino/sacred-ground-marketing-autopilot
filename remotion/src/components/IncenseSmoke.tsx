import React from 'react';
import {useCurrentFrame} from 'remotion';
import {periodSin} from '../lib/loop';
import {usePreviewMode} from '../context/PreviewContext';

export type SmokeLayerConfig = {
  id: string;
  periodFrames: number;
  phaseFrames: number;
  risePx: number;
  bendPx: number;
  width: number;
  opacityPeak: number;
};

export type IncenseSmokeProps = {
  tipX: number;
  tipY: number;
  layers?: SmokeLayerConfig[];
};

const DEFAULT_LAYERS: SmokeLayerConfig[] = [
  {id: 's1', periodFrames: 105, phaseFrames: 0, risePx: 220, bendPx: 28, width: 4, opacityPeak: 0.5},
  {id: 's2', periodFrames: 126, phaseFrames: 35, risePx: 260, bendPx: -22, width: 3, opacityPeak: 0.38},
  {id: 's3', periodFrames: 98, phaseFrames: 58, risePx: 180, bendPx: 18, width: 2.5, opacityPeak: 0.32},
];

/**
 * Incense smoke — tall, thin, directional SVG paths. Deforms per frame; resets only when invisible.
 * Base mask clips emergence from incense tip.
 */
export const IncenseSmoke: React.FC<IncenseSmokeProps> = ({
  tipX,
  tipY,
  layers = DEFAULT_LAYERS,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  if (reducedMotion) {
    return null;
  }

  return (
    <>
      {layers.map((layer) => {
        const localFrame = (frame + layer.phaseFrames) % layer.periodFrames;
        const t = localFrame / layer.periodFrames;

        let opacity = 0;
        if (t < 0.08) {
          opacity = (t / 0.08) * layer.opacityPeak;
        } else if (t < 0.7) {
          opacity = layer.opacityPeak;
        } else if (t < 0.96) {
          opacity = layer.opacityPeak * (1 - (t - 0.7) / 0.26);
        }

        if (opacity < 0.01) {
          return null;
        }

        const rise = -t * layer.risePx;
        const sway1 = periodSin(localFrame, layer.periodFrames, 0) * layer.bendPx;
        const sway2 = periodSin(localFrame, layer.periodFrames, 1.2) * layer.bendPx * 0.6;
        const h = Math.abs(rise) + 20;
        const blur = 1.5 + t * 3;
        const strokeW = layer.width * (1 + t * 0.4);

        const pathD = `M0 0 Q ${sway1 * 0.4} ${-h * 0.35}, ${sway1} ${-h * 0.55} T ${sway2} ${-h}`;

        return (
          <div
            key={layer.id}
            style={{
              position: 'absolute',
              left: tipX,
              top: tipY,
              width: 80,
              height: h + 10,
              overflow: 'hidden',
              opacity,
              pointerEvents: 'none',
            }}
          >
            {/* Narrow base mask — smoke emerges from tip */}
            <div
              style={{
                position: 'absolute',
                left: -8,
                top: 0,
                width: 16,
                height: 12,
                overflow: 'hidden',
              }}
            >
              <svg
                width={80}
                height={h + 10}
                style={{
                  position: 'absolute',
                  left: -36,
                  top: 0,
                  filter: `blur(${blur}px)`,
                }}
              >
                <path
                  d={pathD}
                  fill="none"
                  stroke="rgba(195,188,175,0.75)"
                  strokeWidth={strokeW}
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
        );
      })}
    </>
  );
};
