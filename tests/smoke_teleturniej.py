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
        # tryb mieszany: pełna mieszanka i wybrane dwie kategorie (po równo, na zmianę), wybór zapamiętany
        await pg.evaluate('localStorage.clear()'); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#levelSeg [data-v="mix"]'); await pg.click('#countSeg [data-v="20"]'); await pg.click('#btnStart')
        full = await pg.evaluate('() => new Set(S.deck.map((q) => q.cat)).size')
        await pg.goto(URL); await pg.wait_for_timeout(300)
        chips_visible = await pg.is_visible('#mixPick')
        for k in await pg.eval_on_selector_all('#mixPick [data-k]', 'bs => bs.map((b) => b.dataset.k)'):
            if k not in ('std', 'ts'): await pg.click(f'#mixPick [data-k="{k}"]')
        await pg.goto(URL); await pg.wait_for_timeout(300)
        kept = await pg.evaluate('() => [...document.querySelectorAll("#mixPick [aria-pressed=true]")].map((b) => b.dataset.k).join(",")')
        await pg.click('#btnStart')
        cats = await pg.evaluate('() => S.deck.map((q) => q.cat)')
        two = sorted(set(cats)) == ['Taylor Swift', 'Umiarkowany'] and cats.count('Umiarkowany') == 10 and len(cats) == 20
        mixed = sum(1 for a, b in zip(cats, cats[1:]) if a != b) >= 6
        good = chips_visible and full >= 6 and kept == 'std,ts' and two and mixed and not errs
        print(('✓' if good else '✗'), 'mieszane: pełna mieszanka', full, 'kategorii | wybrane:', kept, '| podział:', {c: cats.count(c) for c in set(cats)}, '| zmian kategorii:', sum(1 for a, b in zip(cats, cats[1:]) if a != b), errs)
        fail += not good
        # koniec czasu: odpowiedzi zostają do zaznaczenia, „Brak odpowiedzi” daje karę, nic nie dzieje się samo
        await pg.evaluate('localStorage.clear()'); await pg.clock.install(); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#timeSeg [data-v="10"]'); await pg.click('#minusSeg [data-v="5"]'); await pg.click('#btnStart')
        await pg.clock.fast_forward(11000); await pg.wait_for_timeout(200)
        late = await pg.is_visible('#late') and not await pg.is_visible('#feedback')
        right = await pg.evaluate('() => S.deck[S.i].c')
        await pg.click(f'#options .row[data-i="{right}"]')
        ok1 = await pg.evaluate('() => S.log[0] && S.log[0].ok === true') and not await pg.is_visible('#late')
        if await pg.is_disabled('#btnNext'): await pg.click('#nextChips [data-p="0"]')
        await pg.click('#btnNext')
        await pg.clock.fast_forward(11000); await pg.wait_for_timeout(200)
        await pg.click('#btnNoAnswer')
        ok2 = await pg.evaluate('() => S.log[1] && S.log[1].ok === false && S.log[1].pick === -1 && scores().reduce((a, b) => a + b, 0) === 10 - 5')
        good = late and ok1 and ok2 and not errs
        print(('✓' if good else '✗'), 'koniec czasu: dobra odpowiedź po czasie +10, „Brak odpowiedzi” −5', late, ok1, ok2, errs)
        fail += not good
        await b.close()
    sys.exit(1 if fail else 0)
asyncio.run(main())
