/** Primary loop — 7s @ 30fps. Frame 0..209; frame 209 must connect to frame 0. */
export const FPS = 30;
export const LOOP_FRAMES = 210;
export const LOOP_SECONDS = LOOP_FRAMES / FPS;

/** Feed + static cover */
export const FEED_W = 1080;
export const FEED_H = 1350;

/** Story / Reel */
export const STORY_W = 1080;
export const STORY_H = 1920;

/** Art band — machine scene fills top; panel sits directly below (no cream gap) */
export const ART_H = 1000;
export const PANEL_H = FEED_H - ART_H;
