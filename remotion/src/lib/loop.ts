import {LOOP_FRAMES} from '../constants';

/**
 * Frame-based loop math only.
 * No CSS animations, timers, rAF, or wall-clock libraries.
 *
 * Continuous elements must match at frame 0 and frame LOOP_FRAMES - 1.
 */

/** Repeating progress in [0, 1) — used for steam, smoke, sparkles, rolling crystals */
export const cycleProgress = (
  frame: number,
  total: number = LOOP_FRAMES,
): number => {
  const f = ((frame % total) + total) % total;
  return f / total;
};

/**
 * Sine over one or more full periods within `periodFrames`.
 * Returns to start when frame wraps — seamless for integer periods dividing the loop.
 */
export const periodSin = (
  frame: number,
  periodFrames: number,
  phase = 0,
): number => {
  const f = ((frame % periodFrames) + periodFrames) % periodFrames;
  return Math.sin((2 * Math.PI * f) / periodFrames + phase);
};

export const periodCos = (
  frame: number,
  periodFrames: number,
  phase = 0,
): number => {
  const f = ((frame % periodFrames) + periodFrames) % periodFrames;
  return Math.cos((2 * Math.PI * f) / periodFrames + phase);
};

/** Full-loop sine — `cycles` complete periods across LOOP_FRAMES */
export const loopSin = (frame: number, cycles = 1): number => {
  return Math.sin((2 * Math.PI * cycles * frame) / LOOP_FRAMES);
};

export const loopCos = (frame: number, cycles = 1): number => {
  return Math.cos((2 * Math.PI * cycles * frame) / LOOP_FRAMES);
};

/** One-shot action between frame indices (inclusive start, exclusive end) */
export const windowProgress = (
  frame: number,
  startFrame: number,
  endFrame: number,
): number => {
  if (frame < startFrame) {
    return 0;
  }
  if (frame >= endFrame) {
    return 1;
  }
  return (frame - startFrame) / (endFrame - startFrame);
};

/** Map window progress through ease (one-shot only) */
export const windowEased = (
  frame: number,
  startFrame: number,
  endFrame: number,
  ease: (t: number) => number,
): number => ease(windowProgress(frame, startFrame, endFrame));

/** Linear interpolate */
export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;

/** Point along polyline path, t in [0,1] */
export const pointOnPath = (
  path: Array<{x: number; y: number}>,
  t: number,
): {x: number; y: number} => {
  if (path.length === 0) {
    return {x: 0, y: 0};
  }
  if (path.length === 1 || t <= 0) {
    return path[0];
  }
  if (t >= 1) {
    return path[path.length - 1];
  }
  const seg = t * (path.length - 1);
  const i = Math.min(Math.floor(seg), path.length - 2);
  const local = seg - i;
  return {
    x: lerp(path[i].x, path[i + 1].x, local),
    y: lerp(path[i].y, path[i + 1].y, local),
  };
};

/** Rolling rotation (radians) from distance traveled along circular cross-section */
export const rollRotation = (distancePx: number, radiusPx: number): number =>
  radiusPx > 0 ? distancePx / radiusPx : 0;
