# Kroki zamiany wersji Live dla Claude (capability `room`) na samodzielną stronę z PeerJS.
# Wykonywane przez tools/web_transform.py: na wejściu zmienna `src` (HTML dist/live-claude.html),
# na wyjściu zmienna `doc` (kompletny dokument HTML). Każda zamiana sprawdza, że wzorzec występuje
# dokładnie raz, więc po zmianach w src/templates/live-claude.html build od razu pokaże, co się rozjechało.

def cut(s, start, end_marker, repl, include_end=False):
    i = s.index(start); j = s.index(end_marker, i)
    if include_end: j += len(end_marker)
    return s[:i] + repl + s[j:]

def rep(s, a, b):
    assert s.count(a) == 1, ('count', s.count(a), a[:60]); return s.replace(a, b)

# --- transport ---
TRANSPORT = r'''const PREFIX = "postaw-krzyzyk-live-v1-";
const PEER_OPTS = window.PK_PEER_OPTS || {};
function merge(a, patch) { const o = Object.assign({}, a); for (const k in patch) { if (patch[k] === null) delete o[k]; else o[k] = patch[k]; } return o; }
function attachRoom(r) {
  room = r;
  room.onConnection((c) => setConn(c ? "on" : "wait"));
  room.onPeers((ch) => { if (role === "host") hostOnPeers(ch); else if (role === "player") playerOnPeers(ch); });
}
function makeHostRoom(code) {
  return new Promise((resolve, reject) => {
    if (!window.Peer) { reject("nolib"); return; }
    const pr = new Peer(PREFIX + code, PEER_OPTS);
    const conns = new Map(), handlers = [], cbs = [];
    let mine = {}, opened = false;
    const snap = () => { const a = [{ peer: "me", isMe: true, sameTab: true, presence: mine, updatedAt: 0 }]; conns.forEach((v, k) => a.push({ peer: k, isMe: false, sameTab: false, presence: v.presence, updatedAt: v.updatedAt })); return a; };
    const fire = () => { const peers = snap(); handlers.forEach((h) => h({ peers, joined: [], left: [], updated: peers })); };
    const status = (v) => cbs.forEach((h) => h(v));
    const room = {
      presence: async (patch) => { mine = merge(mine, patch); conns.forEach((v) => { try { if (v.conn.open) v.conn.send({ t: "host", p: mine }); } catch (e) { } }); },
      peers: snap,
      onPeers: (h) => { handlers.push(h); setTimeout(fire, 0); return () => { }; },
      onConnection: (h) => { cbs.push(h); setTimeout(() => h(opened && !pr.disconnected), 0); return () => { }; },
      close: () => { try { pr.destroy(); } catch (e) { } }
    };
    pr.on("open", () => { const first = !opened; opened = true; status(true); if (first) resolve(room); });
    pr.on("error", (e) => { if (!opened) { try { pr.destroy(); } catch (x) { } reject((e && e.type) || "error"); } else if (!e || e.type !== "peer-unavailable") status(false); });
    pr.on("disconnected", () => { status(false); setTimeout(() => { try { if (!pr.destroyed) pr.reconnect(); } catch (e) { } }, 1500); });
    pr.on("connection", (c) => {
      c.on("open", () => { conns.set(c.peer, { conn: c, presence: {}, updatedAt: performance.now() }); try { c.send({ t: "host", p: mine }); } catch (e) { } fire(); });
      c.on("data", (d) => { if (d && d.t === "pres" && d.p && typeof d.p === "object") { conns.set(c.peer, { conn: c, presence: d.p, updatedAt: performance.now() }); fire(); } });
      const drop = () => { if (conns.has(c.peer)) { conns.delete(c.peer); fire(); } };
      c.on("close", drop); c.on("error", drop);
    });
  });
}
function makePlayerRoom(code) {
  return new Promise((resolve, reject) => {
    if (!window.Peer) { reject("nolib"); return; }
    const pr = new Peer(undefined, PEER_OPTS);
    const handlers = [], cbs = [];
    let mine = {}, host = null, hostAt = 0, c = null, settled = false, alive = true, retry = null;
    const snap = () => { const a = [{ peer: "me", isMe: true, sameTab: true, presence: mine, updatedAt: 0 }]; if (host) a.push({ peer: "host", isMe: false, sameTab: false, presence: host, updatedAt: hostAt }); return a; };
    const fire = () => { const peers = snap(); handlers.forEach((h) => h({ peers, joined: [], left: [], updated: peers })); };
    const status = (v) => cbs.forEach((h) => h(v));
    const later = () => { if (!alive || retry) return; retry = setTimeout(() => { retry = null; connect(); }, 2500); };
    const connect = () => {
      if (!alive) return;
      if (pr.disconnected) { try { pr.reconnect(); } catch (e) { } later(); return; }
      const cc = pr.connect(PREFIX + code, { reliable: true });
      c = cc;
      cc.on("open", () => { status(true); try { cc.send({ t: "pres", p: mine }); } catch (e) { } if (!settled) { settled = true; resolve(room); } });
      cc.on("data", (d) => { if (d && d.t === "host" && d.p && typeof d.p === "object") { host = d.p; hostAt = performance.now(); fire(); } });
      cc.on("close", () => { if (c !== cc) return; status(false); host = null; fire(); later(); });
      cc.on("error", () => { if (c === cc && !cc.open) later(); });
    };
    const room = {
      presence: async (patch) => { mine = merge(mine, patch); if (c && c.open) { try { c.send({ t: "pres", p: mine }); } catch (e) { } } },
      peers: snap,
      onPeers: (h) => { handlers.push(h); setTimeout(fire, 0); return () => { }; },
      onConnection: (h) => { cbs.push(h); setTimeout(() => h(!!(c && c.open)), 0); return () => { }; },
      close: () => { alive = false; try { pr.destroy(); } catch (e) { } }
    };
    pr.on("open", () => { if (!c || !c.open) connect(); });
    pr.on("error", (e) => {
      const t = e && e.type;
      if (!settled) { settled = true; alive = false; try { pr.destroy(); } catch (x) { } reject(t === "peer-unavailable" ? "nogame" : (t || "error")); }
      else { status(false); if (t === "peer-unavailable") later(); }
    });
    pr.on("disconnected", () => { setTimeout(() => { try { if (!pr.destroyed) pr.reconnect(); } catch (e) { } }, 1500); });
    setTimeout(() => { if (!settled) { settled = true; alive = false; try { pr.destroy(); } catch (e) { } reject("timeout"); } }, 15000);
  });
}
function newCode() { const A = "ABCDEFGHJKLMNPRSTUWXYZ"; let s = ""; for (let i = 0; i < 4; i++) s += A[Math.floor(Math.random() * A.length)]; return s; }
function joinUrl(code) { return location.href.split("#")[0].split("?")[0] + "?kod=" + code; }
function showCode(code) { document.querySelectorAll(".gamecode").forEach((el) => (el.textContent = code)); const u = document.querySelector("#joinUrl"); if (u) u.textContent = joinUrl(code); }
'''
src = cut(src, 'async function initRoom() {', 'function setDiag(', TRANSPORT)

# setConn note text + idle state
src = rep(src, 'const txt = state === "on" ? "Połączono" : state === "off" ? "Brak połączenia" : "Łączenie…";',
          'const txt = state === "on" ? "Połączono" : state === "off" ? "Brak połączenia" : state === "idle" ? "Gotowe" : "Łączenie…";')
src = rep(src, 'note.textContent = "Ten telefon nie może połączyć się z grą. Przyciski działają tylko dla osób zalogowanych w Claude, którym właściciel udostępnił ten link przez menu Udostępnij.";',
          'note.textContent = "Brak połączenia z grą. Sprawdź internet. Telefon sam spróbuje połączyć się ponownie.";')
src = rep(src, '<p class="conn" id="connRole"><span class="dot"></span><span>Łączenie…</span></p>', '<p class="conn idle" id="connRole"><span class="dot"></span><span>Gotowe</span></p>')

# join screen
src = rep(src, '<h2 id="t-pjoin" style="font-size:1.6rem;font-stretch:80%;font-weight:850">Jak masz na imię?</h2>',
 '''<h2 id="t-pjoin" style="font-size:1.6rem;font-stretch:80%;font-weight:850">Dołącz do gry</h2>
      <div class="field">
        <label for="pcode">Kod gry (od prowadzącego)</label>
        <input type="text" id="pcode" maxlength="6" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="np. KRZY" style="text-transform:uppercase;font-family:var(--f-mono);letter-spacing:.25em;font-size:1.3rem">
      </div>''')
src = rep(src, '<button type="button" class="btn" id="btnJoin">Dołącz do gry</button>', '<p class="notice" id="joinErr" hidden></p>\n      <button type="button" class="btn" id="btnJoin">Dołącz do gry</button>')
src = rep(src, '  $("#pname").value = P.name;\n', '  $("#pname").value = P.name;\n  $("#pcode").value = load("pkw_code", "") || "";\n')
src = cut(src, '$("#btnJoin").addEventListener("click", () => {', '$("#btnLeave")', r'''$("#btnJoin").addEventListener("click", async () => {
  const n = cleanName($("#pname").value);
  const code = String($("#pcode").value || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
  const err = $("#joinErr"); err.hidden = true;
  if (!code) { $("#pcode").focus(); return; }
  if (!n) { $("#pname").focus(); return; }
  P.name = n; save("pkl_name", n); save("pkw_code", code);
  const btn = $("#btnJoin"); btn.disabled = true; btn.textContent = "Łączę…";
  try {
    if (room && room.close) room.close();
    const r = await makePlayerRoom(code);
    role = "player"; attachRoom(r);
    setPresence({ role: "player", name: n, buzz: null, fs: null });
    renderPlayer(); show("s-player");
  } catch (e) {
    err.hidden = false;
    err.textContent = e === "nogame" ? `Nie ma gry o kodzie ${code}. Sprawdź kod u prowadzącego.` : e === "nolib" ? "Nie udało się wczytać modułu połączeń. Sprawdź internet i odśwież stronę." : "Nie udało się połączyć. Sprawdź internet i spróbuj ponownie.";
  } finally { btn.disabled = false; btn.textContent = "Dołącz do gry"; }
});
''')
src = rep(src, '$("#btnLeave").addEventListener("click", () => { role = null;', '$("#btnLeave").addEventListener("click", () => { if (room && room.close) room.close(); room = null; role = null;')

# host setup code box
src = rep(src, '''      <div class="field">
        <span class="label">Gracze przy przyciskach</span>''', '''      <div class="codebox">
        <p class="eyebrow">Kod gry</p>
        <p class="gamecode big" id="hsCode">----</p>
        <p class="hint">Gracze otwierają tę stronę na swoich telefonach, wybierają „Jestem graczem” i wpisują kod. Albo od razu otwierają ten link:</p>
        <p class="mono joinurl" id="joinUrl"></p>
        <button type="button" class="btn ghost" id="btnCopyLink">Kopiuj link dla graczy</button>
        <p class="copy-note" id="copyLinkNote" aria-live="polite"></p>
      </div>
      <div class="field">
        <span class="label">Gracze przy przyciskach</span>''')
src = rep(src, '<div class="hud-q"><span id="hQnum">Pytanie 1 z 30</span><span class="pill" id="hCat">Kategoria</span></div>',
          '<div class="hud-q"><span id="hQnum">Pytanie 1 z 30</span><span class="pill" id="hCat">Kategoria</span><span class="pill">Kod <span class="gamecode">----</span></span></div>')
src = rep(src, '.toggle { display: flex;', '''.codebox { display: grid; gap: 8px; padding: 14px; border: 1.5px dashed var(--rule-strong); border-radius: 3px; text-align: center; }
.gamecode.big { font-family: var(--f-mono); font-weight: 600; font-size: 2.8rem; letter-spacing: .3em; margin: 0; line-height: 1.1; color: var(--stamp); }
.joinurl { word-break: break-all; font-size: .82rem; margin: 0; font-family: var(--f-mono); }
.toggle { display: flex;''')

# host role handler
src = cut(src, '$("#btnBeHost").addEventListener("click", () => {', '$("#btnBack1")', r'''$("#btnBeHost").addEventListener("click", async () => {
  const b = $("#btnBeHost"); b.disabled = true; b.textContent = "Tworzę grę…";
  let code = load("pkw_hcode", null), r = null, why = null;
  for (let k = 0; k < 4 && !r; k++) {
    if (!code || k > 0) code = newCode();
    try { r = await makeHostRoom(code); } catch (e) { why = e; if (e === "nolib") break; }
  }
  b.disabled = false; b.textContent = "Prowadzę grę";
  if (!r) { const n = $("#roomNote"); n.hidden = false; n.className = "notice"; n.textContent = why === "nolib" ? "Nie udało się wczytać modułu połączeń. Sprawdź internet i odśwież stronę." : "Nie udało się utworzyć gry. Sprawdź internet i spróbuj ponownie."; return; }
  if (room && room.close && room !== r) room.close();
  save("pkw_hcode", code); role = "host"; attachRoom(r); showCode(code);
  if (H && H.deck && H.ph && H.ph !== "lobby" && H.ph !== "final") { publishHost(); renderHost(); show("s-host"); if (H.ph === "locked") startAnswerTimer(); }
  else { H = { ph: "lobby" }; saveH(); publishHost(); renderHostSetup(); show("s-hsetup"); }
});
$("#btnCopyLink").addEventListener("click", () => {
  const code = load("pkw_hcode", ""), t = joinUrl(code), note = $("#copyLinkNote");
  try { navigator.clipboard.writeText(t).then(() => (note.textContent = "Skopiowano link."), () => (note.textContent = "Zaznacz link powyżej i skopiuj go ręcznie.")); } catch (e) { note.textContent = "Zaznacz link powyżej i skopiuj go ręcznie."; }
});
''')
src = rep(src, '$("#btnBack2").addEventListener("click", () => { role = null;', '$("#btnBack2").addEventListener("click", () => { if (room && room.close) room.close(); room = null; role = null;')

# boot
src = cut(src, 'function boot() {', '</script>', r'''function boot() {
  const q = new URLSearchParams(location.search).get("kod");
  if (q) save("pkw_code", q.toUpperCase().replace(/[^A-Z0-9]/g, ""));
  setConn("idle");
  if (q) renderJoin(); else show("s-role");
  if (!window.Peer) { setConn("off"); const n = $("#roomNote"); n.hidden = false; n.className = "notice"; n.textContent = "Nie udało się wczytać modułu połączeń (PeerJS). Sprawdź internet i odśwież stronę."; }
}
boot();
''')
src = rep(src, '<p class="foot" id="foot">Przyciski działają dla osób zalogowanych w Claude, którym udostępniono ten link.</p>',
          '<p class="foot" id="foot">Bez logowania. Telefony łączą się ze sobą bezpośrednio przez internet.</p>')
assert 'initRoom' not in src.split('<script>',1)[1].replace('function setDiag','')

# wrap into standalone document
head_end = src.index('</style>') + len('</style>')
head, body = src[:head_end], src[head_end:]
i = body.index('<script>')
body = body[:i] + '<script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>\n' + body[i:]
doc = ('<!doctype html>\n<html lang="pl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       '<style>[hidden]{display:none!important}html{color-scheme:light}body{margin:0}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}</style>\n'
       + head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '') + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
doc = doc.replace('<title>Postaw Krzyżyk Live</title>', '<title>Postaw Krzyżyk Live</title>')
