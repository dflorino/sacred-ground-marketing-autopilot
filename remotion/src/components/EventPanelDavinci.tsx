import React from 'react';
import {Img, useCurrentFrame} from 'remotion';
import {easeOutBack} from '../lib/ease';
import {windowEased} from '../lib/loop';
import type {DailyContent} from '../types/daily';
import {usePreviewMode} from '../context/PreviewContext';

/** Mechanical / Vitruvian margin sketches — echoes the Morning Machine + Da Vinci pool */
const MarginSketches: React.FC = () => (
  <svg
    width="100%"
    height="100%"
    style={{position: 'absolute', inset: 0, opacity: 0.22, pointerEvents: 'none'}}
    viewBox="0 0 1080 370"
    preserveAspectRatio="xMidYMid slice"
  >
    {/* Gear — ties machine to notebook */}
    <circle cx="88" cy="90" r="34" fill="none" stroke="#3a2818" strokeWidth="1.2" />
    {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => (
      <line
        key={deg}
        x1={88 + Math.cos((deg * Math.PI) / 180) * 28}
        y1={90 + Math.sin((deg * Math.PI) / 180) * 28}
        x2={88 + Math.cos((deg * Math.PI) / 180) * 38}
        y2={90 + Math.sin((deg * Math.PI) / 180) * 38}
        stroke="#3a2818"
        strokeWidth="2"
      />
    ))}
    {/* Pulley */}
    <circle cx="980" cy="70" r="18" fill="none" stroke="#3a2818" strokeWidth="1" />
    <path d="M980 52 L980 30 M962 70 L940 70" stroke="#3a2818" strokeWidth="0.8" />
    {/* Compass */}
    <circle cx="1010" cy="200" r="22" fill="none" stroke="#3a2818" strokeWidth="0.9" />
    <path d="M1010 178 L1010 222 M988 200 L1032 200" stroke="#3a2818" strokeWidth="0.7" />
    {/* Arc / track sketch */}
    <path
      d="M40 280 Q 120 240, 200 270 T 360 260"
      fill="none"
      stroke="#3a2818"
      strokeWidth="0.8"
      strokeDasharray="4 3"
    />
    {/* Small crystal facet */}
    <polygon
      points="920,280 940,250 960,280 940,310"
      fill="none"
      stroke="#3a2818"
      strokeWidth="0.8"
    />
  </svg>
);

export type EventPanelDavinciProps = DailyContent & {
  top: number;
  height: number;
  logoSrc?: string;
  parchmentTextureSrc?: string;
  enterStartFrame?: number;
  enterEndFrame?: number;
};

/**
 * Leonardo notebook panel — parchment, ink margins, scroll pride ribbon.
 * Pairs with Living Worlds machine art on top; schedule stays live React text.
 */
export const EventPanelDavinci: React.FC<EventPanelDavinciProps> = ({
  greeting,
  weekday,
  date,
  readerName,
  readerHours,
  mainEvent,
  eventTime,
  secondaryEvents = [],
  prideLine = "Chicagoland's Premier Crystal Store & Holistic Destination",
  website = 'shopsacredground.com',
  phone = '847-749-3922',
  callToAction = 'Book · Visit · Explore',
  logoSrc,
  parchmentTextureSrc,
  top,
  height,
  enterStartFrame = 170,
  enterEndFrame = 190,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  const enterT =
    enterStartFrame > 0 && !reducedMotion
      ? windowEased(frame, enterStartFrame, enterEndFrame, easeOutBack)
      : 1;
  const slideY = (1 - enterT) * 24;

  const ink = '#1c1420';
  const eggplant = '#3a1c48';
  const sepia = '#5c4030';
  const gold = '#9a7340';

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        width: '100%',
        height,
        overflow: 'hidden',
        transform: `translateY(${slideY}px)`,
        opacity: enterStartFrame > 0 ? 0.4 + enterT * 0.6 : 1,
      }}
    >
      {/* Torn-edge transition from machine art */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 14,
          background:
            'linear-gradient(180deg, rgba(40,28,18,0.35) 0%, transparent 100%)',
          zIndex: 2,
        }}
      />

      {/* Parchment base */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `
            linear-gradient(175deg, #ebe0cc 0%, #dccdb5 35%, #e8dcc8 70%, #d4c4a8 100%)
          `,
        }}
      />
      {parchmentTextureSrc ? (
        <Img
          src={parchmentTextureSrc}
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 0.35,
            mixBlendMode: 'multiply',
          }}
        />
      ) : null}

      <MarginSketches />

      {/* Ink frame border */}
      <div
        style={{
          position: 'absolute',
          inset: 12,
          border: `1.5px solid ${sepia}`,
          borderRadius: 2,
          boxShadow: 'inset 0 0 0 1px rgba(90,64,48,0.15)',
          pointerEvents: 'none',
        }}
      />

      <div
        style={{
          position: 'relative',
          zIndex: 1,
          padding: '22px 36px 14px',
          fontFamily: 'Georgia, "Palatino Linotype", serif',
          color: ink,
          height: '100%',
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <div
            style={{
              fontSize: 38,
              fontWeight: 700,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: eggplant,
              lineHeight: 1.05,
            }}
          >
            {greeting}
          </div>
          <div
            style={{
              fontSize: 19,
              marginTop: 6,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: sepia,
              fontWeight: 600,
            }}
          >
            {weekday} · {date} · Sacred Ground
          </div>

          {/* Reader block — notebook ink, not empty cream */}
          <div
            style={{
              marginTop: 14,
              padding: '12px 16px',
              background: 'rgba(255,252,245,0.45)',
              border: `1px solid ${sepia}`,
              borderRadius: 2,
            }}
          >
            <div style={{fontSize: 22, fontWeight: 700, color: ink}}>
              Today&apos;s reader · {readerName}
            </div>
            <div style={{fontSize: 20, marginTop: 6, fontWeight: 600}}>{mainEvent}</div>
            <div style={{fontSize: 18, marginTop: 4, color: sepia}}>
              {eventTime} · Arlington Heights
            </div>
            {readerHours && readerHours !== eventTime ? (
              <div style={{fontSize: 16, marginTop: 4, opacity: 0.85}}>{readerHours}</div>
            ) : null}
          </div>

          {secondaryEvents.map((ev, i) => (
            <div key={i} style={{marginTop: 10, paddingLeft: 16, borderLeft: `2px solid ${gold}`}}>
              <div style={{fontSize: 17, fontWeight: 600}}>{ev.title}</div>
              <div style={{fontSize: 15, color: sepia}}>{ev.time}</div>
            </div>
          ))}

          {/* Pride scroll ribbon — Da Vinci pool style */}
          <div
            style={{
              marginTop: 12,
              padding: '8px 20px',
              background: `linear-gradient(90deg, transparent, rgba(212,196,168,0.9) 8%, rgba(232,220,200,0.95) 50%, rgba(212,196,168,0.9) 92%, transparent)`,
              borderTop: `1px solid ${gold}`,
              borderBottom: `1px solid ${gold}`,
              textAlign: 'center',
              fontSize: 14,
              fontWeight: 700,
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
              color: eggplant,
            }}
          >
            Sacred Ground — {prideLine}
          </div>
        </div>

        {/* Footer ink band */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderTop: `1.5px solid ${sepia}`,
            paddingTop: 10,
            marginTop: 8,
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
            {logoSrc ? (
              <Img src={logoSrc} style={{width: 40, height: 40, objectFit: 'contain'}} />
            ) : null}
            <div>
              <div style={{fontSize: 17, fontWeight: 600}}>{website}</div>
              <div style={{fontSize: 16, color: sepia}}>{phone}</div>
            </div>
          </div>
          <div
            style={{
              fontFamily: '"Snell Roundhand", "Brush Script MT", cursive',
              fontSize: 26,
              color: gold,
              fontStyle: 'italic',
            }}
          >
            {callToAction}
          </div>
        </div>
      </div>
    </div>
  );
};
