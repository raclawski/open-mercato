/* Losowanie pytań i tryb mieszany („Mieszane”, klucz `mix`): pytania z kilku kategorii w jednej grze.
   Kategorie z mieszanki dostają po równo pytań i przeplatają się (w każdej rundzie w losowej kolejności).
   Najpierw idą pytania, których jeszcze nie było (pk_seen). Id pytania to `kategoria:skrót treści` (qid), więc
   nie zmienia się po dopisaniu pytań i jest wspólne dla gry z jedną kategorią i mieszanej. */
const MIX = "mix";
const realLevels = () => Object.keys(LEVELS).filter((k) => LEVELS[k].bank);
const mixKeys = (sel) => { const ok = (Array.isArray(sel) ? sel : []).filter((k) => LEVELS[k] && LEVELS[k].bank); return ok.length ? ok : realLevels(); };
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
function pickLevel(level, need, seen) {
  const all = [];
  LEVELS[level].bank.forEach((cat) => cat.q.forEach((Q) => all.push({ id: qid(level, Q), Q, cat: cat.name, lv: level })));
  let fresh = shuffle(all.filter((x) => !seen.has(x.id)));
  if (fresh.length < need) { all.forEach((x) => seen.delete(x.id)); fresh = fresh.concat(shuffle(all.filter((x) => !fresh.includes(x)))); }
  return fresh.slice(0, Math.min(need, all.length));
}
function buildDeck(level, count, sel) {
  const seen = new Set(migrateSeen(load("pk_seen", [])));
  let pick;
  if (level !== MIX) pick = pickLevel(level, count, seen);
  else {
    const keys = mixKeys(sel), need = {};
    keys.forEach((k) => (need[k] = 0));
    let left = Math.min(count, keys.reduce((s, k) => s + levelSize(k), 0));
    while (left > 0) for (const k of shuffle(keys)) if (left > 0 && need[k] < levelSize(k)) { need[k]++; left--; }
    const lists = keys.map((k) => pickLevel(k, need[k], seen));
    pick = [];
    while (lists.some((l) => l.length)) for (const l of shuffle(lists)) if (l.length) pick.push(l.shift());
    pick.forEach((x) => (x.cat = LEVELS[x.lv].label));
  }
  pick.forEach((x) => seen.add(x.id)); save("pk_seen", [...seen]);
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
/* Liczba pytań: suwak 1–100 z przyciskami −/+ (na telefonie suwakiem trudno trafić w jedną liczbę). */
const clampCount = (n) => Math.max(1, Math.min(100, Math.round(+n) || 30));
function setCount(n) { const r = $("#countRange"); if (!r) return; r.value = clampCount(n); $("#countOut").textContent = r.value; }
function initCount(onInput, onDone) {
  const r = $("#countRange");
  r.addEventListener("input", () => { $("#countOut").textContent = r.value; onInput(+r.value); });
  r.addEventListener("change", () => onDone());
  document.querySelectorAll("#countPick .cstep").forEach((b) => b.addEventListener("click", () => {
    r.value = clampCount(+r.value + +b.dataset.d); $("#countOut").textContent = r.value; onInput(+r.value); onDone();
  }));
}
