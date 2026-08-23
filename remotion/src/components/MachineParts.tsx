import React from 'react';
import {useCurrentFrame} from 'remotion';
import {easeOutCubic} from '../lib/ease';
import {windowEased} from '../lib/loop';
import {LayerImage} from './LayerImage';

export type MachineLeverProps = {
  src: string;
  hingeX: number;
  hingeY: number;
  width: number;
  height: number;
  startFrame: number;
  endFrame: number;
  maxRotateDeg?: number;
};

export const MachineLever: React.FC<MachineLeverProps> = ({
  src,
  hingeX,
  hingeY,
  width,
  height,
  startFrame,
  endFrame,
  maxRotateDeg = -28,
}) => {
  const frame = useCurrentFrame();
  const t = windowEased(frame, startFrame, endFrame, easeOutCubic);

  return (
    <LayerImage
      src={src}
      x={hingeX}
      y={hingeY - height / 2}
      width={width}
      height={height}
      originX={0}
      originY={height / 2}
      rotation={t * maxRotateDeg}
    />
  );
};

export type KettlePourProps = {
  kettleSrc: string;
  streamMaskX: number;
  streamMaskY: number;
  streamHeight: number;
  hingeX: number;
  hingeY: number;
  width: number;
  height: number;
  tiltStartFrame: number;
  tiltEndFrame: number;
  pourStartFrame: number;
  pourEndFrame: number;
};

export const KettlePour: React.FC<KettlePourProps> = ({
  kettleSrc,
  streamMaskX,
  streamMaskY,
  streamHeight,
  hingeX,
  hingeY,
  width,
  height,
  tiltStartFrame,
  tiltEndFrame,
  pourStartFrame,
  pourEndFrame,
}) => {
  const frame = useCurrentFrame();
  const tiltT = windowEased(frame, tiltStartFrame, tiltEndFrame, easeOutCubic);
  const pourT = windowEased(frame, pourStartFrame, pourEndFrame, easeOutCubic);

  return (
    <>
      <LayerImage
        src={kettleSrc}
        x={hingeX - width * 0.85}
        y={hingeY - height / 2}
        width={width}
        height={height}
        originX={width * 0.85}
        originY={height / 2}
        rotation={tiltT * 32}
      />
      {pourT > 0 ? (
        <div
          style={{
            position: 'absolute',
            left: streamMaskX,
            top: streamMaskY,
            width: 8,
            height: streamHeight * pourT,
            overflow: 'hidden',
            borderRadius: 4,
          }}
        >
          <div
            style={{
              width: '100%',
              height: streamHeight,
              background:
                'linear-gradient(180deg, rgba(90,55,25,0.9) 0%, rgba(60,35,15,0.85) 100%)',
              borderRadius: 4,
            }}
          />
        </div>
      ) : null}
    </>
  );
};

export type GearTurnProps = {
  src: string;
  cx: number;
  cy: number;
  size: number;
  startFrame: number;
  endFrame: number;
  degrees?: number;
};

export const GearTurn: React.FC<GearTurnProps> = ({
  src,
  cx,
  cy,
  size,
  startFrame,
  endFrame,
  degrees = 45,
}) => {
  const frame = useCurrentFrame();
  const t = windowEased(frame, startFrame, endFrame, easeOutCubic);

  return (
    <LayerImage
      src={src}
      x={cx - size / 2}
      y={cy - size / 2}
      width={size}
      height={size}
      originX={size / 2}
      originY={size / 2}
      rotation={t * degrees}
    />
  );
};
