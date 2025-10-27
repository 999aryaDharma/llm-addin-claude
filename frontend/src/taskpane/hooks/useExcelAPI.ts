import { useState, useCallback } from 'react';
import { excelInterop, RangeInfo } from '../services/excelInterop';
import { useExcelStore } from '../store/excelStore';
import { ExcelRange } from '../services/api';

export const useExcelAPI = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setSelectedRange, setRangeAddress, setColumnNames } = useExcelStore();

  /**
   * Get selected range
   */
  const getSelection = useCallback(async (): Promise<RangeInfo | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const range = await excelInterop.getSelectedRange();
      setRangeAddress(range.address);
      return range;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get selection';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [setRangeAddress]);

  /**
   * Get selection formatted for API
   */
  const getSelectionForAPI = useCallback(async (hasHeaders: boolean = true): Promise<ExcelRange | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const range = await excelInterop.getSelectedRangeForAPI(hasHeaders);
      setSelectedRange(range);
      return range;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get selection';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [setSelectedRange]);

  /**
   * Insert formula
   */
  const insertFormula = useCallback(async (formula: string, address?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.insertFormula(formula, address);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to insert formula';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Insert values
   */
  const insertValues = useCallback(async (values: any[][], address?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.insertValues(values, address);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to insert values';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get range by address
   */
  const getRangeByAddress = useCallback(async (address: string, sheetName?: string): Promise<RangeInfo | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const range = await excelInterop.getRangeByAddress(address, sheetName);
      return range;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get range';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get used range
   */
  const getUsedRange = useCallback(async (): Promise<RangeInfo | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const range = await excelInterop.getUsedRange();
      return range;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get used range';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Add comment to cell
   */
  const addComment = useCallback(async (text: string, address?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.addComment(text, address);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add comment';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Highlight range
   */
  const highlightRange = useCallback(async (color: string = '#FFFF00', address?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.highlightRange(color, address);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to highlight range';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Create chart
   */
  const createChart = useCallback(async (
    chartType: string,
    sourceRange: string,
    seriesBy: 'Auto' | 'Columns' | 'Rows' = 'Auto'
  ): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.createChart(chartType, sourceRange, seriesBy);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create chart';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get column names
   */
  const getColumnNames = useCallback(async (address?: string): Promise<string[]> => {
    try {
      setIsLoading(true);
      setError(null);
      const names = await excelInterop.getColumnNames(address);
      setColumnNames(names);
      return names;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get column names';
      setError(message);
      return [];
    } finally {
      setIsLoading(false);
    }
  }, [setColumnNames]);

  /**
   * Get column statistics
   */
  const getColumnStats = useCallback(async (columnIndex: number) => {
    try {
      setIsLoading(true);
      setError(null);
      const stats = await excelInterop.getColumnStats(columnIndex);
      return stats;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get stats';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Format as table
   */
  const formatAsTable = useCallback(async (address?: string, tableName?: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.formatAsTable(address, tableName);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to format as table';
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get active sheet name
   */
  const getActiveSheetName = useCallback(async (): Promise<string | null> => {
    try {
      setIsLoading(true);
      setError(null);
      const name = await excelInterop.getActiveSheetName();
      return name;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to get sheet name';
      setError(message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Sort range
   */
  const sortRange = useCallback(async (columnIndex: number, ascending: boolean = true): Promise<boolean> => {
    try {
      setIsLoading(true);
      setError(null);
      await excelInterop.sortRange(columnIndex, ascending);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to sort';
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
    getSelectionForAPI,
    insertFormula,
    insertValues,
    getRangeByAddress,
    getUsedRange,
    addComment,
    highlightRange,
    createChart,
    getColumnNames,
    getColumnStats,
    formatAsTable,
    getActiveSheetName,
    sortRange
  };
};
