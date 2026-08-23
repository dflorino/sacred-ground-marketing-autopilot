import React from 'react';
import {useCurrentFrame} from 'remotion';
import {cycleProgress, loopSin, pointOnPath, rollRotation, windowProgress} from '../lib/loop';
import {seeded} from '../lib/seed';
import {usePreviewMode} from '../context/PreviewContext';
import {LayerImage} from './LayerImage';

export type SparkleConfig = {
  id: string;
  x: number;
  y: number;
  phaseFrames: number;
  periodFrames: number;
};

export type CrystalSparkleProps = {
  crystalSrc: string;
  highlightSrc?: string;
  x: number;
  y: number;
  width: number;
  height: number;
  /** Rolling path — if omitted, crystal stays put with highlight/sparkle only */
  path?: Array<{x: number; y: number}>;
  rollStartFrame?: number;
  rollEndFrame?: number;
  radiusPx?: number;
  sparkles?: SparkleConfig[];
};

/**
 * Hero crystal — solid, minimal motion. Highlight sweep + 2–3 timed sparkles.
 * Rolling mode: rotation matches distance traveled.
 */
export const CrystalSparkle: React.FC<CrystalSparkleProps> = ({
  crystalSrc,
  highlightSrc,
  x,
  y,
  width,
  height,
  path,
  rollStartFrame = 20,
  rollEndFrame = 50,
  radiusPx = 28,
  sparkles,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  let posX = x;
  let posY = y;
  let rollDeg = 0;

  if (path && path.length > 1) {
    const rollT = windowProgress(frame, rollStartFrame, rollEndFrame);
    const pt = pointOnPath(path, rollT);
    posX = pt.x;
    posY = pt.y;
    const totalDist =
      path.reduce((acc, p, i) => {
        if (i === 0) return 0;
        const prev = path[i - 1];
        return acc + Math.hypot(p.x - prev.x, p.y - prev.y);
      }, 0) * rollT;
    rollDeg = (rollRotation(totalDist, radiusPx) * 180) / Math.PI;
  } else if (!reducedMotion) {
    rollDeg = loopSin(frame, 1) * 1.2;
  }

  const depthScale = 1 + loopSin(frame, 1) * 0.01;

  const defaultSparkles: SparkleConfig[] = [
    {id: 'sp1', x: width * 0.35, y: height * 0.25, phaseFrames: 12, periodFrames: 70},
    {id: 'sp2', x: width * 0.7, y: height * 0.45, phaseFrames: 45, periodFrames: 84},
  ];
  const sparkleList = sparkles ?? defaultSparkles;

  const highlightX = reducedMotion
    ? 0
    : loopSin(frame, 1) * width * 0.15;

  return (
    <>
      <LayerImage
        src={crystalSrc}
        x={posX - width / 2}
        y={posY - height / 2}
        width={width}
        height={height}
        originX={width / 2}
        originY={height / 2}
        rotation={rollDeg}
        scaleX={depthScale}
        scaleY={depthScale}
      />

      {highlightSrc && !reducedMotion ? (
        <LayerImage
          src={highlightSrc}
          x={posX - width / 2 + highlightX}
          y={posY - height / 2}
          width={width * 0.35}
          height={height}
          opacity={0.35 + loopSin(frame, 2) * 0.15}
        />
      ) : !reducedMotion ? (
        <div
          style={{
            position: 'absolute',
            left: posX - width * 0.12 + highlightX,
            top: posY - height * 0.35,
            width: width * 0.22,
            height: height * 0.7,
            background:
              'linear-gradient(105deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.45) 50%, rgba(255,255,255,0) 100%)',
            opacity: 0.5 + loopSin(frame, 2) * 0.2,
            transform: `rotate(${loopSin(frame, 1) * 3}deg)`,
            pointerEvents: 'none',
          }}
        />
      ) : null}

      {!reducedMotion &&
        sparkleList.map((sp) => {
          const lf = (frame + sp.phaseFrames) % sp.periodFrames;
          const t = lf / sp.periodFrames;
          let opacity = 0;
          let scale = 0.2;
          if (t > 0.1 && t < 0.25) {
            const lt = (t - 0.1) / 0.15;
            opacity = lt * 0.9;
            scale = 0.2 + lt * 0.8;
          } else if (t >= 0.25 && t < 0.4) {
            opacity = 0.9;
            scale = 1;
          } else if (t >= 0.4 && t < 0.55) {
            const lt = (t - 0.4) / 0.15;
            opacity = 0.9 * (1 - lt);
            scale = 1 - lt * 0.5;
          }

          if (opacity < 0.02) return null;

          const jitter = seeded(42, sp.phaseFrames) * 4;

          return (
            <div
              key={sp.id}
              style={{
                position: 'absolute',
                left: posX - width / 2 + sp.x + jitter,
                top: posY - height / 2 + sp.y,
                width: 14 * scale,
                height: 14 * scale,
                opacity,
                background:
                  'radial-gradient(circle, rgba(255,255,255,0.95) 0%, rgba(200,230,255,0.4) 40%, transparent 70%)',
                transform: `rotate(45deg) scale(${scale})`,
                pointerEvents: 'none',
              }}
            />
          );
        })}
    </>
  );
};
