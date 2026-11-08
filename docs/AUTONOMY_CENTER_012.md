# NeuroGenesis 0.12.0 — Autonomiczne Centrum Operacyjne

**Autor: Miron przy pomocy AI.**

## Główne okno po uruchomieniu

Po uruchomieniu pełnego EXE pierwsza karta to **AUTONOMIA**, a dalej
**ROZMOWA AI → WIEDZA TXT → MÓZG LIVE → Uczenie ręczne**. Stare
funkcje i istniejąca pamięć SQLite pozostają zachowane.

W odróżnieniu od starszego widoku z odizolowanymi zakładkami nowe
centrum łączy istniejące, realne moduły w jednym miejscu:
- **Inteligencja językowa** — status faktycznego procesu Qwen3-1.7B,
  przycisk uruchamiania, zatrzymania i wejścia do rozmowy.
- **Pamięć wiedzy** — rzeczywista liczba lokalnych plików i fragmentów
  w prywatnej SQLite, status zatwierdzonego folderu TXT, przycisk
  rozpoczęcia nauki.
- **Plastyczność LIF** — rzeczywiste zapisane kroki, liczba neuronów,
  liczba nowych doświadczeń, sprawdzone próby i zatwierdzone zmiany.
  Lokalna automatyczna próba ulepszania **włączona na starcie**, ale
  uruchamia się tylko po 40 nowych obserwacjach, z zachowaniem
  wcześniejszych zabezpieczeń; nie wykonuje automatycznych prób bez
  nowych danych. Trening działa poza wątkiem interfejsu.
- **Percepcja i badanie dziedziny** — status zgody HTTPS, liczba
  faktycznie zapisanych dokumentów, możliwość wpisania celu
  badawczego i uruchomienia rzeczywistego SpecialistStudy.
- **Aktywna specjalizacja** — oddzielne, świadomie włączane i
  ograniczone automatyczne sesje badania wybranego tematu.
  Wymagana zgoda HTTPS i poprawny temat, maksymalnie 3 uruchomienia
  w jednej sesji programu i co najmniej 30 min pomiędzy końcami
  kolejnych badań. SpecialistStudy nadal respektuje robots.txt,
  limity domen i tempo pobierania.
- **Automatyczna wiedza TXT** — używa TEGO SAMEGO kontrolera co
  karta WIEDZA TXT, nie tworzy dodatkowego ukrytego skanera.
  Wymagany wybór i zatwierdzenie praw do folderu. Jest to
  samodzielne aktualizowanie zindeksowanych danych, nie
  samodzielne dostrajanie 1,7 mld parametrów.
- **Monitor faktycznych zmian** — dziennik i schemat przepływu,
  oparte na odczytach SQLite oraz stanie procesu modelu;
  nie symulują impulsów, wzrostu zdolności ani postępu nauki.
  Diagram połączeń między modułami to opis przepływu danych,
  nie skan rzeczywistych biologicznych synaps.

## Rozmowa obejmuje też odkryte publiczne źródła

Zmiana w `BundledModelSession`: zatwierdzone, rzeczywiście
pobrane dokumenty HTTPS przechowywane w dotychczasowej
`experiences.sqlite3` są teraz dostępne przez
`ExperienceMemory.answer_from_knowledge()` i wraz z wybranymi
przez użytkownika lokalnymi TXT trafiają jako niezaufany kontekst
RAG do **prawdziwego modelu Qwen3-1.7B**. System pokazuje URL
w informacji o źródle; nie przedstawia źródła jako sprawdzonego
faktu. Uprawnienia HTTPS pozostają wyłączone domyślnie.

## Ograniczenia, których interfejs nie ukrywa

- Sam rozwój pamięci, wyszukiwanie źródeł i badania LIF nie
  dowodzą nowych ogólnych zdolności ani świadomego mózgu.
- Qwen3-1.7B jest realnym zewnętrznym modelem wytrenowanym
  przez Qwen, a nie własnym samouczącym się modelem NeuroGenesis.
- Nie istnieje bezwarunkowa niezależność od sprzętu, danych
  i energii. Automatyczne działania sieciowe wymagają zgody,
  a użytkownik zawsze może je zatrzymać.
- Główna aplikacja z modułami offline jest spakowana w dużym
  EXE. Nie gwarantuje to, że opcjonalne eksperymenty naukowe
  z dodatkowymi bibliotekami PyTorch/LoRA też są w nim zawarte.

## Akceptacja wersji

`--ui-self-test` Windows sprawdza teraz rzeczywiste widżety
karty AUTONOMIA i ich odczyt. Skrypt `scripts/tk_training_screenshot.py`
zapisuje faktyczny podgląd tego ekranu
`NeuroGenesis-Autonomy-Live.png`, nie obraz z internetu.
Testy autonomicznego badania sprawdzają wymaganą zgodę i limit
sesji, a test integracyjny sprawdza przekazanie niezaufanych
źródeł RAG do modelu. Pełna wersja EXE musi nadal przejść
obowiązkowy test rzeczywistej generacji z jego własnych
zintegrowanych wag.

**Stan**: implementacja w PR #57. Dopóki GitHub Actions, Windows
onefile i test prawdziwego modelu nie zakończą się sukcesem,
wpisu nie należy traktować jako gotowego publicznego wydania.
