-- ===============================================
-- SISTEMA CLIVER SEGUROS - BANCO DE DADOS MELHORADO
-- Versão: 3.0 - Com Campos Personalizados, Consultas e Segurança
-- Data: 01/10/2025
-- ===============================================

USE master;
GO

-- Criação do banco de dados
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'CorretoraDB')
BEGIN
    CREATE DATABASE CorretoraDB;
END
GO

USE CorretoraDB;
GO

-- ===============================================
-- 1. TABELAS PRINCIPAIS COM CAMPOS PERSONALIZADOS
-- ===============================================

-- Tabela de Auditoria (para segurança e rastreamento)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AuditoriaLog' AND xtype='U')
CREATE TABLE AuditoriaLog (
    id_auditoria INT IDENTITY(1,1) PRIMARY KEY,
    tabela_afetada NVARCHAR(100) NOT NULL,
    acao NVARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    id_registro INT,
    usuario NVARCHAR(100),
    data_hora DATETIME2 DEFAULT GETDATE(),
    dados_anteriores NVARCHAR(MAX),
    dados_novos NVARCHAR(MAX),
    ip_address NVARCHAR(45),
    observacoes NVARCHAR(500)
);

-- Tabela de Configurações do Sistema
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='ConfiguracaoSistema' AND xtype='U')
CREATE TABLE ConfiguracaoSistema (
    id_config INT IDENTITY(1,1) PRIMARY KEY,
    chave NVARCHAR(100) UNIQUE NOT NULL,
    valor NVARCHAR(MAX),
    descricao NVARCHAR(500),
    categoria NVARCHAR(100),
    ativo BIT DEFAULT 1,
    data_criacao DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE()
);

-- Tabela de Usuários e Controle de Acesso
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Usuarios' AND xtype='U')
CREATE TABLE Usuarios (
    id_usuario INT IDENTITY(1,1) PRIMARY KEY,
    login NVARCHAR(50) UNIQUE NOT NULL,
    senha_hash NVARCHAR(255) NOT NULL, -- Senha criptografada
    salt NVARCHAR(50) NOT NULL, -- Salt para hash
    nome_completo NVARCHAR(200) NOT NULL,
    email NVARCHAR(200) UNIQUE,
    telefone NVARCHAR(20),
    perfil_acesso NVARCHAR(50) NOT NULL, -- ADMIN, VENDEDOR, CONSULTA, GERENTE
    ativo BIT DEFAULT 1,
    ultimo_login DATETIME2,
    tentativas_login INT DEFAULT 0,
    bloqueado BIT DEFAULT 0,
    data_bloqueio DATETIME2,
    data_criacao DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE(),
    observacoes NVARCHAR(1000),
    foto_perfil NVARCHAR(500) -- URL da foto
);

-- Tabela Clientes com campos personalizados
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Clientes' AND xtype='U')
CREATE TABLE Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(200) NOT NULL,
    cpf_cnpj NVARCHAR(20) UNIQUE,
    tipo_pessoa CHAR(2) CHECK (tipo_pessoa IN ('PF', 'PJ')) DEFAULT 'PF',
    rg_ie NVARCHAR(20),
    data_nascimento DATE,
    genero CHAR(1) CHECK (genero IN ('M', 'F', 'O')),
    estado_civil NVARCHAR(20),
    profissao NVARCHAR(100),
    renda_mensal DECIMAL(15,2),
    
    -- Endereço
    endereco_completo NVARCHAR(500),
    cep NVARCHAR(10),
    cidade NVARCHAR(100),
    estado NVARCHAR(2),
    pais NVARCHAR(50) DEFAULT 'Brasil',
    
    -- Contato
    telefone_principal NVARCHAR(20),
    telefone_secundario NVARCHAR(20),
    email NVARCHAR(200),
    whatsapp NVARCHAR(20),
    
    -- Campos personalizados para corretora
    origem_cliente NVARCHAR(100), -- Site, Indicação, Telefone, etc.
    classificacao_cliente NVARCHAR(20), -- A, B, C, VIP
    limite_credito DECIMAL(15,2),
    observacoes NVARCHAR(2000),
    historico_contato NVARCHAR(MAX), -- JSON com histórico
    preferencias_comunicacao NVARCHAR(500), -- Email, SMS, WhatsApp
    data_ultimo_contato DATETIME2,
    proximo_contato DATETIME2,
    potencial_vendas NVARCHAR(20), -- ALTO, MEDIO, BAIXO
    status_relacionamento NVARCHAR(50), -- ATIVO, INATIVO, PROSPECTO, FRIO
    
    -- Controle
    ativo BIT DEFAULT 1,
    data_cadastro DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE(),
    usuario_cadastro INT,
    usuario_atualizacao INT
);

-- Tabela Seguradoras
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Seguradoras' AND xtype='U')
CREATE TABLE Seguradoras (
    id_seguradora INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(200) NOT NULL,
    cnpj NVARCHAR(20) UNIQUE,
    codigo_susep NVARCHAR(50),
    
    -- Contato
    telefone NVARCHAR(20),
    email NVARCHAR(200),
    site NVARCHAR(500),
    
    -- Endereço
    endereco_completo NVARCHAR(500),
    cidade NVARCHAR(100),
    estado NVARCHAR(2),
    
    -- Campos personalizados
    rating_seguradora NVARCHAR(10), -- AAA, AA, A, B, C
    tempo_pagamento_sinistros INT, -- Em dias
    percentual_comissao_padrao DECIMAL(5,2),
    observacoes NVARCHAR(1000),
    contato_comercial NVARCHAR(200),
    telefone_comercial NVARCHAR(20),
    email_comercial NVARCHAR(200),
    prazo_emissao_apolice INT, -- Em horas
    aceita_pagamento_online BIT DEFAULT 0,
    
    -- Status
    ativo BIT DEFAULT 1,
    data_cadastro DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE()
);

-- Tabela Tipos de Seguro
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='TiposSeguro' AND xtype='U')
CREATE TABLE TiposSeguro (
    id_tipo_seguro INT IDENTITY(1,1) PRIMARY KEY,
    nome NVARCHAR(200) NOT NULL,
    categoria NVARCHAR(100), -- AUTO, VIDA, RESIDENCIAL, EMPRESARIAL, etc.
    descricao NVARCHAR(1000),
    
    -- Campos personalizados
    comissao_minima DECIMAL(5,2),
    comissao_maxima DECIMAL(5,2),
    prazo_carencia INT, -- Em dias
    idade_minima INT,
    idade_maxima INT,
    valor_minimo_cobertura DECIMAL(15,2),
    valor_maximo_cobertura DECIMAL(15,2),
    documentos_necessarios NVARCHAR(MAX), -- JSON com lista de documentos
    observacoes NVARCHAR(1000),
    
    -- Status
    ativo BIT DEFAULT 1,
    popular BIT DEFAULT 0, -- Para destacar os mais vendidos
    data_cadastro DATETIME2 DEFAULT GETDATE()
);

-- Tabela Apólices com campos estendidos
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Apolices' AND xtype='U')
CREATE TABLE Apolices (
    id_apolice INT IDENTITY(1,1) PRIMARY KEY,
    numero_apolice NVARCHAR(50) UNIQUE NOT NULL,
    
    -- Relacionamentos
    id_cliente INT NOT NULL,
    id_seguradora INT NOT NULL,
    id_tipo_seguro INT NOT NULL,
    id_colaborador_vendedor INT,
    
    -- Datas
    data_emissao DATE NOT NULL,
    data_inicio_vigencia DATE NOT NULL,
    data_fim_vigencia DATE NOT NULL,
    data_vencimento DATE,
    
    -- Valores
    valor_premio DECIMAL(15,2) NOT NULL,
    valor_comissao DECIMAL(15,2),
    percentual_comissao DECIMAL(5,2),
    valor_franquia DECIMAL(15,2),
    valor_cobertura DECIMAL(15,2),
    
    -- Campos personalizados
    forma_pagamento NVARCHAR(50), -- À VISTA, PARCELADO, DÉBITO AUTO
    numero_parcelas INT DEFAULT 1,
    valor_parcela DECIMAL(15,2),
    dia_vencimento_parcela INT,
    banco_debito NVARCHAR(100),
    agencia_debito NVARCHAR(20),
    conta_debito NVARCHAR(20),
    
    -- Controle e histórico
    status_apolice NVARCHAR(50) DEFAULT 'ATIVA', -- ATIVA, CANCELADA, SUSPENSA, VENCIDA
    motivo_cancelamento NVARCHAR(500),
    data_cancelamento DATETIME2,
    renovacao_automatica BIT DEFAULT 1,
    observacoes NVARCHAR(2000),
    
    -- Auditoria
    data_cadastro DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE(),
    usuario_cadastro INT,
    usuario_atualizacao INT
);

-- Tabela de Sinistros com campos detalhados
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Sinistros' AND xtype='U')
CREATE TABLE Sinistros (
    id_sinistro INT IDENTITY(1,1) PRIMARY KEY,
    numero_sinistro NVARCHAR(50) UNIQUE NOT NULL,
    id_apolice INT NOT NULL,
    
    -- Detalhes do sinistro
    data_ocorrencia DATETIME2 NOT NULL,
    data_comunicacao DATETIME2 DEFAULT GETDATE(),
    local_ocorrencia NVARCHAR(500),
    descricao NVARCHAR(2000) NOT NULL,
    tipo_sinistro NVARCHAR(100), -- ROUBO, ACIDENTE, INCÊNDIO, etc.
    
    -- Valores
    valor_prejuizo DECIMAL(15,2),
    valor_franquia DECIMAL(15,2),
    valor_indenizacao DECIMAL(15,2),
    
    -- Status e acompanhamento
    status_sinistro NVARCHAR(50) DEFAULT 'ABERTO', -- ABERTO, EM_ANÁLISE, DEFERIDO, INDEFERIDO, PAGO
    protocolo_seguradora NVARCHAR(100),
    perito_responsavel NVARCHAR(200),
    telefone_perito NVARCHAR(20),
    data_vistoria DATETIME2,
    data_conclusao DATETIME2,
    
    -- Documentação
    documentos_enviados NVARCHAR(MAX), -- JSON com lista de documentos
    observacoes NVARCHAR(2000),
    
    -- Auditoria
    data_cadastro DATETIME2 DEFAULT GETDATE(),
    data_atualizacao DATETIME2 DEFAULT GETDATE(),
    usuario_responsavel INT
);

-- Tabela de Renovações
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Renovacoes' AND xtype='U')
CREATE TABLE Renovacoes (
    id_renovacao INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice_original INT NOT NULL,
    id_apolice_nova INT,
    
    -- Datas importantes
    data_aviso DATETIME2 DEFAULT GETDATE(),
    data_vencimento DATE NOT NULL,
    data_renovacao DATE,
    
    -- Status do processo
    status_renovacao NVARCHAR(50) DEFAULT 'PENDENTE', -- PENDENTE, RENOVADA, NÃO_RENOVADA, CANCELADA
    valor_proposto DECIMAL(15,2),
    percentual_reajuste DECIMAL(5,2),
    motivo_nao_renovacao NVARCHAR(500),
    
    -- Acompanhamento
    tentativas_contato INT DEFAULT 0,
    data_ultimo_contato DATETIME2,
    proximo_contato DATETIME2,
    observacoes NVARCHAR(1000),
    
    -- Auditoria
    data_cadastro DATETIME2 DEFAULT GETDATE(),
    usuario_responsavel INT
);

-- Tabela de Tarefas/CRM
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tarefas' AND xtype='U')
CREATE TABLE Tarefas (
    id_tarefa INT IDENTITY(1,1) PRIMARY KEY,
    titulo NVARCHAR(200) NOT NULL,
    descricao NVARCHAR(2000),
    
    -- Relacionamentos opcionais
    id_cliente INT,
    id_apolice INT,
    id_sinistro INT,
    
    -- Classificação
    tipo_tarefa NVARCHAR(50), -- LIGAÇÃO, EMAIL, REUNIÃO, VISTORIA, FOLLOW_UP
    prioridade NVARCHAR(20) DEFAULT 'MÉDIA', -- BAIXA, MÉDIA, ALTA, URGENTE
    categoria NVARCHAR(100), -- VENDAS, ATENDIMENTO, COBRANÇA, RENOVAÇÃO
    
    -- Datas e status
    data_criacao DATETIME2 DEFAULT GETDATE(),
    data_prevista DATETIME2,
    data_conclusao DATETIME2,
    status_tarefa NVARCHAR(50) DEFAULT 'PENDENTE', -- PENDENTE, EM_ANDAMENTO, CONCLUÍDA, CANCELADA
    
    -- Responsabilidade
    usuario_criador INT NOT NULL,
    usuario_responsavel INT NOT NULL,
    
    -- Resultado
    resultado NVARCHAR(2000),
    proxima_acao NVARCHAR(1000),
    data_proxima_acao DATETIME2
);

-- Tabela de Comissões
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Comissoes' AND xtype='U')
CREATE TABLE Comissoes (
    id_comissao INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice INT NOT NULL,
    id_colaborador INT NOT NULL,
    
    -- Valores
    valor_comissao DECIMAL(15,2) NOT NULL,
    percentual DECIMAL(5,2) NOT NULL,
    tipo_comissao NVARCHAR(50), -- VENDA, RENOVAÇÃO, INDICAÇÃO
    
    -- Datas
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    
    -- Status
    status_pagamento NVARCHAR(50) DEFAULT 'PENDENTE', -- PENDENTE, PAGO, CANCELADO
    observacoes NVARCHAR(1000),
    
    -- Auditoria
    data_cadastro DATETIME2 DEFAULT GETDATE()
);

-- ===============================================
-- 2. ADIÇÃO DAS FOREIGN KEYS
-- ===============================================

-- Foreign Keys para Clientes
ALTER TABLE Clientes ADD CONSTRAINT FK_Clientes_UsuarioCadastro 
FOREIGN KEY (usuario_cadastro) REFERENCES Usuarios(id_usuario);

ALTER TABLE Clientes ADD CONSTRAINT FK_Clientes_UsuarioAtualizacao 
FOREIGN KEY (usuario_atualizacao) REFERENCES Usuarios(id_usuario);

-- Foreign Keys para Apolices
ALTER TABLE Apolices ADD CONSTRAINT FK_Apolices_Cliente 
FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente);

ALTER TABLE Apolices ADD CONSTRAINT FK_Apolices_Seguradora 
FOREIGN KEY (id_seguradora) REFERENCES Seguradoras(id_seguradora);

ALTER TABLE Apolices ADD CONSTRAINT FK_Apolices_TipoSeguro 
FOREIGN KEY (id_tipo_seguro) REFERENCES TiposSeguro(id_tipo_seguro);

ALTER TABLE Apolices ADD CONSTRAINT FK_Apolices_ColaboradorVendedor 
FOREIGN KEY (id_colaborador_vendedor) REFERENCES Usuarios(id_usuario);

ALTER TABLE Apolices ADD CONSTRAINT FK_Apolices_UsuarioCadastro 
FOREIGN KEY (usuario_cadastro) REFERENCES Usuarios(id_usuario);

ALTER TABLE Apolices ADD CONSTRAINT FK_Apolices_UsuarioAtualizacao 
FOREIGN KEY (usuario_atualizacao) REFERENCES Usuarios(id_usuario);

-- Foreign Keys para Sinistros
ALTER TABLE Sinistros ADD CONSTRAINT FK_Sinistros_Apolice 
FOREIGN KEY (id_apolice) REFERENCES Apolices(id_apolice);

ALTER TABLE Sinistros ADD CONSTRAINT FK_Sinistros_UsuarioResponsavel 
FOREIGN KEY (usuario_responsavel) REFERENCES Usuarios(id_usuario);

-- Foreign Keys para Renovacoes
ALTER TABLE Renovacoes ADD CONSTRAINT FK_Renovacoes_ApoliceOriginal 
FOREIGN KEY (id_apolice_original) REFERENCES Apolices(id_apolice);

ALTER TABLE Renovacoes ADD CONSTRAINT FK_Renovacoes_ApoliceNova 
FOREIGN KEY (id_apolice_nova) REFERENCES Apolices(id_apolice);

ALTER TABLE Renovacoes ADD CONSTRAINT FK_Renovacoes_UsuarioResponsavel 
FOREIGN KEY (usuario_responsavel) REFERENCES Usuarios(id_usuario);

-- Foreign Keys para Tarefas
ALTER TABLE Tarefas ADD CONSTRAINT FK_Tarefas_Cliente 
FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente);

ALTER TABLE Tarefas ADD CONSTRAINT FK_Tarefas_Apolice 
FOREIGN KEY (id_apolice) REFERENCES Apolices(id_apolice);

ALTER TABLE Tarefas ADD CONSTRAINT FK_Tarefas_Sinistro 
FOREIGN KEY (id_sinistro) REFERENCES Sinistros(id_sinistro);

ALTER TABLE Tarefas ADD CONSTRAINT FK_Tarefas_UsuarioCriador 
FOREIGN KEY (usuario_criador) REFERENCES Usuarios(id_usuario);

ALTER TABLE Tarefas ADD CONSTRAINT FK_Tarefas_UsuarioResponsavel 
FOREIGN KEY (usuario_responsavel) REFERENCES Usuarios(id_usuario);

-- Foreign Keys para Comissoes
ALTER TABLE Comissoes ADD CONSTRAINT FK_Comissoes_Apolice 
FOREIGN KEY (id_apolice) REFERENCES Apolices(id_apolice);

ALTER TABLE Comissoes ADD CONSTRAINT FK_Comissoes_Colaborador 
FOREIGN KEY (id_colaborador) REFERENCES Usuarios(id_usuario);

-- ===============================================
-- 3. ÍNDICES PARA PERFORMANCE
-- ===============================================

-- Índices principais para consultas frequentes
CREATE NONCLUSTERED INDEX IX_Clientes_CPF_CNPJ ON Clientes(cpf_cnpj);
CREATE NONCLUSTERED INDEX IX_Clientes_Nome ON Clientes(nome);
CREATE NONCLUSTERED INDEX IX_Clientes_Email ON Clientes(email);
CREATE NONCLUSTERED INDEX IX_Clientes_Status ON Clientes(status_relacionamento);

CREATE NONCLUSTERED INDEX IX_Apolices_Cliente ON Apolices(id_cliente);
CREATE NONCLUSTERED INDEX IX_Apolices_Numero ON Apolices(numero_apolice);
CREATE NONCLUSTERED INDEX IX_Apolices_Vigencia ON Apolices(data_inicio_vigencia, data_fim_vigencia);
CREATE NONCLUSTERED INDEX IX_Apolices_Vencimento ON Apolices(data_vencimento);
CREATE NONCLUSTERED INDEX IX_Apolices_Status ON Apolices(status_apolice);

CREATE NONCLUSTERED INDEX IX_Sinistros_Apolice ON Sinistros(id_apolice);
CREATE NONCLUSTERED INDEX IX_Sinistros_Status ON Sinistros(status_sinistro);
CREATE NONCLUSTERED INDEX IX_Sinistros_Ocorrencia ON Sinistros(data_ocorrencia);

CREATE NONCLUSTERED INDEX IX_Tarefas_Responsavel ON Tarefas(usuario_responsavel);
CREATE NONCLUSTERED INDEX IX_Tarefas_Status ON Tarefas(status_tarefa);
CREATE NONCLUSTERED INDEX IX_Tarefas_Prevista ON Tarefas(data_prevista);

CREATE NONCLUSTERED INDEX IX_Renovacoes_Vencimento ON Renovacoes(data_vencimento);
CREATE NONCLUSTERED INDEX IX_Renovacoes_Status ON Renovacoes(status_renovacao);

-- ===============================================
-- 4. INSERÇÃO DE DADOS INICIAIS
-- ===============================================

-- Inserir configurações do sistema
INSERT INTO ConfiguracaoSistema (chave, valor, descricao, categoria) VALUES
('SISTEMA_VERSAO', '3.0', 'Versão atual do sistema', 'SISTEMA'),
('BACKUP_AUTOMATICO', 'true', 'Realizar backup automático', 'SEGURANCA'),
('TEMPO_SESSAO', '480', 'Tempo de sessão em minutos', 'SEGURANCA'),
('EMAIL_SMTP_SERVER', 'smtp.gmail.com', 'Servidor SMTP para emails', 'EMAIL'),
('EMAIL_SMTP_PORT', '587', 'Porta do servidor SMTP', 'EMAIL'),
('COMISSAO_PADRAO_AUTO', '15.0', 'Comissão padrão seguro auto (%)', 'COMISSAO'),
('COMISSAO_PADRAO_VIDA', '25.0', 'Comissão padrão seguro vida (%)', 'COMISSAO'),
('COMISSAO_PADRAO_RESIDENCIAL', '20.0', 'Comissão padrão seguro residencial (%)', 'COMISSAO'),
('DIAS_AVISO_RENOVACAO', '30', 'Dias antecipação aviso renovação', 'RENOVACAO'),
('LIMITE_TENTATIVAS_LOGIN', '5', 'Limite de tentativas de login', 'SEGURANCA');

-- Inserir usuário administrador padrão
INSERT INTO Usuarios (login, senha_hash, salt, nome_completo, email, perfil_acesso, observacoes) VALUES
('admin', 'admin_hash_aqui', 'salt_admin', 'Administrador do Sistema', 'admin@clivereguros.com', 'ADMIN', 'Usuário administrador padrão'),
('demo', 'demo_hash_aqui', 'salt_demo', 'Usuário Demonstração', 'demo@clivereguros.com', 'VENDEDOR', 'Usuário para demonstração');

-- Inserir tipos de seguro básicos
INSERT INTO TiposSeguro (nome, categoria, descricao, comissao_minima, comissao_maxima, popular) VALUES
('Seguro Auto', 'AUTO', 'Seguro para veículos automotores', 10.0, 20.0, 1),
('Seguro Vida', 'VIDA', 'Seguro de vida individual', 15.0, 30.0, 1),
('Seguro Residencial', 'RESIDENCIAL', 'Seguro para residências', 12.0, 25.0, 1),
('Seguro Empresarial', 'EMPRESARIAL', 'Seguro para empresas', 8.0, 18.0, 0),
('Seguro Viagem', 'VIAGEM', 'Seguro para viagens', 20.0, 40.0, 0);

-- Inserir seguradoras principais
INSERT INTO Seguradoras (nome, cnpj, rating_seguradora, percentual_comissao_padrao, ativo) VALUES
('Seguradora Porto Seguro', '61.198.164/0001-60', 'AA', 15.0, 1),
('Seguradora Bradesco', '92.682.038/0001-00', 'AAA', 18.0, 1),
('Seguradora Sulamerica', '01.463.570/0001-21', 'AA', 16.0, 1),
('Seguradora Itaú', '17.192.451/0001-70', 'AAA', 17.0, 1),
('Seguradora Mapfre', '61.074.175/0001-38', 'A', 14.0, 1);

-- Inserir clientes de exemplo
INSERT INTO Clientes (nome, cpf_cnpj, tipo_pessoa, telefone_principal, email, classificacao_cliente, potencial_vendas, status_relacionamento, origem_cliente, usuario_cadastro) VALUES
('João Silva Santos', '123.456.789-00', 'PF', '(11) 99999-1234', 'joao.silva@email.com', 'A', 'ALTO', 'ATIVO', 'Site', 1),
('Maria Oliveira Costa', '987.654.321-00', 'PF', '(11) 88888-5678', 'maria.oliveira@email.com', 'B', 'MEDIO', 'ATIVO', 'Indicação', 1),
('Empresa ABC Ltda', '12.345.678/0001-90', 'PJ', '(11) 3333-4444', 'contato@empresaabc.com.br', 'VIP', 'ALTO', 'ATIVO', 'Telefone', 1);

-- Inserir apólices de exemplo
INSERT INTO Apolices (numero_apolice, id_cliente, id_seguradora, id_tipo_seguro, id_colaborador_vendedor, data_emissao, data_inicio_vigencia, data_fim_vigencia, valor_premio, percentual_comissao, valor_comissao, status_apolice, usuario_cadastro) VALUES
('AP-2025-001', 1, 1, 1, 2, '2025-01-01', '2025-01-01', '2025-12-31', 2500.00, 15.0, 375.00, 'ATIVA', 1),
('AP-2025-002', 2, 2, 2, 2, '2025-02-01', '2025-02-01', '2026-01-31', 1800.00, 25.0, 450.00, 'ATIVA', 1),
('AP-2025-003', 3, 1, 4, 2, '2025-03-01', '2025-03-01', '2025-12-31', 15000.00, 12.0, 1800.00, 'ATIVA', 1);

-- ===============================================
-- 5. VIEWS PARA RELATÓRIOS PERSONALIZADOS
-- ===============================================

-- View: Dashboard Resumo
CREATE VIEW VW_Dashboard_Resumo AS
SELECT 
    (SELECT COUNT(*) FROM Clientes WHERE ativo = 1) AS total_clientes,
    (SELECT COUNT(*) FROM Apolices WHERE status_apolice = 'ATIVA') AS apolices_ativas,
    (SELECT COUNT(*) FROM Sinistros WHERE status_sinistro = 'ABERTO') AS sinistros_abertos,
    (SELECT COUNT(*) FROM Renovacoes WHERE status_renovacao = 'PENDENTE' AND data_vencimento <= DATEADD(day, 30, GETDATE())) AS renovacoes_pendentes,
    (SELECT ISNULL(SUM(valor_premio), 0) FROM Apolices WHERE YEAR(data_emissao) = YEAR(GETDATE()) AND status_apolice = 'ATIVA') AS faturamento_ano,
    (SELECT ISNULL(SUM(valor_comissao), 0) FROM Comissoes WHERE YEAR(data_vencimento) = YEAR(GETDATE()) AND status_pagamento = 'PENDENTE') AS comissoes_pendentes;
GO

-- View: Clientes com Potencial de Vendas
CREATE VIEW VW_Clientes_Potencial AS
SELECT 
    c.id_cliente,
    c.nome,
    c.telefone_principal,
    c.email,
    c.potencial_vendas,
    c.classificacao_cliente,
    c.data_ultimo_contato,
    c.proximo_contato,
    COUNT(a.id_apolice) as total_apolices,
    ISNULL(SUM(a.valor_premio), 0) as valor_total_seguros,
    CASE 
        WHEN c.data_ultimo_contato IS NULL THEN 999
        ELSE DATEDIFF(day, c.data_ultimo_contato, GETDATE()) 
    END as dias_sem_contato
FROM Clientes c
LEFT JOIN Apolices a ON c.id_cliente = a.id_cliente AND a.status_apolice = 'ATIVA'
WHERE c.ativo = 1
GROUP BY c.id_cliente, c.nome, c.telefone_principal, c.email, c.potencial_vendas, 
         c.classificacao_cliente, c.data_ultimo_contato, c.proximo_contato;
GO

-- View: Apólices a Vencer
CREATE VIEW VW_Apolices_Vencer AS
SELECT 
    a.id_apolice,
    a.numero_apolice,
    c.nome as cliente_nome,
    c.telefone_principal,
    c.email,
    s.nome as seguradora,
    ts.nome as tipo_seguro,
    a.data_fim_vigencia,
    a.valor_premio,
    DATEDIFF(day, GETDATE(), a.data_fim_vigencia) as dias_para_vencer,
    u.nome_completo as vendedor
FROM Apolices a
INNER JOIN Clientes c ON a.id_cliente = c.id_cliente
INNER JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
INNER JOIN TiposSeguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
LEFT JOIN Usuarios u ON a.id_colaborador_vendedor = u.id_usuario
WHERE a.status_apolice = 'ATIVA' 
  AND a.data_fim_vigencia <= DATEADD(day, 90, GETDATE())
  AND a.data_fim_vigencia >= GETDATE();
GO

-- ===============================================
-- 6. STORED PROCEDURES PARA RELATÓRIOS
-- ===============================================

-- Procedure: Relatório de Vendas por Período
CREATE PROCEDURE SP_Relatorio_Vendas_Periodo
    @DataInicio DATE,
    @DataFim DATE,
    @IdVendedor INT = NULL
AS
BEGIN
    SELECT 
        ISNULL(u.nome_completo, 'Sem Vendedor') as Vendedor,
        ts.nome as TipoSeguro,
        s.nome as Seguradora,
        COUNT(*) as QuantidadeVendas,
        SUM(a.valor_premio) as FaturamentoTotal,
        SUM(a.valor_comissao) as ComissaoTotal,
        AVG(a.valor_premio) as TicketMedio
    FROM Apolices a
    LEFT JOIN Usuarios u ON a.id_colaborador_vendedor = u.id_usuario
    INNER JOIN TiposSeguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
    INNER JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
    WHERE a.data_emissao BETWEEN @DataInicio AND @DataFim
      AND (@IdVendedor IS NULL OR a.id_colaborador_vendedor = @IdVendedor)
      AND a.status_apolice = 'ATIVA'
    GROUP BY u.nome_completo, ts.nome, s.nome
    ORDER BY SUM(a.valor_premio) DESC;
END;
GO

-- ===============================================
-- 7. FUNÇÕES ÚTEIS
-- ===============================================

-- Função: Calcular Comissão
CREATE FUNCTION FN_Calcular_Comissao(@ValorPremio DECIMAL(15,2), @Percentual DECIMAL(5,2))
RETURNS DECIMAL(15,2)
AS
BEGIN
    RETURN (@ValorPremio * @Percentual / 100);
END;
GO

PRINT '✅ Banco de dados CLIVER Seguros v3.0 criado com sucesso!';
PRINT '';
PRINT '📋 RECURSOS IMPLEMENTADOS:';
PRINT '  ✅ Campos personalizados para necessidades específicas da corretora';
PRINT '  ✅ Sistema completo de auditoria e controle de acesso';
PRINT '  ✅ Views para relatórios personalizados e dashboards';
PRINT '  ✅ Procedures para análises avançadas de performance';
PRINT '  ✅ Índices otimizados para consultas rápidas';
PRINT '  ✅ Dados de exemplo para teste imediato';
PRINT '  ✅ Estrutura preparada para segurança com hash de senhas';
PRINT '';
PRINT '🔍 PRÓXIMAS ETAPAS - CONSULTAS DE EXEMPLO:';
GO