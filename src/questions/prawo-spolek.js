const BANK_KSH = [
  {
    name: "Spółki osobowe", q: [
      { q: "Kiedy wierzyciel spółki jawnej może prowadzić egzekucję z majątku osobistego wspólnika?", o: ["Gdy egzekucja z majątku spółki okaże się bezskuteczna", "Od razu, równolegle z egzekucją ze spółki", "Tylko gdy wspólnik prowadził sprawy spółki", "Nigdy, wspólnik odpowiada tylko wkładem"], c: 0,
        e: "To subsydiarność odpowiedzialności z art. 31 KSH. Pozew można złożyć wcześniej, ale egzekucja z majątku wspólnika wchodzi w grę dopiero po bezskutecznej egzekucji ze spółki." },
      { q: "Za co NIE odpowiada partner w spółce partnerskiej?", o: ["Za zobowiązania z wykonywania wolnego zawodu przez innych partnerów", "Za zobowiązania z umów najmu zawartych przez spółkę", "Za zobowiązania podatkowe spółki", "Za własne błędy w wykonywaniu zawodu"], c: 0,
        e: "Tak stanowi art. 95 KSH, chyba że umowa spółki stanowi inaczej. Za pozostałe zobowiązania spółki partner odpowiada jak wspólnik jawny." },
      { q: "Co się dzieje, gdy nazwisko komandytariusza znajdzie się w firmie spółki komandytowej?", o: ["Odpowiada wobec osób trzecich jak komplementariusz", "Wpis jest nieważny z mocy prawa", "Traci prawo do zysku", "Musi podwyższyć sumę komandytową"], c: 0,
        e: "Art. 104 § 4 KSH. Firma spółki komandytowej powinna zawierać nazwisko co najmniej jednego komplementariusza." },
      { q: "W jakiej formie zawiera się umowę spółki komandytowej (poza systemem S24)?", o: ["Aktu notarialnego", "Pisemnej pod rygorem nieważności", "Pisemnej z podpisami notarialnie poświadczonymi", "Dowolnej"], c: 0,
        e: "Umowa spółki jawnej wymaga tylko formy pisemnej pod rygorem nieważności. Spółkę komandytową można też założyć na wzorcu w systemie S24." },
      { q: "Ile wynosi minimalny kapitał zakładowy spółki komandytowo-akcyjnej?", o: ["5 000 zł", "50 000 zł", "100 000 zł", "Nie ma minimum"], c: 1, fix: 1,
        e: "50 tys. zł. Akcjonariusz S.K.A. nie odpowiada za zobowiązania spółki, a komplementariusz odpowiada całym majątkiem." },
      { q: "Od kiedy spółki komandytowe co do zasady są podatnikami CIT?", o: ["Od 2014", "Od 2019", "Od 2021", "Od 2024"], c: 2, fix: 1,
        e: "Od 1 stycznia 2021 r., a spółki, które wybrały odroczenie, od 1 maja 2021 r. Spółki komandytowo-akcyjne były podatnikami CIT już od 2014 r." },
      { q: "Gdzie uregulowano spółkę cywilną?", o: ["W Kodeksie cywilnym", "W Kodeksie spółek handlowych", "W Prawie przedsiębiorców", "W ustawie o swobodzie działalności gospodarczej"], c: 0,
        e: "Spółka cywilna to umowa z art. 860–875 Kodeksu cywilnego. Nie ma osobowości prawnej, a przedsiębiorcami są jej wspólnicy." },
      { q: "Jak może działać komandytariusz w imieniu spółki komandytowej?", o: ["Tylko jako pełnomocnik albo prokurent", "Zawsze, jak każdy wspólnik", "Tylko za zgodą sądu rejestrowego", "W żaden sposób"], c: 0,
        e: "Komandytariusz z mocy prawa nie reprezentuje spółki (art. 117 i 118 KSH). Jeśli działa bez umocowania, odpowiada jak komplementariusz." }
    ]
  },
  {
    name: "Sp. z o.o.", q: [
      { q: "Jaki jest minimalny kapitał zakładowy i minimalna wartość nominalna udziału w sp. z o.o.?", o: ["5 000 zł i 50 zł", "5 000 zł i 1 zł", "10 000 zł i 100 zł", "1 zł i 1 zł"], c: 0,
        e: "Tak stanowi art. 154 KSH. 1 zł kapitału akcyjnego to minimum w prostej spółce akcyjnej." },
      { q: "Który artykuł KSH przewiduje odpowiedzialność członków zarządu sp. z o.o. za jej zobowiązania przy bezskutecznej egzekucji?", o: ["Art. 293", "Art. 299", "Art. 233", "Art. 586"], c: 1, fix: 1,
        e: "Art. 299. Członek zarządu może się zwolnić m.in., jeśli wykaże, że we właściwym czasie złożono wniosek o upadłość. Art. 293 dotyczy szkody wyrządzonej samej spółce." },
      { q: "Przy jakiej stracie zarząd sp. z o.o. musi zwołać zgromadzenie w sprawie dalszego istnienia spółki?", o: ["Gdy przekracza sumę kapitałów zapasowego i rezerwowych oraz połowy kapitału zakładowego", "Gdy przekracza cały kapitał zakładowy", "Gdy przekracza jedną trzecią kapitału zakładowego", "Gdy spółka ma stratę dwa lata z rzędu"], c: 0,
        e: "To art. 233 KSH. W spółce akcyjnej (art. 397) próg to jedna trzecia kapitału zakładowego." },
      { q: "Kiedy w sp. z o.o. trzeba powołać radę nadzorczą lub komisję rewizyjną?", o: ["Gdy kapitał przekracza 500 tys. zł i jest więcej niż 25 wspólników", "Gdy kapitał przekracza 100 tys. zł", "Gdy spółka zatrudnia ponad 50 osób", "Zawsze"], c: 0,
        e: "Oba warunki z art. 213 § 2 KSH muszą być spełnione łącznie. W pozostałych spółkach organ nadzoru jest dobrowolny." },
      { q: "Jaką większością głosów zmienia się umowę sp. z o.o.?", o: ["Bezwzględną", "2/3 głosów", "3/4 głosów", "Jednomyślnie"], c: 1, fix: 1,
        e: "Art. 246 KSH. Istotna zmiana przedmiotu działalności wymaga już 3/4 głosów." },
      { q: "Ile maksymalnie głosów może dawać jeden uprzywilejowany udział w sp. z o.o.?", o: ["2", "3", "5", "Bez ograniczeń"], c: 1, fix: 1,
        e: "Art. 174 § 4 KSH. W spółce akcyjnej limit to 2 głosy na akcję." },
      { q: "Kto nie może samodzielnie zawiązać sp. z o.o.?", o: ["Inna jednoosobowa sp. z o.o.", "Osoba fizyczna", "Spółka akcyjna", "Fundacja"], c: 0,
        e: "Zakaz z art. 151 § 2 KSH ma zapobiegać tworzeniu łańcuchów spółek bez żadnego wspólnika-człowieka." },
      { q: "W jakim terminie trzeba odbyć zwyczajne zgromadzenie wspólników sp. z o.o.?", o: ["W ciągu 3 miesięcy po roku obrotowym", "W ciągu 6 miesięcy po roku obrotowym", "Do końca roku kalendarzowego", "W ciągu 30 dni od sporządzenia sprawozdania"], c: 1, fix: 1,
        e: "Art. 231 KSH. Zgromadzenie zatwierdza sprawozdania, dzieli zysk i udziela absolutorium." },
      { q: "Jak nazywa się powództwo wspólnika o naprawienie szkody wyrządzonej spółce, gdy spółka sama nie pozwała (art. 295 KSH)?", o: ["Actio pro socio", "Actio pauliana", "Actio negatoria", "Actio de in rem verso"], c: 0,
        e: "Actio pauliana to skarga pauliańska wierzyciela z Kodeksu cywilnego." },
      { q: "Co od października 2022 r. chroni członka zarządu działającego „w granicach uzasadnionego ryzyka gospodarczego”?", o: ["Reguła biznesowej oceny sytuacji (business judgment rule)", "Zasada pomocniczości", "Domniemanie dobrej wiary z Kodeksu cywilnego", "Ubezpieczenie D&O"], c: 0,
        e: "Reguła trafiła do art. 293 § 3 i art. 483 § 3 KSH razem z prawem holdingowym." }
    ]
  },
  {
    name: "S.A. i P.S.A.", q: [
      { q: "Jaki jest minimalny kapitał zakładowy i minimalna wartość nominalna akcji w spółce akcyjnej?", o: ["100 000 zł i 1 grosz", "100 000 zł i 1 zł", "50 000 zł i 1 grosz", "500 000 zł i 10 zł"], c: 0,
        e: "Art. 308 KSH. Spółka europejska (SE) potrzebuje co najmniej 120 tys. euro." },
      { q: "Od kiedy można zakładać prostą spółkę akcyjną?", o: ["Od 1 stycznia 2020", "Od 1 lipca 2021", "Od 1 marca 2021", "Od 13 października 2022"], c: 1, fix: 1,
        e: "1 marca 2021 r. weszła w życie dematerializacja akcji, a 13 października 2022 r. prawo holdingowe." },
      { q: "Jaki jest minimalny kapitał akcyjny prostej spółki akcyjnej?", o: ["1 zł", "100 zł", "5 000 zł", "Nie ma minimum"], c: 0, fix: 1,
        e: "Kapitał akcyjny nie jest podzielony na wartości nominalne, a akcje P.S.A. nie mają wartości nominalnej." },
      { q: "Który typ spółki może mieć radę dyrektorów zamiast zarządu i rady nadzorczej (system monistyczny)?", o: ["Prosta spółka akcyjna", "Spółka akcyjna", "Sp. z o.o.", "Spółka komandytowo-akcyjna"], c: 0,
        e: "W P.S.A. wspólnicy wybierają między zarządem z opcjonalną radą nadzorczą a radą dyrektorów." },
      { q: "Ile maksymalnie głosów może dawać akcja uprzywilejowana w spółce akcyjnej (niepublicznej)?", o: ["2", "3", "5", "10"], c: 0, fix: 1,
        e: "Art. 352 KSH. Spółka publiczna nie może w ogóle mieć akcji uprzywilejowanych co do głosu." },
      { q: "Jaką większością zmienia się statut spółki akcyjnej?", o: ["Bezwzględną", "2/3 głosów", "3/4 głosów", "4/5 głosów"], c: 2, fix: 1,
        e: "Art. 415 KSH wymaga 3/4 głosów. W sp. z o.o. do zmiany umowy wystarczą 2/3." },
      { q: "Ile procent kapitału musi mieć akcjonariusz, by przymusowo wykupić akcje mniejszości (squeeze-out, art. 418 KSH)?", o: ["75%", "90%", "95%", "99%"], c: 2, fix: 1,
        e: "Do 5 akcjonariuszy mających łącznie co najmniej 95% kapitału może wykupić pozostałych. Art. 418¹ daje mniejszości odwrotne prawo żądania wykupu (sell-out)." },
      { q: "Do jakiej części kapitału zakładowego i na jak długo statut może upoważnić zarząd do podwyższenia kapitału (kapitał docelowy)?", o: ["Do 3/4, na 3 lata", "Do 1/2, na 5 lat", "Do całości, na 2 lata", "Do 1/3, na rok"], c: 0, fix: 1,
        e: "Art. 444 KSH. Upoważnienie można odnawiać kolejnymi zmianami statutu." },
      { q: "Od kiedy akcje wszystkich spółek akcyjnych muszą być zdematerializowane (w rejestrze akcjonariuszy lub depozycie)?", o: ["Od 1 stycznia 2020", "Od 1 marca 2021", "Od 1 lipca 2021", "Od 13 października 2022"], c: 1, fix: 1,
        e: "Papierowe dokumenty akcji straciły moc 1 marca 2021 r. Nowelizacja z lutego 2026 r. domyka tę reformę." },
      { q: "Przy jakiej stracie zarząd spółki akcyjnej musi zwołać walne zgromadzenie w sprawie dalszego istnienia spółki?", o: ["Gdy przekracza sumę kapitałów zapasowego i rezerwowych oraz jednej trzeciej kapitału zakładowego", "Gdy przekracza połowę kapitału zakładowego", "Gdy przekracza cały kapitał zakładowy", "Gdy wynosi ponad milion złotych"], c: 0,
        e: "Art. 397 KSH. W sp. z o.o. próg to połowa kapitału zakładowego (art. 233)." }
    ]
  },
  {
    name: "Rejestr i różności", q: [
      { q: "Jaki akt obowiązywał przed Kodeksem spółek handlowych?", o: ["Kodeks handlowy z 1934 r.", "Kodeks zobowiązań z 1933 r.", "Ustawa o przedsiębiorstwach państwowych z 1981 r.", "Prawo działalności gospodarczej z 1999 r."], c: 0,
        e: "KSH uchwalono 15 września 2000 r. i obowiązuje od 1 stycznia 2001 r. Kodeks handlowy był rozporządzeniem Prezydenta RP." },
      { q: "Ile typów spółek handlowych przewiduje dziś KSH?", o: ["5", "6", "7", "8"], c: 2, fix: 1,
        e: "Jawna, partnerska, komandytowa, komandytowo-akcyjna, z o.o., prosta spółka akcyjna i akcyjna. Spółka cywilna nie jest handlowa." },
      { q: "Od kiedy wszystkie wnioski do KRS składa się wyłącznie elektronicznie?", o: ["Od 1 stycznia 2019", "Od 1 lipca 2021", "Od 1 marca 2021", "Od 1 stycznia 2023"], c: 1, fix: 1,
        e: "Wnioski składa się przez Portal Rejestrów Sądowych. Papierowe akta rejestrowe zastąpiły elektroniczne." },
      { q: "Komu nie można udzielić prokury?", o: ["Osobie prawnej", "Członkowi rady nadzorczej sp. z o.o.", "Pracownikowi spółki", "Cudzoziemcowi"], c: 0,
        e: "Prokurentem może być tylko osoba fizyczna z pełną zdolnością do czynności prawnych (art. 109² KC). Członek rady nadzorczej nie może jednak być prokurentem z innego powodu: KSH zakazuje łączenia tych funkcji." },
      { q: "Od kiedy KSH reguluje „grupę spółek” i wiążące polecenia spółki dominującej?", o: ["Od 1 stycznia 2001", "Od 1 lipca 2021", "Od 13 października 2022", "Od 1 stycznia 2025"], c: 2, fix: 1,
        e: "Tzw. prawo holdingowe wprowadziło też m.in. doradcę rady nadzorczej i regułę biznesowej oceny sytuacji." },
      { q: "Jakim skrótem oznacza się prostą spółkę akcyjną w jej firmie?", o: ["P.S.A.", "PSA sp.", "S.P.A.", "p.s.a. sp. k."], c: 0,
        e: "Dla spółki akcyjnej to S.A., dla komandytowo-akcyjnej S.K.A., a dla komandytowej sp.k." },
      { q: "Od kiedy w Polsce można zakładać fundację rodzinną?", o: ["Od 1 lipca 2021", "Od 22 maja 2023", "Od 1 stycznia 2024", "Od 13 października 2022"], c: 1, fix: 1,
        e: "Fundację rodzinną reguluje osobna ustawa, nie KSH. Ma służyć sukcesji firm rodzinnych." },
      { q: "Jak nazywa się zasada, że spółka przekształcona przejmuje wszystkie prawa i obowiązki spółki przekształcanej?", o: ["Zasada kontynuacji", "Sukcesja uniwersalna częściowa", "Zasada jawności", "Zasada pierwszeństwa"], c: 0,
        e: "Art. 553 KSH. Przy przekształceniu nie powstaje nowy podmiot, zmienia się tylko forma prawna." },
      { q: "W jakim systemie można założyć sp. z o.o. przez internet na wzorcu umowy?", o: ["S24", "CEIDG", "e-KRS Plus", "ePUAP Biznes"], c: 0,
        e: "Tak założona spółka powinna zostać wpisana do KRS następnego dnia. CEIDG to ewidencja przedsiębiorców będących osobami fizycznymi." }
    ]
  }
];
