# 🚀 START HERE - Office LLM Add-in

## Quick Start (3 Steps)

### 1️⃣ Install Dependencies
```bash
cd frontend
npm install --legacy-peer-deps
```
⏱️ Takes ~1 minute

### 2️⃣ Start Development Server
```bash
npm run dev
```
🌐 Opens at: https://localhost:3000

### 3️⃣ Load in Office
```bash
npm run sideload
```
Or manually: Insert > My Add-ins > Upload `public/manifest.xml`

---

## ✅ Status Check

Run this to verify everything works:
```bash
npx tsc --noEmit
```

Expected output: **No errors!** ✅

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── taskpane/
│   │   ├── App.tsx          # Main router
│   │   ├── Word/            # Word features
│   │   ├── Excel/           # Excel features
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API & Office.js
│   │   ├── store/           # State (Zustand)
│   │   └── utils/           # Helpers
│   └── types/               # TypeScript types
├── public/
│   └── manifest.xml         # Office manifest
└── package.json
```

---

## 🎯 Key Features

### Word Add-in
- ✨ AI Rewrite
- 📊 Text Analysis
- 📝 Summarization
- ✅ Grammar Check
- 🔍 Reference Search

### Excel Add-in
- 🧮 Formula Generator
- 💬 Data Chat
- 📈 Insights & Analysis
- 📊 Chart Recommendations
- 🔗 Correlation Detection

---

## 🛠️ Development Commands

```bash
# Type check
npx tsc --noEmit

# Start dev server
npm run dev

# Build for production
npm run build

# Validate manifest
npm run validate

# Sideload to Office
npm run sideload

# Fix JSX issues (if needed)
.\fix-jsx.ps1  # Windows
./fix-jsx.sh   # Mac/Linux
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `README.md` | Full documentation |
| `QUICK_START.md` | Detailed setup guide |
| `FINAL_FIX_SUMMARY.md` | All fixes applied |
| `TYPESCRIPT_FIXES.md` | TS troubleshooting |
| `JSX_ERRORS_FIX.md` | JSX troubleshooting |

---

## 🔧 Configuration

### Backend API
Default: `http://localhost:8000`

To change, edit: `src/taskpane/services/api.ts`
```typescript
const API_BASE_URL = 'http://your-url:8000';
```

### Manifest
For production, update URLs in `public/manifest.xml`:
```xml
<SourceLocation DefaultValue="https://your-domain.com/taskpane.html"/>
```

---

## 🐛 Troubleshooting

### Error: Dependencies not installed
```bash
npm install --legacy-peer-deps
```

### Error: TypeScript errors
```bash
# Restart TS server in VSCode
Ctrl+Shift+P → "TypeScript: Restart TS Server"
```

### Error: Add-in not loading
```bash
# Reinstall SSL certificates
npx office-addin-dev-certs install

# Restart dev server
npm run dev
```

### Error: CORS issues
Check backend allows: `https://localhost:3000`

---

## 📝 Notes

### Dependencies
- **React 18** (installed with --legacy-peer-deps)
- **TypeScript 5.3+**
- **Office.js** (latest)
- **Zustand** (state management)
- **Tailwind CSS** (styling)

### TypeScript Config
- JSX mode: `react` (not `react-jsx`)
- Strict mode: `false` (for development)
- All type declarations in `src/types/`

### Known Issues
- `react-diff-viewer` requires `--legacy-peer-deps`
- Can be replaced with React 18 compatible alternative

---

## ✅ Pre-Flight Checklist

Before starting development:

- [ ] Dependencies installed
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] Dev server starts (`npm run dev`)
- [ ] Backend API running (port 8000)
- [ ] SSL certificates installed
- [ ] Office apps available (Word/Excel)

---

## 🎯 Next Steps

1. ✅ Verify everything works (see above)
2. 📖 Read `QUICK_START.md` for details
3. 💻 Start development
4. 🧪 Test in Word and Excel
5. 🚀 Build for production

---

## 🆘 Need Help?

1. Check `FINAL_FIX_SUMMARY.md` for recent fixes
2. Check `TYPESCRIPT_FIXES.md` for type errors
3. Check `JSX_ERRORS_FIX.md` for JSX issues
4. Check browser console for runtime errors
5. Check backend logs for API errors

---

## 📊 Current Status

✅ **All TypeScript Errors Fixed**
✅ **All JSX Errors Fixed**
✅ **Dependencies Installed (860 packages)**
✅ **Build Configuration Complete**
✅ **Ready for Development**

---

**Version:** 2.5.0
**Last Updated:** 2025-10-27
**Status:** 🟢 Ready to Use

---

## 🎉 You're All Set!

Start development with:
```bash
npm run dev
```

Open Word or Excel, load the add-in, and start coding! 🚀
