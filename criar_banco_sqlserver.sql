-- ===================================================
-- CLIVER SEGUROS - CRIAÇÃO DO BANCO DE DADOS SQL SERVER
-- Script para criar o banco CorretoraSegurosDB e todas as tabelas
-- ===================================================

USE master;
GO

-- Criar o banco de dados se não existir
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CorretoraSegurosDB')
BEGIN
    CREATE DATABASE CorretoraSegurosDB;
    PRINT '✅ Banco de dados CorretoraSegurosDB criado com sucesso!';
END
ELSE
BEGIN
    PRINT '⚠️ Banco de dados CorretoraSegurosDB já existe.';
END
GO

USE CorretoraSegurosDB;
GO

-- Inicia transação para garantir que todas as tabelas sejam criadas ou nenhuma seja
BEGIN TRANSACTION;

-- Drop Tables (em ordem inversa para lidar com FKs, caso existam)
-- CUIDADO: Este comando apaga as tabelas e todos os seus dados!
-- Use apenas se estiver criando o banco de dados do zero ou resetando.
IF OBJECT_ID('Tarefas', 'U') IS NOT NULL DROP TABLE Tarefas;
IF OBJECT_ID('Renovacao_Apolices', 'U') IS NOT NULL DROP TABLE Renovacao_Apolices;
IF OBJECT_ID('Sinistros', 'U') IS NOT NULL DROP TABLE Sinistros;
IF OBJECT_ID('Apolices', 'U') IS NOT NULL DROP TABLE Apolices;
IF OBJECT_ID('Colaboradores', 'U') IS NOT NULL DROP TABLE Colaboradores;
IF OBJECT_ID('Clientes', 'U') IS NOT NULL DROP TABLE Clientes;
IF OBJECT_ID('Tipos_Seguro', 'U') IS NOT NULL DROP TABLE Tipos_Seguro;
IF OBJECT_ID('Seguradoras', 'U') IS NOT NULL DROP TABLE Seguradoras;
GO

-- -----------------------------------------------------
-- Table `Seguradoras`
-- -----------------------------------------------------
CREATE TABLE Seguradoras (
    id_seguradora INT IDENTITY(1,1) PRIMARY KEY,
    nome_seguradora VARCHAR(255) NOT NULL,
    cnpj_seguradora VARCHAR(18) UNIQUE,
    contato_seguradora VARCHAR(20),
    email_seguradora VARCHAR(255)
);
GO

PRINT '✅ Tabela Seguradoras criada!';

-- -----------------------------------------------------
-- Table `Tipos_Seguro`
-- No SQL Server, para 'ENUM', geralmente usamos uma tabela de lookup
-- e uma FK, ou um VARCHAR com uma CONSTRAINT CHECK.
-- Para simplicidade e seguindo o modelo ENUM anterior, usaremos VARCHAR + CHECK.
-- -----------------------------------------------------
CREATE TABLE Tipos_Seguro (
    id_tipo_seguro INT IDENTITY(1,1) PRIMARY KEY,
    nome_tipo_seguro VARCHAR(100) NOT NULL UNIQUE,
    descricao_tipo_seguro NVARCHAR(MAX) -- NVARCHAR(MAX) para texto longo, suporta caracteres Unicode
);
GO

PRINT '✅ Tabela Tipos_Seguro criada!';

-- -----------------------------------------------------
-- Table `Clientes`
-- -----------------------------------------------------
CREATE TABLE Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo_pessoa VARCHAR(10) NOT NULL CHECK (tipo_pessoa IN ('Fisica', 'Juridica')), -- Simula ENUM
    documento VARCHAR(18) UNIQUE NOT NULL,
    data_nascimento DATE,
    email VARCHAR(255),
    telefone VARCHAR(20),
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(9),
    data_cadastro DATETIME DEFAULT GETDATE() -- GETDATE() ou SYSDATETIME() para data/hora atual
);
GO

PRINT '✅ Tabela Clientes criada!';

-- -----------------------------------------------------
-- Table `Colaboradores`
-- -----------------------------------------------------
CREATE TABLE Colaboradores (
    id_colaborador INT IDENTITY(1,1) PRIMARY KEY,
    nome_colaborador VARCHAR(255) NOT NULL,
    email_colaborador VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL, -- Armazenar HASH da senha, NUNCA a senha em texto puro!
    cargo VARCHAR(100),
    data_contratacao DATE,
    status VARCHAR(10) DEFAULT 'Ativo' CHECK (status IN ('Ativo', 'Inativo')) -- Simula ENUM
);
GO

PRINT '✅ Tabela Colaboradores criada!';

-- -----------------------------------------------------
-- Table `Apolices`
-- -----------------------------------------------------
CREATE TABLE Apolices (
    id_apolice INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_seguradora INT NOT NULL,
    id_tipo_seguro INT NOT NULL,
    id_colaborador INT NOT NULL,
    numero_apolice VARCHAR(50) UNIQUE NOT NULL,
    data_inicio_vigencia DATE NOT NULL,
    data_fim_vigencia DATE NOT NULL,
    valor_premio DECIMAL(10, 2) NOT NULL,
    percentual_comissao_seguradora DECIMAL(5, 2),
    valor_comissao_corretora AS (valor_premio * percentual_comissao_seguradora / 100) PERSISTED, -- Coluna calculada
    percentual_comissao_colaborador DECIMAL(5, 2),
    valor_comissao_colaborador AS ((valor_premio * percentual_comissao_seguradora / 100) * percentual_comissao_colaborador / 100) PERSISTED, -- Coluna calculada
    data_pagamento_comissao_corretora DATE,
    data_pagamento_comissao_colaborador DATE,
    status_apolice VARCHAR(20) NOT NULL DEFAULT 'Ativa' CHECK (status_apolice IN ('Ativa', 'Vencida', 'Cancelada', 'Renovada', 'Aguardando Pagamento')), -- Simula ENUM
    observacoes NVARCHAR(MAX),

    CONSTRAINT FK_Apolices_Clientes FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Seguradoras FOREIGN KEY (id_seguradora) REFERENCES Seguradoras (id_seguradora) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_TiposSeguro FOREIGN KEY (id_tipo_seguro) REFERENCES Tipos_Seguro (id_tipo_seguro) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Apolices_Colaboradores FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

PRINT '✅ Tabela Apolices criada!';

-- -----------------------------------------------------
-- Table `Sinistros`
-- -----------------------------------------------------
CREATE TABLE Sinistros (
    id_sinistro INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice INT NOT NULL,
    data_ocorrido DATE NOT NULL,
    data_comunicacao DATETIME DEFAULT GETDATE(),
    descricao_sinistro NVARCHAR(MAX),
    status_sinistro VARCHAR(20) NOT NULL DEFAULT 'Aberto' CHECK (status_sinistro IN ('Aberto', 'Em Analise', 'Pago', 'Negado', 'Encerrado')), -- Simula ENUM
    numero_processo_seguradora VARCHAR(50),
    valor_indenizacao DECIMAL(10, 2),
    observacoes NVARCHAR(MAX),

    CONSTRAINT FK_Sinistros_Apolices FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) ON DELETE NO ACTION ON UPDATE CASCADE
);
GO

PRINT '✅ Tabela Sinistros criada!';

-- -----------------------------------------------------
-- Table `Renovacao_Apolices`
-- -----------------------------------------------------
CREATE TABLE Renovacao_Apolices (
    id_renovacao INT IDENTITY(1,1) PRIMARY KEY,
    id_apolice_antiga INT NOT NULL,
    data_prevista_renovacao DATE NOT NULL,
    status_renovacao VARCHAR(20) NOT NULL DEFAULT 'Pendente' CHECK (status_renovacao IN ('Pendente', 'Renovada', 'Nao Renovada', 'Em Negociacao')), -- Simula ENUM
    id_apolice_nova INT UNIQUE, -- ID da nova apólice gerada, se a renovação for concluída
    observacoes NVARCHAR(MAX),

    CONSTRAINT FK_RenovacaoApolices_ApolicesAntiga FOREIGN KEY (id_apolice_antiga) REFERENCES Apolices (id_apolice) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_RenovacaoApolices_ApolicesNova FOREIGN KEY (id_apolice_nova) REFERENCES Apolices (id_apolice) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

PRINT '✅ Tabela Renovacao_Apolices criada!';

-- -----------------------------------------------------
-- Table `Tarefas`
-- -----------------------------------------------------
CREATE TABLE Tarefas (
    id_tarefa INT IDENTITY(1,1) PRIMARY KEY,
    id_colaborador INT NOT NULL,
    id_apolice INT, -- Opcional: tarefa pode estar ligada a uma apólice
    id_cliente INT, -- Opcional: tarefa pode estar ligada a um cliente
    titulo_tarefa VARCHAR(255) NOT NULL,
    descricao_tarefa NVARCHAR(MAX),
    data_criacao DATETIME DEFAULT GETDATE(),
    data_vencimento DATETIME,
    prioridade VARCHAR(10) NOT NULL DEFAULT 'Media' CHECK (prioridade IN ('Baixa', 'Media', 'Alta', 'Urgente')), -- Simula ENUM
    status_tarefa VARCHAR(20) NOT NULL DEFAULT 'Pendente' CHECK (status_tarefa IN ('Pendente', 'Em Andamento', 'Concluida', 'Cancelada')), -- Simula ENUM
    data_conclusao DATETIME,

    CONSTRAINT FK_Tarefas_Colaboradores FOREIGN KEY (id_colaborador) REFERENCES Colaboradores (id_colaborador) ON DELETE NO ACTION ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Apolices FOREIGN KEY (id_apolice) REFERENCES Apolices (id_apolice) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT FK_Tarefas_Clientes FOREIGN KEY (id_cliente) REFERENCES Clientes (id_cliente) ON DELETE SET NULL ON UPDATE CASCADE
);
GO

PRINT '✅ Tabela Tarefas criada!';

COMMIT TRANSACTION;
GO

-- ===================================================
-- INSERÇÃO DE DADOS DE EXEMPLO
-- ===================================================

BEGIN TRANSACTION;

PRINT '🔄 Inserindo dados de exemplo...';

-- Inserir Seguradoras
INSERT INTO Seguradoras (nome_seguradora, cnpj_seguradora, contato_seguradora, email_seguradora) VALUES
('Porto Seguro', '33.061.352/0001-81', '(11) 3003-4000', 'contato@portoseguro.com.br'),
('Bradesco Seguros', '92.682.038/0001-00', '(11) 4002-4002', 'seguros@bradesco.com.br'),
('Sul América', '29.978.814/0001-87', '(11) 3175-3000', 'atendimento@sulamerica.com.br'),
('Itaú Seguros', '17.192.451/0001-70', '(11) 4004-4828', 'seguros@itau.com.br');

PRINT '✅ Seguradoras inseridas!';

-- Inserir Tipos de Seguro
INSERT INTO Tipos_Seguro (nome_tipo_seguro, descricao_tipo_seguro) VALUES
('Auto', 'Seguro de veículos automotores'),
('Residencial', 'Seguro residencial e patrimonial'),
('Vida', 'Seguro de vida individual e familiar'),
('Saúde', 'Seguro de assistência médica e hospitalar'),
('Empresarial', 'Seguro para empresas e estabelecimentos comerciais');

PRINT '✅ Tipos de Seguro inseridos!';

-- Inserir Colaboradores (senhas serão hasheadas pelo sistema Python)
INSERT INTO Colaboradores (nome_colaborador, email_colaborador, senha, cargo, data_contratacao, status) VALUES
('Administrador do Sistema', 'admin@cliver.com', 'scrypt:32768:8:1$ROxeXhBfJLBKJm0s$4b5c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a', 'Administrador', '2025-01-01', 'Ativo'),
('João Silva Santos', 'joao.silva@cliver.com', 'scrypt:32768:8:1$ROxeXhBfJLBKJm0s$4b5c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a', 'Corretor Sênior', '2025-01-15', 'Ativo'),
('Maria Santos Oliveira', 'maria.santos@cliver.com', 'scrypt:32768:8:1$ROxeXhBfJLBKJm0s$4b5c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a', 'Corretora', '2025-02-01', 'Ativo'),
('Carlos Lima Pereira', 'carlos.lima@cliver.com', 'scrypt:32768:8:1$ROxeXhBfJLBKJm0s$4b5c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a4c4b1f6c4a', 'Corretor Júnior', '2025-02-15', 'Ativo');

PRINT '✅ Colaboradores inseridos!';

-- Inserir Clientes
INSERT INTO Clientes (nome, tipo_pessoa, documento, data_nascimento, email, telefone, endereco, cidade, estado, cep) VALUES
('João da Silva', 'Fisica', '123.456.789-00', '1980-05-15', 'joao@email.com', '(11) 99999-1234', 'Rua das Flores, 123', 'São Paulo', 'SP', '01234-567'),
('Maria Oliveira Santos', 'Fisica', '987.654.321-00', '1975-08-22', 'maria@email.com', '(11) 99999-5678', 'Av. Paulista, 456', 'São Paulo', 'SP', '01234-890'),
('Empresa XYZ Ltda', 'Juridica', '12.345.678/0001-90', NULL, 'contato@xyz.com.br', '(11) 3333-1234', 'Rua Comercial, 789', 'São Paulo', 'SP', '01234-123'),
('ABC Comércio e Serviços', 'Juridica', '98.765.432/0001-10', NULL, 'financeiro@abc.com.br', '(11) 3333-5678', 'Av. Industrial, 321', 'São Paulo', 'SP', '01234-456'),
('Pedro Santos Costa', 'Fisica', '456.789.123-00', '1990-12-10', 'pedro@email.com', '(11) 99999-9999', 'Rua da Paz, 555', 'São Paulo', 'SP', '01234-999'),
('Transportadora Rápida S/A', 'Juridica', '11.222.333/0001-44', NULL, 'seguros@transportadora.com', '(11) 4444-5555', 'Rodovia SP-100, Km 25', 'São Paulo', 'SP', '01234-000');

PRINT '✅ Clientes inseridos!';

COMMIT TRANSACTION;
GO

-- ===================================================
-- VISUALIZAÇÃO DOS DADOS
-- ===================================================

PRINT '📊 Resumo dos dados inseridos:';
SELECT 'Seguradoras' AS Tabela, COUNT(*) AS Total FROM Seguradoras
UNION ALL
SELECT 'Tipos_Seguro', COUNT(*) FROM Tipos_Seguro
UNION ALL
SELECT 'Colaboradores', COUNT(*) FROM Colaboradores
UNION ALL
SELECT 'Clientes', COUNT(*) FROM Clientes
UNION ALL
SELECT 'Apolices', COUNT(*) FROM Apolices
UNION ALL
SELECT 'Sinistros', COUNT(*) FROM Sinistros
UNION ALL
SELECT 'Tarefas', COUNT(*) FROM Tarefas;

PRINT '🎉 Banco de dados CorretoraSegurosDB criado e configurado com sucesso!';
PRINT '🚀 Sistema CLIVER Seguros pronto para usar!';
GO