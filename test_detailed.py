#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Detalhado de Login
"""

import requests
from bs4 import BeautifulSoup

def test_login_detailed():
    base_url = "http://localhost:5003"
    
    print("🔍 Teste detalhado do login...")
    
    session = requests.Session()
    
    try:
        # 1. Obter página de login
        login_page = session.get(f"{base_url}/login")
        print(f"📄 Página de login: Status {login_page.status_code}")
        
        # 2. Verificar se tem form de login
        soup = BeautifulSoup(login_page.text, 'html.parser')
        form = soup.find('form')
        if form:
            print("✅ Formulário encontrado")
            print(f"Action: {form.get('action', 'Não definido')}")
            print(f"Method: {form.get('method', 'Não definido')}")
        else:
            print("❌ Formulário não encontrado")
            
        # 3. Fazer login com dados corretos
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        print(f"🔐 Fazendo login com: {login_data}")
        
        login_response = session.post(f"{base_url}/login", 
                                    data=login_data, 
                                    allow_redirects=False)
        
        print(f"📊 Resposta do login: Status {login_response.status_code}")
        print(f"Headers: {dict(login_response.headers)}")
        
        # 4. Verificar conteúdo da resposta
        if login_response.status_code == 200:
            # Ainda na página de login - verificar mensagens
            soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Procurar por mensagens de flash
            flash_messages = soup.find_all(class_=['alert', 'message', 'flash'])
            if flash_messages:
                print("📢 Mensagens encontradas:")
                for msg in flash_messages:
                    print(f"  - {msg.get_text().strip()}")
            else:
                print("❌ Nenhuma mensagem de erro encontrada")
                
            # Procurar por texto de erro
            if "inválid" in login_response.text.lower() or "erro" in login_response.text.lower():
                print("❌ Texto de erro encontrado na resposta")
            else:
                print("❓ Não há texto de erro óbvio")
                
        elif login_response.status_code == 302:
            print("✅ Redirecionamento detectado!")
            redirect_url = login_response.headers.get('Location')
            print(f"📍 Redirecionando para: {redirect_url}")
        else:
            print(f"❓ Status inesperado: {login_response.status_code}")
            
        # 5. Verificar se consegue acessar dashboard diretamente
        dashboard_response = session.get(f"{base_url}/dashboard")
        print(f"🏠 Dashboard direto: Status {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            if "dashboard" in dashboard_response.text.lower():
                print("✅ Dashboard acessível após login")
            else:
                print("❌ Dashboard retorna 200 mas não é dashboard")
        
    except Exception as e:
        print(f"💥 Erro durante teste: {e}")

if __name__ == "__main__":
    test_login_detailed()