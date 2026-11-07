# NeuroGenesis — uruchomienie w Windows

Publiczne autorstwo: **Miron przy pomocy AI**.

1. Zainstaluj Python 3.11 lub nowszy oraz Git.
2. Otwórz PowerShell i wykonaj:

```powershell
git clone https://github.com/promirmir/NeuroGenesis.git
cd NeuroGenesis
py -3 -m unittest discover -s tests -v
py -3 -m neurogenesis benchmark --seeds 10 --steps-per-phase 128 --probe-steps 48
py -3 -m neurogenesis demo --steps 160 --state brain.snapshot.json
py -3 -m neurogenesis status --state brain.snapshot.json
```

Wszystkie obliczenia działają lokalnie, bez sieci. Wyniki benchmarku są
wypisywane w formacie JSON. Istniejące pliki `.snapshot.json` przechowuj
prywatnie; nie dodawaj do publicznego repozytorium.

Wersja 0.3 to **symulator badawczy**, nie samodzielnie myślący rozmówca.
Samo nazwisko nie służy do uwierzytelniania operatora.
