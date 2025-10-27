/// <reference types="react" />
import React, { useState } from 'react';
import { FileText, Sparkles, History, Settings, Search } from 'lucide-react';
import AIEditor from './components/AIEditor/AIEditor';
import References from './components/References/References';
import SettingsPanel from './components/Settings/Settings';

type TabType = 'editor' | 'references' | 'history' | 'settings';

const WordApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('editor');

  const tabs = [
    { id: 'editor' as TabType, label: 'AI Editor', icon: Sparkles },
    { id: 'references' as TabType, label: 'References', icon: Search },
    { id: 'history' as TabType, label: 'History', icon: History },
    { id: 'settings' as TabType, label: 'Settings', icon: Settings }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'editor':
        return <AIEditor />;
      case 'references':
        return <References />;
      case 'history':
        return <div className="p-4"><p className="text-gray-600">History coming soon...</p></div>;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <AIEditor />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-primary-600" />
          <h1 className="text-lg font-semibold text-gray-800">Word AI Assistant</h1>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default WordApp;
