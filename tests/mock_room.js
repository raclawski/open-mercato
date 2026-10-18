// Atrapa capability `room` z Claude do testów lokalnych: łączy karty jednej przeglądarki przez BroadcastChannel.
(() => {
  try { localStorage.removeItem("pkl_role"); localStorage.removeItem("pkl_host"); } catch (e) {}
  const id = Math.random().toString(36).slice(2, 10);
  const bc = new BroadcastChannel('mockroom');
  const state = new Map(); let mine = {}; const handlers = [];
  state.set(id, { presence: {}, updatedAt: Date.now() });
  const snapshot = () => [...state.entries()].map(([peer, v]) => Object.freeze({ peer, by: null, isMe: peer === id, sameTab: peer === id, kind: 'viewer', guest: false, presence: v.presence, updatedAt: v.updatedAt }));
  const fire = () => { const peers = snapshot(); handlers.forEach((h) => h({ peers, joined: [], left: [], updated: peers })); };
  bc.onmessage = (e) => { const { peer, presence, hello } = e.data; if (hello) bc.postMessage({ peer: id, presence: mine }); state.set(peer, { presence, updatedAt: Date.now() }); fire(); };
  const room = {
    presence: async (patch) => { mine = Object.assign({}, mine); for (const k in patch) { if (patch[k] === null) delete mine[k]; else mine[k] = patch[k]; } state.set(id, { presence: mine, updatedAt: Date.now() }); bc.postMessage({ peer: id, presence: mine }); fire(); },
    peers: () => snapshot(),
    onPeers: (h) => { handlers.push(h); setTimeout(fire, 0); return () => {}; },
    onConnection: (h) => { setTimeout(() => h(true), 0); return () => {}; },
    connected: () => true,
  };
  bc.postMessage({ peer: id, presence: mine, hello: true });
  window.claude = { use: async (n) => (n === 'room' ? room : null) };
})();
