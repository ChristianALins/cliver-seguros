@echo off
echo ================================================
echo       CLIVER SEGUROS - SQL SERVER VERSION
echo ================================================
echo.

echo Instalando dependencias necessarias...
pip install -r requirements_sqlserver.txt

echo.
echo ================================================
echo Executando sistema CLIVER Seguros...
echo ================================================
echo.

python app_sqlserver_completo.py

pause