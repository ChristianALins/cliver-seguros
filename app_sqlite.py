from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, date
from functools import wraps
import os
import logging
import traceback

app = Flask(__name__)
app.secret_key = 'cliver_seguros_2025_secret_key'

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuração do banco de dados SQLite
DATABASE_PATH = 'cliver_seguros.db'

def get_db_connection():
    """Estabelece conexão com o banco de dados SQLite"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        return conn
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return None

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Colaboradores (Autenticação)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colaboradores (
                id_colaborador INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                telefone TEXT,
                cargo TEXT,
                nivel_acesso TEXT DEFAULT 'CORRETOR',
                data_contratacao DATE,
                salario DECIMAL(10,2),
                percentual_comissao DECIMAL(5,2) DEFAULT 10.00,
                ativo INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo TEXT NOT NULL,
                cpf_cnpj TEXT NOT NULL UNIQUE,
                tipo_pessoa TEXT CHECK (tipo_pessoa IN ('F', 'J')) DEFAULT 'F',
                data_nascimento DATE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                observacoes TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ativo INTEGER DEFAULT 1,
                id_colaborador_responsavel INTEGER,
                FOREIGN KEY (id_colaborador_responsavel) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        # Seguradoras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seguradoras (
                id_seguradora INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                site TEXT,
                endereco TEXT,
                contato_comercial TEXT,
                percentual_comissao_padrao DECIMAL(5,2) DEFAULT 10.00,
                ativa INTEGER DEFAULT 1,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tipos de Seguro
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tipos_seguro (
                id_tipo_seguro INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria TEXT,
                comissao_minima DECIMAL(5,2) DEFAULT 5.00,
                comissao_maxima DECIMAL(5,2) DEFAULT 25.00,
                ativo INTEGER DEFAULT 1
            )
        ''')
        
        # Apólices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apolices (
                id_apolice INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_apolice TEXT NOT NULL UNIQUE,
                id_cliente INTEGER NOT NULL,
                id_seguradora INTEGER NOT NULL,
                id_tipo_seguro INTEGER NOT NULL,
                id_colaborador INTEGER NOT NULL,
                valor_premio DECIMAL(15,2) NOT NULL,
                percentual_comissao DECIMAL(5,2) NOT NULL,
                valor_comissao DECIMAL(15,2) NOT NULL,
                data_inicio_vigencia DATE NOT NULL,
                data_fim_vigencia DATE NOT NULL,
                data_emissao DATE DEFAULT CURRENT_DATE,
                status_apolice TEXT DEFAULT 'ATIVA',
                forma_pagamento TEXT,
                valor_franquia DECIMAL(15,2) DEFAULT 0,
                observacoes TEXT,
                renovacao_automatica INTEGER DEFAULT 0,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_seguradora) REFERENCES seguradoras(id_seguradora),
                FOREIGN KEY (id_tipo_seguro) REFERENCES tipos_seguro(id_tipo_seguro),
                FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador)
            )
        ''')
        
        # Sinistros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinistros (
                id_sinistro INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_sinistro TEXT NOT NULL UNIQUE,
                id_apolice INTEGER NOT NULL,
                data_ocorrencia DATE NOT NULL,
                data_comunicacao DATE DEFAULT CURRENT_DATE,
                descricao TEXT NOT NULL,
                tipo_sinistro TEXT,
                local_ocorrencia TEXT,
                valor_reclamado DECIMAL(15,2),
                valor_indenizado DECIMAL(15,2),
                status_sinistro TEXT DEFAULT 'ABERTO',
                responsavel_analise TEXT,
                observacoes TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
            )
        ''')
        
        # Tarefas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id_tarefa INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                tipo_tarefa TEXT,
                id_cliente INTEGER,
                id_colaborador INTEGER NOT NULL,
                id_apolice INTEGER,
                data_vencimento DATETIME,
                data_conclusao DATETIME,
                status TEXT DEFAULT 'PENDENTE',
                prioridade TEXT DEFAULT 'MEDIA',
                resultado TEXT,
                proxima_acao TEXT,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_alteracao DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador),
                FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
            )
        ''')
        
        # Inserir dados iniciais se não existirem
        cursor.execute("SELECT COUNT(*) FROM colaboradores")
        if cursor.fetchone()[0] == 0:
            # Colaboradores
            cursor.execute('''
                INSERT INTO colaboradores (nome, email, usuario, senha, cargo, nivel_acesso, percentual_comissao, ativo) VALUES
                ('Administrador Sistema', 'admin@cliver.com.br', 'admin', 'admin', 'Administrador', 'ADMINISTRADOR', 0.00, 1),
                ('João Silva', 'joao@cliver.com.br', 'joao', 'joao123', 'Gerente de Vendas', 'GERENTE', 5.00, 1),
                ('Maria Santos', 'maria@cliver.com.br', 'maria', 'maria123', 'Corretora Senior', 'CORRETOR', 12.00, 1),
                ('Pedro Oliveira', 'pedro@cliver.com.br', 'pedro', 'pedro123', 'Corretor Junior', 'CORRETOR', 10.00, 1)
            ''')
            
            # Seguradoras
            cursor.execute('''
                INSERT INTO seguradoras (nome, cnpj, telefone, email, percentual_comissao_padrao, ativa) VALUES
                ('Porto Seguro', '61.198.164/0001-60', '(11) 3003-9303', 'comercial@portoseguro.com.br', 15.00, 1),
                ('Bradesco Seguros', '92.682.038/0001-00', '(11) 4002-4002', 'vendas@bradescoseguros.com.br', 12.00, 1),
                ('SulAmérica Seguros', '01.685.053/0001-56', '(11) 4004-4004', 'comercial@sulamerica.com.br', 18.00, 1),
                ('Allianz Seguros', '61.074.175/0001-38', '(11) 2178-2178', 'parceiros@allianz.com.br', 14.00, 1),
                ('Zurich Seguros', '61.079.978/0001-83', '(11) 3004-3004', 'corretores@zurich.com.br', 16.00, 1)
            ''')
            
            # Tipos de Seguro
            cursor.execute('''
                INSERT INTO tipos_seguro (nome, descricao, categoria, comissao_minima, comissao_maxima, ativo) VALUES
                ('Seguro Auto', 'Cobertura completa para veículos automotores', 'AUTOMOVEL', 10.00, 20.00, 1),
                ('Seguro Residencial', 'Proteção para residências e condomínios', 'RESIDENCIAL', 8.00, 18.00, 1),
                ('Seguro de Vida', 'Cobertura por morte e invalidez', 'VIDA', 15.00, 30.00, 1),
                ('Seguro Empresarial', 'Proteção para empresas e estabelecimentos', 'EMPRESARIAL', 12.00, 25.00, 1),
                ('Seguro Viagem', 'Cobertura para viagens nacionais e internacionais', 'VIAGEM', 20.00, 40.00, 1),
                ('Seguro Saúde', 'Planos de assistência médica e hospitalar', 'SAUDE', 5.00, 15.00, 1)
            ''')
            
            # Clientes
            cursor.execute('''
                INSERT INTO clientes (nome_completo, cpf_cnpj, tipo_pessoa, data_nascimento, telefone, email, endereco, cidade, estado, cep, id_colaborador_responsavel, ativo) VALUES
                ('Ana Costa Silva', '123.456.789-01', 'F', '1985-03-15', '(11) 99999-1111', 'ana.silva@email.com', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234-567', 3, 1),
                ('Carlos Mendes Souza', '987.654.321-02', 'F', '1978-07-22', '(11) 99999-2222', 'carlos.souza@email.com', 'Av. Paulista, 1000', 'São Paulo', 'SP', '01310-100', 3, 1),
                ('Empresa Tech LTDA', '12.345.678/0001-90', 'J', NULL, '(11) 3333-4444', 'contato@empresatech.com.br', 'Rua do Comércio, 500', 'São Paulo', 'SP', '04567-890', 4, 1),
                ('Maria Fernanda Lima', '456.789.123-03', 'F', '1990-12-08', '(11) 99999-3333', 'maria.lima@email.com', 'Rua das Palmeiras, 789', 'São Paulo', 'SP', '05678-901', 4, 1)
            ''')
            
            # Apólices
            cursor.execute('''
                INSERT INTO apolices (numero_apolice, id_cliente, id_seguradora, id_tipo_seguro, id_colaborador, valor_premio, percentual_comissao, valor_comissao, data_inicio_vigencia, data_fim_vigencia, status_apolice, forma_pagamento) VALUES
                ('APL001-2025', 1, 1, 1, 3, 2500.00, 15.00, 375.00, '2025-01-01', '2026-01-01', 'ATIVA', 'ANUAL'),
                ('APL002-2025', 2, 2, 2, 3, 1800.00, 12.00, 216.00, '2025-02-01', '2026-02-01', 'ATIVA', 'MENSAL'),
                ('APL003-2025', 3, 3, 4, 4, 8500.00, 18.00, 1530.00, '2025-03-01', '2026-03-01', 'ATIVA', 'SEMESTRAL'),
                ('APL004-2024', 4, 1, 3, 4, 1200.00, 25.00, 300.00, '2024-12-01', '2025-12-01', 'ATIVA', 'ANUAL'),
                ('APL005-2024', 1, 4, 5, 3, 450.00, 35.00, 157.50, '2024-11-15', '2025-01-15', 'VENCIDA', 'À VISTA')
            ''')
            
            # Tarefas
            cursor.execute('''
                INSERT INTO tarefas (titulo, descricao, tipo_tarefa, id_cliente, id_colaborador, id_apolice, data_vencimento, status, prioridade) VALUES
                ('Contato para renovação - Ana Costa', 'Entrar em contato com a cliente para renovação da apólice de auto', 'RENOVACAO', 1, 3, 1, '2025-11-15 14:00:00', 'PENDENTE', 'ALTA'),
                ('Follow-up proposta - Carlos Souza', 'Acompanhar proposta de seguro residencial enviada', 'FOLLOW_UP', 2, 3, NULL, '2025-10-05 10:00:00', 'PENDENTE', 'MEDIA'),
                ('Visita técnica - Empresa Tech', 'Realizar visita técnica para avaliação de risco empresarial', 'VISITA', 3, 4, 3, '2025-10-10 09:00:00', 'PENDENTE', 'ALTA'),
                ('Ligação pós-venda - Maria Lima', 'Verificar satisfação com o atendimento e serviços', 'LIGACAO', 4, 4, NULL, '2025-10-02 16:00:00', 'PENDENTE', 'BAIXA')
            ''')
            
            # Sinistros
            cursor.execute('''
                INSERT INTO sinistros (numero_sinistro, id_apolice, data_ocorrencia, descricao, tipo_sinistro, local_ocorrencia, valor_reclamado, status_sinistro) VALUES
                ('SIN001-2025', 1, '2025-09-15', 'Colisão traseira no trânsito da cidade', 'COLISAO', 'Av. Paulista com Rua Augusta - São Paulo/SP', 3500.00, 'EM_ANALISE'),
                ('SIN002-2025', 2, '2025-09-20', 'Vazamento em tubulação causou danos na residência', 'DANOS_AGUA', 'Residência do segurado', 1200.00, 'APROVADO')
            ''')
        
        conn.commit()
        print("✅ Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

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
        try:
            usuario = request.form.get('usuario', '').strip()
            senha = request.form.get('senha', '').strip()
            
            if not usuario or not senha:
                flash('Usuário e senha são obrigatórios', 'error')
                return render_template('login.html')
            
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
                session['user_id'] = user['id_colaborador']
                session['username'] = usuario
                session['nome'] = user['nome']
                session['email'] = user['email']
                session['cargo'] = user['cargo']
                session['nivel_acesso'] = user['nivel_acesso']
                
                logger.info(f'Login bem-sucedido para usuário: {usuario}')
                flash(f'Bem-vindo, {user["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha incorretos', 'error')
                logger.warning(f'Tentativa de login falhada para usuário: {usuario}')
                
        except Exception as e:
            logger.error(f'Erro no login: {str(e)}')
            flash('Erro interno no sistema de login', 'error')
    
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
        AND date(data_fim_vigencia) BETWEEN date('now') AND date('now', '+30 days')
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
        SELECT COALESCE(SUM(valor_premio), 0) 
        FROM apolices 
        WHERE strftime('%Y-%m', data_inicio_vigencia) = strftime('%Y-%m', 'now')
        AND status_apolice = 'ATIVA'
    """)
    metrics['receita_mes'] = cursor.fetchone()[0]
    
    # Comissões do mês atual
    cursor.execute("""
        SELECT COALESCE(SUM(valor_comissao), 0) 
        FROM apolices 
        WHERE strftime('%Y-%m', data_inicio_vigencia) = strftime('%Y-%m', 'now')
        AND status_apolice = 'ATIVA'
    """)
    metrics['comissoes_mes'] = cursor.fetchone()[0]
    
    # Últimas atividades (tarefas recentes)
    if session.get('nivel_acesso') == 'ADMINISTRADOR':
        cursor.execute("""
            SELECT t.titulo, t.data_vencimento, t.prioridade, c.nome_completo as cliente, col.nome as responsavel
            FROM tarefas t
            LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
            LEFT JOIN colaboradores col ON t.id_colaborador = col.id_colaborador
            WHERE t.status = 'PENDENTE'
            ORDER BY t.data_vencimento ASC
            LIMIT 5
        """)
    else:
        cursor.execute("""
            SELECT t.titulo, t.data_vencimento, t.prioridade, c.nome_completo as cliente
            FROM tarefas t
            LEFT JOIN clientes c ON t.id_cliente = c.id_cliente
            WHERE t.status = 'PENDENTE' AND t.id_colaborador = ?
            ORDER BY t.data_vencimento ASC
            LIMIT 5
        """, (session['user_id'],))
    
    atividades_recentes = [dict(row) for row in cursor.fetchall()]
    
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
                   COALESCE(SUM(CASE WHEN a.status_apolice = 'ATIVA' THEN a.valor_premio ELSE 0 END), 0) as valor_total
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
                   COALESCE(SUM(CASE WHEN a.status_apolice = 'ATIVA' THEN a.valor_premio ELSE 0 END), 0) as valor_total
            FROM clientes c
            LEFT JOIN colaboradores col ON c.id_colaborador_responsavel = col.id_colaborador
            LEFT JOIN apolices a ON c.id_cliente = a.id_cliente
            GROUP BY c.id_cliente, c.nome_completo, c.cpf_cnpj, c.telefone, c.email, 
                     c.cidade, c.estado, c.ativo, col.nome
            ORDER BY c.nome_completo
        """)
    
    clientes_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('clientes.html', clientes=clientes_list, search=search)

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    """Cadastrar novo cliente"""
    if request.method == 'POST':
        conn = get_db_connection()
        if not conn:
            flash('Erro de conexão com o banco de dados', 'error')
            return render_template('cliente_form.html')
        
        cursor = conn.cursor()
        
        try:
            # Obter dados do formulário de forma segura
            nome_completo = request.form.get('nome_completo', '').strip()
            cpf_cnpj = request.form.get('cpf_cnpj', '').strip()
            tipo_pessoa = request.form.get('tipo_pessoa', 'F')
            data_nascimento = request.form.get('data_nascimento', '')
            telefone = request.form.get('telefone', '').strip()
            email = request.form.get('email', '').strip()
            endereco = request.form.get('endereco', '').strip()
            cidade = request.form.get('cidade', '').strip()
            estado = request.form.get('estado', '').strip()
            cep = request.form.get('cep', '').strip()
            observacoes = request.form.get('observacoes', '').strip()
            
            # Validações básicas
            if not nome_completo:
                flash('Nome completo é obrigatório', 'error')
                return render_template('cliente_form.html')
            
            if not cpf_cnpj:
                flash('CPF/CNPJ é obrigatório', 'error')
                return render_template('cliente_form.html')
            
            cursor.execute("""
                INSERT INTO clientes (nome_completo, cpf_cnpj, tipo_pessoa, data_nascimento, 
                                    telefone, email, endereco, cidade, estado, cep, observacoes, 
                                    id_colaborador_responsavel, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                nome_completo, cpf_cnpj, tipo_pessoa, 
                data_nascimento if data_nascimento else None,
                telefone, email, endereco, cidade, 
                estado, cep, observacoes, 
                session['user_id']
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
               julianday(a.data_fim_vigencia) - julianday('now') as dias_vencimento
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
    apolices_list = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('apolices.html', apolices=apolices_list, 
                         status_filter=status_filter, cliente_filter=cliente_filter)

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
    tarefas_list = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('tarefas.html', tarefas=tarefas_list, 
                         status_filter=status_filter, prioridade_filter=prioridade_filter)

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
    sinistros_list = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('sinistros.html', sinistros=sinistros_list, status_filter=status_filter)

# ============================================
# RELATÓRIOS
# ============================================

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
    dados = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('relatorio_comissoes.html', dados=dados, 
                         data_inicio=data_inicio, data_fim=data_fim)

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
               julianday(a.data_fim_vigencia) - julianday('now') as dias_vencimento
        FROM apolices a
        LEFT JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN seguradoras s ON a.id_seguradora = s.id_seguradora
        LEFT JOIN tipos_seguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
        LEFT JOIN colaboradores col ON a.id_colaborador = col.id_colaborador
        WHERE a.status_apolice = 'ATIVA' 
        AND date(a.data_fim_vigencia) BETWEEN date('now') AND date('now', '+60 days')
    """
    
    # Filtrar por corretor se não for admin
    if session.get('nivel_acesso') == 'CORRETOR':
        query += " AND a.id_colaborador = ?"
        cursor.execute(query + " ORDER BY a.data_fim_vigencia", (session['user_id'],))
    else:
        cursor.execute(query + " ORDER BY a.data_fim_vigencia")
    
    apolices_list = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('apolices_vencimento.html', apolices=apolices_list)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def format_currency(value):
    """Formatar valor como moeda brasileira"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(date_value):
    """Formatar data para exibição"""
    if not date_value:
        return ''
    if isinstance(date_value, str):
        try:
            date_value = datetime.strptime(date_value, '%Y-%m-%d')
        except:
            return date_value
    return date_value.strftime('%d/%m/%Y') if date_value else ''

def format_datetime(datetime_value):
    """Formatar data e hora para exibição"""
    if not datetime_value:
        return ''
    if isinstance(datetime_value, str):
        try:
            datetime_value = datetime.strptime(datetime_value, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime_value
    return datetime_value.strftime('%d/%m/%Y %H:%M') if datetime_value else ''

# ============================================
# ROTAS ADICIONAIS PARA COMPLETAR O SISTEMA
# ============================================

@app.route('/seguradoras')
@login_required
def seguradoras():
    """Lista seguradoras"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('seguradoras.html', seguradoras=[])
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM seguradoras ORDER BY nome")
    seguradoras_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('seguradoras.html', seguradoras=seguradoras_list)

@app.route('/tipos_seguro')
@login_required  
def tipos_seguro():
    """Lista tipos de seguro"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('tipos_seguro.html', tipos=[])
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tipos_seguro ORDER BY nome")
    tipos_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('tipos_seguro.html', tipos=tipos_list)

@app.route('/colaboradores')
@login_required
@admin_required
def colaboradores():
    """Lista colaboradores (apenas admin)"""
    conn = get_db_connection()
    if not conn:
        flash('Erro de conexão com o banco de dados', 'error')
        return render_template('colaboradores.html', colaboradores=[])
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM colaboradores ORDER BY nome")
    colaboradores_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('colaboradores.html', colaboradores=colaboradores_list)

@app.route('/relatorios')
@login_required
def relatorios():
    """Página principal de relatórios"""
    return render_template('relatorios.html')

@app.route('/teste')
def teste():
    """Rota de teste para verificar se o sistema está funcionando"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM colaboradores")
            result = cursor.fetchone()
            conn.close()
            return jsonify({
                'status': 'success', 
                'message': 'Sistema funcionando!',
                'colaboradores': result[0] if result else 0
            })
        else:
            return jsonify({'status': 'error', 'message': 'Erro de conexão com banco'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# ============================================
# TRATAMENTO DE ERROS
# ============================================

@app.errorhandler(404)
def not_found_error(error):
    """Página não encontrada"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Erro interno do servidor"""
    return render_template('errors/500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Tratamento geral de exceções"""
    tb = traceback.format_exc()
    logger.error(f'Erro não tratado: {str(e)}\n{tb}')
    
    # Em modo de debug, mostrar erro detalhado
    if app.debug:
        return f"<h1>Erro:</h1><pre>{tb}</pre>", 500
    
    flash(f'Ocorreu um erro inesperado. Tente novamente.', 'error')
    return redirect(url_for('dashboard'))

# Registrar filtros no Jinja2
app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['date'] = format_date
app.jinja_env.filters['datetime'] = format_datetime

if __name__ == '__main__':
    # Inicializar banco de dados
    if init_database():
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
    else:
        print("❌ Erro ao inicializar o banco de dados. Verifique as configurações.")