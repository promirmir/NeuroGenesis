# NeuroGenesis v0.5.5 — uruchomienie na Windows

**Autorstwo: Miron przy pomocy AI.** Aktualny kod znajduje się w [repozytorium GitHub](https://github.com/promirmir/NeuroGenesis). Nie trzeba instalować Pythona, aby uruchomić gotowy EXE.

## Pobierz i uruchom

1. Otwórz [GitHub Actions — Windows standalone EXE](https://github.com/promirmir/NeuroGenesis/actions/workflows/windows-exe.yml).
2. Wybierz najnowszy przebieg zakończony na zielono na gałęzi `main`. W sekcji **Artifacts** pobierz `NeuroGenesis-Windows-x64` (GitHub może wymagać zalogowania).
3. Rozpakuj ZIP. W środku są `NeuroGenesis.exe` oraz `NeuroGenesis.exe.sha256`. Sprawdź sumę kontrolną w PowerShell:

   ```powershell
   Get-FileHash .\NeuroGenesis.exe -Algorithm SHA256
   ```

4. Uruchom `NeuroGenesis.exe` dwukrotnym kliknięciem. Aplikacja otworzy własne okno z zakładkami **Rozmowa**, **Mózg**, **Internet**.

**Uwaga:** program jest eksperymentalny i nie ma podpisu cyfrowego producenta. Nie ignoruj ostrzeżeń bezpieczeństwa bez sprawdzenia pochodzenia i sumy SHA-256. Artefakty Actions są przechowywane przez 14 dni; nowy udany przebieg zapewnia kolejny plik do pobrania.

## Co naprawdę działa

- Rozmowa: przekazywanie tekstu jako bodźca do **rzeczywistej małej sieci neuronowej**; to nie jest jeszcze rozumiejący język chatbot.
- Mózg: podgląd kroków, neuronów, synaps i lokalnych doświadczeń.
- Pamięć: transakcyjne zapisanie stanu mózgu i obserwacji w prywatnej bazie SQLite. Pełny tekst jest zapisywany wyłącznie po włączeniu opcji.
- Internet: **wyłączony**; wersja v0.5.4 nie czyta samodzielnie stron ani nie wysyła rozmów.
- Samorozwój: w zakładce **Mózg** dostępny jest ręczny przycisk i opcja **AUTO** (domyślnie wyłączona). Po 40 nowych obserwacjach program testuje ograniczone warianty uczenia i zapisuje tylko propozycje, które przejdą kontrolę niezależnego zbioru i poprzedniej umiejętności. Zapisy są atomowe, a niepowodzenie nie usuwa wcześniejszych doświadczeń. Nie jest to swobodna samomodyfikacja algorytmów.
- Homeostaza, naprawa synaps i automatyczne powiększanie sieci pozostają oddzielnymi funkcjami badawczymi, nie są jeszcze autonomicznym procesem produkcyjnym.

## Gdzie jest pamięć?

Plik doświadczeń znajduje się w katalogu użytkownika:

```text
%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3
```

Nie usuwaj tego katalogu przy aktualizowaniu EXE. Twórz prywatne kopie zapasowe, ponieważ GitHub przechowuje **kod programu**, a nie lokalną pamięć użytkownika. Baza nie jest szyfrowana; nie wprowadzaj do niej sekretów.

## Testy i rozwój

Baza v0.5.4 została scalona przez [PR #10](https://github.com/promirmir/NeuroGenesis/pull/10). Wersja v0.5.5 dodaje ograniczony, opcjonalny mechanizm samorozwoju i została scalona przez [PR #12](https://github.com/promirmir/NeuroGenesis/pull/12) po zielonych testach Windows/Linux. Pobieraj najnowszy zielony artefakt z głównej gałęzi. Wyniki dotyczą działania prototypu, nie osiągnięcia inteligencji ogólnej.

Instrukcje pracy od kodu źródłowego: [README](README.md) i [stan projektu](docs/PROJECT_STATE.md).

**Nie korzystaj ze starych instrukcji nadpisywania historii Git ani skryptów typu fresh-root.** Repozytorium posiada już rozwijane `main` i historię zmian.