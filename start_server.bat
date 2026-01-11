@echo off
echo ========================================
echo Starting Django Development Server
echo ========================================
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python manage.py runserver

pause
