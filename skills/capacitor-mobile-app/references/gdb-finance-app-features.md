# GDB Finance App — Feature Map (Web vs Mobile)

Reference for what features the GDB (Gaji Dana Bahagia) app includes, used when ensuring mobile parity with the Next.js web version.

## Web (Next.js — btracker-web/app/page.tsx)

Single-page app with API calls to Laravel backend. Features:

- **Auth**: Login/Register (JWT token, localStorage) — *skip for offline mobile*
- **Dashboard**: Saldo, total income/expense, cycle offset (bulan aktif)
- **Budget**: Budget awal, sisa, batas harian, alarm over-budget
- **Limit Kopi**: Monthly kopi spend vs limit, alarm
- **Quick Spend**: Buttons for Makan/Kopi/Bensin/Servis/Parkir/Tagihan + Bekal + Pemasukan
- **User Selector**: Maulana/Istri
- **Sumber Dana**: Tunai/GoPay/Rekening
- **Trend MoM**: Compare this month vs last month (hemat/boros badge)
- **Charts**: PieChart (distribusi), LineChart (prediksi budget), BarChart (simulasi investasi)
- **Emergency Fund**: Target + current, top up
- **Bekal**: Tabungan terpisah dari expense
- **Recurring/Tagihan**: Auto-debet list (nama, jumlah, tanggal, sumber_dana)
- **Goals**: Shared goals, top up
- **Settings**: Budget, limit kopi, target pensiun, WA number, payday
- **Simulasi Investasi**: Bar chart with rate slider
- **Export**: No CSV export on web

## Mobile (Capacitor — gdb-app)

Offline-first with local SQLite. Parity achieved:

- **No auth** (offline, single-user)
- **Dashboard**: Saldo + income/expense/bekal + trend MoM + alarms
- **Budget bar** + batas harian (auto-calc days remaining)
- **Limit kopi bar** + alarm
- **Quick Spend**: 8 buttons matching web
- **User selector + Sumber dana**: In form + quick spend header
- **Bar chart**: 6-month trend (income vs expense)
- **Emergency fund**: Top up + pakai + progress bar (tracked as goal + setting)
- **Bekal**: is_bekal flag on transactions
- **Tagihan page**: CRUD recurring + "Bayar" button auto-creates expense
- **Goals**: Topup prompt + achieved badge
- **Settings**: Budget, limit kopi, emergency target, target pensiun, WA, payday
- **Export CSV**: Download from browser
- **Search/filter**: On riwayat + transaksi pages
- **Share Target**: PWA + native intent filter for bank notification parsing
- **Notification Listener**: Auto-capture from bank/e-wallet notifs via native NotificationListenerService + Capacitor plugin bridge (see references/native-notification-listener.md)
- **Cycle Offset**: Navigate ◀ ▶ between pay cycles (payday → payday). All saldo/budget/kopi calculations filtered to active cycle, NOT all-time.
- **Budget = Saldo Awal**: When budget is set, it acts as opening balance. Saldo = Budget - Expenses (not totalIncome - Expenses). Display label adapts: "Budget" when budget set, "Masuk" when not.
- **OCR Receipt Scanner**: Camera capture → Tesseract.js OCR → parse amounts/dates → preview → save as transaction. Accessible via Scan tab in bottom nav. See references/ocr-receipt-scanner.md.

## Intentionally Skipped on Mobile

- Auth (offline, no server)
- PieChart, LineChart (Bar chart sufficient for mobile)
- Simulasi investasi (YAGNI — user didn't request)
