# 📖 Documentação Técnica - Sistema Corretora de Seguros

## 🏗️ Arquitetura do Sistema

### Visão Geral
O sistema foi desenvolvido seguindo o padrão **MVC (Model-View-Controller)** com Flask, utilizando:
- **Model**: Estrutura de dados no SQL Server
- **View**: Templates HTML com Jinja2
- **Controller**: Rotas Flask no `app.py`

### Stack Tecnológica
```
┌─────────────────┐
│    Frontend     │  HTML5 + CSS3 + Bootstrap
├─────────────────┤
│    Backend      │  Python 3.11 + Flask 3.1.2
├─────────────────┤
│    Database     │  Microsoft SQL Server 2019+
├─────────────────┤
│   Conectividade │  PyODBC + ODBC Driver 17
└─────────────────┘
```

## 🗄️ Estrutura do Banco de Dados

### Diagrama de Relacionamentos
```
Users ──────────────┐
                    │
Seguradoras ────────┼──── Apolices ────┬──── Sinistros
                    │       │           │
Tipos_Seguro ───────┘       │           └──── Renovacao_Apolices
                            │
Clientes ───────────────────┼──── Tarefas
                            │
Colaboradores ──────────────┘
```

### Tabelas Detalhadas

#### 1. **Apolices** (Tabela Central)
```sql
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
    valor_comissao_corretora AS (valor_premio * percentual_comissao_seguradora / 100) PERSISTED,
    percentual_comissao_colaborador DECIMAL(5, 2),
    valor_comissao_colaborador AS ((valor_premio * percentual_comissao_seguradora / 100) * percentual_comissao_colaborador / 100) PERSISTED,
    -- ... outros campos
);
```

#### 2. **Campos Calculados Automaticamente**
- `valor_comissao_corretora`: Calculado automaticamente
- `valor_comissao_colaborador`: Baseado na comissão da corretora

#### 3. **Integridade Referencial**
- Todas as FKs com `ON DELETE NO ACTION` para preservar histórico
- `ON UPDATE CASCADE` para manter sincronização

## 🔧 Funcionalidades Principais

### Sistema de Comissões
```python
# Cálculo automático via SQL Server
valor_comissao_corretora = valor_premio * percentual_comissao_seguradora / 100
valor_comissao_colaborador = valor_comissao_corretora * percentual_comissao_colaborador / 100
```

### Controle de Renovações
```python
# Query para apólices próximas do vencimento
SELECT * FROM Apolices 
WHERE status_apolice = 'Ativa'
AND data_fim_vigencia BETWEEN GETDATE() AND DATEADD(day, 30, GETDATE())
AND NOT EXISTS (SELECT 1 FROM Renovacao_Apolices WHERE id_apolice_antiga = Apolices.id_apolice)
```

### Sistema de Autenticação
```python
# Sessões Flask para controle de acesso
session['user_id'] = user[0]
session['username'] = user[1] 
session['role'] = user[2]
```

## 📊 Relatórios e Analytics

### Dashboard Principal
- **Indicadores**: Total clientes, apólices ativas, sinistros
- **Gráficos**: Apólices por tipo, sinistros por status
- **Financeiro**: Valor total de prêmios, comissões pendentes

### Relatórios Disponíveis
1. **Performance por Colaborador**
2. **Vendas por Período** 
3. **Análise de Comissões**
4. **Apólices por Vencer**
5. **Status de Sinistros**

## 🔐 Segurança

### Autenticação
- Sistema baseado em sessões Flask
- Senhas armazenadas em texto plano (⚠️ melhorar para hash)
- Controle de acesso por roles

### Proteção SQL Injection
```python
# Uso de parâmetros prepared statements
cursor.execute('SELECT * FROM Users WHERE username = ? AND password = ?', (username, password))
```

### Validação de Entrada
- Validação básica nos formulários HTML
- Verificação de tipos de dados no backend

## 🚀 Performance

### Otimizações Implementadas
- **Campos Persistidos**: Cálculos automáticos no SQL Server
- **Índices**: PKs e UKs para performance
- **Consultas Otimizadas**: JOINs eficientes

### Sugestões para Produção
- Implementar cache (Redis)
- Otimizar consultas complexas
- Adicionar índices adicionais
- Pool de conexões

## 🔄 Fluxos de Negócio

### 1. Venda de Apólice
```
Cliente → Escolha Seguro → Cadastro Apólice → Cálculo Comissões → Registro
```

### 2. Controle de Sinistro  
```
Ocorrência → Comunicação → Análise → Indenização → Encerramento
```

### 3. Processo de Renovação
```
Vencimento Próximo → Alerta → Contato Cliente → Nova Apólice → Vínculo Renovação
```

## 🛠️ Manutenção

### Logs da Aplicação
- Logs básicos via Flask (console)
- Histórico de login via sessões
- Sugestão: Implementar logging estruturado

### Backup e Recovery
- Backup regular do SQL Server
- Scripts de criação/restauração inclusos
- Versionamento de schema recomendado

### Monitoramento
- Health check via rota `/test`
- Monitoramento de conexões DB
- Alertas de erros recomendados

## 📝 Desenvolvimento

### Adicionando Novas Funcionalidades

#### 1. Nova Rota
```python
@app.route('/nova-funcionalidade')
def nova_funcionalidade():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Lógica aqui
    return render_template('template.html')
```

#### 2. Nova Tabela
```sql
CREATE TABLE NovatabEla (
    id INT IDENTITY(1,1) PRIMARY KEY,
    -- campos aqui
);
```

#### 3. Novo Template
```html
{% extends "base.html" %}
{% block content %}
<!-- Conteúdo aqui -->
{% endblock %}
```

### Padrões de Código
- Nomes em português para domínio de negócio
- Nomes em inglês para código técnico
- Comentários em português
- Documentação em markdown

## 🧪 Testes

### Testes Disponíveis
- `test_connection.py`: Testa conectividade
- `test_sistema.py`: Testa funcionalidades
- `check_users.py`: Verifica usuários

### Executando Testes
```bash
python test_connection.py
python test_sistema.py
python check_users.py
```

## 📞 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão SQL Server
```
Erro: [Microsoft][ODBC Driver 17 for SQL Server][SSMS] Login failed
```
**Solução**: Verificar se SQL Server está rodando e autenticação Windows habilitada

#### 2. Módulo não encontrado
```
ModuleNotFoundError: No module named 'flask'
```
**Solução**: `pip install -r requirements.txt`

#### 3. Tabela não existe
```
Invalid object name 'tabela'
```
**Solução**: Executar `INSTALACAO_COMPLETA.sql`

### Logs Úteis
- Flask: Console da aplicação
- SQL Server: SQL Server Logs
- Windows: Event Viewer

---

**Documentação atualizada em:** 01/10/2025  
**Versão do Sistema:** 1.0.0