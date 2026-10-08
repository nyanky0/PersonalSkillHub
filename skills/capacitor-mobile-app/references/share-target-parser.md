# Share Target Parser — Indonesian bank/e-wallet notifications

Reference for `src/utils/shareParser.js` in the GDB app. Receives raw notification text
shared from another Android app and extracts a transaction: `{ type, amount, note, date }`.

## Known-good implementation (with account-number guard)

```js
// Guard: reject bare 8+ digit numbers (bank account numbers, not amounts)
function isAccountNumber(raw) {
  const cleaned = raw.replace(/[\s.,]/g, '')
  return /^\d{8,}$/.test(cleaned)
}

function parseAmount(text) {
  const candidates = []
  // Only match Rp-prefixed or thousands-separated numbers — skip bare account numbers
  const re = /(?:Rp\.?\s*)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)|(?:^|\s)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?)(?:\s|$)/gm
  let m
  while ((m = re.exec(text)) !== null) {
    let raw = m[1] || m[2]
    if (!raw || isAccountNumber(raw)) continue
    if (raw.includes(',')) raw = raw.replace(/\./g, '').replace(',', '.')
    else raw = raw.replace(/\./g, '')
    const n = parseFloat(raw)
    if (!isNaN(n) && n > 0) candidates.push(n)
  }
  return candidates.length ? Math.max(...candidates) : null
}

function parseType(text) {
  if (/masuk|diterima|kredit|pemasukan|income|received/i.test(text)) return 'income'
  if (/keluar|debit|bayar|beli|payment|debited/i.test(text)) return 'expense'
  return null // default expense when saved
}

function parseDate(text) {
  const d = text.match(/(\d{1,2})[/\-.](\d{1,2})(?:[/\-.](\d{2,4}))?/)
  if (d) {
    const y = d[3] ? (d[3].length === 2 ? '20' + d[3] : d[3]) : new Date().getFullYear()
    return `${y}-${String(d[2]).padStart(2,'0')}-${String(d[1]).padStart(2,'0')}`
  }
  return new Date().toISOString().slice(0, 10)
}
```

`parseTransaction(rawText)` returns `null` if no amount found (signal to show "can't parse" error).

## Sample inputs

| Input | type | amount | date |
|-------|------|--------|------|
| `Anda menerima transfer Rp150.000 dari Budi. Saldo: Rp500.000` | income | 150000 | today |
| `Pembayaran GOFOOD Rp45.000 ke Resto ABC berhasil. Saldo Rp255.000` | expense | 45000 | today |
| `23/08/2026 Transfer masuk Rp 1.250.000` | income | 1250000 | 2026-08-23 |
| `Transfer 2.000.000 ke 1234567890 berhasil` | expense | 2000000 | today (NOT 1234567890) |

## Key fix: account numbers vs amounts

Bank transfer messages contain both the transfer amount AND the destination account number (8-16 bare digits). Without the `isAccountNumber()` guard, `Math.max()` picks the account number because `1234567890` > `2000000`.

The regex explicitly requires either:
1. An `Rp` prefix, OR
2. Thousands separator dots (`\d{1,3}(?:\.\d{3})+`)

Bare digit sequences like `1234567890` do NOT match the regex (no separator dots), and the `isAccountNumber()` guard provides a second safety net.

## Notes
- Uses `Math.max(...candidates)` to pick the largest number among valid candidates — handles "amount + balance" texts where balance is also a number.
- Default date = today. Most notifications omit an explicit date; user edits later if needed.
- On Android, route incoming shared text to `/share` (Share.vue) which previews the parse and saves.
- Apply the same guard in `ocrScanner.js` and `GDBNotifPlugin.java` — consistency across all parsers.
