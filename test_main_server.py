#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Login no Servidor Principal
"""

import requests
import sys
from urllib.parse import urljoin

def test_main_server():
    base_url = "http://localhost:5003"
    
    print("🔍 Testando servidor principal na porta 5003...")
    
    # Teste 1: Acessar página de login
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ GET / - Status: {response.status_code}")
        
        if "login" in response.text.lower():
            print("✅ Página de login carregada")
        else:
            print("❌ Página de login não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao acessar /: {e}")
        return False
    
    # Teste 2: Realizar login
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        session = requests.Session()
        
        # Primeiro, obter a página de login
        login_page = session.get(f"{base_url}/login")
        print(f"✅ GET /login - Status: {login_page.status_code}")
        
        # Fazer o POST do login
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"🔐 POST /login - Status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            print("✅ Redirecionamento após login (302)")
            redirect_url = login_response.headers.get('Location')
            print(f"📍 Redirecionando para: {redirect_url}")
            
            # Seguir o redirecionamento
            dashboard_response = session.get(f"{base_url}{redirect_url}")
            print(f"📊 GET Dashboard - Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Dashboard acessado com sucesso!")
                return True
            else:
                print("❌ Falha ao acessar dashboard")
                print(f"Conteúdo: {dashboard_response.text[:200]}...")
        else:
            print(f"❌ Login falhou - Status: {login_response.status_code}")
            print(f"Conteúdo: {login_response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("="*60)
    print("🧪 TESTE DO SERVIDOR PRINCIPAL")
    print("="*60)
    
    success = test_main_server()
    
    print("="*60)
    if success:
        print("✅ TESTE PASSOU! Servidor principal funcionando")
    else:
        print("❌ TESTE FALHOU! Verifique os logs do servidor")
    print("="*60)