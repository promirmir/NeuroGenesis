# NeuroGenesis — bezpieczne przywrócenie nowego repozytorium

Oficjalne autorstwo: **Miron przy pomocy AI**.

Przygotowana paczka zawiera sprawdzony kod badawczy v0.2.2, a nie sam szablon dokumentacji. Poprzednie repozytorium zostało usunięte. Nie importujemy jego publicznej historii.

## Publikacja na Windows

1. Rozpakuj całe archiwum ZIP do nowego katalogu (nie do starego katalogu Git).
2. Upewnij się, że są zainstalowane Git for Windows i Python 3.11+.
3. W ustawieniach GitHub **Settings → Emails** włącz „Keep my email addresses private” oraz blokowanie pushy ujawniających adres e-mail.
4. Otwórz `URUCHOM_BEZPIECZNA_PUBLIKACJE.cmd` w rozpakowanym katalogu.
5. Jeśli Git poprosi o logowanie, wykonaj je wyłącznie w standardowym oknie Git Credential Manager.
6. Skrypt wykona audyt, testy, utworzy pojedynczy nowy commit pod publicznym adresem GitHub `noreply`, a następnie zastąpi tylko *dokładnie wskazany* początkowy commit nowego repozytorium.

Weryfikacja na GitHubie: `https://github.com/promirmir/NeuroGenesis/commits/main`. Powinien być **jeden** nowy commit, którego autor i committer mają wyłącznie publiczny adres `noreply`.

## Zabezpieczenia

- Jeżeli główna gałąź GitHuba zmieniła się w międzyczasie, skrypt **nie opublikuje** zmian.
- Skrypt nie zawiera hasła ani tokenu i nie przesyła prywatnej poczty w metadanych commitów.
- Nie kopiuje dawnej historii Git.
- Zachowuje działające komendy `demo`, `status`, `observe`, `compare`, `predict`, `origin` oraz testy.
- Automatyczny CI sprawdza również prywatność adresów autorów commitów.

**Ograniczenie:** wymiana historii głównej gałęzi nie usuwa automatycznie starych odnośników, cache GitHuba ani kopii pobranych wcześniej. Zgłoszenie do GitHub Support może być nadal konieczne.

## Gdy publikacja się zatrzyma

Nie ponawiaj siłowo push z opcją `--force`. Najpierw sprawdź stan zdalnej gałęzi i skonfrontuj go z lokalnym; zabezpieczenie SHA jest celowe. Po poprawnej publikacji można kontynuować projekt w nowym czacie, każąc asystentowi przeczytać `AGENTS.md` i `docs/PROJECT_STATE.md`.

## Lokalna pamięć doświadczeń (v0.4)

```powershell
py -3 -m neurogenesis remember "Przykładowa obserwacja" --db local-data/experiences.sqlite3
py -3 -m neurogenesis recall "Przykładowa obserwacja" --db local-data/experiences.sqlite3
py -3 -m neurogenesis memory-status --db local-data/experiences.sqlite3
```

Pełna treść tekstu nie jest zapisywana bez `--store-text`. SQLite zachowuje
stan neuronów i dane doświadczeń; nie wrzucaj pliku bazy na GitHub.
