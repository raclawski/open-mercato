"""Atrapa Supabase dla testów w Playwright, z prawdziwym supabase-js po stronie strony.

- Realtime: przechwycony WebSocket (`context.route_web_socket`) i serwer protokołu Phoenix w Pythonie:
  phx_join / phx_leave / heartbeat, presence (track, untrack, presence_state, presence_diff)
  i broadcast (binarny push z klienta, vsn 2.0.0; do odbiorców idzie jako JSON).
- RPC (`/rest/v1/rpc/<funkcja>`): wywołanie funkcji w prawdziwym Postgresie przez psql, jako rola anon,
  z odpowiedzią i błędami w formacie PostgREST.
"""
import asyncio, itertools, json, re, uuid
from playwright._impl import _network

# Playwright 1.56: zamknięcie WebSocketu bez kodu wywala KeyError w obsłudze on_close i psuje kolejne połączenia.
_close_page = _network.WebSocketRoute._channel_close_page
def _safe_close_page(self, event):
    return _close_page(self, dict({'code': None, 'reason': ''}, **event))
_network.WebSocketRoute._channel_close_page = _safe_close_page

SUPA_URL = 'http://supa.test'
ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiJ9.test'


class Realtime:
    def __init__(self):
        self.members = {}       # topic -> {cid: {'ws', 'join_ref', 'key', 'self', 'meta', 'ref'}}
        self.ids = itertools.count(1)
        self.refs = itertools.count(1)
        self.sockets = {}       # cid -> ws
        self.log = []           # (topic, event) do diagnostyki

    async def install(self, context):
        await context.route_web_socket(re.compile(r'.*/realtime/v1/websocket.*'), self.handler)

    def handler(self, ws):
        cid = next(self.ids)
        self.sockets[cid] = ws
        ws.on_message(lambda m: self.on_message(cid, ws, m))
        ws.on_close(lambda *a: self.drop(cid))

    # --- wysyłanie ---
    def push(self, ws, msg):
        try:
            ws.send(json.dumps(msg))
        except Exception:
            pass

    def reply(self, ws, join_ref, ref, topic, response=None):
        self.push(ws, [join_ref, ref, topic, 'phx_reply', {'status': 'ok', 'response': response or {}}])

    def metas(self, m):
        return {'metas': [dict(m['meta'], phx_ref=m['ref'])]}

    def diff(self, topic, joins, leaves):
        for m in list(self.members.get(topic, {}).values()):
            self.push(m['ws'], [m['join_ref'], None, topic, 'presence_diff', {'joins': joins, 'leaves': leaves}])

    # --- odbiór ---
    def on_message(self, cid, ws, raw):
        if isinstance(raw, (bytes, bytearray)):
            self.on_binary(cid, bytes(raw))
            return
        join_ref, ref, topic, event, payload = json.loads(raw)
        self.log.append((topic, event))
        if topic == 'phoenix':
            self.reply(ws, None, ref, 'phoenix')
            return
        room = self.members.setdefault(topic, {})
        if event == 'phx_join':
            cfg = (payload or {}).get('config') or {}
            key = ((cfg.get('presence') or {}).get('key')) or str(uuid.uuid4())
            old = room.get(cid)
            if old and old['meta'] is not None:
                self.diff(topic, {}, {old['key']: self.metas(old)})
            room[cid] = {'ws': ws, 'join_ref': join_ref, 'key': key, 'self': bool((cfg.get('broadcast') or {}).get('self')), 'meta': None, 'ref': None}
            self.reply(ws, join_ref, ref, topic)
            state = {}
            for m in room.values():
                if m['meta'] is not None:
                    state.setdefault(m['key'], {'metas': []})['metas'].append(dict(m['meta'], phx_ref=m['ref']))
            self.push(ws, [join_ref, None, topic, 'presence_state', state])
        elif event == 'phx_leave':
            self.reply(ws, join_ref, ref, topic)
            self.leave(topic, cid)
        elif event == 'presence':
            self.reply(ws, join_ref, ref, topic)
            m = room.get(cid)
            if not m:
                return
            kind = (payload or {}).get('event')
            if kind == 'track':
                leaves = {m['key']: self.metas(m)} if m['meta'] is not None else {}
                m['meta'] = (payload or {}).get('payload') or {}
                m['ref'] = 'r%d' % next(self.refs)
                self.diff(topic, {m['key']: self.metas(m)}, leaves)
            elif kind == 'untrack' and m['meta'] is not None:
                leaves = {m['key']: self.metas(m)}
                m['meta'] = None
                self.diff(topic, {}, leaves)
        elif event == 'broadcast':
            self.reply(ws, join_ref, ref, topic)
            self.fanout(cid, topic, payload.get('event'), payload.get('payload'))
        else:
            self.reply(ws, join_ref, ref, topic)

    def on_binary(self, cid, b):
        # userBroadcastPush: kind, len(join_ref), len(ref), len(topic), len(event), len(meta), encoding, potem pola
        kind, jl, rl, tl, el, ml, enc = b[:7]
        assert kind == 3, kind
        o = 7
        join_ref = b[o:o + jl].decode(); o += jl
        ref = b[o:o + rl].decode(); o += rl
        topic = b[o:o + tl].decode(); o += tl
        event = b[o:o + el].decode(); o += el
        o += ml
        body = b[o:]
        payload = json.loads(body.decode()) if enc == 1 else None
        self.log.append((topic, 'broadcast:' + event))
        m = self.members.get(topic, {}).get(cid)
        if m and ref:
            self.reply(m['ws'], join_ref or None, ref, topic)
        self.fanout(cid, topic, event, payload)

    def fanout(self, cid, topic, event, payload):
        for other, m in list(self.members.get(topic, {}).items()):
            if other == cid and not m['self']:
                continue
            self.push(m['ws'], [None, None, topic, 'broadcast', {'type': 'broadcast', 'event': event, 'payload': payload}])

    def leave(self, topic, cid):
        m = self.members.get(topic, {}).pop(cid, None)
        if m and m['meta'] is not None:
            self.diff(topic, {}, {m['key']: self.metas(m)})

    def drop(self, cid):
        self.sockets.pop(cid, None)
        for topic in list(self.members):
            self.leave(topic, cid)

    async def kill_socket(self, page_filter=None):
        """Zrywa wszystkie połączenia (symulacja utraty sieci); klient sam się połączy ponownie."""
        for cid, ws in list(self.sockets.items()):
            self.drop(cid)
            try:
                await ws.close(code=4000, reason='test')
            except Exception:
                pass


class Rest:
    """RPC przez psql. `fail_next` = ile kolejnych zapisów gry ma się nie udać (symulacja braku sieci)."""
    FUNCS = {
        'pk_submit_game': "select public.pk_submit_game(b->'p_game') from a",
        'pk_leaderboard': "select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from a, lateral public.pk_leaderboard(b->>'p_level', b->>'p_mode', (b->>'p_days')::int, (b->>'p_limit')::int) t",
        'pk_recent_games': "select coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) from a, lateral public.pk_recent_games((b->>'p_limit')::int, b->>'p_name') t",
    }

    def __init__(self, pgurl):
        self.pgurl = pgurl
        self.fail_next = 0
        self.calls = []

    async def install(self, context):
        await context.route(SUPA_URL + '/rest/v1/rpc/*', self.handle)

    async def sql(self, body_json, query):
        assert '$pk$' not in body_json
        script = "\\set VERBOSITY verbose\nset role anon;\nwith a as (select $pk$" + body_json + "$pk$::jsonb as b) " + query + ";\n"
        p = await asyncio.create_subprocess_exec('psql', self.pgurl, '-X', '-q', '-t', '-A', '-v', 'ON_ERROR_STOP=1', '-f', '-',
                                                 stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await p.communicate(script.encode())
        return p.returncode, out.decode().strip(), err.decode()

    async def handle(self, route):
        req = route.request
        if req.method == 'OPTIONS':
            await route.fulfill(status=204, headers=self.cors())
            return
        name = req.url.rsplit('/', 1)[1].split('?')[0]
        body = req.post_data or '{}'
        self.calls.append(name)
        if name == 'pk_submit_game' and self.fail_next > 0:
            self.fail_next -= 1
            await route.fulfill(status=503, headers=self.cors(), content_type='application/json', body='{"message":"Service Unavailable"}')
            return
        if name not in self.FUNCS:
            await route.fulfill(status=404, headers=self.cors(), content_type='application/json', body='{"code":"PGRST202","message":"not found"}')
            return
        code, out, err = await self.sql(body, self.FUNCS[name])
        if code == 0:
            await route.fulfill(status=200, headers=self.cors(), content_type='application/json', body=out or 'null')
        else:
            m = re.search(r'ERROR:\s+([0-9A-Z]{5}):\s+(.*)', err)
            sqlstate, msg = (m.group(1), m.group(2).strip()) if m else ('XX000', err.strip())
            await route.fulfill(status=400, headers=self.cors(), content_type='application/json',
                                body=json.dumps({'code': sqlstate, 'message': msg, 'details': None, 'hint': None}))

    @staticmethod
    def cors():
        return {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'}


def config_js():
    return 'window.PK_CONFIG = %s;' % json.dumps({'supabaseUrl': SUPA_URL, 'supabaseAnonKey': ANON_KEY})
