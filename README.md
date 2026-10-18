# Postaw Krzyżyk

**Graj: https://krzyzyk.vercel.app**

Teleturniej na telefon: polityka, prawo, popkultura. 397 pytań w 8 kategoriach. Serwis na Vercel + Supabase z grą Live przez serwer i listą wyników.

- Opis gry, historia projektu i stan weryfikacji: [PODSUMOWANIE.md](PODSUMOWANIE.md)
- Praca nad kodem (struktura, build, testy, dodawanie kategorii): [CLAUDE.md](CLAUDE.md)
- Wdrożenie na Supabase i Vercel: [WDROZENIE.md](WDROZENIE.md)

## Szybki start

```bash
python3 tools/build.py                 # dist/ z src/
open dist/teleturniej-standalone.html  # gra na jednym telefonie
```

Gotowe pliki są już w `dist/`:

- `dist/web/`: serwis do wdrożenia na Vercel (strona startowa, gra Live, teleturniej, lista wyników),
- `dist/teleturniej-standalone.html`: gra na jednym telefonie, do otwarcia w przeglądarce albo wrzucenia na hosting,
- `dist/live-web/index.html`: wersja z przyciskami na telefonach, bez logowania (wymaga hostingu, np. Netlify Drop albo GitHub Pages),
- `dist/teleturniej.html` i `dist/live-claude.html`: treść artefaktów Claude.
