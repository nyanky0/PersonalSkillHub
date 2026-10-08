/**
 * Kerangka verifikasi UI layar lebar: buka app lokal di browser ASLI milik user
 * (default Microsoft Edge), login, lalu ASSERT teks DOM — bukan screenshot.
 *
 * Salin ke <project>/scripts/verify-<fitur>.cjs lalu sesuaikan bagian CONFIG + CHECKS.
 * Jalankan: node scripts/verify-<fitur>.cjs     (exit code 1 kalau ada assertion gagal)
 *
 * Pakai browser terpasang (channel msedge / chrome / brave), JANGAN memasang browser baru.
 */
const fs = require('fs');
const os = require('os');
const path = require('path');

/** Playwright: dari node_modules project, atau dari cache npx (npx playwright install ...). */
function loadChromium() {
    try { return require('playwright').chromium; } catch (e) { /* cari di cache npx */ }
    const base = path.join(os.homedir(), 'AppData', 'Local', 'npm-cache', '_npx');
    for (const dir of (fs.existsSync(base) ? fs.readdirSync(base) : [])) {
        const mod = path.join(base, dir, 'node_modules', 'playwright');
        if (fs.existsSync(mod)) return require(mod).chromium;
    }
    throw new Error('playwright tidak ditemukan - jalankan: npx playwright install chromium');
}
const chromium = loadChromium();

// ---------------------------------------------------------------- CONFIG
const BASE = process.env.APP_BASE || 'http://127.0.0.1:8000';
const USER = process.env.APP_USER || 'admin';
const PASS = process.env.APP_PASS || 'password';
const CHANNEL = process.env.APP_BROWSER || 'msedge'; // msedge | chrome | brave
const TARGET = BASE + (process.env.APP_PATH || '/');
const SHOT = process.env.APP_SHOT || path.join('storage', 'app', 'verify', 'ui.png');

// ---------------------------------------------------------------- HELPERS
let failed = 0;
const check = (label, ok, extra = '') => {
    console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}${extra ? ' — ' + extra : ''}`);
    if (!ok) failed++;
};

/** Teks dari elemen yang cocok selector, sudah di-trim. */
const texts = (page, selector) => page.$$eval(selector, (els) =>
    els.map((e) => (e.textContent || '').trim()).filter(Boolean));

(async () => {
    const browser = await chromium.launch({ channel: CHANNEL, headless: true });
    const page = await browser.newPage({ viewport: { width: 1680, height: 1000 } });
    page.on('pageerror', (e) => console.log('PAGE-ERR:', String(e).slice(0, 200)));

    // 1. login — dump dulu nama field-nya, jangan menebak 'email'.
    await page.goto(BASE + '/login', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);
    const fields = await page.evaluate(() =>
        [...document.querySelectorAll('input')].map((i) => ({ name: i.name, type: i.type })));
    console.log('INPUT-FIELDS:', JSON.stringify(fields));

    const userField = fields.find((f) => f.name === 'username') || fields.find((f) => f.type === 'text');
    if (userField) await page.fill(`input[name="${userField.name}"]`, USER);
    await page.fill('input[type="password"]', PASS);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(5000);
    console.log('URL-AFTER-LOGIN:', page.url());

    // 2. selesaikan pemilihan cabang/tenant kalau ada (tombol submit-nya).
    if (/select-branch|select-tenant|choose/i.test(page.url())) {
        const confirm = await page.$('button:has-text("Masuk")');
        if (confirm) await confirm.click();
        else await page.click('button[type="submit"]');
        await page.waitForTimeout(5000);
        console.log('URL-AFTER-BRANCH:', page.url());
    }

    // 3. buka URL target (deep link dengan filter aktif = jalur yang paling mungkin rusak).
    await page.goto(TARGET, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(6000); // beri waktu lazy fetch / render pohon
    console.log('URL-TARGET:', page.url());

    // ------------------------------------------------------------ CHECKS
    // Ganti dengan assertion khas fitur. Contoh pola "teks DOM":
    //   const rows = await texts(page, 'aside nav a span');
    //   check('menu sidebar tampil', rows.length > 0, `${rows.length} baris`);
    //   check('tidak ada label kosong', emptyLabels === 0, `${emptyLabels} kosong`);
    const body = await page.evaluate(() => document.body.innerText);
    check('halaman termuat (bukan halaman login)', !/log ?in/i.test(page.url()), page.url());
    check('konten utama tidak kosong', body.trim().length > 200, `${body.trim().length} char`);

    fs.mkdirSync(path.dirname(SHOT), { recursive: true });
    await page.screenshot({ path: SHOT, fullPage: false });
    console.log(`\nscreenshot: ${SHOT}`);
    await browser.close();

    console.log(failed === 0 ? '\nSEMUA ASSERTION LOLOS' : `\n${failed} ASSERTION GAGAL`);
    process.exitCode = failed === 0 ? 0 : 1;
})().catch((err) => {
    console.error('FATAL:', err.message);
    process.exitCode = 1;
});
