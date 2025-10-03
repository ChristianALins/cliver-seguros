#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test do login através de requisições HTTP que simula o navegador
"""

import requests
import sys
import os

def test_login():
    """Testa o login com as credenciais corretas"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Primeira requisição: GET na página de login para pegar cookies de sessão
    print("🔍 Fazendo GET na página de login...")
    session = requests.Session()
    
    try:
        # Fazer GET no login
        get_response = session.get(f"{base_url}/login")
        print(f"GET Status: {get_response.status_code}")
        
        if get_response.status_code != 200:
            print("❌ Erro ao acessar página de login")
            return
            
        # Fazer POST com credenciais
        print("\n🔑 Fazendo POST com credenciais admin/admin...")
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        post_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"POST Status: {post_response.status_code}")
        print(f"Headers: {dict(post_response.headers)}")
        
        # Verificar se houve redirect (302 = sucesso)
        if post_response.status_code == 302:
            location = post_response.headers.get('Location', '')
            print(f"✅ LOGIN SUCESSO! Redirecionando para: {location}")
            
            # Seguir o redirect para verificar se chegamos no dashboard
            if 'dashboard' in location or location.endswith('/'):
                print("🎯 Redirecionamento correto para dashboard")
                
                # Fazer requisição para o dashboard
                dashboard_response = session.get(f"{base_url}/dashboard")
                print(f"Dashboard Status: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard acessível após login!")
                else:
                    print(f"❌ Erro ao acessar dashboard: {dashboard_response.status_code}")
                    
        elif post_response.status_code == 200:
            print("❌ LOGIN FALHOU - Voltou para página de login")
            # Verificar se há mensagem de erro na resposta
            if 'usuário' in post_response.text.lower() or 'senha' in post_response.text.lower():
                print("🔍 Página contém mensagem de erro de usuário/senha")
            else:
                print("🔍 Página não contém mensagem de erro específica")
                
        else:
            print(f"❌ Status inesperado: {post_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False
        
    return True

def verify_server():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get("http://127.0.0.1:5000/login", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🧪 Teste de Login - CLIVER Seguros")
    print("=" * 50)
    
    # Verificar se servidor está rodando
    if not verify_server():
        print("❌ Servidor não está rodando em http://127.0.0.1:5000")
        print("💡 Execute: python app_corrigido.py")
        sys.exit(1)
    
    print("✅ Servidor está rodando")
    print()
    
    # Executar teste
    success = test_login()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Teste concluído")
    else:
        print("❌ Teste falhou")