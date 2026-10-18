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
        await host.click('[data-go="q2"]'); await host.click('a.ans[href="live.html?tryb=prowadzacy"]')
        await host.wait_for_selector('#s-role:not([hidden]) .rules')
        await host.wait_for_timeout(1500)
        stays = await host.evaluate('() => !document.querySelector("#s-role").hidden && document.querySelector("#s-hsetup").hidden && document.querySelector("#btnBePlayer").hidden')
        check(stays and (await host.inner_text('#btnBeHost')).strip() == 'Zaczynamy!', 'instrukcja zostaje, dopóki prowadzący nie kliknie „Zaczynamy!”')
        await host.click('#btnBeHost')
        await host.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        check('tryb=prowadzacy' in host.url, 'wybór trybu: przyciski na telefonach → ustawienia prowadzącego')
        await host.click('#levelSeg [data-v="pop"]'); await host.fill('#countRange', '20'); await host.click('#timeSeg [data-v="5"]')
        await host.click('#modeSeg [data-v="offline"]')  # główny scenariusz: offline; online na końcu testu
        code = (await host.inner_text('#hsCode')).strip()
        check(len(code) == 4 and (await host.inner_text('#joinUrl')).endswith('?kod=' + code), 'gra utworzona, kod i link', code)

        # --- gracze dołączają z linku ---
        players = {}
        for n in ['Asia', 'Tomek']:
            if n == 'Asia':  # przez stronę startową: „Mam kod gry”
                pg = await page(await ctx(), 'index.html')
                await pg.click('[data-go="q2"]'); await pg.click('a.ans[href="live.html?tryb=gracz"]')
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

        # --- lobby: każde odświeżenie daje nowy kod (zapamiętany kod nie wraca, gdy gra nie trwa) ---
        h2 = await page(await ctx(), 'index.html')
        await h2.evaluate('c => localStorage.setItem("pkw_hcode", JSON.stringify(c))', code)
        await h2.click('[data-go="q2"]'); await h2.click('a.ans[href="live.html?tryb=prowadzacy"]')
        await h2.click('#btnBeHost')
        await h2.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        codes = [(await h2.inner_text('#hsCode')).strip()]
        for _ in range(2):
            await h2.reload()
            await h2.click('#btnBeHost')
            await h2.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
            codes.append((await h2.inner_text('#hsCode')).strip())
        check(code not in codes and len(set(codes)) == 3 and all(len(c) == 4 for c in codes), 'lobby: nowy kod po każdym odświeżeniu', codes)
        await h2.close()

        # --- pytanie 1: sygnał, Tomek pierwszy, dobrze ---
        await host.uncheck('#optX2')
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
        await until(players['Asia'], '() => !document.querySelector("#s-final").hidden && document.querySelector("#fBoard").textContent.includes("Tomek")')
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
        await tv.click('[data-go="q2"]'); await tv.click('a.ans[href="teleturniej.html"]')
        await tv.wait_for_selector('#screen-start:not([hidden])')
        shared = await tv.evaluate('() => document.querySelector("#levelSeg [data-v=pop]").getAttribute("aria-pressed") === "true" && document.querySelector("#countRange").value === "20"')
        check(shared and not resume, 'wybór trybu: jeden telefon, kategoria i liczba pytań przeniesione z Live')
        orig = await tv.input_value('#players')
        await tv.fill('#players', 'Ola')
        await until(tv, '() => !document.querySelector("#nickChips").hidden && document.querySelector("#nickChips [data-n=Asia]")')
        await tv.click('#nickChips [data-n="Asia"]')
        chips_ok = await tv.input_value('#players') == 'Ola, Asia' and not await tv.locator('#nickChips [data-n="Asia"]').count()
        check(chips_ok and await tv.locator('#nickChips [data-n="Tomek"]').count() == 1, 'rejestr nicków: gracze z listy wyników jako podpowiedzi', await tv.input_value('#players'))
        await tv.fill('#players', orig)
        seen_rows = psql(dburl, '-Atc', "select count(*) from public.pk_seen_q where name_key = 'asia'").strip()
        await until(tv, '() => Object.keys(QHIST).length > 0')
        hq = await tv.evaluate('() => { const ids = Object.keys(QHIST); return [ids.length, ids.every((k) => /^[a-z]+:[0-9a-z]+$/.test(k)), Math.max(...Object.values(QHIST))]; }')
        check(int(seen_rows) > 0 and hq[1] and 0.9 <= hq[2] <= 2.01, 'dobór pytań: historia nicków zapisana w bazie i pobrana przed grą', f'{seen_rows} wierszy, {hq}')
        await tv.click('#btnStart')
        for i in range(20):
            await tv.click('#options .row >> nth=0')
            if await tv.is_disabled('#btnNext'): await tv.click('#nextChips [data-p="0"]')
            await tv.click('#btnNext')
        await tv.wait_for_selector('#screen-final:not([hidden])')
        await until(tv, '() => document.querySelector("#rankNote").textContent.includes("zapisany")')
        check(True, 'teleturniej: wynik zapisany', await tv.inner_text('#rankNote'))
        # --- gram sam: jeden gracz pod własnym nickiem, bez wskazywania następnego ---
        sp = await page(await ctx(), 'index.html')
        await sp.evaluate('() => localStorage.setItem("pkl_name", JSON.stringify("Solista"))')
        await sp.click('a.ans[href="teleturniej.html?tryb=sam"]')
        await sp.wait_for_selector('#screen-start:not([hidden])')
        solo = [await sp.input_value('#players'), await sp.is_hidden('#starterChips'), (await sp.inner_text('#lblPlayers')).strip()]
        await sp.fill('#countRange', '3'); await sp.uncheck('#optX2'); await sp.click('#btnStart')
        for i in range(3):
            await sp.click('#options .row >> nth=0')
            assert await sp.is_hidden('#nextpick') and not await sp.is_disabled('#btnNext')
            await sp.click('#btnNext')
        await sp.wait_for_selector('#screen-final:not([hidden])')
        await until(sp, '() => document.querySelector("#rankNote").textContent.includes("zapisany")')
        friends = await sp.evaluate('() => (JSON.parse(localStorage.getItem("pk_tv2")) || {}).players')
        check(solo == ['Solista', True, 'Twój nick'] and friends != ['Solista'], 'gram sam: jeden gracz, bez wskazywania następnego, wynik zapisany', solo)

        # --- lista wyników: filtry i historia gracza ---
        await res.reload()
        await until(res, '() => document.querySelectorAll("#board li").length === 6')
        await res.select_option('#modeSel', 'live')
        await until(res, '() => document.querySelectorAll("#board li").length === 2')
        await res.select_option('#modeSel', 'teleturniej')
        await until(res, '() => document.querySelectorAll("#board li").length === 6')
        await res.select_option('#modeSel', '')
        await until(res, '() => document.querySelectorAll("#games .game").length === 3')
        await res.click('#board [data-who="Asia"]')
        await until(res, '() => document.querySelector("#t-games").textContent === "Asia" && document.querySelectorAll("#games .game").length === 2')
        await res.click('#sortSeg [data-v="wins"]')
        check('gracz=Asia' in res.url, 'lista wyników: filtry trybu, historia gracza, sortowanie')

        home = await page(tc, 'index.html')
        await home.wait_for_selector('#topBox:not([hidden])', timeout=8000)
        check(await home.locator('#top li').count() == 5, 'strona główna: czołówka 30 dni')

        # --- wersja online: admin pokoju gra razem z innymi, gra prowadzi się sama ---
        octx = await ctx(); await octx.clock.install()
        oh = await page(octx, 'index.html')  # admin „Ola”
        oh.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await oh.click('[data-go="q2"]'); await oh.click('a.ans[href="live.html?tryb=prowadzacy"]'); await oh.click('#btnBeHost'); await oh.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        await oh.click('#modeSeg [data-v="online"]'); await oh.fill('#countRange', '20')
        await oh.fill('#adminName', 'Ola')
        ocode = (await oh.inner_text('#hsCode')).strip()
        op = {'Ola': oh}
        for n in ['Kuba', 'Ewa']:
            pg = await page(await ctx(), 'live.html?kod=' + ocode)
            await pg.fill('#pname', n); await pg.click('#btnJoin')
            await pg.wait_for_selector('#s-player:not([hidden])', timeout=15000); op[n] = pg
        await until(op['Kuba'], '() => ["Asia", "Tomek"].every((n) => [...document.querySelectorAll("#nickList option")].some((o) => o.value === n))')
        check(True, 'rejestr nicków: podpowiedzi przy imieniu gracza')
        await until(oh, '() => document.querySelectorAll("#hsRoster .sc").length === 3')
        check('3 graczy' in await oh.inner_text('#btnHStart'), 'online: admin Ola liczy się jako gracz', await oh.inner_text('#btnHStart'))
        await oh.uncheck('#optX2')
        await oh.click('#btnHStart')
        await oh.wait_for_selector('#s-player:not([hidden])')
        check(await oh.is_hidden('#s-host'), 'online: admin widzi ekran gracza, nie panel prowadzącego')
        # odliczanie rusza samo, u admina też
        await until(op['Kuba'], '() => document.querySelector("#buzz").classList.contains("count")')
        hidden_cd = await op['Kuba'].evaluate('() => document.querySelector("#pQ").hidden')
        await until(oh, '() => document.querySelector("#buzz").classList.contains("count")')
        await until(op['Kuba'], '() => document.querySelector("#buzz").classList.contains("armed") && !document.querySelector("#pQ").hidden', timeout=8000)
        await until(oh, '() => document.querySelector("#buzz").classList.contains("armed")', timeout=8000)
        below = await op['Kuba'].evaluate('() => document.querySelector("#pQ").getBoundingClientRect().top < document.querySelector("#buzz").getBoundingClientRect().top')
        no_key = await oh.evaluate('() => !document.querySelector("#pOpts .good") && P.host.rev === null && !("c" in (P.host.q || {}) && typeof P.host.q.c === "number")')
        check(hidden_cd and below and no_key, 'online: start sam, pytanie nad przyciskiem, admin nie zna odpowiedzi')
        oc = await oh.evaluate('() => H.deck[H.i].c')
        tA = await op['Kuba'].evaluate('() => [document.querySelector("#buzzWrap").classList.contains("timed"), parseInt(document.querySelector("#pTimerNum").textContent)]')
        check(tA[0] and 10 <= tA[1] <= 15, 'pasek czasu u gracza: czas na wciśnięcie', tA)
        # Kuba wciska pierwszy i klika złą odpowiedź → −1, odbicie rusza samo
        await op['Kuba'].dispatch_event('#buzz', 'pointerdown')
        await until(op['Kuba'], '() => document.querySelectorAll("#pOpts button[data-i]").length === 4')
        await until(op['Ewa'], '() => P.host && P.host.ph === "locked"')
        tL = await op['Ewa'].evaluate('() => [!document.querySelector("#pTimer").hidden && +document.querySelector("#ringFg").style.strokeDashoffset >= 0, parseInt(document.querySelector("#pTimerNum").textContent), P.host.tm && P.host.tm.T]')
        check(tL[0] and 1 <= tL[1] <= tL[2] / 1000, 'pasek czasu u gracza: czas na odpowiedź widzą też pozostali', tL)
        bg = [await op['Kuba'].evaluate('() => document.body.className'), await op['Ewa'].evaluate('() => document.body.className')]
        check('ans-me' in bg[0] and 'ans-other' in bg[1], 'kolor ekranu: zielony u odpowiadającego, szary u pozostałych', bg)
        await op['Kuba'].click(f'#pOpts button[data-i="{(oc + 1) % 4}"]')
        await until(op['Ewa'], '() => document.querySelector("#pScores").textContent.includes("Kuba −1")')
        seen = await op['Ewa'].evaluate('i => { const li = document.querySelectorAll("#pOpts li")[i]; return [li.className, li.textContent, document.body.className]; }', (oc + 1) % 4)
        check(seen[0] == 'bad' and 'Kuba ✗' in seen[1] and 'ans-' not in seen[2], 'pozostali widzą odpowiedź rywala', seen)
        await oh.clock.fast_forward(2500)
        await until(op['Ewa'], '() => document.querySelector("#buzz").classList.contains("count") || document.querySelector("#buzz").classList.contains("armed")', timeout=8000)
        await until(oh, '() => document.querySelector("#buzz").classList.contains("armed")', timeout=8000)
        # admin wciska na swoim telefonie i klika dobrą odpowiedź → +10, odkrycie, potem samo następne pytanie
        await oh.dispatch_event('#buzz', 'pointerdown')
        await until(oh, '() => document.querySelectorAll("#pOpts button[data-i]").length === 4')
        await oh.click(f'#pOpts button[data-i="{oc}"]')
        await until(op['Kuba'], '() => document.querySelector("#pScores").textContent.includes("Ola 10")')
        await until(op['Kuba'], '() => !document.querySelector("#pExplain").hidden')
        await oh.clock.fast_forward(7000)
        await until(op['Ewa'], '() => /Pytanie 2 z/.test(document.querySelector("#pQnum").textContent)', timeout=8000)
        check(True, 'online: Kuba −1, odbicie samo, admin Ola +10, odkrycie i samo pytanie 2')
        # nikt nie wciska → po czasie gra sama odkrywa odpowiedź i idzie dalej
        await until(oh, '() => H.ph === "armed"', timeout=8000)
        await oh.clock.fast_forward(16000)
        await until(oh, '() => H.ph === "reveal"', timeout=8000)
        await oh.clock.fast_forward(7000)
        await until(op['Kuba'], '() => /Pytanie 3 z/.test(document.querySelector("#pQnum").textContent)', timeout=8000)
        check(True, 'online: bez wciśnięcia gra sama odkrywa odpowiedź i przechodzi do pytania 3')
        # wszyscy klikają „Pomiń pytanie” → odkrycie od razu; „Następne pytanie” może kliknąć każdy
        await until(oh, '() => H.ph === "armed"', timeout=8000)
        for n in ['Ola', 'Kuba', 'Ewa']:
            await until(op[n], '() => !document.querySelector("#pSkip").hidden')
            await op[n].click('#pSkip')
        await until(op['Kuba'], '() => P.host && P.host.ph === "reveal" && document.querySelector("#pStatus").textContent === "Nikt nie wziął pytania."', timeout=5000)
        await until(op['Ewa'], '() => !document.querySelector("#pNext").hidden')
        vis = await op['Ewa'].evaluate('() => { const r = document.querySelector("#pNext").getBoundingClientRect(); return r.bottom <= innerHeight && r.top >= 0; }')
        check(vis, '„Następne pytanie” widoczne bez przewijania')
        await op['Ewa'].click('#pNext')
        await until(op['Kuba'], '() => /Pytanie 4 z/.test(document.querySelector("#pQnum").textContent)', timeout=5000)
        check(True, 'pytanie pominięte przez wszystkich: odkrycie od razu, „Następne pytanie” od gracza')
        # admin kończy grę → tabela wyników u wszystkich, wynik na liście
        await oh.click('#btnLeave')
        await oh.wait_for_selector('#s-final:not([hidden])')
        await until(op['Kuba'], '() => !document.querySelector("#s-final").hidden', timeout=8000)
        kb = (await op['Kuba'].inner_text('#fBoard')).replace('\n', ' ')
        await until(oh, '() => document.querySelector("#fRank").textContent.includes("zapisany")')
        check('Ola' in kb and '10 pkt' in kb and 'Kuba' in kb and '−1 pkt' in kb and 'Ewa' in kb, 'online: tabela wyników u gracza, gra zapisana na liście', kb)

        # --- „Kto pierwszy, ten lepszy”: wszyscy odpowiadają naraz, punkty za kolejność dobrych odpowiedzi ---
        rctx = await ctx()
        rh = await page(rctx, 'index.html')  # admin „Zosia”
        rh.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
        await rh.click('[data-go="q2"]'); await rh.click('a.ans[href="live.html?tryb=prowadzacy"]'); await rh.click('#btnBeHost'); await rh.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
        await rh.click('#modeSeg [data-v="race"]'); await rh.fill('#countRange', '5'); await rh.uncheck('#optX2')
        await rh.fill('#adminName', 'Zosia')
        rcode = (await rh.inner_text('#hsCode')).strip()
        rp = {'Zosia': rh}
        for n in ['Jan', 'Iga']:
            pg = await page(await ctx(), 'live.html?kod=' + rcode)
            await pg.fill('#pname', n); await pg.click('#btnJoin')
            await pg.wait_for_selector('#s-player:not([hidden])', timeout=15000); rp[n] = pg
        await until(rh, '() => document.querySelectorAll("#hsRoster .sc").length === 3')
        await rh.click('#btnHStart')
        await until(rp['Jan'], '() => P.host && P.host.ph === "race" && document.querySelectorAll("#pOpts button[data-i]").length === 4', timeout=8000)
        rc = await rh.evaluate('() => H.deck[H.i].c')
        await until(rh, '() => document.querySelectorAll("#pOpts button[data-i]").length === 4')
        await rp['Jan'].click(f'#pOpts button[data-i="{rc}"]'); await rp['Jan'].wait_for_timeout(250)
        await rh.click(f'#pOpts button[data-i="{rc}"]'); await rh.wait_for_timeout(250)
        mid = await rp['Iga'].evaluate('() => [P.host.ph, P.host.ra, document.querySelectorAll("#pOpts li.good, #pOpts li.bad").length]')
        await rp['Iga'].click(f'#pOpts button[data-i="{(rc + 1) % 4}"]')
        await until(rp['Iga'], '() => P.host && P.host.ph === "reveal"', timeout=5000)
        st = await rp['Iga'].inner_text('#pStatus')
        mine = [await rp[n].evaluate('() => document.querySelector("#buzz").textContent') for n in ('Jan', 'Zosia', 'Iga')]
        check(mid == ['race', 2, 0] and st.startswith('1. Jan +10 · 2. Zosia +8') and mine[0].startswith('+10') and mine[1].startswith('+8') and mine[2].startswith('0 pkt'),
              'kto pierwszy: wszyscy odpowiadają naraz, 10 i 8 pkt za kolejność, zła 0', f'{mid} | {st} | {mine}')
        await rh.click('#btnLeave')
        await until(rp['Jan'], '() => !document.querySelector("#s-final").hidden', timeout=8000)
        await until(rh, '() => document.querySelector("#fRank").textContent.includes("zapisany")')
        sc = psql(dburl, '-Atc', "select string_agg(name || '=' || score, ',' order by score desc) from public.pk_game_players p join public.pk_games g on g.id = p.game_id where g.code = '" + rcode + "'").strip()
        check(sc == 'Jan=10,Zosia=8,Iga=0', 'kto pierwszy: wynik na liście wyników', sc)

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
