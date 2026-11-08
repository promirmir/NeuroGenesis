# NeuroGenesis 0.12.4 — Semantyczny ACF / Qwen → plastyczna sieć

**Autor:** Miron przy pomocy AI.

## Co naprawdę zostało zintegrowane

Wersja 0.12.3 uczyła się na ośmiu liczbowych cechach sensora haszującego tekst. Chociaż plastyczność była realna, same bodźce nie kodowały świadomie znaczenia zdań.

Wersja 0.12.4 dodaje drugi, **oddzielny** tor reprezentacji:

1. Użytkownik wysyła wiadomość w istniejącym głównym panelu NeuroGenesis; włączony jest przełącznik „Uczenie LIF + semantyczne ACF (bez treści rozmów)”.
2. Uruchomiony lokalnie model **Qwen3-1.7B-Q4_K_M**, dostarczony w tym samym EXE, faktycznie klasyfikuje znaczenie wypowiedzi przez uwierzytelniony `127.0.0.1`. Nie jest to API w chmurze ani algorytm haszujący. Klasyfikacja jest drugim rzeczywistym wnioskowaniem po odpowiedzi czatu i działa w osobnym wątku.
3. Model ma zwrócić **dokładnie** osiem binarnych kategorii: `facts`, `science`, `mathematics`, `programming`, `engineering`, `planning`, `creativity`, `dialogue`. To dyskretne **znaczniki semantyczne nadane przez model**, nie gęsty embedding i nie dowód prawdziwego rozumienia tekstu. Kategorie mogą współwystępować.
4. Nieprawidłowy JSON, brak wymaganych kategorii, niepoprawna wartość lub awaria lokalnego modelu powodują **brak treningu**. Nie ma losowych wektorów ani niejawnego przełączenia na hasze.
5. Wyłącznie ośmiokanałowy wektor trafia do oddzielnej prywatnej bazy `semantic_fabric.sqlite3` (czas i wersja taggera, bez surowej treści, hashy czy historii rozmowy). Kategorie same w sobie mogą ujawniać ogólną tematykę — pliki należy chronić tak samo jak pozostałą lokalną pamięć.
6. `FabricMemoryObserver` przetwarza tylko nowe zdarzenia, uczy odrębnych sieci LIF z plastycznością i bez rozwoju strukturalnego oraz prostych punktów odniesienia. Wzrost i spadek zdolności predykcyjnych są oceniane przed aktualizacją parametrów (prequential MSE).
7. Cały substrat, historia błędów i wskaźnik ostatniego przetworzonego zdarzenia są atomowo zapisywane w `semantic_fabric.acf.json` obok nowej bazy. Restart nie wymaga ponownego przekazywania wiadomości. W przypadku awarii po zapisie zdarzenia, a przed zapisem stanu sieci, odtworzenie jest bezpieczne.
8. Główny pulpit pokazuje liczbę rzeczywistych wektorów, aktualnie wybrany sposób prognozowania, zmierzony MSE i rozmiar sieci, oddzielnie od starego ACF na haszach.

## Zależności i weryfikacja

Nie dodano wymagania osobnego Pythona, PyTorch, modelu czy zewnętrznego API dla standardowego Windows EXE. Wykorzystujemy już dostarczony model GGUF i natywny llama.cpp. Testy Python sprawdzają kontrakt, prywatność i odtwarzanie po restarcie. **Mandatory full Windows EXE gate** wykonuje teraz nie tylko realną odpowiedź tekstową, lecz również prawdziwą klasyfikację semantyczną z finalnego EXE. Niepoprawna klasyfikacja blokuje publikację.

## Ograniczenia i dalszy eksperyment

- To **pierwsza sensowna integracja modelu językowego z uczącą się siecią ACF**, ale jeszcze nie udowodniona przewaga nad modelem bez tej sieci.
- Model Qwen jest dostawcą znaczenia. ACF nadal nie poprawia automatycznie jego wag ani jakości odpowiedzi. Musimy dopiero wykazać korzyść na niezależnych, niewidzianych zadaniach, np. planowaniu i wyborze sposobu zdobywania wiedzy.
- Binarny wektor kategorii jest znacząco uboższy od rzeczywistych embeddingów; nie należy go z nimi utożsamiać. To pomost badawczy do kolejnego etapu, nie ostateczna architektura sztucznego mózgu.
- Dane źródłowe są wysyłane jedynie do własnego, lokalnego procesu Qwen. Klasyfikator może popełniać błędy i może być podatny na próby manipulacji w tekście użytkownika; dlatego nie nadaje żadnych dodatkowych uprawnień ani nie podejmuje nieodwracalnych działań.
- Nie osiągnięto samodzielnego treningu wag LLM, AGI, świadomości ani najbardziej zaawansowanego modelu świata.
