const { chromium } = require("playwright");
const path = require("path");
const { pathToFileURL } = require("url");

(async () => {
  const browser = await chromium.launch({
    headless: true
  });

  const page = await browser.newPage({
    viewport: {
      width: 1080,
      height: 1920
    }
  });

  const htmlPath = path.join(__dirname, "output.html");

  await page.goto(pathToFileURL(htmlPath).href, {
    waitUntil: "load"
  });

  // الانتظار حتى تحميل الخطوط العربية
  await page.evaluate(() => document.fonts.ready);

  await page.screenshot({
    path: "hadith.png",
    fullPage: false
  });

  await browser.close();

  console.log("تم إنشاء الصورة hadith.png");
})();
