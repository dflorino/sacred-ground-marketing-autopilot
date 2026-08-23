import React from 'react';
import {Img, useCurrentFrame} from 'remotion';
import {easeOutBack} from '../lib/ease';
import {windowEased} from '../lib/loop';
import type {DailyContent} from '../types/daily';
import {usePreviewMode} from '../context/PreviewContext';

export type EventPanelProps = DailyContent & {
  top: number;
  height: number;
  logoSrc?: string;
  /** Slide-in from below — one-shot, then still */
  enterStartFrame?: number;
  enterEndFrame?: number;
  slideOffsetPx?: number;
};

/**
 * Live React text — greeting visible from frame 0.
 * Optional slide-in for secondary reveal; greeting/date never wait.
 */
export const EventPanel: React.FC<EventPanelProps> = ({
  greeting,
  weekday,
  date,
  readerName,
  readerHours,
  mainEvent,
  eventTime,
  secondaryEvents = [],
  prideLine = "Chicagoland's #1 Metaphysical Shop",
  website = 'shopsacredground.com',
  phone = '847-749-3922',
  callToAction,
  logoSrc,
  top,
  height,
  enterStartFrame = 170,
  enterEndFrame = 190,
  slideOffsetPx = 28,
}) => {
  const frame = useCurrentFrame();
  const {reducedMotion} = usePreviewMode();

  const enterT =
    enterStartFrame > 0 && !reducedMotion
      ? windowEased(frame, enterStartFrame, enterEndFrame, easeOutBack)
      : 1;
  const translateY = (1 - enterT) * slideOffsetPx;
  const extraOpacity = enterStartFrame > 0 ? enterT : 1;

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        width: '100%',
        height,
        background: 'linear-gradient(180deg, #f5f0e6 0%, #ebe4d4 100%)',
        fontFamily: 'Georgia, "Times New Roman", serif',
        color: '#1a1208',
        padding: '16px 28px 10px',
        boxSizing: 'border-box',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        transform: `translateY(${translateY}px)`,
        opacity: extraOpacity,
      }}
    >
      <div>
        <div
          style={{
            fontSize: 28,
            fontWeight: 800,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
          }}
        >
          {greeting}
        </div>
        <div style={{fontSize: 20, marginTop: 4, fontWeight: 600}}>
          {weekday} · {date}
        </div>
        <div
          style={{
            fontSize: 22,
            marginTop: 10,
            fontStyle: 'italic',
            color: '#4a3520',
          }}
        >
          {readerName}
        </div>
        <div style={{fontSize: 17, marginTop: 4, opacity: 0.9}}>{readerHours}</div>
        <div style={{marginTop: 12}}>
          <div style={{fontSize: 18, fontWeight: 700}}>{mainEvent}</div>
          <div style={{fontSize: 16, opacity: 0.85}}>{eventTime}</div>
        </div>
        {secondaryEvents.map((ev, i) => (
          <div key={i} style={{marginTop: 8}}>
            <div style={{fontSize: 16, fontWeight: 600}}>{ev.title}</div>
            <div style={{fontSize: 14, opacity: 0.85}}>{ev.time}</div>
          </div>
        ))}
        {prideLine ? (
          <div
            style={{
              marginTop: 10,
              fontSize: 13,
              fontWeight: 700,
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              color: '#6b4e2a',
            }}
          >
            {prideLine}
          </div>
        ) : null}
        {callToAction ? (
          <div style={{marginTop: 8, fontSize: 15, fontWeight: 600}}>{callToAction}</div>
        ) : null}
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 14,
          borderTop: '2px solid rgba(26,18,8,0.12)',
          paddingTop: 8,
          fontSize: 17,
          fontWeight: 600,
        }}
      >
        {logoSrc ? (
          <Img src={logoSrc} style={{width: 42, height: 42, objectFit: 'contain'}} />
        ) : null}
        <span>{website}</span>
        <span>·</span>
        <span>{phone}</span>
      </div>
    </div>
  );
};
