/** Inline SVG data URIs for Motion Laboratory (no external assets needed) */
export const labSvg = (svg: string): string =>
  `data:image/svg+xml,${encodeURIComponent(svg)}`;

export const LAB_CRYSTAL = labSvg(
  '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><polygon points="40,5 70,40 40,75 10,40" fill="rgba(180,220,255,0.9)"/></svg>',
);

export const LAB_PENDANT = labSvg(
  '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="64"><ellipse cx="24" cy="40" rx="18" ry="22" fill="#c0c0c0"/></svg>',
);

export const LAB_CARD_FRONT = labSvg(
  '<svg xmlns="http://www.w3.org/2000/svg" width="88" height="128"><rect width="88" height="128" fill="#4a2060"/><text x="44" y="70" text-anchor="middle" fill="#e8c060" font-size="14">STAR</text></svg>',
);

export const LAB_CARD_BACK = labSvg(
  '<svg xmlns="http://www.w3.org/2000/svg" width="88" height="128"><rect width="88" height="128" fill="#2a1830"/></svg>',
);

export const LAB_OPEN_SIGN = labSvg(
  '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="100"><rect width="80" height="100" fill="#6b4226"/><text x="40" y="55" text-anchor="middle" fill="#f5e6c8" font-size="16">OPEN</text></svg>',
);

export const LAB_DRAWER = labSvg(
  '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="50"><rect width="120" height="50" fill="#8b6914"/></svg>',
);
