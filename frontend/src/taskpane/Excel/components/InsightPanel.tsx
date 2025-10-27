/// <reference types="react" />
import React, { useState } from 'react';
import { Brain, TrendingUp, AlertCircle } from 'lucide-react';
import { useExcelAPI } from '../../hooks/useExcelAPI';
import { excelLLMAPI } from '../../services/api';
import { useExcelStore } from '../../store/excelStore';

const InsightPanel: React.FC = () => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { getSelectionForAPI } = useExcelAPI();
  const { setLastAnalysis } = useExcelStore();

  const handleAnalyze = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);

      const range = await getSelectionForAPI();
      if (!range) {
        setError('Please select a range first');
        return;
      }

      const response = await excelLLMAPI.analyzeComprehensive(range, true, false);
      setAnalysis(response.data.data);
      setLastAnalysis(response.data.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <button
        onClick={handleAnalyze}
        disabled={isAnalyzing}
        className="btn btn-primary w-full flex items-center justify-center gap-2"
      >
        {isAnalyzing ? (
          <>
            <span className="loading-spinner"></span>
            Analyzing Data...
          </>
        ) : (
          <>
            <Brain className="w-4 h-4" />
            Analyze Data
          </>
        )}
      </button>

      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {analysis && (
        <div className="space-y-4">
          {/* Insights */}
          {analysis.insights && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-800 mb-3">Key Insights</h3>
              {analysis.insights.key_findings && (
                <div className="mb-3">
                  <h4 className="text-xs font-medium text-gray-700 mb-1">Key Findings</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.insights.key_findings.map((finding: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600">{finding}</li>
                    ))}
                  </ul>
                </div>
              )}
              {analysis.insights.recommendations && (
                <div>
                  <h4 className="text-xs font-medium text-gray-700 mb-1">Recommendations</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {analysis.insights.recommendations.map((rec: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600">{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Correlations */}
          {analysis.correlations && analysis.correlations.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-800 mb-3">Correlations</h3>
              <div className="space-y-2">
                {analysis.correlations.slice(0, 5).map((corr: any, idx: number) => (
                  <div key={idx} className="bg-gray-50 p-2 rounded">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-800">
                        {corr.column1} ↔ {corr.column2}
                      </span>
                      <span className={`text-xs font-medium ${
                        Math.abs(corr.correlation) > 0.7 ? 'text-green-600' : 'text-gray-600'
                      }`}>
                        {(corr.correlation * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">{corr.interpretation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Patterns */}
          {analysis.patterns && analysis.patterns.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-800 mb-3">Patterns Detected</h3>
              <div className="space-y-2">
                {analysis.patterns.map((pattern: any, idx: number) => (
                  <div key={idx} className="flex items-start gap-2 bg-blue-50 p-2 rounded">
                    <TrendingUp className="w-4 h-4 text-blue-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-blue-900">
                        {pattern.type}: {pattern.column}
                      </p>
                      <p className="text-xs text-blue-700">
                        {pattern.direction && `Direction: ${pattern.direction}`}
                        {pattern.count && ` • Count: ${pattern.count}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Quality */}
          {analysis.analysis?.data_quality && (
            <div className="card">
              <h3 className="text-sm font-semibold text-gray-800 mb-2">Data Quality</h3>
              <div className="bg-gray-50 p-3 rounded">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Completeness</span>
                  <span className="font-medium text-gray-800">
                    {analysis.analysis.data_quality.completeness_score}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${analysis.analysis.data_quality.completeness_score}%` }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!analysis && !isAnalyzing && !error && (
        <div className="card text-center py-8">
          <Brain className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-500">No analysis yet</p>
          <p className="text-xs text-gray-400 mt-1">
            Select a range and click "Analyze Data"
          </p>
        </div>
      )}
    </div>
  );
};

export default InsightPanel;
