# NeuroGenesis v0.5.7 — autonomiczne uczenie kontekstu czasowego

**Autorstwo publiczne: Miron przy pomocy AI.**

## Co naprawdę działa

Program podczas **każdej** wiadomości lokalnie aktualizuje dwie
odrębne, lecz połączone części mechanizmu poznawczego:

1. Dotychczasowy impulsowy mózg LIF z plastycznością synaps otrzymuje
   deterministyczny wektor ośmiu kanałów sensorycznych.
2. Nowy odczyt ContextualNextInputPredictor uczy się przewidywać
   kolejny wektor, wykorzystując bieżący bodziec, poprzedni bodziec oraz
   zagregowane **rzeczywiste ślady aktywności neuronów**.

Formalnie wektor cech dla przewidywania następnego zdarzenia ma postać:

    phi_t = [1, fold(x_t), fold(x_{t-1}), activity(traces_t)]

Odczyt prognozuje clamp(W * phi_t, 0, 1), a po nadejściu x_(t+1)
rejestruje błąd MSE przed jakąkolwiek aktualizacją wag. Reguła uczenia:

    W_i <- clip(W_i + lr * (x_(t+1)[i] - p_i) * phi_t
                          / (1 + ||phi_t||^2), -4, 4)

Nie ma etykiet dostarczanych przez użytkownika ani konieczności kliknięcia
przycisku uczenia: celem samonadzoru jest następny bodziec. Model ma
ograniczone zasoby: 25 cech stałej długości, wektor odpowiedzi szerokości
sensorycznej, wagi [-4,4], skończone wskaźniki błędów i limit snapshotu 16 MiB.

Model korzysta z rzeczywistych śladów neuronów, ale stanowi **dodatkowy
odczyt uczenia nad istniejącym mózgiem**, a nie pełny model biologicznego
rozumienia mowy. Składniki wejścia można osobno wyłączyć w badaniach
(use_history, use_neural), co umożliwia naukową kontrolę ablacją.

## Pamięć i kompatybilność

- Dane pozostają wyłącznie w prywatnej bazie SQLite.
- Nowa tabela contextual_state przechowuje numeryczne wagi, wcześniejszy
  skrócony bodziec, prognozę i statystyki MSE. **Nie zapisuje surowego tekstu**.
- Wszystkie kroki istniejącego mózgu, ewentualnego adaptacyjnego predyktora,
  nowego modelu kontekstu i zdarzenia są wykonywane w **jednej transakcji
  BEGIN IMMEDIATE**. Niepowodzenie któregokolwiek modułu nie zatwierdza
  częściowego uczenia.
- Dotychczasowy schemat SQLite v1, ręcznie nauczone odpowiedzi, stary
  predyktor oraz mechanizm autonomicznych eksperymentów pozostają obsługiwane.
- Uszkodzony lub nadmiernie duży snapshot zostaje odrzucony. Nie powstaje
  automatycznie nowy pusty mózg w miejsce uszkodzonego.
- Stare bazy bez contextual_state działają dalej. Po pierwszym kolejnym
  bodźcu pojawia się nowy model, bez nadpisywania historii.

## Dowody i ich granice

Przygotowane testy porównują prognozy na przyszłych epizodach, **bez
dopasowywania wag do epizodów testowych**, z kontrolą bez pamięci poprzedniego
bodźca. Oddzielny test wykorzystuje rzeczywiste neurony LIF i ich ślady.
Ablacja pamięci pokazuje przydatność kontekstu na syntetycznych sekwencjach.
Wynik nie oznacza znajomości znaczenia słów, rozumowania przyczynowego,
pamięci autobiograficznej ani przewagi nad dojrzałymi modelami językowymi.
Test sekwencji ma tę samą regułę tworzenia danych podczas treningu i oceny;
nie stanowi dowodu generalizacji poza rozkład.

Interfejs Mózg wyświetla liczbę ocenionych przejść i MSE. Odpowiedzi
językowe są nadal odtwarzane tylko z **jawnie nauczonej** tabeli
pytanie–odpowiedź, z opisem źródła. Bez nowej semantycznej zdolności
nie wolno udawać odpowiedzi wygenerowanych przez neurony.

## Dalszy etap

Nauczyć model reprezentacji związków między wieloma słowami, budować trwałe
i weryfikowalne pojęcia oraz oceniać uogólnianie na nowe zdania i nowe
relacje między pojęciami. Wymaga to wyższego wymiaru reprezentacji językowej
i faktycznych danych treningowych; obecne osiem kanałów haszujących nie
zachowuje znaczenia ani porządku wszystkich słów. Rozszerzenie powinno
mieć niezależną kontrolę, testy zapominania oraz budżety CPU/RAM.
