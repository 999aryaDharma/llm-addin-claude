# TypeScript Fixes and Common Errors

## Fixed Issues

### 1. Office.js Type Declarations
**Problem:** `Office`, `Word`, `Excel` namespaces not recognized.

**Solution:**
- Added `@types/office-js` in devDependencies
- Created `src/types/office.d.ts` for additional Office.js types
- Created `src/types/global.d.ts` for global declarations

### 2. crypto.randomUUID() Compatibility
**Problem:** `crypto.randomUUID()` not available in all environments.

**Solution:**
- Created utility function `generateId()` in `src/taskpane/utils/helpers.ts`
- Replaced all `crypto.randomUUID()` calls with `generateId()`
- Fallback implementation using Math.random()

### 3. Excel.ChartType Errors
**Problem:** `Excel.ChartType` enum causing type errors.

**Solution:**
- Changed `chartType` parameter from `Excel.ChartType` to `string`
- Use type assertion `as any` when passing to Excel.js API
- Map chart type strings to Excel chart type names:
  - `'ColumnClustered'` for bar charts
  - `'Line'` for line charts
  - `'Pie'` for pie charts

### 4. Unused Variables
**Problem:** Variables declared but not used causing TS errors.

**Solution:**
- Removed unused `selectedRange` from DataChat component
- Prefixed unused parameters with `_` (e.g., `_author`)
- Removed unused `range` variable in wordInterop

### 5. getPreviousSibling/getNextSibling Type Errors
**Problem:** Methods returning `Word.Paragraph | Word.OfficeExtension.ClientResult<Word.Paragraph>`.

**Solution:**
- Added type assertion `as Word.Paragraph`
- Wrapped in try-catch to handle errors

### 6. Excel AutoFilter API
**Problem:** `range.autoFilter` not available, should be `sheet.autoFilter`.

**Solution:**
- Changed from `range.autoFilter` to `sheet.autoFilter`
- Access via active worksheet instead of range

### 7. Zustand Persist Middleware
**Problem:** Type errors with `persist` middleware.

**Solution:**
- Added type declaration in `src/types/global.d.ts`
- Export type from `'zustand/middleware'`

## Common TypeScript Errors and Solutions

### Error: Cannot find namespace 'Office'
```bash
Cannot find namespace 'Office'.
```

**Solution:**
1. Ensure `@types/office-js` is installed:
```bash
npm install --save-dev @types/office-js
```

2. Add reference in component:
```typescript
/// <reference types="@types/office-js" />
```

### Error: Property does not exist on type
```bash
Property 'randomUUID' does not exist on type 'Crypto'.
```

**Solution:**
Use the helper function:
```typescript
import { generateId } from '../utils/helpers';
const id = generateId(); // Instead of crypto.randomUUID()
```

### Error: Parameter implicitly has 'any' type
```bash
Parameter 'event' implicitly has an 'any' type.
```

**Solution:**
Add explicit type annotation:
```typescript
// Before
function handler(event) { ... }

// After
function handler(event: Office.AddinCommands.Event) { ... }
```

### Error: Cannot use JSX unless '--jsx' flag is provided
```bash
Cannot use JSX unless the '--jsx' flag is provided.
```

**Solution:**
Ensure `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "jsx": "react-jsx"
  }
}
```

## Build and Type Checking

### Check for TypeScript errors
```bash
npx tsc --noEmit
```

### Build with type checking
```bash
npm run build
```

### Watch mode for development
```bash
npm run dev
```

## Best Practices

### 1. Always import helpers
```typescript
import { generateId } from '../utils/helpers';
```

### 2. Use proper Office.js error handling
```typescript
try {
  await Word.run(async (context) => {
    // Your code
    await context.sync();
  });
} catch (error) {
  console.error('Office.js error:', error);
}
```

### 3. Type your state properly
```typescript
// Good
const [data, setData] = useState<MyType | null>(null);

// Avoid
const [data, setData] = useState(null);
```

### 4. Use type assertions carefully
```typescript
// Only when you're certain
const chart = sheet.charts.add(chartType as any, range, seriesBy);

// Better: proper typing
const chartTypeMap: Record<string, string> = {
  'bar': 'ColumnClustered',
  'line': 'Line'
};
```

## VSCode Setup

### Recommended settings.json
```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Recommended extensions
- ESLint
- TypeScript and JavaScript Language Features
- Office Add-in Debugger

## Still Having Issues?

1. **Clear TypeScript cache:**
```bash
rm -rf node_modules/.cache
```

2. **Restart TypeScript server in VSCode:**
- Open Command Palette (Ctrl+Shift+P)
- Type "TypeScript: Restart TS Server"

3. **Reinstall dependencies:**
```bash
rm -rf node_modules package-lock.json
npm install
```

4. **Check tsconfig.json paths:**
Ensure all path mappings are correct:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```
