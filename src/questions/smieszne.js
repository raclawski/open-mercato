const BANK_SMIESZNE = [
  {
    name: "Wałęsizmy", q: [
      { q: "Kto jest autorem zdania: „Jestem za, a nawet przeciw”?", o: ["Waldemar Pawlak", "Lech Wałęsa", "Józef Oleksy", "Andrzej Lepper"], c: 1,
        e: "To jeden z najsłynniejszych „wałęsizmów”, czyli powiedzeń Lecha Wałęsy albo mu przypisywanych." },
      { q: "Komu przypisuje się zdanie: „Dokonałem zwrotu o 360 stopni”?", o: ["Aleksandrowi Kwaśniewskiemu", "Lechowi Kaczyńskiemu", "Lechowi Wałęsie", "Leszkowi Millerowi"], c: 2,
        e: "Pełny obrót o 360 stopni zostawia w tym samym miejscu, więc zdanie brzmi jak pomyłka. Należy do zestawów „wałęsizmów”." },
      { q: "Kto narzekał: „Miała być demokracja, a tu każdy wygaduje, co chce!”?", o: ["Lech Wałęsa", "Jan Olszewski", "Józef Oleksy", "Waldemar Pawlak"], c: 0,
        e: "To kolejny znany wałęsizm, często cytowany jako żartobliwa skarga na wolność słowa." },
      { q: "Kto żartował: „Szłem czy szedłem, ale doszedłem”?", o: ["Aleksander Kwaśniewski", "Andrzej Lepper", "Waldemar Pawlak", "Lech Wałęsa"], c: 3,
        e: "Zdanie wraca w zestawieniach wałęsizmów i gra na wątpliwości, czy mówi się „szłem”, czy „szedłem”." },
      { q: "Kto przerobił toast na: „Zdrowie wasze w gardła nasze!”?", o: ["Lech Wałęsa", "Józef Oleksy", "Jan Maria Rokita", "Leszek Miller"], c: 0,
        e: "Za to zdanie i za „Nie chcem, ale muszem” Lech Wałęsa wygrał w 1992 r. plebiscyt „Srebrne Usta” radiowej Trójki." },
      { q: "Kto powiedział: „Dobrze się stało, że źle się stało”?", o: ["Hanna Suchocka", "Waldemar Pawlak", "Jan Olszewski", "Lech Wałęsa"], c: 3,
        e: "Zdanie zbudowane jak sprzeczność, typowe dla zestawień wałęsizmów." },
    ]
  },
  {
    name: "Lata 90. i 2000.", q: [
      { q: "Kto w 1995 r. powiedział: „Kura najpierw jajko zniesie, a dopiero potem gdacze”?", o: ["Józef Oleksy", "Jan Olszewski", "Waldemar Pawlak", "Hanna Suchocka"], c: 2,
        e: "Waldemar Pawlak, szef PSL, wygrał za te słowa plebiscyt „Srebrne Usta”." },
      { q: "Kto w 1996 r. zapewniał: „Ja nie jestem draniem, łobuzem, cynikiem i brzydzą mnie tego typu nieuczciwości”?", o: ["Marek Belka", "Grzegorz Kołodko", "Leszek Balcerowicz", "Jerzy Hausner"], c: 1,
        e: "Grzegorz Kołodko, wtedy wicepremier i minister finansów, wygrał za te słowa plebiscyt „Srebrne Usta”." },
      { q: "Który minister obrony w rządzie Jerzego Buzka powiedział, że polski lotnik poleci nawet na drzwiach od stodoły?", o: ["Janusz Onyszkiewicz", "Jerzy Szmajdziński", "Radosław Sikorski", "Bronisław Komorowski"], c: 3,
        e: "Bronisław Komorowski był ministrem obrony w latach 2000–2001. Zdanie stało się popularnym powiedzonkiem." },
      { q: "Kto w 2003 r. rzucił hasło „Nicea albo śmierć”?", o: ["Donald Tusk", "Jan Rokita", "Bronisław Geremek", "Marek Borowski"], c: 1,
        e: "Jan Rokita bronił w ten sposób zasad głosowania z traktatu nicejskiego, gdy zaczęły się negocjacje nad konstytucją europejską." },
      { q: "Kto po wygranych wyborach prezydenckich w 2005 r. zwrócił się do brata: „Panie prezesie, melduję wykonanie zadania!”?", o: ["Jarosław Kaczyński", "Kazimierz Marcinkiewicz", "Lech Kaczyński", "Zbigniew Ziobro"], c: 2,
        e: "Lech Kaczyński mówił to do Jarosława, szefa PiS, gdy wynik drugiej tury z 23 października 2005 r. był już jasny." },
      { q: "Który poseł SLD wygrał plebiscyt „Srebrne Usta” za rok 2006 wystąpieniem, które zaczął od słów „Panie Marszałku, Wysoka Izbo, w Hongkongu”?", o: ["Piotr Gadzinowski", "Jerzy Wenderlich", "Wojciech Olejniczak", "Jerzy Szmajdziński"], c: 0,
        e: "Mówił o antykorupcyjnym urzędzie w Hongkongu i żartował, że posłowie PiS mogą nie wiedzieć, czym jest Hongkong." },
      { q: "Kto w październiku 2007 r. skomentował nagranie ze swojego wykładu w Kijowie: „Może wypiłem jeden kieliszek wina, a może dziesięć. Mam prawo robić co chcę, jestem wolnym człowiekiem”?", o: ["Leszek Miller", "Aleksander Kwaśniewski", "Józef Oleksy", "Lech Wałęsa"], c: 1,
        e: "Aleksander Kwaśniewski, wtedy już były prezydent, tłumaczył się z nagrania, na którym chwiał się i miał kłopoty z mówieniem." },
    ]
  },
  {
    name: "Po 2007 roku", q: [
      { q: "Kto w Sejmie powiedział premierowi Tuskowi: „Mam wrażenie, i nie tylko ja w Polsce, że często pan stoi w rozkroku”?", o: ["Beata Kempa", "Renata Beger", "Joanna Kluzik-Rostkowska", "Nelli Rokita"], c: 3,
        e: "Nelli Rokita, posłanka wybrana w 2007 r. z listy PiS, jest laureatką plebiscytu „Srebrne Usta”." },
      { q: "Kto w 2010 r. wygrał plebiscyt „Srebrne Usta” zdaniem: „No i najważniejsze, że jesteśmy po zielonej stronie mocy”?", o: ["Marek Sawicki", "Waldemar Pawlak", "Janusz Piechociński", "Jarosław Kalinowski"], c: 1,
        e: "Waldemar Pawlak po raz pierwszy użył tej metafory w Poznaniu, gdy Al Gore dostawał doktorat honoris causa Uniwersytetu im. Adama Mickiewicza." },
      { q: "Kto w maju 2015 r., w kampanii prezydenckiej, poradził zarabiającemu 2 tys. zł, żeby zmienił pracę i wziął kredyt?", o: ["Andrzej Duda", "Bronisław Komorowski", "Paweł Kukiz", "Ewa Kopacz"], c: 1,
        e: "Bronisław Komorowski, wtedy prezydent, usłyszał potem, że przy takich zarobkach trudno o kredyt." },
      { q: "Który minister spraw zagranicznych w styczniu 2016 r. mówił o świecie rowerzystów i wegetarian, opartym na odnawialnych źródłach energii?", o: ["Radosław Sikorski", "Witold Waszczykowski", "Grzegorz Schetyna", "Jacek Czaputowicz"], c: 1,
        e: "Witold Waszczykowski jest laureatem plebiscytu „Srebrne Usta”. Jego słowa przez długi czas były tematem żartów." },
      { q: "Który poseł zapytał na posiedzeniu komisji śledczej ds. Amber Gold prezes gdańskiego sądu apelacyjnego, dlaczego nazywają ją „caryca”?", o: ["Stanisław Pięta", "Joachim Brudziński", "Marek Suski", "Krzysztof Jurgiel"], c: 2,
        e: "Marek Suski, wiceprzewodniczący komisji, zadał to pytanie Annie Skupnej. Fragment przesłuchania obiegł internet." },
      { q: "Kto w styczniu 2019 r. mówił w telewizji, że dawni ludzie rzucali kamieniami w dinozaura, aż go osłabili?", o: ["Barbara Nowacka", "Joanna Scheuring-Wielgus", "Ewa Kopacz", "Małgorzata Kidawa-Błońska"], c: 2,
        e: "Ewa Kopacz mówiła to w programie „Fakt Opinie” 31 stycznia 2019 r. Dinozaury wyginęły ok. 66 mln lat temu, na długo przed pojawieniem się człowieka. Za tę wypowiedź dostała „Srebrne Usta”." },
      { q: "Kto po spotkaniu z Emmanuelem Macronem mówił o „atakach hakerskich, srakerskich”?", o: ["Mateusz Morawiecki", "Andrzej Duda", "Zbigniew Rau", "Mariusz Błaszczak"], c: 0,
        e: "To przejęzyczenie premiera Mateusza Morawieckiego z konferencji, na której mówiono o rosyjskiej propagandzie i kryzysie na granicy z Białorusią." },
    ]
  },
];
