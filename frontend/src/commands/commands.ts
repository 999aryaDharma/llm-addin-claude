/**
 * Office.js Command Handlers
 * These functions are called from ribbon buttons and context menus
 */

// Show taskpane command
function showTaskpane(event: Office.AddinCommands.Event) {
  Office.addin.showAsTaskpane();
  event.completed();
}

// Quick rewrite command
async function quickRewrite(event: Office.AddinCommands.Event) {
  try {
    if (Office.context.host === Office.HostType.Word) {
      await Word.run(async (context) => {
        const selection = context.document.getSelection();
        selection.load('text');
        await context.sync();

        if (!selection.text.trim()) {
          Office.addin.showAsTaskpane();
          event.completed();
          return;
        }

        // TODO: Call API to rewrite
        // For now, just show taskpane
        Office.addin.showAsTaskpane();
      });
    }
  } catch (error) {
    console.error('Quick rewrite error:', error);
  }
  event.completed();
}

// Quick analyze command
async function quickAnalyze(event: Office.AddinCommands.Event) {
  try {
    if (Office.context.host === Office.HostType.Word) {
      Office.addin.showAsTaskpane();
    } else if (Office.context.host === Office.HostType.Excel) {
      Office.addin.showAsTaskpane();
    }
  } catch (error) {
    console.error('Quick analyze error:', error);
  }
  event.completed();
}

// Insert formula command (Excel)
async function insertFormula(event: Office.AddinCommands.Event) {
  try {
    if (Office.context.host === Office.HostType.Excel) {
      Office.addin.showAsTaskpane();
    }
  } catch (error) {
    console.error('Insert formula error:', error);
  }
  event.completed();
}

// Get insights command (Excel)
async function getInsights(event: Office.AddinCommands.Event) {
  try {
    if (Office.context.host === Office.HostType.Excel) {
      Office.addin.showAsTaskpane();
    }
  } catch (error) {
    console.error('Get insights error:', error);
  }
  event.completed();
}

// Register functions
Office.actions.associate('showTaskpane', showTaskpane);
Office.actions.associate('quickRewrite', quickRewrite);
Office.actions.associate('quickAnalyze', quickAnalyze);
Office.actions.associate('insertFormula', insertFormula);
Office.actions.associate('getInsights', getInsights);
