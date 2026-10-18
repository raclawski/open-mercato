# Dodatkowe kroki dla wersji Live na Supabase (FLAVOR = "supabase").
# Uruchamiane z web_transform_steps.py po krokach PeerJS, na tej samej zmiennej `src`:
# podmienia transport PeerJS na src/web/pk-online.js (Supabase Realtime) i dokłada zapis
# zakończonej gry do listy wyników. Funkcje rep() i cut() pochodzą z web_transform_steps.py.

SUPABASE_TAGS = ('<script src="vendor/supabase.js"></script>\n'
                 '<script src="config.js"></script>\n'
                 '<script src="pk-online.js"></script>\n')

# --- transport: makeHostRoom / makePlayerRoom przez Supabase ---
src = cut(src, 'const PREFIX = "postaw-krzyzyk-live-v1-";', 'function newCode()', r'''/* Stały identyfikator prowadzącego na tym urządzeniu: po odświeżeniu strony wraca do tego samego kodu gry. */
const HID = (() => { let v = load("pkw_hid", null); if (typeof v !== "string" || !v.startsWith("h-")) { v = "h-" + (window.PK ? PK.uuid() : Date.now().toString(36)); save("pkw_hid", v); } return v; })();
function attachRoom(r) {
  room = r;
  room.onConnection((c) => setConn(c ? "on" : "wait"));
  room.onPeers((ch) => { if (role === "host") hostOnPeers(ch); else if (role === "player") playerOnPeers(ch); });
}
function makeHostRoom(code) { return window.PK ? PK.hostRoom(code, HID) : Promise.reject("nolib"); }
function makePlayerRoom(code) { return window.PK ? PK.playerRoom(code) : Promise.reject("nolib"); }
function libErrText(e) {
  return e === "noconfig" ? "Gra nie ma jeszcze ustawionego serwera (brak konfiguracji Supabase w config.js)." : "Nie udało się wczytać modułu połączeń. Sprawdź internet i odśwież stronę.";
}
''')

# komunikaty błędów: brak konfiguracji to osobny przypadek
src = rep(src, 'e === "nolib" ? "Nie udało się wczytać modułu połączeń. Sprawdź internet i odśwież stronę." : "Nie udało się połączyć.',
          'e === "nolib" || e === "noconfig" ? libErrText(e) : "Nie udało się połączyć.')
src = rep(src, 'if (e === "nolib") break;', 'if (e === "nolib" || e === "noconfig") break;')
src = rep(src, 'why === "nolib" ? "Nie udało się wczytać modułu połączeń. Sprawdź internet i odśwież stronę." :',
          'why === "nolib" || why === "noconfig" ? libErrText(why) :')
src = rep(src, '''  if (!window.Peer) { setConn("off"); const n = $("#roomNote"); n.hidden = false; n.className = "notice"; n.textContent = "Nie udało się wczytać modułu połączeń (PeerJS). Sprawdź internet i odśwież stronę."; }''',
          '''  if (!window.PK || !PK.ready()) { setConn("off"); const n = $("#roomNote"); n.hidden = false; n.className = "notice"; n.textContent = libErrText(window.PK ? PK.whyOff() : "nolib"); }''')
src = rep(src, '<p class="foot" id="foot">Bez logowania. Telefony łączą się ze sobą bezpośrednio przez internet.</p>',
          '<p class="foot" id="foot">Bez logowania. Telefony łączą się przez serwer gry, a wyniki trafiają na <a href="wyniki.html">listę wyników</a>.</p>')

# nawigacja na ekranie wyboru roli
src = rep(src, '''        <button type="button" class="btn ghost" id="btnBeHost">Prowadzę grę</button>
      </div>''', '''        <button type="button" class="btn ghost" id="btnBeHost">Prowadzę grę</button>
      </div>
      <p class="sitenav"><a href="index.html">Strona główna</a><a href="wyniki.html">Lista wyników</a></p>''')
src = rep(src, '.foot { text-align: center;', '''.sitenav { display: flex; justify-content: center; gap: 18px; margin: 0; font-family: var(--f-mono); font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; }
.sitenav a, .foot a { color: var(--muted); }
a.btn { text-align: center; text-decoration: none; box-sizing: border-box; }
.foot { text-align: center;''')

# --- lista wyników: każda gra ma uid, po zakończeniu prowadzący zapisuje wynik ---
src = rep(src, 'H = { g: "g" + Date.now().toString(36), level: settings.level,',
          'H = { uid: window.PK ? PK.uuid() : null, g: "g" + Date.now().toString(36), level: settings.level,')
src = rep(src, 'function endGame() { stopTimer(); H.ph = "final"; saveH(); publishHost(); renderFinal(sortedScores(), true); }',
          r'''function endGame() { stopTimer(); H.ph = "final"; saveH(); publishHost(); renderFinal(sortedScores(), true); submitLive(); }
function liveGameRecord() {
  const st = {};
  H.log.forEach((a) => { st[a.name] = st[a.name] || { ok: 0, bad: 0 }; st[a.name][a.ok ? "ok" : "bad"]++; });
  const players = sortedScores().slice(0, 16).map(([n, s]) => ({ name: n, score: s, correct: (st[n] || {}).ok || 0, wrong: (st[n] || {}).bad || 0 }));
  return { id: H.uid, mode: "live", level: H.level, code: load("pkw_hcode", "") || null, questions_total: H.deck.length,
           questions_played: Math.min(H.deck.length, H.i + 1), penalty: H.minus, players };
}
async function submitLive() {
  const note = $("#fRank");
  if (!H || !H.uid || !H.log.length || !window.PK) { note.textContent = H && !H.log.length ? "Gra bez odpowiedzi, nie trafia na listę wyników." : ""; return; }
  if (H.saved) { note.textContent = "Wynik jest na liście wyników."; return; }
  note.textContent = "Zapisuję wynik na liście wyników…";
  const uid = H.uid, r = await PK.submitGame(liveGameRecord());
  if (!H || H.uid !== uid) return;
  if (r.ok) { H.saved = true; saveH(); note.textContent = "Wynik zapisany na liście wyników."; }
  else note.textContent = r.why === "noconfig" ? "Lista wyników nie jest skonfigurowana." : r.why === "rejected" ? `Lista wyników odrzuciła tę grę${r.error && r.error.message ? ` (${r.error.message.replace(/^pk: /, "")})` : ""}.` : "Nie udało się zapisać wyniku. Spróbuję ponownie, gdy wróci internet.";
}''')
src = rep(src, '<div class="host-actions" id="fActions"></div>',
          '<div class="host-actions" id="fActions"></div>\n      <p class="copy-note" id="fRank" aria-live="polite"></p>')
src = rep(src, '''$("#fActions").innerHTML = isHost ? `<button type="button" class="btn go" data-f="again">Nowa gra</button>` : "";''',
          '''$("#fActions").innerHTML = (isHost ? `<button type="button" class="btn go" data-f="again">Nowa gra</button>` : "") + `<a class="btn ghost" href="wyniki.html">Lista wyników</a>`;''')
src = rep(src, '''if (e.target.closest('[data-f="again"]')) { H = { ph: "lobby" };''', '''if (e.target.closest('[data-f="again"]')) { $("#fRank").textContent = ""; H = { ph: "lobby" };''')

# --- jedna gra: tryb wybiera się na stronie startowej (index.html), tu przychodzi w adresie ---
#   live.html?tryb=prowadzacy  od razu ustawienia prowadzącego (albo powrót do trwającej gry)
#   live.html?tryb=gracz       ekran dołączania;  live.html?kod=XXXX  link od prowadzącego
#   bez parametrów             powrót do wyboru trybu
src = rep(src, '''  setConn("idle");
  if (q) renderJoin(); else show("s-role");
  if (!window.PK || !PK.ready()) {''', '''  const tryb = new URLSearchParams(location.search).get("tryb");
  setConn("idle");
  if (q || tryb === "gracz") renderJoin();
  else if (tryb === "prowadzacy") {
    // instrukcja zostaje na ekranie, dopóki prowadzący sam nie kliknie „Zaczynamy!”; trwająca gra wraca od razu
    show("s-role");
    const running = H && H.deck && H.ph && H.ph !== "lobby" && H.ph !== "final";
    if (running) $("#btnBeHost").click();
    else { $("#btnBePlayer").hidden = true; const bh = $("#btnBeHost"); bh.className = "btn go"; bh.textContent = "Zaczynamy!"; bh.dataset.label = "Zaczynamy!"; }
  }
  else { location.replace("index.html"); return; }
  if (!window.PK || !PK.ready()) {''')
src = rep(src, '$("#btnBack1").addEventListener("click", () => show("s-role"));', '$("#btnBack1").addEventListener("click", () => location.assign("index.html"));')
src = rep(src, 'setPresence({ role: null, g: null, ph: null }); show("s-role"); });', 'setPresence({ role: null, g: null, ph: null }); location.assign("index.html"); });')
src = rep(src, 'setPresence({ role: null, name: null, buzz: null, fs: null }); show("s-role"); });', 'setPresence({ role: null, name: null, buzz: null, fs: null }); location.assign("index.html"); });')
src = rep(src, '<button type="button" class="link-btn" id="btnBack1">← Zmień rolę</button>', '<button type="button" class="link-btn" id="btnBack1">← Zmień tryb</button>')
src = rep(src, '<button type="button" class="link-btn" id="btnBack2">← Zmień rolę</button>', '<button type="button" class="link-btn" id="btnBack2">← Zmień tryb</button>')
src = rep(src, '''<p class="eyebrow hot">Prowadzący</p>
      <p class="conn" id="connHS">''', '''<p class="eyebrow hot">Przyciski na telefonach · prowadzący</p>
      <p class="conn" id="connHS">''')

# rejestr nicków: podpowiedzi z listy wyników przy imieniu gracza i admina
src = rep(src, '<input type="text" id="pname" maxlength="20" autocomplete="off" placeholder="np. Asia">',
          '<input type="text" id="pname" maxlength="20" autocomplete="off" placeholder="np. Asia" list="nickList">\n        <datalist id="nickList"></datalist>')
src = rep(src, '<input type="text" id="adminName" maxlength="20" autocomplete="off" placeholder="np. Adam">',
          '<input type="text" id="adminName" maxlength="20" autocomplete="off" placeholder="np. Adam" list="nickList">')
src = rep(src, 'function boot() {', '''function fillNicks() {
  if (!window.PK || !PK.ready()) return;
  PK.nicks().then((list) => { $("#nickList").innerHTML = list.map((n) => `<option value="${esc(n)}"></option>`).join(""); });
}
function boot() {
  fillNicks();''')

# poziom, liczba pytań i kara są wspólne dla obu trybów (pk_common), czas na odpowiedź nie
src = rep(src, 'let settings = Object.assign({ level: "pro", count: 30, time: 10, minus: 1, mode: "online" }, load("pkl_settings2", {}));',
          'let settings = Object.assign({ level: "pro", count: 30, time: 10, minus: 1, mode: "online" }, load("pkl_settings2", {}), load("pk_common", {}));')
src = rep(src, 'const saveSettings = () => save("pkl_settings2", settings);',
          'const saveSettings = () => { save("pkl_settings2", settings); save("pk_common", { level: settings.level, count: settings.count, minus: settings.minus, mix: settings.mix }); };')
