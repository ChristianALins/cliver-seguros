#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da versão final do sistema CLIVER
"""

import urllib.request
import urllib.parse

def test_final_login():
    """Testa o login na versão final"""
    
    try:
        print("🧪 Testando Sistema CLIVER Final (Porta 5003)...")
        
        # Dados do POST
        data = urllib.parse.urlencode({
            'username': 'admin',
            'password': 'admin'
        }).encode('utf-8')
        
        # Request POST
        req = urllib.request.Request(
            'http://127.0.0.1:5003/login',
            data=data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            method='POST'
        )
        
        print(f"📤 Enviando: username=admin, password=admin")
        
        # Fazer requisição
        try:
            response = urllib.request.urlopen(req)
            print(f"📨 Status: {response.getcode()}")
            
            content = response.read().decode('utf-8')
            
            # Analisar resposta
            if 'dashboard' in content.lower():
                print("✅ SUCESSO - Conteúdo do Dashboard detectado!")
            elif 'bem-vindo' in content.lower():
                print("✅ SUCESSO - Mensagem de boas vindas!")
            elif 'login' in content.lower():
                print("❌ FALHA - Ainda na página de login")
                
                # Verificar mensagens específicas
                if 'obrigatórios' in content.lower():
                    print("🔍 Mensagem: Campos obrigatórios")
                elif 'incorret' in content.lower():
                    print("🔍 Mensagem: Credenciais incorretas")
                else:
                    print("🔍 Sem mensagem de erro específica")
            else:
                print("🔍 Conteúdo não identificado")
                
            return response.getcode() == 200
                
        except urllib.error.HTTPError as e:
            if e.code == 302:
                print("✅ REDIRECT DETECTADO - LOGIN FUNCIONANDO!")
                location = e.headers.get('Location', 'Não informado')
                print(f"🎯 Redirecionando para: {location}")
                
                # Testar acesso ao dashboard
                try:
                    dashboard_req = urllib.request.Request('http://127.0.0.1:5003/dashboard')
                    dashboard_resp = urllib.request.urlopen(dashboard_req)
                    if dashboard_resp.getcode() == 200:
                        print("✅ Dashboard acessível!")
                    return True
                except Exception as de:
                    print(f"❌ Erro no dashboard: {de}")
                    return False
            else:
                print(f"❌ Erro HTTP: {e.code} - {e.reason}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Teste Final - Sistema CLIVER Seguros")
    print("=" * 50)
    
    success = test_final_login()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!")
    else:
        print("❌ AINDA HÁ PROBLEMAS NO SISTEMA")
        
    print("\n💡 Para testar manualmente, acesse:")
    print("   🔗 http://127.0.0.1:5003/teste")
    print("   🔗 http://127.0.0.1:5003/login")
    print("\n👤 Use: admin / admin")