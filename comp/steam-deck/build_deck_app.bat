@echo off
title Compilar App para Steam Deck (desde Windows)
echo =======================================================
echo   🎮 COMPILADOR: APP STEAM DECK (DESDE WINDOWS)
echo =======================================================
echo.

cd /d "%~dp0..\..\deck-app"

echo [1/3] Instalando dependencias de Node.js...
call npm install
echo.

echo [2/3] Empaquetando aplicacion para SteamOS...
call npm run build:linux
echo.

cd /d "%~dp0..\.."
if not exist "dist\steam-deck" mkdir "dist\steam-deck"
copy /y "deck-app\dist\*.zip" "dist\steam-deck\" 2>nul
copy /y "deck-app\dist\*.tar.gz" "dist\steam-deck\" 2>nul
copy /y "deck-app\dist\*.AppImage" "dist\steam-deck\" 2>nul

echo =======================================================
echo   ✅ ¡APP DE STEAM DECK GENERADA CON ÉXITO!
echo   📂 Archivo listo para Releases en:
echo      dist\steam-deck\
echo =======================================================
pause
