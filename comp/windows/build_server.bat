@echo off
title Compilar Servidor PC Windows (.exe con GUI)
echo =======================================================
echo   COMPILADOR: SERVIDOR PC WINDOWS (.exe con GUI)
echo =======================================================
echo.

cd /d "%~dp0..\.."

echo [1/3] Verificando dependencias de Python y PyInstaller...
python -m pip install --quiet -r requirements.txt pyinstaller

echo [2/3] Compilando ejecutable con interfaz grafica...
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

if not exist "dist\windows\SteamDeckCompanionServer.exe" (
    echo.
    echo ERROR: No se pudo generar el archivo .exe.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo   SERVIDOR WINDOWS COMPILADO CON EXITO!
echo   Archivo listo para Releases en:
echo      dist\windows\SteamDeckCompanionServer.exe
echo =======================================================
pause
