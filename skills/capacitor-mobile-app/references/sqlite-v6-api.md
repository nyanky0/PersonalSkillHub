# @capacitor-community/sqlite v6 — Correct API Shapes

The plugin's connection object uses **positional arguments**, NOT the options-object shape the online docs/v7+ suggest. Mixing these up silently breaks storage (app opens but transactions never persist).

## Correct calls (v6.0.2, pairs with Capacitor core v6)

```js
import { Capacitor } from '@capacitor/core'
import { SQLiteConnection } from '@capacitor-community/sqlite'

let sqlite, conn
const DB_NAME = 'gdb'

async function ensureConn() {
  if (conn) return conn
  if (!sqlite) {
    if (Capacitor.isNativePlatform()) {
      const mod = await import('@capacitor-community/sqlite')
      sqlite = new mod.SQLiteConnection(mod.CapacitorSQLite)
    } else {
      await import('jeep-sqlite')                       // registers <jeep-sqlite> custom element
      const mod = await import('@capacitor-community/sqlite')
      sqlite = new mod.SQLiteConnection(mod.CapacitorSQLite)
      await sqlite.initWebStore()                       // WEB ONLY — required before createConnection
    }
  }
  await sqlite.createConnection(DB_NAME, false, 'no-encryption', 1, false)  // (db, encrypted, mode, version, readonly)
  conn = await sqlite.retrieveConnection(DB_NAME, false)
  await conn.open()
  await conn.execute(SCHEMA, false)                     // execute(statements: string, transaction?: boolean)
  return conn
}

// run(statement, values?: any[], transaction?: boolean)
await conn.run('INSERT INTO t (a,b) VALUES (?,?)', [v1, v2], false)

// query(statement, values?: any[]) -> { values: [...] }  (NOT a bare array)
const res = await conn.query('SELECT * FROM t WHERE id=?', [id])
const rows = res.values || []
```

## Gotchas
- `conn.run` positional — passing `{statement, values}` object throws or no-ops.
- `conn.query` returns `{ values: [...] }`, not the array directly. Forgetting `.values` yields `undefined` → views show nothing.
- Web (dev/browser) REQUIRES `await sqlite.initWebStore()` before `createConnection`, plus `<jeep-sqlite></jeep-sqlite>` in `index.html`.
- Native Android: no `initWebStore`; uses the real SQLite engine.
- Version pairing: sqlite v6.x ↔ Capacitor core v6.x. The v8 plugin needs core v8 — do NOT mix.

## Real GDB implementation
Full file: `/home/maulana/gdb-app/src/db/index.js` (web/native branch, schema + run/all/get helpers).
