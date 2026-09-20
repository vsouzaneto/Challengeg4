import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCREENSHOT_DIR = path.join(__dirname, '../e2e-screenshots');

const BASE_URL = 'http://localhost:5175';

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    deviceScaleFactor: 2,
  });

  async function takeScreenshot(page, viewport, name) {
    await page.setViewportSize(viewport);
    await page.goto(BASE_URL);
    // Wait for table to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 });
    await page.waitForTimeout(500);
    // Click first "View" button to open modal
    const viewBtn = page.locator('table tbody tr').first().locator('button:has-text("View")');
    await viewBtn.click();
    await page.waitForTimeout(800); // Wait for modal animation + data load
    await page.screenshot({
      path: path.join(SCREENSHOT_DIR, `modal-${name}.png`),
      fullPage: false,
    });
    // Close modal
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
  }

  // Test 1: Desktop layout 1440x900
  const page1 = await context.newPage();
  await takeScreenshot(page1, { width: 1440, height: 900 }, 'desktop');

  // Test 2: Laptop 1280x800
  const page2 = await context.newPage();
  await takeScreenshot(page2, { width: 1280, height: 800 }, 'laptop');

  // Test 3: Tablet 768x1024
  const page3 = await context.newPage();
  await takeScreenshot(page3, { width: 768, height: 1024 }, 'tablet');

  // Test 4: Mobile 375x667 (to check text leakage)
  const page4 = await context.newPage();
  await takeScreenshot(page4, { width: 375, height: 667 }, 'mobile');

  // Test 5: Short viewport 1280x600 (to check scroll + sticky header overlap)
  const page5 = await context.newPage();
  await takeScreenshot(page5, { width: 1280, height: 600 }, 'short-viewport');

  // Test 6: Long account/product name scenario - force a narrow viewport
  const page6 = await context.newPage();
  await page6.setViewportSize({ width: 1024, height: 768 });
  await page6.goto(BASE_URL);
  await page6.waitForSelector('table tbody tr', { timeout: 10000 });
  await page6.waitForTimeout(500);
  const viewBtn6 = page6.locator('table tbody tr').first().locator('button:has-text("View")');
  await viewBtn6.click();
  await page6.waitForTimeout(800);

  // Check for overflowing text
  const overflowIssues = await page6.evaluate(() => {
    const issues = [];
    const els = document.querySelectorAll('[class*="rounded"], [class*="p-"]');
    els.forEach((el, i) => {
      const { scrollWidth, clientWidth, scrollHeight, clientHeight } = el;
      if (scrollWidth > clientWidth + 2 || scrollHeight > clientHeight + 2) {
        const rect = el.getBoundingClientRect();
        const tag = el.tagName.toLowerCase();
        const text = (el.textContent || '').trim().substring(0, 60);
        issues.push({
          index: i,
          tag,
          class: el.className.substring(0, 80),
          text,
          overflowX: scrollWidth - clientWidth,
          overflowY: scrollHeight - clientHeight,
          rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
        });
      }
    });
    return issues;
  });

  console.log('\n=== OVERFLOW ISSUES ===');
  if (overflowIssues.length === 0) {
    console.log('No overflow issues detected in modal.');
  } else {
    overflowIssues.forEach(issue => {
      console.log(`[${issue.tag}] overflowX=${issue.overflowX}px overflowY=${issue.overflowY}px at (${issue.rect.x},${issue.rect.y})`);
      console.log(`  class: ${issue.class}`);
      console.log(`  text: "${issue.text}"`);
    });
  }

  // Check for overlapping elements
  const overlapIssues = await page6.evaluate(() => {
    const issues = [];
    const modal = document.querySelector('[role="dialog"]');
    if (!modal) return [];
    const children = modal.querySelectorAll('*');
    const rects = [];
    children.forEach((el, i) => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        rects.push({ el, rect, index: i });
      }
    });
    // Check the sticky header
    const header = modal.querySelector('[class*="sticky"]');
    if (header) {
      const headerRect = header.getBoundingClientRect();
      // Check elements below header that might be hidden
      children.forEach((el, i) => {
        const r = el.getBoundingClientRect();
        if (r.top > 0 && r.top < headerRect.bottom && r.bottom > headerRect.bottom) {
          if (el !== header && !header.contains(el)) {
            issues.push({
              index: i,
              tag: el.tagName.toLowerCase(),
              text: (el.textContent || '').trim().substring(0, 60),
              hiddenBy: 'sticky-header',
              overlap: Math.round(headerRect.bottom - r.top),
            });
          }
        }
      });
    }
    return issues;
  });

  console.log('\n=== STICKY HEADER OVERLAP ISSUES ===');
  if (overlapIssues.length === 0) {
    console.log('No sticky header overlap issues detected.');
  } else {
    overlapIssues.forEach(issue => {
      console.log(`[${issue.tag}] hidden by sticky header by ${issue.overlap}px: "${issue.text}"`);
    });
  }

  await browser.close();
  console.log('\nScreenshots saved to', SCREENSHOT_DIR);
}

run().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
