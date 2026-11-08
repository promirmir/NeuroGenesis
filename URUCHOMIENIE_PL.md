# NeuroGenesis v0.6.0 — uruchomienie na Windows

**Autorstwo: Miron przy pomocy AI.** Aktualny kod znajduje się w [repozytorium GitHub](https://github.com/promirmir/NeuroGenesis). Nie trzeba instalować Pythona, aby uruchomić gotowy EXE.

## Pobierz i uruchom

1. Kliknij [**POBIERZ NAJNOWSZY NeuroGenesis.exe (Windows x64)**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe). Plik znajduje się w sekcji [GitHub Releases](https://github.com/promirmir/NeuroGenesis/releases/latest) i nie wymaga przeszukiwania GitHub Actions.
2. Z tej samej strony pobierz [**sumę kontrolną SHA-256**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256). Aby porównać ją w PowerShell, wpisz:

   ```powershell
   Get-FileHash .\NeuroGenesis.exe -Algorithm SHA256
   ```

3. Uruchom `NeuroGenesis.exe` dwukrotnym kliknięciem. Aplikacja otworzy własne okno z zakładkami **Rozmowa**, **Mózg**, **Internet** (oraz **Specjalizacja** w wydaniu zawierającym PR #24).

**Uwaga:** program jest eksperymentalny i nie ma podpisu cyfrowego producenta. Nie ignoruj ostrzeżeń bezpieczeństwa bez sprawdzenia pochodzenia i sumy SHA-256. Wydania GitHub Releases mają stałe odnośniki; tymczasowe artefakty GitHub Actions są przechowywane przez 14 dni.

## Co naprawdę działa

- Rozmowa: **działające jawne uczenie odpowiedzi**. Wpisz pytanie, niżej swoją odpowiedź i kliknij **Naucz odpowiedzi**. Przy wysłaniu tego samego pytania program odtworzy zapisaną odpowiedź. Możesz ją poprawić lub usunąć. Równolegle pytania są bodźcami dla małej sieci neuronowej. Tekst odpowiedzi pochodzi z lokalnej bazy, a nie z rozumowania neuronów.
- Mózg: podgląd kroków, neuronów, synaps i lokalnych doświadczeń.
- Pamięć: transakcyjny zapis stanu mózgu, obserwacji i (po jawnym przycisku uczenia) par pytanie–odpowiedź w prywatnej bazie SQLite. Zwykłe wiadomości nie przechowują pełnego tekstu bez zaznaczenia opcji. [Szczegóły uczenia](docs/TEACHABLE_DIALOGUE.md).
- Internet: **domyślnie wyłączony**. Po włączeniu przez użytkownika może pobrać jedną wskazaną publiczną stronę HTTPS, sprawdzić jej pochodzenie i przekazać tekst jako bodziec do istniejącego mózgu. Możliwe jest automatyczne odświeżanie tego samego ręcznie zatwierdzonego adresu co 5 minut. Dane rozmów nie są przesyłane na strony. To nie jest samodzielne rozumienie treści. [Zasady bezpieczeństwa](docs/INTERNET_SENSE.md).
- Samorozwój: w zakładce **Mózg** dostępny jest ręczny przycisk i opcja **AUTO** (domyślnie wyłączona). Po 40 nowych obserwacjach program testuje ograniczone warianty uczenia i zapisuje tylko propozycje, które przejdą kontrolę niezależnego zbioru i poprzedniej umiejętności. Zapisy są atomowe, a niepowodzenie nie usuwa wcześniejszych doświadczeń. Nie jest to swobodna samomodyfikacja algorytmów.
- Homeostaza, naprawa synaps i automatyczne powiększanie sieci pozostają oddzielnymi funkcjami badawczymi, nie są jeszcze autonomicznym procesem produkcyjnym.

## Jak nauczyć pierwszej odpowiedzi?

1. Otwórz zakładkę **Rozmowa**.
2. Wpisz w głównym polu: **Co umiesz?**
3. W dolnym polu wpisz: **Uczę się przez lokalne doświadczenia.**
4. Kliknij **Naucz odpowiedzi**, a następnie **Przekaż do mózgu**. Program odpowie zapamiętanym tekstem.
5. Aby zmienić odpowiedź, wpisz inną i ponownie kliknij **Naucz odpowiedzi**. Aby usunąć skojarzenie, kliknij **Usuń nauczoną odpowiedź**.

Ten tryb nie jest dowodem rozumienia języka: to jawnie nauczone skojarzenie, zapisane lokalnie i powiązane ze stanem sieci. Limit to 512 różnych pytań. Nie wpisuj haseł ani innych sekretów.

## Jak korzystać z internetu?

1. W zakładce **Internet** zaznacz **Włącz odczyt HTTPS**.
2. Wpisz publiczny adres w postaci https://domena.pl/strona (bez parametrów i danych logowania).
3. Kliknij **Pobierz stronę i przekaż mózgowi**. Zobaczysz tekst strony, adres źródłowy, czas odczytu oraz SHA-256.
4. Opcjonalnie zaznacz odświeżanie co pięć minut. Powtórzenie identycznej strony nie zwiększa liczby zdarzeń w pamięci.
5. Wyłącz opcję HTTPS, kiedy nie chcesz pobierać danych. Dane rozmów nie są wysyłane na strony internetowe.

Serwer zobaczy adres IP Twojego połączenia. Program nie otwiera stron wymagających logowania i nie wykonuje kodu ze stron. Odwiedzane adresy zostają zapisane w lokalnej pamięci; ich treść nie jest trwale przechowywana w postaci pełnego tekstu. To pierwszy zmysł internetowy; nie oznacza rozumienia zawartości.

## Jak uruchomić autonomiczne badanie dziedziny? (po wydaniu PR #24)

1. Otwórz **Internet** i świadomie zaznacz **Włącz odczyt HTTPS**.
2. Przejdź do nowej zakładki **Specjalizacja**. Wpisz dziedzinę, na przykład „Mechanika”, i ustal limit stron (1–500; domyślnie 120).
3. Kliknij **Rozpocznij badanie**. Program najpierw szuka stron z Wikipedii, a następnie odkrywa powiązane adresy z innych publicznych domen. Pokazuje liczbę prób, zapisanych obserwacji, błędów i odkrytych źródeł.
4. Kliknij **Stop**, aby przerwać kolejne odczyty. Wyłączenie zgody HTTPS również zatrzymuje proces.

Robot respektuje `robots.txt`, wykonuje nie więcej niż jedno żądanie strony na 5 sekund i nakłada dodatkowe limity domen. Część stron może być niedostępna. **Nie jest to pełny skan internetu ani nauka wag modelu PyTorch**. Przy wcześniejszym EXE zakładka może być nieobecna; najpierw sprawdź, czy nowy kod został scalony i opublikowany.

## Gdzie jest pamięć?

Plik doświadczeń znajduje się w katalogu użytkownika:

```text
%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3
```

Nie usuwaj tego katalogu przy aktualizowaniu EXE. Twórz prywatne kopie zapasowe, ponieważ GitHub przechowuje **kod programu**, a nie lokalną pamięć użytkownika. Baza nie jest szyfrowana; nie wprowadzaj do niej sekretów.

## Testy i rozwój

Baza v0.5.4 została scalona przez [PR #10](https://github.com/promirmir/NeuroGenesis/pull/10). Wersja v0.5.5 dodaje ograniczony, opcjonalny mechanizm samorozwoju i została scalona przez [PR #12](https://github.com/promirmir/NeuroGenesis/pull/12) po zielonych testach Windows/Linux. Pobieraj najnowsze wydanie ze strony GitHub Releases; publikacja następuje po zielonej kompilacji i weryfikacji SHA-256 z głównej gałęzi. Wyniki dotyczą działania prototypu, nie osiągnięcia inteligencji ogólnej.

Instrukcje pracy od kodu źródłowego: [README](README.md) i [stan projektu](docs/PROJECT_STATE.md).

**Nie korzystaj ze starych instrukcji nadpisywania historii Git ani skryptów typu fresh-root.** Repozytorium posiada już rozwijane `main` i historię zmian.