# NeuroGenesis 0.12.9 — sprawdzane odzyskiwanie stanu ACF i audyt źródeł

**Autor publiczny:** Miron przy pomocy AI.

## Co realnie zostało wzmocnione

ACF uczy się na zapisanych wcześniej wektorach z lokalnego SQLite. Każda seria zmian sieci jest zapisywana jako plik JSON zawierający zarówno model neuronowy, jak i numer ostatniego przetworzonego zdarzenia. Dotychczas uszkodzenie tego jedynego pliku zatrzymywało uczenie mimo zachowania dziennika obserwacji.

W wersji 0.12.9 `FabricMemoryObserver` obsługuje **drugą, atomowo zapisaną kopię ostatniego zweryfikowanego stanu** i odmowę aktualizacji przy wykrytym konflikcie:

- Przy każdym faktycznym postępie zapisuje poprzedni, zweryfikowany stan do `<migawka>.previous`, zanim nadpisze migawkę bieżącą. Gdy nie ma nowych obserwacji, nie wykonuje zbędnych zapisów.
- Jeżeli główna migawka stała się niespójnym JSON-em, nie używa jej do uczenia. Próbuje przywrócić `*.previous`, ale **dopiero po pełnym sprawdzeniu schematu i zgodności licznika obserwacji z rzeczywistym dziennikiem SQLite**. Dla semantycznego ACF sprawdza również wersję taggera Qwen.
- **Uszkodzona zawartość jest zachowywana jako `<migawka>.corrupt`**, utworzona bez nadpisywania poprzednich plików diagnostycznych. Przywrócenie bieżącej migawki następuje atomowo, a brakujące zdarzenia zostają ponownie przetworzone.
- Gdy kopia `previous` nie istnieje, jest niepoprawna, nie zgadza się z dziennikiem lub `corrupt` już zajmuje miejsce, mechanizm **zatrzymuje się bez niszczenia danych**. Odzyskanie nie jest udawane.
- Równoległa modyfikacja migawki między odczytem a zapisem jest wykrywana przez porównanie skrótu SHA-256 i odrzucenie przestarzałego wyniku. Jest to ochrona optymistyczna, nie pełna międzyprocesowa blokada; zalecana jest jedna aktywna instancja aplikacji.

Mechanizm działa dla **dwóch odrębnych torów ACF**: sensorycznego z hashowanych cech oraz semantycznego opartego na lokalnych klasyfikacjach Qwen. Nie zmienia schematów ani treści istniejących baz i nie usuwa wcześniejszych stanów pamięci.

## Weryfikacja i raportowanie

W głównym panelu pokazuje się czytelny komunikat o rzeczywistym, zweryfikowanym odtworzeniu stanu. Zwykłe odczytanie statusu nie naprawia ani nie zapisuje plików — odtworzenie następuje tylko w trakcie synchronizacji danych.

Nowe testy sprawdzają: dokładną rekonstrukcję parametrów sieci po uszkodzeniu JSON, brak jakiegokolwiek nadpisania bez poprawnej kopii, wykrycie brakującego rekordu lub niewłaściwego taggera w dzienniku, ochronę już istniejącego pliku `corrupt`, brak zbędnych zapisów przy braku nowych obserwacji, konflikt równoległych aktualizacji oraz poprawne zwolnienie SQLite na Windows.

## Dokładniejszy pomiar halucynowanych cytowań

Testy A/B, A/B/C i A/B/C/D korzystają ze wspólnej procedury rozpoznawania etykiet źródeł. Zmieniono ją tak, aby cytowania `[L0]`, `[L100]`, `[L999]` i podobne **nie umykały pomiarowi**. Etykieta musi odpowiadać dokładnie rzeczywiście podanemu źródłu — `[L01]` nie jest równoznaczne z `[L1]`.

Liczba cytowań bez źródła to tylko pomiar formalnej spójności odpowiedzi. **Nie jest dowodem prawdziwości treści ani wzrostu inteligencji.**

## Granice i bezpieczeństwo

- Kopia `previous` pojawia się po **co najmniej dwóch udanych zapisach migawki**; pierwszej niezabezpieczonej migawki nie da się odtworzyć tym mechanizmem.
- Odtworzenie nie regeneruje danych skasowanych z SQLite, nie naprawia błędnych semantycznie obserwacji, nie poprawia automatycznie wag Qwen i nie jest dowodem biologicznej samonaprawy.
- Wszystko pozostaje lokalne. Kopie zawierają stan liczbowy sieci, nie surową treść rozmów. Nie korzysta z Internetu ani usług zewnętrznych.
- Poprzedni interfejs, dobrowolny tryb badawczy ACF, wszystkie funkcje czatu i formaty pamięci pozostają zgodne.
- Przy wykryciu uszkodzenia bazy danych lub braku bezpiecznej możliwości odtworzenia, **nie wolno ręcznie usuwać plików `corrupt` i `previous` bez zachowania kopii diagnostycznej**.

To praktyczna odporność na pojedynczą awarię migawki, a nie jeszcze samodzielny system odbudowy inteligencji. Dalsza praca wymaga ocen jakości rozumowania, pamięci długotrwałej i regresji umiejętności na niezależnych zestawach danych.
