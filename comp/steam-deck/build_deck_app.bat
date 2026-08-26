@echo off
title Compilar App para Steam Deck (.AppImage)
echo =======================================================
echo   🎮 COMPILADOR: APP STEAM DECK (.AppImage)
echo =======================================================
echo.

cd /d "%~dp0..\..\deck-app"

echo [1/2] Instalando dependencias de Node.js...
call npm install
echo.

echo [2/2] Generando archivo .AppImage para SteamOS...
call npx electron-builder --linux AppImage
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️ ATENCION: En Windows, para empaquetar un archivo .AppImage de Linux,
    echo Windows requiere permisos de enlaces simbolicos (symlinks).
    echo.
    echo Si te salio error de "El cliente no dispone de un privilegio requerido":
    echo 1. Haz clic derecho sobre este archivo 'build_deck_app.bat' y selecciona 'Ejecutar como Administrador'.
    echo O bien activa el 'Modo de Desarrollador' en la configuracion de Windows.
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0..\.."
if not exist "dist\steam-deck" mkdir "dist\steam-deck"
copy /y "deck-app\dist\*.AppImage" "dist\steam-deck\" 2>nul

echo.
echo =======================================================
echo   ✅ ¡APPIMAGE GENERADO CON ÉXITO!
echo   📂 Archivo listo para Releases en:
echo      dist\steam-deck\
echo =======================================================
pause
