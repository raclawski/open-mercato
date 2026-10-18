/* Bęben wyboru kategorii: przewijana lista, wybrany jest wiersz na środku (podświetlony pas z krzyżykiem).
   Wiersze to zwykłe przyciski z data-v i aria-pressed. Wybór idzie przez kliknięcie przycisku,
   więc istniejąca obsługa (bindSeg, setSeg) działa bez zmian. Bęben tylko:
   - po zatrzymaniu przewijania klika wiersz, który stanął na środku,
   - po zmianie wyboru (kliknięcie, strzałki, ustawienia z pamięci) przewija go na środek,
   - wygina wiersze jak na walcu (im dalej od środka, tym bardziej obrócone i bledsze). */
function initDrum(el, meta) {
  const rows = [...el.querySelectorAll("button[data-v]")];
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const BOX = '<span class="dbox" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 5.4 C9.2 9.6 14 14.4 19 19.1"/><path d="M18.8 5.1 C14.3 9.6 9.9 14.2 5.2 19.2"/></svg></span>';
  rows.forEach((b) => { b.innerHTML = BOX + `<span class="dl">${b.innerHTML}</span>` + (meta ? `<span class="dm">${meta(b.dataset.v)}</span>` : ""); });
  let cur = null, auto = false, endT = null, frame = 0;
  const mid = () => el.scrollTop + el.clientHeight / 2;
  const at = (b) => b.offsetTop + b.offsetHeight / 2;
  function paint() {
    frame = 0;
    const m = mid(), h = rows[0].offsetHeight || 1;
    for (const b of rows) {
      const d = (at(b) - m) / h;
      b.style.transform = `perspective(560px) rotateX(${Math.max(-70, Math.min(70, -d * 21))}deg)`;
      b.style.opacity = String(Math.max(0.22, 1 - Math.abs(d) * 0.27));
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
