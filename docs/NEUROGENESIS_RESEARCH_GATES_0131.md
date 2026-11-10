# NeuroGenesis 0.13.1 — audyt i kryteria osiągnięcia celu

**Autor publiczny:** Miron przy pomocy AI.

## 1. Faktyczny stan względem pierwotnych założeń

NeuroGenesis ma prawdziwy lokalny Qwen3-1.7B w jednoplikowym Windows EXE, trwałą pamięć SQLite zatwierdzonych źródeł i ludzkich korekt, ograniczony autonomiczny agent celów, plastyczną sieć LIF/ACF uczącą się prognozowania ośmiu kanałów, monitor synaps, modelowane błędy prequential, kopie stanu i eksperymentalne narzędzia osobnego gradientowego uczenia Foundation/LoRA. NIE ma dowodów, że ta architektura osiągnęła ogólne rozumowanie, samodzielne uczenie języka, świadomość, biologiczną samonaprawę, przewagę plastyczności na rzeczywistych zadaniach czy ludzką równoważność.

Otwarte P0 w repo: #18 wyjście poza ośmiokanałowy model, #9 skalowanie CPU/GPU/wielokomputerowe, #8 autonomiczny rozwój z niezależnym audytem i rollback, #7 bezpieczna samonaprawa, #3 generalizacja i rzetelna ablacja struktury. Dodatkowo #5 prawdziwy samomodel umiejętności i #4 bezpieczna percepcja sieciowa. Żadnego z tych problemów nie wolno oznaczyć jako rozwiązanego tylko na podstawie przejścia testów programistycznych.

## 2. Nowy eksperyment: pamięć → nowe zadanie → mierzalna zmiana

Moduł **neurogenesis/correction_transfer.py** porównuje dwa warianty tego samego lokalnego Qwen z tą samą konfiguracją, bez historii rozmowy:

- A: uprzednio wytrenowany model Qwen bez pamięci (use_context=False).
- B: ten sam model wyłącznie z zatwierdzonymi korektami w prywatnym SQLite — bez innych TXT, HTTPS lub ACF.

Potrzebny jest **uprzednio przygotowany, niezależny, nieużywany podczas nauki** prywatny zestaw JSONL: 6–32 pytań, co najmniej trzy parafrazy dwóch różnych zatwierdzonych korekt i co najmniej trzy niepowiązane pytania kontrolne. Każde pytanie z etykietą "paraphrase" zawiera: question, expected_correction_id, expected_answer_fragment. Każde z etykietą "unrelated": question, forbidden_answer_fragment (fragment tekstu z innej pamięci, którego nie należy przywołać). Program odrzuca identyczne pytania treningowe, duplikaty i przypadki z docelową odpowiedzią jawnie wpisaną w pytaniu.

Przykładowa struktura pojedynczego wiersza (nie jest to pełny zestaw):

    {"kind":"paraphrase","question":"Podaj numer identyfikacyjny urządzenia Kobalt?","expected_correction_id":1,"expected_answer_fragment":"KOB-914"}
    {"kind":"unrelated","question":"Jak rozwija się burza słoneczna?","forbidden_answer_fragment":"KOB-914"}

Uruchomienie **ze źródłowego checkoutu z lokalnym, zweryfikowanym GGUF**, nie jako nowego przycisku w EXE:

    python -m neurogenesis.correction_transfer --corrections-db "C:\private\approved_corrections.sqlite3" --audit "C:\private\heldout.jsonl" --assets-root "C:\verified_bundle" --confirm-corpus-rights --confirm-heldout

Nie publikuj realnych pytań ani baz danych. Wynik liczy faktyczne dosłowne trafienia, prawidłową identyfikację korekty, błędne przypomnienia, regresję na pytaniach niepowiązanych, niepoparte cytowania, czas i dokładne sparowane statystyki. Zawiera tylko statystyki i skróty SHA256, **bez surowych danych prywatnych**. Wynik ujemny pozostaje widoczny. Model nie uczy się na próbie audytowej.

Pamięć jest odczytywana przez połączenie SQLite mode=ro, query_only=ON; przed i po każdej próbie test sprawdza logiczny SHA256 pamięci i PRAGMA data_version. Wykrycie zmiany pamięci przerywa cały eksperyment. Wagi Qwen nie są aktualizowane, nie ma żadnej automatycznej promocji.

**Granica dowodu:** dosłowna obecność spodziewanej frazy nie oznacza pełnej poprawności faktycznej ani uogólnienia. Testy jednostkowe wykorzystują syntetyczne sesje, dlatego są dowodem działania procedury, nie realnym wynikiem porównania Qwen. Niezależność danych wymaga prawdziwego operatora i nie może być automatycznie poświadczona przez program.

## 3. Naprawa kontaminacji niezależnego audytu neuralnego

Do 0.13.0 metoda NextInputPredictor.step(learn=False) blokowała tylko uczenie warstwy odczytu, ale jednocześnie wykonywała synaptyczną plastyczność STDP, zmiany wzorców, wzrost i przycinanie LIF. Wówczas sam „test” mógł aktualizować badany model.

Od wersji 0.13.1 Brain.step(learn=False) zachowuje elektryczną dynamikę — napięcia, impulsy, ślady i refrakcję — ale **nie zmienia wag i wieku synaps, nie dodaje/przycina neuronów i nie zapamiętuje wzorców**. Parametry odczytu również zostają zamrożone. Normalna funkcja learn=True pozostaje bez zmian; wcześniejsze migawki nie wymagają migracji. Wersjonowany protokół neurogenesis_bounded_self_development_v2_frozen_audit rozróżnia nowy, czystszy pomiar od poprzednich raportów.

## 4. Sześć bramek rzeczywistego ukończenia projektu

1. **Generalizacja:** poprawa rozwiązywania wielu niezależnych, wcześniej niewidzianych problemów z testami negatywnymi i sprawdzoną przez człowieka poprawnością.
2. **Przyczynowy wkład plastyczności:** ACF musi pokonać kontrolę o stałej topologii i mocne punkty odniesienia na różnych dziedzinach i nasionach losowych, przy porównywalnym koszcie CPU/RAM, bez utraty dawnych umiejętności.
3. **Autonomiczny rozwój:** kandydaci zmian są tworzeni i oceniani bez dostępu do niezależnej próby audytowej; poprawa oraz brak regresji warunkują zatwierdzenie. Każdą promocję można cofnąć.
4. **Samonaprawa:** testy uszkodzenia danych, utraty procesu, poprawnego wznowienia, konfliktów równoległych zapisów i integralności pamięci w długim okresie.
5. **Skalowanie:** zweryfikowany GPU i ewentualna wymiana stanu między komputerami ze ścisłym limitem zasobów, odtwarzalnością i ochroną prywatnych danych.
6. **Produkt:** rzeczywiście działający pojedynczy EXE, jasne rozróżnienie eksperymentu od potwierdzonej funkcji, wszystkie regresje, jawne zgody, podpisy integralności i dokumentacja.

**Werdykt:** część inżynieryjna jest stopniowo realizowana. „Najpotężniejsze AI / żywy cyfrowy mózg” nie jest obecnie osiągniętym wynikiem, ani naukowo potwierdzoną kategorią. Ukończenie należy definiować przez wyżej wymienione, z góry ustalone i powtarzalne wyniki, nie liczbę neuronów ani atrakcyjność animacji.
