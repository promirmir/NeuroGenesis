# NeuroGenesis 0.12.5 — decyzje oparte na zmierzonej skuteczności ACF

**Autor:** Miron przy pomocy AI.

## Pierwsza rzeczywista decyzja operacyjna sterowana przez plastyczną sieć

Do tej pory semantyczny ACF przyjmował znaczniki wygenerowane przez
lokalny Qwen3-1.7B, przewidywał kolejne znaczniki i raportował
causal/prequential MSE. Nie podejmował jednak działań.

Od 0.12.5 nowy `semantic_policy.py` wprowadza ścisłą **bramkę
metapoznawczą**. Model może zdecydować o **wstępnym odczycie zatwierdzonej
lokalnej bazy wiedzy** dla *przewidywanego następnego tematu*.
To mała, odwracalna operacja, ale faktycznie zależy od jego własnych
historycznych błędów i aktywności sieci.

### Warunki automatycznego działania

Decyzja może zostać wykonana wyłącznie gdy:

- jest co najmniej 64 **rzeczywiście ocenionych**, przyczynowo
  wygenerowanych prognoz;
- najlepsza dotychczas metoda to **plastyczna sieć ACF**, a nie jej
  nierozrastająca się kontrola, ostatnia obserwacja lub przewidywanie stałe;
- średni błąd MSE sieci adaptacyjnej w ostatnim oknie jest mniejszy
  od każdego punktu odniesienia o co najmniej 0,005 oraz o co najmniej 5%;
- prognoza jednej z konkretnych sześciu dziedzin ma aktywację
  co najmniej 0,70 i przewagę co najmniej 0,12 nad drugą kategorią.
  Te wartości nie są skalibrowanymi prawdopodobieństwami ani
  gwarancją trafności. Ogólne `facts` i `dialogue` nie uruchamiają odczytu.

W przypadku jakiejkolwiek niepewności system wybiera **wstrzymanie
decyzji**, nie wymyśla kompetencji. W interfejsie pokazuje rzeczywisty
powód: za mało danych, brak przewagi nad modelem kontrolnym lub
niejednoznaczna prognoza.

### Co jest wykonywane

Tylko `LocalKnowledge.retrieve(query, limit=3)`, na zatwierdzonych
lokalnych indeksach FTS5. Program uzyskuje faktyczną liczbę
wyszukanych fragmentów albo informację o braku wiedzy.

**Zakazane w tej ścieżce:** połączenie z Internetem, pobieranie stron,
modyfikowanie plików, wykonywanie kodu, zmienianie wag Qwen, samodzielne
akceptowanie odpowiedzi lub umieszczanie hipotetycznych źródeł
w odpowiedziach bez ich ponownej, niezależnej weryfikacji dla konkretnego pytania.
Do interfejsu nie trafia treść fragmentów, nazwa prywatnego pliku ani URL.

### Sprawdzenie, czy prognoza ma sens

```powershell
python -m neurogenesis.semantic_policy_benchmark --semantic-sqlite "SCIEZKA_DO_PAMIĘCI/semantic_fabric.sqlite3"
```

Audyt odtwarza **rzeczywiste lokalnie zapisane znaczniki** w kolejności
zdarzeń. Przed ujawnieniem każdego następnego znacznika podejmuje
decyzję, a dopiero później mierzy, czy przewidywana kategoria faktycznie
wystąpiła. Porównuje to z przewidywaniem opartym na poprzedniej
obserwacji **na tych samych wybranych zdarzeniach**. Raportuje również
liczbę wszystkich wstrzymań, wynik zerowy i niekorzystny.

To jest **pomiar selektywny**: wybór momentów zależy od wcześniejszych
wyników, a same kategorie są produktem modelu Qwen. Nie wolno z niego
wyciągać wniosku o ogólnej poprawie jakości odpowiedzi bez
niezależnego zbioru testowego i mierzonej skuteczności użytkowych zadań.
`user_task_improvement_proven=false` jest zapisane w wyniku.

## Faktyczny stan projektu

Wersja 0.12.5 wykonuje jeden autentyczny, ograniczony wybór
operacyjny na podstawie samomodelu ACF. To pierwszy element
zamkniętej pętli: percepcja → uczenie → ocena błędów →
decyzja → **odwracalne działanie na własnej pamięci**.
Nie jest jeszcze dowodem przewagi inteligencji konwersacyjnej,
własnej architektury językowej, samoczynnego trenowania 1,7 mld
parametrów ani sztucznej świadomości.

**Następny wymagany eksperyment:** niezależne, niewidziane zadania,
w których ACF wybiera strategię nauki lub planowania, a
zarejestrowana jakość rozwiązania zostaje porównana z zamrożonym
baseline bez ACF. Dopiero dodatnia, odtwarzalna przewaga może
uzasadnić większą autonomię.
