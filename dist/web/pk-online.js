/* Postaw Krzyżyk online: Supabase (Realtime dla gry Live, RPC dla listy wyników).
   Wymaga wcześniej: vendor/supabase.js (window.supabase) i config.js (window.PK_CONFIG).
   Gra Live korzysta z tego samego API `room` co wersja dla Claude i PeerJS:
   presence(patch), peers(), onPeers(cb), onConnection(cb), close(). */
window.PK = (() => {
  const CFG = window.PK_CONFIG || {};
  const TOPIC = "pk-live-v1-";
  let client = null;

  function configured() { return !!(CFG.supabaseUrl && CFG.supabaseAnonKey); }
  function sb() {
    if (client) return client;
    if (!configured() || !window.supabase || !window.supabase.createClient) return null;
    client = window.supabase.createClient(CFG.supabaseUrl, CFG.supabaseAnonKey, {
      auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
      realtime: { params: { eventsPerSecond: 40 } }
    });
    return client;
  }
  function whyOff() { return !configured() ? "noconfig" : "nolib"; }
  function uuid() {
    try { if (crypto.randomUUID) return crypto.randomUUID(); } catch (e) { }
    const b = new Uint8Array(16); crypto.getRandomValues(b); b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
    const h = [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  }
  function load(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { } }
  function merge(a, patch) { const o = Object.assign({}, a); for (const k in patch) { if (patch[k] === null) delete o[k]; else o[k] = patch[k]; } return o; }
  const isObj = (v) => !!v && typeof v === "object" && !Array.isArray(v);

  /* ---------- pokój gry Live ----------
     Kanał `pk-live-v1-<KOD>`. Presence mówi tylko, kto jest online (prowadzący `h-…`, gracze `p-…`).
     Stan gry płynie przez broadcast, gwiazdą jak w wersji PeerJS:
       host → wszyscy:  "host" {p}       pełny stan prowadzącego (po każdej zmianie i co 10 s)
       gracz → host:    "pres" {id, p}   presence gracza (po zmianie i co 10 s)
       gracz → host:    "hello"          prośba o stan (po wejściu, powrocie do karty)
     Kolejność wciśnięć: czas odebrania "pres" u prowadzącego (updatedAt), jak w pozostałych wersjach. */
  const BEAT_MS = 10000;

  function baseRoom() {
    const handlers = [], cbs = [];
    let online = false;
    return {
      handlers, cbs,
      get online() { return online; },
      status(v) { if (v === online) return; online = v; cbs.forEach((h) => { try { h(v); } catch (e) { } }); },
      fire(peers) { handlers.forEach((h) => { try { h({ peers, joined: [], left: [], updated: peers }); } catch (e) { console.error(e); } }); }
    };
  }
  function send(ch, event, payload) { try { const r = ch.send({ type: "broadcast", event, payload }); if (r && r.catch) r.catch(() => { }); } catch (e) { } }

  function hostRoom(code, hid) {
    return new Promise((resolve, reject) => {
      const c = sb(); if (!c) { reject(whyOff()); return; }
      const ch = c.channel(TOPIC + code, { config: { broadcast: { self: false }, presence: { key: hid } } });
      const B = baseRoom(), players = new Map();
      let mine = {}, settled = false, beat = null, synced = false;
      const snap = () => {
        const a = [{ peer: "me", isMe: true, sameTab: true, presence: mine, updatedAt: 0 }];
        players.forEach((v, k) => a.push({ peer: k, isMe: false, sameTab: false, presence: v.presence, updatedAt: v.updatedAt }));
        return a;
      };
      const fire = () => B.fire(snap());
      const sendHost = () => { if (B.online) send(ch, "host", { p: mine }); };
      const stop = () => { clearInterval(beat); beat = null; try { c.removeChannel(ch); } catch (e) { } };
      const fail = (why) => { if (settled) return; settled = true; stop(); reject(why); };
      const ok = () => { if (settled) return; settled = true; resolve(room); };

      ch.on("broadcast", { event: "pres" }, ({ payload }) => {
        if (!payload || typeof payload.id !== "string" || !payload.id.startsWith("p-") || !isObj(payload.p)) return;
        const j = JSON.stringify(payload.p), cur = players.get(payload.id), now = performance.now();
        if (cur && cur.json === j) { cur.seen = now; return; }
        players.set(payload.id, { presence: payload.p, json: j, updatedAt: now, seen: now, inPres: cur ? cur.inPres : false });
        fire();
      });
      ch.on("broadcast", { event: "hello" }, () => sendHost());
      ch.on("presence", { event: "sync" }, () => {
        const st = ch.presenceState() || {};
        if (!synced) {
          synced = true;
          const other = Object.keys(st).some((k) => k !== hid && k.startsWith("h-"));
          if (other) { fail("taken"); return; }
          ok();
        }
        let changed = false;
        const now = performance.now();
        players.forEach((v, k) => {
          if (st[k]) v.inPres = true;
          else if (v.inPres || now - v.seen > 3 * BEAT_MS) { players.delete(k); changed = true; }
        });
        if (changed) fire();
      });
      ch.on("presence", { event: "join" }, ({ key }) => { if (key !== hid) sendHost(); });

      ch.subscribe((s) => {
        if (s === "SUBSCRIBED") {
          B.status(true);
          ch.track({ role: "host" }).catch(() => { });
          sendHost();
          // brak sync po wejściu (np. wyłączone presence): nie blokuj prowadzącego
          setTimeout(() => { if (!synced) { synced = true; ok(); } }, 4000);
        } else if (s === "CHANNEL_ERROR" || s === "TIMED_OUT" || s === "CLOSED") {
          B.status(false);
          fail(s === "TIMED_OUT" ? "timeout" : "error");
        }
      });
      beat = setInterval(sendHost, BEAT_MS);
      setTimeout(() => fail("timeout"), 15000);

      const room = {
        presence: async (patch) => { mine = merge(mine, patch); sendHost(); },
        peers: snap,
        onPeers: (h) => { B.handlers.push(h); setTimeout(fire, 0); return () => { }; },
        onConnection: (h) => { B.cbs.push(h); setTimeout(() => h(B.online), 0); return () => { }; },
        close: () => { settled = true; stop(); B.status(false); }
      };
    });
  }

  function playerRoom(code) {
    return new Promise((resolve, reject) => {
      const c = sb(); if (!c) { reject(whyOff()); return; }
      const id = "p-" + uuid();
      const ch = c.channel(TOPIC + code, { config: { broadcast: { self: false }, presence: { key: id } } });
      const B = baseRoom();
      let mine = {}, host = null, hostAt = 0, settled = false, beat = null, noHostTimer = null, alive = true;
      const snap = () => {
        const a = [{ peer: "me", isMe: true, sameTab: true, presence: mine, updatedAt: 0 }];
        if (host) a.push({ peer: "host", isMe: false, sameTab: false, presence: host, updatedAt: hostAt });
        return a;
      };
      const fire = () => B.fire(snap());
      const sendPres = () => { if (B.online) send(ch, "pres", { id, p: mine }); };
      const hello = () => { if (B.online) { sendPres(); send(ch, "hello", {}); } };
      const onVis = () => { if (document.visibilityState === "visible") hello(); };
      const stop = () => { alive = false; clearInterval(beat); clearTimeout(noHostTimer); document.removeEventListener("visibilitychange", onVis); try { c.removeChannel(ch); } catch (e) { } };
      const fail = (why) => { if (settled) return; settled = true; stop(); reject(why); };
      const hostKeys = () => Object.keys(ch.presenceState() || {}).filter((k) => k.startsWith("h-"));

      ch.on("broadcast", { event: "host" }, ({ payload }) => {
        if (!payload || !isObj(payload.p)) return;
        host = payload.p; hostAt = performance.now();
        if (!settled) { settled = true; clearTimeout(noHostTimer); resolve(room); }
        fire();
      });
      ch.on("presence", { event: "sync" }, () => {
        const hk = hostKeys();
        if (!hk.length && host) { host = null; fire(); }
        if (hk.length && !host) hello();
      });

      ch.subscribe((s) => {
        if (!alive) return;
        if (s === "SUBSCRIBED") {
          B.status(true);
          ch.track({ role: "player" }).catch(() => { });
          hello();
          if (!settled && !noHostTimer) noHostTimer = setTimeout(() => { if (!hostKeys().length) fail("nogame"); }, 5000);
        } else if (s === "CHANNEL_ERROR" || s === "TIMED_OUT" || s === "CLOSED") {
          B.status(false);
          if (!settled) fail(s === "TIMED_OUT" ? "timeout" : "error");
        }
      });
      document.addEventListener("visibilitychange", onVis);
      beat = setInterval(sendPres, BEAT_MS);
      setTimeout(() => fail(hostKeys().length ? "timeout" : "nogame"), 15000);

      const room = {
        presence: async (patch) => { mine = merge(mine, patch); sendPres(); },
        peers: snap,
        onPeers: (h) => { B.handlers.push(h); setTimeout(fire, 0); return () => { }; },
        onConnection: (h) => { B.cbs.push(h); setTimeout(() => h(B.online), 0); return () => { }; },
        close: () => { settled = true; stop(); B.status(false); }
      };
    });
  }

  /* ---------- lista wyników ----------
     Gra trafia najpierw do kolejki w localStorage (`pk_outbox`), a potem do bazy.
     Nieudany zapis (brak sieci) zostaje w kolejce i jest ponawiany przy następnej okazji. */
  const OUTBOX = "pk_outbox";
  let flushing = null;
  function queue(game) {
    const box = load(OUTBOX, []).filter((g) => g && g.id !== game.id);
    box.push(game); save(OUTBOX, box.slice(-20));
  }
  function flush() {
    if (flushing) return flushing;
    flushing = (async () => {
      const c = sb(); if (!c) return { ok: false, why: whyOff() };
      let last = { ok: true };
      for (const g of load(OUTBOX, [])) {
        const { data, error } = await c.rpc("pk_submit_game", { p_game: g });
        // błąd walidacji (kod 22023) nie zniknie przy ponowieniu, więc taką grę też usuwamy z kolejki
        const final = !error || error.code === "22023";
        if (final) save(OUTBOX, load(OUTBOX, []).filter((x) => x && x.id !== g.id));
        // historia pytań dla nicków (dobór pytań); bez migracji 20261020090000 błąd jest pomijany
        if (!error && Array.isArray(g.qids) && g.qids.length) {
          try { await c.rpc("pk_mark_seen", { p_names: (g.players || []).map((p) => p && p.name), p_qids: g.qids }); } catch (e) { }
        }
        last = error ? { ok: false, why: error.code === "22023" ? "rejected" : "network", id: g.id, error } : { ok: true, id: g.id, data };
        if (!final) break;
      }
      return last;
    })().catch((e) => ({ ok: false, why: "network", error: e })).finally(() => { flushing = null; });
    return flushing;
  }
  function rememberNicks(names) {
    const c = load("pk_nicks", null), old = c && Array.isArray(c.list) ? c.list : [], low = new Set(names.map((n) => n.toLowerCase()));
    save("pk_nicks", { at: c ? c.at : 0, list: names.concat(old.filter((n) => !low.has(String(n).toLowerCase()))) });
  }
  async function submitGame(game) {
    try { rememberNicks((game.players || []).map((p) => String(p.name || "").trim()).filter(Boolean)); } catch (e) { }
    queue(game);
    const r = await flush();
    const left = load(OUTBOX, []).some((g) => g && g.id === game.id);
    return left ? { ok: false, why: r.why || "network", error: r.error } : r.id === game.id ? r : { ok: true };
  }
  async function rpc(name, args) {
    const c = sb(); if (!c) throw new Error(whyOff());
    const { data, error } = await c.rpc(name, args);
    if (error) throw error;
    return data || [];
  }
  const leaderboard = (o = {}) => rpc("pk_leaderboard", { p_level: o.level || null, p_mode: o.mode || null, p_days: o.days || null, p_limit: o.limit || 100 });
  const recentGames = (o = {}) => rpc("pk_recent_games", { p_limit: o.limit || 20, p_name: o.name || null });
  /* Ile razy i jak niedawno te nicki widziały pytania: {qid: ogranie}, dla setQHist w mix.js. Bez bazy: {}. */
  async function history(names) {
    const list = (names || []).map((n) => String(n || "").trim()).filter(Boolean).slice(0, 16);
    if (!list.length || !sb()) return {};
    try { const h = await rpc("pk_history", { p_names: list }); return h && typeof h === "object" && !Array.isArray(h) ? h : {}; } catch (e) { return {}; }
  }
  /* Rejestr nicków: każdy nick, który choć raz zagrał (z listy wyników, ostatnio grający najpierw).
     Kopia w pk_nicks odświeża się co 2 minuty (bez sieci podpowiedzi biorą się z niej), a nicki z gier
     zapisanych na tym telefonie trafiają do niej od razu. */
  async function nicks() {
    const c = load("pk_nicks", null), fresh = c && Array.isArray(c.list) && Date.now() - c.at < 2 * 60 * 1000;
    if (fresh || !sb()) return c && Array.isArray(c.list) ? c.list : [];
    try {
      const list = (await leaderboard({ limit: 500 })).slice().sort((a, b) => String(b.last_played).localeCompare(String(a.last_played))).map((r) => r.name);
      save("pk_nicks", { at: Date.now(), list }); return list;
    } catch (e) { return c && Array.isArray(c.list) ? c.list : []; }
  }

  if (configured()) setTimeout(() => { if (load(OUTBOX, []).length) flush(); }, 1500);
  window.addEventListener("online", () => { if (load(OUTBOX, []).length) flush(); });

  return { configured, ready: () => !!sb(), whyOff, uuid, hostRoom, playerRoom, submitGame, flush, leaderboard, recentGames, nicks, history };
})();
