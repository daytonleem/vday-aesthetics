const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const BASE = '/tmp/vday_carousel';
const ANIM_MS  = 3600;
const HOLD_MS  = 12000;
const DURATION = ANIM_MS + HOLD_MS;

const DECKS = [
  { dir: 'slides_v2_zh',    prefix: 'pricing_zh' },
  { dir: 'slides_myths_zh', prefix: 'myths_zh'   },
  { dir: 'slides_nsfue_zh', prefix: 'nsfue_zh'   },
];

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox','--disable-setuid-sandbox'],
  });

  for (const deck of DECKS) {
    const slideDir = path.join(BASE, deck.dir);
    const outDir   = path.join(BASE, 'mp4_zh', deck.prefix);
    fs.mkdirSync(outDir, { recursive: true });

    for (let i = 1; i <= 8; i++) {
      const tmpDir = path.join(BASE, `_tmp_${deck.prefix}_${i}`);
      fs.mkdirSync(tmpDir, { recursive: true });

      const ctx = await browser.newContext({
        viewport: { width: 1080, height: 1440 },
        recordVideo: { dir: tmpDir, size: { width: 1080, height: 1440 } },
      });
      const page = await ctx.newPage();
      const url  = `file://${path.join(slideDir, `slide${i}.html`)}`;
      await page.goto(url, { waitUntil: 'networkidle' });
      await page.waitForTimeout(DURATION);
      await ctx.close();

      const files = fs.readdirSync(tmpDir).filter(f => f.endsWith('.webm'));
      const webm  = path.join(tmpDir, files[0]);
      const mp4   = path.join(outDir, `slide${i}.mp4`);
      const { execSync } = require('child_process');
      execSync(`ffmpeg -y -i "${webm}" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -movflags +faststart "${mp4}"`, { stdio:'inherit' });
      fs.rmSync(tmpDir, { recursive: true });
      console.log(`done: ${deck.prefix}/slide${i}.mp4`);
    }
  }

  await browser.close();
  console.log('all 24 zh clips done');
})();
