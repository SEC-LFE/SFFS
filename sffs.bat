@echo off
:: SFFS Windows Launcher — runs the GUI with NO terminal window.
:: Double-click to run from USB or the project folder.
setlocal

:: Prefer the windowless interpreter (pythonw.exe) so no console is attached.
if exist "%~dp0python\pythonw.exe" (
    set "PYW=%~dp0python\pythonw.exe"
    set "PY=%~dp0python\python.exe"
) else (
    set "PYW=pythonw"
    set "PY=python"
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
if not exist "%~dp0.deps_installed" (
    "%PY%" -m pip install -r "%~dp0main-code\requirements.txt" --quiet >nul 2>&1
    echo installed> "%~dp0.deps_installed"
)

cd /d "%~dp0"
:: Launch via the windowless interpreter — no terminal, no pause.
"%PYW%" code2\windows_job_wrapper.py %*
endlocal
