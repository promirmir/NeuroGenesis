# NeuroGenesis v0.5.6 — nauka lokalnych odpowiedzi

**Autorstwo: Miron przy pomocy AI.** This is working manually supervised association and neural sensory input, **not natural-language reasoning by the spiking network**.

## W aplikacji Windows

1. Otwórz zakładkę **Rozmowa**.
2. W głównym polu wpisz pytanie, np. **Czym jest synapsa?**
3. W polu pod nim wpisz odpowiedź, np. **Synapsa łączy neurony.**
4. Kliknij **Naucz odpowiedzi**. To wyraźna zgoda na zapis pytania i odpowiedzi w prywatnej bazie SQLite. W tej samej transakcji pytanie jest przetwarzane przez istniejącą sieć neuronową.
5. Kliknij **Przekaż do mózgu**. Otrzymasz nauczoną odpowiedź. Wielkość liter, powtarzające się odstępy i końcowe znaki ?!. nie zmieniają identyfikacji pytania.
6. Możesz wpisać nową odpowiedź dla tego samego pytania, aby ją poprawić, lub kliknąć **Usuń nauczoną odpowiedź** i potwierdzić usunięcie.

Aplikacja nie zgaduje odpowiedzi na pytania, których nie nauczono. Nie łączy wyrazów w nowe znaczenia ani nie produkuje tekstu z własnej wyobraźni. W odróżnieniu od zwykłego potwierdzenia bodźca, wynik pochodzi z jawnej, lokalnej pary pytanie–odpowiedź. Stan spiking brain aktualizuje się podczas zdarzenia, ale tekst odpowiedzi NIE został wygenerowany przez neurony. Ten rozdział jest celowy — umożliwia obiektywną ocenę przyszłego postępu neuralnego uczenia.

## Technicznie: zachowanie pamięci

- Nowa tabela taught_responses istnieje w tym samym prywatnym SQLite co observations, neural_state i opcjonalny predictor_state. Schemat v1 pozostaje; istniejące bazy są migrowane addytywnie.
- Nauczenie pary pytanie–odpowiedź i cztery kroki mózgu są jednym BEGIN IMMEDIATE z commit/rollback. Nie występuje osobny mózg ani niezależny plik pamięci.
- Uczenie jawnie przechowuje znormalizowane pytanie i treść odpowiedzi. Zwykłe obserwacje nadal nie przechowują surowych wiadomości bez zaznaczenia odrębnej opcji. Nie wpisuj sekretów.
- Pojemność: 512 różnych par, pytanie maks. 512 znaków, odpowiedź maks. 2000. Korekta istniejącej pary nie zwiększa ich liczby.
- Odtworzenie jest dokładne po normalizacji: brak dopasowań przybliżonych, samodzielnego wyszukiwania w internecie i uogólniania semantycznego. Kontrola integralności odrzuca uszkodzony zapis i nie nadpisuje go automatycznie.
- Usunięcie pary usuwa tekst odpowiedzi, ale nie cofa plastyczności neuronowej i nie usuwa innych doświadczeń.
- Pamięć w %LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3 nie jest szyfrowana. Aktualizacja EXE nie powinna jej zastąpić. Wykonuj prywatne kopie zapasowe.
- Przy aktywnym samodostosowującym się predyktorze v0.5.5 nauczony bodziec aktualizuje dokładnie ten sam predyktor i mózg w jednej transakcji.

## Weryfikacja

Nowe testy SQLite sprawdzają restart, korektę, rzeczywistą odpowiedź panelu, prywatność zwykłych obserwacji, rollback, limity, SQL injection jako dane, usuwanie, odmowę skorumpowanego zapisu, długie wiadomości i zgodność z predyktorem autonomicznym. Windows PyInstaller --self-test dodatkowo tworzy skojarzenie i odczytuje je. Przed wydaniem wymagane jest CI Python 3.11/3.12/3.13 i Windows EXE.

## Następny etap

Rzeczywista neuronowa reprezentacja znaczeń, generalizacja na niewidziane sformułowania, niezależna walidacja OOD, bogatsze kodery sensoryczne i bezpieczny internet opt-in pozostają osobnymi celami. Nie ogłaszaj tych funkcji jako istniejących.
