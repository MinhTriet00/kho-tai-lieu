@echo off
set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend
set VENV_DIR=%BACKEND_DIR%\.venv

if not exist "%VENV_DIR%" (
    python -m venv "%VENV_DIR%"
)
call "%VENV_DIR%\Scripts\activate.bat"

echo Dang cai dat thu vien (Co the mat 1-2 phut)...
pip install --quiet --upgrade pip
pip install --quiet -r "%BACKEND_DIR%\requirements.txt"

if not exist "%FRONTEND_DIR%\dist" mkdir "%FRONTEND_DIR%\dist"
copy "%FRONTEND_DIR%\index.html" "%FRONTEND_DIR%\dist\index.html" >nul

echo ========================================
echo    KHO TAI LIEU SO DA SAN SANG
echo    Truy cap: http://localhost:8000
echo ========================================

cd "%BACKEND_DIR%"
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --workers 1