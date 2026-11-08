# NeuroGenesis 0.11.0 — FULL offline Windows EXE

**Publiczne autorstwo:** Miron przy pomocy AI.

## Weryfikowalny kontrakt dystrybucji

Nowe publiczne **NeuroGenesis.exe** zawiera wszystkie komponenty
potrzebne do podstawowego działania: GUI, lokalną neuronową
pamięć LIF/SQLite, natywny proces inference llama.cpp oraz
prawdziwe skwantyzowane wagi **Qwen3-1.7B Q4_K_M GGUF**. Do
uruchomienia funkcjonalnego czatu i aktualizowania lokalnej wiedzy
z TXT nie trzeba instalować Pythona, PyTorch, Node, C++, pobierać
dodatkowego modelu ani używać usługi internetowej.

**Ważne:** plik EXE jest teraz duży (około **1,1 GB lub więcej**)
zamiast 13 MB. PyInstaller --onefile rozpakowuje przy uruchomieniu
biblioteki i wagi do tymczasowego prywatnego katalogu: jest to
technicznie jedna paczka do pobrania, a nie jeden nierozpakowywany
plik podczas pracy. Potrzebne są wolna przestrzeń dyskowa i RAM.

## Model / rzeczywiste źródła

**Pretrained model:** Qwen3-1.7B; właściciel wag bazowych
[Qwen](https://huggingface.co/Qwen/Qwen3-1.7B), licencja
**Apache License 2.0**, autor Qwen Team. NeuroGenesis **nie
wytrenował** tych 1,7 miliarda parametrów.

**GGUF quantization** (precyzja Q4_K_M) przez Unsloth:
https://huggingface.co/unsloth/Qwen3-1.7B-GGUF
plik **Qwen3-1.7B-Q4_K_M.gguf** ze stałego snapshotu:

- Commit zbioru wag: \`cc27747d7419139e44ba97777c2f2fd5dca92ee1\`.
- SHA-256 GGUF: \`ba491cf470c3cadc624e4c8d6c9a27c998809e8ba8eb938d1689ae87e024b6b7\`.
- URL wersji: https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/blob/cc27747d7419139e44ba97777c2f2fd5dca92ee1/Qwen3-1.7B-Q4_K_M.gguf

**Engine:** [llama.cpp](https://github.com/ggml-org/llama.cpp),
licencja **MIT**, CPU Windows x64, release \`b12211\`:

- Pobrany plik: \`llama-b12211-bin-win-cpu-x64.zip\`.
- SHA-256 ZIP: \`23729000408c6968faf5e322afc99319d3b8c576ba872ef7663d9b89810090f3\`.
- URL: https://github.com/ggml-org/llama.cpp/releases/tag/b12211

Respektuj wymagania Apache-2.0 i MIT, szczególnie przy redystrybucji.
Dostawca/wydawca powinien dołączyć aktualne teksty obu licencji
oraz noty atrybucji. Dla Qwen należy zachować również NOTICES,
jeżeli znajdują się w opublikowanym modelu. Pełne teksty można
uzyskać z odnośników powyżej; to podsumowanie nie zastępuje licencji.

## Co robi nowy program

1. Uruchamiasz **NeuroGenesis.exe** bez instalowania zależności.
2. W zakładce **Model Chat** wagi są automatycznie weryfikowane
   za pomocą SHA-256, a silnik jest ładowany do pamięci. Pierwszy
   start może trwać dłużej, ponieważ rozpakowuje ~1,1 GB plików.
3. Wpisujesz wiadomość: prawdziwy model generuje odpowiedź offline.
   Wagi pozostają w pamięci procesu pomiędzy turami.
4. W zakładce **Trening TXT** wskazujesz swój plik UTF-8 (do 16 MiB).
   Program, po zatwierdzeniu, dzieli plik na fragmenty, indeksuje
   lokalnie za pomocą SQLite FTS5, zapisuje SHA-256 i źródło.
5. Pytając potem Model Chat, system wyszukuje pasujące fragmenty
   ze swojej prywatnej bazy i dołącza je jako kontekst (RAG).
6. Po zgodzie możesz wskazać folder z własnymi TXT i włączyć
   **aktywny samorozwój wiedzy**: okresowe skanowanie zmian i
   automatyczne zapisywanie nowych wersji tekstów podczas działania
   programu. Żadne dokumenty nie trafiają do zewnętrznego serwera.

Historia dialogu w Model Chat żyje tylko w pamięci bieżącej
sesji; źródła TXT są zapisane odrębnie w
\`%LOCALAPPDATA%\NeuroGenesis\knowledge_local.sqlite3\`.
Istniejący mózg LIF pozostaje w
\`%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3\` i nie
jest resetowany przez aktualizację.

Wbudowany silnik nasłuchuje tylko na losowym porcie
\`127.0.0.1\`, z losowym kluczem dostępu i wyłączonym interfejsem
HTTP; żadne pytanie nie jest wysyłane na zewnętrzne API. To
**komunikacja lokalna między procesami**, nie żądanie do Internetu.

## Co dokładnie NIE jest jeszcze rozwiązane

- **RAG/indeksowanie TXT nie jest dostrajaniem wag modelu.**
  Funkcja automatycznie powiększa zasób wiedzy, ale nie modyfikuje
  1,7B parametrów sieci językowej.
- Starsze \`foundation_train\`, \`lora_train\` i **Foundation Lab**
  to odrębne opcjonalne badania treningu numerycznego, które mogą
  wymagać PyTorch i bibliotek Python. To **nie jest** konieczne
  do podstawowej rozmowy i lokalnej nauki wiedzy z TXT.
- Nie osiągnięto AGI, świadomości, biologicznego samorozwoju,
  wszechobecnego skanowania całego Internetu ani zdolności
  samodzielnego zdobywania mocy obliczeniowej.
- Wersja zawiera CPU backend (uniwersalny Windows x64). Nie
  deklarujemy akceleracji RTX 4050, dopóki jej nie przetestujemy.
- Lokalny model 1.7B może błędnie odpowiadać. Zwiększanie
  liczby dokumentów nie dowodzi mądrości ani nie zastępuje
  testów merytorycznych.

## Warunek konieczny publikacji

Workflow \`.github/workflows/windows-complete.yml\`
**musi**:

- pobrać obie konkretne wersje modelu i silnika oraz potwierdzić
  ich publicznie podane SHA-256;
- przetestować rzeczywistą generację odpowiedzi z wag GGUF;
- zbudować ONEFILE EXE zawierający całe GGUF;
- uruchomić skompilowany EXE w izolowanym teście GUI i SQLite;
- ponownie uruchomić **skompilowany EXE i faktycznie wygenerować
  z niego odpowiedź**, zanim pozwolimy na publikację;
- dołączyć wynikowy checksum EXE oraz niniejszy plik pochodzenia.

Wszystkie te etapy są blokujące. Wynik w zielonym workflow jest
dowodem wykonania ścieżki technicznej, nie niezależnym benchmarkiem
jakości wieloturowej rozmowy po polsku. Publikacja
\`publish-release.yml\` jest uruchamiana **wyłącznie** po sukcesie
workflow **Windows Complete Offline AI EXE** na aktualnym
commicie głównej gałęzi.
