@echo off
REM Diagnostic de l'ecran Claude Code Usage (affiche pourquoi il est vide).
setlocal
cd /d "%~dp0.."
python windows\check-claude.py
echo.
pause
