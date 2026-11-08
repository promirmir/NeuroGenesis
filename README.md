# NeuroGenesis

**Lokalny system badawczy inspirowany neurobiologią — v0.7.0**  
**Autorstwo publiczne: Miron przy pomocy AI**

Research status: **research prototype v0.7.0.** Stabilizacja lokalnego narzędzia badawczego; brak potwierdzonej inteligencji ogólnej.

NeuroGenesis rozwija eksperymentalną, mierzalną architekturę sztucznej inteligencji: plastyczne sieci neuronowe, trwałą prywatną pamięć, kontrolowane zdobywanie wiedzy z publicznych źródeł, niezależne eksperymenty PyTorch oraz transparentne oceny jakości. **To nie jest AGI, cyfrowa świadomość ani zweryfikowana symulacja ludzkiego mózgu.** Wygenerowane przez Foundation Brain bajty nie stanowią jeszcze kompetentnej rozmowy.

## Windows — aplikacja bez instalowania Pythona

[**Pobierz najnowszy NeuroGenesis.exe**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [Suma SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) · [Wszystkie wydania](https://github.com/promirmir/NeuroGenesis/releases)

**Wydawany EXE to sprawdzona aplikacja Windows oparta na Tkinter**, nie opcjonalne Command Center Qt. Przed każdą publikacją GitHub Actions uruchamia testy Windows i właściwy spakowany EXE z prawdziwą testową bazą SQLite, wyznacza SHA-256 i wiąże wydanie z dokładnym SHA kodu. Program pozostaje niepodpisany cyfrowo. Nie uruchamia internetu bez zgody.

### Co działa w opublikowanym EXE

| Obszar | Rzeczywista funkcjonalność |
|---|---|
| Rozmowa | Ręcznie nauczone odpowiedzi oraz dosłowne cytaty ze źródeł; odmowa, gdy brak wystarczającego fragmentu; **brak zweryfikowanego rozumowania semantycznego** |
| Pamięć | Trwała prywatna SQLite: stan małej sieci neuronowej, doświadczenia, odpowiedzi, wersje stron i uprawnienia |
| Internet | Kontrolowany odczyt publicznych stron HTTPS, osobny panel badania dziedziny, ograniczenia zasięgu/tempa/robots.txt, zgoda wyłączona domyślnie |
| Monitor | Prawdziwe kroki mózgu, synapsy, neurony i ślady aktywności sieci LIF — nie wskaźniki świadomości |
| Kopie | **v0.7.0:** ręczna spójna migawka SQLite, kontrola uszkodzeń, SHA-256 oraz bezpieczne odtwarzanie do NOWEGO pliku (narzędzie CLI) |
| Aktualizacja | Wersjonowane EXE i pliki SHA-256 na GitHub; dane pozostają w prywatnym katalogu użytkownika |

Pamięć Windows znajduje się standardowo w `%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3`. Plik i kopie **nie są szyfrowane** — chroń je jak prywatne dokumenty. Nic nie jest wysyłane do GitHub z pamięci użytkownika.

## Command Center — nowoczesna aplikacja Qt

Opcjonalny, prawdziwy interfejs PySide6 oferuje siedem paneli: przegląd, rozmowę ze źródłami i kontekstem sesji, badanie domeny, monitor mózgu, sterowanie osobnym treningiem Foundation Brain, bazę wiedzy i ustawienia (w tym nowe kopie pamięci). Jest już technicznie sprawdzany na Windows i Ubuntu; oddzielny Qt EXE przechodzi testy pakowania, ale **nie jest publicznie dystrybuowany** do czasu pełnej weryfikacji obowiązków LGPLv3, informacji licencyjnych i bibliotek.

Uruchomienie ze źródeł w Pythonie 3.12:

```powershell
py -3.12 -m pip install -e ".[command-center]"
py -3.12 -m neurogenesis.command_center
```

Opcjonalny rzeczywisty lokalny trening PyTorch wymaga osobnego dodatku:

```powershell
py -3.12 -m pip install -e ".[foundation]"
```

Instrukcje: [Command Center](docs/COMMAND_CENTER.md) · [Foundation Brain](docs/FOUNDATION_BRAIN.md) · [Kontrolowany trening](docs/KNOWLEDGE_TRAIN.md).

## Zabezpieczanie i odzyskiwanie prywatnej pamięci

W EXE otwórz zakładkę **Kopia pamięci**, wybierz nową nazwę pliku i sprawdź podaną sumę SHA-256. W Qt znajdziesz analogiczne funkcje w Ustawieniach. Obie działają poza głównym wątkiem interfejsu i korzystają z transakcyjnej kopii SQLite.

Do weryfikacji lub odtworzenia w nowej lokalizacji przez Python:

```powershell
py -3.12 -m neurogenesis.recovery --verify "C:\Kopie\NeuroGenesis-backup.sqlite3"
py -3.12 -m neurogenesis.recovery --restore "C:\Kopie\NeuroGenesis-backup.sqlite3" --output "C:\Kopie\NeuroGenesis-odtworzona.sqlite3" --confirm-restore-new
```

**Nie nadpisuj ręcznie aktywnej bazy.** Zobacz [instrukcję kopii i odtwarzania](docs/MEMORY_RECOVERY.md). Zewnętrzne checkpointy modelu `.pt` muszą być zabezpieczane osobno.

## Jakość i rzeczywiste ograniczenia

- Cytaty zawierają prawdziwy zapisany tekst i źródło, ale **nie dowodzą prawdziwości cytowanego twierdzenia**. Syntetyczne testy wykryły fałszywe cytowania w niektórych pytaniach z nieuprawnioną przesłanką.
- Nie istnieją jeszcze wystarczające niezależne dane wskazujące, że własny Foundation Brain rozumie kontekst rozmowy. Jego PyTorch GRU uczy się przewidywać kolejne bajty; w dotychczasowym małym teście prosty model Markowa był lepszy. Wagi, checkpointy i testy retencji są prawdziwe, ale pozostają eksperymentalne.
- Mechanizmy bezpieczeństwa nie dają uprawnienia do trenowania na dowolnej stronie. Każda wersja źródła wymaga jawnego potwierdzenia praw; autonomiczne badanie internetu jest limitowane i wyłączone na starcie.
- Brak potwierdzonego testu CUDA na fizycznym GPU, niezależnego audytu bezpieczeństwa, przewagi w naturalnym QA, gotowego przetwarzania wielokomputerowego czy oficjalnego pakietu Qt.
- Nie uruchamiaj eksperymentalnych checkpointów z niezaufanych źródeł. Nie przechowuj haseł ani danych wrażliwych w cytatach lub niezaszyfrowanych kopiach.

Pomiar i otwarte ograniczenia: [Audyt dostawy](docs/DELIVERY_AUDIT.md) · [QA z niepewnością statystyczną](docs/QA_ACCEPTANCE.md) · [BM25 kontra wyszukiwanie bieżące](docs/BM25_BASELINE.md) · [Retencja modelu](docs/RETENTION_GATE.md) · [Model zagrożeń](docs/SECURITY.md).

## Niezawodność i rozwój

Kod jest testowany w Pythonie **3.11, 3.12 i 3.13**. Oddzielne kontrole uruchamiają rzeczywisty PyTorch CPU, opcjonalny Qt Windows/Ubuntu, Windows Tk EXE, kontrolę prywatności kodu i pamięć SQLite po restarcie. Aktualny wynik i SHA są dostępne bezpośrednio w [GitHub Actions](https://github.com/promirmir/NeuroGenesis/actions).

Podstawowe informacje do bezstratnej kontynuacji: [PROJECT_STATE.md](docs/PROJECT_STATE.md), [DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md), [AGENTS.md](AGENTS.md).

**Status produktu:** stabilizowane narzędzie badawcze, nie ukończona sztuczna inteligencja ogólna. Najważniejszą otwartą kwestią pozostaje niezależnie potwierdzona jakość rzeczywistego rozumowania i odpowiedzi.
