@echo off
REM ============================================================================
REM  Installe les dependances Python necessaires au gestionnaire multi-ecrans.
REM  A lancer une seule fois (double-clic) apres avoir installe Python.
REM ============================================================================
setlocal
cd /d "%~dp0.."

echo.
echo === Mise a jour de pip ===
python -m pip install --upgrade pip || goto :error

echo.
echo === Installation des dependances du projet (requirements.txt) ===
python -m pip install -r requirements.txt || goto :error

echo.
echo === Installation des dependances du gestionnaire multi-ecrans ===
python -m pip install pynput || goto :error

echo.
echo === Termine avec succes ===
echo Vous pouvez maintenant lancer windows\start.bat pour tester,
echo puis windows\install-autostart.ps1 pour le demarrage automatique.
echo.
pause
exit /b 0

:error
echo.
echo *** Une erreur est survenue. Verifiez que "python" est bien dans le PATH. ***
echo     (Reinstallez Python en cochant "Add Python to PATH" si besoin.)
echo.
pause
exit /b 1
