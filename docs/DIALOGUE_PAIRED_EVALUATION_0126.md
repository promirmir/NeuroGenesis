# NeuroGenesis 0.12.6 — rzeczywisty test jakości odpowiedzi z pamięcią

**Autor:** Miron przy pomocy AI.

## Cel

W 0.12.5 ACF podejmuje eksperymentalną decyzję o odczycie lokalnych dokumentów, ale nie ma dowodu, że jej plastyczność poprawia rozmowę. Moduł neurogenesis/dialogue_ab.py mierzy odpowiedzi prawdziwego, lokalnego Qwen3-1.7B w dwóch warunkach:

- **A — Qwen bez źródeł:** model GGUF bez tekstów TXT i bez źródeł HTTPS.
- **B — Qwen z zatwierdzonym TXT:** ten sam proces modelu, te same pytania i limit odpowiedzi, z rzeczywiście pobranymi fragmentami lokalnych zatwierdzonych tekstów.

Generacja z wyłączonym próbkowaniem. Test przełącza kolejność A/B na B/A dla co drugiego pytania. Żadna odpowiedź testowa nie staje się historią następnego pytania. Raport agreguje dosłowne trafienia wskazanej frazy, trafienia właściwej nazwy źródła, wystąpienia niepopartych cytowań [L1], sparowane sukcesy i porażki, średni czas i różnicę wyników. Raport pokazuje także wyniki zero lub ujemne.

**Prywatność:** pytania, odpowiedzi i nazwy plików nie są umieszczane w raporcie. Baza wiedzy jest otwierana przez SQLite w trybie tylko do odczytu, bez indeksowania i zmian. Nie ma sieci, chmury, pobierania, treningu wag ani ingerencji w ACF.

## Format audytu

Utwórz prywatny plik JSONL (od 4 do 32 niezależnych pytań). Każdy wiersz ma dokładnie pola question, expected_answer_fragment, expected_source. Przykład:

    {"question":"Jakie zjawisko opisuje notatka o indukcji?","expected_answer_fragment":"indukcja elektromagnetyczna","expected_source":"fizyka.txt"}

Nazwa expected_source odnosi się do już zatwierdzonego i zaimportowanego pliku TXT. Nie publikuj pliku próby, jeśli zawiera wrażliwe informacje. Jawnie potwierdź prawa do materiałów i brak użycia próby do wcześniejszego doskonalenia.

Przykładowe uruchomienie z przygotowanego pełnego pakietu lokalnego GGUF (ng_runtime i ng_assets):

    python -m neurogenesis.dialogue_ab --db "C:\private\local_knowledge.sqlite3" --audit "C:\private\audit.jsonl" --assets-root "C:\trusted_bundle" --confirm-corpus-rights --confirm-heldout

To jest narzędzie badawcze źródłowe, nie nowy instalator ani funkcja dostępna przyciskiem w aktualnym EXE. Wymaga lokalnie dostępnych i zweryfikowanych składników modelu; nigdy nie pobiera ich samodzielnie.

## Kryteria kolejnych eksperymentów

1. Zmierzyć bezstronnie A kontra B na uprzednio nieużytych pytaniach, wraz z nieudanymi przypadkami i fałszywymi cytatami.
2. Dopiero później dodać wariant C, w którym ACF ma rzeczywisty wpływ na wybór źródeł dla konkretnego pytania — ale wyłącznie po weryfikacji i bez automatycznego nadawania źródłom wiarygodności.
3. Porównać A/B/C na niezależnej nowej próbie oraz zachować model kontrolny i bramki antyregresji przed włączeniem C do domyślnej rozmowy.

Dosłowne dopasowanie nie jest dowodem prawdziwości stwierdzenia, samodzielnego rozumowania, samouczenia wag Qwen ani AGI. Uczciwy wynik negatywny jest bardziej wartościowy od deklarowania nieistniejącej poprawy.
