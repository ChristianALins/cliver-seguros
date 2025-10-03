from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyodbc
from datetime import datetime, date
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = 'cliver_seguros_2025_secret_key'

# Configuração do banco de dados
DATABASE_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost\\SQLEXPRESS',  # Ajuste conforme sua configuração
    'database': 'CorretoraSeguros',
    'trusted_connection': 'yes'
}

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    conn_str = (
        f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={DATABASE_CONFIG['database']};"
        f"Trusted_Connection={DATABASE_CONFIG['trusted_connection']}"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

def login_required(f):
    """Decorator para exigir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para exigir nível administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('nivel_acesso') != 'ADMINISTRADOR':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# AUTENTICAÇÃO E AUTORIZAÇÃO
# ============================================

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        conn = get_db_connection()
        if not conn:
            flash('Erro de conexão com o banco de dados', 'error')
            return render_template('login.html')
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_colaborador, nome, email, cargo, nivel_acesso, ativo
            FROM colaboradores 
            WHERE usuario = ? AND senha = ? AND ativo = 1
        """, (usuario, senha))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = usuario
            session['nome'] = user[1]
            session['email'] = user[2]
            session['cargo'] = user[3]
            session['nivel_acesso'] = user[4]
            
            flash(f'Bem-vindo, {user[1]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Logout realizado com sucesso', 'info')
    return redirect(url_for('login'))

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal com métricas importantes"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('dashboard.html')
    
    cursor = conn.cursor()
    
    # Métricas gerais
    metrics = {}
    
    # Total de clientes ativos
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE ativo = 1")
    metrics['total_clientes'] = cursor.fetchone()[0]
    
    # Total de apólices ativas
    cursor.execute("SELECT COUNT(*) FROM apolices WHERE status_apolice = 'ATIVA'")
    metrics['total_apolices_ativas'] = cursor.fetchone()[0]
    
    # Apólices próximas ao vencimento (30 dias)
    cursor.execute("""
        SELECT COUNT(*) FROM apolices 
        WHERE status_apolice = 'ATIVA' 
        AND data_fim_vigencia BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
    """)
    metrics['apolices_vencimento'] = cursor.fetchone()[0]
    
    # Tarefas pendentes do usuário ou todas (se admin)
    if session.get('nivel_acesso') == 'ADMINISTRADOR':
        cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'PENDENTE'")
    else:
        cursor.execute("SELECT COUNT(*) FROM tarefas WHERE status = 'PENDENTE' AND id_colaborador = ?", (session['user_id'],))
    metrics['tarefas_pendentes'] = cursor.fetchone()[0]
    
    # Sinistros em aberto
    cursor.execute("SELECT COUNT(*) FROM sinistros WHERE status_sinistro IN ('ABERTO', 'EM_ANALISE')")
    metrics['sinistros_abertos'] = cursor.fetchone()[0]
    
    # Receita total do mês atual
    cursor.execute("""
        SELECT ISNULL(SUM(valor_premio), 0) 
        FROM apolices 
        WHERE YEAR(data_inicio_vigencia) = YEAR(GETDATE()) 
        AND MONTH(data_inicio_vigencia) = MONTH(GETDATE())
        AND status_apolice = 'ATIVA'
    """)
    metrics['receita_mes'] = cursor.fetchone()[0]
    
    # Comissões do mês atual
    cursor.execute("""
        SELECT ISNULL(SUM(valor_comissao), 0) 
        FROM apolices 
        WHERE YEAR(data_inicio_vigencia) = YEAR(GETDATE()) 
        AND MONTH(data_inicio_vigencia) = MONTH(GETDATE())
        AND status_apolice = 'ATIVA'
    """)
    metrics['comissoes_mes'] = cursor.fetchone()[0]
    
    # Últimas atividades (tarefas recentes)
    if session.get('nivel_acesso') == 'ADMINISTRADOR':
        cursor.execute("""
            SELECT TOP 5 t.titulo, t.data_vencimento, t.prioridade, c.nome_completo as cliente, col.nome as responsavel
            FROM tarefas t
            LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
            LEFT JOIN colaboradores col ON t.id_colaborador = col.id_colaborador
            WHERE t.status = 'PENDENTE'
            ORDER BY t.data_vencimento ASC
        """)
    else:
        cursor.execute("""
            SELECT TOP 5 t.titulo, t.data_vencimento, t.prioridade, c.nome_completo as cliente
            FROM tarefas t
            LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
            WHERE t.status = 'PENDENTE' AND t.id_colaborador = ?
            ORDER BY t.data_vencimento ASC
        """, (session['user_id'],))
    
    atividades_recentes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('dashboard.html', metrics=metrics, atividades=atividades_recentes)

# ============================================
# GESTÃO DE CLIENTES
# ============================================

@app.route('/clientes')
@login_required
def clientes():
    """Lista todos os clientes"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('clientes.html', clientes=[])
    
    cursor = conn.cursor()
    
    # Filtros de pesquisa
    search = request.args.get('search', '')
    
    if search:
        cursor.execute("""
            SELECT c.id_cliente, c.nome_completo, c.cpf_cnpj, c.telefone, c.email, 
                   c.cidade, c.estado, c.ativo, col.nome as responsavel,
                   COUNT(a.id_apolice) as total_apolices,
                   ISNULL(SUM(CASE WHEN a.status_apolice = 'ATIVA' THEN a.valor_premio ELSE 0 END), 0) as valor_total
            FROM clientes c
            LEFT JOIN colaboradores col ON c.id_colaborador_responsavel = col.id_colaborador
            LEFT JOIN apolices a ON c.id_cliente = a.id_cliente
            WHERE (c.nome_completo LIKE ? OR c.cpf_cnpj LIKE ? OR c.email LIKE ?)
            GROUP BY c.id_cliente, c.nome_completo, c.cpf_cnpj, c.telefone, c.email, 
                     c.cidade, c.estado, c.ativo, col.nome
            ORDER BY c.nome_completo
        """, (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cursor.execute("""
            SELECT c.id_cliente, c.nome_completo, c.cpf_cnpj, c.telefone, c.email, 
                   c.cidade, c.estado, c.ativo, col.nome as responsavel,
                   COUNT(a.id_apolice) as total_apolices,
                   ISNULL(SUM(CASE WHEN a.status_apolice = 'ATIVA' THEN a.valor_premio ELSE 0 END), 0) as valor_total
            FROM clientes c
            LEFT JOIN colaboradores col ON c.id_colaborador_responsavel = col.id_colaborador
            LEFT JOIN apolices a ON c.id_cliente = a.id_cliente
            GROUP BY c.id_cliente, c.nome_completo, c.cpf_cnpj, c.telefone, c.email, 
                     c.cidade, c.estado, c.ativo, col.nome
            ORDER BY c.nome_completo
        """)
    
    clientes_list = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('clientes.html', clientes=clientes_list, search=search)

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    """Cadastrar novo cliente"""
    if request.method == 'POST':
        data = request.form
        
        conn = get_db_connection()
        if not conn:
            flash('Erro de conexão com o banco de dados', 'error')
            return render_template('cliente_form.html')
        
        cursor = conn.cursor()
        
        try:
            # Processar data de nascimento se fornecida
            data_nascimento = None
            if data.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').strftime('%Y-%m-%d')
                except:
                    data_nascimento = None
            
            cursor.execute("""
                INSERT INTO clientes (nome_completo, cpf_cnpj, tipo_pessoa, data_nascimento, 
                                    telefone, email, endereco, cidade, estado, cep, observacoes, 
                                    id_colaborador_responsavel, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                data['nome_completo'], data['cpf_cnpj'], data['tipo_pessoa'], data_nascimento,
                data['telefone'], data['email'], data['endereco'], data['cidade'], 
                data['estado'], data['cep'], data['observacoes'], 
                session['user_id']  # Usuário logado como responsável
            ))
            
            conn.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao cadastrar cliente: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('cliente_form.html')

@app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    """Editar dados do cliente"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('clientes'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.form
        
        try:
            # Processar data de nascimento se fornecida
            data_nascimento = None
            if data.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').strftime('%Y-%m-%d')
                except:
                    data_nascimento = None
            
            cursor.execute("""
                UPDATE clientes SET nome_completo = ?, cpf_cnpj = ?, tipo_pessoa = ?, 
                                  data_nascimento = ?, telefone = ?, email = ?, endereco = ?, 
                                  cidade = ?, estado = ?, cep = ?, observacoes = ?
                WHERE id_cliente = ?
            """, (
                data['nome_completo'], data['cpf_cnpj'], data['tipo_pessoa'], data_nascimento,
                data['telefone'], data['email'], data['endereco'], data['cidade'], 
                data['estado'], data['cep'], data['observacoes'], id
            ))
            
            conn.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('clientes'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao atualizar cliente: {str(e)}', 'error')
    
    # Buscar dados do cliente
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id,))
    cliente = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    conn.close()
    
    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/<int:id>/detalhes')
@login_required
def detalhes_cliente(id):
    """Visualizar detalhes completos do cliente"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('clientes'))
    
    cursor = conn.cursor()
    
    # Dados do cliente
    cursor.execute("""
        SELECT c.*, col.nome as responsavel_nome
        FROM clientes c
        LEFT JOIN colaboradores col ON c.id_colaborador_responsavel = col.id_colaborador
        WHERE c.id_cliente = ?
    """, (id,))
    cliente = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    # Apólices do cliente
    cursor.execute("""
        SELECT a.*, s.nome as seguradora_nome, ts.nome as tipo_seguro_nome, 
               col.nome as corretor_nome
        FROM apolices a
        LEFT JOIN seguradoras s ON a.id_seguradora = s.id_seguradora
        LEFT JOIN tipos_seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        LEFT JOIN colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE a.id_cliente = ?
        ORDER BY a.data_inicio_vigencia DESC
    """, (id,))
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Tarefas relacionadas ao cliente
    cursor.execute("""
        SELECT t.*, col.nome as responsavel_nome
        FROM tarefas t
        LEFT JOIN colaboradores col ON t.id_colaborador = col.id_colaborador
        WHERE t.id_cliente = ?
        ORDER BY t.data_vencimento DESC
    """, (id,))
    tarefas = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('cliente_detalhes.html', cliente=cliente, apolices=apolices, tarefas=tarefas)

# ============================================
# GESTÃO DE SEGURADORAS
# ============================================

@app.route('/seguradoras')
@login_required
def seguradoras():
    """Lista todas as seguradoras"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('seguradoras.html', seguradoras=[])
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, 
               COUNT(a.id_apolice) as total_apolices,
               ISNULL(SUM(CASE WHEN a.status_apolice = 'ATIVA' THEN a.valor_premio ELSE 0 END), 0) as receita_total
        FROM seguradoras s
        LEFT JOIN apolices a ON s.id_seguradora = a.id_seguradora
        GROUP BY s.id_seguradora, s.nome, s.cnpj, s.telefone, s.email, s.site, 
                 s.endereco, s.contato_comercial, s.percentual_comissao_padrao, s.ativa, s.data_criacao
        ORDER BY s.nome
    """)
    
    seguradoras_list = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('seguradoras.html', seguradoras=seguradoras_list)

@app.route('/seguradoras/nova', methods=['GET', 'POST'])
@login_required
def nova_seguradora():
    """Cadastrar nova seguradora"""
    if request.method == 'POST':
        data = request.form
        
        conn = get_db_connection()
        if not conn:
            flash('Erro de conexão com o banco de dados', 'error')
            return render_template('seguradora_form.html')
        
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO seguradoras (nome, cnpj, telefone, email, site, endereco, 
                                       contato_comercial, percentual_comissao_padrao, ativa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                data['nome'], data['cnpj'], data['telefone'], data['email'],
                data['site'], data['endereco'], data['contato_comercial'],
                float(data['percentual_comissao_padrao'])
            ))
            
            conn.commit()
            flash('Seguradora cadastrada com sucesso!', 'success')
            return redirect(url_for('seguradoras'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao cadastrar seguradora: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('seguradora_form.html')

# ============================================
# GESTÃO DE APÓLICES
# ============================================

@app.route('/apolices')
@login_required
def apolices():
    """Lista apólices com filtros baseados no nível de acesso"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('apolices.html', apolices=[])
    
    cursor = conn.cursor()
    
    # Filtros
    status_filter = request.args.get('status', '')
    cliente_filter = request.args.get('cliente', '')
    
    # Base da query
    base_query = """
        SELECT a.*, c.nome_completo as cliente_nome, s.nome as seguradora_nome, 
               ts.nome as tipo_seguro_nome, col.nome as corretor_nome,
               DATEDIFF(day, GETDATE(), a.data_fim_vigencia) as dias_vencimento
        FROM apolices a
        LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN seguradoras s ON a.id_seguradora = s.id_seguradora
        LEFT JOIN tipos_seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        LEFT JOIN colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE 1=1
    """
    
    params = []
    
    # Filtro por nível de acesso
    if session.get('nivel_acesso') == 'CORRETOR':
        base_query += " AND a.id_colaborador = ?"
        params.append(session['user_id'])
    
    # Filtros adicionais
    if status_filter:
        base_query += " AND a.status_apolice = ?"
        params.append(status_filter)
    
    if cliente_filter:
        base_query += " AND c.nome_completo LIKE ?"
        params.append(f'%{cliente_filter}%')
    
    base_query += " ORDER BY a.data_inicio_vigencia DESC"
    
    cursor.execute(base_query, params)
    apolices_list = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('apolices.html', apolices=apolices_list, 
                         status_filter=status_filter, cliente_filter=cliente_filter)

@app.route('/apolices/nova', methods=['GET', 'POST'])
@login_required
def nova_apolice():
    """Cadastrar nova apólice"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('apolices'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.form
        
        try:
            # Calcular valor da comissão
            valor_premio = float(data['valor_premio'])
            percentual_comissao = float(data['percentual_comissao'])
            valor_comissao = (valor_premio * percentual_comissao) / 100
            
            cursor.execute("""
                INSERT INTO apolices (numero_apolice, id_cliente, id_seguradora, id_tipo_seguro, 
                                    id_colaborador, valor_premio, percentual_comissao, valor_comissao, 
                                    data_inicio_vigencia, data_fim_vigencia, status_apolice, 
                                    forma_pagamento, valor_franquia, observacoes, renovacao_automatica)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['numero_apolice'], int(data['id_cliente']), int(data['id_seguradora']),
                int(data['id_tipo_seguro']), session['user_id'], valor_premio,
                percentual_comissao, valor_comissao, data['data_inicio_vigencia'],
                data['data_fim_vigencia'], data['status_apolice'], data['forma_pagamento'],
                float(data['valor_franquia']) if data['valor_franquia'] else 0,
                data['observacoes'], 1 if data.get('renovacao_automatica') else 0
            ))
            
            conn.commit()
            flash('Apólice cadastrada com sucesso!', 'success')
            return redirect(url_for('apolices'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao cadastrar apólice: {str(e)}', 'error')
    
    # Buscar dados para os selects
    cursor.execute("SELECT id_cliente, nome_completo FROM clientes WHERE ativo = 1 ORDER BY nome_completo")
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_seguradora, nome FROM seguradoras WHERE ativa = 1 ORDER BY nome")
    seguradoras = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_tipo_seguro, nome FROM tipos_seguro WHERE ativo = 1 ORDER BY nome")
    tipos_seguro = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('apolice_form.html', clientes=clientes, 
                         seguradoras=seguradoras, tipos_seguro=tipos_seguro)

@app.route('/apolices/vencimento')
@login_required
def apolices_vencimento():
    """Relatório de apólices próximas ao vencimento"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('apolices_vencimento.html', apolices=[])
    
    cursor = conn.cursor()
    
    # Apólices que vencem nos próximos 60 dias
    query = """
        SELECT a.*, c.nome_completo as cliente_nome, c.telefone as cliente_telefone,
               c.email as cliente_email, s.nome as seguradora_nome, 
               ts.nome as tipo_seguro_nome, col.nome as corretor_nome,
               DATEDIFF(day, GETDATE(), a.data_fim_vigencia) as dias_vencimento
        FROM apolices a
        LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN seguradoras s ON a.id_seguradora = s.id_seguradora
        LEFT JOIN tipos_seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        LEFT JOIN colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE a.status_apolice = 'ATIVA' 
        AND a.data_fim_vigencia BETWEEN GETDATE() AND DATEADD(day, 60, GETDATE())
    """
    
    # Filtrar por corretor se não for admin
    if session.get('nivel_acesso') == 'CORRETOR':
        query += " AND a.id_colaborador = ?"
        cursor.execute(query + " ORDER BY a.data_fim_vigencia", (session['user_id'],))
    else:
        cursor.execute(query + " ORDER BY a.data_fim_vigencia")
    
    apolices_list = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('apolices_vencimento.html', apolices=apolices_list)

# ============================================
# GESTÃO DE SINISTROS
# ============================================

@app.route('/sinistros')
@login_required
def sinistros():
    """Lista todos os sinistros"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('sinistros.html', sinistros=[])
    
    cursor = conn.cursor()
    
    # Filtros
    status_filter = request.args.get('status', '')
    
    query = """
        SELECT s.*, a.numero_apolice, c.nome_completo as cliente_nome,
               seg.nome as seguradora_nome, ts.nome as tipo_seguro_nome,
               col.nome as corretor_nome
        FROM sinistros s
        LEFT JOIN apolices a ON s.id_apolice = a.id_apolice
        LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN seguradoras seg ON a.id_seguradora = seg.id_seguradora
        LEFT JOIN tipos_seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        LEFT JOIN colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE 1=1
    """
    
    params = []
    
    # Filtrar por corretor se necessário
    if session.get('nivel_acesso') == 'CORRETOR':
        query += " AND a.id_colaborador = ?"
        params.append(session['user_id'])
    
    if status_filter:
        query += " AND s.status_sinistro = ?"
        params.append(status_filter)
    
    query += " ORDER BY s.data_ocorrencia DESC"
    
    cursor.execute(query, params)
    sinistros_list = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('sinistros.html', sinistros=sinistros_list, status_filter=status_filter)

@app.route('/sinistros/novo', methods=['GET', 'POST'])
@login_required
def novo_sinistro():
    """Cadastrar novo sinistro"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('sinistros'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.form
        
        try:
            cursor.execute("""
                INSERT INTO sinistros (numero_sinistro, id_apolice, data_ocorrencia, descricao, 
                                     tipo_sinistro, local_ocorrencia, valor_reclamado, 
                                     status_sinistro, responsavel_analise, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['numero_sinistro'], int(data['id_apolice']), data['data_ocorrencia'],
                data['descricao'], data['tipo_sinistro'], data['local_ocorrencia'],
                float(data['valor_reclamado']) if data['valor_reclamado'] else 0,
                data['status_sinistro'], data['responsavel_analise'], data['observacoes']
            ))
            
            conn.commit()
            flash('Sinistro cadastrado com sucesso!', 'success')
            return redirect(url_for('sinistros'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao cadastrar sinistro: {str(e)}', 'error')
    
    # Buscar apólices ativas para o select
    if session.get('nivel_acesso') == 'CORRETOR':
        cursor.execute("""
            SELECT a.id_apolice, a.numero_apolice, c.nome_completo as cliente_nome
            FROM apolices a
            LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
            WHERE a.status_apolice = 'ATIVA' AND a.id_colaborador = ?
            ORDER BY a.numero_apolice
        """, (session['user_id'],))
    else:
        cursor.execute("""
            SELECT a.id_apolice, a.numero_apolice, c.nome_completo as cliente_nome
            FROM apolices a
            LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
            WHERE a.status_apolice = 'ATIVA'
            ORDER BY a.numero_apolice
        """)
    
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('sinistro_form.html', apolices=apolices)

# ============================================
# GESTÃO DE TAREFAS
# ============================================

@app.route('/tarefas')
@login_required
def tarefas():
    """Lista tarefas do usuário ou todas (se admin)"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('tarefas.html', tarefas=[])
    
    cursor = conn.cursor()
    
    # Filtros
    status_filter = request.args.get('status', '')
    prioridade_filter = request.args.get('prioridade', '')
    
    query = """
        SELECT t.*, c.nome_completo as cliente_nome, col.nome as responsavel_nome,
               a.numero_apolice
        FROM tarefas t
        LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
        LEFT JOIN colaboradores col ON t.id_colaborador = col.id_colaborador
        LEFT JOIN apolices a ON t.id_apolice = a.id_apolice
        WHERE 1=1
    """
    
    params = []
    
    # Filtrar por usuário se não for admin
    if session.get('nivel_acesso') != 'ADMINISTRADOR':
        query += " AND t.id_colaborador = ?"
        params.append(session['user_id'])
    
    if status_filter:
        query += " AND t.status = ?"
        params.append(status_filter)
    
    if prioridade_filter:
        query += " AND t.prioridade = ?"
        params.append(prioridade_filter)
    
    query += " ORDER BY t.data_vencimento ASC"
    
    cursor.execute(query, params)
    tarefas_list = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('tarefas.html', tarefas=tarefas_list, 
                         status_filter=status_filter, prioridade_filter=prioridade_filter)

@app.route('/tarefas/nova', methods=['GET', 'POST'])
@login_required
def nova_tarefa():
    """Cadastrar nova tarefa"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('tarefas'))
    
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.form
        
        try:
            # Processar data de vencimento
            data_vencimento = None
            if data.get('data_vencimento'):
                try:
                    data_vencimento = datetime.strptime(data.get('data_vencimento'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
                except:
                    data_vencimento = None
            
            cursor.execute("""
                INSERT INTO tarefas (titulo, descricao, tipo_tarefa, id_cliente, id_colaborador, 
                                   id_apolice, data_vencimento, status, prioridade, resultado, proxima_acao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['titulo'], data['descricao'], data['tipo_tarefa'],
                int(data['id_cliente']) if data.get('id_cliente') else None,
                session['user_id'], 
                int(data['id_apolice']) if data.get('id_apolice') else None,
                data_vencimento, data['status'], data['prioridade'],
                data['resultado'], data['proxima_acao']
            ))
            
            conn.commit()
            flash('Tarefa cadastrada com sucesso!', 'success')
            return redirect(url_for('tarefas'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao cadastrar tarefa: {str(e)}', 'error')
    
    # Buscar dados para os selects
    cursor.execute("SELECT id_cliente, nome_completo FROM clientes WHERE ativo = 1 ORDER BY nome_completo")
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    if session.get('nivel_acesso') == 'CORRETOR':
        cursor.execute("""
            SELECT a.id_apolice, a.numero_apolice, c.nome_completo as cliente_nome
            FROM apolices a
            LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
            WHERE a.status_apolice = 'ATIVA' AND a.id_colaborador = ?
            ORDER BY a.numero_apolice
        """, (session['user_id'],))
    else:
        cursor.execute("""
            SELECT a.id_apolice, a.numero_apolice, c.nome_completo as cliente_nome
            FROM apolices a
            LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
            WHERE a.status_apolice = 'ATIVA'
            ORDER BY a.numero_apolice
        """)
    
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('tarefa_form.html', clientes=clientes, apolices=apolices)

@app.route('/tarefas/<int:id>/concluir', methods=['POST'])
@login_required
def concluir_tarefa(id):
    """Marcar tarefa como concluída"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return redirect(url_for('tarefas'))
    
    cursor = conn.cursor()
    
    try:
        resultado = request.form.get('resultado', '')
        proxima_acao = request.form.get('proxima_acao', '')
        
        cursor.execute("""
            UPDATE tarefas 
            SET status = 'CONCLUIDA', data_conclusao = GETDATE(), 
                resultado = ?, proxima_acao = ?
            WHERE id_tarefa = ? AND id_colaborador = ?
        """, (resultado, proxima_acao, id, session['user_id']))
        
        conn.commit()
        flash('Tarefa concluída com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao concluir tarefa: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('tarefas'))

# ============================================
# RELATÓRIOS
# ============================================

@app.route('/relatorios')
@login_required
def relatorios():
    """Página principal de relatórios"""
    return render_template('relatorios.html')

@app.route('/relatorios/comissoes')
@login_required
def relatorio_comissoes():
    """Relatório de comissões por colaborador"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('relatorio_comissoes.html', dados=[])
    
    cursor = conn.cursor()
    
    # Filtros de período
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    
    if not data_inicio:
        data_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not data_fim:
        data_fim = datetime.now().strftime('%Y-%m-%d')
    
    query = """
        SELECT col.nome as colaborador, col.cargo, col.percentual_comissao as comissao_base,
               COUNT(a.id_apolice) as total_apolices,
               SUM(a.valor_premio) as receita_total,
               SUM(a.valor_comissao) as comissoes_corretora,
               SUM(a.valor_comissao * col.percentual_comissao / 100) as comissoes_colaborador
        FROM colaboradores col
        LEFT JOIN apolices a ON col.id_colaborador = a.id_colaborador 
                              AND a.data_inicio_vigencia BETWEEN ? AND ?
                              AND a.status_apolice = 'ATIVA'
        WHERE col.ativo = 1 AND col.nivel_acesso IN ('CORRETOR', 'GERENTE')
        GROUP BY col.id_colaborador, col.nome, col.cargo, col.percentual_comissao
        ORDER BY comissoes_colaborador DESC
    """
    
    cursor.execute(query, (data_inicio, data_fim))
    dados = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('relatorio_comissoes.html', dados=dados, 
                         data_inicio=data_inicio, data_fim=data_fim)

# ============================================
# API ENDPOINTS (Para AJAX)
# ============================================

@app.route('/api/cliente/<int:id>/apolices')
@login_required
def api_cliente_apolices(id):
    """API para buscar apólices de um cliente específico"""
    conn = get_db_connection()
    if not conn:
        return jsonify([])
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id_apolice, a.numero_apolice, s.nome as seguradora, 
               ts.nome as tipo_seguro, a.status_apolice
        FROM apolices a
        LEFT JOIN seguradoras s ON a.id_seguradora = s.id_seguradora
        LEFT JOIN tipos_seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        WHERE a.id_cliente = ? AND a.status_apolice = 'ATIVA'
        ORDER BY a.data_inicio_vigencia DESC
    """, (id,))
    
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(apolices)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def format_currency(value):
    """Formatar valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(date_value):
    """Formatar data para exibição"""
    if isinstance(date_value, str):
        try:
            date_value = datetime.strptime(date_value, '%Y-%m-%d')
        except:
            return date_value
    return date_value.strftime('%d/%m/%Y') if date_value else ''

def format_datetime(datetime_value):
    """Formatar data e hora para exibição"""
    if isinstance(datetime_value, str):
        try:
            datetime_value = datetime.strptime(datetime_value, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime_value
    return datetime_value.strftime('%d/%m/%Y %H:%M') if datetime_value else ''

# Registrar filtros no Jinja2
app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['date'] = format_date
app.jinja_env.filters['datetime'] = format_datetime

if __name__ == '__main__':
    print("🚀 Iniciando Sistema CLIVER Seguros...")
    print("📊 Dashboard: http://127.0.0.1:5000/dashboard")
    print("🔑 Login: http://127.0.0.1:5000/login")
    print("")
    print("👥 Usuários disponíveis:")
    print("   admin/admin (Administrador)")
    print("   joao/joao123 (Gerente)")
    print("   maria/maria123 (Corretora Senior)")
    print("   pedro/pedro123 (Corretor Junior)")
    print("")
    app.run(debug=True, host='0.0.0.0', port=5000)