"""Zamienia wersję Live dla Claude w samodzielną stronę bez logowania.

  make_web(src)                    PeerJS (bezpośrednie połączenia telefonów, publiczny broker)
  make_web(src, flavor="supabase") Supabase Realtime + zapis wyników do listy wyników
"""
import os
_DIR = os.path.dirname(os.path.abspath(__file__))
_STEPS = os.path.join(_DIR, 'web_transform_steps.py')

def make_web(src, flavor='peer'):
    g = {'src': src, '__name__': 'web_transform_steps', 'FLAVOR': flavor, 'STEPS_DIR': _DIR}
    exec(compile(open(_STEPS, encoding='utf-8').read(), _STEPS, 'exec'), g)
    return g['doc']
