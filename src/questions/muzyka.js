const BANK_MUZYKA = [
  {
    name: "Teoria i instrumenty", q: [
      { q: "Ile półtonów ma oktawa?", o: ["7", "8", "10", "12"], c: 3, fix: 1,
        e: "Oktawa dzieli się na 12 półtonów: siedem dźwięków skali durowej plus pięć dźwięków pośrednich." },
      { q: "Co oznacza włoskie oznaczenie tempa „adagio”?", o: ["Szybko", "Wolno, spokojnie", "Coraz ciszej", "Z wyrazem, śpiewnie"], c: 1,
        e: "„Adagio” to tempo wolne. Szybkie to np. „presto” i „allegro”." },
      { q: "Jak są strojone struny skrzypiec, od najniższej do najwyższej?", o: ["E–A–D–G", "C–G–D–A", "G–D–A–E", "D–A–E–B"], c: 2,
        e: "Skrzypce stroi się w kwintach: g–d¹–a¹–e². C–G–D–A to strój altówki i wiolonczeli." },
      { q: "Ile klawiszy ma standardowy fortepian?", o: ["76", "82", "88", "96"], c: 2, fix: 1,
        e: "Standardowy fortepian ma 88 klawiszy: 52 białe i 36 czarnych." },
      { q: "Ile półtonów ma interwał zwany kwintą czystą?", o: ["5", "6", "7", "9"], c: 2, fix: 1,
        e: "Kwinta czysta to 7 półtonów. Kwarta czysta ma 5, a tryton 6." },
      { q: "Którym kluczem zapisuje się zwykle nuty dla altówki?", o: ["Wiolinowym", "Basowym", "Altowym", "Sopranowym"], c: 2,
        e: "Altówka gra z klucza altowego. Skrzypce czytają z klucza wiolinowego, a wiolonczela głównie z basowego." },
      { q: "Który instrument ma najniższy dźwięk wśród smyczkowych w orkiestrze symfonicznej?", o: ["Wiolonczela", "Altówka", "Kontrabas", "Harfa"], c: 2,
        e: "Kontrabas brzmi najniżej. Harfa jest instrumentem szarpanym, nie smyczkowym." },
    ]
  },
  {
    name: "Muzyka poważna", q: [
      { q: "Kto skomponował cykl koncertów „Cztery pory roku”?", o: ["Johann Sebastian Bach", "Antonio Vivaldi", "Georg Friedrich Händel", "Joseph Haydn"], c: 1,
        e: "Antonio Vivaldi, włoski kompozytor baroku. Każdy z czterech koncertów opisuje inną porę roku." },
      { q: "Kto jest autorem opery „Wesele Figara”?", o: ["Gioachino Rossini", "Giuseppe Verdi", "Wolfgang Amadeus Mozart", "Richard Wagner"], c: 2,
        e: "Opera Mozarta z 1786 r. Libretto napisał Lorenzo Da Ponte." },
      { q: "Który polski kompozytor napisał balet „Harnasie”?", o: ["Karol Szymanowski", "Stanisław Moniuszko", "Witold Lutosławski", "Henryk Mikołaj Górecki"], c: 0,
        e: "Karol Szymanowski, inspirowany muzyką Podhala. Moniuszko jest autorem „Halki”." },
      { q: "Kto skomponował operę „Halka”?", o: ["Fryderyk Chopin", "Stanisław Moniuszko", "Karol Szymanowski", "Ignacy Jan Paderewski"], c: 1,
        e: "Stanisław Moniuszko. „Halka” to jedna z najważniejszych polskich oper narodowych." },
      { q: "Który kompozytor napisał „Bolero” z 1928 r., oparte na jednym, powtarzanym rytmie i melodii?", o: ["Claude Debussy", "Maurice Ravel", "Erik Satie", "Igor Strawiński"], c: 1,
        e: "Maurice Ravel. Utwór składa się z jednej melodii, a rośnie tylko liczba instrumentów i głośność." },
      { q: "Co ile lat odbywa się Międzynarodowy Konkurs Pianistyczny im. Fryderyka Chopina w Warszawie?", o: ["Co 3 lata", "Co 4 lata", "Co 5 lat", "Co 6 lat"], c: 2, fix: 1,
        e: "Konkurs odbywa się co pięć lat." },
      { q: "Ile symfonii skomponował Ludwig van Beethoven?", o: ["5", "7", "9", "12"], c: 2, fix: 1,
        e: "Beethoven napisał dziewięć symfonii. W finale ostatniej, IX, użył chóru i solistów." },
    ]
  },
  {
    name: "Rock, pop i jazz", q: [
      { q: "Który zespół nagrał album „The Dark Side of the Moon” z 1973 r.?", o: ["Led Zeppelin", "Pink Floyd", "Genesis", "Deep Purple"], c: 1,
        e: "Pink Floyd. Płyta przez wiele lat utrzymywała się na liście najlepiej sprzedających się albumów." },
      { q: "Który zespół wydał w 1991 r. album „Nevermind”?", o: ["Pearl Jam", "Soundgarden", "Nirvana", "Red Hot Chili Peppers"], c: 2,
        e: "Nirvana. Album otwiera utwór „Smells Like Teen Spirit”." },
      { q: "Jak nazywa się album Beatlesów z 1967 r. z okładką pełną postaci wokół zespołu w kolorowych mundurach?", o: ["Revolver", "Abbey Road", "Sgt. Pepper's Lonely Hearts Club Band", "Rubber Soul"], c: 2,
        e: "„Sgt. Pepper's Lonely Hearts Club Band”. „Abbey Road” z 1969 r. ma na okładce zespół na przejściu dla pieszych." },
      { q: "Który zespół z Dublina wydał w 1987 r. album „The Joshua Tree”?", o: ["The Cranberries", "Thin Lizzy", "U2", "The Pogues"], c: 2,
        e: "U2. Na płycie są m.in. „With or Without You” i „Where the Streets Have No Name”." },
      { q: "Które miasto uważa się za kolebkę jazzu?", o: ["Chicago", "Nowy Jork", "Nowy Orlean", "Memphis"], c: 2,
        e: "Jazz narodził się na przełomie XIX i XX wieku w Nowym Orleanie." },
      { q: "Kto w 1967 r. wylansował piosenkę „Dziwny jest ten świat”?", o: ["Marek Grechuta", "Czesław Niemen", "Krzysztof Klenczon", "Andrzej Zaucha"], c: 1,
        e: "Czesław Niemen. Piosenka stała się jednym z symboli polskiej muzyki rozrywkowej lat 60." },
    ]
  },
];
