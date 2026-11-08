# NeuroGenesis 0.12.2 — świadoma analiza dowodów

**Autor:** Miron przy pomocy AI.

W 0.12.1 agent zapisywał przy celu metadane źródeł, ale model Qwen otrzymywał tylko ogólne polecenie ich analizy. To nie gwarantowało, że przeczytał konkretny fragment. W 0.12.2 usuwamy tę lukę.

## Rzeczywista pętla

1. Cel trafia do trwałej lokalnej bazy `agent_goals.sqlite3`.
2. Program wyszukuje faktyczne fragmenty zatwierdzonych plików TXT. Jeśli lokalna pamięć zawiera wcześniej pobrane za zgodą strony HTTPS, pobiera też związany z celem cytat wraz z URL i SHA-256. Ten krok nie łączy się samodzielnie z Internetem.
3. Model otrzymuje **te same konkretne fragmenty źródeł**, których identyfikatory znajdą się w historii raportu. Każdy ma widoczną etykietę, nazwę lub URL i część sumy SHA-256.
4. Wszystkie źródła są oznaczane jako niezaufane DANE, a nie instrukcje. Kontekst jest ograniczony do 1750 znaków — mniej niż dopuszcza lokalny silnik. Ochrona przed prompt injection nie jest absolutna.
5. Wynik jest wyłącznie kandydatem do ręcznej oceny.
6. Nowa wersja TXT lub nowe rzeczywiście zarejestrowane źródło HTTPS zmienia odcisk zestawu dowodów i może uruchomić ponowną analizę oczekującego celu; bez nowych danych program nie powinien udawać rozwoju. Pozostaje limit 32 prób na cel.
7. Główny panel wskazuje źródła **przekazane modelowi**, a nie abstrakcyjną listę cytowań.

## Ograniczenia

System zdobywa i ponownie analizuje wiedzę, ale nie trenuje w ten sposób 1,7 mld parametrów Qwen. LIF to nadal eksperymentalna sieć, a nie ludzki mózg. Nie jest to AGI, nieograniczony samorozwój ani bezwarunkowa niezależność od danych i sprzętu. Sieć wymaga osobnej zgody; program nie wykonuje kodu znalezionego na stronach.

Testy obejmują rzeczywisty zapis i odczyt źródła HTTPS w prywatnej SQLite, ponowne wybudzenie oczekującego celu oraz obecność cytowanego fragmentu i SHA w wiadomości wysyłanej do modelu. Release wymaga pełnej kompilacji Windows EXE z prawdziwą odpowiedzią z wag GGUF.
