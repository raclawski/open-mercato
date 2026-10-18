# Wdrożenie: Supabase + Vercel

Gra działa pod adresem **https://krzyzyk.vercel.app**. Link dla graczy ma postać `https://krzyzyk.vercel.app/live?kod=XXXX` i tworzy się sam z adresu strony, więc po zmianie domeny nic w kodzie nie trzeba poprawiać.

Serwis z `dist/web/` składa się z czterech stron: start, gra Live, teleturniej i lista wyników. Supabase daje dwie rzeczy: połączenie telefonów w grze Live (Realtime) i bazę z wynikami. Vercel tylko serwuje pliki statyczne.

Koszt: oba serwisy mają darmowe plany, które wystarczą na gry ze znajomymi.

## 1. Supabase (ok. 5 minut)

1. Załóż konto na https://supabase.com i utwórz projekt (**New project**). Region: Frankfurt (`eu-central-1`), najbliżej Polski. Hasło do bazy zapisz, ale gra go nie potrzebuje.
2. Wgraj bazę wyników. W panelu otwórz **SQL Editor**, wklej całą zawartość pliku `supabase/migrations/20261018120000_ranking.sql` i kliknij **Run**. Skrypt można uruchomić ponownie, nic nie zepsuje.
   Potem tak samo wgraj `supabase/migrations/20261019090000_ranking_accept_all.sql` (lista wyników przyjmuje każdą grę). Jeśli baza już działa, wystarczy ten drugi plik. Wgraj go ponownie, jeśli gra pokazuje „Lista wyników odrzuciła tę grę (nieprawidłowe dane graczy)”: poprawia funkcję czyszczącą nicki, którą mogło zepsuć kopiowanie pierwszego pliku. Do wklejenia otwórz plik jako **Raw** (na GitHubie przycisk *Raw*) i skopiuj całość.
   Jeśli używasz Supabase CLI: `supabase link --project-ref <ref>` i `supabase db push`.
3. Sprawdź Realtime. W **Project Settings → Realtime** opcja publicznego dostępu do kanałów (*Allow public access* / bez wymogu autoryzacji kanałów) musi być włączona. W nowych projektach jest włączona domyślnie. Gra używa tylko Broadcast i Presence, bez nasłuchiwania zmian w tabelach.
4. Skopiuj dane do połączenia z **Project Settings → API** (albo **Connect**):
   - **Project URL**, np. `https://abcdefgh.supabase.co`,
   - klucz **anon** / **publishable** (publiczny).

   Klucz `service_role` / `secret` nigdy nie trafia na stronę. `tools/write-config.mjs` przerwie build, jeśli go dostanie.

## 2. Vercel (ok. 5 minut)

1. Załóż konto na https://vercel.com i zaloguj się przez GitHub.
2. **Add New → Project**, wybierz repozytorium z grą. Ustawienia wczyta z `vercel.json` (bez frameworka, katalog `dist/web`), więc nic nie zmieniaj.
3. W **Environment Variables** dodaj:
   - `SUPABASE_URL`: Project URL z kroku 1.4,
   - `SUPABASE_ANON_KEY`: klucz anon z kroku 1.4.
4. **Deploy**. Po minucie gra działa pod adresem projektu. Nasz adres: **https://krzyzyk.vercel.app** (projekt w Vercel, gałąź produkcyjna `main`).

Zamiast zmiennych w Vercel możesz wpisać oba klucze do `src/web/config.js`, uruchomić `python3 tools/build.py` i zrobić commit. Klucz anon jest publiczny z założenia.

Każdy push na gałąź główną to nowe wdrożenie. Gałęzie robocze dostają osobne adresy podglądu.

## 3. Sprawdzenie po wdrożeniu

1. Otwórz `/live` na komputerze lub telefonie i wybierz **Prowadzę grę**. Pojawi się 4-literowy kod.
2. Na drugim telefonie (najlepiej przez sieć komórkową) otwórz link dla graczy i dołącz. Imię pojawi się u prowadzącego.
3. Rozegraj kilka pytań i zakończ grę. Na ekranie wyników ma się pokazać „Wynik zapisany na liście wyników”.
4. Otwórz `/wyniki`. Gra jest w rankingu i na liście ostatnich gier.

Jeśli strona pisze „brak konfiguracji Supabase”, zmienne w Vercel nie są ustawione albo build nie przeszedł (zobacz **Deployments → Build Logs**).

## Co jest gdzie

| Element | Gdzie |
|---|---|
| Strony (HTML, JS, CSS) | Vercel, katalog `dist/web` |
| Połączenie telefonów w grze Live | Supabase Realtime, kanał `pk-live-v1-<KOD>` |
| Wyniki gier | Supabase Postgres, tabele `pk_games` i `pk_game_players` |
| Dostęp do wyników z przeglądarki | tylko funkcje `pk_submit_game`, `pk_leaderboard`, `pk_recent_games` |

## Bezpieczeństwo i ograniczenia

- Przeglądarka nie czyta ani nie zapisuje tabel bezpośrednio: RLS jest włączony bez polityk, a prawa do tabel odebrane. Wszystko idzie przez funkcje, które sprawdzają dane.
- `pk_submit_game` odrzuca wyniki, które nie wynikają z odpowiedzi (wynik ≠ 10 × dobre − kara × złe), więcej dobrych odpowiedzi niż pytań, powtórzone imiona i wartości spoza zakresu. Zapis tej samej gry drugi raz nic nie zmienia.
- Bez kont każdy może wpisać dowolny nick. Ktoś, kto zna klucz anon (jest na stronie), może też wysłać zmyśloną, ale „spójną” grę. Na grę ze znajomymi to wystarczy. Gdyby ranking stał się publiczny i ważny, kolejny krok to konta (Supabase Auth) albo zapis wyniku po stronie serwera.
- Nie ma limitu liczby zapisów. Usunięcie fałszywej gry: w **SQL Editor** `delete from pk_games where id = '…';` (gracze tej gry usuną się kaskadowo).
