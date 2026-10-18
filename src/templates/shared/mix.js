/* Losowanie pytań i tryb mieszany („Mieszane”, klucz `mix`): pytania z kilku kategorii w jednej grze.
   Kategorie z mieszanki dostają po równo pytań i przeplatają się (w każdej rundzie w losowej kolejności).
   Dobór jak tasowanie w Spotify: nie czysto losowy, tylko według wag. Pytanie, którego nikt jeszcze nie widział,
   ma wagę 1, a ograne (niedawno albo przez kilku graczy) mniejszą, ale nigdy zerową, więc może wrócić, tylko rzadziej.
   „Ogranie” bierze się z pamięci telefonu (pk_seen_at: qid → kiedy) i z bazy dla nicków w grze (setQHist, wersja z serwerem).
   Id pytania to `kategoria:skrót treści` (qid), więc nie zmienia się po dopisaniu pytań. */
const MIX = "mix";
const realLevels = () => Object.keys(LEVELS).filter((k) => LEVELS[k].bank);
/* pusta lista = wszystkie kategorie poza specjalnymi (np. „Chajzerowie”), które do mieszanki trzeba dodać ręcznie */
const mixKeys = (sel) => { const ok = (Array.isArray(sel) ? sel : []).filter((k) => LEVELS[k] && LEVELS[k].bank); return ok.length ? ok : realLevels().filter((k) => !LEVELS[k].special); };
const levelSize = (k) => LEVELS[k].bank.reduce((s, c) => s + c.q.length, 0);
function poolSize(level, sel) { return level === MIX ? mixKeys(sel).reduce((s, k) => s + levelSize(k), 0) : levelSize(level); }
/* Skrót treści pytania (FNV-1a, 32 bity): tylko litery i cyfry, bez wielkości liter. Ten sam liczy tests/validate_questions.js. */
function qhash(t) {
  let h = 0x811c9dc5;
  for (const ch of String(t).toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "")) { h ^= ch.codePointAt(0); h = Math.imul(h, 0x01000193) >>> 0; }
  return h.toString(36);
}
const qid = (level, Q) => `${level}:${qhash(Q.q)}`;
/* Pamięć sprzed stałych id (`kategoria:dział-nr`) przepisuje się na nowe id według obecnej kolejności pytań. */
function migrateSeen(list) {
  return list.map((id) => {
    const m = /^([a-z]+):(\d+)-(\d+)$/.exec(id), cat = m && LEVELS[m[1]] && LEVELS[m[1]].bank && LEVELS[m[1]].bank[+m[2]], Q = cat && cat.q[+m[3]];
    return Q ? qid(m[1], Q) : id;
  });
}
const DAY = 864e5, TAU_DAYS = 20, MIN_W = 0.02;
let QHIST = {};
function setQHist(h) { QHIST = h && typeof h === "object" && !Array.isArray(h) ? h : {}; }
function loadSeenAt() {
  const m = load("pk_seen_at", null);
  if (m && typeof m === "object" && !Array.isArray(m)) return m;
  const out = {}, t = Date.now() - 7 * DAY;  // stara pamięć (lista bez dat) liczy się jak sprzed tygodnia
  migrateSeen(load("pk_seen", [])).forEach((id) => { if (typeof id === "string") out[id] = t; });
  return out;
}
function saveSeenAt(m) { const cut = Date.now() - 365 * DAY; for (const k in m) if (!(m[k] > cut)) delete m[k]; save("pk_seen_at", m); }
/* Ogranie p: wczoraj u jednego gracza ≈ 1, u trzech ≈ 3, sprzed 20 dni ≈ 0,37. Waga e^(−3p), najmniej MIN_W. */
function qweight(id, seenAt, now) {
  const local = seenAt[id] ? Math.exp(-Math.max(0, now - seenAt[id]) / DAY / TAU_DAYS) : 0;
  return Math.max(MIN_W, Math.exp(-3 * Math.max(local, +QHIST[id] || 0)));
}
/* losowanie bez zwracania według wag (Efraimidis–Spirakis): klucz u^(1/w), wygrywają największe */
function weightedPick(items, need, w) {
  return items.map((x) => ({ x, k: Math.pow(Math.random(), 1 / w(x)) })).sort((a, b) => b.k - a.k).slice(0, need).map((o) => o.x);
}
/* dwa pytania z tego samego działu nie idą po sobie, jeśli da się tego uniknąć */
function spread(list, key) {
  const a = list.slice();
  for (let i = 1; i < a.length; i++) if (key(a[i]) === key(a[i - 1])) {
    const j = a.findIndex((x, k) => k > i && key(x) !== key(a[i - 1]));
    if (j > 0) [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function pickLevel(level, need, seenAt, now) {
  const all = [];
  LEVELS[level].bank.forEach((cat) => cat.q.forEach((Q) => all.push({ id: qid(level, Q), Q, cat: cat.name, lv: level })));
  return spread(shuffle(weightedPick(all, Math.min(need, all.length), (x) => qweight(x.id, seenAt, now))), (x) => x.cat);
}
function buildDeck(level, count, sel) {
  const seenAt = loadSeenAt(), now = Date.now();
  let pick;
  if (level !== MIX) pick = pickLevel(level, count, seenAt, now);
  else {
    const keys = mixKeys(sel), need = {};
    keys.forEach((k) => (need[k] = 0));
    let left = Math.min(count, keys.reduce((s, k) => s + levelSize(k), 0));
    while (left > 0) for (const k of shuffle(keys)) if (left > 0 && need[k] < levelSize(k)) { need[k]++; left--; }
    const lists = keys.map((k) => pickLevel(k, need[k], seenAt, now));
    pick = [];
    while (lists.some((l) => l.length)) for (const l of shuffle(lists)) if (l.length) pick.push(l.shift());
    pick.forEach((x) => (x.cat = LEVELS[x.lv].label));
  }
  pick.forEach((x) => (seenAt[x.id] = now)); saveSeenAt(seenAt);
  return pick.map(({ id, Q, cat }) => {
    const order = Q.fix ? Q.o.map((_, i) => i) : shuffle(Q.o.map((_, i) => i));
    return { id, cat, q: Q.q, o: order.map((i) => Q.o[i]), c: order.indexOf(Q.c), e: Q.e };
  });
}
/* Wybór kategorii do mieszanki: chipy pod bębnem, widoczne tylko przy „Mieszane”. Zawsze zostaje co najmniej jedna. */
function initMix(box, getSel, setSel) {
  box.innerHTML = `<span class="label" id="lbl-mix">Kategorie w mieszance</span>
    <div class="chips" role="group" aria-labelledby="lbl-mix">${realLevels().map((k) => `<button type="button" class="chip" data-k="${k}">${esc(LEVELS[k].label)}</button>`).join("")}</div>
    <p class="hint" id="mixHint"></p>`;
  box.addEventListener("click", (e) => {
    const b = e.target.closest("[data-k]"); if (!b) return;
    const cur = mixKeys(getSel()), k = b.dataset.k;
    const next = cur.includes(k) ? cur.filter((x) => x !== k) : realLevels().filter((x) => x === k || cur.includes(x));
    if (next.length) setSel(next);
  });
}
function renderMix(box, level, sel) {
  box.hidden = level !== MIX;
  if (box.hidden) return;
  const on = mixKeys(sel);
  box.querySelectorAll("[data-k]").forEach((b) => b.setAttribute("aria-pressed", String(on.includes(b.dataset.k))));
  box.querySelector("#mixHint").textContent = `${on.length} ${on.length === 1 ? "kategoria" : on.length < 5 ? "kategorie" : "kategorii"}, ${poolSize(MIX, on)} pytań w puli. Kliknij, żeby dodać albo usunąć.`;
}
/* Liczba pytań: suwak z przyciskami −/+ (na telefonie suwakiem trudno trafić w jedną liczbę).
   Najwięcej 100 w jednym quizie i nie więcej, niż jest pytań w wybranych kategoriach (countMax). */
const countMax = (level, sel) => Math.max(1, Math.min(100, poolSize(level, sel)));
const clampCount = (n, max = 100) => Math.max(1, Math.min(max, Math.round(+n) || 30));
function showCount(r) { $("#countOut").innerHTML = `${r.value}<small>/${r.max}</small>`; }
/* ustawia suwak i zwraca liczbę po przycięciu do limitu (do zapisania w ustawieniach) */
function setCount(n, max = 100) { const r = $("#countRange"); if (!r) return clampCount(n, max); r.max = max; r.value = clampCount(n, max); showCount(r); return +r.value; }
function initCount(onInput, onDone) {
  const r = $("#countRange");
  r.addEventListener("input", () => { showCount(r); onInput(+r.value); });
  r.addEventListener("change", () => onDone());
  document.querySelectorAll("#countPick .cstep").forEach((b) => b.addEventListener("click", () => {
    r.value = clampCount(+r.value + +b.dataset.d, +r.max); showCount(r); onInput(+r.value); onDone();
  }));
}
/* Pytanie ×2: jedno losowe na każde 10 pytań (gra na 7 pytań ma jedno). Punkty i kara razy dwa. */
function withX2(deck, on) {
  if (on === false) return deck;
  for (let k = 0; k * 10 < deck.length; k++) { const lo = k * 10, hi = Math.min(deck.length, lo + 10); deck[lo + Math.floor(Math.random() * (hi - lo))].x2 = 1; }
  return deck;
}
const qmul = (q) => (q && q.x2 ? 2 : 1);
function initX2(get, set) { const c = $("#optX2"); c.checked = get() !== false; c.addEventListener("change", () => set(c.checked)); }
