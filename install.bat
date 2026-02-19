@echo off
:: SadTalker Desktop — Installer launcher
:: Uruchom jako Administrator dla najlepszych wyników

echo.
echo  ====================================================
echo   SadTalker Desktop  ^|  Installer
echo  ====================================================
echo.

:: Sprawdź czy PowerShell jest dostępny
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo  [BLAD] PowerShell nie jest zainstalowany lub niedostepny.
    echo  Zainstaluj PowerShell 5.1+ i sprobuj ponownie.
    pause
    exit /b 1
)

:: Odblokuj wykonywanie skryptów PS tylko dla tej sesji i odpal instalator
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -InstallerDir "%~dp0."