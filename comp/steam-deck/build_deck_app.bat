@echo off
title Compilar App Steam Deck (.AppImage)
echo =======================================================
echo   COMPILADOR: APP STEAM DECK (.AppImage)
echo =======================================================
echo.

:: Check for admin privileges (required for symlinks on Windows)
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Necesito permisos de Administrador para crear el .AppImage.
    echo Relanzando como Administrador...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
    exit /b
)

cd /d "%~dp0..\..\deck-app"

echo [1/2] Instalando dependencias de Node.js...
call npm install
echo.

echo [2/2] Generando archivo .AppImage para SteamOS...
call npx electron-builder --linux AppImage

cd /d "%~dp0..\.."
if not exist "dist\steam-deck" mkdir "dist\steam-deck"
copy /y "deck-app\dist\*.AppImage" "dist\steam-deck\" 2>nul

echo.
echo =======================================================
echo   APP DE STEAM DECK COMPILADA CON EXITO!
echo   Archivo listo para Releases en:
echo      dist\steam-deck\
echo =======================================================
pause
