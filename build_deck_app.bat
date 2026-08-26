@echo off
title Compilar Steam Deck Companion AppImage (desde Windows)
echo =======================================================
echo  🎮 COMPILANDO APPIMAGE PARA STEAM DECK DESDE WINDOWS
echo =======================================================
cd deck-app
echo [1/2] Instalando dependencias de Node.js...
call npm install
echo.
echo [2/2] Generando archivo .AppImage para SteamOS...
call npm run build:linux
echo.
echo =======================================================
echo  ✅ ¡APPIMAGE GENERADO CON ÉXITO!
echo  📂 Lo tienes listo en: deck-app\dist\
echo =======================================================
pause
