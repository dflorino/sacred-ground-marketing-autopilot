import React, {createContext, useContext} from 'react';
import type {PreviewMode} from '../types/daily';

const defaultMode: PreviewMode = {};

const PreviewContext = createContext<PreviewMode>(defaultMode);

export const PreviewProvider: React.FC<{
  mode: PreviewMode;
  children: React.ReactNode;
}> = ({mode, children}) => (
  <PreviewContext.Provider value={mode}>{children}</PreviewContext.Provider>
);

export const usePreviewMode = (): PreviewMode => useContext(PreviewContext);
