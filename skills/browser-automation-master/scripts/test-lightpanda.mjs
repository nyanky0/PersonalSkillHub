import { chromium } from 'playwright';
import { spawn } from 'child_process';

async function testLightpandaCDP() {
  console.log('🚀 Menjalankan Lightpanda CDP Server di port 9222...');
  
  // Spawn lightpanda serve via WSL
  const server = spawn('wsl.exe', ['-d', 'Ubuntu', '--', 'bash', '-lic', '~/.local/bin/lightpanda serve --host 0.0.0.0 --port 9222']);
  
  server.stderr.on('data', (d) => process.stderr.write(`[Lightpanda] ${d}`));

  // Tunggu 1.5 detik agar socket siap
  await new Promise((r) => setTimeout(r, 1500));

  try {
    console.log('🔗 Menghubungkan Playwright ke Lightpanda via WebSocket CDP (ws://127.0.0.1:9222)...');
    const browser = await chromium.connectOverCDP('ws://127.0.0.1:9222');
    const context = await browser.newContext();
    const page = await context.newPage();

    console.log('🌐 Mengakses https://example.com...');
    await page.goto('https://example.com');
    const title = await page.title();
    console.log(`✅ Sukses via Lightpanda! Title: "${title}"`);

    await browser.close();
  } catch (err) {
    console.error('❌ Error saat koneksi:', err);
  } finally {
    console.log('🛑 Mematikan server Lightpanda...');
    server.kill();
  }
}

testLightpandaCDP();
