# NeuroGenesis 0.12.7 — ACF aktywnie uczestniczy w doborze wiedzy do odpowiedzi

**Autor publiczny:** Miron przy pomocy AI.

## Rzeczywista integracja z lokalnym Qwen

Dotychczasowy ACF 0.12.5 uczył się prognozowania następnego tematu na podstawie rzeczywistych wektorów semantycznych generowanych przez lokalny Qwen3-1.7B. Potrafił też odczytać lokalną bazę TXT, lecz nie wpływał na odpowiedź. Od 0.12.7 możliwe jest **eksperymentalne podłączenie** tych prognoz do toru RAG odpowiadającego rzeczywistemu użytkownikowi.

1. ACF wczytuje **istniejącą** trwałą migawkę i sprawdza historię przyczynowych błędów MSE. Musi uzyskać przewagę nad nierozrastającą się siecią, utrzymaniem ostatniej obserwacji i prognozą stałą. Domyślna bramka i progi z `semantic_policy.py` pozostają bez zmian.
2. Tylko gdy bramka dopuści decyzję, uruchamiana jest dodatkowa, rzeczywista klasyfikacja znaczenia **bieżącego pytania** przez własny lokalny Qwen, niezależnie od historycznej prognozy. Treści pytania nie zapisuje się w tej ścieżce.
3. Prognozowana dziedzina musi być rzeczywiście rozpoznana w bieżącym pytaniu. W przeciwnym razie ACF wstrzymuje ingerencję.
4. System wyszukuje tylko istniejące, zatwierdzone fragmenty TXT w SQLite FTS5. Kandydat musi zawierać minimum dwa odrębne słowa-klucze występujące bezpośrednio w pytaniu (po odfiltrowaniu słów ogólnych).
5. Do listy istniejących źródeł można dołączyć **maksymalnie jeden** nowy, niepowtarzający się fragment. Jeśli kontekst miał już cztery fragmenty, zastępuje on czwarty. Zwykły Qwen generuje odpowiedź na podstawie jawnie dostarczonego fragmentu jak w istniejącym systemie RAG — nigdy na podstawie niepotwierdzonej prognozy jako faktu.

**Ważne:** nawet jeśli źródło zostało dodane, cytowany tekst może być fałszywy lub zawierać instrukcję typu prompt-injection. Dotychczasowa zasada traktowania danych źródłowych jako niezaufanych nadal obowiązuje. Dopasowanie słów nie dowodzi prawdziwości ani właściwej interpretacji.

## Interfejs Windows

W głównym oknie NEUROGENESIS dostępna jest opcja:

**„BADANIE: ACF może dobrać 1 lokalny fragment TXT”**

Jest **wyłączona domyślnie**, ponieważ nie mamy jeszcze niezależnego dowodu, że poprawia jakość odpowiedzi. Po jej włączeniu wynik rozmowy pokazuje status: fragment dołączony albo konkretny powód wstrzymania. Samodzielne cele agenta oraz wszystkie stare funkcje pozostają bez eksperymentalnej ingerencji. ACF i Qwen nie łączą się z chmurą w tym torze; nie modyfikujemy wag LLM.

## Porównanie A/B/C na prawdziwym modelu

`neurogenesis/dialogue_abc.py` uruchamia trzy warunki dla każdego pytania:

- A: sam Qwen3-1.7B, bez źródeł;
- B: ten sam Qwen + zwykłe lokalne TXT RAG;
- C: ten sam Qwen + lokalne TXT RAG + ACF, o ile spełni bramkę.

Pytania muszą stanowić prywatną, osobno przygotowaną, dotąd niewykorzystywaną próbę. Używamy dokładnie tego samego pliku GGUF i tego samego procesu, bez próbkowania (deterministyczne ustawienie dekodowania). Kolejność A/B/C rotuje między przypadkami. Migawka ACF jest stała podczas testu i **nie uczy się na próbie**. Wynik obejmuje liczbę rzeczywistych zmian źródeł, liczbę wstrzymań, sparowane wyniki odpowiedzi, fałszywe odwołania, czasy i różnicę trafień z możliwością wyniku ujemnego.

Przykład polecenia uruchamianego w pełnym, lokalnym środowisku źródłowym z zweryfikowanym pakietem Qwen:

    python -m neurogenesis.dialogue_abc --db "C:\private\local_knowledge.sqlite3" --audit "C:\private\holdout.jsonl" --acf-state "C:\private\semantic_fabric.acf.json" --assets-root "C:\verified_bundle" --confirm-corpus-rights --confirm-heldout

Format pliku JSONL to dokładnie `question`, `expected_answer_fragment`, `expected_source` jak w `docs/DIALOGUE_PAIRED_EVALUATION_0126.md`, od 4 do 32 niezależnych przypadków. Moduł jest badawczym CLI, nie widżetem GUI. Nie umieszczaj prywatnych pytań w repozytorium.

**Interpretacja:** to kontrolowane porównanie *działania opcji routingu dla utrwalonego stanu*, a nie dowód, że plastyczność sieci podniosła inteligencję. Kategoriom Qwen ani aktywacjom ACF nie przypisujemy skalibrowanego prawdopodobieństwa. Dosłowne trafienie frazy nie dowodzi zgodności z faktami. Ewentualna poprawa może wynikać z dodatkowego, trafniejszego fragmentu, a nie wzrostu zdolności uogólniania sieci. Niezależny audyt prawdziwych zadań pozostaje wymagany przed włączeniem opcji domyślnie.

## Zasady bezpieczeństwa i zachowania stanu

Nie zmieniamy istniejących plików pamięci, formatu semantycznej bazy, ograniczeń źródeł, ustawień internetu, modeli kontrolnych ani standardowej funkcji czatu. Brak migawki, uszkodzony stan, brak przewagi, konflikt znaczenia czy brak źródła powoduje **wstrzymanie eksperymentu**, bez generowania udawanych danych. Statusy nie zwracają pytania, treści źródła ani prywatnej ścieżki. W teście CLI SQLite i migawka są odczytywane bez zapisu.

**Następna bramka rozwoju:** niezależny holdout A/B/C z rzeczywistymi ocenami poprawności, wykrywanie pogorszenia, osobne porównanie ze stałą topologią przy tej samej liczbie dokumentów. Wynik niepotwierdzony lub ujemny oznacza pozostawienie funkcji jako eksperymentalnej, nie przypisywanie sukcesu.
