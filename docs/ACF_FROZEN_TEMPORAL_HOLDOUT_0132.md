# NeuroGenesis 0.13.2 — uczciwy test trwałego uczenia ACF na zdarzeniach przyszłych

**Autor publiczny:** Miron przy pomocy AI.

## Cel badawczy

Zmierzona liczba neuronów nie mówi, czy sieć jest bardziej inteligentna. Istniejący eksperyment A→B→A mierzył błąd przy kolejnym uczeniu, przez co wynik mógł zawierać korzyść z dopasowania już w trakcie testu. Moduł `neurogenesis.acf_temporal_holdout` dodaje **chronologiczny test z całkowicie zamrożonym uczeniem** na autentycznych, wcześniej zapisanych binarnych klasyfikacjach semantycznych z lokalnego Qwen.

To narzędzie badawcze, nie nowa funkcja samodzielnie podnosząca kompetencje Qwen i nie nowy przycisk w panelu. Nie modyfikuje nic w już zapisanych modelach i nie uruchamia Internetu.

## Ściśle określona procedura

1. Odczytaj istniejący, prywatny `semantic_fabric.sqlite3` w trybie `mode=ro`, `query_only=ON`; wymagane **96–2000 kolejnych zdarzeń** i ich zgodność z wersją taggera Qwen. Nie wolno obcinać historii poza z góry ustalonymi granicami.
2. Pierwsze 70% zdarzeń przeznacz tylko do uczenia. Ostatnie 30% to następujący w czasie, niewidziany test. Porządek nie jest mieszany. Minimalnie 64 zdarzenia uczące i 28 testowych.
3. Przeprowadź **pięć wcześniej zdefiniowanych inicjalizacji: 3, 7, 11, 19, 23**, każdą od niezależnego startu parametrów. Dwa warianty sieci na każdym nasieniu mają ten sam początkowy rozmiar, pierwotną topologię, nasiono, obserwacje i współczynnik uczenia. Jeden może rozrastać połączenia i neurony, drugi ma na stałe wyłączony wzrost.
4. Na części testowej **nie aktualizuj wag warstwy odczytu, synaps, ich wieku, topologii ani pamięci wzorców**. Zachowaj jedynie rzeczywistą elektryczną dynamikę LIF (potencjały, impulsy i ślady). Każdy błąd MSE licz na prognozie przygotowanej **przed** bieżącym celem.
5. Zestaw pięć nasion oraz dwie kolejne połowy okresu testowego; oprócz sieci rosnącej i nierosnącej uwzględnij przewidywanie identyczne z poprzednim zdarzeniem oraz stałe 0,5. Podawaj faktyczną liczbę neuronów i synaps (większa rosnąca sieć zużywa więcej zasobów).
6. Z góry ustalony opisowy warunek wyniku dodatniego wymaga rzeczywistego wzrostu, **co najmniej 0,002 MSE poprawy nad obiema kontrolami: stałą strukturą i ostatnim zdarzeniem we wszystkich pięciu nasionach**, oraz poprawy względem tych dwóch metod w obu połowach testu. Niespełnienie któregokolwiek warunku oznacza wynik ujemny lub niewystarczający; nie wolno ukrywać przypadków.

**Uwaga metodologiczna:** jedno pierwsze zdarzenie może wywołać strukturalny wzrost nawet dla strumienia stałych zer. Test negatywny właśnie tego pilnuje: trwały wzrost **nie oznacza** przewagi, bo przewidywanie ostatniego zera daje MSE równe zero.

## Przykładowe polecenie

Uruchomić z checkoutu źródłowego (wraz z lokalną bazą, której nie należy przesyłać do GitHuba):

    python -m neurogenesis.acf_temporal_holdout --semantic-sqlite "C:\private\semantic_fabric.sqlite3"

To nie jest polecenie, które pobiera dane z Internetu lub zmienia pliki. Bez co najmniej 96 prawdziwie zapisanych semantycznych obserwacji zakończy się odmową wykonania.

## Wyniki, integralność i prywatność

Raport JSON zawiera wyłącznie zagregowane liczby i **SHA-256 kolejności i cech binarnych zapisanych obserwacji**. Nie zawiera pytań, odpowiedzi ani zawartości źródeł. SQLite nigdy nie jest otwierana do zapisu; powtórny odczyt i `PRAGMA data_version` mają wykryć zmiany podczas dłuższego badania i zatrzymać analizę. Testy jednostkowe używają wyłącznie danych sztucznych i sprawdzają zachowanie programu oraz przypadki ujemne — **nie są wynikami naukowymi użytkownika**.

## Co badanie może i czego nie może udowodnić

Dodatni wynik byłby **wstępną wskazówką przewagi w przewidywaniu kolejnych ośmiu kategorii Qwen**, nie dowodem rozumienia języka, rozwiązywania nowych problemów czy autonomicznej inteligencji. Zdarzenia powstają przez ten sam klasyfikator LLM i nie są niezależnie ocenionymi faktami. Kolejne zdarzenia są skorelowane w czasie, a pięć nasion powtarza ten sam przebieg; nie należy traktować ich jako niezależnych próbek statystycznych. Rosnąca i nierosnąca sieć **nie mają w okresie testu identycznych kosztów**, dlatego nie można przypisać wzrostu zdolności wyłącznie strukturalnej plastyczności. Wartość progu jest opisową regułą, nie poziomem istotności statystycznej.

Wynik z tego badania **nigdy automatycznie nie zmienia**, nie promuje i nie nadpisuje wag Qwen, parametrów ACF, baz użytkownika ani polityk autonomii. Pozostają do ukończenia zadania #3 (pełna ablacja architektoniczna), #18 (bogatsze reprezentacje poznawcze), #8 (samodoskonalenie z rollback), #7 (homeostaza i samonaprawa), #9 (rzeczywiste skalowanie).

## Następny mierzalny próg

Po zebraniu odpowiednio dużego, niezależnego materiału trzeba z góry zadeklarować nowe zadania i porównać sieć rosnącą z silną **kontrolą nieplastyczną o wyrównanej liczbie parametrów i koszcie obliczeń** oraz z oryginalnym Qwen+RAG na faktycznych jakościowo ocenionych odpowiedziach. Zrealizowane tu kroki służą do uczciwego odrzucania nieudanych pomysłów, nie do deklarowania ukończenia „żywego mózgu”.
