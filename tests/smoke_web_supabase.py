"""Test serwisu z dist/web (Vercel) z prawdziwym supabase-js na atrapie Supabase (tests/fake_supabase.py).

   PK_TEST_PGURL=postgresql://... python3 tests/smoke_web_supabase.py   (najpierw python3 tools/build.py)

PK_TEST_PGURL wskazuje serwer Postgres z prawami superużytkownika. Test zakłada na nim osobną,
tymczasową bazę, wgrywa migrację z supabase/migrations i na końcu ją usuwa.

Sprawdza: tworzenie gry i kod, dołączanie graczy (każdy w osobnej przeglądarce), zły kod, zajęty kod,
sygnał, falstart, kolejność wciśnięć, odbicie, odświeżenie strony prowadzącego, zerwanie połączenia,
zapis wyniku z kolejką ponowień, teleturniej z zapisem, lista wyników z filtrami i historią gracza."""
import asyncio, functools, glob, http.server, os, subprocess, sys, threading, urllib.parse, uuid
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fake_supabase import Realtime, Rest, config_js

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'dist', 'web')
PORT = 8767
BASE = f'http://127.0.0.1:{PORT}/'


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


def serve():
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=WEB)).serve_forever()


def with_db(url, db):
    u = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((u.scheme, u.netloc, '/' + db, u.query, u.fragment))


def psql(url, *args, stdin=None):
    r = subprocess.run(['psql', url, '-X', '-q', '-v', 'ON_ERROR_STOP=1', *args], input=stdin, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('psql: ' + r.stderr)
    return r.stdout


def setup_db(admin):
    db = 'pk_smoke_' + uuid.uuid4().hex[:8]
    psql(admin, '-c', f'create database {db}')
    url = with_db(admin, db)
    psql(url, '-c', "do $$ begin if not exists (select from pg_roles where rolname = 'anon') then create role anon nologin; end if;"
                    " if not exists (select from pg_roles where rolname = 'authenticated') then create role authenticated nologin; end if; end $$;")
    for f in sorted(glob.glob(os.path.join(ROOT, 'supabase', 'migrations', '*.sql'))):
        psql(url, '-f', f)
    return db, url


results = []
def check(ok, what, extra=''):
    results.append(bool(ok))
    print(('✓' if ok else '✗'), what, extra, flush=True)


async def main(dburl):
    rt, rest = Realtime(), Rest(dburl)
    errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch()

        async def ctx():
            c = await b.new_context(viewport={'width': 390, 'height': 844})
            await rt.install(c); await rest.install(c)
            await c.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=config_js()))
            await c.route(lambda u: 'fonts.g' in u, lambda r: r.abort())
            return c

        async def page(c, url):
            pg = await c.new_page()
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(BASE + url)
            return pg

        async def until(pg, js, arg=None, timeout=8000):
            await pg.wait_for_function(js, arg=arg, timeout=timeout)

        plate = lambda pg, name: until(pg, 'n => document.querySelector("#plateName").textContent === n', name)

        # --- prowadzący tworzy grę ---
        hc = await ctx()
        await hc.clock.install()  # czas płynie normalnie, ale test może go przewinąć (koniec czasu na odpowiedź)
        host = await page(hc, 'index.html')
        await host.click('a.mode[href^="live"]')
        await host.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        check('tryb=prowadzacy' in host.url, 'wybór trybu: przyciski na telefonach → ustawienia prowadzącego')
        await host.click('#levelSeg [data-v="pop"]'); await host.click('#countSeg [data-v="20"]'); await host.click('#timeSeg [data-v="5"]')
        await host.click('#modeSeg [data-v="offline"]')  # główny scenariusz: offline; online na końcu testu
        code = (await host.inner_text('#hsCode')).strip()
        check(len(code) == 4 and (await host.inner_text('#joinUrl')).endswith('?kod=' + code), 'gra utworzona, kod i link', code)

        # --- gracze dołączają z linku ---
        players = {}
        for n in ['Asia', 'Tomek']:
            if n == 'Asia':  # przez stronę startową: „Mam kod gry”
                pg = await page(await ctx(), 'index.html')
                await pg.click('a[href="live.html?tryb=gracz"]')
                await pg.wait_for_selector('#s-pjoin:not([hidden])')
                await pg.fill('#pcode', code.lower())
            else:  # z linku od prowadzącego
                pg = await page(await ctx(), 'live.html?kod=' + code)
            await pg.fill('#pname', n); await pg.click('#btnJoin')
            await pg.wait_for_selector('#s-player:not([hidden])', timeout=15000)
            players[n] = pg
        await until(host, '() => document.querySelectorAll("#hsRoster .sc").length === 2')
        check(not await host.is_disabled('#btnHStart'), 'prowadzący widzi 2 graczy', await host.inner_text('#hsRoster'))

        # --- zły kod ---
        bad = await page(await ctx(), 'live.html?kod=ZZZZ')
        await bad.fill('#pname', 'Obcy'); await bad.click('#btnJoin')
        await bad.wait_for_selector('#joinErr:not([hidden])', timeout=12000)
        check('Nie ma gry o kodzie ZZZZ' in await bad.inner_text('#joinErr'), 'zły kod: komunikat')

        # --- zajęty kod: drugi prowadzący z tym samym zapamiętanym kodem dostaje inny ---
        h2 = await page(await ctx(), 'index.html')
        await h2.evaluate('c => localStorage.setItem("pkw_hcode", JSON.stringify(c))', code)
        await h2.click('a.mode[href^="live"]')
        await h2.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        code2 = (await h2.inner_text('#hsCode')).strip()
        check(code2 != code and len(code2) == 4, 'zajęty kod: nowy kod dla drugiego prowadzącego', code2)
        await h2.close()

        # --- pytanie 1: sygnał, Tomek pierwszy, dobrze ---
        await host.click('#btnHStart')
        await host.wait_for_selector('#s-host:not([hidden])')
        await until(players['Asia'], '() => /Pytanie 1 z/.test(document.querySelector("#pQnum").textContent)')
        check(await players['Asia'].evaluate('() => document.querySelector("#pQ").hidden'), 'offline: przed wciśnięciem gracze nie widzą pytania')
        await host.click('[data-act="signal"]')
        await until(players['Tomek'], '() => document.querySelector("#buzz").classList.contains("armed")')
        await players['Tomek'].dispatch_event('#buzz', 'pointerdown')
        await plate(host, 'Tomek')
        await until(players['Asia'], '() => !document.querySelector("#pQ").hidden && !document.querySelector("#pOpts button")')
        await until(players['Tomek'], '() => document.querySelectorAll("#pOpts button[data-i]").length === 4')
        check(True, 'offline: po wciśnięciu wszyscy widzą pytanie, Tomek ma odpowiedzi do kliknięcia')
        # koniec czasu: nic się samo nie ocenia, prowadzący nadal przyznaje punkty
        await host.clock.fast_forward(6000)
        await until(host, '() => document.querySelector("#plateLbl").textContent.startsWith("Czas minął")')
        late_ok = await host.is_visible('[data-act="good"]') and await host.is_visible('[data-act="bad"]') and (await host.inner_text('#plateName')) == 'Tomek'
        check(late_ok, 'po końcu czasu prowadzący nadal może ocenić („Dobrze”, „Źle”)', await host.inner_text('#plateLbl'))
        right = await host.evaluate('() => H.deck[H.i].c')
        await players['Tomek'].click(f'#pOpts button[data-i="{right}"]')
        await until(host, '() => H.ph === "reveal"')
        await until(players['Asia'], '() => document.querySelector("#pScores").textContent.includes("Tomek 10")')
        check(True, 'pytanie 1: Tomek klika dobrą odpowiedź na telefonie (po czasie), gra sama daje +10')

        # --- pytanie 2: falstart Asi, Tomek źle, odbicie bez Asi, odkrycie ---
        await host.click('[data-act="next"]')
        await until(players['Asia'], '() => document.querySelector("#buzz").textContent.includes("sygnał")')
        await players['Asia'].dispatch_event('#buzz', 'pointerdown')
        await until(host, '() => document.querySelector("#hActions").textContent.includes("Falstart: Asia")')
        await until(players['Asia'], '() => document.querySelector("#buzz").classList.contains("blocked")')
        check(True, 'pytanie 2: falstart Asi i blokada')
        await host.click('[data-act="signal"]')
        await until(players['Tomek'], '() => document.querySelector("#buzz").classList.contains("armed")')
        await players['Asia'].dispatch_event('#buzz', 'pointerdown')
        await players['Tomek'].dispatch_event('#buzz', 'pointerdown')
        await plate(host, 'Tomek')
        await host.click('[data-act="bad"]')
        await until(host, '() => document.querySelector("#plateName").textContent === "Odbicie?"')
        await host.click('[data-act="reveal"]')
        await until(players['Asia'], '() => !document.querySelector("#pExplain").hidden')
        check(True, 'pytanie 2: zła odpowiedź, odkrycie widać u gracza')

        # --- pytanie 3: kolejność wciśnięć ---
        await host.click('[data-act="next"]')
        await host.click('[data-act="signal"]')
        await until(players['Tomek'], '() => document.querySelector("#buzz").classList.contains("armed")')
        # oba telefony wciskają w tej samej chwili; odpowiada ten, którego wciśnięcie pierwsze dotarło do prowadzącego
        await asyncio.gather(*(players[n].dispatch_event('#buzz', 'pointerdown') for n in ('Asia', 'Tomek')))
        await until(host, '() => document.querySelectorAll("#hOrder li").length === 2')
        order = (await host.inner_text('#hOrder')).split('\n')
        first = order[0].split('. ', 1)[1]
        check(await host.inner_text('#plateName') == first and '+' in order[1] and ' ms' in order[1], 'pytanie 3: kolejność wciśnięć, odpowiada pierwszy', ' | '.join(order))
        scores = {'Tomek': 10 - 1, 'Asia': 0}
        scores[first] += 10
        await host.click('[data-act="good"]')

        # --- prowadzący odświeża stronę w trakcie gry ---
        await host.reload()
        await host.wait_for_selector('#s-host:not([hidden])', timeout=15000)
        same = await host.evaluate('() => [...document.querySelectorAll(".gamecode")].every((e) => e.textContent === %s)' % repr(code))
        await host.click('[data-act="next"]')
        await until(players['Tomek'], '() => /Pytanie 4 z/.test(document.querySelector("#pQnum").textContent)')
        check(same, 'odświeżenie prowadzącego: ten sam kod, gra trwa dalej')
        start = await page(hc, 'index.html')
        await start.wait_for_selector('#resume:not([hidden])')
        check(code in await start.inner_text('#resume'), 'strona startowa w trakcie gry: „Wróć do gry”', await start.inner_text('#resume'))
        await start.close()

        # --- zerwane połączenie: klienci łączą się ponownie i gra działa ---
        n_before = len(rt.log)
        await rt.kill_socket()
        await host.wait_for_timeout(300)
        try:
            await until(host, '() => document.querySelector("#connH").classList.contains("on")', timeout=15000)
            await host.wait_for_timeout(1500)
            await host.click('[data-act="signal"]')
            await until(players['Tomek'], '() => document.querySelector("#buzz").classList.contains("armed")', timeout=15000)
        except Exception:
            print('DEBUG conn', await host.get_attribute('#connH', 'class'), await players['Tomek'].get_attribute('#connPJ', 'class'), 'sockets', len(rt.sockets))
            print('DEBUG log', rt.log[n_before:n_before + 40])
            raise
        await players['Tomek'].dispatch_event('#buzz', 'pointerdown')
        await plate(host, 'Tomek')
        await host.click('[data-act="good"]')
        check(True, 'po zerwaniu połączenia: sygnał i wciśnięcie działają')

        # --- koniec gry, pierwszy zapis się nie udaje (brak sieci) ---
        rest.fail_next = 1
        await host.click('#btnHEnd'); await host.click('#btnHEnd')
        await host.wait_for_selector('#s-final:not([hidden])')
        await until(host, '() => document.querySelector("#fRank").textContent.includes("Nie udało się")')
        await until(players['Asia'], '() => document.querySelector("#buzz").textContent.includes("Koniec")')
        scores['Tomek'] += 10
        board = (await host.inner_text('#fBoard')).replace('\n', ' ')
        check(all(f'{n}' in board and f'{v} pkt' in board for n, v in scores.items()), 'koniec gry: klasyfikacja u prowadzącego', board)

        # kolejka: wejście na listę wyników ponawia zapis
        res = await page(hc, 'wyniki.html')
        await res.wait_for_timeout(2500)
        await res.reload()
        await until(res, '() => document.querySelectorAll("#board li").length === 2')
        rows = (await res.inner_text('#board')).split('\n')
        leader = max(scores, key=scores.get)
        check(rows[0].startswith('1.') and leader in rows[1] and await res.evaluate('() => (JSON.parse(localStorage.getItem("pk_outbox") || "[]")).length') == 0,
              'zapis z kolejki po powrocie sieci, ranking zgodny z grą', ' | '.join(rows[:4]))

        # --- teleturniej na jednym telefonie ---
        tc = await ctx()
        bare = await page(tc, 'live.html')
        await bare.wait_for_url('**/index.html', timeout=5000)
        check(True, 'live.html bez trybu wraca do wyboru trybu')
        await bare.close()
        tv = await page(hc, 'index.html')  # przeglądarka prowadzącego: ustawienia z Live są w jej localStorage
        resume = await tv.is_visible('#resume')
        await tv.click('a.mode[href="teleturniej.html"]')
        await tv.wait_for_selector('#screen-start:not([hidden])')
        shared = await tv.evaluate('() => document.querySelector("#levelSeg [data-v=pop]").getAttribute("aria-pressed") === "true" && document.querySelector("#countSeg [data-v=\'20\']").getAttribute("aria-pressed") === "true"')
        check(shared and not resume, 'wybór trybu: jeden telefon, kategoria i liczba pytań przeniesione z Live')
        await tv.click('#btnStart')
        for i in range(20):
            await tv.click('#options .row >> nth=0')
            if await tv.is_disabled('#btnNext'): await tv.click('#nextChips [data-p="0"]')
            await tv.click('#btnNext')
        await tv.wait_for_selector('#screen-final:not([hidden])')
        await until(tv, '() => document.querySelector("#rankNote").textContent.includes("zapisany")')
        check(True, 'teleturniej: wynik zapisany', await tv.inner_text('#rankNote'))

        # --- lista wyników: filtry i historia gracza ---
        await res.reload()
        await until(res, '() => document.querySelectorAll("#board li").length === 5')
        await res.select_option('#modeSel', 'live')
        await until(res, '() => document.querySelectorAll("#board li").length === 2')
        await res.select_option('#modeSel', 'teleturniej')
        await until(res, '() => document.querySelectorAll("#board li").length === 5')
        await res.select_option('#modeSel', '')
        await until(res, '() => document.querySelectorAll("#games .game").length === 2')
        await res.click('#board [data-who="Asia"]')
        await until(res, '() => document.querySelector("#t-games").textContent === "Asia" && document.querySelectorAll("#games .game").length === 2')
        await res.click('#sortSeg [data-v="wins"]')
        check('gracz=Asia' in res.url, 'lista wyników: filtry trybu, historia gracza, sortowanie')

        home = await page(tc, 'index.html')
        await home.wait_for_selector('#topBox:not([hidden])', timeout=8000)
        check(await home.locator('#top li').count() == 5, 'strona główna: czołówka 30 dni')

        # --- wersja online: odliczanie, potem pytanie i przycisk naraz, odpowiedź klikana na telefonie ---
        oh = await page(await ctx(), 'index.html')
        await oh.click('a.mode[href^="live"]'); await oh.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        await oh.click('#modeSeg [data-v="online"]')
        ocode = (await oh.inner_text('#hsCode')).strip()
        op = {}
        for n in ['Ola', 'Kuba']:
            pg = await page(await ctx(), 'live.html?kod=' + ocode)
            await pg.fill('#pname', n); await pg.click('#btnJoin')
            await pg.wait_for_selector('#s-player:not([hidden])', timeout=15000); op[n] = pg
        await until(oh, '() => document.querySelectorAll("#hsRoster .sc").length === 2')
        await oh.click('#btnHStart'); await oh.wait_for_selector('#s-host:not([hidden])')
        await until(op['Ola'], '() => /Pytanie 1 z/.test(document.querySelector("#pQnum").textContent)')
        before = await op['Ola'].evaluate('() => document.querySelector("#pQ").hidden && document.querySelector("#buzz").disabled')
        await oh.click('[data-act="signal"]')
        await until(op['Ola'], '() => document.querySelector("#buzz").classList.contains("count")')
        cd = (await op['Ola'].inner_text('#buzz')).strip()
        cd_hidden = await op['Ola'].evaluate('() => document.querySelector("#pQ").hidden')
        await until(op['Ola'], '() => document.querySelector("#buzz").classList.contains("armed") && !document.querySelector("#pQ").hidden', timeout=8000)
        check(before and cd in ('3', '2', '1') and cd_hidden, 'online: przed startem i w odliczaniu pytanie ukryte, potem pytanie i przycisk naraz', cd)
        await op['Kuba'].dispatch_event('#buzz', 'pointerdown')
        await plate(oh, 'Kuba')
        oc = await oh.evaluate('() => H.deck[H.i].c')
        await until(op['Kuba'], '() => document.querySelectorAll("#pOpts button[data-i]").length === 4')
        await op['Kuba'].click(f'#pOpts button[data-i="{(oc + 1) % 4}"]')
        await until(oh, '() => H.ph === "q2"')
        await until(op['Ola'], '() => document.querySelector("#pScores").textContent.includes("Kuba −1")')
        await oh.click('[data-act="signal"]')
        await until(op['Ola'], '() => document.querySelector("#buzz").classList.contains("armed")', timeout=8000)
        await op['Ola'].dispatch_event('#buzz', 'pointerdown')
        await plate(oh, 'Ola')
        await until(op['Ola'], '() => document.querySelectorAll("#pOpts button[data-i]").length === 4')
        await op['Ola'].click(f'#pOpts button[data-i="{oc}"]')
        await until(oh, '() => H.ph === "reveal"')
        await until(op['Kuba'], '() => document.querySelector("#pScores").textContent.includes("Ola 10")')
        check(True, 'online: Kuba klika złą odpowiedź (−1), po odbiciu Ola klika dobrą (+10), gra sama liczy')

        check(not errs, 'brak błędów JS', errs[:3])
        await b.close()


if __name__ == '__main__':
    admin = os.environ.get('PK_TEST_PGURL')
    if not admin:
        sys.exit('Ustaw PK_TEST_PGURL (Postgres z prawami superużytkownika), np. postgresql://postgres@localhost:5432/postgres')
    threading.Thread(target=serve, daemon=True).start()
    db, url = setup_db(admin)
    try:
        asyncio.run(main(url))
    finally:
        psql(admin, '-c', f'drop database if exists {db} with (force)')
    print(f'{sum(results)}/{len(results)} OK')
    sys.exit(0 if results and all(results) else 1)
