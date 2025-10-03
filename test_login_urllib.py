#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simples do login usando urllib (biblioteca padrão)
"""

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import sys

def test_login_simple():
    """Testa o login usando urllib"""
    
    # Criar um opener com suporte a cookies
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)
    
    base_url = "http://127.0.0.1:5000"
    
    try:
        print("🔍 Testando GET na página de login...")
        # GET na página de login
        get_response = urllib.request.urlopen(f"{base_url}/login")
        print(f"GET Status: {get_response.getcode()}")
        
        if get_response.getcode() != 200:
            print("❌ Erro ao acessar página de login")
            return False
        
        print("✅ Página de login acessível")
        
        # Preparar dados do POST
        print("\n🔑 Testando POST com admin/admin...")
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        # Codificar dados
        data = urllib.parse.urlencode(login_data).encode('utf-8')
        
        # Criar request POST
        request = urllib.request.Request(
            f"{base_url}/login",
            data=data,
            method='POST'
        )
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        # Fazer POST sem seguir redirects automaticamente
        try:
            post_response = urllib.request.urlopen(request)
            print(f"POST Status: {post_response.getcode()}")
            
            if post_response.getcode() == 200:
                # Ler conteúdo da resposta para verificar mensagens
                content = post_response.read().decode('utf-8')
                if 'dashboard' in content.lower():
                    print("✅ Possivelmente foi redirecionado para dashboard")
                elif 'usuário' in content.lower() or 'senha' in content.lower() or 'login' in content.lower():
                    print("❌ LOGIN FALHOU - Ainda na página de login")
                    if 'obrigatórios' in content.lower():
                        print("🔍 Mensagem: Campos obrigatórios")
                    if 'incorret' in content.lower():
                        print("🔍 Mensagem: Usuário/senha incorretos")
                else:
                    print("🔍 Conteúdo não identificado")
                    
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print("✅ LOGIN SUCESSO! Recebeu redirect (302)")
                location = e.headers.get('Location', '')
                print(f"🎯 Redirecionando para: {location}")
                
                # Testar se consegue acessar dashboard
                try:
                    dashboard_response = urllib.request.urlopen(f"{base_url}/dashboard")
                    if dashboard_response.getcode() == 200:
                        print("✅ Dashboard acessível após login!")
                        return True
                    else:
                        print(f"❌ Dashboard não acessível: {dashboard_response.getcode()}")
                except Exception as de:
                    print(f"❌ Erro ao acessar dashboard: {de}")
                    
            else:
                print(f"❌ Erro HTTP {e.code}: {e.reason}")
                
        return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def check_server():
    """Verifica se o servidor está rodando"""
    try:
        response = urllib.request.urlopen("http://127.0.0.1:5000/login", timeout=3)
        return response.getcode() == 200
    except:
        return False

if __name__ == "__main__":
    print("🧪 Teste de Login Simples - CLIVER Seguros")
    print("=" * 50)
    
    # Verificar servidor
    if not check_server():
        print("❌ Servidor não está rodando")
        print("💡 Inicie o servidor primeiro: python app_corrigido.py")
        sys.exit(1)
    
    print("✅ Servidor está ativo")
    print()
    
    # Executar teste
    success = test_login_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ LOGIN FUNCIONANDO!")
    else:
        print("❌ PROBLEMA NO LOGIN")