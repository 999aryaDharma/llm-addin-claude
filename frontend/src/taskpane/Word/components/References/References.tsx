/// <reference types="react" />
import React, { useState, useEffect } from 'react';
import { Upload, Trash2, Search, FileText } from 'lucide-react';
import { documentAPI, queryAPI } from '../../../services/api';
import { useDocumentStore } from '../../../store/documentStore';

const References: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { setCurrentDocument } = useDocumentStore();

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await documentAPI.list('word');
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setIsLoading(true);
      const response = await queryAPI.search({
        query: searchQuery,
        max_results: 5
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentAPI.delete(docId);
      await loadDocuments();
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  return (
    <div className="p-4 space-y-4">
      {/* Search */}
      <div className="card">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Search Documents
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            className="input flex-1"
            placeholder="Ask a question or search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="btn btn-primary"
          >
            <Search className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-800 mb-2">Answer</h3>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-800 whitespace-pre-wrap">
              {searchResults.answer}
            </p>
          </div>
          {searchResults.sources && searchResults.sources.length > 0 && (
            <div className="mt-3">
              <h4 className="text-xs font-medium text-gray-600 mb-1">Sources:</h4>
              <div className="space-y-1">
                {searchResults.sources.slice(0, 3).map((source: string, idx: number) => (
                  <p key={idx} className="text-xs text-gray-500 line-clamp-2">
                    {source}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Document List */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-800">Reference Documents</h3>
          <span className="text-xs text-gray-500">{documents.length} docs</span>
        </div>

        {isLoading ? (
          <div className="text-center py-4">
            <div className="loading-spinner mx-auto"></div>
          </div>
        ) : documents.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-4">
            No documents uploaded yet
          </p>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {doc.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default References;
