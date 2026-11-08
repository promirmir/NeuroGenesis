# NeuroGenesis — ACF v1: rzeczywista plastyczność, uczenie i samomodel

**Status:** działający moduł badawczy, nie potwierdzony przełom ani AGI.

**Autor:** Miron przy pomocy AI.

## Problem, który naprawiamy

Dotychczas sieć LIF, model językowy Qwen3-1.7B, pamięć TXT i agent celów były rozdzielnymi mechanizmami. Wzrost liczby neuronów LIF nie przekładał się automatycznie na lepsze rozumowanie. Nie wolno nazywać samych wzrostów liczby połączeń „wzrostem inteligencji”.

ACF v1 tworzy **rzeczywisty, autonomiczny układ predykcyjny** weryfikujący, czy plastyczny substrat wnosi wartość ponad model kontrolny. To pierwszy etap mierzalnego samomodelowania.

## Co zostało zaimplementowane

- **Dwie porównywalne sieci LIF i głowice predykcyjne** w `neurogenesis/acf.py`: jedna ma możliwość dodawania neuronów i połączeń, druga używa tej samej architektury początkowej, ziarna losowego i tempa uczenia, ale bez wzrostu strukturalnego.
- **Dwa nieneuronowe punkty odniesienia**: przewidywanie ostatniej obserwacji oraz stała wartość 0,5. Żadna z czterech metod nie jest z góry faworyzowana.
- **Uczenie przyczynowe, online**: system ocenia przewidywanie poprzedniego kroku *przed* dopuszczeniem nowego bodźca do treningu. Zmierzony błąd przewidywania jest dodawany do okna 128 wyników. Po rozgrzewce 24 pomiarów mechanizm wybiera model z najniższym historycznym MSE, z histerezą zapobiegającą skokom między wariantami.
- **Samomodelowanie oparte na danych**, nie opis generowany przez chatbot: odczyt błędów każdej metody, wskazanie używanej drogi predykcji, obserwacja rozrostu/przycinania synaps oraz jawne sygnały „brak udowodnionej przewagi”. Przybliżone RMSE nie jest skalibrowanym prawdopodobieństwem poprawności.
- **Trwała pamięć**: pojedynczy, atomowo zapisywany JSON z rzeczywistymi neuronami, synapsami, głowicami, historią pomiarów, wybraną trasą i kursorem przetworzonych zdarzeń. Odtwarzanie z dysku zachowuje identyczne dalsze wyniki.
- **Autonomiczne przyswajanie doświadczeń aplikacji** poprzez `FabricMemoryObserver`: odczytuje tylko nowe `id, features` z istniejącej `experiences.sqlite3`. Nie pobiera `raw_text`, treści rozmów ani URL, nie zmienia istniejącej pamięci i nie uruchamia połączeń sieciowych. Każda nowa obserwacja może zaktualizować ACF; brak nowych bodźców oznacza brak „magicznego” postępu. Dodatkowy stan pozostaje w `adaptive_fabric.acf.json` obok bazy aplikacji.
- **Panel rzeczywistego stanu** w głównym oknie: liczba obserwacji, nowych i istniejących neuronów, wzrost/przycięcia, wybrana metoda predykcji i faktyczny zmierzony MSE, z etykietą mówiącą, że nie są to semantyczne zdolności chatbota.

## Reprodukowalny eksperyment porównawczy A → B → A

Uruchom bez żadnych pobrań ani CUDA:

```powershell
python -m neurogenesis.acf_experiment --steps-per-phase 96 --seed 7
```

Protokół generuje identyczne sekwencje bodźców dla wszystkich metod, przeprowadza zmianę zadania A → B i powrót do A, a następnie zwraca rzeczywisty błąd **prequential MSE** dla każdego etapu. Uwzględnia także:
- liczbę neuronów i synaps wariantu wzrastającego i kontrolnego;
- średni błąd faktycznie wybranej metody;
- różnicę błędu wariantu adaptacyjnego względem kontrolnego, **również gdy wynik jest ujemny**;
- jawne oznaczenie, czy plastyczność w ogóle poprawiła przewidywanie w etapie powrotu do zadania A.

Testy `tests/test_acf.py` dodatkowo sprawdzają restart, atomowość kursora, brak użycia surowego tekstu i brak aktualizacji stanu po błędnych danych.

## Czego ACF v1 jeszcze nie potrafi

W szczególności **nie potrafi** samodzielnie modyfikować wag Qwen3-1.7B i nie jest układem semantycznego rozumienia. Obecne 8 cech pochodzą z haszującego sensora `TextSensor`; mogą reprezentować podobieństwa obliczeniowe, ale nie są dowodem rozumienia pojęć. To oddzielny substrat badawczy, którego predykcje nie sterują jeszcze wyborami wyższego poziomu agenta.

Aby mówić o innowacyjnym sztucznym mózgu, kolejne etapy muszą wykazać na *niewidzianych zadaniach*, że predykcja ACF poprawia pamięć, planowanie lub decyzje względem systemu bez ACF. Konieczny jest **strumień semantycznych reprezentacji** i bezpieczny sprzęgłowy interfejs ze zdolnościami językowymi, następnie testy retencji wiedzy i realnej korzyści. Brak poprawy jest poprawnym wynikiem naukowym i nie może być ukrywany.

**Nie deklarujemy:** AGI, świadomości, „najmocniejszej AI na świecie”, nieograniczonego samorozwoju ani udowodnionej przełomowości. Te wnioski wymagałyby wielokrotnie silniejszych dowodów niż bieżący eksperyment.
