#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema CLIVER Seguros - Versão Teste Simplificada
APENAS PARA DEBUG DO LOGIN
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import sys

app = Flask(__name__)
app.secret_key = 'cliver_test_key'

# Banco de dados
DATABASE_PATH = 'cliver_seguros.db'

def get_db_connection():
    """Conecta com SQLite"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"ERRO DB: {e}")
        return None

@app.before_request
def log_request_info():
    """Log de TODAS as requisições"""
    print(f"\n{'='*50}")
    print(f"🔍 REQUEST: {request.method} {request.url}")
    if request.method == 'POST':
        print(f"🔍 FORM DATA: {dict(request.form)}")
        print(f"🔍 CONTENT-TYPE: {request.content_type}")
    print(f"{'='*50}")

@app.route('/')
def index():
    """Home"""
    print("🏠 INDEX: Redirecionando para login")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login super simplificado"""
    print(f"🔑 LOGIN: Método = {request.method}")
    
    if request.method == 'POST':
        print("🔍 POST DETECTADO!")
        
        # Obter dados
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"🔍 USERNAME: '{username}'")
        print(f"🔍 PASSWORD: '{password}'")
        
        # Validação básica
        if not username or not password:
            print("❌ CAMPOS VAZIOS")
            flash('Usuário e senha são obrigatórios', 'error')
            return render_template('login_simple.html')
        
        # Testar com credenciais fixas primeiro
        if username == 'admin' and password == 'admin':
            print("✅ LOGIN SUCESSO (FIXO)")
            session['user_id'] = 1
            session['username'] = username
            session['nome'] = 'Administrador'
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        
        # Testar banco de dados
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_colaborador, nome, nivel_acesso 
                FROM colaboradores 
                WHERE usuario = ? AND senha = ? AND ativo = 1
            """, (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                print(f"✅ LOGIN SUCESSO (DB): {dict(user)}")
                session['user_id'] = user['id_colaborador']
                session['username'] = username
                session['nome'] = user['nome']
                flash(f'Bem-vindo, {user["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
        
        print("❌ LOGIN FALHOU")
        flash('Usuário ou senha incorretos', 'error')
    
    # GET ou falha no POST
    print("📄 RETORNANDO TEMPLATE LOGIN")
    return render_template('login_simple.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard simples"""
    print("📊 DASHBOARD")
    if 'user_id' not in session:
        flash('Faça login primeiro', 'warning')
        return redirect(url_for('login'))
    
    return f"""
    <h1>✅ Dashboard CLIVER</h1>
    <p><strong>Usuário:</strong> {session.get('nome', 'N/A')}</p>
    <p><strong>ID:</strong> {session.get('user_id', 'N/A')}</p>
    <a href="/logout">Logout</a>
    """

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logout realizado', 'info')
    return redirect(url_for('login'))

@app.route('/teste')
def teste():
    """Teste"""
    return """
    <h1>🧪 TESTE CLIVER</h1>
    <p>Sistema funcionando!</p>
    <a href="/login">Login</a>
    """

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧪 SISTEMA CLIVER TESTE - VERSÃO DEBUG")
    print("="*60)
    print("🔑 Login: http://127.0.0.1:5002/login")
    print("📊 Dashboard: http://127.0.0.1:5002/dashboard") 
    print("🧪 Teste: http://127.0.0.1:5002/teste")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5002, debug=True)