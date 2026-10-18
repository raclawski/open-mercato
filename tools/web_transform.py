"""Zamienia wersję Live dla Claude w samodzielną stronę na PeerJS (bez logowania)."""
import os
_STEPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web_transform_steps.py')

def make_web(src):
    g = {'src': src, '__name__': 'web_transform_steps'}
    exec(compile(open(_STEPS, encoding='utf-8').read(), _STEPS, 'exec'), g)
    return g['doc']
