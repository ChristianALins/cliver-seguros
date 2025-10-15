#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste e Correção do Login
CLIVER Seguros - Sistema de Gestão
Autor: Christian Lins
Data: 15/10/2025
"""

import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("🔍 Testando conexão com banco de dados...")
    
    connection_strings = [
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=CorretoraSegurosDB;Trusted_Connection=yes;",
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=CorretoraSegurosDB;Trusted_Connection=yes;TrustServerCertificate=yes;",
        "DRIVER={SQL Server Native Client 11.0};SERVER=localhost;DATABASE=CorretoraSegurosDB;Trusted_Connection=yes;"
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        try:
            conn = pyodbc.connect(conn_str, timeout=10)
            print(f"✅ Conexão {i} bem-sucedida!")
            return conn
        except Exception as e:
            print(f"❌ Conexão {i} falhou: {str(e)}")
    
    return None

def check_colaboradores_table(conn):
    """Verifica a estrutura da tabela Colaboradores"""
    print("\n🔍 Verificando estrutura da tabela Colaboradores...")
    
    try:
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'Colaboradores'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("❌ Tabela Colaboradores não existe!")
            return False
        
        # Verificar estrutura da tabela
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'Colaboradores'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        print("✅ Estrutura da tabela Colaboradores:")
        for col in columns:
            print(f"   📋 {col[0]} - {col[1]} ({col[2]}) - Max: {col[3] or 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {str(e)}")
        return False

def check_test_user(conn):
    """Verifica se o usuário de teste existe"""
    print("\n🔍 Verificando usuário de teste...")
    
    try:
        cursor = conn.cursor()
        
        # Buscar usuário de teste
        cursor.execute("""
            SELECT id_colaborador, nome_colaborador, email_colaborador, 
                   senha, cargo, status 
            FROM Colaboradores 
            WHERE email_colaborador = ?
        """, ('christian.lins@outlook.com.br',))
        
        user = cursor.fetchone()
        
        if user:
            print("✅ Usuário encontrado:")
            print(f"   👤 ID: {user[0]}")
            print(f"   📧 Email: {user[2]}")
            print(f"   🎯 Cargo: {user[4] or 'N/A'}")
            print(f"   📊 Status: {user[5] or 'N/A'}")
            print(f"   🔑 Senha Hash: {user[3][:20]}..." if user[3] else "   🔑 Senha: Não definida")
            
            # Testar se a senha funciona
            if user[3]:
                test_password = check_password_hash(user[3], '123456')
                print(f"   🔐 Teste senha '123456': {'✅ OK' if test_password else '❌ FALHOU'}")
            
            return user
        else:
            print("❌ Usuário de teste não encontrado!")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {str(e)}")
        return None

def create_test_user(conn):
    """Cria ou atualiza o usuário de teste"""
    print("\n🔧 Criando/atualizando usuário de teste...")
    
    try:
        cursor = conn.cursor()
        
        # Hash da senha
        senha_hash = generate_password_hash('123456')
        
        # Verificar se usuário já existe
        cursor.execute("""
            SELECT id_colaborador FROM Colaboradores 
            WHERE email_colaborador = ?
        """, ('christian.lins@outlook.com.br',))
        
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Atualizar usuário existente
            cursor.execute("""
                UPDATE Colaboradores 
                SET nome_colaborador = ?, 
                    senha = ?, 
                    cargo = ?, 
                    status = ?,
                    data_cadastro = ?
                WHERE email_colaborador = ?
            """, (
                'Christian Lins',
                senha_hash,
                'Administrador',
                'Ativo',
                datetime.now(),
                'christian.lins@outlook.com.br'
            ))
            print("✅ Usuário atualizado com sucesso!")
            
        else:
            # Criar novo usuário
            cursor.execute("""
                INSERT INTO Colaboradores 
                (nome_colaborador, email_colaborador, senha, cargo, status, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'Christian Lins',
                'christian.lins@outlook.com.br',
                senha_hash,
                'Administrador',
                'Ativo',
                datetime.now()
            ))
            print("✅ Usuário criado com sucesso!")
        
        conn.commit()
        
        # Verificar criação
        return check_test_user(conn)
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {str(e)}")
        conn.rollback()
        return None

def test_login_process():
    """Testa todo o processo de login"""
    print("\n🧪 Testando processo completo de login...")
    
    conn = test_database_connection()
    if not conn:
        print("🔴 Não foi possível conectar ao banco!")
        return False
    
    # Verificar tabela
    if not check_colaboradores_table(conn):
        conn.close()
        return False
    
    # Verificar usuário
    user = check_test_user(conn)
    if not user:
        print("\n🔧 Criando usuário de teste...")
        user = create_test_user(conn)
    
    if not user:
        print("🔴 Falha ao criar/verificar usuário!")
        conn.close()
        return False
    
    # Teste de autenticação
    print("\n🔐 Testando autenticação...")
    
    if user[3]:  # Se tem senha
        auth_test = check_password_hash(user[3], '123456')
        if auth_test:
            print("✅ Autenticação funcionando corretamente!")
            print(f"\n🎯 Login funcional:")
            print(f"   📧 Email: {user[2]}")
            print(f"   🔑 Senha: 123456")
            print(f"   👤 Nome: {user[1]}")
            print(f"   🎭 Cargo: {user[4] or 'Administrador'}")
        else:
            print("❌ Falha na autenticação!")
            conn.close()
            return False
    else:
        print("❌ Usuário sem senha definida!")
        conn.close()
        return False
    
    conn.close()
    return True

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 TESTE E CORREÇÃO DO LOGIN - CLIVER SEGUROS")
    print("=" * 60)
    
    success = test_login_process()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ SISTEMA DE LOGIN FUNCIONANDO CORRETAMENTE!")
        print("🌐 Acesse: http://localhost:5006")
        print("📧 Email: christian.lins@outlook.com.br")
        print("🔑 Senha: 123456")
    else:
        print("🔴 PROBLEMAS ENCONTRADOS NO SISTEMA DE LOGIN!")
        print("🛠️ Execute as correções necessárias no banco de dados.")
    print("=" * 60)

if __name__ == "__main__":
    main()