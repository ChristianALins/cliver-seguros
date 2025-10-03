# 📊 DIAGRAMA DE RELACIONAMENTOS - ESTRUTURA CORRIGIDA

## 🏗️ **VISÃO GERAL DA ARQUITETURA**

```
                    SISTEMA CORRETORA DE SEGUROS
                         Estrutura Normalizada
    
    ┌─────────────────────────────────────────────────────────────────┐
    │                     ENTIDADES PRINCIPAIS                        │
    └─────────────────────────────────────────────────────────────────┘
    
    SEGURADORAS ──────┐
    │ id_seguradora    │
    │ nome_seguradora  │◄────┐
    │ especialidades   │     │
    │ condicoes_pag    │     │
    └─────────────────┘     │
                            │
    PRODUTOS ───────────────┘
    │ id_produto        │
    │ id_seguradora (FK)│
    │ tipo_seguro       │◄──────────┐
    │ cobertura         │           │
    │ franquia          │           │
    │ valor_min/max     │           │
    └──────────────────┘           │
            │                      │
            │ M:N                  │ M:N
            ▼                      ▼
    ┌──────────────────┐    ┌──────────────────┐
    │ PROPOSTA_PRODUTOS│    │ APOLICE_PRODUTOS │
    │ id_proposta (FK) │    │ id_apolice (FK)  │
    │ id_produto (FK)  │    │ id_produto (FK)  │
    │ valor_unitario   │    │ valor_unitario   │
    └─────────┬────────┘    └────────┬─────────┘
              │                      │
              ▼ 1:N                  ▼ 1:N
    ┌─────────────────┐      ┌─────────────────┐
    │   PROPOSTAS     │ 1:1  │    APOLICES     │
    │ id_proposta     │─────▶│ id_apolice      │
    │ numero_proposta │      │ numero_apolice  │
    │ id_cliente (FK) │◄──┐  │ id_proposta(FK) │
    │ status_proposta │   │  │ data_emissao    │
    │ data_proposta   │   │  │ validade        │
    └─────────────────┘   │  │ id_cliente (FK) │◄──┐
                          │  │ id_seguradora   │   │
                          │  └─────────┬───────┘   │
                          │            │           │
    ┌─────────────────┐   │            │ 1:N       │
    │    CLIENTES     │───┘            │           │
    │ id_cliente      │◄───────────────┘           │
    │ nome            │                            │
    │ cpf_cnpj        │◄───────────────────────────┘
    │ data_nascimento │
    │ endereco        │
    │ telefone        │
    └─────────┬───────┘
              │
              │ 1:N (histórico)
              ▼
    ┌─────────────────┐
    │    TAREFAS      │
    │ id_tarefa       │
    │ id_cliente (FK) │
    │ titulo_tarefa   │
    └─────────────────┘
```

## 🔗 **FLUXO DE RELACIONAMENTOS DETALHADO**

### **📋 FLUXO COMERCIAL**
```
1. CLIENTE faz solicitação
    ↓
2. COLABORADOR cria PROPOSTA
    ↓
3. PROPOSTA vincula PRODUTOS (M:N via Proposta_Produtos)
    ↓
4. SEGURADORA analisa PROPOSTA
    ↓ (se aprovada)
5. PROPOSTA gera APÓLICE
    ↓
6. APÓLICE herda PRODUTOS (M:N via Apolice_Produtos)
    ↓
7. APÓLICE gera PAGAMENTOS (parcelas)
    ↓ (se necessário)
8. CLIENTE aciona seguro → SINISTRO
```

### **💰 FLUXO FINANCEIRO**
```
APÓLICE
├── PAGAMENTOS (N parcelas)
│   ├── data_vencimento
│   ├── valor_parcela
│   ├── forma_pagamento
│   └── status_pagamento
│
├── COMISSÕES (calculadas)
│   ├── valor_comissao_corretora
│   └── valor_comissao_colaborador
│
└── SINISTROS (se houver)
    ├── valor_sinistro
    ├── valor_franquia
    └── valor_indenizacao
```

## 📊 **MATRIZ DE RELACIONAMENTOS**

| **Tabela Origem** | **Tabela Destino** | **Tipo** | **Cardinalidade** | **FK** |
|-------------------|-------------------|----------|-------------------|---------|
| Seguradoras | Produtos | 1:N | 1 Seguradora → N Produtos | id_seguradora |
| Produtos | Proposta_Produtos | 1:N | 1 Produto → N Propostas | id_produto |
| Propostas | Proposta_Produtos | 1:N | 1 Proposta → N Produtos | id_proposta |
| Clientes | Propostas | 1:N | 1 Cliente → N Propostas | id_cliente |
| Colaboradores | Propostas | 1:N | 1 Colaborador → N Propostas | id_colaborador |
| Seguradoras | Propostas | 1:N | 1 Seguradora → N Propostas | id_seguradora |
| Propostas | Apolices | 1:1 | 1 Proposta → 1 Apólice | id_proposta |
| Clientes | Apolices | 1:N | 1 Cliente → N Apólices | id_cliente |
| Seguradoras | Apolices | 1:N | 1 Seguradora → N Apólices | id_seguradora |
| Colaboradores | Apolices | 1:N | 1 Colaborador → N Apólices | id_colaborador |
| Apolices | Apolice_Produtos | 1:N | 1 Apólice → N Produtos | id_apolice |
| Produtos | Apolice_Produtos | 1:N | 1 Produto → N Apólices | id_produto |
| Apolices | Pagamentos | 1:N | 1 Apólice → N Pagamentos | id_apolice |
| Apolices | Sinistros | 1:N | 1 Apólice → N Sinistros | id_apolice |
| Apolices | Renovacao_Apolices | 1:N | 1 Apólice → N Renovações | id_apolice |
| Clientes | Tarefas | 1:N | 1 Cliente → N Tarefas | id_cliente |
| Apolices | Tarefas | 1:N | 1 Apólice → N Tarefas | id_apolice |
| Propostas | Tarefas | 1:N | 1 Proposta → N Tarefas | id_proposta |
| Colaboradores | Tarefas | 1:N | 1 Colaborador → N Tarefas | id_colaborador |

## 🎯 **PONTOS CHAVE DA ARQUITETURA**

### **✅ Relacionamentos M:N Implementados**
1. **Proposta ↔ Produtos**
   - Uma proposta pode ter múltiplos produtos
   - Um produto pode estar em múltiplas propostas
   - Tabela: `Proposta_Produtos`

2. **Apólice ↔ Produtos**
   - Uma apólice pode cobrir múltiplos produtos
   - Um produto pode estar em múltiplas apólices
   - Tabela: `Apolice_Produtos`

### **✅ Integridade Referencial Garantida**
- **ON DELETE NO ACTION**: Evita exclusão acidental de dados críticos
- **ON UPDATE CASCADE**: Propaga mudanças de IDs automaticamente
- **ON DELETE CASCADE**: Para tabelas de ligação (M:N)
- **ON DELETE SET NULL**: Para relacionamentos opcionais

### **✅ Campos Calculados**
```sql
-- Comissões calculadas automaticamente
valor_comissao_corretora AS (valor_total * percentual_comissao_seguradora / 100) PERSISTED
valor_comissao_colaborador AS ((valor_total * percentual_comissao_seguradora / 100) * percentual_comissao_colaborador / 100) PERSISTED
```

### **✅ Validações de Domínio**
```sql
-- Exemplos de constraints implementadas
CHECK (tipo_pessoa IN ('Fisica', 'Juridica'))
CHECK (status_proposta IN ('Pendente', 'Em Analise', 'Aprovada', 'Rejeitada', 'Cancelada'))
CHECK (tipo_seguro IN ('Vida', 'Auto', 'Residencial', 'Empresarial', 'Saude', 'Viagem', 'Outros'))
CHECK (forma_pagamento IN ('Boleto', 'Cartao Credito', 'Cartao Debito', 'PIX', 'Transferencia', 'Dinheiro'))
```

## 🚀 **BENEFÍCIOS DA ESTRUTURA CORRIGIDA**

### **📈 Escalabilidade**
- Suporte a múltiplos produtos por apólice
- Propostas complexas com vários produtos
- Histórico completo de relacionamentos

### **🔒 Integridade**
- Chaves estrangeiras garantem consistência
- Constraints validam dados na inserção
- Índices otimizam performance

### **📊 Flexibilidade**
- Fácil adição de novos tipos de seguro
- Controle granular de comissões
- Acompanhamento detalhado de pagamentos

### **🔍 Rastreabilidade**
- Histórico completo cliente → proposta → apólice → sinistro
- Números únicos para propostas, apólices e sinistros
- Auditoria completa de transações

**🎉 A estrutura está agora completa, normalizada e pronta para suportar um sistema robusto de corretora de seguros!**