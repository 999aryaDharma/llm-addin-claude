/**
 * Excel Interop Service
 * Handles all Excel.js API interactions
 */

import { ExcelRange } from './api';

export interface RangeInfo {
  address: string;
  values: any[][];
  formulas: string[][];
  sheetName: string;
  workbookName: string;
  rowCount: number;
  columnCount: number;
}

export class ExcelInteropService {
  /**
   * Get currently selected range
   */
  async getSelectedRange(): Promise<RangeInfo> {
    return Excel.run(async (context) => {
      const range = context.workbook.getSelectedRange();
      const sheet = range.worksheet;
      const workbook = context.workbook;

      range.load(['address', 'values', 'formulas', 'rowCount', 'columnCount']);
      sheet.load('name');
      workbook.load('name');

      await context.sync();

      return {
        address: range.address,
        values: range.values,
        formulas: range.formulas,
        sheetName: sheet.name,
        workbookName: workbook.name,
        rowCount: range.rowCount,
        columnCount: range.columnCount
      };
    });
  }

  /**
   * Convert range to ExcelRange format for API
   */
  async getSelectedRangeForAPI(hasHeaders: boolean = true): Promise<ExcelRange> {
    const rangeInfo = await this.getSelectedRange();

    return {
      values: rangeInfo.values,
      sheet_name: rangeInfo.sheetName,
      address: rangeInfo.address,
      workbook_name: rangeInfo.workbookName,
      has_headers: hasHeaders
    };
  }

  /**
   * Insert formula into selected cell
   */
  async insertFormula(formula: string, address?: string): Promise<void> {
    return Excel.run(async (context) => {
      let range;
      if (address) {
        range = context.workbook.worksheets.getActiveWorksheet().getRange(address);
      } else {
        range = context.workbook.getSelectedRange();
      }

      // Ensure formula starts with =
      const formulaText = formula.startsWith('=') ? formula : `=${formula}`;
      range.formulas = [[formulaText]];

      await context.sync();
    });
  }

  /**
   * Insert values into range
   */
  async insertValues(values: any[][], address?: string): Promise<void> {
    return Excel.run(async (context) => {
      let range;
      if (address) {
        range = context.workbook.worksheets.getActiveWorksheet().getRange(address);
      } else {
        range = context.workbook.getSelectedRange();
      }

      range.values = values;
      await context.sync();
    });
  }

  /**
   * Get range by address
   */
  async getRangeByAddress(address: string, sheetName?: string): Promise<RangeInfo> {
    return Excel.run(async (context) => {
      let sheet;
      if (sheetName) {
        sheet = context.workbook.worksheets.getItem(sheetName);
      } else {
        sheet = context.workbook.worksheets.getActiveWorksheet();
      }

      const range = sheet.getRange(address);
      const workbook = context.workbook;

      range.load(['address', 'values', 'formulas', 'rowCount', 'columnCount']);
      sheet.load('name');
      workbook.load('name');

      await context.sync();

      return {
        address: range.address,
        values: range.values,
        formulas: range.formulas,
        sheetName: sheet.name,
        workbookName: workbook.name,
        rowCount: range.rowCount,
        columnCount: range.columnCount
      };
    });
  }

  /**
   * Get used range in active sheet
   */
  async getUsedRange(): Promise<RangeInfo> {
    return Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      const range = sheet.getUsedRange();
      const workbook = context.workbook;

      range.load(['address', 'values', 'formulas', 'rowCount', 'columnCount']);
      sheet.load('name');
      workbook.load('name');

      await context.sync();

      return {
        address: range.address,
        values: range.values,
        formulas: range.formulas,
        sheetName: sheet.name,
        workbookName: workbook.name,
        rowCount: range.rowCount,
        columnCount: range.columnCount
      };
    });
  }

  /**
   * Add comment to cell
   */
  async addComment(text: string, address?: string): Promise<void> {
    return Excel.run(async (context) => {
      let range;
      if (address) {
        range = context.workbook.worksheets.getActiveWorksheet().getRange(address);
      } else {
        range = context.workbook.getSelectedRange();
      }

      const comment = range.addComment(text);
      await context.sync();
    });
  }

  /**
   * Highlight range
   */
  async highlightRange(color: string = '#FFFF00', address?: string): Promise<void> {
    return Excel.run(async (context) => {
      let range;
      if (address) {
        range = context.workbook.worksheets.getActiveWorksheet().getRange(address);
      } else {
        range = context.workbook.getSelectedRange();
      }

      range.format.fill.color = color;
      await context.sync();
    });
  }

  /**
   * Create chart
   */
  async createChart(
    chartType: string,
    sourceRange: string,
    seriesBy: 'Auto' | 'Columns' | 'Rows' = 'Auto'
  ): Promise<void> {
    return Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      const range = sheet.getRange(sourceRange);

      const chart = sheet.charts.add(chartType as any, range, seriesBy);
      chart.title.text = 'AI Generated Chart';

      await context.sync();
    });
  }

  /**
   * Get column names (from first row)
   */
  async getColumnNames(address?: string): Promise<string[]> {
    return Excel.run(async (context) => {
      let range;
      if (address) {
        range = context.workbook.worksheets.getActiveWorksheet().getRange(address);
      } else {
        range = context.workbook.getSelectedRange();
      }

      const headerRow = range.getRow(0);
      headerRow.load('values');

      await context.sync();

      return headerRow.values[0].map(v => String(v));
    });
  }

  /**
   * Get data summary statistics
   */
  async getColumnStats(columnIndex: number): Promise<{
    min: number;
    max: number;
    average: number;
    count: number;
  }> {
    return Excel.run(async (context) => {
      const range = context.workbook.getSelectedRange();
      range.load(['values', 'rowCount']);
      await context.sync();

      const values = range.values.slice(1).map(row => row[columnIndex]).filter(v => typeof v === 'number');

      if (values.length === 0) {
        return { min: 0, max: 0, average: 0, count: 0 };
      }

      const sum = values.reduce((a, b) => a + b, 0);
      return {
        min: Math.min(...values),
        max: Math.max(...values),
        average: sum / values.length,
        count: values.length
      };
    });
  }

  /**
   * Auto-format range as table
   */
  async formatAsTable(address?: string, tableName?: string): Promise<void> {
    return Excel.run(async (context) => {
      let range;
      if (address) {
        range = context.workbook.worksheets.getActiveWorksheet().getRange(address);
      } else {
        range = context.workbook.getSelectedRange();
      }

      const table = context.workbook.worksheets.getActiveWorksheet().tables.add(range, true);
      if (tableName) {
        table.name = tableName;
      }
      table.style = 'TableStyleMedium2';

      await context.sync();
    });
  }

  /**
   * Get active worksheet name
   */
  async getActiveSheetName(): Promise<string> {
    return Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      sheet.load('name');
      await context.sync();
      return sheet.name;
    });
  }

  /**
   * Get all worksheet names
   */
  async getAllSheetNames(): Promise<string[]> {
    return Excel.run(async (context) => {
      const sheets = context.workbook.worksheets;
      sheets.load('items/name');
      await context.sync();

      return sheets.items.map(sheet => sheet.name);
    });
  }

  /**
   * Freeze panes
   */
  async freezePanes(rowsToFreeze: number = 1, columnsToFreeze: number = 0): Promise<void> {
    return Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      sheet.freezePanes.freezeRows(rowsToFreeze);
      if (columnsToFreeze > 0) {
        sheet.freezePanes.freezeColumns(columnsToFreeze);
      }

      await context.sync();
    });
  }

  /**
   * Sort range
   */
  async sortRange(columnIndex: number, ascending: boolean = true): Promise<void> {
    return Excel.run(async (context) => {
      const range = context.workbook.getSelectedRange();
      const sortFields = [
        {
          key: columnIndex,
          ascending: ascending
        }
      ];

      range.sort.apply(sortFields);
      await context.sync();
    });
  }

  /**
   * Filter range
   */
  async applyFilter(columnIndex: number, criteria: string): Promise<void> {
    return Excel.run(async (context) => {
      const range = context.workbook.getSelectedRange();
      const sheet = context.workbook.worksheets.getActiveWorksheet();

      // Apply autofilter to range
      sheet.autoFilter.apply(range);

      // Apply filter criteria
      sheet.autoFilter.apply(range, columnIndex, {
        filterOn: 'Values' as any,
        values: [criteria]
      });

      await context.sync();
    });
  }

  /**
   * Clear filters
   */
  async clearFilters(): Promise<void> {
    return Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      sheet.autoFilter.clearCriteria();
      await context.sync();
    });
  }

  /**
   * Insert sparkline (mini chart in cell)
   */
  async insertSparkline(dataRange: string, targetCell: string, type: 'Line' | 'Column' = 'Line'): Promise<void> {
    return Excel.run(async (context) => {
      // Note: Sparklines are not directly supported in Office.js
      // This is a placeholder for future implementation
      // You might need to use conditional formatting or other workarounds
      console.warn('Sparklines not directly supported in Office.js');
    });
  }
}

export const excelInterop = new ExcelInteropService();
