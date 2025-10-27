import { useState, useCallback } from 'react';
import { wordInterop, TextSelection } from '../services/wordInterop';
import { useDocumentStore } from '../store/documentStore';

export const useWordAPI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setSelectedText, setSelectedContext } = useDocumentStore();

  /**
   * Get selected text
   */
  const getSelection = useCallback(async (): Promise<TextSelection | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const selection = await wordInterop.getSelectedText();
      setSelectedText(selection.text);
      return selection;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get selection';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [setSelectedText]);

  /**
   * Replace selected text
   */
  const replaceSelection = useCallback(async (newText: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await wordInterop.replaceSelectedText(newText);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to replace text';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Insert text
   */
  const insertText = useCallback(async (text: string, location: 'replace' | 'start' | 'end' = 'end'): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await wordInterop.insertText(text, location);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to insert text';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Insert comment (for draft mode)
   */
  const insertComment = useCallback(async (text: string, author?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await wordInterop.insertComment(text, author);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to insert comment';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get entire document
   */
  const getDocument = useCallback(async (): Promise<string | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const text = await wordInterop.getDocumentText();
      return text;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get document';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get current paragraph
   */
  const getCurrentParagraph = useCallback(async (): Promise<string | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const text = await wordInterop.getCurrentParagraph();
      return text;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get paragraph';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get surrounding context
   */
  const getContext = useCallback(async (before: number = 2, after: number = 2): Promise<string | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const context = await wordInterop.getSurroundingContext(before, after);
      setSelectedContext(context);
      return context;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get context';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [setSelectedContext]);

  /**
   * Highlight selection
   */
  const highlightText = useCallback(async (color: string = 'yellow'): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await wordInterop.highlightSelection(color);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to highlight';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Search and replace
   */
  const searchReplace = useCallback(async (searchTerm: string, replaceWith: string): Promise<number> => {
    try {
      setIsLoading(true);
      setError(null);
      const count = await wordInterop.searchAndReplace(searchTerm, replaceWith);
      return count;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to search and replace';
      setError(message);
      return 0;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get word count
   */
  const getWordCount = useCallback(async (): Promise<number> => {
    try {
      setIsLoading(true);
      setError(null);
      const count = await wordInterop.getWordCount();
      return count;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get word count';
      setError(message);
      return 0;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Insert content control (for draft mode with replace option)
   */
  const insertDraft = useCallback(async (text: string, tag: string = 'AI_DRAFT'): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await wordInterop.insertContentControl(text, tag);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to insert draft';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    getSelection,
    replaceSelection,
    insertText,
    insertComment,
    getDocument,
    getCurrentParagraph,
    getContext,
    highlightText,
    searchReplace,
    getWordCount,
    insertDraft
  };
};
