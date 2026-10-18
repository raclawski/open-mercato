"""Rozgrywa każdy poziom teleturnieju do końca i zgłasza błędy JS.
   python3 tests/smoke_teleturniej.py   (najpierw python3 tools/build.py)"""
import asyncio, os, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = 'file://' + os.path.join(ROOT, 'dist', 'teleturniej-standalone.html')
async def main():
    fail = 0
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 390, 'height': 844})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(300)
        levels = await pg.eval_on_selector_all('#levelSeg button', 'bs => bs.map(b => b.dataset.v)')
        for lv in levels:
            await pg.evaluate('localStorage.clear()'); await pg.goto(URL); await pg.wait_for_timeout(200)
            await pg.click(f'#levelSeg [data-v="{lv}"]'); await pg.click('#countSeg [data-v="20"]'); await pg.click('#btnStart')
            for i in range(20):
                await pg.click('#options .row >> nth=0')
                if await pg.is_disabled('#btnNext'): await pg.click('#nextChips [data-p="0"]')
                await pg.click('#btnNext')
            done = await pg.is_visible('#screen-final')
            print(('✓' if done and not errs else '✗'), lv, await pg.inner_text('#fCount'))
            fail += (not done) or bool(errs); errs.clear()
        await b.close()
    sys.exit(1 if fail else 0)
asyncio.run(main())
