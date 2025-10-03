#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE MÍNIMO DE LOGIN - CLIVER SEGUROS
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = 'cliver_seguros_secret_key_2024'

DATABASE = 'cliver_seguros.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    print("🏠 HOME: Redirecionando para login")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("🔑 LOGIN: Função chamada")
    print(f"   Método: {request.method}")
    
    if request.method == 'POST':
        print("   📝 POST detectado - processando dados...")
        
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            print(f"   Username: '{username}'")
            print(f"   Password: '{password}'")
            
            if not username or not password:
                print("   ❌ Campos vazios")
                flash('Preencha todos os campos!', 'error')
                return render_template('login_clean.html')
            
            print("   🔍 Consultando banco...")
            conn = get_db()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND active = 1', 
                               (username,)).fetchone()
            conn.close()
            
            print(f"   Usuário encontrado: {user is not None}")
            
            if user:
                print("   🔐 Verificando senha...")
                password_ok = check_password_hash(user['password'], password)
                print(f"   Senha OK: {password_ok}")
                
                if password_ok:
                    print("   ✅ LOGIN SUCESSO!")
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['user_role'] = user['role']
                    
                    flash('Login realizado com sucesso!', 'success')
                    print("   🔄 Redirecionando...")
                    return redirect(url_for('dashboard'))
                else:
                    print("   ❌ Senha incorreta")
                    flash('Senha incorreta!', 'error')
            else:
                print("   ❌ Usuário não encontrado")
                flash('Usuário não encontrado!', 'error')
                
        except Exception as e:
            print(f"   💥 ERRO: {e}")
            flash(f'Erro: {str(e)}', 'error')
    
    print("   📄 Renderizando login...")
    return render_template('login_clean.html')

@app.route('/dashboard')
def dashboard():
    print(f"📊 DASHBOARD: user_id={session.get('user_id')}")
    
    if 'user_id' not in session:
        print("   ❌ Não logado - redirecionando")
        return redirect(url_for('login'))
    
    # Retorno simples em texto puro para teste
    return f"""
    <h1>DASHBOARD CLIVER SEGUROS</h1>
    <p>Bem-vindo, {session.get('username')}!</p>
    <p>User ID: {session.get('user_id')}</p>
    <p><a href="/logout">Logout</a></p>
    """

@app.route('/logout')
def logout():
    print("🚪 LOGOUT")
    session.clear()
    flash('Logout realizado!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🧪 SERVIDOR DE TESTE MÍNIMO")
    print("🔑 Testando apenas login/dashboard")
    print("🌐 http://localhost:5005")
    app.run(host='0.0.0.0', port=5005, debug=True)