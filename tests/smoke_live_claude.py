"""Symuluje prowadzącego i 3 graczy w wersji Live dla Claude (atrapa room z tests/mock_room.js).
   python3 tests/smoke_live_claude.py   (najpierw python3 tools/build.py)"""
import asyncio, os, sys, threading, http.server, functools
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765
def serve():
    # Artefakt nie ma <!doctype>; owijamy go jak Claude, w locie.
    class H(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            body = open(os.path.join(ROOT, 'dist', 'live-claude.html'), encoding='utf-8').read()
            html = ('<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">'
                    '<style>[hidden]{display:none!important}body{margin:0}</style></head><body>' + body + '</body></html>').encode()
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.end_headers(); self.wfile.write(html)
        def log_message(self, *a): pass
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
async def main():
    threading.Thread(target=serve, daemon=True).start()
    url = f'http://127.0.0.1:{PORT}/'
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script(path=os.path.join(ROOT, 'tests', 'mock_room.js'))
        errs = []
        host = await ctx.new_page(); host.on('pageerror', lambda e: errs.append(str(e)))
        await host.goto(url); await host.click('#btnBeHost'); await host.wait_for_timeout(200)
        pl = []
        for n in ['Asia', 'Tomek', 'Zając']:
            pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(url); await pg.click('#btnBePlayer'); await pg.fill('#pname', n); await pg.click('#btnJoin'); await pg.wait_for_timeout(150)
            pl.append(pg)
        await host.wait_for_timeout(300); await host.click('#btnHStart'); await host.wait_for_timeout(200)
        await pl[2].dispatch_event('#buzz', 'pointerdown'); await host.wait_for_timeout(200)   # falstart
        await host.click('[data-act="signal"]'); await host.wait_for_timeout(200)
        await pl[1].dispatch_event('#buzz', 'pointerdown'); await host.wait_for_timeout(300)
        first = await host.inner_text('#plateName')
        await host.click('[data-act="bad"]'); await host.wait_for_timeout(150)
        await host.click('[data-act="signal"]'); await host.wait_for_timeout(150)
        await pl[0].dispatch_event('#buzz', 'pointerdown'); await host.wait_for_timeout(300)
        await host.click('[data-act="good"]'); await host.wait_for_timeout(300)
        roster = (await host.inner_text('#hRoster')).replace('\n', ', ')
        ok = first == 'Tomek' and 'Asia 10' in roster and 'Tomek −1' in roster and not errs
        print(('✓' if ok else '✗'), 'pierwszy wcisnął:', first, '| punkty:', roster, '| błędy:', errs)
        await b.close()
    sys.exit(0 if ok else 1)
asyncio.run(main())
