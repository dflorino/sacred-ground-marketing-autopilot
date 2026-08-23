/**
 * Deterministic pseudo-random — same seed + index = same value every render.
 * Never use Math.random() without a fixed seed.
 */
export const seeded = (seed: number, index: number): number => {
  const x = Math.sin(seed * 127.1 + index * 311.7) * 43758.5453;
  return x - Math.floor(x);
};
