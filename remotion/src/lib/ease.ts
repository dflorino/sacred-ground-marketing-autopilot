/** Ease-out for one-shot actions (panel slide, card flip settle). Not for continuous loops. */
export const easeOutCubic = (t: number): number => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3);

export const easeOutQuad = (t: number): number => {
  const x = Math.min(1, Math.max(0, t));
  return 1 - (1 - x) * (1 - x);
};

/** Optional 2–3px overshoot for panel settle */
export const easeOutBack = (t: number, overshoot = 0.08): number => {
  const x = Math.min(1, Math.max(0, t));
  const c1 = 1 + overshoot;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};
