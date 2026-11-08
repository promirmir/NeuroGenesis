@echo off
setlocal
cd /d "%~dp0"
title NeuroGenesis Mission Control - local Qt
if not exist "pyproject.toml" (
  echo [ERROR] Uruchom plik z pelnego folderu zrodel NeuroGenesis.
  pause
  exit /b 2
)
set "VENV=.venv"
set "PY=%VENV%\Scripts\python.exe"
if not exist "%PY%" (
  py -3.12 --version >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Zainstaluj Python 3.12 x64 ze strony python.org i uruchom ponownie.
    echo Nie wprowadzono zmian w lokalnej pamieci NeuroGenesis.
    pause
    exit /b 3
  )
  echo Tworzenie lokalnego srodowiska Python, bez uprawnien administratora.
  py -3.12 -m venv "%VENV%"
  if errorlevel 1 goto fail
)
"%PY%" -c "import PySide6.QtWidgets, neurogenesis" >nul 2>&1
if errorlevel 1 (
  echo.
  echo [UWAGA] Pierwsze uruchomienie musi zainstalowac biblioteki PySide6 przez pip.
  echo Pobieranie oznacza polaczenie z publicznym indeksem pakietow.
  echo Repozytorium nie pobiera ani nie wysyla Twojej prywatnej bazy SQLite.
  choice /M "Czy wyrazasz zgode na pobranie zaleznosci Qt"
  if errorlevel 2 exit /b 0
  "%PY%" -m pip install --disable-pip-version-check -e ".[command-center]"
  if errorlevel 1 goto fail
)
echo.
echo NeuroGenesis Mission Control - Qt z prawdziwa lokalna telemetria.
echo Siec aplikacji wylaczona bez Twojej zgody.
"%PY%" -m neurogenesis.command_center
if errorlevel 1 goto fail
exit /b 0
:fail
echo [ERROR] Uruchomienie nie powiodlo sie. Sprawdz terminal i dokumentacje.
pause
exit /b 1
