const BANK_TS = [
  {
    name: "Albumy", q: [
      { q: "Jak nazywał się debiutancki singiel Taylor Swift z 2006 r.?", o: ["„Tim McGraw”", "„Teardrops on My Guitar”", "„Our Song”", "„Picture to Burn”"], c: 0,
        e: "Piosenka nosi nazwisko gwiazdy country. Ukazała się na debiutanckim albumie „Taylor Swift”." },
      { q: "W której wytwórni Taylor Swift wydała swoje pierwsze sześć albumów?", o: ["Big Machine Records", "Republic Records", "Sony Music Nashville", "Interscope"], c: 0,
        e: "Big Machine założył Scott Borchetta. Od albumu „Lover” (2019) Swift jest w Republic Records." },
      { q: "Który album Swift napisała w całości sama, bez współautorów?", o: ["„Speak Now”", "„Fearless”", "„Red”", "„1989”"], c: 0,
        e: "„Speak Now” z 2010 r. był odpowiedzią na zarzuty, że nie pisze sama swoich piosenek." },
      { q: "Który producent jest głównym współtwórcą popowego brzmienia „1989” i „The Life of a Showgirl”?", o: ["Max Martin", "Jack Antonoff", "Aaron Dessner", "Rick Rubin"], c: 0,
        e: "Przy „The Life of a Showgirl” Max Martin pracował ze Shellbackiem. Antonoff to główny współpracownik „Midnights”, a Dessner „Folklore” i „Evermore”." },
      { q: "Z muzykiem którego zespołu Swift nagrała większość albumów „Folklore” i „Evermore”?", o: ["The National", "Bon Iver", "HAIM", "The 1975"], c: 0,
        e: "Aaron Dessner jest gitarzystą The National. Justin Vernon z Bon Iver zaśpiewał w duecie „exile”." },
      { q: "Które trzy piosenki z „Folklore” opowiadają jeden szkolny trójkąt miłosny?", o: ["„cardigan”, „august”, „betty”", "„exile”, „seven”, „mirrorball”", "„the 1”, „hoax”, „peace”", "„invisible string”, „epiphany”, „mad woman”"], c: 0,
        e: "Bohaterami są Betty, James i dziewczyna z „august”. Swift opowiedziała tę historię z trzech perspektyw." },
      { q: "Co jako pierwsza artystka w historii osiągnęła Swift dzięki albumowi „Midnights” (2022)?", o: ["Zajęła całą pierwszą dziesiątkę Billboard Hot 100", "Sprzedała milion winyli w tydzień", "Dostała Oscara za piosenkę", "Wydała album jednocześnie w 10 wersjach"], c: 0,
        e: "Wszystkie miejsca od 1 do 10 zajęły piosenki z „Midnights”, na czele z „Anti-Hero”." },
      { q: "Gdzie Swift ogłosiła album „The Tortured Poets Department”?", o: ["Podczas odbierania nagrody Grammy w lutym 2024", "Na koncercie Eras Tour w Tokio", "W podcaście „New Heights”", "Na gali VMA 2023"], c: 0,
        e: "Ogłosiła go, odbierając Grammy za „Midnights”. Album ukazał się 19 kwietnia 2024 r., z wersją „Anthology” liczącą 31 piosenek." },
      { q: "Który z kolei album studyjny Swift to „The Life of a Showgirl” (2025)?", o: ["10.", "11.", "12.", "13."], c: 2, fix: 1,
        e: "Ukazał się 3 października 2025 r. Nagrany był w Szwecji w trakcie europejskiej części Eras Tour." },
      { q: "Czyj rekord sprzedaży z pierwszego tygodnia pobiła w 2025 r. płyta „The Life of a Showgirl”?", o: ["Adele, za album „25”", "Własny, za „1989”", "Michaela Jacksona, za „Thriller”", "Beyoncé, za „Lemonade”"], c: 0,
        e: "Płyta miała ok. 4 mln jednostek w pierwszym tygodniu w USA. „25” Adele z 2015 r. miało ok. 3,5 mln." },
      { q: "Kto gościnnie śpiewa w tytułowej piosence „The Life of a Showgirl”?", o: ["Sabrina Carpenter", "Olivia Rodrigo", "Lana Del Rey", "Phoebe Bridgers"], c: 0,
        e: "Carpenter supportowała Swift na części koncertów Eras Tour. Lana Del Rey gościła na „Snow on the Beach” z „Midnights”." }
    ]
  },
  {
    name: "Rekordy i nagrody", q: [
      { q: "Ile razy Taylor Swift zdobyła Grammy za Album Roku?", o: ["2", "3", "4", "5"], c: 2, fix: 1,
        e: "Za „Fearless”, „1989”, „Folklore” i „Midnights”. Jest pierwszą osobą z czterema takimi nagrodami jako główna wykonawczyni." },
      { q: "Która piosenka Swift jest najdłuższą w historii, jaka trafiła na 1. miejsce Billboard Hot 100?", o: ["„All Too Well (10 Minute Version)”", "„Champagne Problems”", "„Marjorie”", "„The Last Great American Dynasty”"], c: 0,
        e: "W listopadzie 2021 r. pobiła rekord „American Pie” Dona McLeana." },
      { q: "Za który teledysk Swift odbierała nagrodę VMA w 2009 r., gdy przerwał jej Kanye West?", o: ["„You Belong with Me”", "„Love Story”", "„Fifteen”", "„White Horse”"], c: 0,
        e: "Kanye wszedł na scenę z tezą, że wygrać powinna Beyoncé. Konflikt wracał w karierze Swift przez kolejne lata." },
      { q: "Ile lat miała Swift, gdy po raz pierwszy wygrała Grammy za Album Roku (za „Fearless”)?", o: ["18", "20", "22", "24"], c: 1, fix: 1,
        e: "Była wtedy najmłodszą zdobywczynią tej nagrody. Rekord odebrała jej później Billie Eilish." },
      { q: "Który tygodnik w 2023 r. wybrał Swift Człowiekiem Roku?", o: ["„Time”", "„Forbes”", "„Rolling Stone”", "„Billboard”"], c: 0,
        e: "Była pierwszą osobą wyróżnioną za osiągnięcia w sztuce. W 2017 r. „Time” wyróżnił ją w grupie „Silence Breakers”." },
      { q: "Ile koncertów liczyła trasa The Eras Tour?", o: ["101", "126", "149", "172"], c: 2, fix: 1,
        e: "Trasa trwała od marca 2023 do grudnia 2024 r. i jako pierwsza w historii przekroczyła 2 mld dolarów przychodu." },
      { q: "W jakim mieście zaczęła się trasa The Eras Tour (marzec 2023)?", o: ["Glendale (Arizona)", "Nashville", "Los Angeles", "Las Vegas"], c: 0,
        e: "Pierwszy koncert odbył się 17 marca 2023 r. na stadionie w Glendale pod Phoenix." },
      { q: "W jakim mieście odbył się ostatni koncert The Eras Tour w grudniu 2024 r.?", o: ["Vancouver", "Toronto", "Nowy Jork", "Londyn"], c: 0,
        e: "Trasa zakończyła się 8 grudnia 2024 r. Wcześniej Swift zagrała sześć koncertów w Toronto." }
    ]
  },
  {
    name: "Biznes i prawa", q: [
      { q: "Kto w 2019 r. przejął wytwórnię Big Machine razem z nagraniami pierwszych sześciu albumów Swift?", o: ["Scooter Braun", "Scott Borchetta", "Jay-Z", "Simon Cowell"], c: 0,
        e: "Firma Ithaca Holdings Brauna kupiła Big Machine. Swift nazwała to najgorszym scenariuszem i postanowiła nagrać płyty od nowa." },
      { q: "Który album jako pierwszy ukazał się w wersji „Taylor's Version” (2021)?", o: ["„Fearless”", "„Red”", "„Speak Now”", "„1989”"], c: 0,
        e: "„Fearless (Taylor's Version)” ukazał się w kwietniu 2021 r., a „Red” w listopadzie tego samego roku." },
      { q: "W którym roku Swift odkupiła nagrania swoich pierwszych albumów?", o: ["2023", "2024", "2025", "Nigdy ich nie odkupiła"], c: 2, fix: 1,
        e: "Ogłosiła to 30 maja 2025 r. Nagrania kupiła od funduszu Shamrock Capital, który wcześniej odkupił je od Brauna." },
      { q: "Pierwszy album, którego nagrania od początku należą do Swift, to:", o: ["„Lover”", "„Reputation”", "„Folklore”", "„1989”"], c: 0,
        e: "„Lover” z 2019 r. był pierwszym po przejściu do Republic Records." },
      { q: "Po chaosie przy sprzedaży biletów na Eras Tour w 2022 r. który serwis musiał się tłumaczyć przed Senatem USA?", o: ["Ticketmaster", "StubHub", "Eventim", "Ticketfly"], c: 0,
        e: "Ticketmaster należy do Live Nation. Przesłuchanie w Senacie w styczniu 2023 r. dotyczyło jego monopolu na rynku biletów." },
      { q: "Który film koncertowy stał się najbardziej dochodowym w historii kin?", o: ["„Taylor Swift: The Eras Tour”", "„Michael Jackson's This Is It”", "„Justin Bieber: Never Say Never”", "„Renaissance: A Film by Beyoncé”"], c: 0,
        e: "Film trafił do kin w październiku 2023 r., z pominięciem dużych studiów, przez sieć AMC." }
    ]
  },
  {
    name: "Życie i fani", q: [
      { q: "Która liczba jest szczęśliwą liczbą Taylor Swift?", o: ["7", "13", "22", "89"], c: 1, fix: 1,
        e: "Urodziła się 13 grudnia 1989 r. Na początku kariery rysowała 13 na dłoni przed koncertami." },
      { q: "W jakim stanie urodziła się Taylor Swift?", o: ["Pensylwania", "Tennessee", "Teksas", "Nowy Jork"], c: 0,
        e: "Urodziła się w West Reading w Pensylwanii, a jako nastolatka przeprowadziła się z rodziną w okolice Nashville." },
      { q: "Jak wabi się kot Swift nazwany po bohaterce serialu „Prawo i porządek: Sekcja specjalna”?", o: ["Olivia Benson", "Meredith Grey", "Benjamin Button", "Detective Stabler"], c: 0,
        e: "Meredith Grey to bohaterka „Chirurgów”, a Benjamin Button to trzeci kot, adoptowany na planie teledysku „ME!”." },
      { q: "W jakiej drużynie NFL gra Travis Kelce?", o: ["Kansas City Chiefs", "Philadelphia Eagles", "Buffalo Bills", "San Francisco 49ers"], c: 0,
        e: "W Eagles grał jego brat Jason. Bracia prowadzą razem podcast „New Heights”." },
      { q: "Gdzie Swift ogłosiła album „The Life of a Showgirl” w sierpniu 2025 r.?", o: ["W podcaście „New Heights”", "Na gali VMA", "Na koncercie w Londynie", "W „Saturday Night Live”"], c: 0,
        e: "Wystąpiła w podcaście braci Kelce. Kilka tygodni później ogłosiła zaręczyny z Travisem." },
      { q: "W którym roku Taylor Swift poślubiła Travisa Kelce?", o: ["2024", "2025", "2026", "Jeszcze się nie pobrali"], c: 2, fix: 1,
        e: "Zaręczyli się w sierpniu 2025 r., a ślub odbył się w lipcu 2026 r. w Nowym Jorku." },
      { q: "Ile koncertów Eras Tour Swift zagrała w Warszawie w sierpniu 2024 r.?", o: ["1", "2", "3", "4"], c: 2, fix: 1,
        e: "Zagrała 1, 2 i 3 sierpnia na PGE Narodowym. Były to jej pierwsze koncerty w Polsce." },
      { q: "Dlaczego odwołano koncerty Eras Tour w Wiedniu w sierpniu 2024 r.?", o: ["Udaremniono planowany zamach terrorystyczny", "Przez upały", "Przez chorobę Swift", "Przez strajk obsługi stadionu"], c: 0,
        e: "Austriackie służby zatrzymały podejrzanych o planowanie ataku. Fani śpiewali wtedy na wiedeńskich ulicach." },
      { q: "W jakim filmie Swift zagrała kotkę Bombalurinę (2019)?", o: ["„Koty”", "„Walentynki”", "„Dawca pamięci”", "„Amsterdam”"], c: 0,
        e: "„Koty” Toma Hoopera były kinową klapą. W „Walentynkach” (2010) Swift zadebiutowała jako aktorka." },
      { q: "Kto zagrał główne role w „All Too Well: The Short Film” wyreżyserowanym przez Swift?", o: ["Sadie Sink i Dylan O'Brien", "Zendaya i Tom Holland", "Millie Bobby Brown i Noah Schnapp", "Emma Stone i Ryan Gosling"], c: 0,
        e: "Krótki metraż z 2021 r. towarzyszył 10-minutowej wersji piosenki. Sadie Sink znana jest ze „Stranger Things”." },
      { q: "Jak Swift podpisała we wrześniu 2024 r. post z poparciem dla Kamali Harris?", o: ["„Childless Cat Lady”", "„Swiftie in Chief”", "„Taylor's Version”", "„Cat Mom for America”"], c: 0,
        e: "Nawiązała do wcześniejszych słów J.D. Vance'a o „bezdzietnych kociarach”." }
    ]
  }
];
