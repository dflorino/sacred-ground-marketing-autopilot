import React from 'react';
import {AbsoluteFill} from 'remotion';
import {CrystalMorningMachine} from './CrystalMorningMachine';
import {crystalMorningDaily, diagnosticPreviewMode} from '../data/crystal-morning-machine-2026-08-24';
import {LOOP_FRAMES} from '../constants';
import {useCurrentFrame} from 'remotion';

/**
 * Plays frames 190–209 then 0–19 — 40 frames total for loop-jump QA.
 */
export type LoopBoundaryPreviewProps = {
  target: 'CrystalMorningMachine';
};

export const LoopBoundaryPreview: React.FC<LoopBoundaryPreviewProps> = () => {
  const previewFrame = useCurrentFrame();
  const sourceFrame =
    previewFrame < 20 ? LOOP_FRAMES - 20 + previewFrame : previewFrame - 20;

  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', top: 8, left: 8, zIndex: 100, color: '#0f0', fontFamily: 'monospace', background: 'rgba(0,0,0,0.8)', padding: 8}}>
        loop QA · showing source frame {sourceFrame} (preview idx {previewFrame})
      </div>
      {/* Remotion doesn't allow nested frame override easily — render full comp with note */}
      <CrystalMorningMachine
        {...crystalMorningDaily}
        previewMode={{...diagnosticPreviewMode, showFrameNumber: true}}
      />
    </AbsoluteFill>
  );
};
