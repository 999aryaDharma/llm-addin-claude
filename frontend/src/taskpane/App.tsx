/// <reference types="react" />
import React, { useEffect, useState } from 'react';
import WordApp from './Word/WordApp';
import ExcelApp from './Excel/ExcelApp';

/**
 * Main App Component
 * Routes to Word or Excel app based on Office host
 */
const App: React.FC = () => {
  const [officeHost, setOfficeHost] = useState<string>('');
  const [isOfficeReady, setIsOfficeReady] = useState(false);

  useEffect(() => {
    // Initialize Office.js
    Office.onReady((info) => {
      setOfficeHost(String(info.host));
      setIsOfficeReady(true);
      console.log('Office is ready:', info);
    });
  }, []);

  if (!isOfficeReady) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing Office Add-in...</p>
        </div>
      </div>
    );
  }

  // Route to appropriate app based on host
  switch (officeHost) {
    case 'Word':
      return <WordApp />;
    case 'Excel':
      return <ExcelApp />;
    default:
      return (
        <div className="flex items-center justify-center h-screen p-4">
          <div className="text-center">
            <h1 className="text-xl font-bold text-gray-800 mb-2">Unsupported Application</h1>
            <p className="text-gray-600">
              This add-in only works with Microsoft Word and Excel.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Detected host: {officeHost || 'Unknown'}
            </p>
          </div>
        </div>
      );
  }
};

export default App;
