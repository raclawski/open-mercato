# Plan prac

Lista usprawnień do wyboru. Działa w cyklach: wybierasz pozycje i kolejność, ja je robię, testuję, wdrażam na `main` i zaznaczam tutaj. Nowe pomysły dopisuję na końcu listy „Do zrobienia”.

Wielkość: **S** to krótka zmiana, **M** to kilka godzin pracy z testami, **L** to kilka sesji albo zmiana bazy.
Zmiana bazy (**SQL**) oznacza, że po wdrożeniu musisz wgrać nowy plik w Supabase → SQL Editor.

## Wdrożone

| ID | Usprawnienie | Kiedy |
|---|---|---|
| A1 | Nowy kod pokoju przy każdym odświeżeniu lobby. Trwająca gra zachowuje kod. | 18.10.2026 |
| A2 | Serwis nazywa się TELETURNIEJ. Domena i artefakty Claude bez zmian. | 18.10.2026 |
| A4 | Pasek czasu u gracza: czas na wciśnięcie (online) i na odpowiedź, widoczny dla wszystkich | 18.10.2026 |
| A5 | Liczba pytań: suwak 1–100 z przyciskami −/+ | 18.10.2026 |
| B0 | Stałe identyfikatory pytań: id z treści, stara pamięć telefonu przepisana | 18.10.2026 |
| B1 | Rejestr nicków: podpowiedzi znanych nicków przy imieniu (gracz, admin, jeden telefon), lista wyników domyślnie „Zawsze” (do 500 nicków). Punkty sumują się po nicku jak dotąd. | 18.10.2026 |
| A8 | Instrukcja gry z przyciskami zostaje na ekranie, dopóki prowadzący nie kliknie „Zaczynamy!” | 18.10.2026 |
| C1 | Partia 1 bazy pytań: 5 nowych kategorii po 100 pytań (razem 944) | 18.10.2026 |
| — | Naprawa listy wyników (funkcja czyszcząca nicki) | 18.10.2026 |

## Do zrobienia

Kolejność ustalona przez Ciebie: B0 (✓), B1 (✓), B2. Pozycje dopisane później stoją za nimi, chyba że zdecydujesz inaczej.

| ID | Usprawnienie | Wielkość | Status |
|---|---|---|---|
| B2 | Dobór pytań sterujący częstotliwością powtórek dla nicku | M, SQL | następne |
| A9 | Wybór kategorii: najpierw „1 kategoria” albo „MIX”, potem bęben jako wielkie koło | M | — |
| A7 | Przycisk „Następne pytanie”, żeby nie czekać na automatyczne przejście | S | — |
| A6 | Pytanie za podwójne punkty (×2), z komunikatem dla graczy, włączane w lobby | M, SQL | — |
| B3 | Trzeci tryb online: „Kto pierwszy, ten lepszy” | L, SQL | — |
| A3 | Kontrola wersji bazy: gra ostrzega, gdy migracja nie jest wgrana | S, SQL | — |
| C2 | Zgłaszanie błędnego pytania z poziomu gry | M, SQL | — |
| D1 | Komunikaty i dopracowanie interfejsu | M | — |
| C1 | Baza 5000 pytań, kolejne partie po 500 | L, cyklicznie | wstrzymane |

A6 i B3 zmieniają sposób liczenia punktów, a baza dziś sama przelicza wynik jako 10 × dobre − kara × złe. Obie pozycje warto więc zrobić z jedną wspólną zmianą bazy.

---

## B0. Stałe identyfikatory pytań

Dziś id pytania to `kategoria:dział-numer`, więc po dopisaniu albo usunięciu pytania w środku działu numery się przesuwają, a historia „już było” wskazuje na inne pytania. Zmiana: id liczone z treści pytania. Walidator pilnuje, żeby się nie powtarzały. Na tym opiera się B2.

## B1. Rejestr nicków

Ustalone: każdy może wpisać każdy nick, bez kluczy i kodów odzyskiwania, bez blokowania wulgarnych.
- Baza prowadzi listę wszystkich nicków, które choć raz zagrały: od kiedy, ile gier, suma punktów.
- Lista wyników pokazuje każdy taki nick, w widoku „cały czas” także z zerem w wybranym okresie i kategorii.
- Przy wpisywaniu nicku gra podpowiada istniejące nicki, żeby „Tomek” i „Tomek ” albo „tomek” nie rozjeżdżały się na dwa konta. Dziś wielkość liter i tak nie ma znaczenia.
- Telefon pamięta ostatnio używany nick.

## B2. Dobór pytań jak tasowanie w Spotify

Ustalone: żadne pytanie nie jest blokowane, sterujemy tylko częstotliwością.
- Baza zapisuje dla nicku, które pytania widział i kiedy.
- Każde pytanie dostaje wagę: niewidziane przez nikogo w pokoju ma najwyższą, widziane niedawno albo przez wielu graczy niską, ale nigdy zerową. Waga wraca do pełnej w ciągu ok. 60 dni.
- Losujemy według wag, więc kolejność jest nieprzewidywalna, a powtórki rzadkie.
- Pytania z tego samego działu nie idą po sobie, a kategorie w mieszance przeplatają się równo.
- Bez internetu: obecna pamięć telefonu (`pk_seen`), też jako wagi zamiast blokady.

## A9. Wybór kategorii

- Najpierw dwa duże przyciski: **1 kategoria** albo **MIX**.
- „1 kategoria” pokazuje bęben z kategoriami, „MIX” pokazuje listę kategorii do zaznaczenia (jak dziś chipy).
- Bęben jako wielkie koło: środkowy wiersz pełny i ostry, wiersze dalej od środka coraz bardziej spłaszczone (obrót w perspektywie), mniejsze i wyszarzone, jak w kole wyboru daty w iPhonie.

## A7. „Następne pytanie”

Po odkryciu odpowiedzi gra online czeka 6 s i sama przechodzi dalej. Przycisk „Następne pytanie” przechodzi od razu.
**Do decyzji:** kto może go kliknąć: tylko admin pokoju (propozycja) czy każdy gracz?

## A6. Pytanie ×2

Jedno losowe pytanie w rundzie jest warte podwójnie (+20, kara też podwójna). Przed pytaniem wszyscy widzą komunikat „Pytanie za podwójne punkty!”. Opcję włącza się w lobby i w ustawieniach jednego telefonu.
**Do decyzji:**
1. Co to jest „runda”? Propozycja: każde kolejne 10 pytań. Gra na 30 pytań ma wtedy 3 pytania ×2, a gra na 7 pytań jedno.
2. Czy kara za złą odpowiedź też jest podwójna? Propozycja: tak.

## B3. „Kto pierwszy, ten lepszy”

Trzeci tryb online: wszyscy widzą pytanie naraz i każdy klika odpowiedź u siebie, bez wciskania przycisku. Punkty zależą od poprawności i szybkości. Pytanie kończy się, gdy odpowiedzą wszyscy albo minie czas, potem odkrycie i tabela.
**Do decyzji: punktacja.** Propozycje:
- (a) Miejsca: najszybsza dobra odpowiedź 10 pkt, druga 8, trzecia 6, każda kolejna dobra 4, zła 0.
- (b) Czas: dobra odpowiedź daje od 10 pkt (od razu) do 5 pkt (na koniec czasu), zła 0, jak w Kahoot.
- Czy zła odpowiedź ma karę (np. −kara z lobby)? Bez kary opłaca się strzelać, z karą gracze mogą nie odpowiadać.

## A3. Kontrola wersji bazy

Funkcja `pk_version()` w bazie. Strona startowa pokazuje wyraźny komunikat, gdy baza wymaga aktualizacji. Gra odrzucona przez bazę zostaje w kolejce i zapisze się po naprawie.

## C2. Zgłaszanie błędnego pytania

Przycisk „Zgłoś” przy wyjaśnieniu zapisuje id pytania i opis w bazie. Raz na cykl przeglądam zgłoszenia i poprawiam pytania.

## D1. Komunikaty i interfejs

Czytelniejsze komunikaty o połączeniu i zapisie, ekran lobby, drobne poprawki układu. Zakres na podstawie uwag z testów.

## C1. Baza 5000 pytań (wstrzymane)

| Partia | Zawartość | Status |
|---|---|---|
| 1 | Telewizja i show, Historia Polski, Geografia i przyroda, Sport polski, Literatura polska | ✓ |
| 2 | Kino polskie, Muzyka, Nauka i technika, Kuchnia i obyczaje, Język polski | — |
| 3 | PRL na co dzień + dopełnienie 9 starych kategorii | — |
| 4–10 | Dopełnianie wszystkich kategorii do ok. 250 | — |
