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
            await pg.click(f'#levelSeg [data-v="{lv}"]'); await pg.fill('#countRange', '20'); await pg.click('#btnStart')
            for i in range(20):
                await pg.click('#options .row >> nth=0')
                if await pg.is_disabled('#btnNext'): await pg.click('#nextChips [data-p="0"]')
                await pg.click('#btnNext')
            done = await pg.is_visible('#screen-final')
            print(('✓' if done and not errs else '✗'), lv, await pg.inner_text('#fCount'))
            fail += (not done) or bool(errs); errs.clear()
        # tryb mieszany: pełna mieszanka i wybrane dwie kategorie (po równo, na zmianę), wybór zapamiętany
        await pg.evaluate('localStorage.clear()'); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#catMode [data-v="mix"]'); await pg.fill('#countRange', '20'); await pg.click('#btnStart')
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
        # „1 kategoria” / „MIX”: MIX chowa bęben i pokazuje listę, „1 kategoria” wraca do ostatniej kategorii
        await pg.evaluate('localStorage.clear()'); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#levelSeg [data-v="geo"]'); await pg.click('#catMode [data-v="mix"]')
        m1 = [await pg.is_hidden('.drum-wrap'), await pg.is_visible('#mixPick'), await pg.evaluate('() => settings.level')]
        await pg.click('#catMode [data-v="one"]')
        try:
            await pg.wait_for_function('() => { const d = document.querySelector("#levelSeg"), b = d.querySelector("[data-v=geo]"), r = d.getBoundingClientRect(), q = b.getBoundingClientRect(); return Math.abs((q.top + q.bottom) / 2 - (r.top + r.bottom) / 2) < 6 && parseFloat(b.style.opacity) > 0.99; }', timeout=3000)
            centered = True
        except Exception:
            centered = await pg.evaluate('() => { const d = document.querySelector("#levelSeg"), b = d.querySelector("[data-v=geo]"), r = d.getBoundingClientRect(), q = b.getBoundingClientRect(); return [(q.top + q.bottom) / 2 - (r.top + r.bottom) / 2, b.style.opacity, d.scrollTop, d.clientHeight, scrollY]; }')
        m2 = [await pg.is_visible('.drum-wrap'), await pg.is_hidden('#mixPick'), await pg.evaluate('() => settings.level'), centered]
        good = m1 == [True, True, 'mix'] and m2 == [True, True, 'geo', True] and not errs
        print(('✓' if good else '✗'), '„1 kategoria” albo „MIX”, wybrana kategoria na środku koła', m1, m2, errs)
        fail += not good
        # stałe id pytań: id z treści, stara pamięć `kategoria:dział-nr` przepisana na nowe id
        await pg.evaluate('localStorage.clear()'); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.evaluate('() => localStorage.setItem("pk_seen", JSON.stringify(["std:0-0", "std:1-2"]))')
        await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#levelSeg [data-v="std"]'); await pg.fill('#countRange', '20'); await pg.click('#btnStart')
        r = await pg.evaluate("""() => { const seen = Object.keys(JSON.parse(localStorage.getItem("pk_seen_at"))), a = qid("std", LEVELS.std.bank[0].q[0]), b = qid("std", LEVELS.std.bank[1].q[2]);
          return [seen.includes(a) && seen.includes(b) && !seen.some((x) => /-/.test(x)), S.deck.every((q) => /^std:[0-9a-z]+$/.test(q.id)), seen.length >= 20]; }""")
        good = all(r) and not errs
        print(('✓' if good else '✗'), 'stałe id pytań i przepisanie starej pamięci', r, errs)
        fail += not good
        # dobór według wag: 41 z 61 pytań „std” widziane wczoraj, nowa gra na 20 bierze głównie niewidziane,
        # ale ograne nie są zablokowane (po wyczerpaniu puli gra dalej się układa)
        res = await pg.evaluate("""() => {
          const all = []; LEVELS.std.bank.forEach((c) => c.q.forEach((Q) => all.push(qid("std", Q))));
          const old = {}, t = Date.now() - 864e5; all.slice(0, 41).forEach((id) => (old[id] = t));
          const fresh = new Set(all.slice(41)), runs = [];
          for (let k = 0; k < 40; k++) { localStorage.setItem("pk_seen_at", JSON.stringify(old)); runs.push(buildDeck("std", 20).filter((q) => fresh.has(q.id)).length); }
          localStorage.setItem("pk_seen_at", JSON.stringify(Object.fromEntries(all.map((id) => [id, Date.now()]))));
          const full = buildDeck("std", 20);
          let same = 0; for (let i = 1; i < full.length; i++) if (full[i].cat === full[i - 1].cat) same++;
          return { avg: runs.reduce((a, b) => a + b, 0) / runs.length, min: Math.min(...runs), full: full.length, same, ids: new Set(full.map((q) => q.id)).size }; }""")
        good = res['avg'] >= 15 and res['min'] < 20 and res['full'] == 20 and res['ids'] == 20 and res['same'] <= 2 and not errs
        print(('✓' if good else '✗'), 'dobór według wag: niewidziane częściej, ograne nie zablokowane, działy rozłożone', res, errs)
        fail += not good
        # pytanie ×2: jedno na każde 10 pytań, baner, punkty i kara razy dwa
        await pg.evaluate('localStorage.clear()'); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#levelSeg [data-v="std"]'); await pg.fill('#countRange', '25'); await pg.click('#minusSeg [data-v="5"]'); await pg.click('#btnStart')
        x2 = await pg.evaluate('() => [0, 1, 2].map((k) => S.deck.slice(k * 10, k * 10 + 10).filter((q) => q.x2).length)')
        first = await pg.evaluate('() => S.deck.findIndex((q) => q.x2)')
        while await pg.evaluate('() => S.i') < first:
            await pg.click('#options .row >> nth=0')
            if await pg.is_disabled('#btnNext'): await pg.click('#nextChips [data-p="0"]')
            await pg.click('#btnNext')
        ban = [await pg.is_visible('#x2Q'), (await pg.inner_text('#stakePlus')).strip(), (await pg.inner_text('#stakeMinus')).strip()]
        before = await pg.evaluate('() => scores()[S.cur]')
        right = await pg.evaluate('() => S.deck[S.i].c')
        await pg.click(f'#options .row[data-i="{right}"]')
        gain = await pg.evaluate('(b) => scores()[S.log[S.i].p] - b', before)
        good = x2 == [1, 1, 1] and ban == [True, '+20', '−10'] and gain == 20 and not errs
        print(('✓' if good else '✗'), 'pytanie ×2: jedno na 10, baner, +20/−10', x2, ban, gain, errs)
        fail += not good
        # koniec czasu: odpowiedzi zostają do zaznaczenia, „Brak odpowiedzi” daje karę, nic nie dzieje się samo
        await pg.evaluate('localStorage.clear()'); await pg.clock.install(); await pg.goto(URL); await pg.wait_for_timeout(200)
        await pg.click('#timeSeg [data-v="10"]'); await pg.click('#minusSeg [data-v="5"]'); await pg.uncheck('#optX2'); await pg.click('#btnStart')
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
