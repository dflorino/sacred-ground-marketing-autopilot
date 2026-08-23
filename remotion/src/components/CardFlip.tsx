import React from 'react';
import {useCurrentFrame} from 'remotion';
import {easeOutCubic} from '../lib/ease';
import {windowEased} from '../lib/loop';
import {usePreviewMode} from '../context/PreviewContext';
import {LayerImage} from './LayerImage';

export type CardFlipProps = {
  frontSrc: string;
  backSrc: string;
  x: number;
  y: number;
  width: number;
  height: number;
  flipStartFrame: number;
  flipEndFrame: number;
};

/**
 * Card Y-axis flip — back first half, switch at edge-on, front second half.
 * Perspective preserved; small shadow grounds the card.
 */
export const CardFlip: React.FC<CardFlipProps> = ({
  frontSrc,
  backSrc,
  x,
  y,
  width,
  height,
  flipStartFrame,
  flipEndFrame,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  const t = reducedMotion
    ? 1
    : windowEased(frame, flipStartFrame, flipEndFrame, easeOutCubic);
  const rotateY = t * 180;
  const showFront = rotateY >= 90;
  const displayY = showFront ? rotateY - 180 : rotateY;
  const src = showFront ? frontSrc : backSrc;
  const shadowBlur = 4 + Math.sin((rotateY * Math.PI) / 180) * 6;

  return (
    <div
      style={{
        position: 'absolute',
        left: x - width / 2,
        top: y - height / 2,
        width,
        height,
        perspective: 900,
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          transformStyle: 'preserve-3d',
          transform: `rotateY(${displayY}deg)`,
          filter: `drop-shadow(0 ${shadowBlur}px ${shadowBlur}px rgba(0,0,0,0.35))`,
        }}
      >
        <LayerImage src={src} x={0} y={0} width={width} height={height} />
      </div>
    </div>
  );
};
