#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das rotas do Sistema Cliver Seguros
Verifica se todas as rotas estão respondendo corretamente
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:5003"

def test_routes():
    """Testa as principais rotas do sistema"""
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Rotas para testar (sem autenticação)
    public_routes = [
        "/",
        "/login",
        "/test"
    ]
    
    # Rotas que precisam de autenticação (testar depois do login)
    protected_routes = [
        "/dashboard",
        "/clientes",
        "/clientes/novo",
        "/apolices",
        "/apolices/nova",
        "/apolices/vencimento", 
        "/sinistros",
        "/sinistros/novo",
        "/consultas",
        "/relatorios",
        "/relatorios/vendas",
        "/relatorios/comissoes",
        "/relatorios/sinistros",
        "/configuracoes",
        "/seguradoras",
        "/tipos-seguro"
    ]
    
    print("=" * 60)
    print("TESTE DAS ROTAS DO SISTEMA CLIVER SEGUROS")
    print("=" * 60)
    
    # Testar rotas públicas
    print("\n1. TESTANDO ROTAS PÚBLICAS:")
    for route in public_routes:
        try:
            url = urljoin(BASE_URL, route)
            response = session.get(url)
            status = "✅ OK" if response.status_code in [200, 302] else f"❌ ERRO {response.status_code}"
            print(f"   {route:<20} - {status}")
        except Exception as e:
            print(f"   {route:<20} - ❌ ERRO: {e}")
    
    # Fazer login
    print("\n2. FAZENDO LOGIN:")
    try:
        login_url = urljoin(BASE_URL, "/login")
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        response = session.post(login_url, data=login_data)
        if response.status_code in [200, 302]:
            print("   ✅ Login realizado com sucesso!")
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro no login: {e}")
        return
    
    # Testar rotas protegidas
    print("\n3. TESTANDO ROTAS PROTEGIDAS:")
    for route in protected_routes:
        try:
            url = urljoin(BASE_URL, route)
            response = session.get(url)
            status = "✅ OK" if response.status_code == 200 else f"❌ ERRO {response.status_code}"
            print(f"   {route:<25} - {status}")
        except Exception as e:
            print(f"   {route:<25} - ❌ ERRO: {e}")
    
    # Testar API endpoints
    print("\n4. TESTANDO API ENDPOINTS:")
    api_routes = [
        "/api/dashboard-stats",
        "/consultas/cliente?busca_cliente=admin",
        "/consultas/apolice?busca_apolice=123"
    ]
    
    for route in api_routes:
        try:
            url = urljoin(BASE_URL, route)
            response = session.get(url)
            status = "✅ OK" if response.status_code == 200 else f"❌ ERRO {response.status_code}"
            print(f"   {route:<35} - {status}")
        except Exception as e:
            print(f"   {route:<35} - ❌ ERRO: {e}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    test_routes()