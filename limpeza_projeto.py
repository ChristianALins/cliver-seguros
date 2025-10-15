#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Limpeza do Projeto CLIVER Seguros
Remove arquivos obsoletos mantendo apenas os essenciais
Autor: Christian Lins
Data: 14/10/2025
"""

import os
import shutil
from datetime import datetime

def main():
    print("=" * 70)
    print("🧹 CLIVER SEGUROS - LIMPEZA DE ARQUIVOS OBSOLETOS")
    print("=" * 70)
    
    workspace_path = os.getcwd()
    print(f"📂 Diretório: {workspace_path}")
    
    # Arquivos essenciais para manter
    arquivos_essenciais = {
        # Aplicação principal (versão mais recente e funcional)
        'app_sistema_corrigido.py',  # Versão 2.0 - Mais completa e corrigida
        
        # Configurações e banco
        'config.py',
        'requirements.txt',
        'requirements_sqlserver.txt',
        'create_tables_completo.sql',
        'criar_banco_sqlserver.sql',
        'database_completo_melhorado.sql',
        
        # Documentação importante
        'README.md',
        'LICENSE',
        'VERSION',
        'PROJECT_SUMMARY.md',
        'IMPLEMENTACAO_COMPLETA.md',
        'SISTEMA_FUNCIONANDO.md',
        
        # Scripts de inicialização
        'INICIAR_SISTEMA.bat',
        'INICIAR_CLIVER_SQLSERVER.bat',
        
        # Utilitários importantes
        'criar_colaboradores.py',
        'verificar_banco.py',
        'verificar_colaboradores.py',
        
        # Controle de versão
        '.gitignore',
    }
    
    # Arquivos app_* obsoletos para remover
    arquivos_app_obsoletos = [
        'app.py',
        'app_cliver_corrigido.py',
        'app_cliver_final.py',
        'app_cliver_seguro_testado.py',
        'app_cliver_sqlite_completo.py',
        'app_complete.py',
        'app_completo_final.py',
        'app_completo_funcional.py',  # Versão com erros de template
        'app_completo_funcionando.py',
        'app_corrigido.py',
        'app_debug_login.py',
        'app_debug_simple.py',
        'app_final_corrigido.py',
        'app_final_testado.py',  # Versão intermediária
        'app_hibrido_teste.py',
        'app_links_corrigidos.py',
        'app_simples.py',
        'app_sistema_estavel.py',  # Com erros
        'app_sistema_simples.py',  # Versão simplificada
        'app_sqlite.py',
        'app_sqlserver_completo.py',
        'app_teste_final.py',
        'app_teste_minimo.py',
        'app_ultra_simples.py',
    ]
    
    # Arquivos de teste obsoletos
    arquivos_teste_obsoletos = [
        'check_apolices.py',
        'check_db.py',
        'diagnostico_login.py',
        'teste_completo.py',
        'teste_final_sistema.py',
        'teste_servidor.py',
        'teste_sistema_completo.py',
        'test_browser_login.py',
        'test_colaboradores.py',
        'test_debug.py',
        'test_detailed.py',
        'test_final.py',
        'test_login.py',
        'test_login_simple.py',
        'test_login_urllib.py',
        'test_main_server.py',
        'test_post_debug.py',
        'test_routes.py',
        'test_routes_final.py',
        'test_simple.py',
        'test_single_route.py',
        'test_sistema.py',
        'verificar_acesso.py',
    ]
    
    # Arquivos de documentação obsoletos/duplicados
    docs_obsoletos = [
        'ANALISE_E_CORRECOES.md',
        'ANALISE_ESTRUTURA_CORRIGIDA.md',
        'ATUALIZACAO_CORES_CLIVER.md',
        'CHANGELOG.md',
        'CORRECOES_IMPLEMENTADAS.md',
        'CORRECOES_REALIZADAS.md',
        'DIAGRAMA_RELACIONAMENTOS.md',
        'FRONTEND_CORRIGIDO.md',
        'GITHUB_UPLOAD_GUIDE.md',
        'GITHUB_UPLOAD_GUIDE_v1.2.md',
        'GUIA_SEGURANCA.md',
        'README_GITHUB.md',
        'README_SQLSERVER.md',
        'README_v1.2.md',
        'RELATORIOS_PERSONALIZADOS.md',
        'RELATORIO_CORRECOES_FINAIS.md',
        'RELATORIO_FINAL_SISTEMA.md',
        'RELATORIO_TESTE_FINAL.md',
        'TESTE_EXECUTADO_SUCESSO.md',
        'PROJETO_FINALIZADO_RELATORIO.md',
    ]
    
    # Scripts obsoletos
    scripts_obsoletos = [
        'INICIAR_CLIVER.bat',
        'PROJETO_FINALIZADO.py',
        'INSTALACAO_CLIVER.py',
    ]
    
    # Arquivos SQL duplicados/obsoletos
    sql_obsoletos = [
        'CONSULTAS_EXEMPLOS.sql',
        'create_corretoradb.sql',
        'create_database_complete.sql',
        'create_tables.sql',
        'create_tables_corrigido.sql',
        'database_completo_com_melhorias.sql',
        'insert_teste.sql',
    ]
    
    # Outros arquivos obsoletos
    outros_obsoletos = [
        'cliver_seguros.db',
        'cliver_seguros.log',
        'cliver_seguros_completo.db',
        'cliver_seguros_nova.db',
        'config_cliver.ini',
        'CONTRIBUTING.md',
        '.gitignore_template',
    ]
    
    # Compilar lista completa de arquivos para remover
    arquivos_para_remover = (
        arquivos_app_obsoletos +
        arquivos_teste_obsoletos + 
        docs_obsoletos +
        scripts_obsoletos +
        sql_obsoletos +
        outros_obsoletos
    )
    
    # Diretórios para remover
    diretorios_para_remover = [
        'static',      # Se vazio ou desnecessário
        'templates',   # Se vazio ou desnecessário  
        '__pycache__',
        'docs',        # Se houver documentação obsoleta
    ]
    
    removidos = 0
    mantidos = 0
    
    print(f"\\n🔍 Analisando arquivos...")
    
    # Remover arquivos
    for arquivo in arquivos_para_remover:
        caminho = os.path.join(workspace_path, arquivo)
        if os.path.exists(caminho):
            try:
                os.remove(caminho)
                print(f"🗑️  Removido: {arquivo}")
                removidos += 1
            except Exception as e:
                print(f"❌ Erro ao remover {arquivo}: {e}")
        
    # Remover diretórios vazios ou desnecessários
    for diretorio in diretorios_para_remover:
        caminho = os.path.join(workspace_path, diretorio)
        if os.path.exists(caminho):
            try:
                if diretorio == '__pycache__':
                    shutil.rmtree(caminho)
                    print(f"🗑️  Removido diretório: {diretorio}")
                    removidos += 1
                elif os.path.isdir(caminho) and not os.listdir(caminho):
                    os.rmdir(caminho)
                    print(f"🗑️  Removido diretório vazio: {diretorio}")
                    removidos += 1
            except Exception as e:
                print(f"❌ Erro ao remover diretório {diretorio}: {e}")
    
    # Contar arquivos mantidos
    for arquivo in os.listdir(workspace_path):
        if os.path.isfile(os.path.join(workspace_path, arquivo)):
            mantidos += 1
    
    print(f"\\n✅ Limpeza concluída!")
    print(f"🗑️  Arquivos removidos: {removidos}")
    print(f"📄 Arquivos mantidos: {mantidos}")
    
    print(f"\\n📋 Arquivos essenciais mantidos:")
    for arquivo in sorted(os.listdir(workspace_path)):
        if os.path.isfile(os.path.join(workspace_path, arquivo)):
            print(f"   ✓ {arquivo}")
    
    print(f"\\n🎯 Sistema otimizado e organizado!")
    print("=" * 70)

if __name__ == "__main__":
    main()