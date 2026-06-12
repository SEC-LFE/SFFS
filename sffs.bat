@echo off
:: SFFS Windows Launcher — runs the GUI with NO terminal window.
:: The app code + bundled Python live on the hidden SFFS_VAULT partition; this
:: launcher sits alone on the visible partition and locates the vault at runtime.
:: Double-click to run.
setlocal EnableDelayedExpansion

:: ── Locate the app root ───────────────────────────────────────────────────────
:: Resolution order:
::   1. SFFS_VAULT partition — a drive holding .sffs_vault marker + python\pythonw.exe
::   2. bundled  %~dp0python\pythonw.exe   (single-folder portable build)
::   3. project  %~dp0.venv\Scripts\...     (local dev)
set "APP="
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if not defined APP if exist "%%D:\.sffs_vault" if exist "%%D:\python\pythonw.exe" set "APP=%%D:\"
)
if not defined APP if exist "%~dp0python\pythonw.exe" set "APP=%~dp0"
if not defined APP if exist "%~dp0.venv\Scripts\pythonw.exe" set "APP=%~dp0"

if not defined APP (
    echo SFFS: could not locate the app. No SFFS_VAULT partition found and no local
    echo python\ or .venv next to this launcher.
    pause
    exit /b 1
)

if exist "%APP%python\pythonw.exe" (
    set "PYW=%APP%python\pythonw.exe"
    set "PY=%APP%python\python.exe"
) else (
    set "PYW=%APP%.venv\Scripts\pythonw.exe"
    set "PY=%APP%.venv\Scripts\python.exe"
)

:: On first pass, relaunch this script fully hidden via WScript (window style 0)
:: so the cmd console never stays on screen, then exit this visible instance.
:: NOTE: keep this OUT of an if(...) block — the parens in CreateObject(...) would
:: otherwise close the block early and break batch parsing.
if defined SFFS_HIDDEN goto :run
set "SFFS_HIDDEN=1"
set "VBS=%temp%\sffs_launch.vbs"
>"%VBS%" echo CreateObject("WScript.Shell").Run "cmd /c """"%~f0"""" %*", 0, False
wscript //nologo "%VBS%"
del "%VBS%" >nul 2>&1
exit /b

:run
:: First-run dependency install (silent — no console output).
if not exist "%APP%.deps_installed" (
    "%PY%" -m pip install -r "%APP%main-code\requirements.txt" --quiet >nul 2>&1
    echo installed> "%APP%.deps_installed"
)

cd /d "%APP%"
:: Launch via the windowless interpreter — no terminal, no pause.
:: windows_job_wrapper.py resolves the repo root from its own location (the vault).
"%PYW%" "%APP%code2\windows_job_wrapper.py" %*
endlocal
