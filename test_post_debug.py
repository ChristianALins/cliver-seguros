#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico para requisição POST
"""

import urllib.request
import urllib.parse
import sys

def test_post_debug():
    """Testa POST com debug detalhado"""
    
    try:
        print("🔍 Testando POST direto na rota /login...")
        
        # Dados do POST
        data = urllib.parse.urlencode({
            'username': 'admin',
            'password': 'admin'
        }).encode('utf-8')
        
        # Criar request
        req = urllib.request.Request(
            'http://127.0.0.1:5001/login',
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            method='POST'
        )
        
        print(f"Data enviado: {data}")
        print(f"Headers: {req.headers}")
        
        # Fazer requisição
        response = urllib.request.urlopen(req)
        
        print(f"Status: {response.getcode()}")
        print(f"Headers da resposta: {dict(response.headers)}")
        
        # Ler conteúdo
        content = response.read().decode('utf-8')
        
        # Verificar se há redirecionamento ou permanece na página
        if 'dashboard' in content.lower():
            print("✅ Posível sucesso - conteúdo do dashboard")
        elif 'login' in content.lower() and 'form' in content.lower():
            print("❌ Ainda na página de login")
            
            # Procurar por mensagens específicas
            if 'obrigatórios' in content.lower():
                print("🔍 Encontrou: 'obrigatórios'")
            if 'incorret' in content.lower():
                print("🔍 Encontrou: 'incorretos'")
            if 'bem-vindo' in content.lower():
                print("🔍 Encontrou: 'bem-vindo'")
                
        # Mostrar um trecho do conteúdo para análise
        print(f"\n📄 Primeiros 500 caracteres da resposta:")
        print(content[:500])
        
    except urllib.error.HTTPError as e:
        if e.code == 302:
            print("✅ Redirecionamento 302 - LOGIN SUCESSO!")
            location = e.headers.get('Location', 'Não informado')
            print(f"Redirecionando para: {location}")
        else:
            print(f"❌ Erro HTTP: {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🧪 Teste POST Debug")
    print("=" * 50)
    test_post_debug()