import { chromium } from 'playwright';

async function main() {
  console.log('🚀 Menjalankan Playwright Edge (msedge)...');
  const browser = await chromium.launch({
    channel: 'msedge',
    headless: true
  });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  const title = await page.title();
  const heading = await page.locator('h1').textContent();
  console.log(`✅ Sukses! Title: "${title}", Heading: "${heading.trim()}"`);
  await browser.close();
}

main().catch(err => {
  console.error('❌ Gagal:', err);
  process.exit(1);
});
