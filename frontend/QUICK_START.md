# Quick Start Guide

## Prerequisites
- Node.js 18+ and npm
- Microsoft Office (Word & Excel 2016 or later)
- Backend API running at `http://localhost:8000`

## Installation

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Install Development Certificates (for HTTPS)
```bash
npx office-addin-dev-certs install
```

This will create a trusted SSL certificate for localhost development.

### 3. Verify TypeScript Configuration
```bash
npx tsc --noEmit
```

Should complete with no errors. If you see errors, refer to `TYPESCRIPT_FIXES.md`.

## Development

### Start Development Server
```bash
npm run dev
```

The add-in will be available at `https://localhost:3000`

### Sideload the Add-in

#### Method 1: Using CLI (Recommended)
```bash
npm run sideload
```

#### Method 2: Manual Upload (Windows)
1. Open Word or Excel
2. Go to **Insert** > **My Add-ins**
3. Click **Upload My Add-in**
4. Browse to `frontend/public/manifest.xml`
5. Click **Upload**

#### Method 3: Manual Copy (Mac)
1. Copy `manifest.xml` to:
   - Word: `~/Library/Containers/com.microsoft.Word/Data/Documents/wef/`
   - Excel: `~/Library/Containers/com.microsoft.Excel/Data/Documents/wef/`
2. Restart Word or Excel
3. Go to **Insert** > **My Add-ins**

## Testing

### 1. Test in Word
1. Open Microsoft Word
2. Open the add-in from Insert > My Add-ins
3. Select some text
4. Try these features:
   - **AI Rewrite** - Rewrite the selected text
   - **Analyze** - Get text analysis
   - **Summarize** - Generate a summary

### 2. Test in Excel
1. Open Microsoft Excel
2. Open the add-in from Insert > My Add-ins
3. Select a data range (with headers)
4. Try these features:
   - **Formula** - Generate formulas from descriptions
   - **Data Chat** - Ask questions about your data
   - **Insights** - Get comprehensive analysis
   - **Charts** - Get chart recommendations

## Troubleshooting

### Add-in doesn't load
**Check:**
1. Is the dev server running? (`npm run dev`)
2. Is the URL correct in manifest.xml? (should be `https://localhost:3000`)
3. Are SSL certificates trusted? (run `npx office-addin-dev-certs install` again)

**Solution:**
```bash
# Restart dev server
npm run dev

# Verify manifest
npm run validate
```

### TypeScript Errors
**Solution:**
```bash
# Check for errors
npx tsc --noEmit

# If errors persist, see TYPESCRIPT_FIXES.md
```

### API Connection Issues
**Check:**
1. Is backend running? (should be at `http://localhost:8000`)
2. Check backend health: `curl http://localhost:8000/health`

**Solution:**
Update API URL in `src/taskpane/services/api.ts` if needed:
```typescript
const API_BASE_URL = 'http://your-backend-url:8000';
```

### CORS Errors
**Solution:**
Ensure backend CORS configuration allows `https://localhost:3000`:

```python
# In backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Changes not appearing
**Solution:**
```bash
# Hard refresh the taskpane
# In the add-in window: Ctrl+F5 or Cmd+Shift+R

# Or clear Office cache (Windows)
# Close Office apps, then delete:
%LOCALAPPDATA%\Microsoft\Office\16.0\Wef\

# Restart Office and reload add-in
```

### Office.js not loading
**Check browser console in add-in window:**
1. Right-click in the add-in taskpane
2. Select "Inspect" or "Inspect Element"
3. Check Console tab for errors

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

### Deploy to Production
1. Update manifest.xml with production URLs
2. Host `dist/` folder on HTTPS server
3. Update all URLs in manifest to production domain
4. Distribute manifest.xml to users

## Development Tips

### Hot Reload
The dev server supports hot reload. Most changes will update automatically without refreshing.

### Debugging
1. **Open DevTools:**
   - Right-click in taskpane → Inspect
   - Or use F12 (Windows) / Cmd+Opt+I (Mac)

2. **View Console Logs:**
   ```typescript
   console.log('Debug info:', data);
   ```

3. **Test Office.js:**
   ```typescript
   // In browser console
   Word.run(async (context) => {
     const selection = context.document.getSelection();
     selection.load('text');
     await context.sync();
     console.log(selection.text);
   });
   ```

### VSCode Extensions
Recommended extensions:
- ESLint
- TypeScript and JavaScript Language Features
- Office Add-in Debugger
- Tailwind CSS IntelliSense

## Common Tasks

### Add New Component
```bash
# Create new component
touch src/taskpane/Word/components/MyComponent/MyComponent.tsx
```

### Add New API Endpoint
1. Add function to `src/taskpane/services/api.ts`
2. Use in component:
```typescript
import { wordAPI } from '../services/api';

const response = await wordAPI.rewrite(data);
```

### Update Styling
Edit `src/index.css` (uses Tailwind CSS)

### Add New Store
```typescript
// src/taskpane/store/myStore.ts
import { create } from 'zustand';

interface MyState {
  data: any;
  setData: (data: any) => void;
}

export const useMyStore = create<MyState>((set) => ({
  data: null,
  setData: (data) => set({ data })
}));
```

## Project Structure

```
frontend/
├── src/
│   ├── taskpane/
│   │   ├── App.tsx              # Router
│   │   ├── Word/                # Word features
│   │   ├── Excel/               # Excel features
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API & Office.js
│   │   ├── store/               # State management
│   │   ├── utils/               # Utilities
│   │   └── types/               # Type declarations
│   └── commands/                # Ribbon commands
├── public/
│   ├── manifest.xml             # Office manifest
│   ├── taskpane.html
│   └── commands.html
└── package.json
```

## Support

For issues:
1. Check `TYPESCRIPT_FIXES.md` for TypeScript errors
2. Check `README.md` for detailed documentation
3. Check browser console for runtime errors
4. Check backend logs for API errors

## Next Steps

1. ✅ Install dependencies
2. ✅ Start dev server
3. ✅ Sideload add-in
4. ✅ Test in Word
5. ✅ Test in Excel
6. 📝 Read full documentation in `README.md`
7. 🔧 Customize for your needs

Happy coding! 🚀
