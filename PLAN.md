# Plan prac

Lista usprawnień do wyboru. Działa w cyklach: na początku cyklu wybierasz pozycje (np. „cykl 2: A1, A2, D1”), ja je robię, testuję, wdrażam na `main` i zaznaczam tutaj. Potem wybierasz następne. Kolejność w tabeli to moja propozycja, nie zobowiązanie.

Wielkość: **S** to jedna krótka sesja, **M** to kilka godzin pracy z testami, **L** to kilka sesji albo zmiana bazy.
Status: `—` czeka, `▶` w toku, `✓` wdrożone.

## Do zrobienia przez Ciebie

- [x] Wgraj ponownie `supabase/migrations/20261019090000_ranking_accept_all.sql` w Supabase (zrobione 18.10.2026; do potwierdzenia testem z SQL Editora albo jedną rozegraną grą).

## Lista

| ID | Usprawnienie | Wielkość | Zależy od | Status |
|---|---|---|---|---|
| A1 | Nowy kod pokoju przy każdym odświeżeniu | S | — | — |
| A2 | Nowa nazwa aplikacji: TELETURNIEJ | S | — | — |
| A3 | Kontrola wersji bazy (gra wie, czy migracja jest wgrana) | S | — | — |
| B0 | Stałe identyfikatory pytań | S | — | — |
| B1 | Rezerwacja nicków bez kont | L | A3 | — |
| B2 | Dobór pytań, który unika powtórek dla nicku | M | B0 (lepiej też B1) | — |
| C1 | Baza 5000 pytań w 20 kategoriach (partie po 500) | L, cyklicznie | — | wstrzymane, partia 1 ✓ (944 pytania) |
| C2 | Zgłaszanie błędnego pytania z poziomu gry | M | — | — |
| D1 | Komunikaty i dopracowanie interfejsu | M | A2 | — |

Proponowana kolejność: **cykl 2**: A1, A2, A3, B0 (szybkie i porządkujące). **Cykl 3**: B1. **Cykl 4**: B2. Dalej C2, D1, a pytania (C1) wracają, gdy zdecydujesz.

---

## A1. Nowy kod pokoju przy każdym odświeżeniu

Dziś prowadzący ma stały identyfikator na urządzeniu (`pkw_hid`) i zapamiętany kod (`pkw_hcode`), więc po odświeżeniu wraca do tego samego pokoju. Zmiana: każde wejście na ekran tworzenia gry losuje nowy kod.

**Do decyzji:** co ma się dziać po odświeżeniu **w trakcie** trwającej gry?
- (a) *Rekomendacja:* nowy kod w lobby i po zakończeniu gry, ale trwająca gra zachowuje kod. Inaczej odświeżenie strony przez admina wyrzuca wszystkich graczy i kończy grę.
- (b) Zawsze nowy kod. Odświeżenie kończy grę, a gracze muszą wpisać nowy kod.

Gotowe, gdy: dwa odświeżenia lobby dają dwa różne kody. Test w `tests/smoke_web_supabase.py`.

## A2. Nowa nazwa: TELETURNIEJ

Zakres: tytuły stron, nagłówki, strona startowa, lista wyników, teksty w grze, README, CLAUDE.md, PODSUMOWANIE.md, artefakty Claude.
Bez zmian: klucze `localStorage` (`pk_*`), nazwy kanałów Realtime i tabel w bazie. Dzięki temu trwające gry, zapisane ustawienia i wyniki działają dalej.

**Do decyzji:**
- Domena: zostaje `krzyzyk.vercel.app` czy zmieniamy? Nowa nazwa w Vercel (Settings → Domains) jest darmowa, ale stary link przestanie działać, chyba że ustawimy przekierowanie.
- Zapis: „TELETURNIEJ” wielkimi literami w logo, a w tekście „Teleturniej”?

## A3. Kontrola wersji bazy

Dzisiejszy problem z listą wyników (zepsuta funkcja po wklejeniu migracji) dało się wykryć dopiero po grze. Zmiana:
- funkcja `pk_version()` w bazie,
- strona startowa sprawdza wersję i pokazuje wyraźny komunikat „baza wymaga aktualizacji: wgraj plik X”,
- gra odrzucona przez bazę zostaje w kolejce `pk_outbox`, zamiast znikać, i zapisze się po naprawie bazy.

## B0. Stałe identyfikatory pytań

Dziś id pytania to `kategoria:dział-numer`. Po dopisaniu albo usunięciu pytania w środku działu numery się przesuwają i historia „już było” wskazuje na inne pytania. Przy partiach po 500 to będzie się zdarzać. Zmiana: id liczone z treści pytania (krótki skrót), walidator pilnuje unikalności. Na tym opiera się B2.

## B1. Rezerwacja nicków bez kont

Stan obecny: ranking już sumuje punkty po nicku (bez względu na wielkość liter), ale każdy może wpisać cudzy nick.

**Jak to działałoby:**
- Pierwsza zapisana gra z wolnym nickiem rezerwuje go dla tego telefonu. Telefon dostaje tajny klucz (w `localStorage`), a baza trzyma tylko jego skrót.
- Każdy zarezerwowany nick jest na liście wyników, także bez punktów w danym okresie, a kolejne gry dopisują mu punkty.
- Przy wpisywaniu nicku gra od razu mówi „ten nick jest zajęty”, zanim gracz dołączy.
- Przeniesienie na inny telefon: kod odzyskiwania (np. 8 znaków) do zapisania, pokazany po rezerwacji i dostępny w „Moje nicki”.

**Ważny szczegół techniczny:** w grze z przyciskami wynik zapisuje admin, a kanał gry jest publiczny dla każdego, kto zna kod. Tajne klucze graczy nie mogą więc iść przez kanał. Każdy telefon gracza na końcu gry sam potwierdza w bazie „to byłem ja” swoim kluczem. Punkty dla zarezerwowanego nicku liczą się tylko po potwierdzeniu.

**Do decyzji:**
1. Ktoś gra cudzym zarezerwowanym nickiem bez klucza: (a) *rekomendacja:* gra nie pozwala go użyć; (b) gra się zapisuje, ale punkty idą do „Tomek (gość)”.
2. Tryb „jeden telefon” (kilku graczy na jednym telefonie): ten telefon rezerwuje wszystkie nicki? *Rekomendacja:* tak, kod odzyskiwania pozwala potem przenieść nick na własny telefon.
3. Nicki, które już są na liście wyników: rezerwuje je pierwszy telefon, który zagra po wdrożeniu (*rekomendacja*), czy zostają wolne do ręcznego przydzielenia?
4. Czy blokujemy wulgarne nicki (prosta lista słów)?
5. Czy nick wygasa po np. roku bez gry?

## B2. Dobór pytań jak tasowanie w Spotify

Dziś: najpierw pytania jeszcze nie wylosowane na tym **telefonie** (`pk_seen`), w kolejności czysto losowej. Po wyczerpaniu puli pamięć się zeruje.

Zmiana: dobór na podstawie historii **nicków w pokoju**, a nie telefonu. Działa podobnie do tasowania w Spotify: nie jest czysto losowy, unika tego, co było niedawno, i rozkłada podobne utwory, tu działy, równo w czasie.
- Baza zapisuje dla nicku, które pytania widział i kiedy.
- Każde pytanie dostaje wagę: niewidziane przez nikogo w pokoju ma najwyższą, widziane dawno średnią, widziane niedawno albo przez wielu graczy bliską zera. Losujemy według wag, więc kolejność dalej jest nieprzewidywalna, ale powtórki są rzadkie.
- Rozkładanie: dwa pytania z tego samego działu nie idą po sobie, a w trybie mieszanym kategorie przeplatają się równo (tak jak dziś).
- Bez internetu albo bez nicków wraca obecny sposób (`pk_seen`).

**Do decyzji:** jak szybko pytanie „wraca do puli”? Propozycja: waga odbudowuje się w ok. 60 dni, a po wyczerpaniu niewidzianych pytań pierwsze wracają te widziane najdawniej.

## C1. Baza 5000 pytań

Cel to 20 kategorii, średnio ok. 250 pytań. Każda partia ma ok. 500 pytań: piszę, sprawdzam fakty w sieci, przeglądam, testuję i wdrażam.

| Partia | Zawartość | Status |
|---|---|---|
| 1 | Telewizja i show, Historia Polski, Geografia i przyroda, Sport polski, Literatura polska (5 × 100) | ✓ |
| 2 | Kino polskie, Muzyka, Nauka i technika, Kuchnia i obyczaje, Język polski | — |
| 3 | PRL na co dzień + dopełnienie 9 starych kategorii | — |
| 4–10 | Dopełnianie wszystkich kategorii do ok. 250 | — |

**Do decyzji:** czy któraś kategoria ma być większa (np. „Taniec z gwiazdami” jako osobna)? Czy Taylor Swift i Prawo spółek zostają mniejsze?

## C2. Zgłaszanie błędnego pytania

Przy 5000 pytań trafią się pomyłki. Przycisk „Zgłoś” przy wyjaśnieniu zapisuje id pytania i krótki opis w bazie, a ja raz na cykl przeglądam zgłoszenia i poprawiam pytania.

## D1. Komunikaty i interfejs

Zapowiedziane znajomym na kolejny sprint: czytelniejsze komunikaty o połączeniu i zapisie, ekran lobby, drobne poprawki układu na telefonie. Zakres ustalimy na podstawie Waszych uwag z testów.
