import { create } from 'zustand';
import { ExcelRange } from '../services/api';
import { generateId } from '../utils/helpers';

export interface InsightResult {
  id: string;
  timestamp: Date;
  type: 'formula' | 'analysis' | 'chart' | 'query';
  input: string;
  output: any;
  rangeAddress: string;
}

export interface ChartRecommendation {
  type: string;
  description: string;
  columns: string[];
  reason: string;
}

interface ExcelState {
  // Current range
  selectedRange: ExcelRange | null;
  rangeAddress: string;

  // Insights and results
  insights: InsightResult[];
  lastAnalysis: any | null;
  chartRecommendations: ChartRecommendation[];

  // Loading states
  isAnalyzing: boolean;
  isGeneratingFormula: boolean;
  error: string | null;

  // Data summary
  columnNames: string[];
  dataSummary: Record<string, any> | null;

  // Actions
  setSelectedRange: (range: ExcelRange | null) => void;
  setRangeAddress: (address: string) => void;
  addInsight: (insight: Omit<InsightResult, 'id' | 'timestamp'>) => void;
  clearInsights: () => void;
  setLastAnalysis: (analysis: any) => void;
  setChartRecommendations: (recommendations: ChartRecommendation[]) => void;
  setAnalyzing: (analyzing: boolean) => void;
  setGeneratingFormula: (generating: boolean) => void;
  setError: (error: string | null) => void;
  setColumnNames: (names: string[]) => void;
  setDataSummary: (summary: Record<string, any>) => void;
}

export const useExcelStore = create<ExcelState>((set) => ({
  selectedRange: null,
  rangeAddress: '',
  insights: [],
  lastAnalysis: null,
  chartRecommendations: [],
  isAnalyzing: false,
  isGeneratingFormula: false,
  error: null,
  columnNames: [],
  dataSummary: null,

  setSelectedRange: (range) => set({ selectedRange: range }),

  setRangeAddress: (address) => set({ rangeAddress: address }),

  addInsight: (insight) =>
    set((state) => ({
      insights: [
        {
          ...insight,
          id: generateId(),
          timestamp: new Date()
        },
        ...state.insights
      ].slice(0, 30) // Keep last 30 insights
    })),

  clearInsights: () => set({ insights: [] }),

  setLastAnalysis: (analysis) => set({ lastAnalysis: analysis }),

  setChartRecommendations: (recommendations) => set({ chartRecommendations: recommendations }),

  setAnalyzing: (analyzing) => set({ isAnalyzing: analyzing }),

  setGeneratingFormula: (generating) => set({ isGeneratingFormula: generating }),

  setError: (error) => set({ error }),

  setColumnNames: (names) => set({ columnNames: names }),

  setDataSummary: (summary) => set({ dataSummary: summary })
}));
