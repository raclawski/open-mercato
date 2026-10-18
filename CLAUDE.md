# CLAUDE.md: wskazówki do pracy nad projektem

Projekt: teleturniej „Postaw Krzyżyk” po polsku, w trzech wersjach z jednego źródła. Pełny opis gry, historia i znane ograniczenia: `PODSUMOWANIE.md`. Komunikacja z użytkownikiem po polsku.

## Struktura

```
src/questions/*.js        pule pytań, każdy plik definiuje jedną stałą `const BANK_XXX = [...]`
src/questions/ORDER.txt   kolejność wklejania plików do szablonów
src/templates/teleturniej.html   gra na jednym telefonie (bez zależności)
src/templates/live-claude.html   gra z przyciskami przez capability `room` artefaktów Claude
tools/build.py            składa dist/ z src/
tools/web_transform*.py   zamienia live-claude w wersję bez logowania (PeerJS)
tests/                    walidacja pytań i testy rozgrywki w Playwright
dist/                     wynik buildu, nie edytuj ręcznie
```

Szablony to pojedyncze pliki HTML+CSS+JS bez frameworka. Miejsce na pytania to znacznik `/*__BANKS__*/`. Szablony nie mają `<!doctype>`, `<html>`, `<head>` ani `<body>`, bo publikacja jako artefakt Claude sama dokłada szkielet. `build.py` robi z nich też pełne strony do hostingu.

## Polecenia

```bash
python3 tools/build.py              # buduje dist/
node tests/validate_questions.js    # struktura wszystkich pytań
python3 tests/smoke_teleturniej.py  # rozgrywa 20 pytań na każdym poziomie
python3 tests/smoke_live_claude.py  # prowadzący + 3 graczy na atrapie room (tests/mock_room.js)
npm install && python3 tests/smoke_live_web.py   # wersja PeerJS na lokalnym serwerze peer
npm test                            # wszystko po kolei
```

Testy wymagają Pythona z pakietem `playwright` (`pip install playwright && playwright install chromium`) i Node.

## Format pytania

```js
{ q: "Treść pytania?", o: ["A", "B", "C", "D"], c: 2, fix: 1, e: "Wyjaśnienie po odpowiedzi." }
```

- `o`: zawsze 4 różne odpowiedzi. `c`: indeks poprawnej (0–3).
- `fix: 1`: nie mieszaj kolejności odpowiedzi (liczby, daty, progresje). Bez `fix` odpowiedzi są tasowane.
- `e`: 1–2 zdania, krótko i rzeczowo. Wyjaśnia, dlaczego to ta odpowiedź, i często, czym różnią się mylące opcje.
- Kategoria to `{ name: "Dział", q: [...] }`. Pula to tablica 3–4 takich działów.

## Jak dodać nową kategorię

1. Utwórz `src/questions/nazwa.js` z `const BANK_NAZWA = [...]` i dopisz plik na końcu `ORDER.txt`.
2. W **obu** szablonach (`teleturniej.html` i `live-claude.html`):
   - dopisz wpis w obiekcie `LEVELS`: `klucz: { label: "Etykieta", bank: BANK_NAZWA, hint: "Opis pod przyciskami." }`,
   - dopisz przycisk w `#levelSeg`: `<button type="button" data-v="klucz" class="hotbtn">Etykieta</button>`. Siatka ma 2 kolumny. Przy nieparzystej liczbie przycisków ostatni dostaje klasę `wide` (pełna szerokość).
3. `node tests/validate_questions.js && python3 tools/build.py && python3 tests/smoke_teleturniej.py`.

`build.py` przerywa, jeśli w szablonie brakuje wpisu `LEVELS` dla któregoś `BANK_*`.

## Zasady treści

- Fakty muszą być pewne. Wszystko z ostatnich lat (wyniki, kto pełni funkcję, nowe przepisy) sprawdź w sieci przed dodaniem. Unikaj pytań, które zdezaktualizują się przy najbliższej zmianie władzy, chyba że są jawnie datowane.
- Nie cytuj tekstów piosenek, wierszy ani fragmentów książek. Pytaj o tytuły, daty i fakty.
- Kategoria „Używki” to historia, chemia, kultura i prawo. Bez dawkowania, sposobów pozyskania czy wytwarzania.
- Styl: proste, krótkie zdania po polsku, polskie cudzysłowy „…”, minus jako „−” przy punktach.

## Publikacja

- Artefakty Claude:
  - teleturniej: https://claude.ai/artifact/Je7ndn81PYiKodds6YGnW9 (publikuj `dist/teleturniej.html`),
  - Live: https://claude.ai/artifact/UGowZNmDKDReG99ZDPR2WE (publikuj `dist/live-claude.html` z `capabilities: {room: {}}`; ponowna publikacja bez `capabilities` zachowuje zapisane).
  - Aktualizacja pod tym samym linkiem wymaga narzędzia Artifact z parametrem `url` i wcześniejszego odczytu (`action: "read"`).
- Wersja bez logowania: wrzuć `dist/live-web/index.html` na hosting statyczny. Strona ładuje PeerJS 1.5.4 z unpkg i łączy się z publicznym brokerem PeerJS. Własny broker: przed skryptem gry ustaw `window.PK_PEER_OPTS = { host, port, path, secure }`.

## Ważne szczegóły implementacji

- `localStorage`: `pk_tv2` (ustawienia teleturnieju), `pk_seen` (wylosowane już pytania, wspólne dla wersji), `pkl_*` (Live: rola, imię, stan prowadzącego), `pkw_*` (kod gry w wersji PeerJS). Dostęp zawsze w `try/catch`.
- Live w Claude: stan gry siedzi w `presence` prowadzącego (`role: "host"`, faza, numer pytania, `arm`, zwycięzca, zablokowani, wyniki; poprawna odpowiedź dopiero po odkryciu). Gracze ustawiają `presence` `{role: "player", name, buzz, fs}`. O kolejności decyduje `updatedAt` po stronie prowadzącego. Bez `db`, bez topiców.
- Wersja PeerJS emuluje to samo API `room` (presence, peers, onPeers, onConnection). Prowadzący to peer `postaw-krzyzyk-live-v1-<KOD>`, gracze łączą się z nim gwiazdą.
- Motyw: tokeny CSS w `:root` z wariantem ciemnym (`prefers-color-scheme` i `[data-theme]`). Fonty Archivo, IBM Plex Sans i IBM Plex Mono z Google Fonts.
