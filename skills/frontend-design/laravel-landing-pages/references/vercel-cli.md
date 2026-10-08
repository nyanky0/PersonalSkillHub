# Vercel CLI — auth, deploy, rename (praktik terbukti)

## Install & login

```bash
# tanpa install global (cache npx):
npx -y vercel@latest --version

# login device-flow (butuh user buka URL di browser):
npx -y vercel@latest login
# -> print: Visit https://vercel.com/oauth/device?user_code=XXXX-XXXX
# user approve di browser; CLI tunggu otomatis (poll process status sampai "signed in")
```

## Lokasi auth (CLI 58+)

Auth TIDAK di `~/.vercel/auth.json` (folder itu kosong/tidak ada) — CLI 58 simpan di:
`~/.local/share/com.vercel.cli/auth.json` → `{"token": "...", "email": ...}`

Ekstrak token tanpa print:
```bash
node -e "console.log(JSON.parse(require('fs').readFileSync('/home/maulana/.local/share/com.vercel.cli/auth.json')).token)"
```

## Deploy folder statis

```bash
npx -y vercel@latest deploy dist --prod --yes
```
- Pertama kali tanpa project link → CLI buat project baru, nama DEFAULT DARI NAMA FOLDER (folder `dist` → project `dist` — jelek, rename setelahnya).
- Output: `Production https://<hash>-<user>-projects.vercel.app` + `Aliased https://<slug>.vercel.app`
- Redeploy: `vercel deploy dist --prod --yes` lagi (project sudah ter-link otomatis di ~/.local/share/com.vercel.cli).

## Rename project (CLI TIDAK punya command rename — pakai API)

```bash
TOKEN=$(node -e "console.log(JSON.parse(require('fs').readFileSync('/home/maulana/.local/share/com.vercel.cli/auth.json')).token)")
curl -s -X PATCH "https://api.vercel.com/v9/projects/<nama-lama>" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"<nama-baru>"}'
```
- Rename TIDAK mengubah URL deployment yang sudah live (slug vercel.app tetap).
- Nama project baru kepake untuk deploy berikutnya.

## Verifikasi live

```bash
B="https://<slug>.vercel.app"
curl -s -o /dev/null -w "index: %{http_code}\n" "$B/"
curl -s -o /dev/null -w "css: %{http_code}\n" "$B/build/assets/<hash>.css"   # cek nama asli dari index.html
curl -s -o /dev/null -w "foto: %{http_code}\n" "$B/images/profile.jpg"
```
Lalu `browser_navigate` ke production URL, cek aksesibility snapshot lengkap + 0 JS error di `browser_console`.

## Catatan

- Deploy pertama user login device-flow: process di background pty, poll sampai "Congratulations! You are now signed in."
- Laravel ga bisa native di Vercel — selalu static export (render blade → dist/).
- Custom domain: attach di dashboard (Settings → Domains), gratis di akun hobby.
