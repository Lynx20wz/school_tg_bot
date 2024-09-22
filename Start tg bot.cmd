@echo off
:: Путь к вашему виртуальному окружению
set VENV_PATH==\venv\Scripts\activate.bat

:: Активация виртуального окружения
call %VENV_PATH%

:: Запуск вашего Python файла
python main.py