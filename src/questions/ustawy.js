const BANK_USTAWY = [
  {
    name: "Ustawa Kamilka", q: [
      { q: "Z jakiej daty jest ustawa, którą nazywa się „ustawą Kamilka” (nowelizacja Kodeksu rodzinnego i opiekuńczego)?", o: ["7 lipca 2023 r.", "28 lipca 2023 r.", "30 sierpnia 2023 r.", "15 lutego 2024 r."], c: 1, fix: 1,
        e: "To ustawa z 28 lipca 2023 r. (Dz.U. 2023 poz. 1606). Większość przepisów weszła w życie 15 lutego 2024 r., a część wcześniej, w sierpniu 2023 r." },
      { q: "Kiedy weszła w życie większość przepisów ustawy Kamilka?", o: ["1 stycznia 2024 r.", "15 lutego 2024 r.", "1 lipca 2024 r.", "1 stycznia 2025 r."], c: 1, fix: 1,
        e: "Większość przepisów zaczęła obowiązywać 15 lutego 2024 r. Wcześniej, w sierpniu 2023 r., weszła tylko ich część." },
      { q: "Ile lat miał Kamilek z Częstochowy, po którego śmierci uchwalono ustawę?", o: ["6 lat", "7 lat", "8 lat", "9 lat"], c: 2, fix: 1,
        e: "Ośmioletni chłopiec zmarł po znęcaniu się nad nim przez ojczyma. Jego śmierć dała impuls do zmian w prawie." },
      { q: "Jak nazywa się procedura z ustawy Kamilka, czyli obowiązkowa analiza najpoważniejszych przypadków przemocy wobec dzieci?", o: ["Niebieska Karta", "Serious Case Review", "Standardy ochrony małoletnich", "Rejestr zdarzeń krytycznych"], c: 1,
        e: "Serious Case Review to analiza najpoważniejszych przypadków przemocy wobec dzieci. „Niebieska Karta” to starsza procedura wobec przemocy w rodzinie." },
      { q: "Co według ustawy Kamilka wchodzi w skład standardów ochrony małoletnich, które muszą wdrożyć podmioty pracujące z dziećmi?", o: ["Pozyskiwanie zaświadczeń o niekaralności z Krajowego Rejestru Karnego", "Badania psychologiczne wszystkich rodziców", "Monitoring wizyjny w każdym pomieszczeniu", "Roczne szkolenie z pierwszej pomocy dla uczniów"], c: 0,
        e: "Standardy obejmują m.in. sprawdzanie niekaralności osób pracujących z dziećmi w Krajowym Rejestrze Karnym." },
      { q: "Którą ustawę zasadniczo zmienia ustawa Kamilka?", o: ["Kodeks karny", "Kodeks rodzinny i opiekuńczy", "Kodeks postępowania cywilnego", "Kodeks pracy"], c: 1,
        e: "Pełny tytuł to ustawa o zmianie ustawy – Kodeks rodzinny i opiekuńczy oraz niektórych innych ustaw." },
    ]
  },
  {
    name: "Ustawa o przeciwdziałaniu narkomanii", q: [
      { q: "Z jakiej daty jest obowiązująca ustawa o przeciwdziałaniu narkomanii?", o: ["24 kwietnia 1997 r.", "29 lipca 2005 r.", "1 kwietnia 2011 r.", "20 lipca 2018 r."], c: 1, fix: 1,
        e: "To ustawa z 29 lipca 2005 r. Zastąpiła wcześniejszą ustawę z 24 kwietnia 1997 r. Późniejsze daty to nowelizacje." },
      { q: "Który artykuł ustawy o przeciwdziałaniu narkomanii, dodany w 2011 r., pozwala umorzyć postępowanie przy nieznacznej ilości środka?", o: ["Art. 62", "Art. 62a", "Art. 62b", "Art. 59"], c: 1,
        e: "Art. 62a pozwala prokuratorowi i sądowi umorzyć postępowanie, ale nie depenalizuje posiadania: art. 62 pozostał bez zmian." },
      { q: "Kiedy weszła w życie nowelizacja z 2011 r., która dodała art. 62a?", o: ["1 kwietnia 2011 r.", "1 lipca 2011 r.", "9 grudnia 2011 r.", "1 stycznia 2012 r."], c: 2, fix: 1,
        e: "Ustawa nowelizująca jest z 1 kwietnia 2011 r., ale w życie weszła dopiero 9 grudnia 2011 r." },
      { q: "Jakiego pojęcia z przepisów karnych ustawa o przeciwdziałaniu narkomanii nie definiuje?", o: ["„Środek odurzający”", "„Znaczna ilość”", "„Środek zastępczy”", "„Nowa substancja psychoaktywna”"], c: 1,
        e: "Ustawa nie mówi, ile to „znaczna” ani „nieznaczna” ilość. Ocenia to sąd na podstawie okoliczności sprawy i orzecznictwa." },
      { q: "W którym roku do ustawy o przeciwdziałaniu narkomanii trafiło pojęcie „środka zastępczego”, czyli tzw. dopalaczy?", o: ["2005", "2010", "2013", "2018"], c: 1, fix: 1,
        e: "Nowelizacja z października 2010 r. wprowadziła środki zastępcze i dała Państwowej Inspekcji Sanitarnej uprawnienia wobec sklepów z dopalaczami." },
      { q: "Od kiedy lekarz może przepisać pacjentowi medyczną marihuanę (art. 33a–33d ustawy)?", o: ["1 stycznia 2017 r.", "1 listopada 2017 r.", "1 maja 2018 r.", "1 października 2019 r."], c: 1, fix: 1,
        e: "Nowelizacja z 7 lipca 2017 r. zaczęła w tej części obowiązywać 1 listopada 2017 r. Receptę może wystawić każdy lekarz, a leki nie są refundowane." },
      { q: "W jakim akcie, według ustawy po nowelizacji z 2018 r., ogłasza się wykaz nowych substancji psychoaktywnych?", o: ["W samej ustawie, w załączniku", "W rozporządzeniu Ministra Zdrowia", "W zarządzeniu Głównego Inspektora Sanitarnego", "W uchwale Sejmu"], c: 1,
        e: "Wykaz ustala rozporządzenie Ministra Zdrowia, więc nowe substancje można obejmować zakazem szybciej niż zmianą ustawy." },
    ]
  },
  {
    name: "Inne mało znane ustawy", q: [
      { q: "Kiedy weszła w życie ustawa o ograniczeniu handlu w niedziele i święta?", o: ["1 stycznia 2018 r.", "1 marca 2018 r.", "1 stycznia 2019 r.", "1 stycznia 2020 r."], c: 1, fix: 1,
        e: "Ustawa z 10 stycznia 2018 r. zaczęła obowiązywać 1 marca 2018 r. Zakaz wprowadzano stopniowo: najpierw handlowe były dwie niedziele w miesiącu." },
      { q: "Ile niedziel handlowych w roku przewidywał docelowy model ustawy z 2018 r., obowiązujący od 2020 r.?", o: ["4", "7", "10", "12"], c: 1, fix: 1,
        e: "To dwie niedziele przed Bożym Narodzeniem, jedna przed Wielkanocą oraz ostatnie niedziele stycznia, kwietnia, czerwca i sierpnia." },
      { q: "W którym roku nowelizacja ustawy o godle, barwach i hymnie ustanowiła 2 maja Dniem Flagi Rzeczypospolitej Polskiej?", o: ["1990", "1999", "2004", "2010"], c: 2, fix: 1,
        e: "Święto ustanowiła nowelizacja uchwalona przez Sejm 20 lutego 2004 r." },
      { q: "Z jakiej daty jest ustawa o godle, barwach i hymnie Rzeczypospolitej Polskiej oraz o pieczęciach państwowych?", o: ["1 sierpnia 1919 r.", "31 stycznia 1980 r.", "9 lutego 1990 r.", "20 lutego 2004 r."], c: 1, fix: 1,
        e: "Pierwotnie dotyczyła Polskiej Rzeczypospolitej Ludowej. W 1990 r. zmieniono jej przepisy, a w 2004 r. dopisano Dzień Flagi." },
      { q: "Z jakiej daty jest ustawa o języku polskim, która powołała Radę Języka Polskiego?", o: ["26 października 1982 r.", "21 sierpnia 1997 r.", "7 października 1999 r.", "16 kwietnia 2004 r."], c: 2, fix: 1,
        e: "Ustawa z 7 października 1999 r. Rada Języka Polskiego działa przy Prezydium Polskiej Akademii Nauk." },
      { q: "Z jakiej daty jest ustawa o ochronie zwierząt?", o: ["13 października 1995 r.", "21 sierpnia 1997 r.", "7 października 1999 r.", "16 kwietnia 2004 r."], c: 1, fix: 1,
        e: "To ustawa z 21 sierpnia 1997 r. Prawo łowieckie jest starsze: z 13 października 1995 r." },
      { q: "Z jakiej daty jest ustawa o pomocy państwa w wychowywaniu dzieci, czyli „500+”?", o: ["15 stycznia 2016 r.", "11 lutego 2016 r.", "11 marca 2016 r.", "1 kwietnia 2016 r."], c: 1, fix: 1,
        e: "Ustawa jest z 11 lutego 2016 r., a w życie weszła 1 kwietnia 2016 r." },
    ]
  },
];
