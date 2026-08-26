@echo off
title Compilar Todo (Windows Server .exe + Steam Deck .AppImage)
echo ================================================================
echo   🚀 COMPILANDO TODO PARA GITHUB RELEASES (DESDE WINDOWS)
echo ================================================================
echo.

echo [PASO 1/2] Compilando Servidor para Windows (SteamDeckCompanionServer.exe)...
python scripts\build_server.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error al compilar el servidor Windows.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [PASO 2/2] Compilando App para Steam Deck (SteamDeckCompanion.AppImage)...
cd deck-app
call npm install
call npm run build:linux
cd ..

echo.
echo ================================================================
echo   🎉 ¡TODO COMPILADO Y LISTO PARA SUBIR A GITHUB RELEASES!
echo ================================================================
echo.
echo  1. Servidor PC Windows:  dist\SteamDeckCompanionServer.exe
echo  2. App Steam Deck:       deck-app\dist\*.AppImage
echo.
echo ================================================================
pause
