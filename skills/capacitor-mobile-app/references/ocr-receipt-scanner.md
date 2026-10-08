# OCR Receipt Scanner — Implementation Reference

Camera-based receipt/struk scanning using Tesseract.js + Capacitor Camera plugin.

## Dependencies

```bash
npm install @capacitor/camera tesseract.js --legacy-peer-deps
```

`--legacy-peer-deps` required — capacitor-camera@8 has peer dep conflicts with Capacitor 6 core.

## Android Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
```

`READ_MEDIA_IMAGES` is for Android 13+ (API 33+). `READ_EXTERNAL_STORAGE` covers Android 12 and below.

## Build Toolchain Impact

Adding `@capacitor/camera@8.x` triggers `androidx.core:core:1.17.0` which requires:
- `compileSdkVersion = 36` (was 34)
- `targetSdkVersion = 36`
- `minSdkVersion = 24` (ioncameralib needs 24, was 22)
- AGP `8.9.1` (was 8.2.1)
- Gradle wrapper `8.11.1` (was 8.2.1)
- SDK `platforms;android-36` + `build-tools;36.0.0` installed

See SKILL.md "Gradle/AGP upgrade chain" section for full upgrade recipe.

## OCR Scanner Utility (src/utils/ocrScanner.js)

**CRITICAL**: Do NOT top-level `import Tesseract from 'tesseract.js'`. This bundles the ~4MB worker into the main chunk, slowing startup. Use dynamic import inside the scan function.

**CRITICAL**: Account numbers in bank screenshots are 8-16 bare digits that get misidentified as amounts. See "Account number guard" below.

```js
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera'

// Account number guard — reject bare 8+ digit sequences
function isAccountNumber(raw) {
  const cleaned = raw.replace(/[\s.,]/g, '')
  return /^\d{8,}$/.test(cleaned)
}

// Parse OCR text → extract amounts, date, note
export function parseReceiptText(text) {
  if (!text || !text.trim()) return null

  const amounts = []
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean)

  // Regex requires Rp prefix OR thousands separator — won't match bare account numbers
  const re = /(?:Rp\.?\s*)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)|(?:^|\s)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)(?:\s|$)/gm
  let m
  while ((m = re.exec(text)) !== null) {
    let raw = m[1] || m[2]
    if (!raw || isAccountNumber(raw)) continue
    // ... parse raw into number, push to amounts
  }

  // Also check lines near transfer/bayar keywords (amount may lack Rp prefix)
  // ...

  // Pick best amount: total-keyword match > Rp-prefixed > largest
  // ...
}

// Open camera/gallery → OCR → parse
export async function scanReceipt(fromGallery = false) {
  const photo = await Camera.getPhoto({
    quality: 90,
    resultType: CameraResultType.DataUrl,
    source: fromGallery ? CameraSource.Photos : CameraSource.Camera,
  })

  const Tesseract = await import('tesseract.js')  // dynamic import
  const result = await Tesseract.recognize(photo.dataUrl, 'ind+eng', { logger: () => {} })
  const text = result.data.text
  const parsed = parseReceiptText(text)
  return { ok: !!parsed, parsed, rawText: text, photo: photo.dataUrl }
}
```

## Scan View Pattern (src/views/Scan.vue)

UX flow:
1. Two buttons: "Foto Struk" (camera) → `scanReceipt(false)`, "Dari Galeri" → `scanReceipt(true)`
2. Show OCR progress (Tesseract can take 5-30s)
3. Show parsed result: amount, date, note — all editable
4. User can edit amount, date, category before saving
5. Save button inserts transaction into SQLite

Key template sections:
- Camera button + gallery button side by side
- Progress bar during OCR (Tesseract `logger` callback for progress %)
- Parsed result preview with editable fields
- Category dropdown (loaded from `categories` table)
- "Simpan" button → `db.run('INSERT INTO transactions ...')`

## Account number guard

Bank transfer screenshots contain BOTH the transfer amount AND the destination account number (8-16 bare digits). Without a guard, `Math.max()` picks the account number (e.g., `1234567890` = 1.2B) instead of the actual amount (`2.000.000` = 2M).

Three-layer defense:
1. **Regex**: Only match amounts with `Rp` prefix or thousands-separator dots (`\d{1,3}(?:\.\d{3})+`). Bare 8+ digit strings don't match.
2. **`isAccountNumber()`**: After regex match, check if the raw string (stripped of separators) is 8+ digits — reject it.
3. **Keyword proximity**: Prefer amounts on lines containing "transfer", "trf", "bayar", "total" — these are more likely the actual transaction amount.

Apply this guard in ALL parsers: `ocrScanner.js`, `shareParser.js`, AND `GDBNotifPlugin.java`.

## Pitfalls

- **Tesseract traineddata download**: First OCR run downloads ~4MB `eng.traineddata` / `ind.traineddata`. Subsequent runs use cache. Show loading state.
- **OCR accuracy**: ~60-80% on receipts. Never auto-save — always show parsed result for confirmation.
- **Camera permission**: On Android 13+, `READ_MEDIA_IMAGES` is the correct permission (not `READ_EXTERNAL_STORAGE`). Both should be declared for backward compat.
- **Base64 photo size**: `CameraResultType.DataUrl` returns base64-encoded image. Limit width to 1200px to keep memory reasonable.
- **Gallery fallback**: Use `CameraSource.Photos` for gallery-only. Pass `fromGallery` param to `scanReceipt()`.
- **Dynamic import required**: `await import('tesseract.js')` inside scan function. Top-level import bundles 4MB worker into main chunk.
- **Account numbers masquerading as amounts**: Always use `isAccountNumber()` guard. See above.
