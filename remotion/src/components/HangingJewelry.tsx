import React from 'react';
import {useCurrentFrame} from 'remotion';
import {loopSin, windowProgress} from '../lib/loop';
import {usePreviewMode} from '../context/PreviewContext';
import {LayerImage} from './LayerImage';

export type HangingJewelryProps = {
  src: string;
  pivotX: number;
  pivotY: number;
  width: number;
  height: number;
  maxSwingDeg?: number;
  phaseOffset?: number;
  /** One-shot swing window; if omitted, continuous gentle pendulum */
  swingStartFrame?: number;
  swingEndFrame?: number;
};

/**
 * Pendant / necklace — transform origin at chain attachment (top center).
 * Sine pendulum; optional one-shot damped swing.
 */
export const HangingJewelry: React.FC<HangingJewelryProps> = ({
  src,
  pivotX,
  pivotY,
  width,
  height,
  maxSwingDeg = 2,
  phaseOffset = 0,
  swingStartFrame,
  swingEndFrame,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  if (reducedMotion) {
    return (
      <LayerImage
        src={src}
        x={pivotX - width / 2}
        y={pivotY}
        width={width}
        height={height}
        originX={width / 2}
        originY={0}
      />
    );
  }

  let angle = loopSin(frame + phaseOffset, 1) * maxSwingDeg;

  if (swingStartFrame !== undefined && swingEndFrame !== undefined) {
    const swingT = windowProgress(frame, swingStartFrame, swingEndFrame);
    const damped = Math.sin(Math.PI * swingT);
    angle = maxSwingDeg * 3 * damped + loopSin(frame + phaseOffset, 2) * 0.8;
  }

  const microY = loopSin(frame + phaseOffset, 3) * 1.5;

  return (
    <LayerImage
      src={src}
      x={pivotX - width / 2}
      y={pivotY + microY}
      width={width}
      height={height}
      originX={width / 2}
      originY={0}
      rotation={angle}
    />
  );
};

/** Pair of earrings with phase offsets */
export type EarringPairProps = {
  leftSrc: string;
  rightSrc: string;
  leftPivot: {x: number; y: number};
  rightPivot: {x: number; y: number};
  size: number;
};

export const EarringPair: React.FC<EarringPairProps> = ({
  leftSrc,
  rightSrc,
  leftPivot,
  rightPivot,
  size,
}) => (
  <>
    <HangingJewelry
      src={leftSrc}
      pivotX={leftPivot.x}
      pivotY={leftPivot.y}
      width={size}
      height={size * 1.4}
      maxSwingDeg={3}
      phaseOffset={0}
    />
    <HangingJewelry
      src={rightSrc}
      pivotX={rightPivot.x}
      pivotY={rightPivot.y}
      width={size}
      height={size * 1.4}
      maxSwingDeg={2.5}
      phaseOffset={18}
    />
  </>
);
