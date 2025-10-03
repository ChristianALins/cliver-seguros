@echo off
title Sistema Corretora de Seguros - Inicialização
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              SISTEMA CORRETORA DE SEGUROS                ║
echo ║                     Versão 1.0                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo [INFO] Verificando sistema...

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado! Instale Python 3.11+ antes de continuar.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

:: Navegar para o diretório correto
cd /d "%~dp0"
echo [INFO] Diretório de trabalho: %cd%

:: Verificar se o arquivo app.py existe
if not exist "app.py" (
    echo [ERRO] Arquivo app.py não encontrado!
    echo Certifique-se de estar no diretório correto.
    pause
    exit /b 1
)

echo [OK] Aplicação encontrada
echo.

echo [INFO] Iniciando sistema...
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    INFORMAÇÕES DE ACESSO                 ║
echo ║                                                          ║
echo ║  URL: http://localhost:5000                              ║
echo ║                                                          ║
echo ║  CREDENCIAIS DE TESTE:                                   ║
echo ║  • master / master123 (Administrador)                   ║
echo ║  • user / user123 (Usuário)                            ║
echo ║  • admin / admin123 (Admin)                            ║
echo ║                                                          ║
echo ║  Pressione Ctrl+C para parar o servidor                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Executar a aplicação
python app.py

echo.
echo [INFO] Sistema encerrado.
pause