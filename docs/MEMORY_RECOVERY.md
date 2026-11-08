# NeuroGenesis — bezpieczna kopia i odtwarzanie pamięci

**Publiczne autorstwo: Miron przy pomocy AI.** Dotyczy lokalnej prywatnej bazy `experiences.sqlite3` używanej przez dotychczasowe Windows EXE i opcjonalne Qt Command Center.

## Gwarancje i ograniczenia

- Każda ręcznie uruchomiona kopia wykorzystuje natywną metodę `sqlite3.Connection.backup()`. Jest to **spójna transakcyjnie migawka** obejmująca zapisane transakcje również wtedy, gdy baza korzysta z dziennika WAL.
- Kopiowane są obserwacje, stan sieci neuronowej, ręcznie nauczone odpowiedzi, źródła i ich wersje, fragmenty wiedzy, zgody na trening i historia ich zmiany. Nie trzeba wyłączać dostępu HTTPS, jednak kopiowane są tylko **zakończone transakcje**.
- Narzędzie odczytuje i kontroluje `PRAGMA quick_check`, obowiązkowe tabele, wersję schematu, oraz poprawność całego zapisanego stanu `Brain`. Potem liczy SHA-256 **ukończonej kopii**. Raport zawiera wyłącznie statystyki i sumę, bez prywatnych tekstów, haseł czy adresów stron.
- Docelowy plik `*.sqlite3` musi być **NOWY**. Program zapisuje i weryfikuje plik tymczasowy w tym samym folderze, a następnie tworzy nazwę wyniku za pomocą atomowego twardego dowiązania bez możliwości nadpisania istniejącego pliku. Na dyskach bez obsługi takiej operacji narzędzie odmówi zamiast ryzykować uszkodzenie danych.
- Przywracanie jest **wyłącznie do nowej ścieżki**; nigdy nie nadpisuje aktualnej bazy. Aktywne pliki `-wal`/`-journal` są odrzucane jako źródło zwykłego odtwarzania — najpierw należy utworzyć migawkę przez SQLite backup API.
- Nic nie jest wysyłane do internetu. **Kopia nie jest szyfrowana**: należy ją przechowywać na nośniku z ograniczonym dostępem, nie publikować w GitHub i nie przekazywać niepowołanym osobom. Nie zawiera automatycznie zewnętrznych checkpointów PyTorch `.pt`, ponieważ nie są one częścią SQLite — trzeba je zarchiwizować osobno, jeśli są istotne.

## Aplikacja Windows

W tradycyjnym `NeuroGenesis.exe` dostępna jest zakładka **Kopia pamięci**. Wskaż nowy plik na komputerze; po zakończeniu odczytaj wynik integralności i SHA-256. Drugi przycisk pozwala sprawdzić wcześniej zapisany plik. Operacja pracuje w osobnym wątku i nie wymaga Pythona ani połączenia sieciowego.

W opcjonalnym Command Center Qt analogiczne przyciski znajdują się w **Ustawienia → Bezpieczeństwo pamięci**. Obie aplikacje korzystają z tej samej implementacji i tych samych formatów.

## Weryfikacja i przywrócenie kopii przez terminal

Poniższe przykłady używają lokalnej instalacji projektu i Pythona 3.12. Zastąp ścieżki ścieżkami **na własnym komputerze**.

```powershell
py -3.12 -m neurogenesis.recovery --verify "C:\\Kopie\\NeuroGenesis-backup.sqlite3"
py -3.12 -m neurogenesis.recovery --verify "C:\\Kopie\\NeuroGenesis-backup.sqlite3" --expected-sha256 <wstaw-64-znakową-sumę>
py -3.12 -m neurogenesis.recovery --restore "C:\\Kopie\\NeuroGenesis-backup.sqlite3" --output "C:\\Kopie\\NeuroGenesis-odtworzona.sqlite3" --confirm-restore-new
```

Przywrócenie daje drugą bazę do przejrzenia. Aby użyć jej zamiast aktywnej, zamknij wszystkie instancje aplikacji, wykonaj dodatkowy backup aktualnej bazy, zweryfikuj kopię i uruchom aplikację z jawnym `--db` wskazującym nowy plik. **Nie usuwaj** starej bazy przed ręczną weryfikacją nowej. Nie wykonuj poleceń na bazach, których pochodzenia nie znasz.

## Niezależne testy jakości

`tests/test_recovery.py` wykonuje prawdziwe transakcje na prywatnym testowym SQLite: zapisuje neuronowe obserwacje, ręczną naukę, cytowane źródła i uprawnienia; sprawdza kopię i nienaruszalność oryginału, odtwarzanie do nowej bazy, sumę SHA-256, błędy uszkodzenia, niedozwolone nadpisanie i dane utrwalone w WAL.

W `desktop.self_test()` sprawdzana jest cała ścieżka kopia → suma → przywrócenie również we **właściwym spakowanym Windows EXE**. Dedykowany test Qt uruchamia asynchroniczną kopię w panelu Ustawienia. Wdrożenie można uznać za zweryfikowane dopiero po zielonych testach Windows/Python/Qt i ochrony danych.

## Co nie jest objęte

To nie jest szyfrowanie woluminów, ochrona przed fizyczną kradzieżą komputera, backup w chmurze, synchronizacja wielu komputerów, automat codziennego kopiowania ani odwrócenie wcześniejszych gradientów neuronowych. Zapisywanie checkpointów `.pt` i ich bezpieczna ocena pozostają osobnym procesem. Nie utożsamiaj udanego backupu z ukończeniem modelu AGI.
