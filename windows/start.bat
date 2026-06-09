@echo off
REM ============================================================================
REM  Lance le gestionnaire multi-ecrans AVEC une fenetre console (debug/test).
REM  Pour le demarrage automatique silencieux, utilisez run-hidden.vbs.
REM ============================================================================
setlocal
cd /d "%~dp0.."

echo Lancement du gestionnaire multi-ecrans (Ctrl+C pour arreter)...
echo.
python multiscreen.py

echo.
echo Le programme s'est arrete.
pause
