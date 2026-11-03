// Interim (Mihono) scan test runner. Runs build/interim_scan.js from umalyfe-engine inside a headless browser on the GitHub runner.
// Prints counts and timing only. Saves the piece file(s) into ./out (uploaded as a build artifact by the workflow). Stores nothing in any repo.
// Env: START (course index), COURSES (how many), FULL ('true' = 5 styles x 4 grounds, else 1 x 1 smoke test), LIMIT_MIN (give up after N minutes), ROUND.
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const E = process.env, START = +(E.START || 7), COURSES = +(E.COURSES || 1), FULL = E.FULL === 'true', LIMIT = +(E.LIMIT_MIN || 40), ROUND = +(E.ROUND || 1);
const src0 = fs.readFileSync(path.join(__dirname, '..', 'engine', 'build', 'interim_scan.js'), 'utf8');
const cfg = `var CFG = {ROUND: ${ROUND}, START: ${START}, INTERVAL_MIN: 56, STYLES: ${FULL ? '[0, 1, 2, 3, 4]' : '[0]'}, GROUNDS: ${FULL ? '[0, 1, 2, 3]' : '[0]'}, MAX_COURSES: ${COURSES}, NOSAVE: true};`;
const src = src0.replace(/var CFG = \{[^;]*\};/, cfg);
if (src === src0) throw new Error('CFG line not found in interim_scan.js');
const sl = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const t0 = Date.now(), mins = () => ((Date.now() - t0) / 60000).toFixed(1);
  const br = await chromium.launch({ headless: true });
  const ctx = await br.newContext({ viewport: { width: 1400, height: 1000 }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' });
  const page = await ctx.newPage();
  const resp = await page.goto('https://mihonostudios.com/tools/skill-recommender', { waitUntil: 'networkidle', timeout: 120000 });
  console.log('page status', resp && resp.status(), 'after', mins(), 'min');
  await page.waitForSelector('#rcd-v-2-track', { timeout: 60000 });
  console.log('page ready; hidden =', await page.evaluate(() => document.hidden));
  await page.evaluate(src);
  let last = '';
  while (true) {
    await sl(20000);
    const s = await page.evaluate(() => window.I && window.I.s());
    const line = JSON.stringify(s);
    if (line !== last) { console.log(mins() + ' min', line); last = line; }
    if (!s || s[0] === 'stopped' || s[0] === 'error') break;
    if ((Date.now() - t0) / 60000 > LIMIT) { console.log('LIMIT reached, stopping'); await page.evaluate(() => { window.I.stop = true; }); await sl(60000); break; }
  }
  const s = await page.evaluate(() => window.I && window.I.s());
  const names = await page.evaluate(() => Object.keys(window.I.blobs));
  fs.mkdirSync('out', { recursive: true });
  for (const n of names) {
    const b64 = await page.evaluate(n => new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(window.I.blobs[n]); }), n);
    fs.writeFileSync(path.join('out', n), Buffer.from(b64, 'base64')); console.log('saved piece', n, fs.statSync(path.join('out', n)).size, 'bytes');
  }
  const scans = s ? +String(s[3]).replace('scans ', '') : 0, bad = s ? +String(s[5]).replace('bad ', '') : 0;
  const sum = `interim test: ${scans} scans, ${bad} bad, ${mins()} min total, ${scans ? ((Date.now() - t0) / 60000 / scans).toFixed(2) : '-'} min per scan, final state ${JSON.stringify(s)}`;
  console.log(sum); console.log('::notice title=interim_scan_test::' + sum);
  await br.close();
  process.exit(names.length ? 0 : 1);
})().catch(e => { console.log('FAILED', e.message); process.exit(1); });
