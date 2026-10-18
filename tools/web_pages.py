"""Strony serwisu do hostingu (Vercel): teleturniej z zapisem wyników i strony z src/web.

Funkcje rep() sprawdzają, że wzorzec występuje dokładnie raz, więc zmiana w szablonie
od razu przerwie build w miejscu, które trzeba poprawić.
"""
import re

SUPABASE_TAGS = ('<script src="vendor/supabase.js"></script>\n'
                 '<script src="config.js"></script>\n'
                 '<script src="pk-online.js"></script>\n')

def rep(s, a, b):
    assert s.count(a) == 1, ('count', s.count(a), a[:60]); return s.replace(a, b)

def make_tv_web(doc):
    """Teleturniej (pełna strona z build.py) + zapis zakończonej gry do listy wyników."""
    s = rep(doc, '<script>\n', SUPABASE_TAGS + '<script>\n')
    s = rep(s, '  S = { level: settings.level, players,', '  S = { uid: window.PK ? PK.uuid() : null, level: settings.level, players,')
    s = rep(s, '<p class="copy-note" id="copyNote" aria-live="polite"></p>',
            '<p class="copy-note" id="copyNote" aria-live="polite"></p>\n'
            '      <p class="copy-note" id="rankNote" aria-live="polite"></p>\n'
            '      <a class="btn ghost" href="wyniki.html">Lista wyników</a>')
    # rejestr nicków: gracze z listy wyników jako chipy do dopisania
    s = rep(s, '<p class="hint">Imiona oddzielone przecinkami, w kolejności siedzenia.</p>',
            '<p class="hint">Imiona oddzielone przecinkami, w kolejności siedzenia.</p>\n'
            '        <div class="chips nickchips" id="nickChips" aria-label="Gracze z listy wyników" hidden></div>')
    s = rep(s, '$("#players").addEventListener("input", (e) => { settings.players = parsePlayers(e.target.value); saveSettings(); renderStarter(); });',
            '''$("#players").addEventListener("input", (e) => { settings.players = parsePlayers(e.target.value); saveSettings(); renderStarter(); renderNickChips(); });
let knownNicks = [];
function renderNickChips() {
  const have = new Set(settings.players.map((n) => n.toLowerCase())), box = $("#nickChips");
  const list = knownNicks.filter((n) => !have.has(n.toLowerCase())).slice(0, 12);
  box.hidden = !list.length;
  box.innerHTML = list.map((n) => `<button type="button" class="chip" data-n="${esc(n)}">+ ${esc(n)}</button>`).join("");
}
$("#nickChips").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-n]"); if (!b) return;
  const inp = $("#players"); inp.value = settings.players.concat(b.dataset.n).join(", ");
  inp.dispatchEvent(new Event("input"));
});
if (window.PK && PK.ready()) PK.nicks().then((l) => { knownNicks = l; renderNickChips(); });
/* dobór pytań: historia graczy z listy (z bazy) pobiera się przy zmianie listy, przed startem gry */
let histKey = null, histT = null;
function prefetchHist() {
  if (!window.PK || !PK.ready()) return;
  const key = settings.players.map((n) => n.toLowerCase()).sort().join("|");
  if (key === histKey) return;
  histKey = key; clearTimeout(histT);
  histT = setTimeout(() => PK.history(settings.players).then((h) => { if (histKey === key) setQHist(h); }), 400);
}
$("#players").addEventListener("input", prefetchHist); prefetchHist();''')
    s = rep(s, '.foot {', '''.nickchips { margin-top: 8px; }
.nickchips .chip { min-height: 36px; padding: 5px 12px; font-weight: 500; font-size: .85rem; }
.foot {''')
    # jedna gra: tryb wybiera się na stronie startowej; ustawienia wspólne z Live (pk_common)
    s = rep(s, '<button type="button" class="btn" id="btnStart">Zaczynamy</button>',
            '<button type="button" class="btn" id="btnStart">Zaczynamy</button>\n      <a class="link-btn" href="index.html">← Zmień tryb</a>')
    s = rep(s, '<p class="eyebrow" id="topicEyebrow">Teleturniej · Polityka</p>', '<p class="eyebrow hot" id="topicEyebrow">Tryb: jeden telefon</p>')
    s = rep(s, '$("#topicEyebrow").textContent = settings.level === "pop" ? "Teleturniej · Popkultura" : "Teleturniej · Polityka";', '')
    s = rep(s, 'count: 30, time: 15, minus: 1 }, load("pk_tv2", {}));', 'count: 30, time: 15, minus: 1 }, load("pk_tv2", {}), load("pk_common", {}));')
    s = rep(s, 'const saveSettings = () => save("pk_tv2", settings);',
            'const saveSettings = () => { save("pk_tv2", settings); save("pk_common", { level: settings.level, count: settings.count, minus: settings.minus, mix: settings.mix }); };')
    s = rep(s, '<p class="foot" id="foot"></p>',
            '<p class="sitenav"><a href="index.html">Strona główna</a><a href="wyniki.html">Lista wyników</a></p>\n  <p class="foot" id="foot"></p>')
    s = rep(s, '.foot {', '''.sitenav { display: flex; justify-content: center; gap: 18px; margin: 0; font-family: var(--f-mono); font-size: .72rem; letter-spacing: .06em; text-transform: uppercase; }
.sitenav a { color: var(--muted); }
a.btn { text-align: center; text-decoration: none; }
.foot {''')
    s = rep(s, '  show("final");\n}\n', r'''  show("final");
  submitTv();
}
function tvGameRecord() {
  const t = scores(), st = stats(), seen = new Set();
  const players = S.players.slice(0, 16).map((n, i) => {
    let name = String(n).trim().slice(0, 20) || "Gracz";
    for (let k = 2; seen.has(name.toLowerCase()); k++) name = String(n).trim().slice(0, 17) + " " + k;
    seen.add(name.toLowerCase());
    return { name, score: t[i], correct: st[i].ok, wrong: st[i].bad };
  });
  return { id: S.uid, mode: "teleturniej", level: S.level, code: null, questions_total: S.deck.length,
           questions_played: Math.max(1, S.log.filter(Boolean).length), penalty: S.minus, players,
           qids: S.deck.filter((q, i) => S.log[i]).map((q) => q.id) };
}
async function submitTv() {
  const note = $("#rankNote");
  if (!S || !S.uid || !window.PK) { note.textContent = ""; return; }
  if (!S.log.some(Boolean)) { note.textContent = "Gra bez odpowiedzi, nie trafia na listę wyników."; return; }
  if (S.saved) { note.textContent = "Wynik jest na liście wyników."; return; }
  note.textContent = "Zapisuję wynik na liście wyników…";
  const uid = S.uid, r = await PK.submitGame(tvGameRecord());
  if (!S || S.uid !== uid) return;
  if (r.ok) { S.saved = true; note.textContent = "Wynik zapisany na liście wyników."; }
  else note.textContent = r.why === "noconfig" ? "Lista wyników nie jest skonfigurowana." : r.why === "rejected" ? `Lista wyników odrzuciła tę grę${r.error && r.error.message ? ` (${r.error.message.replace(/^pk: /, "")})` : ""}.` : "Nie udało się zapisać wyniku. Spróbuję ponownie, gdy wróci internet.";
}
''')
    return s

def level_labels(template):
    """Słownik klucz → etykieta z obiektu LEVELS w szablonie (jedno źródło prawdy dla listy wyników)."""
    block = template[template.index('const LEVELS = {'):]
    block = block[:block.index('\n};')]
    pairs = re.findall(r'^\s*(\w+):\s*\{\s*label:\s*"([^"]+)"', block, re.M)
    assert pairs, 'nie znaleziono wpisów LEVELS'
    return dict(pairs)
