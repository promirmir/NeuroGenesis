# NeuroGenesis 0.12 — autonomiczne centrum sterowania

## Nowy ekran domyślny

Główny ekran otwiera od razu lokalny model Qwen3-1.7B z wbudowanych wag i silnika llama.cpp. Pytanie wpisane podczas ładowania zostaje zakolejkowane i wysłane samoczynnie. Bez oddzielnego Pythona i zewnętrznego API.

Dwa intuicyjne obszary: rozmowa po lewej; samodzielne cele, ich raporty i podgląd rzeczywistej sieci LIF po prawej. Zakładki laboratoryjne i klasyczna rozmowa zostały przeniesione pod Zaawansowane, bez usuwania ich możliwości. Prawy panel przewija się na laptopach.

## Rzeczywista pętla zadań

1. Operator wpisuje trwały cel (12–600 znaków). Cel jest zapisany w lokalnym agent_goals.sqlite3.
2. Agent samodzielnie przeszukuje wcześniej zatwierdzone pliki TXT w SQLite FTS5. Jeżeli brak źródeł, lokalny model przygotowuje plan i wyszczególnia brakujące dane. Zadanie ma stan WAITING; nie udaje sukcesu.
3. Gdy istnieją pasujące źródła, model tworzy nowy raport-kandydat, do którego dołączane są faktyczne nazwy plików i SHA-256. Ma stan CANDIDATE, wymaga oceny.
4. Co około 9,5 s agent sprawdza, czy zatwierdzony korpus wiedzy został zmieniony. Nowe/zmienione TXT uruchamiają ponowną analizę niedokończonych celów (limit 32 prób). Bez zmiany wiedzy nie zapętla zbędnych odpowiedzi.
5. Operator może obejrzeć raport, zatwierdzić go, wstrzymać lub wznowić. Zadania przerwane przez restart wracają do kolejki.
6. Rozmowa użytkownika i proces analizowania celu współdzielą JEDNĄ wczytaną kopię modelu językowego. Bieżące wiadomości mają pierwszeństwo przed nową analizą autonomiczną.

## Rzeczywista telemetria i samodoskonalenie LIF

Ekran odczytuje liczbę zapisanych neuronów, synaps, kroków, impulsów i doświadczeń z SQLite. Rysuje rzeczywisty connectome, który nie animuje nieistniejących bodźców. Użytkownik może wyłączyć rejestrację cech zmysłowych rozmowy; gdy jest włączona, zapisywane są wyłącznie numeryczne cechy (nie surowy tekst rozmowy).

AutonomicSupervisor sam testuje poprawę predyktora LIF, gdy uzbiera się 40 nowych doświadczeń. Walidacja może propozycję odrzucić. Żaden wzrost neuronów nie jest utożsamiany z rozumowaniem językowym.

## Weryfikowalne ograniczenia

Jest to samodzielna pętla celu → plan → analiza zatwierdzonych danych → raport i ponowna analiza po zmianach. To nie jest AGI, automatyczne przejęcie komputera, swobodne skanowanie całego internetu, samodzielna modyfikacja kodu ani gradientowe trenowanie 1,7 mld wag Qwen. Internet nadal wymaga osobnej zgody.

Testy obejmują trwałość celów, przerwanie i wznowienie, rozpoznanie nowych źródeł, brak fikcyjnych sukcesów, prywatność i UI. Release FULL 0.12 wymaga dodatkowo prawdziwej generacji odpowiedzi z dużego EXE w Windows CI. Nie wolno ogłaszać gotowego wydania przed powodzeniem tych testów.

Publiczny podpis: Miron przy pomocy AI.
