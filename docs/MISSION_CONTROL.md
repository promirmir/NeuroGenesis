# NeuroGenesis Mission Control — standard docelowego interfejsu

**Autorstwo publiczne: Miron przy pomocy AI.** Wersja badawcza 0.7.x — bez nieuzasadnionych deklaracji AGI.

## Co faktycznie wyświetla nowy ekran

Główny ekran w opcjonalnym **Qt / PySide6** został przebudowany z trzech tekstowych kafli na prawdziwe centrum pracy lokalnego systemu:

- **NEURAL FABRIC / SYSTEM MAP:** duże, interaktywne płótno z grafem dokładnie istniejących neuronów i połączeń zapisanej małej sieci LIF, wagami, wartościami potencjału oraz śladami. Przesuwanie lewym przyciskiem i powiększanie kółkiem; po wskazaniu neuronu pokazuje się jego odczyt. Tylko faktyczny nowy krok uruchamia maks. 0,8 sekundy podświetlenia zarejestrowanych impulsów. Podświetlenie poruszające się wzdłuż linii **to umowna animacja zdarzenia, nie zmierzona prędkość przewodzenia**. Brak nowych kroków oznacza brak sztucznych błysków.
- **Live data:** cztery czytelne kafle rzeczywistych kroków LIF, neuronów, synaps i dokumentów w SQLite. Po prawej wykres liczby świecących neuronów z ostatniej zapisanej maski spike (jedna próbka tylko po odczycie nowszego kroku) oraz dziennik faktycznie zaobserwowanych zmian. Bez procentu inteligencji czy świadomości.
- **System modules:** precyzyjne stany uprawnień HTTPS, liczby wersji dokumentów, zapisanych kroków LIF i *oddzielnego* worker'a PyTorch. Schemat nie twierdzi, że LIF jest połączony z generatorem odpowiedzi. Przyciski przechodzą do rzeczywistych paneli Rozmowa, Badanie i Trening.
- **Research, Chat, Knowledge, Safety and Training:** dotychczasowe funkcje zachowane, bez zmiany SQLite, logicznego silnika, domyślnych zezwoleń lub checkpointów. Monitor treningu pokazuje tylko realne zdarzenia loss. Klawisze Ctrl+1…Ctrl+7 przełączają panele; przewijany ekran główny i skalowanie Qt dostosowują się do różnych rozmiarów okna.

## Co pozostaje oddzielnym eksperymentem

NeuroGenesis ma dwa odrębne mechanizmy: małą sieć LIF opartą na impulsach i model Foundation Brain (PyTorch GRU, predykcja bajtów). Pokazany graf to tylko LIF. Nie udajemy setek miliardów synaps ani stanu ukrytych neuronów GRU, kiedy nie jest mierzony. Nie ma niezmierzonego wykresu GPU, nieprawdziwego licznika uczenia czy ciągłej animacji bez nowych wyników. Wniosek jakościowy wymaga niezależnych testów QA i porównań, a nie lepszego wyglądu.

## Windows — jak uruchomić prawdziwe Qt

**Publicznie dostępny EXE Windows nadal uruchamia Tkinter.** Przed ogłoszeniem publicznego EXE Qt trzeba spełnić odpowiednie obowiązki LGPLv3, przygotować kompletny pakiet DLL/notice/source/replaceability oraz przeprowadzić ręczne testy. Udane spakowanie techniczne nie oznacza zgody na dystrybucję.

Dostępna jest natomiast łatwiejsza droga do uruchomienia **prawdziwej aplikacji Qt ze źródeł**, bez redystrybucji Qt DLL w repozytorium. Pobierz cały kod z GitHub, zainstaluj lokalnie Python 3.12 x64 i uruchom dwuklikiem:

`Launch-NeuroGenesis-Mission-Control.cmd`

Skrypt tworzy prywatny folder `.venv` (ignorowany przez Git). Przed pierwszym pobraniem zależności PySide6/pip wymaga wyraźnego potwierdzenia połączenia z Internetem. Następne uruchomienia używają istniejącego środowiska. Nie dotyka istniejącej lokalnej pamięci; sam Qt domyślnie ma wyłączony HTTPS. Nie jest to jeszcze niezależna instalka EXE i wymaga Pythona.

## Obraz rzeczywistej aplikacji w CI

`scripts/qt_visual_smoke.py` na Windows/Ubuntu otwiera rzeczywisty Command Center z rzeczywistymi wyliczeniami, ale **wyłącznie na celowo wygenerowanej, fikcyjnej lokalnej bazie SQLite**. Wytwarza PNG (Qt `QWidget.grab()`), który testy GitHub Actions udostępniają jako plik `Mission-Control-Visual-<OS>`. To prawdziwy zrzut uruchomionego Qt, nie makieta generowana przez model graficzny. Nie zawiera prywatnych materiałów użytkownika. Dokumentacja nie twierdzi, że jest to ręczny test DPI na jego monitorze.

## Bramka zakończenia migracji

Przed zastąpieniem Tk publicznym Qt:
1. Ostateczny przejrzysty ekran na Windows w minimum 1366×768 i 1920×1080, ręczne sprawdzenie skalowania 125/150/200%, poprawnej nawigacji, dostępności klawiaturowej i odpowiedniej liczby FPS.
2. Przejście wszystkich testów Python 3.11–3.13, rzeczywistego PyTorch CPU, Qt Windows/Ubuntu, spakowanego technicznie Qt, starego Tk EXE i prywatności. Brak automatycznego Internetu, fałszywych danych oraz migracji usuwających pamięć.
3. Rozwiązanie zobowiązań prawnych przy rozpowszechnianiu PySide6/Qt: licencje, odpowiednia kopia kodu bibliotek/written offer pod kontrolą wydawcy, możliwość zastąpienia bibliotek dynamicznych, wymagane informacje i licencje elementów trzecich. Oficjalny opis: https://www.qt.io/development/open-source-lgpl-obligations .
4. Publikacja pakietu ze ścisłym SHA kodu, pełną sumą SHA-256, plikiem poświadczającym użyte biblioteki oraz niezależnym testem uruchomienia na czystym Windows.

## Dlaczego nie scalamy starej gałęzi

`feat/live-neural-network-command-visualization-20261108` jest wcześniejszym, rozbieżnym podejściem (Qt `qt_neural_view.py`, Tk `tk_neural_view.py`). Jego HEAD `8c44fcdd` miał czerwone testy metadanych `0.8.0` kontra README `0.7.0`, a gałąź była zarówno przed, jak i za `main`. Zawierała częściowo podobne elementy. Obecna migracja świadomie przenosi użyteczne aspekty podświetlenia związanego z rzeczywistym krokiem **bez przepisywania bieżącej bazy i bez pozostawiania dwóch aktywnych rendererów**. Starej gałęzi nie usuwamy ani nie scalamy automatycznie.
