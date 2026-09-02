const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

(async () => {
  const browser = await chromium.launch({ headless: true });

  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 }
  });

  const htmlPath = path.join(__dirname, "output.html");

  await page.goto(pathToFileURL(htmlPath).href, {
    waitUntil: "load"
  });

  await page.evaluate(() => document.fonts.ready);

  await page.screenshot({
    path: "hadith.jpg",
    type: "jpeg",
    quality: 95,
    fullPage: false
  });

  await browser.close();

  console.log("تم إنشاء الصورة hadith.jpg");
})();
