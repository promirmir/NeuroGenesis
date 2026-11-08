# NeuroGenesis 0.9 — Embodied Presence + local Foundation Lab

**Publiczne autorstwo: Miron przy pomocy AI.**

## Faktyczny ekran aplikacji Windows

Domyślny, dystrybuowany program `NeuroGenesis.exe` pozostaje oparty na
**Tkinter**. Nie dodano zależności Qt ani PyTorch do jednoplikowego EXE.

W centrum Mission Control można przełączać trzy rzeczywiste widoki:

- **HOLOGRAM 3D** — symboliczna obracająca się przestrzennie reprezentacja
  faktycznych neuronów, synaps, wag i ostatniego impulsu LIF.
- **CONNECTOME 2D** — istniejąca dokładna mapa faktycznych połączeń.
- **AWATAR** — grafika humanoidalnej, cyfrowej postaci. Efekty oczu i
  pierścienia uruchamiają się tylko po nowym zapisanym kroku LIF, jasne
  spojrzenie wymaga zarejestrowanych impulsów neuronów. Spokojna animacja
  kamery jest wyłącznie efektem graficznym.

Nie jest to biologiczna symulacja mózgu, ucieleśniona sztuczna świadomość,
fotorealistyczna postać, urządzenie fizyczne ani sygnał z GRU Foundation.

### Rzeczywista predykcja Foundation w EXE — opcjonalny worker

Zakładka **Foundation Lab** jest w tym samym **domyślnym Windows EXE**.
Działa bez logowania, nie łączy się z żadnym API AI, nie pobiera niczego
i nie startuje automatycznie. Operator wybiera:

1. Własne `python.exe` z zainstalowanymi lokalnie pakietami
   `neurogenesis` i `torch`.
2. Własny zaufany checkpoint `.pt`/`.pth`, który ma co najmniej jeden
   zapisany krok uczenia.
3. Prefiks UTF-8 do 512 znaków, 1–64 bajty wyniku oraz CPU/CUDA.
4. Jawne potwierdzenie zaufania do checkpointu, potem uruchamia predykcję.

Wynik powstaje z **naprawdę wytrenowanych wag** GRU i jest raportowany
oddzielnie jako surowa kontynuacja bajtowa z faktyczną liczbą parametrów
i zmierzoną przepustowością. Nawet poprawny UTF-8 **nie jest automatycznie
merytoryczną odpowiedzią**. Model nie jest domyślnie wytrenowany, nie
otrzymuje autorytetu źródeł z rozmowy i nie zapisuje odpowiedzi do SQLite.

#### Przygotowanie środowiska tylko na żądanie

W lokalnym katalogu kopii pełnego repozytorium:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[foundation]"
```

Następnie wskaż `.venv\Scripts\python.exe` w zakładce Foundation Lab.
Do samych obrazów/rozmów i przeglądania pamięci Python **nie jest**
wymagany. Instalacja PyTorch odbywa się tylko na wyraźne działanie
operatora, poza plikiem EXE.

Aby wytworzyć checkpoint, użyj własnego lub licencjonowanego korpusu:

```powershell
.\.venv\Scripts\python.exe -m neurogenesis.foundation_train --input corpus.txt --output local-foundation.pt --confirm-corpus-rights --device cpu --steps 100
```

Sam trening jest odrębną operacją i nie uruchamia się po starcie GUI.
Nie pobieramy samodzielnie tekstu do trenowania. Nie zapewniamy
poprawnego polskiego dialogu po kilkudziesięciu krokach uczenia.

### Granice i prywatność

- Nie ma śledzenia oczu, mikrofonu, kamery, renderowania prawdziwej
  świadomości ani przekierowania danych na zewnętrzny serwer.
- Osobny proces nie otrzymuje promptu w argumentach polecenia;
  lokalny prefiks płynie przez standardowe wejście. Nie jest
  tworzony plik tymczasowy z treścią.
- Niezaufanych checkpointów **nie należy otwierać**. Nawet ograniczenie
  PyTorch `weights_only=True` nie stanowi bezpiecznego sandboxu.
- Wymagane osobne środowisko lokalne; system kończy się jawnym błędem,
  kiedy PyTorch lub checkpoint nie są dostępne. Nie udaje sukcesu.
- Prywatna baza SQLite i jej dotychczasowe limity LIF nie są migrowane;
  zmiany `0.8 → 0.9` dotyczą głównie UI i opcjonalnej predykcji.
- Do potwierdzenia znacząco wyższej inteligencji nadal potrzeba
  zewnętrznych, dokumentowo niezależnych testów generalizacji,
  długiego kontekstu, zapominania i prawdziwości odpowiedzi.

## Bramka dostarczenia

Dla publicznego wydania wymagane są: macierz Python 3.11–3.13,
ochrona prywatności, testy prawdziwego Tk na Windows, `--self-test`,
`--ui-self-test` faktycznego spakowanego EXE, testy opcjonalnego Qt,
osobny test CPU PyTorch oraz tag związany z jednoznacznym commitem
i opublikowana suma SHA-256. Dopóki nie przejdą, ta dokumentacja opisuje
**kod weryfikowany na gałęzi**, a nie dostępny publicznie EXE.
