# NeuroGenesis 0.12.8 — uczciwy test wkładu plastycznej sieci ACF

**Autor publiczny:** Miron przy pomocy AI.

## Jaki błąd metodologiczny naprawiamy?

W wersji 0.12.7 test A/B/C porównywał Qwen, Qwen+RAG i Qwen+RAG+ACF. Gdy C dodawał nowe źródło i odpowiadał lepiej, **nie dało się stwierdzić**, czy poprawę spowodowała prognoza sieci ACF, czy samo dodatkowe wyszukiwanie.

Wersja 0.12.8 wprowadza rzetelniejszą ablację z czwartym wariantem, bez włączania eksperymentu wszystkim użytkownikom:

| Ramię | Co robi |
|---|---|
| A — Qwen | Zwykły wbudowany lokalny Qwen3-1.7B, bez kontekstu TXT |
| B — Qwen+TXT | Zwykły retrieval/RAG lokalnych zatwierdzonych tekstów |
| C — Qwen+TXT+ACF | To samo RAG, plus ewentualna prognoza historycznie uczonego ACF |
| D — Qwen+TXT+temat bieżący | To samo RAG i jedna dodatkowa próba wyszukiwania, ale **bez prognoz ACF**; bazuje na bieżącej klasyfikacji Qwen |

**Pierwszoplanowym testem jest C kontra D.** Obydwa warianty dysponują tą samą zatwierdzoną bazą, tym samym klasyfikatorem, słownikiem zapytań FTS, progiem 2 odrębnych słów-kluczy i budżetem maksymalnie czterech źródeł. D wybiera jedną dziedzinę za pomocą z góry ustalonego dopasowania słów pytania do słowników dziedzin; przy remisie rozstrzyga stała kolejność osi. Nie wolno wybierać dziedziny na podstawie oczekiwanej odpowiedzi ani treści znalezionych źródeł. C może wstrzymać się, gdy jego rzeczywiście zmierzony błąd prognozy przegrywa z modelami kontrolnymi lub przewidywany temat nie zgadza się z aktualnym pytaniem.

**Zasada antyregresyjna:** jeśli cztery fragmenty są już w kontekście, nowy fragment z C lub D może zastąpić czwarty tylko przy *ściśle większej* liczbie zgodnych słów-kluczy. Nie dopuszczamy automatycznego wypierania lepiej dopasowanego źródła.

## Wykonanie rzeczywistego eksperymentu

Źródłowe narzędzie `python -m neurogenesis.dialogue_abcd` przyjmuje prywatny lokalny JSONL z 4–32 niezależnymi przypadkami (takimi jak w `DIALOGUE_PAIRED_EVALUATION_0126.md`), zatwierdzony korpus TXT, istniejącą migawkę semantycznego ACF oraz komplet zweryfikowanych lokalnych zasobów GGUF.

Przykładowo z lokalnego środowiska źródłowego:

    python -m neurogenesis.dialogue_abcd --db "C:\private\local_knowledge.sqlite3" --audit "C:\private\holdout.jsonl" --acf-state "C:\private\semantic_fabric.acf.json" --assets-root "C:\verified_bundle" --confirm-corpus-rights --confirm-heldout

Trzeba użyć **rzeczywistych, uprzednio nieużytych pytań oraz własnych danych z właściwymi uprawnieniami**. Nie wysyłaj pytań ani korpusu na GitHub. Najlepiej zamknąć równoległą aplikację na czas badania. Skrypt wykrywa zmiany migawki ACF, datyfikowane zmiany w lokalnych indeksach SQLite oraz zmianę wersji korpusu podczas badania; przerywa zamiast mieszać wyniki z różnych stanów pamięci. Nie używa internetu. Nie wykonuje dodatkowego treningu.

Dla każdego pytania używa tego samego rzeczywistego Qwen, identycznego ustawienia deterministycznego dekodowania i rotuje kolejność A/B/C/D, aby ograniczyć efekt kolejności. Raport zawiera jedynie zagregowane wyniki; nie zawiera pytań, odpowiedzi ani prywatnych nazw plików.

## Interpretacja wyników

- Zliczamy dosłowne wystąpienie oczekiwanej frazy, trafienia nazw źródeł i odwołania do nieistniejących źródeł. **To NIE jest pełne sprawdzenie prawdziwości odpowiedzi.**
- Dla C i D podajemy pary rozstrzygające na korzyść każdego z nich, różnicę odsetków, dokładny dwustronny test sparowanych wyników binarnych oraz opisowe przedziały Wilsona (95%). Testy są eksploracyjne, bez korekty wielokrotnego porównywania. Maksymalnie 32 przypadki nie wystarczą do wykazania uniwersalnej przewagi.
- Raport pokazuje zarówno wyniki negatywne, jak i sytuacje bez zmiany, liczbę rzeczywistych ingerencji ACF oraz liczbę przypadków, w których C i D ostatecznie wybrały te same źródła.
- Rzeczywista przewaga C nad D **nadal nie dowodzi**, że wzrost liczby neuronów spowodował lepszą inteligencję. Do tego wymagany jest kolejny niezależny test strukturalnej plastyczności kontra identyczny model bez wzrostu synaps oraz weryfikacja przez człowieka.

## Zabezpieczenia i testy wydania

Domyślny Windows EXE i zapisane pamięci SQLite zachowują dotychczasowe działanie. ACF w panelu pozostaje eksperymentem **wyłączonym domyślnie**. Nie ma samoczynnego włączania funkcji na podstawie raportu, zmiany wag Qwen, internetowego crawlowania ani rozsyłania prywatnych tekstów.

GitHub CI testuje obie drogi pobierania fragmentów na realnym lokalnym SQLite, kontrolę limitu, brak regresu domyślnej rozmowy, odmowę przy złym pochodzeniu danych, prywatność raportu i reakcję na modyfikację stanu podczas testu. Pełna kompilacja Windows dodatkowo uruchamia prawdziwy Qwen z przygotowanego modelu **i z jednoplikowego EXE**, w tym nowy nie-neuronowy tor kontroli tematu. Same testowe sztuczne odpowiedzi i sztuczne dane ACF **nie są** ogłaszane pomiarem inteligencji.

**Stan naukowy:** przygotowany protokół porównawczy, nieudowodniony dodatni efekt ACF do czasu realnej niezależnej ewaluacji.
