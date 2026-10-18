# CLAUDE.md: wskazówki do pracy nad projektem

Projekt: teleturniej „Postaw Krzyżyk” po polsku, w kilku wersjach z jednego źródła. Główny cel to serwis na Vercel + Supabase (`dist/web`): gra Live przez serwer i lista wyników. Pełny opis gry, historia i znane ograniczenia: `PODSUMOWANIE.md`. Komunikacja z użytkownikiem po polsku.

## Struktura

```
src/questions/*.js        pule pytań, każdy plik definiuje jedną stałą `const BANK_XXX = [...]`
src/questions/ORDER.txt   kolejność wklejania plików do szablonów
src/templates/teleturniej.html   gra na jednym telefonie (bez zależności)
src/templates/live-claude.html   gra z przyciskami przez capability `room` artefaktów Claude
tools/build.py            składa dist/ z src/
tools/web_transform*.py   zamienia live-claude w wersję bez logowania (PeerJS albo Supabase)
tools/supabase_transform_steps.py  kroki tylko dla wersji Supabase (transport, zapis wyniku)
tools/web_pages.py        teleturniej z zapisem wyniku, etykiety kategorii dla listy wyników
tools/write-config.mjs    Vercel: config.js ze zmiennych SUPABASE_URL i SUPABASE_ANON_KEY
src/web/                  serwis: index.html, wyniki.html, pk-online.js (Supabase), site.css, config.js
supabase/migrations/      baza wyników (tabele, RLS, funkcje RPC)
tests/                    walidacja pytań, testy rozgrywki w Playwright, testy SQL
vercel.json               hosting: katalog dist/web, cleanUrls
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
npm test                            # wszystko po kolei (bez Supabase)
PK_TEST_PGURL=postgresql://… npm run test:sql   # funkcje rankingu na prawdziwym Postgresie
PK_TEST_PGURL=postgresql://… npm run test:web   # serwis dist/web: Live, teleturniej, lista wyników
```

Testy wymagają Pythona z pakietem `playwright` (`pip install playwright && playwright install chromium`) i Node. `PK_TEST_PGURL` to Postgres z prawami superużytkownika: `test:web` zakłada na nim tymczasową bazę i ją usuwa, `test:sql` wgrywa migrację do wskazanej bazy (użyj testowej). `test:web` korzysta z prawdziwego supabase-js, a Realtime i RPC emuluje `tests/fake_supabase.py` (protokół Phoenix na przechwyconym WebSockecie, RPC przez psql jako rola anon).

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

`build.py` przerywa, jeśli w szablonie brakuje wpisu `LEVELS` dla któregoś `BANK_*`. Lista wyników bierze etykiety kategorii z `LEVELS`, więc nic więcej nie trzeba dopisywać. Klucz kategorii musi pasować do `^[a-z]{2,12}$` (sprawdza to baza).

## Zasady treści

- Fakty muszą być pewne. Wszystko z ostatnich lat (wyniki, kto pełni funkcję, nowe przepisy) sprawdź w sieci przed dodaniem. Unikaj pytań, które zdezaktualizują się przy najbliższej zmianie władzy, chyba że są jawnie datowane.
- Nie cytuj tekstów piosenek, wierszy ani fragmentów książek. Pytaj o tytuły, daty i fakty.
- Kategoria „Używki” to historia, chemia, kultura i prawo. Bez dawkowania, sposobów pozyskania czy wytwarzania.
- Styl: proste, krótkie zdania po polsku, polskie cudzysłowy „…”, minus jako „−” przy punktach.

## Publikacja

- **Serwis (główny)**: Vercel z `dist/web`, dane w Supabase. Instrukcja krok po kroku: `WDROZENIE.md`. `dist/web` jest w repozytorium, Vercel tylko generuje `config.js`, więc po zmianach zawsze uruchom `python3 tools/build.py` i zrób commit wyniku.

- Artefakty Claude:
  - teleturniej: https://claude.ai/artifact/Je7ndn81PYiKodds6YGnW9 (publikuj `dist/teleturniej.html`),
  - Live: https://claude.ai/artifact/UGowZNmDKDReG99ZDPR2WE (publikuj `dist/live-claude.html` z `capabilities: {room: {}}`; ponowna publikacja bez `capabilities` zachowuje zapisane).
  - Aktualizacja pod tym samym linkiem wymaga narzędzia Artifact z parametrem `url` i wcześniejszego odczytu (`action: "read"`).
- Wersja bez logowania: wrzuć `dist/live-web/index.html` na hosting statyczny. Strona ładuje PeerJS 1.5.4 z unpkg i łączy się z publicznym brokerem PeerJS. Własny broker: przed skryptem gry ustaw `window.PK_PEER_OPTS = { host, port, path, secure }`.

## Ważne szczegóły implementacji

- `localStorage`: `pk_tv2` (ustawienia teleturnieju), `pk_seen` (wylosowane już pytania, wspólne dla wersji), `pkl_*` (Live: rola, imię, stan prowadzącego), `pkw_*` (kod gry, identyfikator prowadzącego), `pk_outbox` (gry czekające na zapis), `pk_board` (filtry listy wyników). Dostęp zawsze w `try/catch`.
- Live w Claude: stan gry siedzi w `presence` prowadzącego (`role: "host"`, faza, numer pytania, `arm`, zwycięzca, zablokowani, wyniki; poprawna odpowiedź dopiero po odkryciu). Gracze ustawiają `presence` `{role: "player", name, buzz, fs}`. O kolejności decyduje `updatedAt` po stronie prowadzącego. Bez `db`, bez topiców.
- Wersja PeerJS emuluje to samo API `room` (presence, peers, onPeers, onConnection). Prowadzący to peer `postaw-krzyzyk-live-v1-<KOD>`, gracze łączą się z nim gwiazdą.
- Wersja Supabase (`src/web/pk-online.js`) emuluje to samo API na kanale Realtime `pk-live-v1-<KOD>`. Presence mówi tylko, kto jest online (klucze `h-…` prowadzący, `p-…` gracze). Stan płynie broadcastem: `host` (pełny stan prowadzącego, po zmianie i co 10 s), `pres` (presence gracza), `hello` (prośba o stan). Kolejność wciśnięć: czas odebrania `pres` u prowadzącego. Identyfikator prowadzącego `pkw_hid` jest stały na urządzeniu, więc po odświeżeniu wraca do tego samego kodu. Kod zajęty przez innego prowadzącego jest losowany od nowa.
- Jedna gra w serwisie: tryb wybiera się na stronie startowej (`index.html`): „Jeden telefon” → `teleturniej.html`, „Przyciski na telefonach” → `live.html?tryb=prowadzacy` (od razu ustawienia prowadzącego albo powrót do trwającej gry), „Mam kod gry” → `live.html?tryb=gracz`. Link dla graczy to nadal `live.html?kod=XXXX`, a `live.html` bez parametrów wraca do wyboru trybu. Poziom, liczba pytań i kara są wspólne dla obu trybów (`pk_common` w `localStorage`).
- Lista wyników: każda gra ma `uid`. Po końcu gry prowadzący (Live) albo telefon (teleturniej) wysyła ją przez `PK.submitGame`: najpierw kolejka `pk_outbox` w `localStorage`, potem RPC `pk_submit_game`. Nieudany zapis ponawia się przy następnym wejściu na dowolną stronę serwisu. Zapis jest idempotentny po `uid`. Ranking łączy gry po nicku bez względu na wielkość liter.
- Motyw: tokeny CSS w `:root` z wariantem ciemnym (`prefers-color-scheme` i `[data-theme]`). Fonty Archivo, IBM Plex Sans i IBM Plex Mono z Google Fonts.
