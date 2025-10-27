/**
 * Office.js Type Declarations
 * Additional types for Office.js APIs
 */

/// <reference types="@types/office-js" />

declare namespace Office {
  namespace AddinCommands {
    interface Event {
      completed(): void;
    }
  }

  namespace HostType {
    const Word: string;
    const Excel: string;
  }

  namespace addin {
    function showAsTaskpane(): void;
  }

  namespace actions {
    function associate(id: string, handler: (event: AddinCommands.Event) => void): void;
  }
}
