# Office LLM Add-in Frontend

AI-powered Office Add-in for Microsoft Word and Excel, providing intelligent writing assistance, data analysis, and insights.

## Version 2.5.0

## Features

### Word Add-in
- **AI Rewrite**: Rewrite text in different styles (formal, casual, academic, persuasive, concise)
- **Text Analysis**: Analyze writing style, grammar, readability, and sentiment
- **Summarization**: Generate concise or detailed summaries
- **Grammar Check**: Check and fix grammar issues
- **Reference Documents**: Search and query uploaded reference documents
- **Context-Aware**: Automatically extract context from surrounding paragraphs

### Excel Add-in
- **Formula Helper**: Generate Excel formulas from natural language descriptions
- **Data Chat**: Ask questions about your data in natural language
- **Insights Panel**: Get comprehensive AI-powered analysis of your data
- **Chart Advisor**: Get chart recommendations based on your data structure
- **Correlation Detection**: Find relationships between columns
- **Trend Analysis**: Identify patterns and trends in your data

## Architecture

```
frontend/
├── public/
│   ├── manifest.xml          # Office Add-in manifest (Word & Excel)
│   ├── taskpane.html          # Main entry point
│   └── commands.html          # Command handlers
│
├── src/
│   ├── taskpane/
│   │   ├── App.tsx            # Root app with routing
│   │   ├── Word/              # Word-specific components
│   │   │   ├── WordApp.tsx
│   │   │   └── components/
│   │   │       ├── AIEditor/
│   │   │       ├── References/
│   │   │       └── Settings/
│   │   │
│   │   ├── Excel/             # Excel-specific components
│   │   │   ├── ExcelApp.tsx
│   │   │   └── components/
│   │   │       ├── FormulaHelper.tsx
│   │   │       ├── DataChat.tsx
│   │   │       ├── ChartAdvisor.tsx
│   │   │       ├── InsightPanel.tsx
│   │   │       └── RangeSelector.tsx
│   │   │
│   │   ├── hooks/             # Custom hooks
│   │   │   ├── useWordAPI.ts
│   │   │   └── useExcelAPI.ts
│   │   │
│   │   ├── services/          # API & Office.js services
│   │   │   ├── api.ts
│   │   │   ├── wordInterop.ts
│   │   │   └── excelInterop.ts
│   │   │
│   │   └── store/             # State management (Zustand)
│   │       ├── documentStore.ts
│   │       ├── excelStore.ts
│   │       └── settingsStore.ts
│   │
│   └── commands/
│       └── commands.ts         # Ribbon button handlers
│
├── package.json
├── tsconfig.json
├── webpack.config.js
└── tailwind.config.js
```

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Office Integration**: Office.js API
- **Build Tool**: Webpack 5
- **Icons**: Lucide React

## Setup & Installation

### Prerequisites
- Node.js 18+ and npm
- Microsoft Office (Word & Excel) installed
- Backend API running at `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Install dev certificates (for HTTPS):
```bash
npx office-addin-dev-certs install
```

3. Update manifest.xml with your add-in ID and URLs (if needed)

### Development

Start the development server:
```bash
npm run dev
```

The add-in will be available at `https://localhost:3000`

### Sideload the Add-in

#### Word/Excel on Windows
```bash
npm run sideload
```

Or manually:
1. Open Word or Excel
2. Go to Insert > My Add-ins > Upload My Add-in
3. Browse to `frontend/public/manifest.xml`

#### Word/Excel on Mac
1. Copy `manifest.xml` to: `~/Library/Containers/com.microsoft.Word/Data/Documents/wef/`
2. Restart Word/Excel
3. Go to Insert > My Add-ins

### Build for Production

```bash
npm run build
```

## Configuration

### API Base URL

Update the API base URL in `src/taskpane/services/api.ts`:

```typescript
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
```

Or create a `.env` file:
```
API_BASE_URL=http://your-api-url:8000
```

### Manifest Configuration

Update `public/manifest.xml`:
- Change `<Id>` to your unique GUID
- Update `<ProviderName>` and `<DisplayName>`
- Update URLs to your hosting domain

## Usage

### Word

1. Open Word and select some text
2. Click "AI Assistant" in the ribbon
3. Choose an action:
   - **Rewrite**: Improve the text in different styles
   - **Analyze**: Get insights about writing style and quality
   - **Summarize**: Create a summary of selected text
   - **Grammar**: Check for grammar issues

### Excel

1. Open Excel and select a data range
2. Click "AI Assistant" in the ribbon
3. Choose a feature:
   - **Formula**: Generate formulas from descriptions
   - **Data Chat**: Ask questions about your data
   - **Insights**: Get comprehensive analysis
   - **Charts**: Get chart recommendations

## Features in Detail

### Context Layer

The add-in uses a three-level context system:
- **Local**: Current selection or cell
- **Section**: Surrounding paragraphs or worksheet
- **Global**: Entire document or workbook summary

### Draft Mode

In Word, AI suggestions can be inserted as:
- **Replace**: Direct replacement of selected text
- **Comment**: Insert as a comment for review

### Caching

Results are cached to improve performance and reduce API calls. Cache can be disabled in settings.

## API Integration

All API calls are made through the services in `src/taskpane/services/api.ts`. The API client handles:
- Authentication (if needed)
- Error handling
- Request/response formatting

## State Management

Uses Zustand for lightweight, efficient state management:
- `documentStore`: Word document state and history
- `excelStore`: Excel data, insights, and analysis
- `settingsStore`: User preferences (persisted to localStorage)

## Office.js API Usage

### Word API
- Selection manipulation
- Text insertion and replacement
- Comment creation
- Document traversal
- Content controls

### Excel API
- Range selection and manipulation
- Formula insertion
- Cell values and formatting
- Chart creation
- Worksheet operations

## Troubleshooting

### Add-in doesn't load
- Check that Office.js is loaded (open browser console)
- Verify manifest.xml is valid: `npm run validate`
- Ensure HTTPS certificates are trusted
- Check that backend API is running

### API calls fail
- Verify API_BASE_URL is correct
- Check CORS configuration on backend
- Ensure backend is running on port 8000

### Changes not appearing
- Clear Office cache: `%LOCALAPPDATA%\Microsoft\Office\16.0\Wef\`
- Restart Office application
- Rebuild: `npm run build`

## Development Tips

### Hot Reload
The dev server supports hot reload. Changes to React components will update automatically.

### Debugging
- Use browser DevTools: Right-click in taskpane > Inspect
- Console logs appear in DevTools console
- Use React DevTools extension for component inspection

### Testing Office.js APIs
Test Office.js code in the browser console:
```javascript
Word.run(async (context) => {
  const selection = context.document.getSelection();
  selection.load('text');
  await context.sync();
  console.log(selection.text);
});
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test in both Word and Excel
4. Submit a pull request

## License

MIT

## Support

For issues and questions, please file an issue on GitHub or contact support.
