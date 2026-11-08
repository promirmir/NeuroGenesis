# NeuroGenesis 0.10 — local model training and conversational AI

**Publiczny podpis: Miron przy pomocy AI.**

## Co faktycznie działa w domyślnym Windows EXE

- **Trening TXT** — pliki UTF-8 o rozmiarze 1 KiB–32 MiB,
  sterowanie krokami i wybór CPU/CUDA, nowy checkpoint/kandydat,
  przyciski STOP, pobierania modelu i zewnętrznego zbioru.
- **Model Chat** — realna wieloturowa rozmowa z lokalnie działającym
  *wstępnie wytrenowanym* modelem **Qwen3-0.6B**, opcjonalnie z wybranym
  osobno adapterem LoRA. Komunikacja jest przesyłana przez stdin do
  zewnętrznego procesu lokalnego Pythona, bez API w chmurze i bez
  zapisywania treści do starej bazy SQLite.
- **Foundation Lab** i zwykła **Rozmowa** pozostają odrębne.
  Historyczny GRU bazuje na predykcji bajtów i **nie staje się**
  porównywalnym chatbotem przez samo zwiększenie pliku TXT.
- **AUTO-KANDYDACI** — świadomie włączony monitoring jednego lokalnego,
  wybranego i zatwierdzonego pliku TXT. Jeżeli zmieni się jego SHA-256,
  uruchomiony program może zainicjować nowy trening LoRA.
  Wynik jest wyłącznie kandydatem i **nie zastępuje wag
  używanych w rozmowie**. Bez świeżych danych trening nie dzieje
  się sam. Po zamknięciu aplikacji żadne zadanie nie jest uruchamiane.
- Działa też istniejący, odrębny `AutonomicSupervisor` dla cech
  impulsowej sieci LIF. Nie jest to uczenie umiejętności dialogowych
  ani samodzielne programowanie.

**Żaden z tych mechanizmów nie dowodzi niezależnej ogólnej inteligencji,
ludzkiej świadomości czy nieskończonego samorozwoju.** Program nie
potrafi z gwarancją stale poprawiać się bez danych, procesora/GPU,
walidacji i zachowania stabilnych uprawnień.

## Przygotowanie środowiska — jednorazowo

Pakiet EXE nadal jest niewielki i nie zawiera ~1,5 GB wag modelu,
PyTorch, Transformers ani materiałów stron trzecich. W katalogu
pełnego repozytorium, w prywatnym Pythonie 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dialogue]"
```

To jawna instalacja bibliotek; wymaga dostępu do internetu i
przestrzeni na dysku. CUDA wymaga zgodnego sprzętu, sterowników
i odpowiedniego zestawu PyTorch; nie jest gwarantowana samym
zaznaczeniem GPU w GUI.

W programie **Trening TXT** podaj lokalizację
`.venv\Scripts\python.exe`. W **Model Chat** również wskaż
ten interpreter oraz katalog z już pobranymi wagami modelu.

## Pobranie modelu konwersacyjnego

Model z oficjalnej strony:
[Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B).
Karta modelu deklaruje licencję **Apache-2.0**. Aplikacja pobiera
pliki z przypiętego commita
`c1899de289a04d12100db370d81485cdf75e47ca`,
wyłącznie po świadomym kliknięciu **POBIERZ QWEN 0.6B**
i potwierdzeniu zgody.

Odpowiednik w konsoli:
```powershell
.\.venv\Scripts\python.exe -m neurogenesis.local_dialogue --download-model --model-dir ".\NeuroGenesis-Qwen3-0.6B" --confirm-download-license
```

Wykonywanie `Model Chat` korzysta wyłącznie z lokalnych plików
`.safetensors` i `local_files_only=True`; nie wykonuje
`trust_remote_code=True` i nie wysyła rozmowy na serwer.
Po pobraniu modelu i instalacji zależności rozmowa może działać
bez internetu. **Model bazowy nie został wytrenowany przez NeuroGenesis.**

## Własny TXT i dwa rozdzielne tryby uczenia

### Foundation TXT / GRU

Zwykły tekst UTF-8, np. dokument lub korpus. `Trening TXT`
uruchamia istniejący backend `foundation_train`, który
optymalizuje małą sieć GRU do prognozowania kolejnego bajtu.
Walidacja to oddzielny, późniejszy fragment tego samego tekstu;
jej wynik NIE jest niezależnym testem zdolności konwersacyjnych.

### Dialog TXT / LoRA

Wybierz pobrany model lokalny i tekst w formacie **jedna linia na
rolę**, na przykład:

```text
USER: Czym jest sieć neuronowa?
ASSISTANT: To model obliczeniowy złożony z połączonych jednostek.

USER: Jak sprawdzisz swoją odpowiedź?
ASSISTANT: Porównam ją z wiarygodnymi źródłami lub pomiarem.
```

Wspierane są także polskie nagłówki `UŻYTKOWNIK:` i
`ASYSTENT:`. Minimum **20 niepowtarzających się par**;
odpowiedź musi wystąpić po każdym pytaniu. Trening dzieli
pary deterministycznie (ziarno) na dane treningowe i odłożone,
bez użycia odłożonych odpowiedzi do gradientu.
Używa szablonu rozmowy tokenizera, `PEFT/LoRA` z
`target_modules=[q_proj, v_proj]`, stratą tylko na odpowiedzi
asystenta (`labels=-100` w tokenach pytania), `AdamW`,
ograniczoną liczbą kroków i `clip_grad_norm_`.
Zapisuje nowy katalog adaptera `*.safetensors` i raport
zmiany straty holdout. **Nie aktywuje adaptera automatycznie**.
Lepsza strata bajtów/tokenów nie dowodzi lepszej wiedzy,
bezpieczeństwa ani odporności na zapominanie.

Do sprawdzenia formatu dostępny jest mały autorski plik
[`training/starter_dialogues_pl.txt`](../training/starter_dialogues_pl.txt)
z 51 wymyślonymi na potrzeby tego projektu parami. Nie jest
to profesjonalny korpus ani źródło pewnego rozumowania.

## Większy zbiór rozmów: tylko za zgodą

Przycisk **POBIERZ ULTRACHAT → TXT** korzysta ze
źródła [HuggingFaceH4/ultrachat_200k](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k),
w trybie `streaming=True` i tylko z `train_sft`. Karta
deklaruje **MIT**, jednak materiał ma określone pochodzenie,
ograniczenia i dane syntetyczne: użytkownik musi przejrzeć
kartę źródła i warunki zastosowania przed potwierdzeniem
zgody. Nie należy zakładać, że deklaracja karty wyczerpuje
wszystkie prawa do danych źródłowych.

Import wymaga kliknięcia, nie wykonuje kodu datasetu,
zapisuje najwyżej 1500 rekordów / 32 MiB do **nowego**
pliku TXT, zachowuje kolejność ról i zwraca hash SHA-256.
Samo pobranie nie oznacza zgody na trening: checkbox
praw do wybranego TXT jest oddzielny. UltraChat jest
**anglojęzyczny**, więc nie rozwiąże automatycznie
problemu jakości konwersacji po polsku.

## Bezpieczeństwo, regresje, prawdziwa jakość

- Dane nie są używane do treningu bez ręcznego potwierdzenia
  posiadania odpowiednich praw; pliki wynikowe nie nadpisują
  istniejących wag/modeli. Nie przetrenowujemy modelu bez końca
  na przypadkowych stronach z internetu.
- Niezależny lokalny model odpowiada z prawdziwych wag,
  ale może halucynować. To **nie** automatycznie zweryfikowana
  odpowiedź z URL i nie zastępuje dotychczasowej ekstrakcji.
- Do jakości produkcyjnej konieczne są: ocena odpowiedzi na
  niewidzianych zadaniach, zewnętrzne testy po polsku,
  analiza prywatności, pomiar powtarzalności, zabezpieczenia
  przed zatruciem danych oraz osobna weryfikacja LoRA na
  kompatybilnej maszynie. CI bada zasady, ścieżkę GUI
  i brak niejawnych pobrań; **nie pobiera 1,5 GB modelu
  ani nie dowodzi jakości odpowiedzi na GPU użytkownika**.

Podstawa techniczna: [Hugging Face TRL SFT Trainer](https://huggingface.co/docs/trl/sft_trainer)
opisuje standardowy format rozmów i maskowanie straty
tylko na odpowiedziach. Kod projektu używa własnej jawnej
pętli PyTorch + PEFT zamiast ukrytej magii, z analogicznym
podziałem na kontekst i odpowiedź.
