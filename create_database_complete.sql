-- ============================================
-- BANCO DE DADOS SISTEMA CLIVER SEGUROS - VERSÃO FINAL
-- Implementação completa com autenticação, autorização e relatórios
-- Data: 01/10/2025
-- ============================================

USE master;
GO

-- Criar banco se não existir
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'CorretoraSeguros')
BEGIN
    CREATE DATABASE CorretoraSeguros;
    PRINT '✅ Banco CorretoraSeguros criado com sucesso!';
END
ELSE
BEGIN
    PRINT '✅ Banco CorretoraSeguros já existe!';
END
GO

USE CorretoraSeguros;
GO

-- ============================================
-- 1. TABELA DE COLABORADORES (Autenticação)
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'colaboradores')
BEGIN
    CREATE TABLE colaboradores (
        id_colaborador INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(255) NOT NULL,
        email NVARCHAR(255) UNIQUE NOT NULL,
        usuario NVARCHAR(100) UNIQUE NOT NULL,
        senha NVARCHAR(255) NOT NULL, -- Em produção usar hash
        telefone NVARCHAR(20),
        cargo NVARCHAR(100),
        nivel_acesso NVARCHAR(50) DEFAULT 'CORRETOR', -- ADMINISTRADOR, GERENTE, CORRETOR
        data_contratacao DATE,
        salario DECIMAL(10,2),
        percentual_comissao DECIMAL(5,2) DEFAULT 10.00,
        ativo BIT DEFAULT 1,
        data_criacao DATETIME2 DEFAULT GETDATE(),
        data_alteracao DATETIME2 DEFAULT GETDATE()
    );
    PRINT '✅ Tabela colaboradores criada!';
END
GO

-- ============================================
-- 2. TABELA DE CLIENTES
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'clientes')
BEGIN
    CREATE TABLE clientes (
        id_cliente INT IDENTITY(1,1) PRIMARY KEY,
        nome_completo NVARCHAR(255) NOT NULL,
        cpf_cnpj NVARCHAR(20) NOT NULL UNIQUE,
        tipo_pessoa CHAR(1) CHECK (tipo_pessoa IN ('F', 'J')) DEFAULT 'F', -- F=Física, J=Jurídica
        data_nascimento DATE,
        telefone NVARCHAR(20),
        email NVARCHAR(255),
        endereco NVARCHAR(500),
        cidade NVARCHAR(100),
        estado CHAR(2),
        cep NVARCHAR(10),
        observacoes NVARCHAR(MAX),
        data_cadastro DATETIME2 DEFAULT GETDATE(),
        ativo BIT DEFAULT 1,
        id_colaborador_responsavel INT, -- Colaborador responsável pelo cliente
        FOREIGN KEY (id_colaborador_responsavel) REFERENCES colaboradores(id_colaborador)
    );
    PRINT '✅ Tabela clientes criada!';
END
GO

-- ============================================
-- 3. TABELA DE SEGURADORAS
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'seguradoras')
BEGIN
    CREATE TABLE seguradoras (
        id_seguradora INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(255) NOT NULL,
        cnpj NVARCHAR(20),
        telefone NVARCHAR(20),
        email NVARCHAR(255),
        site NVARCHAR(255),
        endereco NVARCHAR(500),
        contato_comercial NVARCHAR(255),
        percentual_comissao_padrao DECIMAL(5,2) DEFAULT 10.00,
        ativa BIT DEFAULT 1,
        data_criacao DATETIME2 DEFAULT GETDATE()
    );
    PRINT '✅ Tabela seguradoras criada!';
END
GO

-- ============================================
-- 4. TABELA DE TIPOS DE SEGURO
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tipos_seguro')
BEGIN
    CREATE TABLE tipos_seguro (
        id_tipo_seguro INT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(255) NOT NULL,
        descricao NVARCHAR(MAX),
        categoria NVARCHAR(100), -- VIDA, AUTOMOVEL, RESIDENCIAL, EMPRESARIAL
        comissao_minima DECIMAL(5,2) DEFAULT 5.00,
        comissao_maxima DECIMAL(5,2) DEFAULT 25.00,
        ativo BIT DEFAULT 1
    );
    PRINT '✅ Tabela tipos_seguro criada!';
END
GO

-- ============================================
-- 5. TABELA DE APÓLICES
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'apolices')
BEGIN
    CREATE TABLE apolices (
        id_apolice INT IDENTITY(1,1) PRIMARY KEY,
        numero_apolice NVARCHAR(50) NOT NULL UNIQUE,
        id_cliente INT NOT NULL,
        id_seguradora INT NOT NULL,
        id_tipo_seguro INT NOT NULL,
        id_colaborador INT NOT NULL, -- Corretor responsável
        
        -- Valores financeiros
        valor_premio DECIMAL(15,2) NOT NULL,
        percentual_comissao DECIMAL(5,2) NOT NULL,
        valor_comissao DECIMAL(15,2) NOT NULL,
        
        -- Datas de vigência
        data_inicio_vigencia DATE NOT NULL,
        data_fim_vigencia DATE NOT NULL,
        data_emissao DATE DEFAULT GETDATE(),
        
        -- Status e forma de pagamento
        status_apolice NVARCHAR(20) DEFAULT 'ATIVA', -- ATIVA, CANCELADA, VENCIDA, SUSPENSA
        forma_pagamento NVARCHAR(50), -- À VISTA, MENSAL, TRIMESTRAL, SEMESTRAL, ANUAL
        
        -- Campos adicionais
        valor_franquia DECIMAL(15,2) DEFAULT 0,
        observacoes NVARCHAR(MAX),
        renovacao_automatica BIT DEFAULT 0,
        
        -- Auditoria
        data_criacao DATETIME2 DEFAULT GETDATE(),
        data_alteracao DATETIME2 DEFAULT GETDATE(),
        
        -- Foreign Keys
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_seguradora) REFERENCES seguradoras(id_seguradora),
        FOREIGN KEY (id_tipo_seguro) REFERENCES tipos_seguro(id_tipo_seguro),
        FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador)
    );
    PRINT '✅ Tabela apolices criada!';
END
GO

-- ============================================
-- 6. TABELA DE RENOVAÇÕES DE APÓLICES
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'renovacao_apolices')
BEGIN
    CREATE TABLE renovacao_apolices (
        id_renovacao INT IDENTITY(1,1) PRIMARY KEY,
        id_apolice_original INT NOT NULL,
        id_apolice_renovada INT NOT NULL,
        data_renovacao DATE DEFAULT GETDATE(),
        valor_premio_anterior DECIMAL(15,2),
        valor_premio_novo DECIMAL(15,2),
        observacoes NVARCHAR(MAX),
        
        FOREIGN KEY (id_apolice_original) REFERENCES apolices(id_apolice),
        FOREIGN KEY (id_apolice_renovada) REFERENCES apolices(id_apolice)
    );
    PRINT '✅ Tabela renovacao_apolices criada!';
END
GO

-- ============================================
-- 7. TABELA DE SINISTROS
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sinistros')
BEGIN
    CREATE TABLE sinistros (
        id_sinistro INT IDENTITY(1,1) PRIMARY KEY,
        numero_sinistro NVARCHAR(50) NOT NULL UNIQUE,
        id_apolice INT NOT NULL,
        data_ocorrencia DATE NOT NULL,
        data_comunicacao DATE DEFAULT GETDATE(),
        descricao NVARCHAR(MAX) NOT NULL,
        tipo_sinistro NVARCHAR(100), -- ROUBO, COLISAO, INCENDIO, DANOS_TERCEIROS
        local_ocorrencia NVARCHAR(255),
        valor_reclamado DECIMAL(15,2),
        valor_indenizado DECIMAL(15,2),
        status_sinistro NVARCHAR(30) DEFAULT 'ABERTO', -- ABERTO, EM_ANALISE, APROVADO, NEGADO, PAGO
        responsavel_analise NVARCHAR(255),
        observacoes NVARCHAR(MAX),
        data_criacao DATETIME2 DEFAULT GETDATE(),
        data_alteracao DATETIME2 DEFAULT GETDATE(),
        
        FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
    );
    PRINT '✅ Tabela sinistros criada!';
END
GO

-- ============================================
-- 8. TABELA DE TAREFAS
-- ============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'tarefas')
BEGIN
    CREATE TABLE tarefas (
        id_tarefa INT IDENTITY(1,1) PRIMARY KEY,
        titulo NVARCHAR(255) NOT NULL,
        descricao NVARCHAR(MAX),
        tipo_tarefa NVARCHAR(50), -- LIGACAO, VISITA, EMAIL, PROPOSTA, RENOVACAO, FOLLOW_UP
        id_cliente INT,
        id_colaborador INT NOT NULL, -- Responsável pela tarefa
        id_apolice INT, -- Apólice relacionada (opcional)
        
        -- Datas e status
        data_vencimento DATETIME2,
        data_conclusao DATETIME2,
        status NVARCHAR(20) DEFAULT 'PENDENTE', -- PENDENTE, EM_ANDAMENTO, CONCLUIDA, CANCELADA
        prioridade NVARCHAR(20) DEFAULT 'MEDIA', -- BAIXA, MEDIA, ALTA, URGENTE
        
        -- Resultados
        resultado NVARCHAR(MAX),
        proxima_acao NVARCHAR(255),
        
        -- Auditoria
        data_criacao DATETIME2 DEFAULT GETDATE(),
        data_alteracao DATETIME2 DEFAULT GETDATE(),
        
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_colaborador) REFERENCES colaboradores(id_colaborador),
        FOREIGN KEY (id_apolice) REFERENCES apolices(id_apolice)
    );
    PRINT '✅ Tabela tarefas criada!';
END
GO

-- ============================================
-- 9. ÍNDICES PARA PERFORMANCE
-- ============================================

-- Índices para clientes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Clientes_CPF_CNPJ')
    CREATE INDEX IX_Clientes_CPF_CNPJ ON clientes(cpf_cnpj);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Clientes_Nome')
    CREATE INDEX IX_Clientes_Nome ON clientes(nome_completo);

-- Índices para apólices
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Apolices_Numero')
    CREATE INDEX IX_Apolices_Numero ON apolices(numero_apolice);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Apolices_Cliente')
    CREATE INDEX IX_Apolices_Cliente ON apolices(id_cliente);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Apolices_Colaborador')
    CREATE INDEX IX_Apolices_Colaborador ON apolices(id_colaborador);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Apolices_Vigencia')
    CREATE INDEX IX_Apolices_Vigencia ON apolices(data_fim_vigencia);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Apolices_Status')
    CREATE INDEX IX_Apolices_Status ON apolices(status_apolice);

-- Índices para tarefas
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tarefas_Colaborador')
    CREATE INDEX IX_Tarefas_Colaborador ON tarefas(id_colaborador);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tarefas_Vencimento')
    CREATE INDEX IX_Tarefas_Vencimento ON tarefas(data_vencimento);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Tarefas_Status')
    CREATE INDEX IX_Tarefas_Status ON tarefas(status);

-- Índices para sinistros
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_Sinistros_Status')
    CREATE INDEX IX_Sinistros_Status ON sinistros(status_sinistro);

PRINT '✅ Índices criados para otimização de performance!';

-- ============================================
-- 10. DADOS INICIAIS PARA TESTES
-- ============================================

-- Inserir colaboradores de teste
IF NOT EXISTS (SELECT * FROM colaboradores WHERE usuario = 'admin')
BEGIN
    INSERT INTO colaboradores (nome, email, usuario, senha, cargo, nivel_acesso, percentual_comissao, ativo) VALUES
    ('Administrador Sistema', 'admin@cliver.com.br', 'admin', 'admin', 'Administrador', 'ADMINISTRADOR', 0.00, 1),
    ('João Silva', 'joao@cliver.com.br', 'joao', 'joao123', 'Gerente de Vendas', 'GERENTE', 5.00, 1),
    ('Maria Santos', 'maria@cliver.com.br', 'maria', 'maria123', 'Corretora Senior', 'CORRETOR', 12.00, 1),
    ('Pedro Oliveira', 'pedro@cliver.com.br', 'pedro', 'pedro123', 'Corretor Junior', 'CORRETOR', 10.00, 1);
    
    PRINT '✅ Colaboradores de teste inseridos!';
END

-- Inserir seguradoras de teste
IF NOT EXISTS (SELECT * FROM seguradoras WHERE nome = 'Porto Seguro')
BEGIN
    INSERT INTO seguradoras (nome, cnpj, telefone, email, percentual_comissao_padrao, ativa) VALUES
    ('Porto Seguro', '61.198.164/0001-60', '(11) 3003-9303', 'comercial@portoseguro.com.br', 15.00, 1),
    ('Bradesco Seguros', '92.682.038/0001-00', '(11) 4002-4002', 'vendas@bradescoseguros.com.br', 12.00, 1),
    ('SulAmérica Seguros', '01.685.053/0001-56', '(11) 4004-4004', 'comercial@sulamerica.com.br', 18.00, 1),
    ('Allianz Seguros', '61.074.175/0001-38', '(11) 2178-2178', 'parceiros@allianz.com.br', 14.00, 1),
    ('Zurich Seguros', '61.079.978/0001-83', '(11) 3004-3004', 'corretores@zurich.com.br', 16.00, 1);
    
    PRINT '✅ Seguradoras de teste inseridas!';
END

-- Inserir tipos de seguro
IF NOT EXISTS (SELECT * FROM tipos_seguro WHERE nome = 'Seguro Auto')
BEGIN
    INSERT INTO tipos_seguro (nome, descricao, categoria, comissao_minima, comissao_maxima, ativo) VALUES
    ('Seguro Auto', 'Cobertura completa para veículos automotores', 'AUTOMOVEL', 10.00, 20.00, 1),
    ('Seguro Residencial', 'Proteção para residências e condomínios', 'RESIDENCIAL', 8.00, 18.00, 1),
    ('Seguro de Vida', 'Cobertura por morte e invalidez', 'VIDA', 15.00, 30.00, 1),
    ('Seguro Empresarial', 'Proteção para empresas e estabelecimentos', 'EMPRESARIAL', 12.00, 25.00, 1),
    ('Seguro Viagem', 'Cobertura para viagens nacionais e internacionais', 'VIAGEM', 20.00, 40.00, 1),
    ('Seguro Saúde', 'Planos de assistência médica e hospitalar', 'SAUDE', 5.00, 15.00, 1);
    
    PRINT '✅ Tipos de seguro inseridos!';
END

-- Inserir clientes de teste
IF NOT EXISTS (SELECT * FROM clientes WHERE cpf_cnpj = '123.456.789-01')
BEGIN
    INSERT INTO clientes (nome_completo, cpf_cnpj, tipo_pessoa, data_nascimento, telefone, email, endereco, cidade, estado, cep, id_colaborador_responsavel, ativo) VALUES
    ('Ana Costa Silva', '123.456.789-01', 'F', '1985-03-15', '(11) 99999-1111', 'ana.silva@email.com', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234-567', 3, 1),
    ('Carlos Mendes Souza', '987.654.321-02', 'F', '1978-07-22', '(11) 99999-2222', 'carlos.souza@email.com', 'Av. Paulista, 1000', 'São Paulo', 'SP', '01310-100', 3, 1),
    ('Empresa Tech LTDA', '12.345.678/0001-90', 'J', NULL, '(11) 3333-4444', 'contato@empresatech.com.br', 'Rua do Comércio, 500', 'São Paulo', 'SP', '04567-890', 4, 1),
    ('Maria Fernanda Lima', '456.789.123-03', 'F', '1990-12-08', '(11) 99999-3333', 'maria.lima@email.com', 'Rua das Palmeiras, 789', 'São Paulo', 'SP', '05678-901', 4, 1);
    
    PRINT '✅ Clientes de teste inseridos!';
END

-- Inserir apólices de teste
IF NOT EXISTS (SELECT * FROM apolices WHERE numero_apolice = 'APL001-2025')
BEGIN
    INSERT INTO apolices (numero_apolice, id_cliente, id_seguradora, id_tipo_seguro, id_colaborador, valor_premio, percentual_comissao, valor_comissao, data_inicio_vigencia, data_fim_vigencia, status_apolice, forma_pagamento) VALUES
    ('APL001-2025', 1, 1, 1, 3, 2500.00, 15.00, 375.00, '2025-01-01', '2026-01-01', 'ATIVA', 'ANUAL'),
    ('APL002-2025', 2, 2, 2, 3, 1800.00, 12.00, 216.00, '2025-02-01', '2026-02-01', 'ATIVA', 'MENSAL'),
    ('APL003-2025', 3, 3, 4, 4, 8500.00, 18.00, 1530.00, '2025-03-01', '2026-03-01', 'ATIVA', 'SEMESTRAL'),
    ('APL004-2024', 4, 1, 3, 4, 1200.00, 25.00, 300.00, '2024-12-01', '2025-12-01', 'ATIVA', 'ANUAL'),
    ('APL005-2024', 1, 4, 5, 3, 450.00, 35.00, 157.50, '2024-11-15', '2025-01-15', 'VENCIDA', 'À VISTA');
    
    PRINT '✅ Apólices de teste inseridas!';
END

-- Inserir tarefas de teste
IF NOT EXISTS (SELECT * FROM tarefas WHERE titulo = 'Contato para renovação - Ana Costa')
BEGIN
    INSERT INTO tarefas (titulo, descricao, tipo_tarefa, id_cliente, id_colaborador, id_apolice, data_vencimento, status, prioridade) VALUES
    ('Contato para renovação - Ana Costa', 'Entrar em contato com a cliente para renovação da apólice de auto', 'RENOVACAO', 1, 3, 1, '2025-11-15 14:00:00', 'PENDENTE', 'ALTA'),
    ('Follow-up proposta - Carlos Souza', 'Acompanhar proposta de seguro residencial enviada', 'FOLLOW_UP', 2, 3, NULL, '2025-10-05 10:00:00', 'PENDENTE', 'MEDIA'),
    ('Visita técnica - Empresa Tech', 'Realizar visita técnica para avaliação de risco empresarial', 'VISITA', 3, 4, 3, '2025-10-10 09:00:00', 'PENDENTE', 'ALTA'),
    ('Ligação pós-venda - Maria Lima', 'Verificar satisfação com o atendimento e serviços', 'LIGACAO', 4, 4, NULL, '2025-10-02 16:00:00', 'PENDENTE', 'BAIXA');
    
    PRINT '✅ Tarefas de teste inseridas!';
END

-- Inserir sinistros de teste
IF NOT EXISTS (SELECT * FROM sinistros WHERE numero_sinistro = 'SIN001-2025')
BEGIN
    INSERT INTO sinistros (numero_sinistro, id_apolice, data_ocorrencia, descricao, tipo_sinistro, local_ocorrencia, valor_reclamado, status_sinistro) VALUES
    ('SIN001-2025', 1, '2025-09-15', 'Colisão traseira no trânsito da cidade', 'COLISAO', 'Av. Paulista com Rua Augusta - São Paulo/SP', 3500.00, 'EM_ANALISE'),
    ('SIN002-2025', 2, '2025-09-20', 'Vazamento em tubulação causou danos na residência', 'DANOS_AGUA', 'Residência do segurado', 1200.00, 'APROVADO');
    
    PRINT '✅ Sinistros de teste inseridos!';
END

PRINT '';
PRINT '🎉 ===== BANCO DE DADOS CLIVER SEGUROS =====';
PRINT '✅ Estrutura completa criada com sucesso!';
PRINT '✅ Dados de teste inseridos!';
PRINT '';
PRINT '👥 USUÁRIOS DISPONÍVEIS:';
PRINT '   🔑 admin/admin (Administrador)';
PRINT '   🔑 joao/joao123 (Gerente)'; 
PRINT '   🔑 maria/maria123 (Corretora Senior)';
PRINT '   🔑 pedro/pedro123 (Corretor Junior)';
PRINT '';
PRINT '📊 DADOS DISPONÍVEIS:';
PRINT '   👥 4 Clientes de teste';
PRINT '   🏢 5 Seguradoras';
PRINT '   📋 6 Tipos de seguro';
PRINT '   📄 5 Apólices (4 ativas, 1 vencida)';
PRINT '   📝 4 Tarefas pendentes';
PRINT '   🚨 2 Sinistros em andamento';
PRINT '';
PRINT '🚀 Sistema pronto para uso!';
GO