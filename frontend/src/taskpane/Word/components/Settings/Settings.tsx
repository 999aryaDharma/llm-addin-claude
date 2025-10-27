/// <reference types="react" />
import React from 'react';
import { useSettingsStore, WritingStyle } from '../../../store/settingsStore';

const SettingsPanel: React.FC = () => {
  const {
    defaultWritingStyle,
    autoContextExtraction,
    useCache,
    enableTooltipMode,
    enableDraftMode,
    setDefaultWritingStyle,
    setAutoContextExtraction,
    setUseCache,
    setEnableTooltipMode,
    setEnableDraftMode,
    resetToDefaults
  } = useSettingsStore();

  const writingStyles: { value: WritingStyle; label: string }[] = [
    { value: 'formal', label: 'Formal' },
    { value: 'casual', label: 'Casual' },
    { value: 'academic', label: 'Academic' },
    { value: 'persuasive', label: 'Persuasive' },
    { value: 'concise', label: 'Concise' }
  ];

  return (
    <div className="p-4 space-y-4">
      {/* Writing Style */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-800 mb-3">Default Writing Style</h3>
        <select
          value={defaultWritingStyle}
          onChange={(e) => setDefaultWritingStyle(e.target.value as WritingStyle)}
          className="input"
        >
          {writingStyles.map((style) => (
            <option key={style.value} value={style.value}>
              {style.label}
            </option>
          ))}
        </select>
      </div>

      {/* Features */}
      <div className="card space-y-3">
        <h3 className="text-sm font-semibold text-gray-800">Features</h3>

        <label className="flex items-center justify-between">
          <span className="text-sm text-gray-700">Auto Context Extraction</span>
          <input
            type="checkbox"
            checked={autoContextExtraction}
            onChange={(e) => setAutoContextExtraction(e.target.checked)}
            className="w-4 h-4 text-primary-600"
          />
        </label>

        <label className="flex items-center justify-between">
          <span className="text-sm text-gray-700">Use Cache</span>
          <input
            type="checkbox"
            checked={useCache}
            onChange={(e) => setUseCache(e.target.checked)}
            className="w-4 h-4 text-primary-600"
          />
        </label>

        <label className="flex items-center justify-between">
          <span className="text-sm text-gray-700">Tooltip Mode</span>
          <input
            type="checkbox"
            checked={enableTooltipMode}
            onChange={(e) => setEnableTooltipMode(e.target.checked)}
            className="w-4 h-4 text-primary-600"
          />
        </label>

        <label className="flex items-center justify-between">
          <span className="text-sm text-gray-700">Draft Mode (Comments)</span>
          <input
            type="checkbox"
            checked={enableDraftMode}
            onChange={(e) => setEnableDraftMode(e.target.checked)}
            className="w-4 h-4 text-primary-600"
          />
        </label>
      </div>

      {/* Actions */}
      <div className="card">
        <button
          onClick={resetToDefaults}
          className="btn btn-secondary w-full"
        >
          Reset to Defaults
        </button>
      </div>

      {/* Version Info */}
      <div className="card">
        <h3 className="text-sm font-semibold text-gray-800 mb-2">About</h3>
        <p className="text-xs text-gray-600">
          Office LLM Add-in<br />
          Version 2.5.0<br />
          Word & Excel AI Assistant
        </p>
      </div>
    </div>
  );
};

export default SettingsPanel;
