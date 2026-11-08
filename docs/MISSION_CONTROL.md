## 2026-11-08 — VERIFIED published default Windows Mission Control v0.8.0

- **Root cause fixed:** A user's screenshot showed that the last official onefile `NeuroGenesis.exe` displayed the old plain Tk chat, despite the separate optional Qt Mission Control already being source-tested. This was a delivery mismatch. PR #50 upgraded the **actual default public Windows application**, not just another non-distributed Qt prototype.
- **Merged code:** PR #50 into `main` `8e27f420613adee40b7f94b89760f1514284f743`. Official Release: [v0.8.0-main.8e27f420](https://github.com/promirmir/NeuroGenesis/releases/tag/v0.8.0-main.8e27f420). `NeuroGenesis.exe` Windows x64, 13,094,247 bytes, **SHA-256 `5e48e1c7ecde3b7a066a39c2b71c8a70764351888ff30dc23ba75b53c6fcb44e`**. Verified GitHub Actions post-merge research-core, dedicated real PyTorch CPU, Qt Windows/Ubuntu, public onefile Windows EXE and publisher checks all **SUCCESS**. The real frozen EXE successfully ran both old `--self-test` and new `--ui-self-test` with disposable SQLite and actual Tk widgets.
- **Now visible upon double-click:** fullscreen-capable native Tk Mission Control first tab with dark responsive layout, clear rather than grey notebook tabs, four true brain/knowledge metrics, visible connectome from real recorded LIF synapses, recorded spike trace, real-event journal and permission/memory/brain/Foundation module statuses. The legacy conversation interface was restyled to match, with distinct user/assistant text and visible composer. All old brain/research/memory/recovery functions retained; no database migration/reset or network startup. Window size now respects local screen dimensions; dashboard scrolls on small virtual/laptop screens.
- **Actual visual verification:** Windows CI captured and uploaded `NeuroGenesis-Tk-Mission-Visual` (synthetic only, genuine Tk screenshot; screenshot dimension 1000×676 on constrained hosted desktop), inspected and corrected small-screen clipping; this artifact previews the **dashboard pane**, not a screenshot of the full Tk tab chrome or a physical user laptop. Screenshots from earlier head may differ in layout slightly; exact final source head is `a362411aa555b9506983b055ed8c26e1b41c1b7f` and its Windows screenshot artifact is from that commit.
- **Still distinct:** The released `NeuroGenesis.exe` remains a **polished Tk interface**, not the more advanced optional PySide6/Qt binary. Public Qt EXE packaging remains gated by verified LGPLv3 notices, corresponding library source/source offer controlled by publisher, library replacement/relinking and full runtime license audit. Qt remains available via consent-first `Launch-NeuroGenesis-Mission-Control.cmd` from full repository with Python 3.12.
- **Scientific scope:** no general AI, model-level semantic conversation, brain reconstruction, physical CUDA performance demonstration or validated knowledge of factual entailment is established by this GUI change. LIF trace is not Foundation GRU internals. No fake learning indicators.
- **Follow-up:** do not again recommend downloading prior v0.7.x GUI when asked for the improved interface. Keep the correct v0.8.0 verified link/sha in docs. Avoid additional feature churn until users have validated the release on their own Windows/DPI environment. The historical candidate sections below are superseded by this verified heading.

## 2026-11-08 — VERSION 0.8.0 DEFAULT WINDOWS EXE GUI FIX, pending CI

- Important user-reported mismatch (screenshot): the official 0.7.0 `NeuroGenesis.exe` opened the **old Tk window with empty oversized conversation box**, despite earlier announcement of futuristic Qt Mission Control. Qt had only been tested in source and was **not** the published EXE. The messaging was misleading. This branch fixes the actual shipped front end rather than another demo.
- Source baseline `main` `c2db57b1ab1ef99927f8cd7e17d1b522ae78141e`. Branch `feat/default-exe-mission-dashboard-20261108` changes **default `desktop_launcher.py` → `desktop.launch`** by adding a new first and preselected `CENTRUM` tab with dark premium native Tk layout: true SQLite LIF neural fabric canvas, 4 measured KPI cards, recorded spike-mask trace, actual step-change journal, real SQLite/HTTPS/LIF and separate Foundation module status, navigation actions to preserved chat/brain/internet tabs. Dark readable notebook tab styles, 1450×920 startup, scrollable panel to accommodate lower resolution; no UI data fabrication, no empty chat first screen.
- New `neurogenesis/tk_mission.py` is standard-library Tk and uses **existing** proven `neural_telemetry.py` and `tk_connectome.py`, never touches users' private memories, creates no new database schema and no Qt dependency. Network stays disabled by default. `desktop --ui-self-test` starts **actual widgets** using only a throwaway synthetic SQLite; Windows CI runs it in Python and in the *real frozen public Tk EXE* in addition to existing read-only brain/SQLite smoke. `tests/test_tk_mission.py` verifies persisted steps/synapses, no fabricated idle events, updated real spikes, and network consent state on actual Windows Tk widgets.
- Update package and README metadata to **0.8.0**, including the explicit difference between distributable Tk Mission dashboard and optional richer Qt. Do not promise bundled Qt until independent LGPLv3 source/notice/relinking compliance. The LIF display is not a visual simulation of Foundation GRU or human intelligence; semantic natural QA performance remains an open scientific goal.
- Candidate must pass Python 3.11–3.13, privacy, real Windows source Tk widget tests, **actual frozen EXE --self-test AND --ui-self-test**, Qt Windows/Ubuntu regression and post-merge SHA-verified 0.8.0 release before marking delivered. Do not ask user to redownload 0.7.0: it retains the old default screen.

## Stan zweryfikowany (8 listopada 2026)

PR #48 został scalony do `main` jako `caa544798c5c20ac1cc7cb523e82a9593bd513f2`. Finalne testy jego gałęzi zakończyły się powodzeniem: Python 3.11–3.13, prywatność, Qt Windows/Ubuntu, spakowany technicznie Qt i starszy Windows Tk EXE. Sprawdziłem rzeczywiste zrzuty ekranu w obu systemach; usunięto prostokątne tła napisów i problem czcionek w bezekranowym CI Windows. Wersja Qt jest funkcjonalna *w kodzie źródłowym*, lecz publiczne niezależne Qt EXE wymaga osobnej zgodnej licencyjnie dystrybucji. Nowy launcher `.cmd` wymaga instalacji Python 3.12 i jawnej zgody na pobranie PySide6. Brak AGI, zmierzonej przewagi CUDA i niezależnie potwierdzonej jakości naturalnej rozmowy.

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
