/** Editable daily fields — never hardcoded into artwork */
export type DailyContent = {
  date: string;
  greeting: string;
  weekday: string;
  readerName: string;
  readerHours: string;
  readerImage?: string;
  mainEvent: string;
  eventTime: string;
  secondaryEvents?: Array<{title: string; time: string}>;
  featuredCrystal?: string;
  featuredJewelry?: string;
  coffeeMessage?: string;
  callToAction?: string;
  templateId: string;
  colorPalette?: string;
  prideLine?: string;
  website?: string;
  phone?: string;
};

export type LayerAsset = {
  src: string;
  x: number;
  y: number;
  width: number;
  height: number;
  originX?: number;
  originY?: number;
  opacity?: number;
};

export type LayerManifest = {
  id: string;
  format: 'feed' | 'story';
  width: number;
  height: number;
  artHeight: number;
  /** Required transparent layers — see docs/LIVING-WORLDS-LAYER-PREP.md */
  layers: {
    backgroundPlate: string;
    foregroundFrame?: string;
    coffeeCup: string;
    coffeeSteam1: string;
    coffeeSteam2: string;
    coffeeSteam3?: string;
    candleBody: string;
    candleFlame: string;
    candleGlow: string;
    incenseHolder: string;
    incenseSmoke1: string;
    incenseSmoke2: string;
    incenseSmoke3?: string;
    heroCrystal: string;
    crystalHighlight?: string;
    crystalSparkle?: string;
    jewelry: string;
    reader?: string;
    readerHand?: string;
    cardFront: string;
    cardBack: string;
    openSign: string;
    lever?: string;
    kettle?: string;
    coffeeStream?: string;
    gear?: string;
    logo: string;
  };
  anchors: Record<string, {x: number; y: number} | Array<{x: number; y: number}>>;
  smokeSafeRegion?: {x: number; y: number; width: number; height: number};
  textSafeRegion?: {x: number; y: number; width: number; height: number};
};

export type PreviewMode = {
  showLayerBounds?: boolean;
  showAnchors?: boolean;
  showTransformOrigins?: boolean;
  showSafeAreas?: boolean;
  showFrameNumber?: boolean;
  showPhase?: boolean;
  reducedMotion?: boolean;
  loopBoundaryPreview?: boolean;
};
