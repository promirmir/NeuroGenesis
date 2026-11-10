## NeuroGenesis 0.13.2 — niezależny czasowo, zamrożony test plastycznej sieci ACF

Nowy **weryfikowalny audyt własnej sieci** sprawdza, czy rozwój neuronów poprawia prognozowanie późniejszych, niewidzianych obserwacji. Na 70% rzeczywiście zapisanych lokalnych kategorii Qwen uczy dwie sieci — plastyczną i o nierosnącej strukturze — po czym na pozostałych 30% **nie pozwala im już aktualizować wag, synaps ani topologii**. Z góry ustalone pięć inicjalizacji, dwie części testu, kontrola ostatniego zdarzenia, kontrola stałej 0,5, jawny koszt neuronów i synaps oraz wynik także ujemny. Odczytuje prywatne SQLite wyłącznie read-only, nie zmienia Qwen ani zwykłej rozmowy. **To jeszcze nie jest dowód poprawy językowej inteligencji ani AGI**, a testy syntetyczne CI nie są realną ewaluacją użytkownika. [Protokół, ograniczenia i polecenie uruchomienia](docs/ACF_FROZEN_TEMPORAL_HOLDOUT_0132.md).

## NeuroGenesis 0.13.1 — rzetelny test transferu i zamrożonej walidacji sieci

**Dwa konkretne wzmocnienia:** prywatny eksperyment porównujący realne odpowiedzi Qwen bez pamięci i z zatwierdzonymi korektami na nowych parafrazach oraz niepowiązanych kontrolach; naprawa błędu, przez który dotychczasowe próby `learn=False` nadal uczyły synapsy i zmieniały strukturę sieci LIF. Teraz badanie nie zmienia wag, wzorców ani topologii; rzeczywista aktywność elektryczna pozostaje. Nowe testy mierzą również fałszywe wspomnienia, regresję i zmiany prywatnej pamięci podczas audytu. Brak niezależnego prywatnego holdoutu oznacza, że nie deklarujemy jeszcze poprawy inteligencji. Domyślna rozmowa, dane i istniejący EXE zachowują dotychczasowe funkcje. [Audyt pierwotnego celu, procedura eksperymentu i kryteria ukończenia](docs/NEUROGENESIS_RESEARCH_GATES_0131.md).

## NeuroGenesis 0.13.0 — rzeczywista pamięć korekt między rozmowami

W głównej aplikacji dostępny jest przycisk **„PAMIĘĆ POPRAWEK / ZAPAMIĘTAJ I POPRAW”**. Wpisz własną poprawioną odpowiedź, zatwierdź ją i wykorzystaj wiedzę w następnej rozmowie — również po zamknięciu i ponownym uruchomieniu programu. Oddzielne, prywatne SQLite zapisuje tylko pytania i poprawki **jawnie zaakceptowane** przez operatora. Korektę można później edytować lub usunąć. Qwen3-1.7B otrzymuje co najwyżej jedną trafną korektę jako oznaczone, niezaufane dane; automatyczne zapisywanie rozmów pozostaje wyłączone. Wagi Qwen się nie zmieniają. Rzeczywisty test modelu z kompletnym Windows EXE potwierdza odtwarzanie syntetycznego kodu po jego zatwierdzeniu i zapisie. [Dokładne zasady pamięci, usuwania i bezpieczeństwa](docs/DURABLE_CORRECTIVE_MEMORY_0130.md).

## NeuroGenesis 0.12.9 — odporność na uszkodzenie stanu uczącego się ACF

Nowy mechanizm **zachowuje poprzednią, poprawną migawkę sieci neuronowej**. Przy uszkodzeniu głównego pliku JSON sprawdza pochodzenie poprzedniego stanu w oryginalnym dzienniku SQLite, zachowuje uszkodzone bajty w pliku diagnostycznym i odtwarza brakujące rzeczywiste obserwacje. Przy niezgodności **wstrzymuje aktualizację bez kasowania danych**; wykrywa też konflikty migawek. Panel pokazuje potwierdzone odzyskanie. W eksperymentach A/B/C/D poprawiono wykrywanie niepopartych cytowań, także `[L0]`, `[L100]`, `[L999]`. **Nie udowadnia to jeszcze wzrostu inteligencji ani odzyskiwania brakujących danych.** [Ograniczenia, scenariusze awaryjne i testy](docs/ACF_VERIFIED_RECOVERY_0129.md). Istniejące SQLite, wagi Qwen, interfejs i domyślny tryb rozmowy pozostają bez migracji.

## NeuroGenesis 0.12.8 — czteroramienny test rzeczywistego wkładu ACF

Dodano **kontrolę bez plastycznej sieci**: lokalny Qwen+TXT RAG z doborem jednego dodatkowego zatwierdzonego fragmentu na podstawie bieżącego tematu. Porównuje się ją na tej samej próbie z RAG kierowanym prognozą ACF, zwykłym RAG i samym Qwen. Kryteria doboru, budżet źródeł i klasyfikator są takie same; nowy fragment nie może wyprzeć lepiej dopasowanego czwartego dokumentu. Test A/B/C/D zbiera sparowane wyniki, test dokładny i przedziały opisowe, sprawdza zamrożenie ACF/SQLite, niczego nie wysyła ani nie trenuje. **Nie udowodniono jeszcze poprawy jakości AI**. Wbudowany test modelu sprawdza rzeczywistą ścieżkę kontrolną także z gotowego Windows EXE. [Dokumentacja](docs/ACF_MATCHED_ABLATION_0128.md). Domyślna aplikacja, wagi i lokalna pamięć pozostają niezmienione.

## NeuroGenesis 0.12.7 — aktywne, kontrolowane wykorzystanie ACF w rozmowie

**Eksperyment, domyślnie wyłączony:** ACF po wykazanej przewadze prequential MSE i zgodności rozpoznanego znaczenia bieżącego pytania może dodać **jeden** nowy fragment uprzednio zatwierdzonego lokalnego TXT do rzeczywistego kontekstu Qwen3-1.7B. Brak dowodu poprawy jakości rozmowy; decyzje są wstrzymywane przy niepewności. Nowy protokół A/B/C mierzy osobno Qwen, Qwen+TXT oraz Qwen+TXT+ACF. Kod nie zmienia wag Qwen, nie modyfikuje prywatnych baz i nie udaje AGI. [Dokumentacja i bezpieczeństwo](docs/ACF_DIALOGUE_ROUTING_0127.md).

## NeuroGenesis 0.12.6 — weryfikacja jakości odpowiedzi Qwen w warunkach kontrolnych

Dodano rzeczywisty, lokalny, prywatny test A/B: ten sam Qwen3-1.7B bez źródeł vs z zaakceptowaną wiedzą TXT, z pomiarem trafień, kosztu czasu i błędnych cytowań. W ramach eksperymentu nie zmieniamy domyślnego interfejsu ani pamięci. W tej wersji nie ma jeszcze dowodu, że ACF poprawia dialog. [Protokół i instrukcja](docs/DIALOGUE_PAIRED_EVALUATION_0126.md).

## NeuroGenesis 0.12.5 — ACF podejmuje pierwszą mierzalną decyzję

Nowa `semantic_policy.py` zamyka pierwszą realną pętlę działania:
**lokalne doświadczenie → plastyczne uczenie → porównanie błędów →
wybór strategii → odczyt zatwierdzonej wiedzy TXT**. Agent może
samodzielnie przygotować maksymalnie 3 lokalne fragmenty dotyczące
spodziewanego następnego tematu. Własna plastyczna sieć ACF musi
najpierw uzyskać wystarczającą liczbę przyczynowo ocenionych prognoz
i **udowodnioną, wstępną przewagę MSE nad trzema punktami odniesienia**.
W przeciwnym razie powstrzymuje się od działania; pulpit podaje
konkretny powód. Żadnych samoczynnych zapytań do Internetu.

Jest to rzeczywista, odwracalna operacja na własnej bazie wiedzy.
Nie należy jej mylić z automatyczną poprawą odpowiedzi Qwen:
program nie wstawia przewidywanych materiałów do rozmowy bez
niezależnej weryfikacji, a przewidywanie tematu nie jest skalibrowaną
pewnością. Testy oceniają trafność prognoz na kolejnych prawdziwych
zdarzeniach, uwzględniając niewykonane decyzje i wyniki ujemne.

[**Metodologia, progi, ograniczenia i polecenie audytu**](docs/SEMANTIC_DECISION_GATE_0125.md).

---

## NeuroGenesis 0.12.4 — rzeczywiste znaczenie trafia do plastycznej sieci

Po każdej udanej rozmowie (przy włączonej zgodzie na uczenie) **wbudowany Qwen3-1.7B** osobno klasyfikuje znaczenie wypowiedzi w ośmiu kategoriach. Powstaje rzeczywisty modelowy wektor semantyczny — nie dotychczasowy hash liter. Trafia on do drugiego, niezależnego ACF, który autonomicznie uczy się przewidywać kolejne kategorie, porównuje plastykę strukturalną z nierozrastającą się kontrolą i zapisuje mierzalny samomodel.

Całość działa lokalnie, asynchronicznie i bez zapisywania treści rozmowy. Główny ekran pokazuje liczbę rzeczywiście zebranych próbek i zmierzony błąd MSE. Nieprawidłowa klasyfikacja **nie powoduje tworzenia fikcyjnego treningu**. Gotowy EXE musi wykazać zarówno prawdziwą generację tekstu, jak i faktyczną klasyfikację semantyczną Qwen.

[**Pełna architektura, ograniczenia i prywatność**](docs/SEMANTIC_ACF_0124.md).

**Granica:** osiem kategorii znaczeniowych to uproszczony, dyskretny sygnał z modelu językowego, a nie gęste embeddingi i nie dowód zwiększenia zdolności Qwen. ACF nie zmienia jeszcze wag językowych ani polityki autonomicznego planowania. Projekt nie jest ukończony.

---

## NeuroGenesis 0.12.3 — ACF: plastyczność neuronalna z rzeczywistym samomodelem

Nie kolejna zakładka: uruchamiamy eksperymentalny **Adaptive Cognitive Fabric (ACF)** wewnątrz głównego NeuroGenesis. Uczy się sam z nowych, rzeczywiście zapisanych doświadczeń SQLite (tylko ośmiokanałowe cechy, bez tekstu prywatnych rozmów), zachowuje stan po zamknięciu aplikacji i może autonomicznie zmieniać połączenia w osobnej sieci LIF. Porównuje wzrost sieci z identyczną kontrolą bez wzrostu, poprzednim bodźcem oraz prostą wartością stałą. Mechanizm samomodelowania wybiera metodę przewidywania na podstawie **faktycznie zmierzonych wcześniejszych błędów**, nie deklaracji o rosnącej inteligencji.

Na głównym ekranie widać mierzone neurony, zmiany synaps, aktualnie wybraną metodę i błąd MSE. Test A → B → A porównuje uczenie, zmianę zadania i retencję umiejętności. **Wynik może wykazać brak przewagi plastyczności** i wtedy właśnie tak będzie raportowany.

[**Architektura, testy, reprodukowalny eksperyment i niewdrożone etapy**](docs/ADAPTIVE_COGNITIVE_FABRIC.md).

**Granica:** to rzeczywisty obliczeniowy układ predykcyjny, ale jeszcze nie semantyczny mózg sterujący Qwen i planowaniem. Nie jest AGI ani systemem niezależnym od danych, sprzętu i energii. Poprawę rzeczywistych zdolności należy dopiero udowodnić na niewidzianych zadaniach. Kod wersji 0.12.3 wymaga przejścia testów przed publicznym wydaniem.

---

## NeuroGenesis 0.12.2 — autonomiczne cele reagują na wyniki badań

Agent celów nie czeka już wyłącznie na zmianę prywatnych plików TXT. Po legalnym i świadomie zatwierdzonym pobraniu źródła HTTPS, jego faktyczne fragmenty i wersja SHA-256 trafiają do tej samej pętli cel → źródło → analiza → raport do oceny. Cel w stanie *waiting* wznawia pracę po pojawieniu się pasujących informacji. Niepasujące strony nie powodują udawanego postępu, a niezmieniona wersja źródła nie uruchamia ciągłego ponawiania pracy.

Operacja korzysta wyłącznie z prywatnego indeksu SQLite, nie wykonuje samodzielnie żadnych dodatkowych żądań sieciowych. W panelu wyświetlane są rzeczywiste odnośniki i SHA-256, a wyniki modelu nadal wymagają oceny. To pamięć i autonomiczna analiza źródeł, a nie dostrajanie wag Qwen.

---

## 0.12.1 — Samodzielne badania + wykorzystanie źródeł przez model

Wersja 0.12.1 jest **rozszerzeniem głównego, autonomicznego interfejsu 0.12**, nie drugim, konkurencyjnym pulpitem. Pierwszy ekran pozostaje jeden: **NeuroGenesis — rozmowa, trwałe cele, postęp autonomii i rzeczywisty connectome**.

- **Przycisk BADAJ ŹRÓDŁA** na ekranie głównym otwiera bezpośrednio specjalizację, bez szukania jej w hierarchii starych kart.
- **Autonomia celu badawczego:** podajesz temat, dobrowolnie aktywujesz zgodę na HTTPS i tryb kontynuacji. System może wykonać maksymalnie trzy ograniczone sesje badawcze w trakcie jednego uruchomienia, z przerwą co najmniej 30 minut; respektuje dotychczasowe robots.txt, limit domen i tempo odczytu. Cofnięcie zgody zatrzymuje badanie.
- **Wspólna inteligencja:** wcześniej zatwierdzone i rzeczywiście zapisane fragmenty stron WWW trafiają przez mechanizm RAG do tego samego lokalnego Qwen3-1.7B co własne TXT. Materiały pozostają niezaufanymi danymi, są oznaczone URL i sumą SHA-256, a odpowiedź nie jest automatycznie weryfikowana jako prawdziwa.
- **Bezpieczne zamykanie:** anulowanie ładowania dużych wag modelu nie zostawia uruchomionego w tle procesu llama.cpp.

Nowa funkcja nie zmienia istniejących wag LLM przez trening gradientowy. Trwały plan celów w modelu 0.12, historia i prywatna SQLite pozostają nienaruszone. Dopiero pełne testy Windows z prawdziwą odpowiedzią wygenerowaną z jednego EXE uprawniają do wydania.

---

## NeuroGenesis 0.12.0 — autonomiczny ekran startowy i aktywny agent celów

**Rozwijane w PR (weryfikacja CI przed wydaniem):** zamiast domyślnie otwierać statystyczny Mission Control, nowy Windows EXE od razu pokazuje **NEUROGENESIS**: lokalną rozmowę Qwen3-1.7B, autonomiczne cele z trwałą kolejką, podgląd rzeczywistej sieci LIF i bieżące stany systemu. Model sam ładuje wbudowane wagi; pytanie napisane podczas uruchamiania zostaje w kolejce i jest automatycznie obsługiwane.

**Nowe niezależne zadania:** wpisz cel raz; system tworzy plan, analizuje dostępne zatwierdzone TXT i samodzielnie ponawia analizę po zmianie wiedzy. Raporty z faktycznymi SHA-256 źródeł wymagają zatwierdzenia — nie są automatycznie uznawane za zweryfikowane. Rejestracja numerycznych cech rozmowy do badawczego mózgu LIF jest widoczna i może być wyłączona; 40 świeżych bodźców umożliwia osobne badawcze próby autoregulacji. Panel nie udaje impulsów, kiedy nie ma nowych zdarzeń.

Zakładki laboratoryjne, stary system rozmowy i specjalizacja nie zostały usunięte — są teraz pod **Zaawansowane**. [Zobacz dokładnie jak działa autonomia i co jest, a czego nie ma](docs/AUTONOMOUS_HOME.md).

**Wersja 0.12 nie jest jeszcze ukończonym AGI ani autonomicznym trenerem 1,7 mld parametrów.** Główny model nadal jest wstępnie wytrenowanym Qwen; autonomiczne zadania wykonują kontrolowane planowanie i analizę zatwierdzonych źródeł lokalnych. Publikację nowej wersji uzależniamy od testów, rzeczywistej kompilacji Windows i wygenerowania odpowiedzi wewnątrz finalnego EXE.

---

# NeuroGenesis 0.11.0 — COMPLETE OFFLINE AI / Windows

**Miron przy pomocy AI.**

**Najważniejsza zmiana: jedno kompletne EXE z rzeczywistym modelem językowym i silnikiem obliczeniowym.** Wcześniejszy plik 13 MB był tylko interfejsem; jego Model Chat wymagał osobnego Pythona i ręcznie pobieranych wag. To zostało naprawione w nowym profilu FULL.

[**Pobierz najnowszy zweryfikowany NeuroGenesis.exe**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [Suma SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) · [Wszystkie wydania](https://github.com/promirmir/NeuroGenesis/releases)

### Jak to działa

- **Model Chat** automatycznie uruchamia model **Qwen3-1.7B**, Q4_K_M, działający lokalnie przez **llama.cpp CPU** — pełne wagi i DLL są spakowane do tego samego EXE. Nie wymaga Python, PyTorch ani pobrania dodatkowego modelu. Historia tylko w pamięci sesji. Silnik między turami pozostaje załadowany.
- **Trening TXT** działa bez zewnętrznych bibliotek: importuje wskazany plik UTF-8, indeksuje go i pozwala modelowi przywołać właściwy fragment w odpowiedzi. **To pamięć z retrieval/RAG, nie gradientowy trening parametrów sieci.**
- **Aktywny samorozwój wiedzy**: po włączeniu obserwuje jeden zatwierdzony folder z plikami TXT, sam wczytuje nowe/zmienione pliki i aktualizuje bazę podczas działania aplikacji. Bez potajemnego treningu na przypadkowych stronach.
- Stare **Mission Control**, sieć impulsowa LIF i prywatna SQLite pozostają dostępne. Nie kasujemy starej pamięci.
- **Kryterium release:** Windows Actions musi pobrać zweryfikowane wagami SHA-256 GGUF i oficjalny silnik, zbudować duży ONEFILE EXE, a następnie uzyskać **rzeczywistą odpowiedź Qwen uruchomioną z tego właśnie EXE**. Bez tego nie publikujemy nowej wersji.

**Wielkość:** gotowy EXE ma zawierać ponad 1 GB skwantyzowanych wag, a nie być „13 MB cudownym AI”. Przy pierwszym uruchomieniu PyInstaller rozpakowuje zasoby do tymczasowego katalogu. Kompletność w tej wersji oznacza **działającą lokalną rozmowę i pozyskiwanie wiedzy z TXT**. Opcjonalne badawcze eksperymenty LoRA/PyTorch nadal wymagają osobnych bibliotek; nie nazywamy ich częścią kompletnego offline treningu wag.

[**Dokładny kontrakt możliwości, pochodzenie wag, SHA-256, licencje, ograniczenia i testy**](docs/FULL_OFFLINE_EXE.md).

---

## NeuroGenesis 0.10 — Trening TXT + prawdziwa rozmowa z lokalnym modelem

**Nowe funkcje w kodzie Windows EXE (przed publikacją wydania):**

- **Trening TXT**: odczyt lokalnych plików UTF-8 i dwa rzeczywiste tryby uczenia: mały badawczy Foundation GRU (zwykły tekst) oraz LoRA/PEFT (uporządkowane pary `USER:/ASSISTANT:`) dla lokalnego modelu instrukcyjnego. Zapisywanie **nowych** wag-kandydatów, ewaluacja oddzielnych przykładów i STOP.
- **Model Chat**: lokalna rozmowa z rzeczywistym modelem `Qwen/Qwen3-0.6B` (Apache-2.0), po świadomym pobraniu ~1,5 GB wag i przygotowaniu środowiska Python+Torch/Transformers. Opcjonalnie ręcznie wybrany adapter LoRA. **Brak zdalnego API podczas rozmowy.**
- **Pobieranie danych**: po zgodzie można pobrać do nowego TXT ograniczony zbiór anglojęzycznych dialogów UltraChat 200k (deklaracja licencji MIT w karcie) do weryfikacji praw i dalszego treningu. Przygotowany jest również [autorski polski plik przykładów](training/starter_dialogues_pl.txt).
- **Autonauka w granicach praw i zasobów**: opcjonalne monitorowanie wskazanego lokalnego TXT; zmiana danych może uruchomić trening nowego kandydata LoRA. **Bez automatycznej podmiany używanego modelu, bez ukrytego crawlowania i bez działania po zamknięciu aplikacji.**

[**Pełna instrukcja instalacji, danych, treningu i uruchamiania offline**](docs/TRAINING_AND_LOCAL_CHAT.md).

**Granica:** mała sieć GRU nie staje się kompetentnym chatbotem po wczytaniu TXT. Realny dialog korzysta z wcześniej wytrenowanego modelu zewnętrznego, działającego lokalnie. Pełna, niezależna samodzielność rozwojowa bez danych i zasobów nie jest możliwa do zapewnienia; nie deklarujemy AGI ani ukończonej kompetencji. **Kod 0.10 czeka na testy i publiczne EXE; najnowsze opublikowane wydanie może nadal być wcześniejsze.**

## NeuroGenesis 0.9.0 — awatar i działające laboratorium Foundation

**W kodzie programu:** [EMBODIED FOUNDATION](docs/EMBODIED_FOUNDATION.md).
Domyślne Windows `NeuroGenesis.exe` zawiera teraz trzy przełączane widoki:
obracający się hologram LIF, dokładną mapę synaps 2D oraz cybernetyczną
postać (AWATAR). Jej efekty związane z aktywnością zależą tylko od
faktycznych kroków i impulsów zapisywanych w SQLite; ruch kamery ma
charakter wizualny.

Dodatkowa zakładka **Foundation Lab** potrafi wywołać rzeczywistą predykcję
istniejącego modelu GRU z zaufanego lokalnego checkpointu. Użytkownik
wybiera osobne środowisko Python z PyTorch — mały plik EXE go nie zawiera.
Wynik to niezweryfikowana kontynuacja bajtowa, nie czat AI, a checkpoint
musi być uprzednio wytrenowany. Nie ma automatycznych pobrań, treningu,
samozmiany ani nadpisywania pamięci. [Wymagania i instrukcja](docs/EMBODIED_FOUNDATION.md).

**Status udostępniania:** kod 0.9.0 trafia przez testy CI. Oficjalne EXE
0.9.0 wskazuje dopiero nowe zweryfikowane wydanie pod
[releases/latest](https://github.com/promirmir/NeuroGenesis/releases/latest),
nie należy mylić starszego EXE 0.8.0 z nowymi funkcjami.

## Poprzednie zweryfikowane wydanie Windows 0.8.0 (archiwalne)

**NeuroGenesis 0.8.0 — rzeczywisty, nowy ekran startowy w samodzielnym EXE.** [Pobierz zweryfikowane wydanie](https://github.com/promirmir/NeuroGenesis/releases/tag/v0.8.0-main.8e27f420). SHA-256 pliku EXE: `5e48e1c7ecde3b7a066a39c2b71c8a70764351888ff30dc23ba75b53c6fcb44e`. Windows GUI otwiera teraz `CENTRUM` z prawdziwym grafem LIF i metrykami zamiast starej pustej rozmowy. Źródło i testy: PR #50; pełna macierz Windows/Python/Torch/Qt/ochrona prywatności zielona. Technologia **publicznego EXE: Tkinter**; rozbudowane Qt pozostaje opcjonalnym programem uruchamianym ze źródeł i wymaga osobnej licencyjnej bramki wydania. Brak AGI i samodzielnego semantycznego modelu języka.

# NeuroGenesis — Mission Control

**research prototype v0.13.2.**  
**Publiczne autorstwo: Miron przy pomocy AI.**

NeuroGenesis to lokalny projekt badawczy AI: rzeczywista mała sieć neuronowa LIF ze strukturalną plastycznością, prywatna trwała baza SQLite, kontrolowane zdobywanie informacji ze źródeł HTTPS, ekstrakcyjne cytowanie oraz odrębny eksperymentalny model Foundation Brain trenowany w PyTorch. **System nie jest AGI, świadomością, modelem ludzkiego mózgu ani niezależnie zweryfikowanym systemem rozumienia języka naturalnego.**

## Windows x64 — aktualna aplikacja bez Pythona

[**Pobierz aktualny NeuroGenesis.exe**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [Suma SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) · [Wszystkie wydania](https://github.com/promirmir/NeuroGenesis/releases)

**Od v0.8.0 domyślnie wyświetlany jest faktyczny MISSION CONTROL.** Nie jest to stary pusty ekran rozmowy ze zdjęcia zgłoszonego przez użytkownika. Uruchamiany od razu dashboard w samodzielnym, spakowanym Windows EXE ma ciemny, futurystyczny układ z:

- centralną interaktywną mapą **faktycznie zapisanej w SQLite sieci LIF** (neurony, rzeczywiste synapsy, wagi, impulsy);
- czterema rzeczywistymi kaflami: kroki LIF, neurony, synapsy i dokumenty;
- mierzoną historią ostatniej maski spike *tylko po nowym zapisanym kroku* i dziennikiem faktycznie zaobserwowanych zmian;
- stanami modułów: uprawnienia HTTPS, lokalna wiedza, stan LIF i oddzielny Foundation Brain;
- przyciskami przejścia do zachowanych modułów Rozmowa, Internet, Mózg, Specjalizacja i Kopia pamięci.

Przy braku nowych kroków graf nie udaje pracy neuronów. Przewijanie myszą przybliża wykres. Wartości nie są umownymi procentami inteligencji. Sam fakt odrysowania połączeń nie jest dowodem powstania jakościowo nowej AI.

**Silnik interfejsu publicznego EXE nadal korzysta z systemowego Tkintera**, dzięki czemu program działa bez instalowania biblioteki Qt i nie rozpowszechnia Qt DLL. Wygląd oraz domyślny ekran zostały jednak rzeczywiście przebudowane. Nie myl tego wydania z bardziej rozbudowanym, opcjonalnym interfejsem PySide6.

### Pamięć i bezpieczeństwo

Prywatna baza Windows standardowo znajduje się pod `%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3` i nie jest usuwana podczas aktualizacji aplikacji. Kopie tworzy się ręcznie w zakładce **Kopia pamięci**, za pomocą spójnego transakcyjnego backupu SQLite i weryfikacji SHA-256. Przywracanie wyłącznie do **nowego pliku**. Backup nie jest szyfrowany; trzymaj go w prywatnym miejscu. [Procedura](docs/MEMORY_RECOVERY.md).

Sieć pozostaje wyłączona na starcie. Pozyskiwanie informacji z publicznych stron wymaga jawnej zgody użytkownika i jest ograniczone. Strony są traktowane jako niezaufane dane, a publiczne udostępnienie nie jest zgodą na trening modelu.

## Rozbudowane NeuroGenesis Command Center — opcjonalne Qt

Repozytorium zawiera też drugi, działający interfejs napisany w **PySide6 / Qt**, z bardziej rozbudowaną nawigacją, przestrzenną panoramą sieci LIF, podglądem konkretnego neuronu, wykresem rzeczywistych strat treningu i panelami badania, pamięci, rozmowy oraz diagnostyki.

Aby uruchomić go na Windows **ze źródeł**, pobierz całe repozytorium, zainstaluj Python 3.12 x64 i użyj `Launch-NeuroGenesis-Mission-Control.cmd`. Skrypt tworzy lokalne środowisko oraz pyta o zgodę przed pierwszym pobraniem PySide6. **To nie jest plik EXE Qt.** Spakowany techniczny Qt na Windows przechodzi testy, ale nie jest publicznie rozpowszechniany, dopóki nie zostaną zweryfikowane wszystkie obowiązki licencyjne LGPLv3. [Dokumentacja Qt](docs/MISSION_CONTROL.md).

## Co faktycznie działa, a czego jeszcze nie dowiedziono

| Moduł | Potwierdzone funkcje i ograniczenia |
|---|---|
| Neurony LIF | Rzeczywiste kroki, impulsy, wagi, tworzenie neuronów i usuwanie połączeń; **to mała sieć eksperymentalna** |
| Rozmowa | Jawnie nauczone odpowiedzi, dosłowne fragmenty i URL, zachowanie kontekstu w Qt w bieżącej sesji; **bez potwierdzonego rozumowania semantycznego** |
| Internet | Kontrolowane, limitowane źródła i prywatna wersjonowana wiedza; nie oznacza automatycznego trenowania |
| Foundation Brain | Osobny prawdziwy eksperyment PyTorch (predykcja bajtów), checkpointy, CPU i opcjonalne CUDA; **nie jest jeszcze silnikiem rozmowy** |
| Wykresy | Dane zapisane w lokalnym mózgu / prawdziwe zdarzenia treningowe, nigdy sztuczne pomiary świadomości |
| Jakość | Testy Python 3.11–3.13, Windows frozen EXE, prywatności, QA i opcjonalnego Qt; niezależna rzeczywista QA i fizyczny GPU pozostają niezweryfikowane |

W szczególności system może błędnie cytować dokument przy pytaniu z fałszywą przesłanką. Syntetyczne testy BM25 również wykazały tę klasę błędu. Nie utożsamiaj cytowania z prawdziwością i nie przyjmuj, że zwiększająca się liczba neuronów lub pobranych dokumentów dowodzi wzrostu inteligencji.

## Dokumentacja, rozwój i odpowiedzialne wydania

- [Stan projektu i aktualne ograniczenia](docs/PROJECT_STATE.md)
- [Dziennik zmian](docs/DEVELOPMENT_LOG.md)
- [Architektura i wymogi Mission Control](docs/MISSION_CONTROL.md)
- [Foundation Brain](docs/FOUNDATION_BRAIN.md)
- [QA i metody odniesienia](docs/QA_ACCEPTANCE.md)
- [Bezpieczeństwo](docs/SECURITY.md)
- [Testy CI](https://github.com/promirmir/NeuroGenesis/actions)

Wydanie Windows jest publikowane tylko z dokładnie zweryfikowanego commita `main` i zawiera plik kontrolny SHA-256. **v0.8.0 jest etapem doprowadzania istniejącej aplikacji do wyższej jakości użytkowej, a nie deklaracją osiągnięcia AGI ani ukończenia wszystkich celów badawczych.**


### Eksperyment pomiarowy 0.12.6 — Qwen kontra Qwen + pamięć TXT

Wprowadzono niezależny audyt A/B prawdziwego lokalnego Qwen (ten sam model, próba bez źródeł i z zatwierdzoną wiedzą TXT). Mierzy dosłowne trafienia odpowiedzi, odnalezione źródła, fałszywe cytowania, wyniki sparowane i koszty czasowe; nie używa sieci, nie trenuje modelu i nie publikuje prywatnych pytań. **Nie dowodzi jeszcze przewagi ACF ani AGI.** Instrukcja: [DIALOGUE_PAIRED_EVALUATION_0126.md](docs/DIALOGUE_PAIRED_EVALUATION_0126.md). Domyślne rozmowy, prywatne SQLite i pobierane EXE zachowują dotychczasowe działanie.
