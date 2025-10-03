-- Inserção de dados de teste para todas as tabelas principais
USE CorretoraSegurosDB;
GO

-- Seguradoras
INSERT INTO Seguradoras (nome_seguradora, cnpj_seguradora, contato_seguradora, email_seguradora)
VALUES ('Seguradora Alpha', '12.345.678/0001-99', '11999999999', 'contato@alpha.com');

-- Tipos de Seguro
INSERT INTO Tipos_Seguro (nome_tipo_seguro, descricao_tipo_seguro)
VALUES ('Auto', 'Seguro de automóveis'), ('Vida', 'Seguro de vida');

-- Clientes
INSERT INTO Clientes (nome, tipo_pessoa, documento, data_nascimento, email, telefone, endereco, cidade, estado, cep)
VALUES ('João da Silva', 'Fisica', '123.456.789-00', '1980-01-01', 'joao@email.com', '11988887777', 'Rua A, 100', 'São Paulo', 'SP', '01000-000');

-- Colaboradores
INSERT INTO Colaboradores (nome_colaborador, email_colaborador, senha, cargo, data_contratacao, status)
VALUES ('Maria Corretora', 'maria@corretora.com', 'senha123', 'Vendedora', '2020-05-10', 'Ativo');

-- Apólices
INSERT INTO Apolices (id_cliente, id_seguradora, id_tipo_seguro, id_colaborador, numero_apolice, data_inicio_vigencia, data_fim_vigencia, valor_premio, percentual_comissao_seguradora, percentual_comissao_colaborador, data_pagamento_comissao_corretora, data_pagamento_comissao_colaborador, status_apolice, observacoes)
VALUES (1, 1, 1, 1, 'APO123', '2024-01-01', '2025-01-01', 1500.00, 10.00, 5.00, '2024-02-01', '2024-02-10', 'Ativa', 'Apólice de teste');

-- Sinistros
INSERT INTO Sinistros (id_apolice, data_ocorrido, descricao_sinistro, status_sinistro, numero_processo_seguradora, valor_indenizacao, observacoes)
VALUES (1, '2024-06-01', 'Colisão traseira', 'Aberto', 'PROC001', 5000.00, 'Sinistro em análise');

-- Renovação de Apólices
INSERT INTO Renovacao_Apolices (id_apolice_antiga, data_prevista_renovacao, status_renovacao, observacoes)
VALUES (1, '2025-01-01', 'Pendente', 'Aguardando contato do cliente');

-- Tarefas
INSERT INTO Tarefas (id_colaborador, id_apolice, id_cliente, titulo_tarefa, descricao_tarefa, data_vencimento, prioridade, status_tarefa)
VALUES (1, 1, 1, 'Ligar para cliente', 'Confirmar interesse em renovação', '2024-12-15', 'Alta', 'Pendente');
GO

-- Consultas de teste
SELECT * FROM Seguradoras;
SELECT * FROM Tipos_Seguro;
SELECT * FROM Clientes;
SELECT * FROM Colaboradores;
SELECT * FROM Apolices;
SELECT * FROM Sinistros;
SELECT * FROM Renovacao_Apolices;
SELECT * FROM Tarefas;
GO
