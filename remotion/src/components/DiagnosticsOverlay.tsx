import React from 'react';
import {useCurrentFrame} from 'remotion';
import {usePreviewMode} from '../context/PreviewContext';
import {cycleProgress} from '../lib/loop';
import {LOOP_FRAMES} from '../constants';

export const DiagnosticsOverlay: React.FC<{
  phase?: string;
  width: number;
  height: number;
  smokeSafe?: {x: number; y: number; width: number; height: number};
  textSafe?: {x: number; y: number; width: number; height: number};
  anchors?: Array<{label: string; x: number; y: number; color?: string}>;
}> = ({phase, width, height, smokeSafe, textSafe, anchors = []}) => {
  const frame = useCurrentFrame();
  const mode = usePreviewMode();

  if (
    !mode.showFrameNumber &&
    !mode.showPhase &&
    !mode.showAnchors &&
    !mode.showSafeAreas &&
    !mode.showLayerBounds
  ) {
    return null;
  }

  const progress = cycleProgress(frame);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 9999,
        fontFamily: 'monospace',
        fontSize: 13,
      }}
    >
      {mode.showFrameNumber ? (
        <div
          style={{
            position: 'absolute',
            top: 8,
            left: 8,
            background: 'rgba(0,0,0,0.75)',
            color: '#0f0',
            padding: '6px 10px',
            borderRadius: 4,
          }}
        >
          frame {frame} / {LOOP_FRAMES - 1} · cycle {(progress * 100).toFixed(1)}%
        </div>
      ) : null}
      {mode.showPhase && phase ? (
        <div
          style={{
            position: 'absolute',
            top: 8,
            right: 8,
            background: 'rgba(0,0,0,0.75)',
            color: '#ff0',
            padding: '6px 10px',
            borderRadius: 4,
          }}
        >
          {phase}
        </div>
      ) : null}
      {mode.showSafeAreas && smokeSafe ? (
        <div
          style={{
            position: 'absolute',
            left: smokeSafe.x,
            top: smokeSafe.y,
            width: smokeSafe.width,
            height: smokeSafe.height,
            border: '2px dashed rgba(100,200,255,0.8)',
            background: 'rgba(100,200,255,0.06)',
          }}
        />
      ) : null}
      {mode.showSafeAreas && textSafe ? (
        <div
          style={{
            position: 'absolute',
            left: textSafe.x,
            top: textSafe.y,
            width: textSafe.width,
            height: textSafe.height,
            border: '2px dashed rgba(255,180,100,0.9)',
            background: 'rgba(255,180,100,0.06)',
          }}
        />
      ) : null}
      {mode.showAnchors || mode.showTransformOrigins
        ? anchors.map((a) => (
            <div key={a.label}>
              <div
                style={{
                  position: 'absolute',
                  left: a.x - 5,
                  top: a.y - 5,
                  width: 10,
                  height: 10,
                  borderRadius: '50%',
                  background: a.color ?? '#f0f',
                  border: '2px solid #fff',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  left: a.x + 8,
                  top: a.y - 6,
                  color: a.color ?? '#f0f',
                  textShadow: '0 0 4px #000',
                  fontSize: 11,
                }}
              >
                {a.label}
              </div>
            </div>
          ))
        : null}
      {mode.showLayerBounds ? (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            border: '1px solid rgba(255,0,255,0.4)',
          }}
        />
      ) : null}
    </div>
  );
};
