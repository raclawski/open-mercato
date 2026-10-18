# Postaw Krzyżyk: podsumowanie projektu

Teleturniej na telefon z pytaniami o polityce, prawie i popkulturze. Zaczęło się od prostego pub quizu, a skończyło na grze z przyciskami na telefonach graczy. Stan na 18 października 2026.

## Wersje gry

| Wersja | Gdzie działa | Kto może grać | Plik w projekcie |
|---|---|---|---|
| **Teleturniej** (jeden telefon prowadzącego) | Artefakt Claude: https://claude.ai/artifact/Je7ndn81PYiKodds6YGnW9 | Właściciel i osoby, którym go udostępniono (albo każdy, jeśli włączysz publiczny link) | `dist/teleturniej.html`, wersja do hostingu: `dist/teleturniej-standalone.html` |
| **Live w Claude** (przyciski na telefonach) | Artefakt Claude z capability `room`: https://claude.ai/artifact/UGowZNmDKDReG99ZDPR2WE | Tylko zalogowani w Claude, którym udostępniono stronę. Z publicznego linku pokazuje „Brak połączenia z grą” | `dist/live-claude.html` |
| **Live bez logowania** | Dowolny hosting statyczny (Netlify, GitHub Pages) | Każdy z linkiem i kodem gry | `dist/live-web/index.html` |
| **Serwis online** (Live przez serwer, teleturniej, lista wyników) | https://krzyzyk.vercel.app (Vercel + Supabase, instrukcja: `WDROZENIE.md`) | Każdy z linkiem; wyniki pod nickiem, bez logowania | `dist/web/` |

## Zasady gry

### Teleturniej (jeden telefon)

- Na pytanie odpowiada jedna wskazana osoba. Jej imię jest na ciemnej tabliczce nad pytaniem.
- **Dobra odpowiedź: +10 pkt.** Ta osoba wskazuje, kto odpowiada następny: innego gracza albo siebie. Bez wskazania nie da się przejść dalej.
- **Zła odpowiedź albo koniec czasu: −1 pkt** (domyślnie, do wyboru −1, −5, −10). Pytanie przechodzi do następnej osoby w kolejce, a prowadzący może wskazać kogoś innego.
- Ustawienia na starcie: poziom pytań, gracze (domyślnie Adam, Zając, Asia, Tomek, Julia), kto zaczyna (albo losowo), liczba pytań (20, 30, 40, 50), czas na odpowiedź (10, 15, 20 s albo bez limitu).
- Na koniec: pieczątka ze zwycięzcą, klasyfikacja z bilansem dobrych i złych odpowiedzi, przebieg gry pytanie po pytaniu, przyciski „Rewanż” i „Kopiuj wyniki”.

### Live (przyciski)

- Prowadzący czyta pytanie i wciska „Sygnał!”. Na telefonach graczy przycisk robi się czerwony („TERAZ!”).
- Kto pierwszy wciśnie, odpowiada na głos. O kolejności decyduje to, które wciśnięcie pierwsze dotarło do telefonu prowadzącego.
- Wciśnięcie przed sygnałem to falstart i blokada w tym pytaniu.
- Prowadzący ocenia: „Dobrze +10” albo „Źle −1”. Po złej odpowiedzi może dać sygnał pozostałym („odbicie”) albo odkryć odpowiedź.
- Tylko prowadzący widzi poprawną odpowiedź przed odkryciem (da się wyłączyć). Gracze widzą pytanie, odpowiedzi i wyniki na żywo.
- W wersji bez logowania prowadzący dostaje 4-literowy kod gry i link dla graczy (`?kod=XXXX`).

## Kategorie (poziomy pytań)

Razem **444 pytania**. Każda gra losuje pytania, najpierw te, których jeszcze nie było (pamięć w `localStorage`).

| Przycisk | Plik | Pytań | Zawartość |
|---|---|---|---|
| Umiarkowany | `umiarkowany.js` | 61 | Ustrój RP, historia polityczna, świat i instytucje, społeczeństwo |
| Mega | `mega.js` | 62 | Te same działy, poziom artykułów Konstytucji, traktatów i teorii |
| Ekspert PL | `ekspert-pl.js` | 69 | Tylko polska polityka: wybory, rządy III RP, PRL i II RP, ustrój i prawo |
| Popkultura PL | `popkultura-pl.js` | 44 | Polska popkultura 2010–2026: muzyka i Eurowizja, film i seriale, internet i gry, sport |
| Jaki to urząd? | `jaki-to-urzad.js` | 41 | Opis kompetencji, a gracze rozpoznają urząd: organy naczelne, sądy i kontrola, urzędy i służby, samorząd i UE |
| Używki | `uzywki.js` | 47 | Bardzo trudne: alkohol, nikotyna i kofeina, historia narkotyków, polskie prawo. Historia, chemia i kultura, bez instrukcji użycia |
| Prawo spółek | `prawo-spolek.js` | 37 | KSH: spółki osobowe, sp. z o.o., S.A. i P.S.A., KRS i różności |
| Jaki to wydział? | `jaki-to-wydzial.js` | 47 | Poziom niżej niż „Jaki to urząd?”: wydziały, biura, izby i jednostki urzędów. Parlament, prezydent i rząd, sądy i rejestry, służby, skarbówka i IPN, sprawy obywatela |
| Taylor Swift | `taylor-swift.js` | 36 | Albumy, rekordy i nagrody, biznes i prawa do nagrań, życie i fani. Bez cytowania tekstów piosenek |

## Historia zmian

1. Pub quiz na telefon: polityka i społeczeństwo, poziom umiarkowany, 4 rundy po 5 pytań, timer, joker ×2.
2. Dodany poziom „Mega zaawansowany”.
3. Punktacja dla graczy (Adam, Zając, Asia, Tomek, Julia): po pytaniu zaznaczano, kto trafił.
4. Przebudowa w teleturniej: odpowiada wskazana osoba, ujemne punkty, trafiający wskazuje następnego. Nowy poziom „Ekspert PL”, bo uczestnicy wyśmiali poprzednie pytania.
5. Kategoria „Popkultura PL 2010–2026”.
6. Wersja Live w Claude z przyciskami na telefonach (osobny link).
7. Kara za błąd zmieniona na −1 pkt (domyślnie) we wszystkich wersjach.
8. Diagnostyka połączenia w wersji Live. Okazało się, że capability `room` nie działa dla osób z publicznego linku.
9. Wersja Live bez logowania na PeerJS, jako plik do hostingu.
10. Kategorie „Jaki to urząd?”, „Używki”, „Prawo spółek (KSH)” i „Taylor Swift”.
11. Serwis na Vercel + Supabase: gra Live przez Supabase Realtime (zamiast połączeń telefon–telefon), odporna na odświeżenie strony i chwilowy brak sieci; lista wyników z rankingiem (okres, kategoria, tryb, sortowanie), ostatnimi grami i historią gracza; strona startowa z czołówką.
15. Kategoria „Jaki to wydział?” (47 pytań). Fakty z ostatnich lat sprawdzone w sieci; pominięte jednostki w trakcie zmian (CBŚP i CBZC, które Policja łączy w 2026 r. w Narodowe Biuro Śledcze, oraz COI).
14. Tryb mieszany („Mieszane” na bębnie): pytania z kilku wybranych kategorii w jednej grze, po równo i na zmianę. Działa w obu trybach i na liście wyników.
13. Dwie wersje gry z przyciskami. Online: odliczanie 3…2…1, potem pytanie i przycisk na wszystkich telefonach. Offline: prowadzący czyta pytanie i daje sygnał, gracze widzą tylko przycisk, a pytanie dopiero po wciśnięciu. W obu odpowiadający klika odpowiedź na swoim telefonie i gra sama liczy punkty. Koniec czasu niczego nie ocenia: decyduje prowadzący.
12. Jedna gra w serwisie: na starcie wybór trybu (jeden telefon albo przyciski na telefonach), potem ekran ustawień wybranego trybu. Kategoria, liczba pytań i kara przechodzą między trybami.

## Co sprawdzono

- **Struktura wszystkich 397 pytań**: każde ma 4 różne odpowiedzi, poprawny indeks i wyjaśnienie (`tests/validate_questions.js`).
- **Rozgrywka teleturnieju**: na każdym z 8 poziomów rozegrano grę od początku do końca w przeglądarce, bez błędów JS (`tests/smoke_teleturniej.py`).
- **Live w Claude**: prowadzący i 3 graczy na atrapie `room`. Sprawdzono falstart, sygnał, kolejność, odbicie i punkty (`tests/smoke_live_claude.py`).
- **Live bez logowania**: prowadzący i 2 graczy w osobnych przeglądarkach na lokalnym serwerze PeerJS (`tests/smoke_live_web.py`).
- **Serwis online** (`tests/smoke_web_supabase.py`, `tests/ranking_test.sql`): prawdziwy supabase-js na emulatorze Realtime i prawdziwym Postgresie. Sprawdzono: kod gry, dołączanie, zły i zajęty kod, falstart, kolejność, odbicie, odświeżenie strony prowadzącego, zerwanie połączenia, zapis wyniku z ponowieniem, teleturniej, filtry rankingu, historię gracza, odrzucanie fałszywych wyników. Nie sprawdzono jeszcze na prawdziwym projekcie Supabase i Vercel.
- **Czego nie sprawdzono**: gry na prawdziwych telefonach. Wersja bez logowania korzysta w praktyce z publicznego serwera PeerJS (0.peerjs.com), którego nie dało się przetestować z sandboksa. Niektóre sieci (firmowe Wi-Fi, część sieci komórkowych) mogą blokować bezpośrednie połączenia między telefonami.

## Fakty w pytaniach

- Większość faktów podano z pamięci modelu. W internecie sprawdzono rzeczy z ostatnich lat: liczbę ludności Polski w 2026 (GUS), Eurowizję 2025 (Steczkowska, 14. miejsce) i 2026 (Szemplińska, 12. miejsce), Wimbledon 2025, #Hot16Challenge2, nowelizację KSH z lutego 2026, „The Life of a Showgirl”, ślub Swift i Kelce (lipiec 2026) oraz koncerty Eras Tour w Warszawie.
- Najmniej pewne: szczegóły oznaczeń Witkacego na portretach (Używki), dokładne liczby mandatów i procenty w poziomie Ekspert PL.
- Pytania nie zależą od tego, kto akurat pełni jakąś funkcję, poza jawnie datowanymi faktami (np. wynik wyborów 2025).

## Znane ograniczenia i pomysły na dalej

- Live w Claude działa tylko dla zalogowanych osób z dostępem do artefaktu. Do gry ze znajomymi lepsza jest wersja bez logowania.
- Wersja bez logowania ładuje PeerJS z unpkg.com i łączy się przez publiczny broker PeerJS. Dla pewności można postawić własny serwer `peer` i ustawić `window.PK_PEER_OPTS`.
- Wpis kategorii (`LEVELS`) i przycisk poziomu są osobno w każdym szablonie, więc nową kategorię trzeba dopisać w dwóch miejscach (instrukcja w `CLAUDE.md`).
- Pomysły: mieszanie kilku kategorii w jednej grze, rundy tematyczne, tryb „TV” (duży ekran dla publiczności), zapis historii gier, edytor własnych pytań.

## Źródła użyte do weryfikacji

- [Interia: liczba ludności Polski w 2026 (GUS)](https://biznes.interia.pl/gospodarka/news-w-rok-ubylo-159-tys-osob-w-polsce-zmiany-demograficzne-juz-p,nId,23518504)
- [ESKA: Eurowizja 2025, wynik Steczkowskiej](https://www.eska.pl/news/eurowizja-2025-wynik-polski-ktore-miejsce-zajela-justyna-steczkowska-w-finale-wyniki-online-aa-xMgE-aUtY-FFBN.html)
- [Open FM: Eurowizja 2026, wynik Szemplińskiej](https://open.fm/muzyka/eurowizja-2026-ktore-miejsce-zajela-polska-alicja-szemplinska-zakonczyla-final-z-150-punktami-7286659108694080a)
- [CBS Sports: finał Wimbledonu 2025](https://www.cbssports.com/tennis/news/wimbledon-2025-results-iga-swiatek-makes-history-vs-amanda-anisimova-with-6-0-6-0-win-for-sixth-major)
- [Notes from Poland: #Hot16Challenge2](https://notesfrompoland.com/2020/05/17/polish-president-and-other-public-figures-join-online-rap-battle-to-raise-money-for-medical-workers/)
- [Kramer i Wspólnicy: nowelizacja KSH z lutego 2026](https://kwlaw.pl/nowelizacja-ksh-podpisana-w-lutym-2026-r-czyli-domkniecie-reformy-dematerializacji-akcji/)
- [Wikipedia: The Life of a Showgirl](https://en.wikipedia.org/wiki/The_Life_of_a_Showgirl)
- [NPR: ślub Taylor Swift i Travisa Kelce](https://www.npr.org/2026/07/03/nx-s1-5877361/taylor-swift-travis-kelce-wedding-msg)
- [Notes from Poland: Eras Tour w Warszawie](https://notesfrompoland.com/2024/07/29/swiftmania-hits-warsaw-with-eras-tour-concerts-expected-to-bring-city-e44-million/)
