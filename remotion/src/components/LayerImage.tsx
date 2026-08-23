import React from 'react';
import {Img} from 'remotion';

export type LayerImageProps = {
  src: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation?: number;
  originX?: number;
  originY?: number;
  opacity?: number;
  scaleX?: number;
  scaleY?: number;
  blur?: number;
};

/** Positioned transparent PNG — all transforms from props (frame-derived upstream). */
export const LayerImage: React.FC<LayerImageProps> = ({
  src,
  x,
  y,
  width,
  height,
  rotation = 0,
  originX = width / 2,
  originY = height / 2,
  opacity = 1,
  scaleX = 1,
  scaleY = 1,
  blur = 0,
}) => {
  if (opacity <= 0.001) {
    return null;
  }

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width,
        height,
        opacity,
        transformOrigin: `${originX}px ${originY}px`,
        transform: `rotate(${rotation}deg) scale(${scaleX}, ${scaleY})`,
        filter: blur > 0 ? `blur(${blur}px)` : undefined,
      }}
    >
      <Img src={src} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
    </div>
  );
};
