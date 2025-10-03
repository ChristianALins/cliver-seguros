#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação do banco de dados
"""

import sqlite3
import os

def verificar_banco():
    """Verifica o estado do banco de dados"""
    
    db_path = 'cliver_seguros.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("✅ Banco de dados conectado com sucesso!")
        print(f"📁 Arquivo: {db_path}")
        print(f"📏 Tamanho: {os.path.getsize(db_path)} bytes")
        
        # Listar tabelas
        print("\n=== TABELAS ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        for tabela in tabelas:
            print(f"📋 {tabela[0]}")
            
        # Verificar estrutura da tabela colaboradores
        print("\n=== ESTRUTURA COLABORADORES ===")
        cursor.execute("PRAGMA table_info(colaboradores)")
        colunas = cursor.fetchall()
        
        for coluna in colunas:
            print(f"🔹 {coluna[1]} ({coluna[2]})")
            
        # Listar usuários
        print("\n=== USUÁRIOS ATIVOS ===")
        cursor.execute("SELECT usuario, senha, nome, nivel_acesso FROM colaboradores WHERE ativo=1")
        usuarios = cursor.fetchall()
        
        if usuarios:
            for user in usuarios:
                print(f"👤 User: '{user[0]}' | Pass: '{user[1]}' | Nome: '{user[2]}' | Nível: '{user[3]}'")
        else:
            print("❌ Nenhum usuário ativo encontrado!")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verificação do Banco de Dados - CLIVER Seguros")
    print("=" * 60)
    verificar_banco()