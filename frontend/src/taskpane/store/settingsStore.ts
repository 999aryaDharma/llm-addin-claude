import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'auto';
export type WritingStyle = 'formal' | 'casual' | 'academic' | 'persuasive' | 'concise';

interface SettingsState {
  // UI Settings
  theme: Theme;
  sidebarCollapsed: boolean;

  // AI Settings
  defaultWritingStyle: WritingStyle;
  autoContextExtraction: boolean;
  maxContextLength: number;
  useCache: boolean;

  // Feature flags
  enableTooltipMode: boolean;
  enableDraftMode: boolean;
  enableContinuousMode: boolean;

  // API Settings
  apiBaseUrl: string;

  // Actions
  setTheme: (theme: Theme) => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setDefaultWritingStyle: (style: WritingStyle) => void;
  setAutoContextExtraction: (enabled: boolean) => void;
  setMaxContextLength: (length: number) => void;
  setUseCache: (useCache: boolean) => void;
  setEnableTooltipMode: (enabled: boolean) => void;
  setEnableDraftMode: (enabled: boolean) => void;
  setEnableContinuousMode: (enabled: boolean) => void;
  setApiBaseUrl: (url: string) => void;
  resetToDefaults: () => void;
}

const defaultSettings = {
  theme: 'auto' as Theme,
  sidebarCollapsed: false,
  defaultWritingStyle: 'formal' as WritingStyle,
  autoContextExtraction: true,
  maxContextLength: 3000,
  useCache: true,
  enableTooltipMode: true,
  enableDraftMode: true,
  enableContinuousMode: false,
  apiBaseUrl: 'http://localhost:8000'
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      ...defaultSettings,

      setTheme: (theme) => set({ theme }),

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      setDefaultWritingStyle: (style) => set({ defaultWritingStyle: style }),

      setAutoContextExtraction: (enabled) => set({ autoContextExtraction: enabled }),

      setMaxContextLength: (length) => set({ maxContextLength: length }),

      setUseCache: (useCache) => set({ useCache }),

      setEnableTooltipMode: (enabled) => set({ enableTooltipMode: enabled }),

      setEnableDraftMode: (enabled) => set({ enableDraftMode: enabled }),

      setEnableContinuousMode: (enabled) => set({ enableContinuousMode: enabled }),

      setApiBaseUrl: (url) => set({ apiBaseUrl: url }),

      resetToDefaults: () => set(defaultSettings)
    }),
    {
      name: 'office-llm-settings',
      version: 1
    }
  )
);
