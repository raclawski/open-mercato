/* Bęben wyboru kategorii: przewijana lista, wybrany jest wiersz na środku (podświetlony pas z krzyżykiem).
   Wiersze to zwykłe przyciski z data-v i aria-pressed. Wybór idzie przez kliknięcie przycisku,
   więc istniejąca obsługa (bindSeg, setSeg) działa bez zmian. Bęben tylko:
   - po zatrzymaniu przewijania klika wiersz, który stanął na środku,
   - po zmianie wyboru (kliknięcie, strzałki, ustawienia z pamięci) przewija go na środek,
   - układa wiersze na wielkim kole: im dalej od środka, tym bardziej obrócone (spłaszczone), mniejsze,
     bliżej środka koła i bledsze; środkowy wiersz jest pełny i ostry. */
function initDrum(el, meta) {
  const rows = [...el.querySelectorAll("button[data-v]")];
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const BOX = '<span class="dbox" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 5.4 C9.2 9.6 14 14.4 19 19.1"/><path d="M18.8 5.1 C14.3 9.6 9.9 14.2 5.2 19.2"/></svg></span>';
  rows.forEach((b) => { b.innerHTML = BOX + `<span class="dl">${b.innerHTML}</span>` + (meta ? `<span class="dm">${meta(b.dataset.v)}</span>` : ""); });
  let cur = null, auto = false, endT = null, frame = 0;
  const mid = () => el.scrollTop + el.clientHeight / 2;
  const at = (b) => b.offsetTop + b.offsetHeight / 2;
  const STEP = 20;  // stopnie koła na jeden wiersz
  function paint() {
    frame = 0;
    const m = mid(), h = rows[0].offsetHeight || 1, R = h / (STEP * Math.PI / 180);
    for (const b of rows) {
      const d = (at(b) - m) / h, th = Math.max(-88, Math.min(88, d * STEP)), rad = th * Math.PI / 180;
      // na kole wiersz stoi na wysokości R·sin(kąt), a nie d·h jak na liście: dosuwamy go do środka
      const dy = R * Math.sin(rad) - d * h, sc = 1 - Math.min(0.24, Math.abs(d) * 0.08);
      b.style.transform = `translateY(${dy.toFixed(1)}px) perspective(900px) rotateX(${(-th).toFixed(1)}deg) scale(${sc.toFixed(3)})`;
      b.style.opacity = Math.abs(th) >= 88 ? "0" : String(Math.max(0.1, Math.pow(Math.cos(rad), 1.8)).toFixed(3));
    }
  }
  const nearest = () => { const m = mid(); return rows.reduce((a, b) => (Math.abs(at(b) - m) < Math.abs(at(a) - m) ? b : a)); };
  function center(b, smooth) {
    const top = at(b) - el.clientHeight / 2;
    if (Math.abs(el.scrollTop - top) < 1) return;
    auto = true;
    el.scrollTo({ top, behavior: smooth && !still ? "smooth" : "auto" });
  }
  function settle() {
    if (auto) { auto = false; return; }
    // ukrycie ekranu (np. start gry) też zmienia przewinięcie; to nie jest wybór gracza
    if (!el.clientHeight) return;
    const b = nearest();
    if (b.getAttribute("aria-pressed") !== "true") b.click();
    else center(b, true);
  }
  function sync(smooth) {
    const p = rows.find((b) => b.getAttribute("aria-pressed") === "true");
    if (p && p !== cur) { cur = p; if (el.clientHeight) center(p, smooth); }
  }
  el.addEventListener("scroll", () => {
    if (!el.clientHeight) { auto = false; clearTimeout(endT); return; }
    if (!frame) frame = requestAnimationFrame(paint);
    clearTimeout(endT); endT = setTimeout(settle, 140);
  }, { passive: true });
  el.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    const i = rows.indexOf(cur || nearest()), b = rows[Math.max(0, Math.min(rows.length - 1, i + (e.key === "ArrowDown" ? 1 : -1)))];
    b.click(); b.focus({ preventScroll: true });
  });
  new MutationObserver(() => sync(true)).observe(el, { subtree: true, attributes: true, attributeFilter: ["aria-pressed"] });
  // ukryty ekran nie ma wymiarów: wycentruj wybór, gdy bęben pojawi się na ekranie
  new ResizeObserver(() => { if (!el.clientHeight) return; if (cur) center(cur, false); paint(); }).observe(el);
  sync(false);
}
/* Rodzaj gry nad bębnem: „1 kategoria” (bęben) albo „MIX” (lista kategorii do zaznaczenia).
   Ostatnia pojedyncza kategoria jest pamiętana (pk_cat1), żeby powrót z MIX wracał do niej. */
function syncCatMode(level) {
  const mix = level === MIX, wrap = $("#levelSeg").closest(".drum-wrap");
  document.querySelectorAll("#catMode button").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.v === "mix") === mix)));
  wrap.hidden = mix;
  if (!mix && LEVELS[level] && LEVELS[level].bank) save("pk_cat1", level);
}
function initCatMode(setLevel) {
  $("#catMode").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-v]"); if (!b) return;
    const last = load("pk_cat1", null);
    setLevel(b.dataset.v === "mix" ? MIX : LEVELS[last] && LEVELS[last].bank ? last : realLevels()[0]);
  });
}
