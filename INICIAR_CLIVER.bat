@echo off
echo ============================================================
echo INICIANDO SISTEMA CLIVER SEGUROS
echo ============================================================
echo.

cd /d "C:\Users\Christian&Amanda\Documents\SQL Server Management Studio\CorretoraSegurosDB\CorretoraSegurosDB-1\database\schema\workspace"

echo Verificando arquivos...
if not exist "app_cliver_final.py" (
    echo ERRO: Aplicacao nao encontrada!
    pause
    exit /b 1
)

echo Iniciando aplicacao Flask...
python app_cliver_final.py

echo.
echo ============================================================
echo Aplicacao finalizada. Pressione qualquer tecla para sair.
pause > nul