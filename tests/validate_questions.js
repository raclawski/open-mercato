// Sprawdza strukturę wszystkich pul pytań: node tests/validate_questions.js
const fs = require('fs'), path = require('path');
const dir = path.join(__dirname, '..', 'src', 'questions');
const order = fs.readFileSync(path.join(dir, 'ORDER.txt'), 'utf8').split('\n').map((s) => s.trim()).filter(Boolean);
let errors = 0, total = 0;
const seenQ = new Map();
const norm = (t) => String(t).toLowerCase().replace(/[^0-9a-ząćęłńóśźż]+/g, ' ').trim();
for (const f of order) {
  const src = fs.readFileSync(path.join(dir, f), 'utf8');
  const name = (src.match(/const (BANK_\w+) = /) || [])[1];
  if (!name) { console.log(`✗ ${f}: brak "const BANK_... = "`); errors++; continue; }
  const bank = new Function(src + `;return ${name};`)();
  let n = 0;
  bank.forEach((cat) => {
    if (!cat.name || !Array.isArray(cat.q)) { console.log(`✗ ${f}: kategoria bez name/q`); errors++; return; }
    cat.q.forEach((q, i) => {
      n++;
      const where = `${f} › ${cat.name} › #${i + 1}`;
      if (!q.q || !q.e) { console.log(`✗ ${where}: brak pytania (q) albo wyjaśnienia (e)`); errors++; }
      if (!Array.isArray(q.o) || q.o.length !== 4) { console.log(`✗ ${where}: musi mieć 4 odpowiedzi`); errors++; }
      else if (new Set(q.o).size !== 4) { console.log(`✗ ${where}: powtórzona odpowiedź`); errors++; }
      if (!(Number.isInteger(q.c) && q.c >= 0 && q.c < 4)) { console.log(`✗ ${where}: c musi być 0–3`); errors++; }
      if (q.q && !/[?…:]$/.test(q.q.trim())) { console.log(`✗ ${where}: pytanie powinno kończyć się „?”`); errors++; }
      if (q.q) { const k = norm(q.q); if (seenQ.has(k)) { console.log(`✗ ${where}: to samo pytanie co ${seenQ.get(k)}`); errors++; } else seenQ.set(k, where); }
    });
  });
  total += n;
  console.log(`✓ ${f.padEnd(20)} ${name.padEnd(10)} ${String(n).padStart(3)} pytań w ${bank.length} działach`);
}
console.log(`Razem: ${total} pytań. Błędy: ${errors}.`);
process.exit(errors ? 1 : 0);
