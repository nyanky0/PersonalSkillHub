# SANITY Examples — Before & After

Real-world examples menunjukkan perbedaan response kualitas sebelum dan sesudah SANITY Protocol.

---

## Example 1: Flutter Function Verification

**Prompt:** "Bagaimana cara hapus item dari SharedPreferences di Flutter?"

### ❌ Tanpa SANITY
```dart
// Langsung jawab tanpa verifikasi
SharedPreferences prefs = await SharedPreferences.getInstance();
prefs.delete('key_name');  // ← SALAH! Method ini tidak ada
```

### ✅ Dengan SANITY
```
[Training Knowledge check: SharedPreferences API]
[🟢 CONFIRMED dari training data] Method yang benar adalah remove(), bukan delete():

SharedPreferences prefs = await SharedPreferences.getInstance();
await prefs.remove('key_name');  // Benar — return Future<bool>

// Untuk hapus semua:
await prefs.clear();  // Hapus semua keys

[⚠️ Training Knowledge, cutoff Aug 2025 — verifikasi di pub.dev/packages/shared_preferences]
```

---

## Example 2: File Content Verification

**Prompt:** "Apakah AppDelegate.swift sudah dikonfigurasi untuk push notifications?"

### ❌ Tanpa SANITY
```
"Ya, AppDelegate.swift biasanya sudah dikonfigurasi secara default dengan 
UNUserNotificationCenter delegation dan didRegisterForRemoteNotificationsWithDeviceToken handler."
[Tidak membaca file, hanya prediksi berdasarkan pattern]
```

### ✅ Dengan SANITY
```
[Read: ios/Runner/AppDelegate.swift]

Setelah membaca file:
- Baris 1-20: Standard Flutter AppDelegate setup ✓
- Push notification setup: BELUM ADA [🟢 CONFIRMED]
- Tidak ada UNUserNotificationCenterDelegate conformance
- Tidak ada didRegisterForRemoteNotificationsWithDeviceToken

[🟢 CONFIRMED] File ini BELUM dikonfigurasi untuk push notifications.
Perlu ditambahkan:
1. UNUserNotificationCenterDelegate conformance
2. requestAuthorization() di didFinishLaunchingWithOptions
3. register handler methods
```

---

## Example 3: Database Query Verification

**Prompt:** "Tulis query untuk ambil 10 user terbaru yang sudah verified."

### ❌ Tanpa SANITY
```sql
-- Langsung tulis tanpa tahu schema
SELECT * FROM users 
WHERE is_verified = true 
ORDER BY created_at DESC 
LIMIT 10;
```

### ✅ Dengan SANITY
```
[ASUMSI SCHEMA] Saya tidak tahu schema database kamu. Saya akan tulis query 
berdasarkan [ASUMSI] nama kolom yang umum digunakan.

[PERLU VERIFIKASI] Pastikan nama kolom ini sesuai dengan schema aktual:

-- Jika kolom-kolomnya: id, email, is_verified (boolean), created_at (timestamp)
SELECT id, email, created_at 
FROM users 
WHERE is_verified = TRUE 
ORDER BY created_at DESC 
LIMIT 10;

[ASUMSI] Menggunakan PostgreSQL/MySQL. Syntax mungkin berbeda untuk SQLite.
[PERLU KONFIRMASI] Jalankan `\d users` (PostgreSQL) atau `DESCRIBE users` (MySQL) 
untuk verifikasi nama kolom yang benar.
```

---

## Example 4: Package Version Claim

**Prompt:** "Berapa versi Riverpod yang saya pakai?"

### ❌ Tanpa SANITY
```
"Berdasarkan project Flutter modern, kemungkinan kamu menggunakan Riverpod 2.x 
yang mendukung AsyncNotifier dan FamilyNotifier."
[Tebak-tebakan, tidak baca pubspec]
```

### ✅ Dengan SANITY
```
[Read: pubspec.yaml]

Dari pubspec.yaml baris 23:
  flutter_riverpod: ^3.0.0-beta.1

[🟢 CONFIRMED] Kamu menggunakan flutter_riverpod ^3.0.0-beta.1 (pre-release).

Catatan penting:
[⚠️ Training Knowledge] Riverpod 3.x API mungkin berbeda dari yang ada di training 
data saya. Untuk API reference yang akurat, cek https://riverpod.dev/docs
```

---

## Example 5: Math Calculation with Verification

**Prompt:** "Berapa storage yang dibutuhkan kalau tiap user punya rata-rata 50 foto, 
masing-masing 2MB, untuk 100,000 users?"

### ❌ Tanpa SANITY
```
"Sekitar 10TB storage yang dibutuhkan."
[Tidak ada show work, susah diverifikasi]
```

### ✅ Dengan SANITY
```
Mari hitung step by step [🟢 CONFIRMED — semua langkah verified]:

1. Storage per user:
   50 foto × 2 MB/foto = 100 MB/user

2. Total raw storage:
   100,000 users × 100 MB/user = 10,000,000 MB = 10,000 GB = 10 TB

3. Dengan redundancy (3x replication — standard S3/GCS):
   10 TB × 3 = 30 TB stored capacity needed

4. Dengan 20% overhead untuk metadata/thumbnails:
   30 TB × 1.2 = 36 TB total

JAWABAN: ~36 TB dengan redundancy standar, atau 10 TB raw.

[ASUMSI] Foto tidak dicompress saat upload. Jika ada compression 50%, 
total menjadi ~18 TB dengan redundancy.
```

---

## Example 6: Recovery Protocol in Action

**Prompt sebelumnya:** "Gunakan `context.read<UserProvider>().fetchUser()` ya"  
**Respons sebelumnya:** "Oke, gunakan kode itu."

**User:** "Error! ProviderScope not found..."

### ❌ Tanpa SANITY
```
"Coba tambahkan ProviderScope di main.dart sebelum runApp()..."
[Defense tanpa mengakui error]
```

### ✅ Dengan SANITY (Recovery Protocol)
```
⚠️ KOREKSI: Saya tadi keliru merespons tanpa memverifikasi kode kamu.

[Read: main.dart]
[Read: lib/providers/user_provider.dart]

Setelah verifikasi:
- ProviderScope memang belum ada di main.dart (baris 1-15, tidak ada ProviderScope)
- Project ini menggunakan Riverpod 3.x — syntax yang benar berbeda

Yang BENAR untuk Riverpod 3.x:
// main.dart
void main() {
  runApp(ProviderScope(child: MyApp()));  // ← Harus di sini
}

// Di widget
final user = ref.watch(userProvider);  // ← Gunakan ref.watch, bukan context.read

[🟢 CONFIRMED dari membaca actual files]
Maaf atas respons sebelumnya yang tidak diverifikasi terlebih dahulu.
```

---

*Examples ini menunjukkan perbedaan nyata antara AI yang hallucinate dengan AI yang beroperasi di bawah SANITY Protocol.*
