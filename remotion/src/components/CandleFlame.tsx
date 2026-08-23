import React from 'react';
import {useCurrentFrame} from 'remotion';
import {loopSin, periodSin, windowProgress} from '../lib/loop';
import {usePreviewMode} from '../context/PreviewContext';
import {LayerImage} from './LayerImage';

export type CandleFlameProps = {
  wickX: number;
  wickY: number;
  flameSrc?: string;
  glowSrc?: string;
  /** Frame when flame ignites (one-shot reveal) */
  igniteFrame?: number;
  flameWidth?: number;
  flameHeight?: number;
};

/**
 * Candle flame + separate glow. Transform origin at wick (bottom center).
 * Multiple oscillation frequencies — organic flicker, wick always attached.
 */
export const CandleFlame: React.FC<CandleFlameProps> = ({
  wickX,
  wickY,
  flameSrc,
  glowSrc,
  igniteFrame = 0,
  flameWidth = 24,
  flameHeight = 44,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  const ignite = igniteFrame > 0 ? windowProgress(frame, igniteFrame, igniteFrame + 12) : 1;
  if (ignite <= 0 || reducedMotion) {
    return null;
  }

  const scaleY = 0.96 + 0.04 * loopSin(frame, 5) + 0.02 * periodSin(frame, 17);
  const scaleX = 0.97 + 0.03 * loopSin(frame, 7) + 0.015 * periodSin(frame, 23, 0.5);
  const rotate = loopSin(frame, 3) * 1.2 + periodSin(frame, 31) * 0.4;
  const dx = loopSin(frame, 11) * 1.5;
  const dy = periodSin(frame, 19) * 1;
  const brightness = 1 + loopSin(frame, 4) * 0.06;
  const flameOpacity = 0.92 + loopSin(frame, 6) * 0.06;

  const glowScale = 1 + loopSin(frame, 1) * 0.035 + periodSin(frame, 90) * 0.015;
  const glowOpacity =
    (0.28 + loopSin(frame, 2) * 0.08) * Math.min(1, ignite * 1.5);

  const originX = flameWidth / 2;
  const originY = flameHeight;

  return (
    <>
      {/* Slower amber glow behind flame */}
      {glowSrc ? (
        <LayerImage
          src={glowSrc}
          x={wickX - flameWidth}
          y={wickY - flameHeight - 8}
          width={flameWidth * 2.2}
          height={flameHeight * 1.8}
          originX={flameWidth * 1.1}
          originY={flameHeight * 1.5}
          opacity={glowOpacity * ignite}
          scaleX={glowScale}
          scaleY={glowScale}
          blur={8}
        />
      ) : (
        <div
          style={{
            position: 'absolute',
            left: wickX - flameWidth,
            top: wickY - flameHeight - 12,
            width: flameWidth * 2.2,
            height: flameHeight * 1.6,
            borderRadius: '50%',
            background: `radial-gradient(ellipse, rgba(255,180,60,${glowOpacity * ignite}) 0%, rgba(255,100,20,0) 70%)`,
            filter: 'blur(10px)',
            pointerEvents: 'none',
          }}
        />
      )}

      {flameSrc ? (
        <LayerImage
          src={flameSrc}
          x={wickX - originX + dx}
          y={wickY - originY + dy}
          width={flameWidth}
          height={flameHeight}
          originX={originX}
          originY={originY}
          rotation={rotate}
          scaleX={scaleX * ignite}
          scaleY={scaleY * ignite}
          opacity={flameOpacity * ignite}
        />
      ) : (
        <div
          style={{
            position: 'absolute',
            left: wickX - originX + dx,
            top: wickY - originY + dy,
            width: flameWidth,
            height: flameHeight,
            transformOrigin: `${originX}px ${originY}px`,
            transform: `rotate(${rotate}deg) scale(${scaleX * ignite}, ${scaleY * ignite})`,
            opacity: flameOpacity * ignite,
            filter: `brightness(${brightness})`,
            pointerEvents: 'none',
          }}
        >
          <svg width={flameWidth} height={flameHeight} viewBox={`0 0 ${flameWidth} ${flameHeight}`}>
            <defs>
              <linearGradient id="sgFlame" x1="0" y1="1" x2="0" y2="0">
                <stop offset="0%" stopColor="#e85a00" />
                <stop offset="50%" stopColor="#ffb400" />
                <stop offset="100%" stopColor="#fff6d0" />
              </linearGradient>
            </defs>
            <path
              d={`M${flameWidth / 2} ${flameHeight} Q${flameWidth * 0.12} ${flameHeight * 0.5} ${flameWidth / 2} ${flameHeight * 0.08} Q${flameWidth * 0.88} ${flameHeight * 0.5} ${flameWidth / 2} ${flameHeight} Z`}
              fill="url(#sgFlame)"
            />
          </svg>
        </div>
      )}
    </>
  );
};

/** Glow-only export for layering order control */
export const CandleGlow: React.FC<Pick<CandleFlameProps, 'wickX' | 'wickY' | 'glowSrc' | 'igniteFrame' | 'flameWidth' | 'flameHeight'>> = (props) => {
  const frame = useCurrentFrame();
  const ignite = (props.igniteFrame ?? 0) > 0 ? windowProgress(frame, props.igniteFrame!, props.igniteFrame! + 18) : 1;
  const glowScale = 1 + loopSin(frame, 1) * 0.04;
  const glowOpacity = (0.3 + loopSin(frame, 2) * 0.07) * ignite;
  const fw = props.flameWidth ?? 24;
  const fh = props.flameHeight ?? 44;
  return (
    <div
      style={{
        position: 'absolute',
        left: props.wickX - fw,
        top: props.wickY - fh - 10,
        width: fw * 2.2,
        height: fh * 1.5,
        borderRadius: '50%',
        background: `radial-gradient(ellipse, rgba(255,175,50,${glowOpacity}) 0%, rgba(255,90,10,0) 72%)`,
        transform: `scale(${glowScale})`,
        transformOrigin: 'center bottom',
        filter: 'blur(12px)',
        pointerEvents: 'none',
      }}
    />
  );
};
