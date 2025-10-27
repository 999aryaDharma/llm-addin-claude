/// <reference types="react" />
import React, { useState } from 'react';
import { Target, Check } from 'lucide-react';
import { useExcelAPI } from '../../hooks/useExcelAPI';
import { useExcelStore } from '../../store/excelStore';

const RangeSelector: React.FC = () => {
  const [isSelecting, setIsSelecting] = useState(false);
  const { getSelection } = useExcelAPI();
  const { rangeAddress, setRangeAddress } = useExcelStore();

  const handleSelectRange = async () => {
    try {
      setIsSelecting(true);
      const range = await getSelection();
      if (range) {
        setRangeAddress(range.address);
      }
    } catch (err) {
      console.error('Failed to select range:', err);
    } finally {
      setIsSelecting(false);
    }
  };

  return (
    <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
      <Target className="w-4 h-4 text-gray-500" />
      <span className="text-sm text-gray-600 flex-1">
        {rangeAddress || 'No range selected'}
      </span>
      <button
        onClick={handleSelectRange}
        disabled={isSelecting}
        className="btn btn-sm btn-secondary"
      >
        {isSelecting ? (
          <span className="loading-spinner w-3 h-3"></span>
        ) : (
          <Check className="w-4 h-4" />
        )}
      </button>
    </div>
  );
};

export default RangeSelector;
