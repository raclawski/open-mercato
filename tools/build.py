#!/usr/bin/env python3
"""Buduje wszystkie wersje gry z src/ do dist/.

  python3 tools/build.py

Wynik:
  dist/teleturniej.html          treść artefaktu Claude (bez <!doctype>, Artifact sam dokłada szkielet)
  dist/teleturniej-standalone.html  ta sama gra jako zwykła strona do hostowania
  dist/live-claude.html          treść artefaktu Claude z przyciskami (capability room)
  dist/live-web/index.html       Live bez logowania (PeerJS), do wrzucenia na hosting
  dist/web/                      serwis na Vercel: Live na Supabase, teleturniej i lista wyników
"""
import json, os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from web_transform import make_web
from web_pages import make_tv_web, level_labels

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
    for mark, part in (('/*__DRUM_CSS__*/', 'drum.css'), ('/*__DRUM_JS__*/', 'drum.js'), ('/*__MIX_JS__*/', 'mix.js')):
        assert out.count(mark) == 1, (tpl, mark)
        out = out.replace(mark, rd('src/templates/shared/' + part).strip())
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
tv_doc = STANDALONE_HEAD + tv[:i] + '\n</head>\n<body>\n' + tv[i:] + '\n</body>\n</html>\n'
wr('dist/teleturniej-standalone.html', tv_doc)
lv = fill('live-claude.html'); wr('dist/live-claude.html', lv)
wr('dist/live-web/index.html', make_web(lv))

# --- serwis na Vercel (dist/web) ---
labels = level_labels(rd('src/templates/teleturniej.html'))
assert labels == level_labels(rd('src/templates/live-claude.html')), 'LEVELS różnią się między szablonami'
n_questions = sum(len(re.findall(r'^\s*\{ q: "', rd('src/questions/' + f), re.M)) for f in order)
wr('dist/web/live.html', make_web(lv, flavor='supabase'))
wr('dist/web/teleturniej.html', make_tv_web(tv_doc))
wr('dist/web/wyniki.html', rd('src/web/wyniki.html').replace('/*__LEVEL_LABELS__*/{}', json.dumps(labels, ensure_ascii=False)))
wr('dist/web/index.html', rd('src/web/index.html').replace('/*__QUESTION_COUNT__*/', str(n_questions)).replace('/*__LEVEL_COUNT__*/', str(len(labels))))
for f in ('pk-online.js', 'site.css'):
    wr('dist/web/' + f, rd('src/web/' + f))
url, key = os.environ.get('SUPABASE_URL', ''), os.environ.get('SUPABASE_ANON_KEY', '')
wr('dist/web/config.js', '// Wygenerowane przez tools/build.py ze zmiennych środowiskowych.\nwindow.PK_CONFIG = '
   + json.dumps({'supabaseUrl': url, 'supabaseAnonKey': key}, indent=2) + ';\n' if url and key else rd('src/web/config.js'))
# supabase-js z node_modules (npm install); bez node_modules zostaje kopia z repozytorium
lib = os.path.join(ROOT, 'node_modules/@supabase/supabase-js/dist/umd/supabase.js')
if os.path.exists(lib):
    os.makedirs(os.path.join(ROOT, 'dist/web/vendor'), exist_ok=True)
    shutil.copyfile(lib, os.path.join(ROOT, 'dist/web/vendor/supabase.js')); print('   dist/web/vendor/supabase.js')
assert os.path.exists(os.path.join(ROOT, 'dist/web/vendor/supabase.js')), 'brak dist/web/vendor/supabase.js: uruchom npm install'
print('Gotowe.')
