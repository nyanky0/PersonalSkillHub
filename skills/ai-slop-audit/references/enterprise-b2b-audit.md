# Enterprise B2B App Audit Checklist

Context: Internal web apps (React/Vue/Laravel Inertia), not public marketing sites.

## Core Differences from Landing Page Audit
| Landing Page | Enterprise App |
|-------------|---------------|
| Fake stats = slop | Real operational data |
| Unsplash images = red flag | Internal logos/assets only |
| Marketing copy patterns | Business process language |
| CTA conversion focus | Workflow efficiency focus |

## Developer Slop Checklist

### 1. Hardcoded Mock Data
```bash
grep -rn "useState('[A-Z]\\{2,\\}')" resources/js/
grep -rn "initial.*=.*'[^{]" resources/js/ | grep -v "//"
```
Red flags:
- `vessel_code: 'VSL-001'`
- `user_id: '12345'`
- Mock IDs that should come from props/API

### 2. Console.log Production Residue
**Remove** (not needed in production):
- `console.log('Request:', payload)`
- `console.group('Processing...')`
- `console.table(data)`
- Debug step counters

**Keep** (intentional):
- `console.error('Failed to load:', err)` — legitimate error handling
- Conditional debug with guard: `if (debugMode) console.log(...)`

### 3. Inline Styles in JSX
**Convert to Tailwind:**
```jsx
// BAD (inline)
<div style={{ padding: '16px', backgroundColor: '#f8fafc' }}>

// GOOD (Tailwind)
<div className="p-4 bg-slate-50">
```

Check: `grep -c "style={{" *.jsx`
Goal: Error boundaries only (acceptable), all else → Tailwind.

### 4. Emoji in Formal Labels
Context matters:
- **Bad**: `⏱️ Lead Time:`, `📦 Status:`, `✅ Success:`
- **Acceptable**: Icon components (`<CheckCircle />`), status badges with proper semantic meaning

### 5. Font & Design System
Enterprise apps should have:
- Consistent font stack (Inter for body, JetBrains Mono for code)
- Custom color scale from brand guidelines
- No external font dependencies (use local or Google Fonts with fallback)

```bash
# Check Google Fonts usage
grep -rn "fonts.googleapis" resources/views/

# Check font declarations in CSS
grep -n "font-family" resources/css/app.css
```

## Common False Positives (Don't Flag)
- `console.error` in catch blocks — proper error handling
- Conditional debug logs with feature flags — intentional dev tool
- Large component files (>1000 lines) — common in enterprise, not slop
- Complex state management — necessary for business logic
- TypeScript types — actually reduces slop, not increases

## Post-Fix Verification
Always run build after changes:
```bash
npm run build 2>&1 | tail -30
# Look for: ✓ built in Xs (success) or ERROR lines (failure)
```

Exit code 0 = safe to deploy.