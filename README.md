## NeuroGenesis 0.12.0 — autonomiczny ekran startowy i aktywny agent celów

**Rozwijane w PR (weryfikacja CI przed wydaniem):** zamiast domyślnie otwierać statystyczny Mission Control, nowy Windows EXE od razu pokazuje **NEUROGENESIS**: lokalną rozmowę Qwen3-1.7B, autonomiczne cele z trwałą kolejką, podgląd rzeczywistej sieci LIF i bieżące stany systemu. Model sam ładuje wbudowane wagi; pytanie napisane podczas uruchamiania zostaje w kolejce i jest automatycznie obsługiwane.

**Nowe niezależne zadania:** wpisz cel raz; system tworzy plan, analizuje dostępne zatwierdzone TXT i samodzielnie ponawia analizę po zmianie wiedzy. Raporty z faktycznymi SHA-256 źródeł wymagają zatwierdzenia — nie są automatycznie uznawane za zweryfikowane. Rejestracja numerycznych cech rozmowy do badawczego mózgu LIF jest widoczna i może być wyłączona; 40 świeżych bodźców umożliwia osobne badawcze próby autoregulacji. Panel nie udaje impulsów, kiedy nie ma nowych zdarzeń.

Zakładki laboratoryjne, stary system rozmowy i specjalizacja nie zostały usunięte — są teraz pod **Zaawansowane**. [Zobacz dokładnie jak działa autonomia i co jest, a czego nie ma](docs/AUTONOMOUS_HOME.md).

**Wersja 0.12 nie jest jeszcze ukończonym AGI ani autonomicznym trenerem 1,7 mld parametrów.** Główny model nadal jest wstępnie wytrenowanym Qwen; autonomiczne zadania wykonują kontrolowane planowanie i analizę zatwierdzonych źródeł lokalnych. Publikację nowej wersji uzależniamy od testów, rzeczywistej kompilacji Windows i wygenerowania odpowiedzi wewnątrz finalnego EXE.

---

# NeuroGenesis 0.11.0 — COMPLETE OFFLINE AI / Windows

**Miron przy pomocy AI.**

**Najważniejsza zmiana: jedno kompletne EXE z rzeczywistym modelem językowym i silnikiem obliczeniowym.** Wcześniejszy plik 13 MB był tylko interfejsem; jego Model Chat wymagał osobnego Pythona i ręcznie pobieranych wag. To zostało naprawione w nowym profilu FULL.

[**Pobierz najnowszy zweryfikowany NeuroGenesis.exe**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [Suma SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) · [Wszystkie wydania](https://github.com/promirmir/NeuroGenesis/releases)

### Jak to działa

- **Model Chat** automatycznie uruchamia model **Qwen3-1.7B**, Q4_K_M, działający lokalnie przez **llama.cpp CPU** — pełne wagi i DLL są spakowane do tego samego EXE. Nie wymaga Python, PyTorch ani pobrania dodatkowego modelu. Historia tylko w pamięci sesji. Silnik między turami pozostaje załadowany.
- **Trening TXT** działa bez zewnętrznych bibliotek: importuje wskazany plik UTF-8, indeksuje go i pozwala modelowi przywołać właściwy fragment w odpowiedzi. **To pamięć z retrieval/RAG, nie gradientowy trening parametrów sieci.**
- **Aktywny samorozwój wiedzy**: po włączeniu obserwuje jeden zatwierdzony folder z plikami TXT, sam wczytuje nowe/zmienione pliki i aktualizuje bazę podczas działania aplikacji. Bez potajemnego treningu na przypadkowych stronach.
- Stare **Mission Control**, sieć impulsowa LIF i prywatna SQLite pozostają dostępne. Nie kasujemy starej pamięci.
- **Kryterium release:** Windows Actions musi pobrać zweryfikowane wagami SHA-256 GGUF i oficjalny silnik, zbudować duży ONEFILE EXE, a następnie uzyskać **rzeczywistą odpowiedź Qwen uruchomioną z tego właśnie EXE**. Bez tego nie publikujemy nowej wersji.

**Wielkość:** gotowy EXE ma zawierać ponad 1 GB skwantyzowanych wag, a nie być „13 MB cudownym AI”. Przy pierwszym uruchomieniu PyInstaller rozpakowuje zasoby do tymczasowego katalogu. Kompletność w tej wersji oznacza **działającą lokalną rozmowę i pozyskiwanie wiedzy z TXT**. Opcjonalne badawcze eksperymenty LoRA/PyTorch nadal wymagają osobnych bibliotek; nie nazywamy ich częścią kompletnego offline treningu wag.

[**Dokładny kontrakt możliwości, pochodzenie wag, SHA-256, licencje, ograniczenia i testy**](docs/FULL_OFFLINE_EXE.md).

---

## NeuroGenesis 0.10 — Trening TXT + prawdziwa rozmowa z lokalnym modelem

**Nowe funkcje w kodzie Windows EXE (przed publikacją wydania):**

- **Trening TXT**: odczyt lokalnych plików UTF-8 i dwa rzeczywiste tryby uczenia: mały badawczy Foundation GRU (zwykły tekst) oraz LoRA/PEFT (uporządkowane pary `USER:/ASSISTANT:`) dla lokalnego modelu instrukcyjnego. Zapisywanie **nowych** wag-kandydatów, ewaluacja oddzielnych przykładów i STOP.
- **Model Chat**: lokalna rozmowa z rzeczywistym modelem `Qwen/Qwen3-0.6B` (Apache-2.0), po świadomym pobraniu ~1,5 GB wag i przygotowaniu środowiska Python+Torch/Transformers. Opcjonalnie ręcznie wybrany adapter LoRA. **Brak zdalnego API podczas rozmowy.**
- **Pobieranie danych**: po zgodzie można pobrać do nowego TXT ograniczony zbiór anglojęzycznych dialogów UltraChat 200k (deklaracja licencji MIT w karcie) do weryfikacji praw i dalszego treningu. Przygotowany jest również [autorski polski plik przykładów](training/starter_dialogues_pl.txt).
- **Autonauka w granicach praw i zasobów**: opcjonalne monitorowanie wskazanego lokalnego TXT; zmiana danych może uruchomić trening nowego kandydata LoRA. **Bez automatycznej podmiany używanego modelu, bez ukrytego crawlowania i bez działania po zamknięciu aplikacji.**

[**Pełna instrukcja instalacji, danych, treningu i uruchamiania offline**](docs/TRAINING_AND_LOCAL_CHAT.md).

**Granica:** mała sieć GRU nie staje się kompetentnym chatbotem po wczytaniu TXT. Realny dialog korzysta z wcześniej wytrenowanego modelu zewnętrznego, działającego lokalnie. Pełna, niezależna samodzielność rozwojowa bez danych i zasobów nie jest możliwa do zapewnienia; nie deklarujemy AGI ani ukończonej kompetencji. **Kod 0.10 czeka na testy i publiczne EXE; najnowsze opublikowane wydanie może nadal być wcześniejsze.**

## NeuroGenesis 0.9.0 — awatar i działające laboratorium Foundation

**W kodzie programu:** [EMBODIED FOUNDATION](docs/EMBODIED_FOUNDATION.md).
Domyślne Windows `NeuroGenesis.exe` zawiera teraz trzy przełączane widoki:
obracający się hologram LIF, dokładną mapę synaps 2D oraz cybernetyczną
postać (AWATAR). Jej efekty związane z aktywnością zależą tylko od
faktycznych kroków i impulsów zapisywanych w SQLite; ruch kamery ma
charakter wizualny.

Dodatkowa zakładka **Foundation Lab** potrafi wywołać rzeczywistą predykcję
istniejącego modelu GRU z zaufanego lokalnego checkpointu. Użytkownik
wybiera osobne środowisko Python z PyTorch — mały plik EXE go nie zawiera.
Wynik to niezweryfikowana kontynuacja bajtowa, nie czat AI, a checkpoint
musi być uprzednio wytrenowany. Nie ma automatycznych pobrań, treningu,
samozmiany ani nadpisywania pamięci. [Wymagania i instrukcja](docs/EMBODIED_FOUNDATION.md).

**Status udostępniania:** kod 0.9.0 trafia przez testy CI. Oficjalne EXE
0.9.0 wskazuje dopiero nowe zweryfikowane wydanie pod
[releases/latest](https://github.com/promirmir/NeuroGenesis/releases/latest),
nie należy mylić starszego EXE 0.8.0 z nowymi funkcjami.

## Poprzednie zweryfikowane wydanie Windows 0.8.0 (archiwalne)

**NeuroGenesis 0.8.0 — rzeczywisty, nowy ekran startowy w samodzielnym EXE.** [Pobierz zweryfikowane wydanie](https://github.com/promirmir/NeuroGenesis/releases/tag/v0.8.0-main.8e27f420). SHA-256 pliku EXE: `5e48e1c7ecde3b7a066a39c2b71c8a70764351888ff30dc23ba75b53c6fcb44e`. Windows GUI otwiera teraz `CENTRUM` z prawdziwym grafem LIF i metrykami zamiast starej pustej rozmowy. Źródło i testy: PR #50; pełna macierz Windows/Python/Torch/Qt/ochrona prywatności zielona. Technologia **publicznego EXE: Tkinter**; rozbudowane Qt pozostaje opcjonalnym programem uruchamianym ze źródeł i wymaga osobnej licencyjnej bramki wydania. Brak AGI i samodzielnego semantycznego modelu języka.

# NeuroGenesis — Mission Control

**research prototype v0.12.0.**  
**Publiczne autorstwo: Miron przy pomocy AI.**

NeuroGenesis to lokalny projekt badawczy AI: rzeczywista mała sieć neuronowa LIF ze strukturalną plastycznością, prywatna trwała baza SQLite, kontrolowane zdobywanie informacji ze źródeł HTTPS, ekstrakcyjne cytowanie oraz odrębny eksperymentalny model Foundation Brain trenowany w PyTorch. **System nie jest AGI, świadomością, modelem ludzkiego mózgu ani niezależnie zweryfikowanym systemem rozumienia języka naturalnego.**

## Windows x64 — aktualna aplikacja bez Pythona

[**Pobierz aktualny NeuroGenesis.exe**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [Suma SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) · [Wszystkie wydania](https://github.com/promirmir/NeuroGenesis/releases)

**Od v0.8.0 domyślnie wyświetlany jest faktyczny MISSION CONTROL.** Nie jest to stary pusty ekran rozmowy ze zdjęcia zgłoszonego przez użytkownika. Uruchamiany od razu dashboard w samodzielnym, spakowanym Windows EXE ma ciemny, futurystyczny układ z:

- centralną interaktywną mapą **faktycznie zapisanej w SQLite sieci LIF** (neurony, rzeczywiste synapsy, wagi, impulsy);
- czterema rzeczywistymi kaflami: kroki LIF, neurony, synapsy i dokumenty;
- mierzoną historią ostatniej maski spike *tylko po nowym zapisanym kroku* i dziennikiem faktycznie zaobserwowanych zmian;
- stanami modułów: uprawnienia HTTPS, lokalna wiedza, stan LIF i oddzielny Foundation Brain;
- przyciskami przejścia do zachowanych modułów Rozmowa, Internet, Mózg, Specjalizacja i Kopia pamięci.

Przy braku nowych kroków graf nie udaje pracy neuronów. Przewijanie myszą przybliża wykres. Wartości nie są umownymi procentami inteligencji. Sam fakt odrysowania połączeń nie jest dowodem powstania jakościowo nowej AI.

**Silnik interfejsu publicznego EXE nadal korzysta z systemowego Tkintera**, dzięki czemu program działa bez instalowania biblioteki Qt i nie rozpowszechnia Qt DLL. Wygląd oraz domyślny ekran zostały jednak rzeczywiście przebudowane. Nie myl tego wydania z bardziej rozbudowanym, opcjonalnym interfejsem PySide6.

### Pamięć i bezpieczeństwo

Prywatna baza Windows standardowo znajduje się pod `%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3` i nie jest usuwana podczas aktualizacji aplikacji. Kopie tworzy się ręcznie w zakładce **Kopia pamięci**, za pomocą spójnego transakcyjnego backupu SQLite i weryfikacji SHA-256. Przywracanie wyłącznie do **nowego pliku**. Backup nie jest szyfrowany; trzymaj go w prywatnym miejscu. [Procedura](docs/MEMORY_RECOVERY.md).

Sieć pozostaje wyłączona na starcie. Pozyskiwanie informacji z publicznych stron wymaga jawnej zgody użytkownika i jest ograniczone. Strony są traktowane jako niezaufane dane, a publiczne udostępnienie nie jest zgodą na trening modelu.

## Rozbudowane NeuroGenesis Command Center — opcjonalne Qt

Repozytorium zawiera też drugi, działający interfejs napisany w **PySide6 / Qt**, z bardziej rozbudowaną nawigacją, przestrzenną panoramą sieci LIF, podglądem konkretnego neuronu, wykresem rzeczywistych strat treningu i panelami badania, pamięci, rozmowy oraz diagnostyki.

Aby uruchomić go na Windows **ze źródeł**, pobierz całe repozytorium, zainstaluj Python 3.12 x64 i użyj `Launch-NeuroGenesis-Mission-Control.cmd`. Skrypt tworzy lokalne środowisko oraz pyta o zgodę przed pierwszym pobraniem PySide6. **To nie jest plik EXE Qt.** Spakowany techniczny Qt na Windows przechodzi testy, ale nie jest publicznie rozpowszechniany, dopóki nie zostaną zweryfikowane wszystkie obowiązki licencyjne LGPLv3. [Dokumentacja Qt](docs/MISSION_CONTROL.md).

## Co faktycznie działa, a czego jeszcze nie dowiedziono

| Moduł | Potwierdzone funkcje i ograniczenia |
|---|---|
| Neurony LIF | Rzeczywiste kroki, impulsy, wagi, tworzenie neuronów i usuwanie połączeń; **to mała sieć eksperymentalna** |
| Rozmowa | Jawnie nauczone odpowiedzi, dosłowne fragmenty i URL, zachowanie kontekstu w Qt w bieżącej sesji; **bez potwierdzonego rozumowania semantycznego** |
| Internet | Kontrolowane, limitowane źródła i prywatna wersjonowana wiedza; nie oznacza automatycznego trenowania |
| Foundation Brain | Osobny prawdziwy eksperyment PyTorch (predykcja bajtów), checkpointy, CPU i opcjonalne CUDA; **nie jest jeszcze silnikiem rozmowy** |
| Wykresy | Dane zapisane w lokalnym mózgu / prawdziwe zdarzenia treningowe, nigdy sztuczne pomiary świadomości |
| Jakość | Testy Python 3.11–3.13, Windows frozen EXE, prywatności, QA i opcjonalnego Qt; niezależna rzeczywista QA i fizyczny GPU pozostają niezweryfikowane |

W szczególności system może błędnie cytować dokument przy pytaniu z fałszywą przesłanką. Syntetyczne testy BM25 również wykazały tę klasę błędu. Nie utożsamiaj cytowania z prawdziwością i nie przyjmuj, że zwiększająca się liczba neuronów lub pobranych dokumentów dowodzi wzrostu inteligencji.

## Dokumentacja, rozwój i odpowiedzialne wydania

- [Stan projektu i aktualne ograniczenia](docs/PROJECT_STATE.md)
- [Dziennik zmian](docs/DEVELOPMENT_LOG.md)
- [Architektura i wymogi Mission Control](docs/MISSION_CONTROL.md)
- [Foundation Brain](docs/FOUNDATION_BRAIN.md)
- [QA i metody odniesienia](docs/QA_ACCEPTANCE.md)
- [Bezpieczeństwo](docs/SECURITY.md)
- [Testy CI](https://github.com/promirmir/NeuroGenesis/actions)

Wydanie Windows jest publikowane tylko z dokładnie zweryfikowanego commita `main` i zawiera plik kontrolny SHA-256. **v0.8.0 jest etapem doprowadzania istniejącej aplikacji do wyższej jakości użytkowej, a nie deklaracją osiągnięcia AGI ani ukończenia wszystkich celów badawczych.**
