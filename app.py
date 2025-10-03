from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyodbc
from datetime import datetime, date
from functools import wraps

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
def nova_seguradora():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Seguradoras (nome_seguradora, cnpj_seguradora, contato_seguradora, email_seguradora) VALUES (?, ?, ?, ?)',
            (
                data['nome_seguradora'],
                data['cnpj_seguradora'],
                data.get('contato_seguradora'),
                data.get('email_seguradora')
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('seguradoras'))
    return render_template('seguradora_form.html', seguradora=None)

@app.route('/seguradoras/editar/<int:id>', methods=['GET', 'POST'])
def editar_seguradora(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            'UPDATE Seguradoras SET nome_seguradora=?, cnpj_seguradora=?, contato_seguradora=?, email_seguradora=? WHERE id_seguradora=?',
            (
                data['nome_seguradora'],
                data['cnpj_seguradora'],
                data.get('contato_seguradora'),
                data.get('email_seguradora'),
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('seguradoras'))
    cursor.execute('SELECT * FROM Seguradoras WHERE id_seguradora=?', (id,))
    row = cursor.fetchone()
    seguradora = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('seguradora_form.html', seguradora=seguradora)

# Rota para dashboard principal
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Estatísticas gerais
    stats = {}
    
    # Total de clientes
    cursor.execute('SELECT COUNT(*) FROM Clientes')
    stats['total_clientes'] = cursor.fetchone()[0]
    
    # Total de apólices
    cursor.execute('SELECT COUNT(*) FROM Apolices')
    stats['total_apolices'] = cursor.fetchone()[0]
    
    # Total de sinistros
    cursor.execute('SELECT COUNT(*) FROM Sinistros')
    stats['total_sinistros'] = cursor.fetchone()[0]
    
    # Apólices ativas
    cursor.execute("SELECT COUNT(*) FROM Apolices WHERE status_apolice = 'Ativa'")
    stats['apolices_ativas'] = cursor.fetchone()[0]
    
    # Valor total de prêmios
    cursor.execute('SELECT ISNULL(SUM(valor_premio), 0) FROM Apolices WHERE status_apolice = \'Ativa\'')
    stats['valor_total_premios'] = cursor.fetchone()[0]
    
    # Gráfico de apólices por tipo de seguro
    cursor.execute('''
        SELECT ts.nome_tipo_seguro, COUNT(a.id_apolice) as total
        FROM Tipos_Seguro ts
        LEFT JOIN Apolices a ON ts.id_tipo_seguro = a.id_tipo_seguro
        GROUP BY ts.nome_tipo_seguro, ts.id_tipo_seguro
        ORDER BY total DESC
    ''')
    apolices_por_tipo = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Gráfico de sinistros por status
    cursor.execute('''
        SELECT status_sinistro, COUNT(*) as total
        FROM Sinistros
        GROUP BY status_sinistro
    ''')
    sinistros_por_status = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Apólices recentes
    cursor.execute('''
        SELECT TOP 5 a.numero_apolice, c.nome, s.nome_seguradora, a.valor_premio, a.data_inicio_vigencia
        FROM Apolices a
        JOIN Clientes c ON a.id_cliente = c.id_cliente
        JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
        ORDER BY a.id_apolice DESC
    ''')
    apolices_recentes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         apolices_por_tipo=apolices_por_tipo,
                         sinistros_por_status=sinistros_por_status,
                         apolices_recentes=apolices_recentes)

# Rotas para Tipos de Seguro
@app.route('/tipos_seguro')
def tipos_seguro():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_tipo_seguro, nome_tipo_seguro, descricao_tipo_seguro FROM Tipos_Seguro')
    tipos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template('tipos_seguro.html', tipos_seguro=tipos)

@app.route('/tipos_seguro/novo', methods=['GET', 'POST'])
def novo_tipo_seguro():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se o tipo de seguro já existe
        cursor.execute(
            'SELECT COUNT(*) FROM Tipos_Seguro WHERE nome_tipo_seguro = ?',
            (data['nome_tipo_seguro'],)
        )
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            flash('Erro: Já existe um tipo de seguro com este nome!', 'error')
            return render_template('tipo_seguro_form.html', tipo_seguro=None, error='Tipo de seguro já existe')
        
        try:
            cursor.execute(
                'INSERT INTO Tipos_Seguro (nome_tipo_seguro, descricao_tipo_seguro) VALUES (?, ?)',
                (data['nome_tipo_seguro'], data.get('descricao_tipo_seguro'))
            )
            conn.commit()
            flash('Tipo de seguro criado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao criar tipo de seguro: {str(e)}', 'error')
            return render_template('tipo_seguro_form.html', tipo_seguro=None, error=str(e))
        finally:
            conn.close()
            
        return redirect(url_for('tipos_seguro'))
    return render_template('tipo_seguro_form.html', tipo_seguro=None)

@app.route('/tipos_seguro/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_seguro(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            'UPDATE Tipos_Seguro SET nome_tipo_seguro=?, descricao_tipo_seguro=? WHERE id_tipo_seguro=?',
            (data['nome_tipo_seguro'], data.get('descricao_tipo_seguro'), id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('tipos_seguro'))
    cursor.execute('SELECT * FROM Tipos_Seguro WHERE id_tipo_seguro=?', (id,))
    row = cursor.fetchone()
    tipo_seguro = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('tipo_seguro_form.html', tipo_seguro=tipo_seguro)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Credenciais de demonstração (remover em produção)
            if username == 'admin' and password == 'admin':
                session['user_id'] = 1
                session['username'] = 'Administrador'
                session['role'] = 'admin'
                flash('Bem-vindo(a) ao sistema CLIVER!', 'success')
                return redirect(url_for('dashboard'))
            elif username == 'demo' and password == 'demo':
                session['user_id'] = 2
                session['username'] = 'Usuario Demo'
                session['role'] = 'user'
                flash('Bem-vindo(a) ao sistema CLIVER!', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Tentar autenticar pela tabela Colaboradores
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                            SELECT id_colaborador, nome_colaborador, cargo 
                            FROM Colaboradores 
                            WHERE email_colaborador = ? AND status = 'Ativo'
                        ''', (username,))
                        
                        colaborador = cursor.fetchone()
                        conn.close()
                        
                        if colaborador:
                            # Verificação simples de senha (melhorar em produção)
                            if password == 'cliver2025' or password == colaborador[1].split()[0].lower():
                                session['user_id'] = colaborador[0]
                                session['username'] = colaborador[1]
                                session['role'] = get_role_from_cargo(colaborador[2])
                                flash(f'Bem-vindo(a), {colaborador[1]}!', 'success')
                                return redirect(url_for('dashboard'))
                        
                        flash('Credenciais inválidas!', 'error')
                    else:
                        flash('Erro na conexão com banco de dados. Use: admin/admin ou demo/demo', 'warning')
                except Exception as db_error:
                    flash('Banco indisponível. Use: admin/admin para acesso administrativo ou demo/demo para acesso limitado.', 'warning')
                    
        except Exception as e:
            flash(f'Erro no sistema: Use credenciais temporárias - admin/admin', 'error')
    
    return render_template('login.html')

def get_role_from_cargo(cargo):
    """Converte cargo em role para controle de acesso"""
    cargo_lower = cargo.lower() if cargo else ''
    
    if 'sócio' in cargo_lower or 'administrador' in cargo_lower or 'gerente' in cargo_lower:
        return 'admin'
    elif 'corretor' in cargo_lower:
        return 'corretor'
    else:
        return 'usuario'

def requires_role(required_role):
    """Decorator para controle de acesso por role"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))
            
            user_role = session.get('role', 'usuario')
            
            # Hierarquia de permissões: admin > corretor > usuario
            role_hierarchy = {'admin': 3, 'corretor': 2, 'usuario': 1}
            required_level = role_hierarchy.get(required_role, 1)
            user_level = role_hierarchy.get(user_role, 1)
            
            if user_level < required_level:
                flash('Acesso negado! Você não tem permissão para acessar esta funcionalidade.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Dashboard do Banco de Dados
@app.route('/banco')
def banco_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('banco_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rotas de Clientes
@app.route('/clientes')
def clientes():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Parâmetros de pesquisa e filtros
    busca = request.args.get('busca', '').strip()
    tipo_pessoa = request.args.get('tipo_pessoa', '')
    cidade = request.args.get('cidade', '')
    ordenar = request.args.get('ordenar', 'nome')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query base com filtros dinâmicos
    base_query = '''
    SELECT 
        c.id_cliente, 
        c.nome, 
        c.tipo_pessoa, 
        c.documento, 
        c.email, 
        c.telefone, 
        c.cidade,
        c.estado,
        c.data_cadastro,
        COUNT(a.id_apolice) as total_apolices,
        SUM(CASE WHEN a.status_apolice = 'Ativa' THEN a.valor_premio ELSE 0 END) as valor_total_apolices
    FROM Clientes c
    LEFT JOIN Apolices a ON c.id_cliente = a.id_cliente
    WHERE 1=1
    '''
    
    params = []
    
    # Filtro de busca (nome ou documento)
    if busca:
        base_query += ' AND (c.nome LIKE ? OR c.documento LIKE ?)'
        params.extend([f'%{busca}%', f'%{busca}%'])
    
    # Filtro por tipo de pessoa
    if tipo_pessoa:
        base_query += ' AND c.tipo_pessoa = ?'
        params.append(tipo_pessoa)
    
    # Filtro por cidade
    if cidade:
        base_query += ' AND c.cidade = ?'
        params.append(cidade)
    
    base_query += ' GROUP BY c.id_cliente, c.nome, c.tipo_pessoa, c.documento, c.email, c.telefone, c.cidade, c.estado, c.data_cadastro'
    
    # Ordenação
    if ordenar == 'nome':
        base_query += ' ORDER BY c.nome'
    elif ordenar == 'data_cadastro':
        base_query += ' ORDER BY c.data_cadastro DESC'
    elif ordenar == 'total_apolices':
        base_query += ' ORDER BY total_apolices DESC'
    elif ordenar == 'valor_total':
        base_query += ' ORDER BY valor_total_apolices DESC'
    else:
        base_query += ' ORDER BY c.nome'
    
    cursor.execute(base_query, params)
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Estatísticas para dashboard
    stats_query = '''
    SELECT 
        COUNT(*) as total_clientes,
        COUNT(CASE WHEN tipo_pessoa = 'Fisica' THEN 1 END) as pessoas_fisicas,
        COUNT(CASE WHEN tipo_pessoa = 'Juridica' THEN 1 END) as pessoas_juridicas,
        COUNT(DISTINCT cidade) as total_cidades
    FROM Clientes
    '''
    
    if busca or tipo_pessoa or cidade:
        # Se há filtros, calcular stats apenas dos resultados filtrados
        stats_params = []
        stats_query = 'SELECT COUNT(*) as total_clientes FROM Clientes WHERE 1=1'
        
        if busca:
            stats_query += ' AND (nome LIKE ? OR documento LIKE ?)'
            stats_params.extend([f'%{busca}%', f'%{busca}%'])
        
        if tipo_pessoa:
            stats_query += ' AND tipo_pessoa = ?'
            stats_params.append(tipo_pessoa)
        
        if cidade:
            stats_query += ' AND cidade = ?'
            stats_params.append(cidade)
        
        cursor.execute(stats_query, stats_params)
        result = cursor.fetchone()
        stats = {'total_clientes': result[0], 'pessoas_fisicas': 0, 'pessoas_juridicas': 0, 'total_cidades': 0}
    else:
        cursor.execute(stats_query)
        stats = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    # Lista de cidades para o filtro
    cursor.execute('SELECT DISTINCT cidade FROM Clientes WHERE cidade IS NOT NULL ORDER BY cidade')
    cidades = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('clientes.html', 
                         clientes=clientes, 
                         stats=stats,
                         cidades=cidades,
                         filtros={
                             'busca': busca,
                             'tipo_pessoa': tipo_pessoa,
                             'cidade': cidade,
                             'ordenar': ordenar
                         })

@app.route('/clientes/novo', methods=['GET', 'POST'])
def novo_cliente():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.form
        
        # Debug: verificar valor recebido
        print(f"DEBUG: tipo_pessoa recebido = '{data.get('tipo_pessoa')}'")
        
        # Validação do tipo_pessoa
        tipo_pessoa = data.get('tipo_pessoa')
        if tipo_pessoa not in ['Fisica', 'Juridica']:
            flash(f'Tipo de pessoa inválido: {tipo_pessoa}. Use "Fisica" ou "Juridica".')
            return redirect(url_for('novo_cliente'))
        
        try:
            # Processar data de nascimento
            data_nascimento = None
            if data.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').strftime('%Y-%m-%d')
                except:
                    data_nascimento = None
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Clientes (nome, tipo_pessoa, documento, data_nascimento, email, telefone, endereco, cidade, estado, cep) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    data['nome'],
                    tipo_pessoa,
                    data['documento'],
                    data_nascimento,
                    data.get('email'),
                    data.get('telefone'),
                    data.get('endereco'),
                    data.get('cidade'),
                    data.get('estado'),
                    data.get('cep')
                )
            )
            conn.commit()
        except Exception as e:
            flash(f'Erro ao salvar cliente: {str(e)}')
            conn.rollback()
            conn.close()
            return redirect(url_for('novo_cliente'))
        conn.close()
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', cliente=None)

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.form
        
        # Validação do tipo_pessoa
        tipo_pessoa = data.get('tipo_pessoa')
        if tipo_pessoa not in ['Fisica', 'Juridica']:
            flash(f'Tipo de pessoa inválido: {tipo_pessoa}. Use "Fisica" ou "Juridica".')
            return redirect(url_for('editar_cliente', id=id))
        
        try:
            # Processar data de nascimento
            data_nascimento = None
            if data.get('data_nascimento'):
                try:
                    data_nascimento = datetime.strptime(data.get('data_nascimento'), '%Y-%m-%d').strftime('%Y-%m-%d')
                except:
                    data_nascimento = None
            
            cursor.execute(
                'UPDATE Clientes SET nome=?, tipo_pessoa=?, documento=?, data_nascimento=?, email=?, telefone=?, endereco=?, cidade=?, estado=?, cep=? WHERE id_cliente=?',
                (
                    data['nome'],
                    tipo_pessoa,
                    data['documento'],
                    data_nascimento,
                    data.get('email'),
                    data.get('telefone'),
                    data.get('endereco'),
                    data.get('cidade'),
                    data.get('estado'),
                    data.get('cep'),
                    id
                )
            )
            conn.commit()
        except Exception as e:
            flash(f'Erro ao atualizar cliente: {str(e)}')
            conn.rollback()
            conn.close()
            return redirect(url_for('editar_cliente', id=id))
        conn.close()
        return redirect(url_for('clientes'))
    cursor.execute('SELECT * FROM Clientes WHERE id_cliente=?', (id,))
    row = cursor.fetchone()
    cliente = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('cliente_form.html', cliente=cliente)

@app.route('/clientes/excluir/<int:id>', methods=['POST'])
@requires_role('admin')  # Apenas administradores podem excluir clientes
def excluir_cliente(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se o cliente possui apólices
        cursor.execute('SELECT COUNT(*) FROM Apolices WHERE id_cliente = ?', (id,))
        total_apolices = cursor.fetchone()[0]
        
        if total_apolices > 0:
            flash(f'Não é possível excluir o cliente. Ele possui {total_apolices} apólice(s) vinculada(s).', 'error')
            return redirect(url_for('clientes'))
        
        # Buscar nome do cliente para log
        cursor.execute('SELECT nome FROM Clientes WHERE id_cliente = ?', (id,))
        result = cursor.fetchone()
        
        if not result:
            flash('Cliente não encontrado!', 'error')
            return redirect(url_for('clientes'))
        
        nome_cliente = result[0]
        
        # Excluir cliente
        cursor.execute('DELETE FROM Clientes WHERE id_cliente = ?', (id,))
        conn.commit()
        
        flash(f'Cliente "{nome_cliente}" excluído com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao excluir cliente: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('clientes'))

@app.route('/clientes/detalhes/<int:id>')
def detalhes_cliente(id):
    """Visualizar detalhes completos do cliente"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Dados do cliente
    cursor.execute('SELECT * FROM Clientes WHERE id_cliente = ?', (id,))
    row = cursor.fetchone()
    
    if not row:
        flash('Cliente não encontrado!', 'error')
        return redirect(url_for('clientes'))
    
    cliente = dict(zip([column[0] for column in cursor.description], row))
    
    # Apólices do cliente
    cursor.execute('''
        SELECT 
            a.id_apolice,
            a.numero_apolice,
            s.nome_seguradora,
            ts.nome_tipo_seguro,
            col.nome_colaborador,
            a.data_inicio_vigencia,
            a.data_fim_vigencia,
            a.valor_premio,
            a.status_apolice,
            CASE 
                WHEN a.data_fim_vigencia < GETDATE() THEN 'Vencida'
                WHEN a.data_fim_vigencia <= DATEADD(day, 30, GETDATE()) THEN 'Vencendo'
                ELSE 'Normal'
            END as situacao_vigencia
        FROM Apolices a
        JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
        JOIN Tipos_Seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        JOIN Colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE a.id_cliente = ?
        ORDER BY a.data_inicio_vigencia DESC
    ''', (id,))
    
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Estatísticas do cliente
    cursor.execute('''
        SELECT 
            COUNT(*) as total_apolices,
            COUNT(CASE WHEN status_apolice = 'Ativa' THEN 1 END) as apolices_ativas,
            SUM(CASE WHEN status_apolice = 'Ativa' THEN valor_premio ELSE 0 END) as valor_total_ativo,
            MIN(data_inicio_vigencia) as primeira_apolice,
            MAX(data_inicio_vigencia) as ultima_apolice
        FROM Apolices 
        WHERE id_cliente = ?
    ''', (id,))
    
    stats_row = cursor.fetchone()
    stats = dict(zip([column[0] for column in cursor.description], stats_row)) if stats_row else {}
    
    conn.close()
    
    return render_template('cliente_detalhes.html', 
                         cliente=cliente, 
                         apolices=apolices, 
                         stats=stats)

@app.route('/colaboradores')
@requires_role('admin')  # Apenas administradores podem ver lista de colaboradores
def colaboradores():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query com estatísticas de performance
    cursor.execute('''
        SELECT 
            c.id_colaborador, 
            c.nome_colaborador, 
            c.email_colaborador, 
            c.cargo, 
            c.status,
            c.data_contratacao,
            COUNT(a.id_apolice) as total_apolices,
            SUM(CASE WHEN a.status_apolice = 'Ativa' THEN a.valor_premio ELSE 0 END) as valor_total_vendas,
            SUM(CASE WHEN a.status_apolice = 'Ativa' THEN (a.valor_premio * a.percentual_comissao_colaborador / 100) ELSE 0 END) as comissao_total
        FROM Colaboradores c
        LEFT JOIN Apolices a ON c.id_colaborador = a.id_colaborador
        GROUP BY c.id_colaborador, c.nome_colaborador, c.email_colaborador, c.cargo, c.status, c.data_contratacao
        ORDER BY c.nome_colaborador
    ''')
    
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template('colaboradores.html', colaboradores=colaboradores)

@app.route('/colaboradores/novo', methods=['GET', 'POST'])
@requires_role('admin')  # Apenas administradores podem criar novos colaboradores
def novo_colaborador():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.form
        
        # Processar data de contratação
        data_contratacao = None
        if data.get('data_contratacao'):
            try:
                data_contratacao = datetime.strptime(data.get('data_contratacao'), '%Y-%m-%d').strftime('%Y-%m-%d')
            except:
                data_contratacao = None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Colaboradores (nome_colaborador, email_colaborador, senha, cargo, data_contratacao, status) VALUES (?, ?, ?, ?, ?, ?)',
            (
                data['nome_colaborador'],
                data['email_colaborador'],
                data['senha'],
                data.get('cargo'),
                data_contratacao,
                data.get('status', 'Ativo')
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('colaboradores'))
    return render_template('colaborador_form.html', colaborador=None)

@app.route('/colaboradores/editar/<int:id>', methods=['GET', 'POST'])
def editar_colaborador(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = request.form
        
        # Processar data de contratação
        data_contratacao = None
        if data.get('data_contratacao'):
            try:
                data_contratacao = datetime.strptime(data.get('data_contratacao'), '%Y-%m-%d').strftime('%Y-%m-%d')
            except:
                data_contratacao = None
        
        # Só atualiza senha se for informada
        if data.get('senha'):
            cursor.execute(
                'UPDATE Colaboradores SET nome_colaborador=?, email_colaborador=?, senha=?, cargo=?, data_contratacao=?, status=? WHERE id_colaborador=?',
                (
                    data['nome_colaborador'],
                    data['email_colaborador'],
                    data['senha'],
                    data.get('cargo'),
                    data_contratacao,
                    data.get('status', 'Ativo'),
                    id
                )
            )
        else:
            cursor.execute(
                'UPDATE Colaboradores SET nome_colaborador=?, email_colaborador=?, cargo=?, data_contratacao=?, status=? WHERE id_colaborador=?',
                (
                    data['nome_colaborador'],
                    data['email_colaborador'],
                    data.get('cargo'),
                    data_contratacao,
                    data.get('status', 'Ativo'),
                    id
                )
            )
        conn.commit()
        conn.close()
        return redirect(url_for('colaboradores'))
    cursor.execute('SELECT * FROM Colaboradores WHERE id_colaborador=?', (id,))
    row = cursor.fetchone()
    colaborador = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('colaborador_form.html', colaborador=colaborador)

# --- Apólices ---
@app.route('/apolices')
def apolices():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Parâmetros de filtro
    status = request.args.get('status', '')
    cliente_id = request.args.get('cliente_id', '')
    colaborador_id = request.args.get('colaborador_id', '')
    tipo_seguro_id = request.args.get('tipo_seguro_id', '')
    
    # Controle de acesso baseado no role
    user_role = session.get('role', 'usuario')
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query principal com todos os dados necessários incluindo comissões
    query = '''
    SELECT 
        a.id_apolice,
        a.numero_apolice,
        c.nome as cliente_nome,
        c.email as cliente_email,
        s.nome_seguradora as seguradora_nome,
        t.nome_tipo_seguro as tipo_seguro_nome,
        col.nome_colaborador,
        a.valor_premio,
        a.percentual_comissao_seguradora,
        a.percentual_comissao_colaborador,
        (a.valor_premio * a.percentual_comissao_seguradora / 100) as comissao_corretora,
        (a.valor_premio * a.percentual_comissao_colaborador / 100) as comissao_colaborador,
        a.data_inicio_vigencia,
        a.data_fim_vigencia,
        a.status_apolice,
        a.observacoes,
        CASE 
            WHEN a.data_fim_vigencia < GETDATE() THEN 'Vencida'
            WHEN a.data_fim_vigencia <= DATEADD(day, 30, GETDATE()) THEN 'Vencendo'
            ELSE 'Normal'
        END as situacao_vigencia
    FROM Apolices a
    JOIN Clientes c ON a.id_cliente = c.id_cliente
    JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
    JOIN Tipos_Seguro t ON a.id_tipo_seguro = t.id_tipo_seguro
    JOIN Colaboradores col ON a.id_colaborador = col.id_colaborador
    WHERE 1=1
    '''
    
    params = []
    
    # Se for corretor, mostrar apenas suas próprias apólices
    if user_role == 'corretor':
        query += ' AND a.id_colaborador = ?'
        params.append(user_id)
    
    # Adicionar filtros dinamicamente
    if status:
        query += ' AND a.status_apolice = ?'
        params.append(status)
    
    if cliente_id:
        query += ' AND a.id_cliente = ?'
        params.append(cliente_id)
    
    if colaborador_id:
        query += ' AND a.id_colaborador = ?'
        params.append(colaborador_id)
    
    if tipo_seguro_id:
        query += ' AND a.id_tipo_seguro = ?'
        params.append(tipo_seguro_id)
    
    query += ' ORDER BY a.data_inicio_vigencia DESC'
    
    cursor.execute(query, params)
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Estatísticas para o dashboard
    stats_query = '''
    SELECT 
        COUNT(*) as total_apolices,
        COUNT(CASE WHEN status_apolice = 'Ativa' THEN 1 END) as apolices_ativas,
        COUNT(CASE WHEN data_fim_vigencia <= DATEADD(day, 30, GETDATE()) AND status_apolice = 'Ativa' THEN 1 END) as apolices_vencendo,
        SUM(CASE WHEN status_apolice = 'Ativa' THEN valor_premio ELSE 0 END) as valor_total,
        SUM(CASE WHEN status_apolice = 'Ativa' THEN (valor_premio * percentual_comissao_seguradora / 100) ELSE 0 END) as comissoes_corretora,
        SUM(CASE WHEN status_apolice = 'Ativa' THEN (valor_premio * percentual_comissao_colaborador / 100) ELSE 0 END) as comissoes_colaboradores
    FROM Apolices
    '''
    
    cursor.execute(stats_query)
    stats = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    # Listas para os filtros
    cursor.execute('SELECT id_cliente, nome FROM Clientes ORDER BY nome')
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute('SELECT id_colaborador, nome_colaborador FROM Colaboradores ORDER BY nome_colaborador')
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute('SELECT id_tipo_seguro, nome_tipo_seguro FROM Tipos_Seguro ORDER BY nome_tipo_seguro')
    tipos_seguro = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    from datetime import date
    
    return render_template('apolices.html', 
                         apolices=apolices, 
                         stats=stats,
                         clientes=clientes,
                         colaboradores=colaboradores,
                         tipos_seguro=tipos_seguro,
                         today=date.today(),
                         filtros={
                             'status': status,
                             'cliente_id': cliente_id,
                             'colaborador_id': colaborador_id,
                             'tipo_seguro_id': tipo_seguro_id
                         })

@app.route('/apolices/nova', methods=['GET', 'POST'])
def nova_apolice():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Carregar dados para os selects
    cursor.execute('SELECT id_cliente, nome, email, telefone FROM Clientes ORDER BY nome')
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute('SELECT id_seguradora, nome_seguradora FROM Seguradoras ORDER BY nome_seguradora')
    seguradoras = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute('SELECT id_tipo_seguro, nome_tipo_seguro, descricao_tipo_seguro FROM Tipos_Seguro ORDER BY nome_tipo_seguro')
    tipos_seguro = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    cursor.execute('SELECT id_colaborador, nome_colaborador, email_colaborador FROM Colaboradores ORDER BY nome_colaborador')
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    if request.method == 'POST':
        data = request.form
        
        # Validações
        errors = []
        
        # Verificar se o número da apólice já existe
        cursor.execute('SELECT COUNT(*) FROM Apolices WHERE numero_apolice = ?', (data['numero_apolice'],))
        if cursor.fetchone()[0] > 0:
            errors.append('Número de apólice já existe no sistema')
        
        # Validar datas
        from datetime import datetime
        try:
            data_inicio = datetime.strptime(data['data_inicio_vigencia'], '%Y-%m-%d')
            data_fim = datetime.strptime(data['data_fim_vigencia'], '%Y-%m-%d')
            if data_fim <= data_inicio:
                errors.append('Data fim deve ser posterior à data início')
        except ValueError:
            errors.append('Datas inválidas')
        
        # Validar valor do prêmio
        try:
            valor_premio = float(data['valor_premio'])
            if valor_premio <= 0:
                errors.append('Valor do prêmio deve ser maior que zero')
        except ValueError:
            errors.append('Valor do prêmio inválido')
        
        # Validar percentuais
        try:
            perc_seguradora = float(data.get('percentual_comissao_seguradora', 0))
            perc_colaborador = float(data.get('percentual_comissao_colaborador', 0))
            if perc_seguradora < 0 or perc_seguradora > 100:
                errors.append('Percentual da corretora deve estar entre 0 e 100')
            if perc_colaborador < 0 or perc_colaborador > 100:
                errors.append('Percentual do colaborador deve estar entre 0 e 100')
        except ValueError:
            errors.append('Percentuais de comissão inválidos')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                # Gerar número de apólice automático se não informado
                numero_apolice = data['numero_apolice']
                if not numero_apolice:
                    cursor.execute('SELECT COUNT(*) FROM Apolices')
                    count = cursor.fetchone()[0]
                    numero_apolice = f"APL-{datetime.now().year}-{count + 1:04d}"
                
                cursor.execute('''
                    INSERT INTO Apolices 
                    (id_cliente, id_seguradora, id_tipo_seguro, id_colaborador, 
                     numero_apolice, data_inicio_vigencia, data_fim_vigencia, 
                     valor_premio, percentual_comissao_seguradora, percentual_comissao_colaborador, 
                     status_apolice, observacoes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['id_cliente'],
                    data['id_seguradora'],
                    data['id_tipo_seguro'],
                    data['id_colaborador'],
                    numero_apolice,
                    data['data_inicio_vigencia'],
                    data['data_fim_vigencia'],
                    data['valor_premio'],
                    data.get('percentual_comissao_seguradora', 15),  # Default 15%
                    data.get('percentual_comissao_colaborador', 10),  # Default 10%
                    data.get('status_apolice', 'Ativa'),
                    data.get('observacoes', '')
                ))
                
                conn.commit()
                flash('Apólice cadastrada com sucesso!', 'success')
                conn.close()
                return redirect(url_for('apolices'))
                
            except Exception as e:
                conn.rollback()
                flash(f'Erro ao cadastrar apólice: {str(e)}', 'error')
    
    conn.close()
    return render_template('apolice_form.html', 
                         apolice=None, 
                         clientes=clientes, 
                         seguradoras=seguradoras, 
                         tipos_seguro=tipos_seguro, 
                         colaboradores=colaboradores)

@app.route('/apolices/editar/<int:id>', methods=['GET', 'POST'])
def editar_apolice(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_cliente, nome FROM Clientes')
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_seguradora, nome_seguradora FROM Seguradoras')
    seguradoras = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_tipo_seguro, nome_tipo_seguro FROM Tipos_Seguro')
    tipos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_colaborador, nome_colaborador FROM Colaboradores')
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            '''UPDATE Apolices SET id_cliente=?, id_seguradora=?, id_tipo_seguro=?, id_colaborador=?, numero_apolice=?, data_inicio_vigencia=?, data_fim_vigencia=?, valor_premio=?, percentual_comissao_seguradora=?, percentual_comissao_colaborador=?, data_pagamento_comissao_corretora=?, data_pagamento_comissao_colaborador=?, status_apolice=?, observacoes=? WHERE id_apolice=?''',
            (
                data['id_cliente'],
                data['id_seguradora'],
                data['id_tipo_seguro'],
                data['id_colaborador'],
                data['numero_apolice'],
                data['data_inicio_vigencia'],
                data['data_fim_vigencia'],
                data['valor_premio'],
                data.get('percentual_comissao_seguradora'),
                data.get('percentual_comissao_colaborador'),
                data.get('data_pagamento_comissao_corretora'),
                data.get('data_pagamento_comissao_colaborador'),
                data.get('status_apolice'),
                data.get('observacoes'),
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('apolices'))
    cursor.execute('SELECT * FROM Apolices WHERE id_apolice=?', (id,))
    row = cursor.fetchone()
    apolice = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('apolice_form.html', apolice=apolice, clientes=clientes, seguradoras=seguradoras, tipos=tipos, colaboradores=colaboradores)

@app.route('/apolices/excluir/<int:id>', methods=['POST'])
@requires_role('admin')  # Apenas administradores podem excluir apólices
def excluir_apolice(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se a apólice possui renovações
        cursor.execute('SELECT COUNT(*) FROM Renovacao_Apolices WHERE id_apolice_antiga = ? OR id_apolice_nova = ?', (id, id))
        total_renovacoes = cursor.fetchone()[0]
        
        # Verificar se a apólice possui sinistros
        cursor.execute('SELECT COUNT(*) FROM Sinistros WHERE id_apolice = ?', (id,))
        total_sinistros = cursor.fetchone()[0]
        
        if total_renovacoes > 0:
            flash(f'Não é possível excluir a apólice. Ela possui {total_renovacoes} renovação(ões) vinculada(s).', 'error')
            return redirect(url_for('apolices'))
        
        if total_sinistros > 0:
            flash(f'Não é possível excluir a apólice. Ela possui {total_sinistros} sinistro(s) vinculado(s).', 'error')
            return redirect(url_for('apolices'))
        
        # Buscar número da apólice para log
        cursor.execute('SELECT numero_apolice FROM Apolices WHERE id_apolice = ?', (id,))
        result = cursor.fetchone()
        
        if not result:
            flash('Apólice não encontrada!', 'error')
            return redirect(url_for('apolices'))
        
        numero_apolice = result[0]
        
        # Excluir apólice
        cursor.execute('DELETE FROM Apolices WHERE id_apolice = ?', (id,))
        conn.commit()
        
        flash(f'Apólice "{numero_apolice}" excluída com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao excluir apólice: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('apolices'))

# --- Sinistros ---
@app.route('/sinistros')
def sinistros():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT s.id_sinistro, a.numero_apolice, s.data_ocorrido, s.status_sinistro, s.numero_processo_seguradora, s.valor_indenizacao
                      FROM Sinistros s JOIN Apolices a ON s.id_apolice = a.id_apolice''')
    sinistros = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template('sinistros.html', sinistros=sinistros)

@app.route('/sinistros/novo', methods=['GET', 'POST'])
def novo_sinistro():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_apolice, numero_apolice FROM Apolices')
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            '''INSERT INTO Sinistros (id_apolice, data_ocorrido, data_comunicacao, descricao_sinistro, status_sinistro, numero_processo_seguradora, valor_indenizacao, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['id_apolice'],
                data['data_ocorrido'],
                data.get('data_comunicacao'),
                data.get('descricao_sinistro'),
                data.get('status_sinistro'),
                data.get('numero_processo_seguradora'),
                data.get('valor_indenizacao'),
                data.get('observacoes')
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('sinistros'))
    conn.close()
    return render_template('sinistro_form.html', sinistro=None, apolices=apolices)

@app.route('/sinistros/editar/<int:id>', methods=['GET', 'POST'])
def editar_sinistro(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_apolice, numero_apolice FROM Apolices')
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            '''UPDATE Sinistros SET id_apolice=?, data_ocorrido=?, data_comunicacao=?, descricao_sinistro=?, status_sinistro=?, numero_processo_seguradora=?, valor_indenizacao=?, observacoes=? WHERE id_sinistro=?''',
            (
                data['id_apolice'],
                data['data_ocorrido'],
                data.get('data_comunicacao'),
                data.get('descricao_sinistro'),
                data.get('status_sinistro'),
                data.get('numero_processo_seguradora'),
                data.get('valor_indenizacao'),
                data.get('observacoes'),
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('sinistros'))
    cursor.execute('SELECT * FROM Sinistros WHERE id_sinistro=?', (id,))
    row = cursor.fetchone()
    sinistro = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('sinistro_form.html', sinistro=sinistro, apolices=apolices)

# --- Renovações de Apólices ---
# (Função renovacoes movida para o final do arquivo para evitar duplicação)

# Rota removida - versão específica está no final do arquivo

@app.route('/renovacoes/editar/<int:id>', methods=['GET', 'POST'])
def editar_renovacao(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_apolice, numero_apolice FROM Apolices')
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            '''UPDATE Renovacao_Apolices SET id_apolice_antiga=?, data_prevista_renovacao=?, status_renovacao=?, id_apolice_nova=?, observacoes=? WHERE id_renovacao=?''',
            (
                data['id_apolice_antiga'],
                data['data_prevista_renovacao'],
                data.get('status_renovacao'),
                data.get('id_apolice_nova') or None,
                data.get('observacoes'),
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('renovacoes'))
    cursor.execute('SELECT * FROM Renovacao_Apolices WHERE id_renovacao=?', (id,))
    row = cursor.fetchone()
    renovacao = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('renovacao_form.html', renovacao=renovacao, apolices=apolices)

# --- Tarefas ---
@app.route('/tarefas')
def tarefas():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Controle de acesso baseado no role
    user_role = session.get('role', 'usuario')
    user_id = session.get('user_id')
    
    # Parâmetros de filtro
    status = request.args.get('status', '')
    prioridade = request.args.get('prioridade', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query base com filtros
    base_query = '''
    SELECT 
        t.id_tarefa, 
        t.titulo_tarefa, 
        c.nome_colaborador, 
        cli.nome as nome_cliente, 
        a.numero_apolice, 
        t.prioridade, 
        t.status_tarefa, 
        t.data_vencimento,
        t.descricao_tarefa,
        CASE 
            WHEN t.data_vencimento < GETDATE() THEN 'Atrasada'
            WHEN t.data_vencimento <= DATEADD(day, 3, GETDATE()) THEN 'Urgente'
            ELSE 'Normal'
        END as urgencia
    FROM Tarefas t
    JOIN Colaboradores c ON t.id_colaborador = c.id_colaborador
    LEFT JOIN Clientes cli ON t.id_cliente = cli.id_cliente
    LEFT JOIN Apolices a ON t.id_apolice = a.id_apolice
    WHERE 1=1
    '''
    
    params = []
    
    # Se for corretor, mostrar apenas suas próprias tarefas
    if user_role == 'corretor':
        base_query += ' AND t.id_colaborador = ?'
        params.append(user_id)
    
    # Filtros adicionais
    if status:
        base_query += ' AND t.status_tarefa = ?'
        params.append(status)
    
    if prioridade:
        base_query += ' AND t.prioridade = ?'
        params.append(prioridade)
    
    base_query += ' ORDER BY t.data_vencimento ASC, t.prioridade DESC'
    
    cursor.execute(base_query, params)
    tarefas = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Estatísticas de tarefas
    stats_query = '''
    SELECT 
        COUNT(*) as total_tarefas,
        COUNT(CASE WHEN status_tarefa = 'Pendente' THEN 1 END) as pendentes,
        COUNT(CASE WHEN status_tarefa = 'Em Andamento' THEN 1 END) as em_andamento,
        COUNT(CASE WHEN status_tarefa = 'Concluida' THEN 1 END) as concluidas,
        COUNT(CASE WHEN data_vencimento < GETDATE() AND status_tarefa != 'Concluida' THEN 1 END) as atrasadas
    FROM Tarefas t
    WHERE 1=1
    '''
    
    stats_params = []
    if user_role == 'corretor':
        stats_query += ' AND t.id_colaborador = ?'
        stats_params.append(user_id)
    
    cursor.execute(stats_query, stats_params)
    stats = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    conn.close()
    return render_template('tarefas.html', 
                         tarefas=tarefas, 
                         stats=stats,
                         filtros={'status': status, 'prioridade': prioridade})

@app.route('/tarefas/nova', methods=['GET', 'POST'])
def nova_tarefa():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_colaborador, nome_colaborador FROM Colaboradores')
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_cliente, nome FROM Clientes')
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_apolice, numero_apolice FROM Apolices')
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    if request.method == 'POST':
        data = request.form
        
        # Processar datas para formato correto
        data_vencimento = None
        if data.get('data_vencimento'):
            try:
                data_vencimento = datetime.strptime(data.get('data_vencimento'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
            except:
                data_vencimento = None
        
        data_conclusao = None
        if data.get('data_conclusao'):
            try:
                data_conclusao = datetime.strptime(data.get('data_conclusao'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
            except:
                data_conclusao = None
        
        cursor.execute(
            '''INSERT INTO Tarefas (titulo_tarefa, id_colaborador, id_cliente, id_apolice, descricao_tarefa, data_vencimento, prioridade, status_tarefa, data_conclusao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['titulo_tarefa'],
                data['id_colaborador'] if data.get('id_colaborador') else None,
                data.get('id_cliente') if data.get('id_cliente') else None,
                data.get('id_apolice') if data.get('id_apolice') else None,
                data.get('descricao_tarefa'),
                data_vencimento,
                data.get('prioridade'),
                data.get('status_tarefa'),
                data_conclusao
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('tarefas'))
    conn.close()
    return render_template('tarefa_form.html', tarefa=None, colaboradores=colaboradores, clientes=clientes, apolices=apolices)

@app.route('/tarefas/editar/<int:id>', methods=['GET', 'POST'])
def editar_tarefa(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_colaborador, nome_colaborador FROM Colaboradores')
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_cliente, nome FROM Clientes')
    clientes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    cursor.execute('SELECT id_apolice, numero_apolice FROM Apolices')
    apolices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    if request.method == 'POST':
        data = request.form
        
        # Processar datas para formato correto
        data_vencimento = None
        if data.get('data_vencimento'):
            try:
                data_vencimento = datetime.strptime(data.get('data_vencimento'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
            except:
                data_vencimento = None
        
        data_conclusao = None
        if data.get('data_conclusao'):
            try:
                data_conclusao = datetime.strptime(data.get('data_conclusao'), '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
            except:
                data_conclusao = None
        
        cursor.execute(
            '''UPDATE Tarefas SET titulo_tarefa=?, id_colaborador=?, id_cliente=?, id_apolice=?, descricao_tarefa=?, data_vencimento=?, prioridade=?, status_tarefa=?, data_conclusao=? WHERE id_tarefa=?''',
            (
                data['titulo_tarefa'],
                data['id_colaborador'] if data.get('id_colaborador') else None,
                data.get('id_cliente') if data.get('id_cliente') else None,
                data.get('id_apolice') if data.get('id_apolice') else None,
                data.get('descricao_tarefa'),
                data_vencimento,
                data.get('prioridade'),
                data.get('status_tarefa'),
                data_conclusao,
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('tarefas'))
    cursor.execute('SELECT * FROM Tarefas WHERE id_tarefa=?', (id,))
    row = cursor.fetchone()
    tarefa = dict(zip([column[0] for column in cursor.description], row)) if row else None
    conn.close()
    return render_template('tarefa_form.html', tarefa=tarefa, colaboradores=colaboradores, clientes=clientes, apolices=apolices)

# --- Relatórios de Comissões ---
@app.route('/relatorios')
def relatorios():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('relatorios.html')

@app.route('/relatorios/comissoes', methods=['GET', 'POST'])
def relatorio_comissoes():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Parâmetros de filtro
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    colaborador_id = request.args.get('colaborador_id', '')
    
    # Query base para comissões por colaborador
    base_query = """
    SELECT 
        c.id_colaborador,
        c.nome_colaborador,
        c.email_colaborador,
        COUNT(a.id_apolice) as total_apolices,
        SUM(a.valor_premio) as valor_total_premios,
        SUM(a.valor_premio * (a.percentual_comissao_colaborador / 100)) as comissao_total,
        AVG(a.percentual_comissao_colaborador) as percentual_medio,
        MIN(a.data_inicio_vigencia) as primeira_venda,
        MAX(a.data_inicio_vigencia) as ultima_venda
    FROM Colaboradores c
    LEFT JOIN Apolices a ON c.id_colaborador = a.id_colaborador
    WHERE 1=1
    """
    
    params = []
    
    # Adicionar filtros se fornecidos
    if data_inicio:
        base_query += " AND a.data_inicio_vigencia >= ?"
        params.append(data_inicio)
    
    if data_fim:
        base_query += " AND a.data_inicio_vigencia <= ?"
        params.append(data_fim)
    
    if colaborador_id:
        base_query += " AND c.id_colaborador = ?"
        params.append(colaborador_id)
    
    base_query += """
    GROUP BY c.id_colaborador, c.nome_colaborador, c.email_colaborador
    ORDER BY comissao_total DESC
    """
    
    cursor.execute(base_query, params)
    comissoes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Query para estatísticas gerais
    stats_query = """
    SELECT 
        COUNT(DISTINCT c.id_colaborador) as total_colaboradores,
        COUNT(a.id_apolice) as total_apolices,
        SUM(a.valor_premio) as valor_total_vendas,
        SUM(a.valor_premio * (a.percentual_comissao_colaborador / 100)) as total_comissoes
    FROM Colaboradores c
    LEFT JOIN Apolices a ON c.id_colaborador = a.id_colaborador
    WHERE 1=1
    """
    
    stats_params = []
    if data_inicio:
        stats_query += " AND a.data_inicio_vigencia >= ?"
        stats_params.append(data_inicio)
    
    if data_fim:
        stats_query += " AND a.data_inicio_vigencia <= ?"
        stats_params.append(data_fim)
    
    cursor.execute(stats_query, stats_params)
    estatisticas = dict(zip([column[0] for column in cursor.description], cursor.fetchone()))
    
    # Lista de colaboradores para filtro
    cursor.execute("SELECT id_colaborador, nome_colaborador FROM Colaboradores ORDER BY nome_colaborador")
    colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('relatorio_comissoes.html', 
                         comissoes=comissoes, 
                         estatisticas=estatisticas,
                         colaboradores=colaboradores,
                         filtros={
                             'data_inicio': data_inicio,
                             'data_fim': data_fim,
                             'colaborador_id': colaborador_id
                         })

@app.route('/relatorios/vendas-periodo')
def relatorio_vendas_periodo():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query para vendas por período (últimos 12 meses)
    query = """
    SELECT 
        YEAR(a.data_inicio_vigencia) as ano,
        MONTH(a.data_inicio_vigencia) as mes,
        DATENAME(month, a.data_inicio_vigencia) + '/' + CAST(YEAR(a.data_inicio_vigencia) as VARCHAR) as periodo,
        COUNT(a.id_apolice) as total_apolices,
        SUM(a.valor_premio) as valor_total,
        SUM(a.valor_premio * (a.percentual_comissao_colaborador / 100)) as comissao_total,
        AVG(a.valor_premio) as ticket_medio
    FROM Apolices a
    WHERE a.data_inicio_vigencia >= DATEADD(month, -12, GETDATE())
    GROUP BY YEAR(a.data_inicio_vigencia), MONTH(a.data_inicio_vigencia), DATENAME(month, a.data_inicio_vigencia)
    ORDER BY ano DESC, mes DESC
    """
    
    cursor.execute(query)
    vendas_periodo = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Query para top colaboradores no período
    top_colaboradores_query = """
    SELECT TOP 5
        c.nome_colaborador,
        COUNT(a.id_apolice) as total_vendas,
        SUM(a.valor_premio) as valor_total,
        SUM(a.valor_premio * (a.percentual_comissao_colaborador / 100)) as comissao_total
    FROM Colaboradores c
    INNER JOIN Apolices a ON c.id_colaborador = a.id_colaborador
    WHERE a.data_inicio_vigencia >= DATEADD(month, -12, GETDATE())
    GROUP BY c.id_colaborador, c.nome_colaborador
    ORDER BY comissao_total DESC
    """
    
    cursor.execute(top_colaboradores_query)
    top_colaboradores = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Query para tipos de seguro mais vendidos
    tipos_query = """
    SELECT 
        ts.nome_tipo_seguro,
        COUNT(a.id_apolice) as quantidade,
        SUM(a.valor_premio) as valor_total,
        AVG(a.valor_premio) as valor_medio
    FROM Tipos_Seguro ts
    INNER JOIN Apolices a ON ts.id_tipo_seguro = a.id_tipo_seguro
    WHERE a.data_inicio_vigencia >= DATEADD(month, -12, GETDATE())
    GROUP BY ts.id_tipo_seguro, ts.nome_tipo_seguro
    ORDER BY quantidade DESC
    """
    
    cursor.execute(tipos_query)
    tipos_vendidos = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('relatorio_vendas_periodo.html',
                         vendas_periodo=vendas_periodo,
                         top_colaboradores=top_colaboradores,
                         tipos_vendidos=tipos_vendidos)

@app.route('/relatorios/performance-detalhada')
def relatorio_performance_detalhada():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query detalhada por colaborador com métricas avançadas
    query = """
    SELECT 
        c.nome_colaborador,
        c.email_colaborador,
        c.cargo,
        COUNT(a.id_apolice) as total_vendas,
        SUM(a.valor_premio) as valor_total_vendido,
        SUM(a.valor_comissao_colaborador) as comissao_total,
        AVG(a.valor_premio) as ticket_medio,
        MIN(a.data_inicio_vigencia) as primeira_venda,
        MAX(a.data_inicio_vigencia) as ultima_venda,
        COUNT(DISTINCT YEAR(a.data_inicio_vigencia) * 100 + MONTH(a.data_inicio_vigencia)) as meses_ativos,
        CASE 
            WHEN COUNT(a.id_apolice) = 0 THEN 0
            ELSE CAST(COUNT(a.id_apolice) AS FLOAT) / NULLIF(COUNT(DISTINCT YEAR(a.data_inicio_vigencia) * 100 + MONTH(a.data_inicio_vigencia)), 0)
        END as vendas_por_mes
    FROM Colaboradores c
    LEFT JOIN Apolices a ON c.id_colaborador = a.id_colaborador
    WHERE c.status = 'Ativo'
    GROUP BY c.id_colaborador, c.nome_colaborador, c.email_colaborador, c.cargo
    ORDER BY comissao_total DESC
    """
    
    cursor.execute(query)
    performance = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Query para análise de renovações
    renovacoes_query = """
    SELECT 
        c.nome_colaborador,
        COUNT(r.id_renovacao) as total_renovacoes,
        COUNT(CASE WHEN r.status_renovacao = 'Concluida' THEN 1 END) as renovacoes_concluidas,
        CASE 
            WHEN COUNT(r.id_renovacao) = 0 THEN 0
            ELSE CAST(COUNT(CASE WHEN r.status_renovacao = 'Concluida' THEN 1 END) AS FLOAT) * 100 / COUNT(r.id_renovacao)
        END as taxa_renovacao
    FROM Colaboradores c
    LEFT JOIN Apolices a ON c.id_colaborador = a.id_colaborador
    LEFT JOIN Renovacao_Apolices r ON a.id_apolice = r.id_apolice_antiga
    GROUP BY c.id_colaborador, c.nome_colaborador
    ORDER BY taxa_renovacao DESC
    """
    
    cursor.execute(renovacoes_query)
    renovacoes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('relatorio_performance_detalhada.html',
                         performance=performance,
                         renovacoes=renovacoes)

# Rotas de Renovações
@app.route('/renovacoes')
def renovacoes():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query corrigida para renovações com dados relacionados
    query = """
    SELECT 
        r.id_renovacao,
        r.id_apolice_antiga,
        r.id_apolice_nova,
        ao.numero_apolice as apolice_original,
        ao.data_fim_vigencia as vencimento_original,
        ao.valor_premio as valor_original,
        ar.numero_apolice as apolice_renovada,
        ar.data_inicio_vigencia as inicio_renovada,
        ar.data_fim_vigencia as fim_renovada,
        ar.valor_premio as valor_renovada,
        c.nome as cliente_nome,
        s.nome_seguradora,
        ts.nome_tipo_seguro,
        col.nome_colaborador,
        ar.data_inicio_vigencia as data_renovacao
    FROM Renovacao_Apolices r
    INNER JOIN Apolices ao ON r.id_apolice_antiga = ao.id_apolice
    INNER JOIN Apolices ar ON r.id_apolice_nova = ar.id_apolice
    INNER JOIN Clientes c ON ao.id_cliente = c.id_cliente
    INNER JOIN Seguradoras s ON ao.id_seguradora = s.id_seguradora
    INNER JOIN Tipos_Seguro ts ON ao.id_tipo_seguro = ts.id_tipo_seguro
    INNER JOIN Colaboradores col ON ao.id_colaborador = col.id_colaborador
    ORDER BY ar.data_inicio_vigencia DESC
    """
    
    cursor.execute(query)
    renovacoes = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    return render_template('renovacoes.html', renovacoes=renovacoes)

@app.route('/renovacoes/nova/<int:id_apolice>', methods=['GET', 'POST'])
def nova_renovacao(id_apolice):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar dados da apólice original
    cursor.execute("""
        SELECT a.*, c.nome as cliente_nome, s.nome_seguradora, ts.nome_tipo_seguro, col.nome_colaborador
        FROM Apolices a
        INNER JOIN Clientes c ON a.id_cliente = c.id_cliente
        INNER JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
        INNER JOIN Tipos_Seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        INNER JOIN Colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE a.id_apolice = ?
    """, (id_apolice,))
    
    apolice_original = cursor.fetchone()
    if not apolice_original:
        flash('Apólice não encontrada!', 'error')
        return redirect(url_for('apolices'))
    
    apolice_original = dict(zip([column[0] for column in cursor.description], apolice_original))
    
    # Verificar se já foi renovada
    cursor.execute('SELECT COUNT(*) FROM Renovacao_Apolices WHERE id_apolice_antiga = ?', (id_apolice,))
    if cursor.fetchone()[0] > 0:
        flash('Esta apólice já foi renovada!', 'error')
        return redirect(url_for('apolices'))
    
    if request.method == 'POST':
        data = request.form
        
        try:
            from datetime import datetime, timedelta
            
            # Criar nova apólice com dados atualizados
            cursor.execute('''
                INSERT INTO Apolices 
                (id_cliente, id_seguradora, id_tipo_seguro, id_colaborador, 
                 numero_apolice, data_inicio_vigencia, data_fim_vigencia, 
                 valor_premio, percentual_comissao_seguradora, percentual_comissao_colaborador, 
                 status_apolice, observacoes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                apolice_original['id_cliente'],
                apolice_original['id_seguradora'],
                apolice_original['id_tipo_seguro'],
                apolice_original['id_colaborador'],
                data['numero_apolice_nova'],
                data['data_inicio_vigencia'],
                data['data_fim_vigencia'],
                data['valor_premio'],
                data.get('percentual_comissao_seguradora', apolice_original['percentual_comissao_seguradora']),
                data.get('percentual_comissao_colaborador', apolice_original['percentual_comissao_colaborador']),
                'Ativa',
                data.get('observacoes', '')
            ))
            
            # Obter ID da nova apólice
            cursor.execute('SELECT @@IDENTITY as id')
            id_apolice_nova = cursor.fetchone()[0]
            
            # Registrar a renovação
            cursor.execute('''
                INSERT INTO Renovacao_Apolices 
                (id_apolice_antiga, id_apolice_nova, data_renovacao, observacoes_renovacao)
                VALUES (?, ?, ?, ?)
            ''', (
                id_apolice,
                id_apolice_nova,
                datetime.now().strftime('%Y-%m-%d'),
                data.get('observacoes_renovacao', '')
            ))
            
            # Atualizar status da apólice original
            cursor.execute('UPDATE Apolices SET status_apolice = ? WHERE id_apolice = ?', 
                         ('Renovada', id_apolice))
            
            conn.commit()
            flash('Apólice renovada com sucesso!', 'success')
            conn.close()
            return redirect(url_for('renovacoes'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao renovar apólice: {str(e)}', 'error')
    
    conn.close()
    return render_template('renovacao_form.html', apolice=apolice_original)

@app.route('/apolices/vencimento')
def apolices_vencimento():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar apólices que vencem nos próximos 30 dias
    query = """
    SELECT 
        a.*,
        c.nome as cliente_nome,
        s.nome_seguradora,
        ts.nome_tipo_seguro,
        col.nome_colaborador,
        DATEDIFF(day, GETDATE(), a.data_fim_vigencia) as dias_vencimento
    FROM Apolices a
    INNER JOIN Clientes c ON a.id_cliente = c.id_cliente
    INNER JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
    INNER JOIN Tipos_Seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
    INNER JOIN Colaboradores col ON a.id_colaborador = col.id_colaborador
    WHERE a.status_apolice = 'Ativa'
    AND a.data_fim_vigencia BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
    AND NOT EXISTS (SELECT 1 FROM Renovacao_Apolices WHERE id_apolice_antiga = a.id_apolice)
    ORDER BY a.data_fim_vigencia ASC
    """
    
    cursor.execute(query)
    apolices_vencimento = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    conn.close()
    return render_template('apolices_vencimento.html', apolices=apolices_vencimento)

if __name__ == '__main__':
    app.run(debug=True, port=5000)