import { create } from 'zustand';
import { generateId } from '../utils/helpers';

export interface HistoryEntry {
  id: string;
  timestamp: Date;
  action: string;
  input: string;
  output: string;
  metadata?: Record<string, any>;
}

export interface Document {
  id: string;
  name: string;
  type: 'word' | 'excel';
  uploaded_at: string;
  metadata?: Record<string, any>;
}

interface DocumentState {
  // Current document info
  currentDocument: Document | null;
  documentList: Document[];

  // History
  history: HistoryEntry[];

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Selected text/range
  selectedText: string;
  selectedContext: string;

  // Actions
  setCurrentDocument: (doc: Document | null) => void;
  setDocumentList: (docs: Document[]) => void;
  addToHistory: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
  clearHistory: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedText: (text: string) => void;
  setSelectedContext: (context: string) => void;
  clearSelectedText: () => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  currentDocument: null,
  documentList: [],
  history: [],
  isLoading: false,
  error: null,
  selectedText: '',
  selectedContext: '',

  setCurrentDocument: (doc) => set({ currentDocument: doc }),

  setDocumentList: (docs) => set({ documentList: docs }),

  addToHistory: (entry) =>
    set((state) => ({
      history: [
        {
          ...entry,
          id: generateId(),
          timestamp: new Date()
        },
        ...state.history
      ].slice(0, 50) // Keep last 50 entries
    })),

  clearHistory: () => set({ history: [] }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  setSelectedText: (text) => set({ selectedText: text }),

  setSelectedContext: (context) => set({ selectedContext: context }),

  clearSelectedText: () => set({ selectedText: '', selectedContext: '' })
}));
