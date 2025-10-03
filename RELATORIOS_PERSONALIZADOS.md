# 📊 RELATÓRIOS PERSONALIZADOS - SISTEMA CLIVER SEGUROS

## **🎯 RELATÓRIOS PARA ANÁLISE DE PERFORMANCE**

### **📈 1. RELATÓRIO EXECUTIVO - DASHBOARD KPIs**

```sql
-- KPIs Principais do Negócio
SELECT 
    -- Métricas de Clientes
    (SELECT COUNT(*) FROM Clientes WHERE ativo = 1) as clientes_ativos,
    (SELECT COUNT(*) FROM Clientes WHERE ativo = 1 AND data_cadastro >= DATEADD(month, -1, GETDATE())) as novos_clientes_mes,
    
    -- Métricas de Apólices
    (SELECT COUNT(*) FROM Apolices WHERE status_apolice = 'ATIVA') as apolices_ativas,
    (SELECT COUNT(*) FROM Apolices WHERE data_emissao >= DATEADD(month, -1, GETDATE())) as apolices_mes,
    
    -- Métricas Financeiras
    (SELECT ISNULL(SUM(valor_premio), 0) FROM Apolices 
     WHERE YEAR(data_emissao) = YEAR(GETDATE()) AND status_apolice = 'ATIVA') as faturamento_ano,
    (SELECT ISNULL(SUM(valor_premio), 0) FROM Apolices 
     WHERE MONTH(data_emissao) = MONTH(GETDATE()) AND YEAR(data_emissao) = YEAR(GETDATE())) as faturamento_mes,
    
    -- Métricas de Comissões
    (SELECT ISNULL(SUM(valor_comissao), 0) FROM Comissoes WHERE status_pagamento = 'PENDENTE') as comissoes_a_receber,
    (SELECT ISNULL(SUM(valor_comissao), 0) FROM Comissoes 
     WHERE status_pagamento = 'PAGO' AND YEAR(data_pagamento) = YEAR(GETDATE())) as comissoes_recebidas_ano,
    
    -- Métricas Operacionais
    (SELECT COUNT(*) FROM Sinistros WHERE status_sinistro = 'ABERTO') as sinistros_abertos,
    (SELECT COUNT(*) FROM Tarefas WHERE status_tarefa = 'PENDENTE' AND data_prevista < GETDATE()) as tarefas_atrasadas,
    (SELECT COUNT(*) FROM Renovacoes WHERE status_renovacao = 'PENDENTE' 
     AND data_vencimento <= DATEADD(day, 30, GETDATE())) as renovacoes_urgentes;
```

---

### **🏆 2. RELATÓRIO DE PERFORMANCE DE VENDEDORES**

```sql
-- Ranking de Vendedores por Performance
SELECT 
    ROW_NUMBER() OVER (ORDER BY ISNULL(SUM(a.valor_premio), 0) DESC) as ranking,
    u.nome_completo as vendedor,
    u.email,
    
    -- Métricas de Vendas
    COUNT(a.id_apolice) as total_vendas_ano,
    ISNULL(SUM(a.valor_premio), 0) as faturamento_ano,
    ISNULL(AVG(a.valor_premio), 0) as ticket_medio,
    COUNT(DISTINCT a.id_cliente) as clientes_unicos,
    
    -- Métricas de Comissão
    ISNULL(SUM(a.valor_comissao), 0) as comissoes_ano,
    ISNULL(AVG(a.percentual_comissao), 0) as percentual_comissao_medio,
    
    -- Métricas de Produtividade
    COUNT(CASE WHEN a.data_emissao >= DATEADD(month, -1, GETDATE()) THEN 1 END) as vendas_ultimo_mes,
    (SELECT COUNT(*) FROM Tarefas t WHERE t.usuario_responsavel = u.id_usuario 
     AND t.status_tarefa = 'CONCLUÍDA' AND t.data_conclusao >= DATEADD(month, -1, GETDATE())) as tarefas_concluidas_mes,
    (SELECT COUNT(*) FROM Tarefas t WHERE t.usuario_responsavel = u.id_usuario 
     AND t.status_tarefa = 'PENDENTE') as tarefas_pendentes,
    
    -- Métricas de Relacionamento
    u.ultimo_login,
    CASE 
        WHEN u.ultimo_login >= DATEADD(day, -7, GETDATE()) THEN 'Ativo'
        WHEN u.ultimo_login >= DATEADD(day, -30, GETDATE()) THEN 'Regular' 
        ELSE 'Inativo'
    END as status_atividade

FROM Usuarios u
LEFT JOIN Apolices a ON u.id_usuario = a.id_colaborador_vendedor 
    AND YEAR(a.data_emissao) = YEAR(GETDATE()) 
    AND a.status_apolice = 'ATIVA'
WHERE u.perfil_acesso IN ('VENDEDOR', 'GERENTE') 
  AND u.ativo = 1
GROUP BY u.id_usuario, u.nome_completo, u.email, u.ultimo_login
ORDER BY ISNULL(SUM(a.valor_premio), 0) DESC;
```

---

### **💰 3. RELATÓRIO FINANCEIRO DETALHADO**

```sql
-- Análise Financeira Completa
WITH FaturamentoMensal AS (
    SELECT 
        YEAR(data_emissao) as ano,
        MONTH(data_emissao) as mes,
        COUNT(*) as quantidade_apolices,
        SUM(valor_premio) as faturamento_mes,
        SUM(valor_comissao) as comissao_mes,
        AVG(valor_premio) as ticket_medio_mes
    FROM Apolices
    WHERE status_apolice = 'ATIVA' 
      AND data_emissao >= DATEADD(month, -12, GETDATE())
    GROUP BY YEAR(data_emissao), MONTH(data_emissao)
)
SELECT 
    fm.ano,
    fm.mes,
    DATENAME(month, DATEFROMPARTS(fm.ano, fm.mes, 1)) + '/' + CAST(fm.ano AS NVARCHAR) as periodo,
    fm.quantidade_apolices,
    fm.faturamento_mes,
    fm.comissao_mes,
    fm.ticket_medio_mes,
    
    -- Crescimento em relação ao mês anterior
    LAG(fm.faturamento_mes) OVER (ORDER BY fm.ano, fm.mes) as faturamento_mes_anterior,
    CASE 
        WHEN LAG(fm.faturamento_mes) OVER (ORDER BY fm.ano, fm.mes) > 0 THEN
            ROUND(((fm.faturamento_mes - LAG(fm.faturamento_mes) OVER (ORDER BY fm.ano, fm.mes)) * 100.0 / 
                   LAG(fm.faturamento_mes) OVER (ORDER BY fm.ano, fm.mes)), 2)
        ELSE 0
    END as crescimento_percentual,
    
    -- Acumulado no ano
    SUM(fm.faturamento_mes) OVER (
        PARTITION BY fm.ano 
        ORDER BY fm.mes 
        ROWS UNBOUNDED PRECEDING
    ) as faturamento_acumulado_ano

FROM FaturamentoMensal fm
ORDER BY fm.ano DESC, fm.mes DESC;
```

---

### **🎯 4. RELATÓRIO DE OPORTUNIDADES COMERCIAIS**

```sql
-- Identificação de Oportunidades de Negócio
SELECT 
    'Clientes VIP sem contato há 30+ dias' as oportunidade,
    COUNT(*) as quantidade,
    ISNULL(SUM(historico.valor_total_apolices), 0) as potencial_faturamento
FROM Clientes c
LEFT JOIN (
    SELECT 
        a.id_cliente,
        SUM(a.valor_premio) as valor_total_apolices
    FROM Apolices a 
    WHERE a.status_apolice = 'ATIVA' 
    GROUP BY a.id_cliente
) historico ON c.id_cliente = historico.id_cliente
WHERE c.ativo = 1 
  AND c.classificacao_cliente = 'VIP'
  AND (c.data_ultimo_contato IS NULL OR c.data_ultimo_contato < DATEADD(day, -30, GETDATE()))

UNION ALL

SELECT 
    'Clientes com potencial ALTO sem apólices ativas' as oportunidade,
    COUNT(*) as quantidade,
    0 as potencial_faturamento
FROM Clientes c
WHERE c.ativo = 1 
  AND c.potencial_vendas = 'ALTO'
  AND NOT EXISTS (SELECT 1 FROM Apolices a WHERE a.id_cliente = c.id_cliente AND a.status_apolice = 'ATIVA')

UNION ALL

SELECT 
    'Apólices vencendo em 30 dias (renovação)' as oportunidade,
    COUNT(*) as quantidade,
    SUM(a.valor_premio) as potencial_faturamento
FROM Apolices a
WHERE a.status_apolice = 'ATIVA'
  AND a.data_fim_vigencia BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
  AND a.renovacao_automatica = 1

UNION ALL

SELECT 
    'Clientes com apenas 1 tipo de seguro (cross-sell)' as oportunidade,
    COUNT(DISTINCT c.id_cliente) as quantidade,
    0 as potencial_faturamento
FROM Clientes c
INNER JOIN Apolices a ON c.id_cliente = a.id_cliente
WHERE c.ativo = 1 AND a.status_apolice = 'ATIVA'
GROUP BY c.id_cliente
HAVING COUNT(DISTINCT a.id_tipo_seguro) = 1;
```

---

### **📋 5. RELATÓRIO DE SATISFAÇÃO E RETENÇÃO**

```sql
-- Análise de Satisfação do Cliente
WITH AnaliseCliente AS (
    SELECT 
        c.id_cliente,
        c.nome,
        c.classificacao_cliente,
        c.data_cadastro,
        DATEDIFF(month, c.data_cadastro, GETDATE()) as meses_como_cliente,
        
        -- Métricas de Apólices
        COUNT(a.id_apolice) as total_apolices,
        COUNT(CASE WHEN a.status_apolice = 'ATIVA' THEN 1 END) as apolices_ativas,
        COUNT(CASE WHEN a.status_apolice = 'CANCELADA' THEN 1 END) as apolices_canceladas,
        ISNULL(SUM(CASE WHEN a.status_apolice = 'ATIVA' THEN a.valor_premio END), 0) as valor_apolices_ativas,
        
        -- Métricas de Sinistros
        COUNT(s.id_sinistro) as total_sinistros,
        COUNT(CASE WHEN s.status_sinistro = 'DEFERIDO' THEN 1 END) as sinistros_aprovados,
        COUNT(CASE WHEN s.status_sinistro = 'INDEFERIDO' THEN 1 END) as sinistros_negados,
        
        -- Métricas de Relacionamento
        c.data_ultimo_contato,
        COUNT(t.id_tarefa) as total_interacoes,
        
        -- Métricas de Renovação
        COUNT(r.id_renovacao) as total_renovacoes,
        COUNT(CASE WHEN r.status_renovacao = 'RENOVADA' THEN 1 END) as renovacoes_sucesso
        
    FROM Clientes c
    LEFT JOIN Apolices a ON c.id_cliente = a.id_cliente
    LEFT JOIN Sinistros s ON a.id_apolice = s.id_apolice
    LEFT JOIN Tarefas t ON c.id_cliente = t.id_cliente
    LEFT JOIN Renovacoes r ON a.id_apolice = r.id_apolice_original
    WHERE c.ativo = 1
    GROUP BY c.id_cliente, c.nome, c.classificacao_cliente, c.data_cadastro, c.data_ultimo_contato
)
SELECT 
    ac.classificacao_cliente,
    COUNT(*) as total_clientes,
    AVG(ac.meses_como_cliente) as media_meses_cliente,
    AVG(CAST(ac.total_apolices AS FLOAT)) as media_apolices_por_cliente,
    AVG(ac.valor_apolices_ativas) as media_valor_por_cliente,
    
    -- Taxa de Retenção
    CASE 
        WHEN SUM(ac.total_renovacoes) > 0 THEN
            ROUND(CAST(SUM(ac.renovacoes_sucesso) AS FLOAT) * 100 / SUM(ac.total_renovacoes), 2)
        ELSE 0 
    END as taxa_renovacao_percentual,
    
    -- Taxa de Sinistralidade
    CASE 
        WHEN SUM(ac.total_sinistros) > 0 THEN
            ROUND(CAST(SUM(ac.sinistros_aprovados) AS FLOAT) * 100 / SUM(ac.total_sinistros), 2)
        ELSE 0 
    END as taxa_aprovacao_sinistros,
    
    -- Engajamento
    AVG(ac.total_interacoes) as media_interacoes_por_cliente,
    COUNT(CASE WHEN ac.data_ultimo_contato >= DATEADD(day, -30, GETDATE()) THEN 1 END) as clientes_contato_recente,
    
    -- Status de Risco
    COUNT(CASE WHEN ac.apolices_canceladas > 0 THEN 1 END) as clientes_com_cancelamento,
    COUNT(CASE WHEN ac.data_ultimo_contato < DATEADD(day, -90, GETDATE()) THEN 1 END) as clientes_sem_contato_90dias

FROM AnaliseCliente ac
GROUP BY ac.classificacao_cliente
ORDER BY COUNT(*) DESC;
```

---

### **🚨 6. RELATÓRIO DE SINISTROS E RISCOS**

```sql
-- Análise Detalhada de Sinistros
SELECT 
    s.nome as seguradora,
    ts.categoria as categoria_seguro,
    ts.nome as tipo_seguro,
    
    -- Métricas de Sinistros
    COUNT(si.id_sinistro) as total_sinistros,
    COUNT(CASE WHEN si.status_sinistro = 'ABERTO' THEN 1 END) as sinistros_abertos,
    COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) as sinistros_aprovados,
    COUNT(CASE WHEN si.status_sinistro = 'INDEFERIDO' THEN 1 END) as sinistros_negados,
    
    -- Valores
    ISNULL(SUM(si.valor_prejuizo), 0) as valor_total_prejuizo,
    ISNULL(SUM(si.valor_indenizacao), 0) as valor_total_indenizacao,
    ISNULL(AVG(si.valor_prejuizo), 0) as valor_medio_prejuizo,
    
    -- Taxa de Aprovação
    CASE 
        WHEN COUNT(si.id_sinistro) > 0 THEN
            ROUND(CAST(COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) AS FLOAT) * 100 / 
                  COUNT(si.id_sinistro), 2)
        ELSE 0 
    END as taxa_aprovacao_percentual,
    
    -- Tempo Médio de Resolução
    AVG(CASE 
        WHEN si.data_conclusao IS NOT NULL THEN 
            DATEDIFF(day, si.data_ocorrencia, si.data_conclusao)
        ELSE NULL 
    END) as tempo_medio_resolucao_dias,
    
    -- Sinistros por Tipo
    COUNT(CASE WHEN si.tipo_sinistro = 'ROUBO' THEN 1 END) as sinistros_roubo,
    COUNT(CASE WHEN si.tipo_sinistro = 'ACIDENTE' THEN 1 END) as sinistros_acidente,
    COUNT(CASE WHEN si.tipo_sinistro = 'INCÊNDIO' THEN 1 END) as sinistros_incendio

FROM Seguradoras s
LEFT JOIN Apolices a ON s.id_seguradora = a.id_seguradora
LEFT JOIN TiposSeguro ts ON a.id_tipo_seguro = ts.id_tipo_seguro
LEFT JOIN Sinistros si ON a.id_apolice = si.id_apolice
WHERE s.ativo = 1
GROUP BY s.id_seguradora, s.nome, ts.categoria, ts.nome
HAVING COUNT(si.id_sinistro) > 0
ORDER BY COUNT(si.id_sinistro) DESC;
```

---

### **📞 7. RELATÓRIO DE CRM E RELACIONAMENTO**

```sql
-- Análise de Atividades de CRM
WITH AtividadeCRM AS (
    SELECT 
        u.nome_completo as responsavel,
        t.tipo_tarefa,
        t.categoria,
        t.prioridade,
        COUNT(*) as total_tarefas,
        COUNT(CASE WHEN t.status_tarefa = 'CONCLUÍDA' THEN 1 END) as tarefas_concluidas,
        COUNT(CASE WHEN t.status_tarefa = 'PENDENTE' THEN 1 END) as tarefas_pendentes,
        COUNT(CASE WHEN t.status_tarefa = 'PENDENTE' AND t.data_prevista < GETDATE() THEN 1 END) as tarefas_atrasadas,
        AVG(CASE 
            WHEN t.status_tarefa = 'CONCLUÍDA' AND t.data_conclusao IS NOT NULL THEN 
                DATEDIFF(day, t.data_criacao, t.data_conclusao)
            ELSE NULL 
        END) as tempo_medio_conclusao_dias
    FROM Usuarios u
    LEFT JOIN Tarefas t ON u.id_usuario = t.usuario_responsavel
    WHERE u.ativo = 1 AND u.perfil_acesso IN ('VENDEDOR', 'GERENTE')
    GROUP BY u.id_usuario, u.nome_completo, t.tipo_tarefa, t.categoria, t.prioridade
)
SELECT 
    ac.responsavel,
    ac.tipo_tarefa,
    ac.categoria,
    ac.prioridade,
    ac.total_tarefas,
    ac.tarefas_concluidas,
    ac.tarefas_pendentes,
    ac.tarefas_atrasadas,
    
    -- Taxa de Conclusão
    CASE 
        WHEN ac.total_tarefas > 0 THEN
            ROUND(CAST(ac.tarefas_concluidas AS FLOAT) * 100 / ac.total_tarefas, 2)
        ELSE 0 
    END as taxa_conclusao_percentual,
    
    -- Produtividade
    ac.tempo_medio_conclusao_dias,
    
    -- Status de Performance
    CASE 
        WHEN ac.tarefas_atrasadas = 0 AND ac.tarefas_pendentes <= 5 THEN 'EXCELENTE'
        WHEN ac.tarefas_atrasadas <= 2 AND ac.tarefas_pendentes <= 10 THEN 'BOM'
        WHEN ac.tarefas_atrasadas <= 5 THEN 'REGULAR'
        ELSE 'CRÍTICO'
    END as status_performance

FROM AtividadeCRM ac
WHERE ac.total_tarefas > 0
ORDER BY ac.responsavel, 
         CASE ac.prioridade 
             WHEN 'URGENTE' THEN 1 
             WHEN 'ALTA' THEN 2 
             WHEN 'MÉDIA' THEN 3 
             ELSE 4 
         END;
```

---

### **📊 8. RELATÓRIO COMPARATIVO DE SEGURADORAS**

```sql
-- Benchmarking de Seguradoras
SELECT 
    s.nome as seguradora,
    s.rating_seguradora,
    s.percentual_comissao_padrao,
    s.tempo_pagamento_sinistros,
    s.prazo_emissao_apolice,
    
    -- Volume de Negócios
    COUNT(a.id_apolice) as total_apolices,
    ISNULL(SUM(a.valor_premio), 0) as faturamento_total,
    ISNULL(AVG(a.valor_premio), 0) as ticket_medio,
    
    -- Performance de Sinistros
    COUNT(si.id_sinistro) as total_sinistros,
    CASE 
        WHEN COUNT(si.id_sinistro) > 0 THEN
            ROUND(CAST(COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) AS FLOAT) * 100 / 
                  COUNT(si.id_sinistro), 2)
        ELSE 0 
    END as taxa_aprovacao_sinistros,
    
    -- Tempo de Resposta
    AVG(CASE 
        WHEN si.data_conclusao IS NOT NULL THEN 
            DATEDIFF(day, si.data_comunicacao, si.data_conclusao)
        ELSE NULL 
    END) as tempo_medio_resposta_sinistros,
    
    -- Rentabilidade para Corretora
    ISNULL(SUM(a.valor_comissao), 0) as comissao_total_gerada,
    
    -- Market Share
    ROUND(CAST(COUNT(a.id_apolice) AS FLOAT) * 100 / 
          (SELECT COUNT(*) FROM Apolices WHERE status_apolice = 'ATIVA'), 2) as market_share_percentual,
    
    -- Score Geral (0-100)
    (
        CASE s.rating_seguradora 
            WHEN 'AAA' THEN 25 
            WHEN 'AA' THEN 20 
            WHEN 'A' THEN 15 
            ELSE 10 
        END +
        CASE 
            WHEN s.percentual_comissao_padrao >= 20 THEN 25
            WHEN s.percentual_comissao_padrao >= 15 THEN 20
            WHEN s.percentual_comissao_padrao >= 10 THEN 15
            ELSE 10
        END +
        CASE 
            WHEN COUNT(si.id_sinistro) > 0 AND 
                 CAST(COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) AS FLOAT) * 100 / COUNT(si.id_sinistro) >= 80 THEN 25
            WHEN COUNT(si.id_sinistro) > 0 AND 
                 CAST(COUNT(CASE WHEN si.status_sinistro = 'DEFERIDO' THEN 1 END) AS FLOAT) * 100 / COUNT(si.id_sinistro) >= 60 THEN 20
            ELSE 15
        END +
        CASE 
            WHEN s.tempo_pagamento_sinistros <= 15 THEN 25
            WHEN s.tempo_pagamento_sinistros <= 30 THEN 20
            ELSE 15
        END
    ) as score_geral

FROM Seguradoras s
LEFT JOIN Apolices a ON s.id_seguradora = a.id_seguradora AND a.status_apolice = 'ATIVA'
LEFT JOIN Sinistros si ON a.id_apolice = si.id_apolice
WHERE s.ativo = 1
GROUP BY s.id_seguradora, s.nome, s.rating_seguradora, s.percentual_comissao_padrao,
         s.tempo_pagamento_sinistros, s.prazo_emissao_apolice
ORDER BY (
    CASE s.rating_seguradora WHEN 'AAA' THEN 25 WHEN 'AA' THEN 20 WHEN 'A' THEN 15 ELSE 10 END +
    CASE WHEN s.percentual_comissao_padrao >= 20 THEN 25 WHEN s.percentual_comissao_padrao >= 15 THEN 20 WHEN s.percentual_comissao_padrao >= 10 THEN 15 ELSE 10 END +
    25 + -- Score de sinistros (simplificado)
    CASE WHEN s.tempo_pagamento_sinistros <= 15 THEN 25 WHEN s.tempo_pagamento_sinistros <= 30 THEN 20 ELSE 15 END
) DESC;
```

---

## **🎯 COMO USAR OS RELATÓRIOS**

### **📋 Instruções de Implementação**

1. **Copie e cole** qualquer consulta no SQL Server Management Studio
2. **Execute** para obter resultados imediatos
3. **Exporte** para Excel/PDF conforme necessário
4. **Agende** execução automática para relatórios regulares
5. **Personalize** filtros de data/usuário conforme necessidade

### **📊 Frequência Sugerida**

- **Dashboard KPIs**: Diário
- **Performance Vendedores**: Semanal/Mensal
- **Financeiro**: Mensal
- **Oportunidades**: Semanal
- **Satisfação**: Trimestral
- **Sinistros**: Mensal
- **CRM**: Semanal
- **Seguradoras**: Trimestral

### **🎨 Integração com Sistema CLIVER**

Estes relatórios podem ser integrados diretamente nas telas do sistema Flask, criando dashboards interativos com gráficos e filtros personalizáveis.

**✅ Todos os relatórios estão prontos para uso imediato!**