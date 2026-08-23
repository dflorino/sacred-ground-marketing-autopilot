import React from 'react';
import {Composition} from 'remotion';
import {
  CrystalMorningMachine,
  CrystalMorningMachineDefault,
} from './compositions/CrystalMorningMachine';
import {MotionLaboratory} from './compositions/MotionLaboratory';
import {CrystalMorningMachineDavinciPreview} from './compositions/CrystalMorningMachineDavinciPreview';
import {LoopBoundaryPreview} from './compositions/LoopBoundaryPreview';
import {FEED_H, FEED_W, FPS, LOOP_FRAMES} from './constants';
import {diagnosticPreviewMode} from './data/crystal-morning-machine-2026-08-24';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MotionLaboratory"
        component={MotionLaboratory}
        durationInFrames={LOOP_FRAMES}
        fps={FPS}
        width={FEED_W}
        height={FEED_H}
        defaultProps={{previewMode: diagnosticPreviewMode}}
      />
      <Composition
        id="MotionLaboratoryReduced"
        component={MotionLaboratory}
        durationInFrames={LOOP_FRAMES}
        fps={FPS}
        width={FEED_W}
        height={FEED_H}
        defaultProps={{previewMode: {reducedMotion: true}}}
      />
      <Composition
        id="CrystalMorningMachine"
        component={CrystalMorningMachine}
        durationInFrames={LOOP_FRAMES}
        fps={FPS}
        width={FEED_W}
        height={FEED_H}
        defaultProps={{
          ...CrystalMorningMachineDefault,
          previewMode: {},
        }}
      />
      <Composition
        id="CrystalMorningMachineDiagnostics"
        component={CrystalMorningMachine}
        durationInFrames={LOOP_FRAMES}
        fps={FPS}
        width={FEED_W}
        height={FEED_H}
        defaultProps={{
          ...CrystalMorningMachineDefault,
          previewMode: diagnosticPreviewMode,
        }}
      />
      <Composition
        id="CrystalMorningMachineDavinciPreview"
        component={CrystalMorningMachineDavinciPreview}
        durationInFrames={LOOP_FRAMES}
        fps={FPS}
        width={FEED_W}
        height={FEED_H}
      />
      <Composition
        id="LoopBoundaryPreview"
        component={LoopBoundaryPreview}
        durationInFrames={40}
        fps={FPS}
        width={FEED_W}
        height={FEED_H}
        defaultProps={{target: 'CrystalMorningMachine' as const}}
      />
    </>
  );
};
