@echo off
REM build\windows\build-win.bat — compila e empacota o instalador Windows.
REM Uso:  build\windows\build-win.bat [VERSION]
REM
REM Pré-requisitos:
REM   - Python 3.9+ no PATH
REM   - PyInstaller (pip install pyinstaller)
REM   - NSIS instalado (https://nsis.sourceforge.io)

setlocal enabledelayedexpansion

set VERSION=%1
if "%VERSION%"=="" set VERSION=0.2.0

echo.
echo === fzBGPTools v%VERSION% — Windows build ===
echo.

REM 1. Limpar
if exist build\work rmdir /s /q build\work
if exist dist\fzbgptools.exe del /q dist\fzbgptools.exe
if exist dist\fzBGPTools-%VERSION%-setup.exe del /q dist\fzBGPTools-%VERSION%-setup.exe

REM 2. Instalar deps
echo [1/4] Instalando dependencias...
python -m pip install --quiet -r requirements.txt
python -m pip install --quiet pyinstaller Pillow

REM 3. Gerar icon.ico a partir do icon.png (necessario para NSIS)
echo [2/4] Gerando icon.ico...
python -c "from PIL import Image; img = Image.open('src/resources/icon.png'); img.save('src/resources/icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
if %errorlevel% neq 0 (
    echo X Falha ao gerar icon.ico
    exit /b 1
)

REM 4. PyInstaller
echo [3/4] Compilando binario com PyInstaller...
pyinstaller --noconfirm --clean fzbgptools.spec
if not exist dist\fzbgptools.exe (
    echo X PyInstaller falhou.
    exit /b 1
)

REM 5. NSIS
echo [4/4] Empacotando instalador NSIS...
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo X makensis nao encontrado no PATH. Instale NSIS: https://nsis.sourceforge.io
    exit /b 1
)
makensis /DVERSION=%VERSION% build\windows\installer.nsi
if %errorlevel% neq 0 (
    echo X NSIS falhou.
    exit /b 1
)

echo.
echo + Instalador gerado: dist\fzBGPTools-%VERSION%-setup.exe
echo.
endlocal
