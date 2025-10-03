#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA CLIVER SEGUROS - Versão Principal Corrigida
Baseado no servidor de debug que funciona
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'cliver_seguros_secret_key_2024'

# Configuração do banco de dados
DATABASE = 'cliver_seguros.db'

def get_db():
    """Retorna conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def require_login(f):
    """Decorator para verificar se o usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            print("❌ Acesso negado - usuário não logado")
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        print(f"✅ Acesso autorizado para user_id: {session.get('user_id')}")
        return f(*args, **kwargs)
    return decorated_function

# ROTAS PRINCIPAIS

@app.route('/')
def home():
    print("📍 Rota / acessada")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"📍 Rota /login acessada - Método: {request.method}")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"   📝 Dados recebidos: username='{username}', password='{password}'")
        
        if not username or not password:
            print("   ❌ Username ou password vazios")
            flash('Por favor, preencha todos os campos!', 'error')
            return render_template('login_clean.html')
        
        try:
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND active = 1', 
                               (username,)).fetchone()
            conn.close()
            
            print(f"   🔍 Usuário encontrado no banco: {user is not None}")
            
            if user:
                print(f"   🔐 Verificando senha...")
                password_ok = check_password_hash(user['password'], password)
                print(f"   🔐 Senha correta: {password_ok}")
                
                if password_ok:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_role'] = user['role']
                    
                    print(f"   ✅ LOGIN SUCESSO! Sessão criada para user_id: {user['id']}")
                    
                    # Atualizar último login
                    conn = get_db()
                    conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', 
                                (user['id'],))
                    conn.commit()
                    conn.close()
                    
                    flash('Login realizado com sucesso!', 'success')
                    print("   🔄 Redirecionando para dashboard...")
                    return redirect(url_for('dashboard'))
                else:
                    print("   ❌ Senha incorreta")
                    flash('Senha incorreta!', 'error')
            else:
                print("   ❌ Usuário não encontrado ou inativo")
                flash('Usuário não encontrado!', 'error')
                
        except Exception as e:
            print(f"   💥 Erro no login: {e}")
            flash(f'Erro interno: {str(e)}', 'error')
    
    print("   📄 Renderizando template de login")
    return render_template('login_clean.html')

@app.route('/dashboard')
@require_login
def dashboard():
    print(f"📍 Rota /dashboard acessada")
    print(f"   ✅ Usuário logado: {session.get('username')} (ID: {session.get('user_id')})")
    
    conn = get_db()
    
    # Estatísticas para o dashboard
    stats = {}
    stats['total_clientes'] = conn.execute('SELECT COUNT(*) as count FROM clientes WHERE status = "ativo"').fetchone()['count']
    stats['total_apolices'] = conn.execute('SELECT COUNT(*) as count FROM apolices WHERE status = "ativa"').fetchone()['count']
    stats['sinistros_abertos'] = conn.execute('SELECT COUNT(*) as count FROM sinistros WHERE status = "aberto"').fetchone()['count']
    stats['renovacoes_pendentes'] = conn.execute('SELECT COUNT(*) as count FROM renovacoes WHERE status = "pendente"').fetchone()['count']
    
    # Apólices próximas ao vencimento (30 dias)
    vencimento_proximo = conn.execute('''
        SELECT a.*, c.nome as cliente_nome, s.nome as seguradora_nome
        FROM apolices a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN seguradoras s ON a.seguradora_id = s.id
        WHERE a.data_vencimento BETWEEN DATE('now') AND DATE('now', '+30 days')
        AND a.status = 'ativa'
        ORDER BY a.data_vencimento
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    return render_template('dashboard_simple.html', stats=stats, vencimentos=vencimento_proximo)

@app.route('/logout')
def logout():
    print(f"📍 Logout - usuário: {session.get('username')}")
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# ROTAS DE CLIENTES

@app.route('/clientes')
@require_login
def listar_clientes():
    conn = get_db()
    clientes = conn.execute('''
        SELECT c.*, COUNT(a.id) as total_apolices
        FROM clientes c
        LEFT JOIN apolices a ON c.id = a.cliente_id
        WHERE c.status = 'ativo'
        GROUP BY c.id
        ORDER BY c.nome
    ''').fetchall()
    conn.close()
    
    return render_template('clientes.html', clientes=clientes)

if __name__ == '__main__':
    print("="*50)
    print("🚀 SISTEMA CLIVER SEGUROS CORRIGIDO")
    print("="*50)
    print("📊 Dashboard: http://localhost:5003/")
    print("👤 Login: admin / admin")
    print("📱 Versão com debug completo!")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5003, debug=True)