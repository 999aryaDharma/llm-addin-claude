/**
 * Global Type Declarations
 */

/// <reference types="@types/office-js" />
/// <reference types="react" />
/// <reference types="react-dom" />

// Extend Window interface if needed
interface Window {
  Office?: typeof Office;
}

// Ensure React is in global scope
import * as React from 'react';

// Module declarations for imports
declare module '*.css' {
  const content: { [className: string]: string };
  export default content;
}

declare module '*.png' {
  const value: string;
  export default value;
}

declare module '*.jpg' {
  const value: string;
  export default value;
}

declare module '*.svg' {
  const value: string;
  export default value;
}

// Zustand persist middleware types fix
declare module 'zustand/middleware' {
  export function persist<T>(
    config: (set: any, get: any, api: any) => T,
    options?: {
      name: string;
      version?: number;
      getStorage?: () => any;
    }
  ): (set: any, get: any, api: any) => T;
}
