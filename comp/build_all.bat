@echo off
title Compilar Todo para GitHub Releases
echo ================================================================
echo   COMPILADOR MAESTRO — Todo para GitHub Releases
echo ================================================================
echo.
echo   1. Servidor Windows (.exe con GUI)
echo   2. App Steam Deck (.AppImage)
echo   3. Servidor Linux (Paquete Portable .zip)
echo.
echo ================================================================
echo.

:: Check admin
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Necesito permisos de Administrador para el .AppImage de Steam Deck.
    echo Relanzando como Administrador...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
    exit /b
)

cd /d "%~dp0.."

:: ═══════════════════════════════════════════
:: 1. SERVIDOR WINDOWS (.exe)
:: ═══════════════════════════════════════════
echo.
echo ================================================================
echo   [1/3] COMPILANDO SERVIDOR WINDOWS (.exe con GUI)
echo ================================================================
echo.

cd /d "%~dp0.."

python -m pip install --quiet -r requirements.txt pyinstaller

if not exist "dist\windows" mkdir "dist\windows"

python -m PyInstaller ^
    --name "SteamDeckCompanionServer" ^
    --onefile ^
    --windowed ^
    --clean ^
    --noconfirm ^
    --add-data "%CD%\profiles;profiles" ^
    --add-data "%CD%\src\client;src/client" ^
    --distpath "dist\windows" ^
    "src\server\main.py"

if exist "SteamDeckCompanionServer.spec" del "SteamDeckCompanionServer.spec"
if exist "build" rmdir /s /q "build"

if exist "dist\windows\SteamDeckCompanionServer.exe" (
    echo    [OK] dist\windows\SteamDeckCompanionServer.exe
) else (
    echo    [FALLO] No se genero el .exe
)

:: ═══════════════════════════════════════════
:: 2. APP STEAM DECK (.AppImage)
:: ═══════════════════════════════════════════
echo.
echo ================================================================
echo   [2/3] COMPILANDO APP STEAM DECK (.AppImage)
echo ================================================================
echo.

cd /d "%~dp0..\deck-app"
call npm install
call npx electron-builder --linux AppImage

cd /d "%~dp0.."
if not exist "dist\steam-deck" mkdir "dist\steam-deck"
copy /y "deck-app\dist\*.AppImage" "dist\steam-deck\" 2>nul

if exist "dist\steam-deck\*.AppImage" (
    echo    [OK] AppImage generado en dist\steam-deck\
) else (
    echo    [FALLO] No se genero el .AppImage
)

:: ═══════════════════════════════════════════
:: 3. SERVIDOR LINUX (Paquete Portable)
:: ═══════════════════════════════════════════
echo.
echo ================================================================
echo   [3/3] EMPAQUETANDO SERVIDOR LINUX (Portable .zip)
echo ================================================================
echo.

cd /d "%~dp0.."

if not exist "dist\linux" mkdir "dist\linux"

:: Create portable zip with all server files + launcher
python -c "import zipfile, os; z=zipfile.ZipFile('dist/linux/SteamDeckCompanionServer-Linux-Portable.zip','w',zipfile.ZIP_DEFLATED); [z.writestr('iniciar_servidor.sh','#!/bin/bash\ncd \"$(dirname \"$0\")\"\npython3 -m venv .venv 2>/dev/null || true\n[ -f .venv/bin/pip ] && .venv/bin/pip install --quiet -r requirements.txt\nPY=${0/.venv/bin/python3:-python3}\n\"$PY\" src/server/main.py\n')]; [z.write(os.path.join(r,f),os.path.relpath(os.path.join(r,f),'.')) for folder in ['src','profiles'] for r,_,fs in os.walk(folder) for f in fs]; z.write('requirements.txt'); z.close(); print('[OK] Paquete portable generado.')"

echo    Nota: Para compilar un .AppImage nativo del servidor Linux,
echo    ejecuta comp/linux/build_server.sh en cualquier maquina Linux.

:: ═══════════════════════════════════════════
:: RESUMEN
:: ═══════════════════════════════════════════
echo.
echo ================================================================
echo   RESUMEN DE ARCHIVOS GENERADOS PARA GITHUB RELEASES:
echo ================================================================
echo.
echo   1. dist\windows\SteamDeckCompanionServer.exe  (Servidor Windows)
echo   2. dist\steam-deck\*.AppImage                 (App Steam Deck)
echo   3. dist\linux\*-Portable.zip                  (Servidor Linux)
echo.
echo   Para el .AppImage nativo del servidor Linux,
echo   ejecuta comp\linux\build_server.sh en Linux.
echo.
echo ================================================================
pause
