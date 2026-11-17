@echo off
REM Gera o executavel ContatosTerritorio.exe em dist\ContatosTerritorio\
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul || (echo Python nao encontrado. Instale em https://www.python.org & pause & exit /b 1)

python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

set DEST=dist\ContatosTerritorio
if exist "%DEST%" rmdir /s /q "%DEST%"
pyinstaller --noconfirm --clean --onefile --console --name ContatosTerritorio --distpath "%DEST%" executar.py || (pause & exit /b 1)

mkdir "%DEST%\dados"
copy config.json "%DEST%\" >nul
copy dados\territorios_exemplo.geojson "%DEST%\dados\" >nul
copy dados\territorios.geojson "%DEST%\dados\" >nul
copy dados\bloqueio.csv "%DEST%\dados\" >nul
copy dados\amostra_osm_ficticia.json "%DEST%\dados\" >nul
copy docs\GUIA_DO_VOLUNTARIO.md "%DEST%\" >nul

echo.
echo Pronto! Executavel em %DEST%
pause
