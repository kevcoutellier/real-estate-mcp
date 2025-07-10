@echo off
REM Script Windows pour lancer le MCP avec environnement virtuel actif
REM Utilisé par Claude Desktop sur Windows

cd /d "%~dp0"

REM Vérifier que l'environnement virtuel existe
if not exist "venv\Scripts\python.exe" (
    echo ❌ Environnement virtuel non trouve !
    echo 🔧 Lancez 'python install.py' pour creer l'environnement
    exit /b 1
)

REM Activer l'environnement virtuel et lancer le serveur
call venv\Scripts\activate.bat
set PYTHONPATH=%~dp0src
python mcp_wrapper.py
