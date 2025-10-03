-- ============================================
-- EXEMPLOS DE CONSULTAS - SISTEMA CLIVER SEGUROS
-- Versão: 3.0
-- Data: 01/10/2025
-- ============================================

/*
Este arquivo contém exemplos práticos de consultas SQL para o sistema CLIVER Seguros.
Estas consultas atendem às solicitações de:
- Listar todos os clientes
- Buscar apólices de um cliente específico
- Relatórios personalizados
- Análises de performance
- Segurança e auditoria
*/

-- ============================================
-- 1. CONSULTAS BÁSICAS SOLICITADAS
-- ============================================

-- ✅ LISTAR TODOS OS CLIENTES ATIVOS
SELECT 
    c.id_cliente,
    c.nome,
    c.cpf_cnpj,
    c.tipo_pessoa,
    c.telefone_principal,
    c.email,
    c.classificacao_cliente,
    c.potencial_vendas,
    c.status_relacionamento,
    c.origem_cliente,
    COUNT(a.id_apolice) as total_apolices,
    ISNULL(SUM(a.valor_premio), 0) as faturamento_total,
    c.data_ultimo_contato,
    c.proximo_contato
FROM Clientes c
LEFT JOIN Apolices a ON c.id_cliente = a.id_cliente AND a.status_apolice = 'ATIVA'
WHERE c.ativo = 1
GROUP BY c.id_cliente, c.nome, c.cpf_cnpj, c.tipo_pessoa, c.telefone_principal, 
         c.email, c.classificacao_cliente, c.potencial_vendas, c.status_relacionamento, 
         c.origem_cliente, c.data_ultimo_contato, c.proximo_contato
ORDER BY c.nome;

-- ✅ BUSCAR TODAS AS APÓLICES DE UM DETERMINADO CLIENTE
-- (Substituir @ClienteId pelo ID do cliente desejado)
DECLARE @ClienteId INT = 1; -- Exemplo: Cliente ID 1

SELECT 
    c.nome as cliente_nome,
    c.cpf_cnpj as cliente_documento,
    a.numero_apolice,
    a.data_emissao,
    a.data_inicio_vigencia,
    a.data_fim_vigencia,
    a.data_vencimento,
    ts.nome as tipo_seguro,
    ts.categoria as categoria_seguro,
    s.nome as seguradora,
    s.rating_seguradora,
    a.valor_premio,
    a.valor_comissao,
    a.percentual_comissao,
    a.forma_pagamento,
    a.numero_parcelas,
    a.status_apolice,
    u.nome_completo as vendedor_responsavel,
    a.observacoes
FROM Apolices a
INNER JOIN Clientes c ON a.id_cliente = c.id_cliente
INNER JOIN TiposSeguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
INNER JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
LEFT JOIN Usuarios u ON a.id_colaborador_vendedor = u.id_usuario
WHERE a.id_cliente = @ClienteId
ORDER BY a.data_emissao DESC;

-- ============================================
-- 2. CONSULTAS PARA CAMPOS PERSONALIZADOS
-- ============================================

-- 🎯 CLIENTES POR CLASSIFICAÇÃO E POTENCIAL DE VENDAS
SELECT 
    c.classificacao_cliente,
    c.potencial_vendas,
    COUNT(*) as quantidade_clientes,
    AVG(CASE WHEN c.data_ultimo_contato IS NULL THEN 999 
             ELSE DATEDIFF(day, c.data_ultimo_contato, GETDATE()) END) as media_dias_sem_contato,
    COUNT(CASE WHEN a.status_apolice = 'ATIVA' THEN 1 END) as clientes_com_apolice_ativa,
    ISNULL(SUM(a.valor_premio), 0) as faturamento_total_grupo
FROM Clientes c
LEFT JOIN Apolices a ON c.id_cliente = a.id_cliente AND a.status_apolice = 'ATIVA'
WHERE c.ativo = 1
GROUP BY c.classificacao_cliente, c.potencial_vendas
ORDER BY c.classificacao_cliente, c.potencial_vendas;

-- 🏢 ANÁLISE DE SEGURADORAS - PERFORMANCE PERSONALIZADA
SELECT 
    s.nome as seguradora,
    s.rating_seguradora,
    s.percentual_comissao_padrao,
    s.tempo_pagamento_sinistros,
    s.prazo_emissao_apolice,
    COUNT(a.id_apolice) as total_apolices_ativas,
    ISNULL(SUM(a.valor_premio), 0) as faturamento_total,
    ISNULL(AVG(a.valor_premio), 0) as ticket_medio,
    COUNT(si.id_sinistro) as total_sinistros,
    COUNT(CASE WHEN si.status_sinistro = 'ABERTO' THEN 1 END) as sinistros_abertos
FROM Seguradoras s
LEFT JOIN Apolices a ON s.id_seguradora = a.id_seguradora AND a.status_apolice = 'ATIVA'
LEFT JOIN Sinistros si ON a.id_apolice = si.id_apolice
WHERE s.ativo = 1
GROUP BY s.id_seguradora, s.nome, s.rating_seguradora, s.percentual_comissao_padrao,
         s.tempo_pagamento_sinistros, s.prazo_emissao_apolice
ORDER BY ISNULL(SUM(a.valor_premio), 0) DESC;

-- ============================================
-- 3. RELATÓRIOS PERSONALIZADOS
-- ============================================

-- 📊 DASHBOARD EXECUTIVO - MÉTRICAS GERAIS
SELECT 
    'Clientes Ativos' as metrica, 
    CAST(COUNT(*) AS NVARCHAR(50)) as valor
FROM Clientes WHERE ativo = 1
UNION ALL
SELECT 
    'Apólices Ativas' as metrica, 
    CAST(COUNT(*) AS NVARCHAR(50)) as valor
FROM Apolices WHERE status_apolice = 'ATIVA'
UNION ALL
SELECT 
    'Faturamento Ano Atual' as metrica, 
    'R$ ' + FORMAT(ISNULL(SUM(valor_premio), 0), 'N2', 'pt-BR') as valor
FROM Apolices 
WHERE status_apolice = 'ATIVA' AND YEAR(data_emissao) = YEAR(GETDATE())
UNION ALL
SELECT 
    'Comissões Pendentes' as metrica, 
    'R$ ' + FORMAT(ISNULL(SUM(valor_comissao), 0), 'N2', 'pt-BR') as valor
FROM Comissoes 
WHERE status_pagamento = 'PENDENTE'
UNION ALL
SELECT 
    'Sinistros Abertos' as metrica, 
    CAST(COUNT(*) AS NVARCHAR(50)) as valor
FROM Sinistros WHERE status_sinistro = 'ABERTO';

-- 🎯 ANÁLISE DE OPORTUNIDADES - CLIENTES SEM CONTATO
SELECT 
    c.nome,
    c.telefone_principal,
    c.email,
    c.classificacao_cliente,
    c.potencial_vendas,
    c.data_ultimo_contato,
    CASE 
        WHEN c.data_ultimo_contato IS NULL THEN 'Nunca contatado'
        ELSE CAST(DATEDIFF(day, c.data_ultimo_contato, GETDATE()) AS NVARCHAR(10)) + ' dias'
    END as tempo_sem_contato,
    c.proximo_contato,
    COUNT(a.id_apolice) as apolices_ativas,
    ISNULL(SUM(a.valor_premio), 0) as valor_apolices_ativas,
    c.observacoes
FROM Clientes c
LEFT JOIN Apolices a ON c.id_cliente = a.id_cliente AND a.status_apolice = 'ATIVA'
WHERE c.ativo = 1 
  AND (c.data_ultimo_contato IS NULL OR c.data_ultimo_contato < DATEADD(day, -30, GETDATE()))
  AND c.potencial_vendas IN ('ALTO', 'MEDIO')
GROUP BY c.id_cliente, c.nome, c.telefone_principal, c.email, c.classificacao_cliente,
         c.potencial_vendas, c.data_ultimo_contato, c.proximo_contato, c.observacoes
ORDER BY 
    CASE c.potencial_vendas WHEN 'ALTO' THEN 1 WHEN 'MEDIO' THEN 2 ELSE 3 END,
    CASE WHEN c.data_ultimo_contato IS NULL THEN 999 
         ELSE DATEDIFF(day, c.data_ultimo_contato, GETDATE()) END DESC;

-- 💰 TOP 10 CLIENTES POR FATURAMENTO
SELECT TOP 10
    c.nome,
    c.cpf_cnpj,
    c.telefone_principal,
    c.email,
    c.classificacao_cliente,
    COUNT(a.id_apolice) as total_apolices,
    SUM(a.valor_premio) as faturamento_total,
    AVG(a.valor_premio) as ticket_medio,
    MAX(a.data_emissao) as ultima_compra,
    DATEDIFF(day, MAX(a.data_emissao), GETDATE()) as dias_desde_ultima_compra
FROM Clientes c
INNER JOIN Apolices a ON c.id_cliente = a.id_cliente
WHERE a.status_apolice = 'ATIVA'
GROUP BY c.id_cliente, c.nome, c.cpf_cnpj, c.telefone_principal, 
         c.email, c.classificacao_cliente
ORDER BY SUM(a.valor_premio) DESC;

-- ============================================
-- 4. ANÁLISES DE PERFORMANCE
-- ============================================

-- 🏆 PERFORMANCE DE VENDEDORES
SELECT 
    u.nome_completo as vendedor,
    u.email as email_vendedor,
    u.perfil_acesso,
    COUNT(a.id_apolice) as total_vendas_ano,
    ISNULL(SUM(a.valor_premio), 0) as faturamento_ano,
    ISNULL(SUM(a.valor_comissao), 0) as comissoes_ano,
    ISNULL(AVG(a.valor_premio), 0) as ticket_medio,
    COUNT(DISTINCT a.id_cliente) as clientes_unicos,
    (SELECT COUNT(*) FROM Tarefas t 
     WHERE t.usuario_responsavel = u.id_usuario AND t.status_tarefa = 'PENDENTE') as tarefas_pendentes,
    u.ultimo_login,
    CASE 
        WHEN u.ultimo_login IS NULL THEN 'Nunca logou'
        ELSE CAST(DATEDIFF(day, u.ultimo_login, GETDATE()) AS NVARCHAR(10)) + ' dias atrás'
    END as ultimo_acesso
FROM Usuarios u
LEFT JOIN Apolices a ON u.id_usuario = a.id_colaborador_vendedor 
    AND YEAR(a.data_emissao) = YEAR(GETDATE())
    AND a.status_apolice = 'ATIVA'
WHERE u.perfil_acesso IN ('VENDEDOR', 'GERENTE') AND u.ativo = 1
GROUP BY u.id_usuario, u.nome_completo, u.email, u.perfil_acesso, u.ultimo_login
ORDER BY ISNULL(SUM(a.valor_premio), 0) DESC;

-- 📅 APÓLICES QUE VENCEM NOS PRÓXIMOS 30, 60 E 90 DIAS
SELECT 
    CASE 
        WHEN DATEDIFF(day, GETDATE(), a.data_fim_vigencia) <= 30 THEN 'Próximos 30 dias'
        WHEN DATEDIFF(day, GETDATE(), a.data_fim_vigencia) <= 60 THEN 'Próximos 60 dias'
        ELSE 'Próximos 90 dias'
    END as periodo_vencimento,
    a.numero_apolice,
    c.nome as cliente_nome,
    c.telefone_principal,
    c.email,
    s.nome as seguradora,
    ts.nome as tipo_seguro,
    a.data_fim_vigencia,
    a.valor_premio,
    DATEDIFF(day, GETDATE(), a.data_fim_vigencia) as dias_para_vencer,
    u.nome_completo as vendedor_responsavel,
    a.renovacao_automatica
FROM Apolices a
INNER JOIN Clientes c ON a.id_cliente = c.id_cliente
INNER JOIN Seguradoras s ON a.id_seguradora = s.id_seguradora
INNER JOIN TiposSeguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
LEFT JOIN Usuarios u ON a.id_colaborador_vendedor = u.id_usuario
WHERE a.status_apolice = 'ATIVA' 
  AND a.data_fim_vigencia <= DATEADD(day, 90, GETDATE())
  AND a.data_fim_vigencia >= GETDATE()
ORDER BY a.data_fim_vigencia;

-- ============================================
-- 5. ANÁLISES DE SINISTROS E SEGURANÇA
-- ============================================

-- 🚨 RELATÓRIO DE SINISTROS POR SEGURADORA
SELECT 
    s.nome as seguradora,
    s.rating_seguradora,
    s.tempo_pagamento_sinistros as prazo_pagamento_dias,
    COUNT(si.id_sinistro) as total_sinistros,
    COUNT(CASE WHEN si.status_sinistro = 'ABERTO' THEN 1 END) as sinistros_abertos,
    COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) as sinistros_deferidos,
    COUNT(CASE WHEN si.status_sinistro = 'INDEFERIDO' THEN 1 END) as sinistros_indeferidos,
    ISNULL(SUM(si.valor_prejuizo), 0) as valor_total_prejuizo,
    ISNULL(SUM(si.valor_indenizacao), 0) as valor_total_indenizacao,
    CASE 
        WHEN COUNT(si.id_sinistro) > 0 THEN 
            CAST(COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) * 100.0 / COUNT(si.id_sinistro) AS DECIMAL(5,2))
        ELSE 0 
    END as percentual_aprovacao
FROM Seguradoras s
LEFT JOIN Apolices a ON s.id_seguradora = a.id_seguradora
LEFT JOIN Sinistros si ON a.id_apolice = si.id_apolice
WHERE s.ativo = 1
GROUP BY s.id_seguradora, s.nome, s.rating_seguradora, s.tempo_pagamento_sinistros
ORDER BY COUNT(si.id_sinistro) DESC;

-- 🔍 AUDITORIA - ÚLTIMAS ATIVIDADES NO SISTEMA
SELECT TOP 20
    al.data_hora,
    al.tabela_afetada,
    al.acao,
    al.id_registro,
    al.usuario,
    al.ip_address,
    al.observacoes
FROM AuditoriaLog al
ORDER BY al.data_hora DESC;

-- ============================================
-- 6. CONSULTAS DE CRM E TAREFAS
-- ============================================

-- 📋 TAREFAS PENDENTES POR PRIORIDADE E USUÁRIO
SELECT 
    u.nome_completo as responsavel,
    t.prioridade,
    t.tipo_tarefa,
    t.categoria,
    COUNT(*) as quantidade_tarefas,
    MIN(t.data_prevista) as tarefa_mais_antiga,
    MAX(t.data_prevista) as tarefa_mais_recente,
    COUNT(CASE WHEN t.data_prevista < GETDATE() THEN 1 END) as tarefas_atrasadas
FROM Usuarios u
INNER JOIN Tarefas t ON u.id_usuario = t.usuario_responsavel
WHERE t.status_tarefa = 'PENDENTE' AND u.ativo = 1
GROUP BY u.id_usuario, u.nome_completo, t.prioridade, t.tipo_tarefa, t.categoria
ORDER BY 
    CASE t.prioridade 
        WHEN 'URGENTE' THEN 1 
        WHEN 'ALTA' THEN 2 
        WHEN 'MÉDIA' THEN 3 
        ELSE 4 
    END,
    COUNT(CASE WHEN t.data_prevista < GETDATE() THEN 1 END) DESC;

-- 💼 HISTÓRICO DE INTERAÇÕES POR CLIENTE
SELECT 
    c.nome as cliente,
    t.data_criacao as data_interacao,
    t.tipo_tarefa,
    t.titulo,
    t.descricao,
    t.resultado,
    t.status_tarefa,
    u.nome_completo as responsavel
FROM Clientes c
LEFT JOIN Tarefas t ON c.id_cliente = t.id_cliente
LEFT JOIN Usuarios u ON t.usuario_responsavel = u.id_usuario
WHERE c.ativo = 1
  AND t.id_tarefa IS NOT NULL
ORDER BY c.nome, t.data_criacao DESC;

-- ============================================
-- 7. ANÁLISES FINANCEIRAS
-- ============================================

-- 💰 FATURAMENTO POR TIPO DE SEGURO NO ANO
SELECT 
    ts.categoria,
    ts.nome as tipo_seguro,
    COUNT(a.id_apolice) as quantidade_vendida,
    SUM(a.valor_premio) as faturamento_total,
    AVG(a.valor_premio) as ticket_medio,
    SUM(a.valor_comissao) as comissao_total,
    MIN(a.valor_premio) as menor_premio,
    MAX(a.valor_premio) as maior_premio
FROM TiposSeguro ts
INNER JOIN Apolices a ON ts.id_tipo_seguro = a.id_tipo_seguro
WHERE YEAR(a.data_emissao) = YEAR(GETDATE()) 
  AND a.status_apolice = 'ATIVA'
GROUP BY ts.categoria, ts.nome
ORDER BY SUM(a.valor_premio) DESC;

-- 💳 COMISSÕES A RECEBER POR VENDEDOR
SELECT 
    u.nome_completo as vendedor,
    COUNT(co.id_comissao) as total_comissoes_pendentes,
    SUM(co.valor_comissao) as valor_total_pendente,
    MIN(co.data_vencimento) as primeira_comissao_vence,
    MAX(co.data_vencimento) as ultima_comissao_vence,
    COUNT(CASE WHEN co.data_vencimento < GETDATE() THEN 1 END) as comissoes_vencidas,
    SUM(CASE WHEN co.data_vencimento < GETDATE() THEN co.valor_comissao ELSE 0 END) as valor_vencido
FROM Usuarios u
INNER JOIN Comissoes co ON u.id_usuario = co.id_colaborador
WHERE co.status_pagamento = 'PENDENTE' AND u.ativo = 1
GROUP BY u.id_usuario, u.nome_completo
ORDER BY SUM(co.valor_comissao) DESC;

-- ============================================
-- 8. CONSULTAS DE CONTROLE E CONFIGURAÇÃO
-- ============================================

-- ⚙️ CONFIGURAÇÕES ATUAIS DO SISTEMA
SELECT 
    cs.categoria,
    cs.chave,
    cs.valor,
    cs.descricao,
    cs.ativo,
    cs.data_atualizacao
FROM ConfiguracaoSistema cs
WHERE cs.ativo = 1
ORDER BY cs.categoria, cs.chave;

-- 👥 USUÁRIOS ATIVOS E SEUS PERFIS
SELECT 
    u.nome_completo as usuario,
    u.login,
    u.email,
    u.telefone,
    u.perfil_acesso,
    u.ultimo_login,
    u.tentativas_login,
    CASE WHEN u.bloqueado = 1 THEN 'BLOQUEADO' ELSE 'ATIVO' END as status_conta,
    COUNT(a.id_apolice) as total_vendas_historico,
    ISNULL(SUM(a.valor_comissao), 0) as total_comissoes_historico
FROM Usuarios u
LEFT JOIN Apolices a ON u.id_usuario = a.id_colaborador_vendedor AND a.status_apolice = 'ATIVA'
WHERE u.ativo = 1
GROUP BY u.id_usuario, u.nome_completo, u.login, u.email, u.telefone, 
         u.perfil_acesso, u.ultimo_login, u.tentativas_login, u.bloqueado
ORDER BY u.perfil_acesso, u.nome_completo;

-- ============================================
-- EXEMPLO DE USO DAS CONSULTAS:
-- ============================================

/*
Para usar estas consultas:

1. CONSULTA BÁSICA - Todos os clientes:
   Copie e execute a primeira consulta para ver todos os clientes ativos

2. APÓLICES DE UM CLIENTE:
   Modifique a variável @ClienteId para o ID desejado e execute

3. RELATÓRIOS PERSONALIZADOS:
   Execute qualquer consulta da seção de relatórios conforme necessário

4. ANÁLISES DE PERFORMANCE:
   Use as consultas de performance para avaliar vendedores e oportunidades

5. CONTROLE DE SEGURANÇA:
   Execute as consultas de auditoria para monitorar atividades do sistema

Todas as consultas incluem tratamento de valores nulos e formatação adequada.
*/

-- Fim do arquivo de consultas de exemplo