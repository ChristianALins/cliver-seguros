#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do sistema simplificado
"""

import urllib.request
import urllib.parse

def test_simple_login():
    """Testa o login no sistema simplificado"""
    
    try:
        print("🧪 Testando sistema simplificado na porta 5002...")
        
        # Dados do POST
        data = urllib.parse.urlencode({
            'username': 'admin',
            'password': 'admin'
        }).encode('utf-8')
        
        # Request POST
        req = urllib.request.Request(
            'http://127.0.0.1:5002/login',
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            method='POST'
        )
        
        print(f"Enviando: {data}")
        
        # Fazer requisição
        try:
            response = urllib.request.urlopen(req)
            print(f"Status: {response.getcode()}")
            
            # Se chegou aqui, não houve redirect (seria HTTPError 302)
            content = response.read().decode('utf-8')
            
            if 'dashboard' in content.lower():
                print("✅ SUCESSO - Dashboard carregado!")
            elif 'bem-vindo' in content.lower():
                print("✅ SUCESSO - Mensagem de boas vindas!")
            elif 'login' in content.lower():
                print("❌ FALHOU - Ainda na página de login")
                if 'obrigatórios' in content.lower():
                    print("🔍 Erro: Campos obrigatórios")
                if 'incorretos' in content.lower():
                    print("🔍 Erro: Credenciais incorretas")
            else:
                print("🔍 Resposta não identificada")
                
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print("✅ REDIRECT DETECTADO - LOGIN SUCESSO!")
                location = e.headers.get('Location', 'Não informado')
                print(f"Redirecionando para: {location}")
                return True
            else:
                print(f"❌ Erro HTTP: {e.code}")
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    return False

if __name__ == "__main__":
    print("🧪 Teste Sistema Simplificado")
    print("=" * 50)
    test_simple_login()