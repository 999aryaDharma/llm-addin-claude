/// <reference types="react" />
import React, { useState } from 'react';
import { BarChart3, TrendingUp, PieChart, LineChart } from 'lucide-react';
import { useExcelAPI } from '../../hooks/useExcelAPI';
import { excelQueryAPI } from '../../services/api';

const ChartAdvisor: React.FC = () => {
  const [recommendation, setRecommendation] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { getSelectionForAPI, createChart } = useExcelAPI();

  const handleAnalyze = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);
      setRecommendation(null);

      const range = await getSelectionForAPI();
      if (!range) {
        setError('Please select a range first');
        return;
      }

      const response = await excelQueryAPI.chart({ context: range });
      setRecommendation(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCreateChart = async (chartType: string) => {
    try {
      const range = await getSelectionForAPI();
      if (!range) return;

      // Map chart type string to Excel chart type string
      const excelChartType = chartType.toLowerCase().includes('bar')
        ? 'ColumnClustered'
        : chartType.toLowerCase().includes('line')
        ? 'Line'
        : chartType.toLowerCase().includes('pie')
        ? 'Pie'
        : 'ColumnClustered';

      await createChart(excelChartType, range.address);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create chart');
    }
  };

  const getChartIcon = (type: string) => {
    if (type.toLowerCase().includes('bar')) return BarChart3;
    if (type.toLowerCase().includes('line')) return LineChart;
    if (type.toLowerCase().includes('pie')) return PieChart;
    return TrendingUp;
  };

  return (
    <div className="p-4 space-y-4">
      <button
        onClick={handleAnalyze}
        disabled={isAnalyzing}
        className="btn btn-primary w-full"
      >
        {isAnalyzing ? (
          <>
            <span className="loading-spinner mr-2"></span>
            Analyzing...
          </>
        ) : (
          <>
            <BarChart3 className="w-4 h-4 mr-2" />
            Get Chart Recommendations
          </>
        )}
      </button>

      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {recommendation && (
        <div className="card space-y-3">
          <h3 className="text-sm font-semibold text-gray-800">Recommended Charts</h3>
          {recommendation.recommendations?.map((rec: any, idx: number) => {
            const Icon = getChartIcon(rec.chart_type);
            return (
              <div key={idx} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-start gap-3">
                  <Icon className="w-5 h-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-800">{rec.chart_type}</h4>
                    <p className="text-xs text-gray-600 mt-1">{rec.description}</p>
                    {rec.reason && (
                      <p className="text-xs text-gray-500 mt-1">
                        <span className="font-medium">Why:</span> {rec.reason}
                      </p>
                    )}
                    <button
                      onClick={() => handleCreateChart(rec.chart_type)}
                      className="btn btn-sm btn-primary mt-2"
                    >
                      Create Chart
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ChartAdvisor;
