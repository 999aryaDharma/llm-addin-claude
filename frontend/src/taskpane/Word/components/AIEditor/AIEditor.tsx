/// <reference types="react" />
import React, { useState } from 'react';
import { Send, Wand2, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useWordAPI } from '../../../hooks/useWordAPI';
import { wordAPI, AnalyzeRequest, RewriteRequest, SummarizeRequest } from '../../../services/api';
import { useDocumentStore } from '../../../store/documentStore';
import { useSettingsStore } from '../../../store/settingsStore';

type ActionType = 'rewrite' | 'analyze' | 'summarize' | 'grammar' | 'generate';

const AIEditor: React.FC = () => {
  const [action, setAction] = useState<ActionType>('rewrite');
  const [instruction, setInstruction] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { getSelection, replaceSelection, insertComment } = useWordAPI();
  const { selectedText, addToHistory } = useDocumentStore();
  const { defaultWritingStyle, autoContextExtraction } = useSettingsStore();

  const handleAction = async () => {
    try {
      setIsProcessing(true);
      setError(null);
      setResult(null);

      // Get selected text
      const selection = await getSelection();
      if (!selection || !selection.text.trim()) {
        setError('Please select some text first');
        return;
      }

      let response;

      switch (action) {
        case 'rewrite':
          const rewriteData: RewriteRequest = {
            text: selection.text,
            instruction: instruction || 'Improve this text',
            style: defaultWritingStyle,
            use_context: autoContextExtraction
          };
          response = await wordAPI.rewrite(rewriteData);
          break;

        case 'analyze':
          const analyzeData: AnalyzeRequest = {
            text: selection.text,
            analysis_type: 'general',
            include_suggestions: true
          };
          response = await wordAPI.analyze(analyzeData);
          break;

        case 'summarize':
          const summarizeData: SummarizeRequest = {
            text: selection.text,
            summary_type: 'concise'
          };
          response = await wordAPI.summarize(summarizeData);
          break;

        case 'grammar':
          response = await wordAPI.grammarCheck(selection.text);
          break;

        default:
          throw new Error('Unsupported action');
      }

      setResult(response.data);

      // Add to history
      addToHistory({
        action,
        input: selection.text,
        output: JSON.stringify(response.data),
        metadata: { instruction }
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReplace = async () => {
    if (!result) return;

    try {
      const textToReplace = result.rewritten || result.summary || '';
      if (textToReplace) {
        await replaceSelection(textToReplace);
        setResult(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to replace text');
    }
  };

  const handleInsertAsDraft = async () => {
    if (!result) return;

    try {
      const textToInsert = result.rewritten || result.summary || '';
      if (textToInsert) {
        await insertComment(textToInsert);
        setResult(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to insert draft');
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Action Selector */}
      <div className="card">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Choose Action
        </label>
        <div className="grid grid-cols-2 gap-2">
          {[
            { id: 'rewrite' as ActionType, label: 'Rewrite', icon: Wand2 },
            { id: 'analyze' as ActionType, label: 'Analyze', icon: FileText },
            { id: 'summarize' as ActionType, label: 'Summarize', icon: FileText },
            { id: 'grammar' as ActionType, label: 'Grammar', icon: CheckCircle }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setAction(item.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  action === item.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Instruction Input */}
      {action === 'rewrite' && (
        <div className="card">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Instruction (Optional)
          </label>
          <input
            type="text"
            className="input"
            placeholder="E.g., Make it more formal, Add more details..."
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
          />
        </div>
      )}

      {/* Action Button */}
      <button
        onClick={handleAction}
        disabled={isProcessing}
        className="btn btn-primary w-full flex items-center justify-center gap-2"
      >
        {isProcessing ? (
          <>
            <span className="loading-spinner"></span>
            Processing...
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Run {action.charAt(0).toUpperCase() + action.slice(1)}
          </>
        )}
      </button>

      {/* Error Display */}
      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <div>
              <h4 className="text-sm font-medium text-red-800">Error</h4>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Result Display */}
      {result && (
        <div className="card space-y-3">
          <h3 className="text-sm font-semibold text-gray-800">Result</h3>

          {/* Rewrite Result */}
          {result.rewritten && (
            <div className="space-y-2">
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-sm text-gray-800 whitespace-pre-wrap">{result.rewritten}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={handleReplace} className="btn btn-primary btn-sm flex-1">
                  Replace Text
                </button>
                <button onClick={handleInsertAsDraft} className="btn btn-secondary btn-sm flex-1">
                  Insert as Comment
                </button>
              </div>
            </div>
          )}

          {/* Summary Result */}
          {result.summary && (
            <div className="space-y-2">
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-sm text-gray-800">{result.summary}</p>
              </div>
              {result.key_points && (
                <div>
                  <h4 className="text-xs font-medium text-gray-700 mb-1">Key Points:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {result.key_points.map((point: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600">{point}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Analysis Result */}
          {result.analysis && (
            <div className="space-y-2">
              <div className="bg-gray-50 p-3 rounded-lg text-sm space-y-2">
                {Object.entries(result.analysis).map(([key, value]) => (
                  <div key={key}>
                    <span className="font-medium text-gray-700">{key}: </span>
                    <span className="text-gray-600">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
              {result.suggestions && result.suggestions.length > 0 && (
                <div>
                  <h4 className="text-xs font-medium text-gray-700 mb-1">Suggestions:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {result.suggestions.map((suggestion: string, idx: number) => (
                      <li key={idx} className="text-sm text-gray-600">{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIEditor;
