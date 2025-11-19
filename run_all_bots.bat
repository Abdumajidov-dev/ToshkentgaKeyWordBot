@echo off
REM ===========================================================
REM Toshkent Keyword Bot - Barcha 4 ta botni ishga tushirish
REM ===========================================================
REM 1. UserBot - Keyword monitoring (FAST/NORMAL)
REM 2. Admin Bot - Keywords va Groups
REM 3. Customer Bot - Mijozlar va to'lovlar
REM 4. Duplicate Remover Bot - Takroriy habarlar
REM ===========================================================

cd /d "%~dp0"
echo.
echo ============================================================
echo BARCHA BOTLARNI ISHGA TUSHIRISH
echo ============================================================
echo.
python main.py
pause
