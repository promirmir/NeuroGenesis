# NeuroGenesis 0.13.0 — trwała pamięć korekt w rzeczywistej rozmowie

**Autor publiczny:** Miron przy pomocy AI.

## Co działa

NeuroGenesis posiada teraz oddzielny mechanizm **uczenia na podstawie zatwierdzonej informacji zwrotnej użytkownika**, połączony z tym samym lokalnym modelem Qwen3-1.7B, który odpowiada w głównym oknie.

Po otrzymaniu niezadowalającej lub błędnej odpowiedzi można nacisnąć **„PAMIĘĆ POPRAWEK / ZAPAMIĘTAJ I POPRAW”**. Okno wczytuje ostatnie pytanie z pamięci RAM, ale **nie zapisuje automatycznie odpowiedzi modelu**. Użytkownik wpisuje poprawioną treść i świadomie potwierdza zapis. Dostępne są także: przegląd istniejących wpisów, edycja wcześniej zatwierdzonej korekty i jawne usunięcie wybranego wpisu.

Każde zatwierdzone pytanie i poprawka trafiają do osobnej, prywatnej bazy SQLite `approved_corrections.sqlite3`. Ponowne uruchomienie EXE nie usuwa tej wiedzy. Dotychczasowe `experiences.sqlite3`, indeks TXT, zapis ACF i wagi GGUF nie wymagają migracji.

## Jak zmienia to faktyczne odpowiedzi

1. Przy kolejnym pytaniu aplikacja przeszukuje zatwierdzone korekty, porównując je z **pytaniem**, a nie z treścią poprawnej odpowiedzi.
2. Identyczne pytanie wybiera jego zatwierdzoną korektę. Dla przeformułowania potrzeba minimum dwóch wspólnych znaczących wyrazów i dopasowania co najmniej połowy wyrazów kluczowych nowego pytania. Remis między dwiema korektami powoduje **wstrzymanie** wykorzystania obu (brak arbitralnego zgadywania).
3. Do kontekstu rzeczywistej inferencji Qwen może zostać dodana **maksymalnie jedna** korekta, razem z najwyżej trzema wcześniej pobranymi fragmentami TXT/HTTPS. Przechowywana poprawka jest oznaczona jako `zatwierdzona poprawka użytkownika`, ale traktowana jako **niezaufane DANE**, nie instrukcja systemowa. Treść pytania zapisanego w pamięci nie jest ponownie doklejana do promptu.
4. Gdy zatwierdzona korekta jest dostępna, ma pierwszeństwo przed eksperymentalnym doborem źródła przez ACF lub kontrolą tematu. Nie można wypierać świadomie zapisanej poprawki spekulatywną prognozą neuronową.
5. Model pokazuje w wyniku etykietę rzeczywiście użytego źródła i fakt, że zastosowano zapamiętaną korektę. W trybie kontrolnym `use_context=False` korekty są wyłączone tak samo jak TXT i HTTPS, więc nie zniekształcają porównań A/B/C/D.

## Prywatność, granice i uprawnienia

- **Brak automatycznego zapisu rozmów, pełnych odpowiedzi, danych z internetu czy pytań do bazy korekt.** Zapisanie konkretnej treści wymaga każdorazowo jawnego zatwierdzenia.
- To **lokalne, nieszyfrowane SQLite**. Osoba mająca uprawnienia do odczytu plików profilu może zapoznać się z korektami; na tym etapie nie należy zapisywać tam sekretów ani haseł. Nie ma transferu do chmury (poza uwierzytelnionym lokalnym `127.0.0.1` używanym przez silnik Qwen).
- `ZAPOMNIJ` usuwa wpis z aktywnego wyszukiwania i tabeli po osobnym potwierdzeniu. SQLite używa `PRAGMA secure_delete=ON`, lecz program **nie gwarantuje fizycznego usunięcia kopii z SSD, migawek systemowych ani istniejących backupów**.
- Limit 250 wpisów; pojedyncze pytanie do 512 znaków, treść poprawki do 720 znaków. Powtórne zatwierdzenie tego samego pytania zastępuje wcześniejszą treść i zwiększa numer wersji. Nie zachowujemy ukrytej historii starych odpowiedzi.
- Korekta może zawierać błąd. Samo zatwierdzenie przez operatora **nie dowodzi zgodności z faktami**. Tekst jest dostarczany do LLM jako dane, z dotychczasowym zabezpieczeniem przed prompt injection.
- To **retrieval-augmented memory**, a nie gradientowe trenowanie wag Qwen, sztuczna samoświadomość, samoczynne udowadnianie poprawności lub pełne rozumienie kontekstu.
- Nie zgłaszamy wzrostu jakości w niezależnym benchmarku, dopóki nie przeprowadzimy rzeczywistego testu na wcześniej nieużytych przypadkach.

## Testy i potwierdzenie prawdziwej inferencji

Testy jednostkowe obejmują: domyślną odmowę niezatwierdzonego zapisu, odczyt po zamknięciu i ponownym otwarciu bazy, poprawkę wcześniej błędnego faktu, brak niejawnej historii wersji, zbyt luźne i niejednoznaczne skojarzenia, zatwierdzone usuwanie, limity i kontrolę prompt injection.

Obowiązkowy pełny test wydania Windows uruchamia **oryginalny lokalny Qwen z gotowego jednoplikowego EXE**, tworzy w tymczasowym katalogu rzeczywistą bazę SQLite z zatwierdzonym syntetycznym kodem testowym, po czym wymaga, aby model w odpowiedzi faktycznie odtworzył podany kod. Po sprawdzeniu usuwa dane testowe. Taki test potwierdza konkretną zdolność przypomnienia zatwierdzonej poprawki; **nie jest** niezależnym dowodem uogólnionej inteligencji.

## Kolejny pomiar

Warto zbudować oddzielny, niepodlegający przeciekowi zestaw korekt i pytań kontrolnych z parafrazami, błędnymi i sprzecznymi źródłami, a następnie porównać identyczny model z pamięcią i bez niej. Przy kolejnych etapach trzeba ocenić także negatywny transfer (sytuacje, kiedy niepowiązana korekta pogarsza odpowiedź), miary kalibracji i zachowanie pamięci po restarcie.

**Stan naukowy:** implementacja realnej, jawnie kontrolowanej pamięci długoterminowej i jej użycia w rozmowie — bez twierdzenia o aktualizacji wag ani przełomie AGI.
