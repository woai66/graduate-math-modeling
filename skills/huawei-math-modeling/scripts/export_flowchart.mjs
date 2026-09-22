// 导出已校验的 Archify 页面，保留来源指纹，不修改图的内容或几何。
import { parseArgs } from 'node:util';
import { readFile, writeFile, mkdir, mkdtemp, copyFile, rm } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { join, resolve, dirname, basename } from 'node:path';
import { pathToFileURL } from 'node:url';
import { tmpdir } from 'node:os';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    'playwright-dir': { type: 'string' },
    browser: { type: 'string' },
    help: { type: 'boolean', short: 'h' },
  },
});
if (values.help || positionals.length !== 1 || !values['playwright-dir'] || !values.browser) {
  console.log('Usage: node export_flowchart.mjs diagram.html --playwright-dir <package-dir> --browser <chrome.exe>');
  process.exit(values.help ? 0 : 2);
}
const input = resolve(positionals[0]);
if (!input.toLowerCase().endsWith('.html')) throw new Error('输入必须是本地 Archify HTML。');
const stem = input.slice(0, -5);
const digest = (bytes) => createHash('sha256').update(bytes).digest('hex');
const readJson = async (file) => JSON.parse((await readFile(file, 'utf8')).replace(/^\uFEFF/, ''));
const delivery = await readJson(`${stem}.delivery.json`);
const htmlHash = digest(await readFile(input));
if (!delivery.ok || delivery.command !== 'deliver' || delivery.artifact?.sha256 !== htmlHash) {
  throw new Error('HTML 与有效 delivery 凭据不一致，拒绝导出过期或未校验页面。');
}
if (delivery.validation?.checksPassed !== 9 || delivery.validation?.errors !== 0 || delivery.validation?.warnings !== 0) {
  throw new Error('缺少 9/9、零错误、零警告的结构检查。');
}
const specificationPath = resolve(dirname(input), basename(delivery.input));
if (digest(await readFile(specificationPath)) !== delivery.specification?.sha256) {
  throw new Error('图规格已变化，请先重新校验和生成 HTML。');
}
const { chromium } = await import(pathToFileURL(join(resolve(values['playwright-dir']), 'index.mjs')).href);
const scratch = await mkdtemp(join(tmpdir(), 'math-flowchart-export-'));
let browser;
try {
  browser = await chromium.launch({ executablePath: resolve(values.browser), headless: true });
  const context = await browser.newContext({ acceptDownloads: true, colorScheme: 'light', viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.route(/^https?:\/\//, (route) => route.abort());
  await page.goto(pathToFileURL(input).href, { waitUntil: 'load' });
  await page.evaluate(async () => { await document.fonts.ready; });
  const downloaded = [];
  for (const format of ['svg', 'png']) {
    if (await page.locator('#btn-export').getAttribute('aria-expanded') !== 'true') {
      await page.locator('#btn-export').click();
    }
    const waiting = page.waitForEvent('download', { timeout: 30000 });
    await page.locator(`#export-menu button[data-format="${format}"]`).click();
    const download = await waiting;
    const failure = await download.failure();
    if (failure) throw new Error(`导出 ${format} 失败：${failure}`);
    const staged = join(scratch, `diagram.${format}`);
    await download.saveAs(staged);
    const data = await readFile(staged);
    if (data.length < 100) throw new Error(`导出 ${format} 为空或过短。`);
    const item = { format, file: `${basename(stem)}.${format}`, sha256: digest(data), bytes: data.length };
    if (format === 'png') {
      if (data.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw new Error('PNG 文件头无效。');
      item.width = data.readUInt32BE(16);
      item.height = data.readUInt32BE(20);
      item.maxWidthCmAt300Dpi = +(item.width / 300 * 2.54).toFixed(2);
    } else if (!data.toString('utf8').includes('<svg')) {
      throw new Error('SVG 输出内容无效。');
    }
    downloaded.push({ ...item, staged });
  }
  if (digest(await readFile(input)) !== htmlHash) throw new Error('导出期间 HTML 已变化，拒绝发布该导出。');
  await mkdir(dirname(input), { recursive: true });
  for (const item of downloaded) await copyFile(item.staged, join(dirname(input), item.file));
  const receipt = {
    schema_version: 1,
    status: 'exported_pending_visual_review',
    source_html: basename(input),
    source_html_sha256: htmlHash,
    specification_sha256: delivery.specification.sha256,
    theme: { png: 'light', svg: 'archify_dual_theme' },
    exports: downloaded.map(({ staged, ...item }) => item),
    limitations: ['导出不等于视觉验收。', 'SVG 随主题变化；正式 Word 插图使用已检查的浅色 PNG 或另行验证 SVG 兼容性。', '尚未验证目标 Word 版本与实际论文版面。'],
  };
  await writeFile(`${stem}.export.json`, JSON.stringify(receipt, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify(receipt, null, 2));
} finally {
  if (browser) await browser.close();
  // 仅清理 mkdtemp 在系统临时目录中创建的本次目录。
  if (dirname(resolve(scratch)) !== resolve(tmpdir()) || !basename(scratch).startsWith('math-flowchart-export-')) {
    throw new Error('临时目录边界校验失败，保留目录。');
  }
  await rm(scratch, { recursive: true, force: true });
}
