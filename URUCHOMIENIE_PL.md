# NeuroGenesis v0.5.4 — uruchomienie na Windows

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
- Homeostaza, samonaprawa, samodoskonalenie i skalowanie pojemności: zaimplementowane jako **oddzielne moduły badawcze i testy**. Nie działają jeszcze jako jeden automatyczny proces stale modyfikujący mózg.

## Gdzie jest pamięć?

Plik doświadczeń znajduje się w katalogu użytkownika:

```text
%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3
```

Nie usuwaj tego katalogu przy aktualizowaniu EXE. Twórz prywatne kopie zapasowe, ponieważ GitHub przechowuje **kod programu**, a nie lokalną pamięć użytkownika. Baza nie jest szyfrowana; nie wprowadzaj do niej sekretów.

## Testy i rozwój

Zmiany v0.5.4 są na `main` po [PR #10](https://github.com/promirmir/NeuroGenesis/pull/10). Przed scaleniem przeszło 125 testów Windows, trzy wersje Python w Linux CI oraz test uruchomienia samodzielnego EXE. Wyniki dotyczą działania prototypu, nie osiągnięcia inteligencji ogólnej.

Instrukcje pracy od kodu źródłowego: [README](README.md) i [stan projektu](docs/PROJECT_STATE.md).

**Nie korzystaj ze starych instrukcji nadpisywania historii Git ani skryptów typu fresh-root.** Repozytorium posiada już rozwijane `main` i historię zmian.