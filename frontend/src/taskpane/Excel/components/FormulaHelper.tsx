/// <reference types="react" />
import React, { useState } from 'react';
import { Send, Copy, CheckCircle } from 'lucide-react';
import { useExcelAPI } from '../../hooks/useExcelAPI';
import { excelQueryAPI } from '../../services/api';
import { useExcelStore } from '../../store/excelStore';

const FormulaHelper: React.FC = () => {
  const [description, setDescription] = useState('');
  const [formula, setFormula] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { getSelectionForAPI, insertFormula } = useExcelAPI();
  const { addInsight } = useExcelStore();

  const handleGenerate = async () => {
    if (!description.trim()) return;

    try {
      setIsGenerating(true);
      setError(null);
      setFormula(null);
      setExplanation(null);

      // Get selected range for context
      const range = await getSelectionForAPI();
      if (!range) {
        setError('Please select a range first');
        return;
      }

      // Generate formula
      const response = await excelQueryAPI.formula({
        description,
        context: range
      });

      if (response.data.success) {
        setFormula(response.data.formula);
        setExplanation(response.data.explanation);

        // Add to insights
        addInsight({
          type: 'formula',
          input: description,
          output: response.data,
          rangeAddress: range.address
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate formula');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleInsert = async () => {
    if (!formula) return;

    try {
      const success = await insertFormula(formula);
      if (success) {
        setFormula(null);
        setExplanation(null);
        setDescription('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to insert formula');
    }
  };

  const handleCopy = () => {
    if (!formula) return;
    navigator.clipboard.writeText(formula);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-4 space-y-4">
      {/* Formula Description */}
      <div className="card">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Describe the formula you need
        </label>
        <textarea
          className="input min-h-[100px] resize-none"
          placeholder="E.g., Calculate the sum of sales for each region, Find the average of column B excluding zeros, Count unique values in the selected range..."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || !description.trim()}
        className="btn btn-primary w-full flex items-center justify-center gap-2"
      >
        {isGenerating ? (
          <>
            <span className="loading-spinner"></span>
            Generating...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Generate Formula
          </>
        )}
      </button>

      {/* Error */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Result */}
      {formula && (
        <div className="card space-y-3">
          <h3 className="text-sm font-semibold text-gray-800">Generated Formula</h3>

          {/* Formula Display */}
          <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-sm overflow-x-auto">
            {formula}
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={handleInsert}
              className="btn btn-primary flex-1"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              Insert into Cell
            </button>
            <button
              onClick={handleCopy}
              className="btn btn-secondary"
              title="Copy to clipboard"
            >
              {copied ? (
                <CheckCircle className="w-4 h-4 text-green-600" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Explanation */}
          {explanation && (
            <div className="bg-blue-50 p-3 rounded-lg">
              <h4 className="text-xs font-semibold text-blue-800 mb-1">Explanation</h4>
              <p className="text-sm text-blue-900">{explanation}</p>
            </div>
          )}
        </div>
      )}

      {/* Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h4 className="text-sm font-semibold text-blue-800 mb-2">Tips</h4>
        <ul className="text-xs text-blue-900 space-y-1">
          <li>• Select the range you want to work with before generating</li>
          <li>• Be specific about what you want to calculate</li>
          <li>• Mention column names or positions if relevant</li>
          <li>• Try: "Sum column A if column B equals 'Active'"</li>
        </ul>
      </div>
    </div>
  );
};

export default FormulaHelper;
