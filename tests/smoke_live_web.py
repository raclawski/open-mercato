"""Test wersji bez logowania na lokalnym serwerze PeerJS (3 oddzielne przeglądarki).
   npm install   (instaluje peer i peerjs)
   python3 tests/smoke_live_web.py   (najpierw python3 tools/build.py)"""
import asyncio, os, sys, subprocess, threading, http.server, functools, time
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, 'dist', 'live-web')
def prepare():
    d = open(os.path.join(WEB, 'index.html'), encoding='utf-8').read()
    d = d.replace('<script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>',
      '<script>window.PK_PEER_OPTS={host:"127.0.0.1",port:9000,path:"/pk",secure:false,config:{iceServers:[]}};</script>'
      '<script src="/peerjs.min.js"></script>')
    return d.replace('https://fonts.googleapis.com', 'http://127.0.0.1:1').encode()
def serve(page):
    lib = open(os.path.join(ROOT, 'node_modules', 'peerjs', 'dist', 'peerjs.min.js'), 'rb').read()
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body, ct = (lib, 'application/javascript') if self.path.startswith('/peerjs.min.js') else (page, 'text/html; charset=utf-8')
            self.send_response(200); self.send_header('Content-Type', ct); self.end_headers(); self.wfile.write(body)
        def log_message(self, *a): pass
    http.server.ThreadingHTTPServer(('127.0.0.1', 8766), H).serve_forever()
async def main():
    srv = subprocess.Popen(['node', '-e', "require('peer').PeerServer({port:9000,path:'/pk',host:'127.0.0.1'})"], cwd=ROOT)
    threading.Thread(target=serve, args=(prepare(),), daemon=True).start(); time.sleep(1.5)
    url = 'http://127.0.0.1:8766/'
    ok = False
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(); errs = []
            async def newpage():
                ctx = await b.new_context(viewport={'width': 390, 'height': 844}); pg = await ctx.new_page()
                pg.on('pageerror', lambda e: errs.append(str(e))); return pg
            host = await newpage(); await host.goto(url); await host.click('#btnBeHost')
            await host.wait_for_selector('#s-hsetup:not([hidden])', timeout=15000)
            code = (await host.inner_text('#hsCode')).strip()
            pl = []
            for n in ['Asia', 'Tomek']:
                pg = await newpage(); await pg.goto(url + '?kod=' + code); await pg.fill('#pname', n); await pg.click('#btnJoin')
                await pg.wait_for_selector('#s-player:not([hidden])', timeout=20000); pl.append(pg)
            await host.wait_for_timeout(800); await host.click('#modeSeg [data-v="offline"]'); await host.click('#btnHStart'); await host.wait_for_timeout(400)
            await host.click('[data-act="signal"]'); await host.wait_for_timeout(500)
            await pl[1].dispatch_event('#buzz', 'pointerdown'); await host.wait_for_timeout(600)
            who = await host.inner_text('#plateName')
            await host.click('[data-act="good"]'); await host.wait_for_timeout(600)
            seen = (await pl[0].inner_text('#pScores')).replace('\n', ', ')
            ok = who == 'Tomek' and 'Tomek 10' in seen and not errs
            print(('✓' if ok else '✗'), 'kod:', code, '| odpowiada:', who, '| gracz widzi:', seen, '| błędy:', errs)
            await b.close()
    finally:
        srv.terminate()
    sys.exit(0 if ok else 1)
asyncio.run(main())
