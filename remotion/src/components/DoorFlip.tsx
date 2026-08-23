import React from 'react';
import {useCurrentFrame} from 'remotion';
import {easeOutCubic} from '../lib/ease';
import {loopSin, windowEased, windowProgress} from '../lib/loop';
import {usePreviewMode} from '../context/PreviewContext';
import {LayerImage} from './LayerImage';

export type DoorFlipProps = {
  src: string;
  hingeX: number;
  hingeY: number;
  width: number;
  height: number;
  flipStartFrame: number;
  flipEndFrame: number;
  /** After flip, gentle pendulum from chain */
  pendulumDeg?: number;
};

/**
 * Door / OPEN sign — rotates around hinge (left edge), not center.
 */
export const DoorFlip: React.FC<DoorFlipProps> = ({
  src,
  hingeX,
  hingeY,
  width,
  height,
  flipStartFrame,
  flipEndFrame,
  pendulumDeg = 3,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  const flipT = reducedMotion
    ? 1
    : windowEased(frame, flipStartFrame, flipEndFrame, easeOutCubic);
  const flipAngle = flipT * -85;

  const settled = windowProgress(frame, flipEndFrame, flipEndFrame + 1) >= 1;
  const pendulum = settled ? loopSin(frame, 1) * pendulumDeg : 0;

  return (
    <LayerImage
      src={src}
      x={hingeX}
      y={hingeY - height / 2}
      width={width}
      height={height}
      originX={0}
      originY={height / 2}
      rotation={flipAngle + pendulum}
    />
  );
};

export type DrawerSlideProps = {
  src: string;
  trackX: number;
  trackY: number;
  width: number;
  height: number;
  slideStartFrame: number;
  slideEndFrame: number;
  slideDistancePx?: number;
};

/** Drawer slides along straight track with shadow depth shift */
export const DrawerSlide: React.FC<DrawerSlideProps> = ({
  src,
  trackX,
  trackY,
  width,
  height,
  slideStartFrame,
  slideEndFrame,
  slideDistancePx = 60,
}) => {
  const frame = useCurrentFrame();
  const t = windowEased(frame, slideStartFrame, slideEndFrame, easeOutCubic);
  const offset = t * slideDistancePx;
  const shadow = 2 + t * 4;

  return (
    <div style={{position: 'absolute', pointerEvents: 'none'}}>
      <LayerImage
        src={src}
        x={trackX + offset}
        y={trackY}
        width={width}
        height={height}
      />
      <div
        style={{
          position: 'absolute',
          left: trackX + offset + 4,
          top: trackY + height - 4,
          width: width - 8,
          height: 6,
          background: `rgba(0,0,0,${0.15 + t * 0.1})`,
          filter: `blur(${shadow}px)`,
        }}
      />
    </div>
  );
};
