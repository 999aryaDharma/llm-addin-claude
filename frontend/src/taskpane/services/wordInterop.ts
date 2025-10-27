/**
 * Word Interop Service
 * Handles all Word.js API interactions
 */

export interface TextSelection {
  text: string;
  range: Word.Range | null;
}

export class WordInteropService {
  /**
   * Get currently selected text in Word
   */
  async getSelectedText(): Promise<TextSelection> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      selection.load('text');
      await context.sync();

      return {
        text: selection.text,
        range: selection
      };
    });
  }

  /**
   * Replace selected text with new text
   */
  async replaceSelectedText(newText: string): Promise<void> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      selection.insertText(newText, Word.InsertLocation.replace);
      await context.sync();
    });
  }

  /**
   * Insert text at cursor position
   */
  async insertText(text: string, location: 'replace' | 'start' | 'end' = 'end'): Promise<void> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      const insertLocation = location === 'replace'
        ? Word.InsertLocation.replace
        : location === 'start'
        ? Word.InsertLocation.start
        : Word.InsertLocation.end;

      selection.insertText(text, insertLocation);
      await context.sync();
    });
  }

  /**
   * Insert comment at selection
   */
  async insertComment(text: string, _author: string = 'AI Assistant'): Promise<void> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      selection.insertComment(text);
      await context.sync();
    });
  }

  /**
   * Get entire document text
   */
  async getDocumentText(): Promise<string> {
    return Word.run(async (context) => {
      const body = context.document.body;
      body.load('text');
      await context.sync();
      return body.text;
    });
  }

  /**
   * Get document by paragraphs
   */
  async getParagraphs(): Promise<string[]> {
    return Word.run(async (context) => {
      const paragraphs = context.document.body.paragraphs;
      paragraphs.load('text');
      await context.sync();

      return paragraphs.items.map(p => p.text);
    });
  }

  /**
   * Get current paragraph context
   */
  async getCurrentParagraph(): Promise<string> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      const paragraph = selection.paragraphs.getFirst();
      paragraph.load('text');
      await context.sync();

      return paragraph.text;
    });
  }

  /**
   * Get surrounding context (current paragraph + neighbors)
   */
  async getSurroundingContext(paragraphsBefore: number = 2, paragraphsAfter: number = 2): Promise<string> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();

      // Get current paragraph
      const currentParagraph = selection.paragraphs.getFirst();

      // Get previous paragraphs
      const contextParagraphs: Word.Paragraph[] = [];
      let currentP = currentParagraph;

      for (let i = 0; i < paragraphsBefore; i++) {
        try {
          // @ts-ignore - getPreviousSibling exists but not in all Office.js versions
          currentP = currentP.getPreviousSibling() as Word.Paragraph;
          contextParagraphs.unshift(currentP);
        } catch {
          break;
        }
      }

      // Add current
      contextParagraphs.push(currentParagraph);

      // Get next paragraphs
      currentP = currentParagraph;
      for (let i = 0; i < paragraphsAfter; i++) {
        try {
          // @ts-ignore - getNextSibling exists but not in all Office.js versions
          currentP = currentP.getNextSibling() as Word.Paragraph;
          contextParagraphs.push(currentP);
        } catch {
          break;
        }
      }

      // Load all
      contextParagraphs.forEach(p => p.load('text'));
      await context.sync();

      return contextParagraphs.map(p => p.text).join('\n\n');
    });
  }

  /**
   * Highlight text
   */
  async highlightSelection(color: string = 'yellow'): Promise<void> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      selection.font.highlightColor = color;
      await context.sync();
    });
  }

  /**
   * Insert text with formatting
   */
  async insertFormattedText(
    text: string,
    options: {
      bold?: boolean;
      italic?: boolean;
      color?: string;
      fontSize?: number;
    } = {}
  ): Promise<void> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      const range = selection.insertText(text, Word.InsertLocation.end);

      if (options.bold) range.font.bold = true;
      if (options.italic) range.font.italic = true;
      if (options.color) range.font.color = options.color;
      if (options.fontSize) range.font.size = options.fontSize;

      await context.sync();
    });
  }

  /**
   * Search and replace in document
   */
  async searchAndReplace(searchTerm: string, replaceWith: string): Promise<number> {
    return Word.run(async (context) => {
      const searchResults = context.document.body.search(searchTerm, { matchCase: false, matchWholeWord: false });
      searchResults.load('length');
      await context.sync();

      searchResults.items.forEach(item => {
        item.insertText(replaceWith, Word.InsertLocation.replace);
      });

      await context.sync();
      return searchResults.items.length;
    });
  }

  /**
   * Get document properties
   */
  async getDocumentProperties(): Promise<{
    title: string;
    author: string;
    subject: string;
  }> {
    return Word.run(async (context) => {
      const properties = context.document.properties;
      properties.load(['title', 'author', 'subject']);
      await context.sync();

      return {
        title: properties.title,
        author: properties.author,
        subject: properties.subject
      };
    });
  }

  /**
   * Get word count
   */
  async getWordCount(): Promise<number> {
    return Word.run(async (context) => {
      const body = context.document.body;
      body.load('text');
      await context.sync();

      const words = body.text.trim().split(/\s+/);
      return words.length;
    });
  }

  /**
   * Insert content control (for draft mode)
   */
  async insertContentControl(text: string, tag: string = 'AI_DRAFT'): Promise<void> {
    return Word.run(async (context) => {
      const selection = context.document.getSelection();
      const contentControl = selection.insertContentControl();
      contentControl.tag = tag;
      contentControl.title = 'AI Draft';
      contentControl.insertText(text, Word.InsertLocation.replace);
      contentControl.appearance = Word.ContentControlAppearance.boundingBox;

      await context.sync();
    });
  }

  /**
   * Show tooltip/popup at selection (using comment as workaround)
   */
  async showTooltip(message: string): Promise<void> {
    // Office.js doesn't support true tooltips, we use comments
    return this.insertComment(message, 'AI Suggestion');
  }
}

export const wordInterop = new WordInteropService();
