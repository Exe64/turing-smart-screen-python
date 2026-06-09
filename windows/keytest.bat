@echo off
REM Testeur de touches : affiche ce que le clavier envoie (utile pour le G915).
setlocal
cd /d "%~dp0.."
python windows\keytest.py
echo.
pause
