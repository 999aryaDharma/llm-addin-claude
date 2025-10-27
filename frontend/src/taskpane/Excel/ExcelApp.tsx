/// <reference types="react" />
import React, { useState } from 'react';
import { Table, Calculator, BarChart3, MessageSquare, Settings } from 'lucide-react';
import FormulaHelper from './components/FormulaHelper';
import DataChat from './components/DataChat';
import ChartAdvisor from './components/ChartAdvisor';
import InsightPanel from './components/InsightPanel';

type TabType = 'formula' | 'chat' | 'insight' | 'chart' | 'settings';

const ExcelApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('formula');

  const tabs = [
    { id: 'formula' as TabType, label: 'Formula', icon: Calculator },
    { id: 'chat' as TabType, label: 'Data Chat', icon: MessageSquare },
    { id: 'insight' as TabType, label: 'Insights', icon: Table },
    { id: 'chart' as TabType, label: 'Charts', icon: BarChart3 }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'formula':
        return <FormulaHelper />;
      case 'chat':
        return <DataChat />;
      case 'insight':
        return <InsightPanel />;
      case 'chart':
        return <ChartAdvisor />;
      default:
        return <FormulaHelper />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center gap-2">
          <Table className="w-5 h-5 text-green-600" />
          <h1 className="text-lg font-semibold text-gray-800">Excel AI Assistant</h1>
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
                    ? 'text-green-600 border-b-2 border-green-600 bg-green-50'
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

export default ExcelApp;
