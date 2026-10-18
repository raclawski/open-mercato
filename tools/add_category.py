#!/usr/bin/env python3
"""Dodaje kategorię do gry: wpis w LEVELS i wiersz bębna w obu szablonach oraz plik w ORDER.txt.

  python3 tools/add_category.py KLUCZ PLIK.js BANK_NAZWA "Etykieta" "Opis pod bębnem." [--after KLUCZ]

Plik z pytaniami (src/questions/PLIK.js) musi już istnieć. Skrypt nic nie zmienia, jeśli kategoria jest już dodana.
"""
import argparse, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = ['src/templates/teleturniej.html', 'src/templates/live-claude.html']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('key'); ap.add_argument('file'); ap.add_argument('bank'); ap.add_argument('label'); ap.add_argument('hint')
    ap.add_argument('--after', help='klucz kategorii, po której wstawić (domyślnie na końcu)')
    a = ap.parse_args()
    assert re.fullmatch(r'[a-z]{2,12}', a.key), 'klucz: 2–12 małych liter (wymóg bazy wyników)'
    assert re.fullmatch(r'BANK_[A-Z0-9_]+', a.bank), 'nazwa stałej: BANK_…'
    qpath = os.path.join(ROOT, 'src/questions', a.file)
    assert os.path.exists(qpath), f'brak pliku {qpath}'
    assert f'const {a.bank} = ' in open(qpath, encoding='utf-8').read(), f'{a.file} nie definiuje {a.bank}'
    js = lambda s: s.replace('\\', '\\\\').replace('"', '\\"')
    for t in TEMPLATES:
        p = os.path.join(ROOT, t); s = open(p, encoding='utf-8').read()
        if re.search(r'^\s*' + a.key + r': \{ label:', s, re.M):
            print(f'  {t}: {a.key} już jest'); continue
        entry = f'  {a.key}: {{ label: "{js(a.label)}", bank: {a.bank}, hint: "{js(a.hint)}" }},\n'
        button = f'            <button type="button" data-v="{a.key}" class="hotbtn">{a.label}</button>\n'
        block_start = s.index('const LEVELS = {\n'); block_end = s.index('\n};', block_start) + 1
        if a.after:
            m = re.search(r'^  ' + a.after + r': \{ label:[^\n]*\n', s[block_start:block_end], re.M); assert m, f'brak {a.after} w LEVELS'
            i = block_start + m.end()
            bm = re.search(r'^            <button type="button" data-v="' + a.after + r'"[^\n]*\n', s, re.M); assert bm
            bi = bm.end()
        else:
            i = block_end
            prev = s.rindex('\n', block_start, i - 1)  # ostatni wpis musi kończyć się przecinkiem
            if not s[prev:i].rstrip().endswith(','):
                s = s[:i - 1] + ',' + s[i - 1:]; i += 1
            drum = s.index('id="levelSeg">'); bi = s.index('          </div>', drum)
        if bi > i:
            s = s[:bi] + button + s[bi:]; s = s[:i] + entry + s[i:]
        else:
            s = s[:i] + entry + s[i:]; s = s[:bi] + button + s[bi:]
        open(p, 'w', encoding='utf-8').write(s); print(f'  {t}: dodano {a.key}')
    order = os.path.join(ROOT, 'src/questions/ORDER.txt')
    lines = [l.strip() for l in open(order, encoding='utf-8') if l.strip()]
    if a.file not in lines:
        lines.append(a.file); open(order, 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print(f'  ORDER.txt: dodano {a.file}')

if __name__ == '__main__':
    main()
