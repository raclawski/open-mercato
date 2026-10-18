#!/usr/bin/env python3
"""Buduje wszystkie wersje gry z src/ do dist/.

  python3 tools/build.py

Wynik:
  dist/teleturniej.html          treść artefaktu Claude (bez <!doctype>, Artifact sam dokłada szkielet)
  dist/teleturniej-standalone.html  ta sama gra jako zwykła strona do hostowania
  dist/live-claude.html          treść artefaktu Claude z przyciskami (capability room)
  dist/live-web/index.html       Live bez logowania (PeerJS), do wrzucenia na hosting
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from web_transform import make_web

def rd(p): return open(os.path.join(ROOT, p), encoding='utf-8').read()
def wr(p, s):
    full = os.path.join(ROOT, p); os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(s); print('  ', p, f'({len(s)//1024} KB)')

order = [l.strip() for l in rd('src/questions/ORDER.txt').splitlines() if l.strip()]
banks = '\n\n'.join(rd('src/questions/' + f).strip() for f in order) + '\n\n'
names = re.findall(r'const (BANK_\w+) = ', banks)
assert len(names) == len(order), 'każdy plik w src/questions musi definiować dokładnie jedną stałą BANK_*'

def fill(tpl):
    t = rd('src/templates/' + tpl)
    assert t.count('/*__BANKS__*/') == 1, tpl
    out = t.replace('/*__BANKS__*/', banks)
    for n in names:
        assert re.search(r'bank:\s*' + n + r'\b', out), f'{tpl}: brak wpisu w LEVELS dla {n}'
    return out

print('Buduję:')
tv = fill('teleturniej.html'); wr('dist/teleturniej.html', tv)
STANDALONE_HEAD = ('<!doctype html>\n<html lang="pl">\n<head>\n<meta charset="utf-8">\n'
  '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
  '<style>[hidden]{display:none!important}html{color-scheme:light}body{margin:0}'
  ':root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}</style>\n')
i = tv.index('</style>') + len('</style>')
wr('dist/teleturniej-standalone.html', STANDALONE_HEAD + tv[:i] + '\n</head>\n<body>\n' + tv[i:] + '\n</body>\n</html>\n')
lv = fill('live-claude.html'); wr('dist/live-claude.html', lv)
wr('dist/live-web/index.html', make_web(lv))
print('Gotowe.')
