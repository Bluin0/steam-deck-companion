@echo off
title Compilar Servidor PC Windows (.exe)
echo =======================================================
echo   🖥️ COMPILADOR: SERVIDOR PC WINDOWS (.exe)
echo =======================================================
echo.

cd /d "%~dp0..\.."

echo [1/3] Verificando dependencias de Python y PyInstaller...
python -m pip install --quiet -r requirements.txt pyinstaller

echo [2/3] Compilando ejecutable unico de Windows...
if not exist "dist\windows" mkdir "dist\windows"

python -m PyInstaller ^
    --name "SteamDeckCompanionServer" ^
    --onefile ^
    --clean ^
    --noconfirm ^
    --add-data "profiles;profiles" ^
    --add-data "src/client;src/client" ^
    --distpath "dist\windows" ^
    --workpath "build_temp\win" ^
    --specpath "build_temp\win" ^
    "src\server\main.py"

if exist "build_temp" rmdir /s /q "build_temp"

echo.
echo =======================================================
echo   ✅ ¡SERVIDOR WINDOWS COMPILADO CON ÉXITO!
echo   📂 Archivo listo para Releases en:
echo      dist\windows\SteamDeckCompanionServer.exe
echo =======================================================
pause
