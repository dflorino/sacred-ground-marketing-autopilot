import type {DailyContent, PreviewMode} from '../types/daily';

export const crystalMorningDaily: DailyContent = {
  templateId: 'living_crystal_morning_machine',
  date: 'August 24, 2026',
  greeting: 'GOOD MORNING',
  weekday: 'MONDAY',
  readerName: 'Lisa Maria Intuitive Tarot',
  readerHours: '12:00 PM – 5:00 PM',
  mainEvent: 'Lisa Maria Intuitive Tarot',
  eventTime: '12:00 PM – 5:00 PM',
  prideLine: "Chicagoland's #1 Metaphysical Shop",
  website: 'shopsacredground.com',
  phone: '847-749-3922',
  callToAction: 'Walk in · Arlington Heights',
};

export const LAYER_BASE = 'layers/crystal-morning-machine-2026-08-24';

export const crystalMachineLayers = {
  backgroundPlate: `${LAYER_BASE}/background-plate.png`,
  coffeeCup: `${LAYER_BASE}/coffee-cup.png`,
  coffeeSteam1: `${LAYER_BASE}/coffee-steam-1.png`,
  coffeeSteam2: `${LAYER_BASE}/coffee-steam-2.png`,
  coffeeSteam3: `${LAYER_BASE}/coffee-steam-3.png`,
  candleBody: `${LAYER_BASE}/candle-body.png`,
  candleFlame: `${LAYER_BASE}/candle-flame.png`,
  candleGlow: `${LAYER_BASE}/candle-glow.png`,
  incenseHolder: `${LAYER_BASE}/incense-holder.png`,
  incenseSmoke1: `${LAYER_BASE}/incense-smoke-1.png`,
  incenseSmoke2: `${LAYER_BASE}/incense-smoke-2.png`,
  heroCrystal: `${LAYER_BASE}/hero-crystal.png`,
  jewelry: `${LAYER_BASE}/pendant.png`,
  cardFront: `${LAYER_BASE}/card-front.png`,
  cardBack: `${LAYER_BASE}/card-back.png`,
  openSign: `${LAYER_BASE}/open-sign.png`,
  lever: `${LAYER_BASE}/lever.png`,
  kettle: `${LAYER_BASE}/kettle.png`,
  gear: `${LAYER_BASE}/gear.png`,
  logo: 'brand/sacred-ground-logo-circle-transparent.png',
};

/** Feed art-band coordinates (1080×980) */
export const crystalMachineAnchors = {
  crystalPath: [
    {x: 188, y: 248},
    {x: 248, y: 380},
    {x: 318, y: 520},
    {x: 385, y: 640},
  ],
  cup: {x: 720, y: 580},
  candleWick: {x: 548, y: 518},
  incenseTip: {x: 612, y: 468},
  pendantPivot: {x: 782, y: 292},
  card: {x: 385, y: 640},
  openSignHinge: {x: 130, y: 720},
  leverHinge: {x: 340, y: 580},
  kettleHinge: {x: 680, y: 420},
  pourStream: {x: 698, y: 460},
  gear: {x: 480, y: 500},
};

export const smokeSafeRegion = {x: 0, y: 0, width: 1080, height: 720};
export const textSafeRegion = {x: 0, y: 980, width: 1080, height: 370};

export const defaultPreviewMode: PreviewMode = {
  showFrameNumber: false,
  showAnchors: false,
  showSafeAreas: false,
  reducedMotion: false,
};

export const diagnosticPreviewMode: PreviewMode = {
  showFrameNumber: true,
  showAnchors: true,
  showTransformOrigins: true,
  showSafeAreas: true,
  showPhase: true,
  showLayerBounds: true,
  reducedMotion: false,
};
