# 🧪 Guia de Testes - Sistema Clínica Saúde+

Este guia explica como executar todos os testes implementados no sistema.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Instalação](#instalação)
3. [Tipos de Testes](#tipos-de-testes)
4. [Executando os Testes](#executando-os-testes)
5. [Interpretando Resultados](#interpretando-resultados)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Software Necessário:
- Python 3.10+
- Docker e Docker Compose
- Google Chrome (para testes E2E)
- PostgreSQL (se executar fora do Docker)

### Portas Necessárias:
- `8000` - Backend API
- `5432` - PostgreSQL
- `80` - Frontend (Nginx)

---

## 📦 Instalação

### 1. Instalar Dependências de Teste

```powershell
# Navegar para o diretório backend
cd backend

# Instalar dependências principais
pip install -r requirements.txt

# Instalar dependências de teste
pip install -r requirements-test.txt
```

### 2. Iniciar Aplicação (para testes E2E)

```powershell
# Do diretório raiz do projeto
docker-compose up -d
```

Aguarde todos os containers iniciarem:
- ✅ Backend API em http://localhost:8000
- ✅ Frontend em http://localhost
- ✅ PostgreSQL em localhost:5432

---

## 🎯 Tipos de Testes

### 1. Testes de Validadores (`test_validators_completo.py`)
- ✅ Validação de CPF, email, telefone
- ✅ Validação de senha alfanumérica
- ✅ Regras de negócio (limite de consultas, cancelamento 24h)
- ✅ Conflitos de horários

### 2. Testes de Segurança (`test_seguranca_completo.py`)
- ✅ Hashing de senhas
- ✅ Autenticação JWT
- ✅ Autorização por nível
- ✅ Proteção SQL Injection
- ✅ Proteção XSS
- ✅ Dados sensíveis

### 3. Testes E2E com Selenium (`test_e2e_selenium.py`)
- ✅ Formulários e máscaras
- ✅ Fluxos de usuário completos
- ✅ Validações de interface
- ✅ Navegação

### 4. Validação de Banco de Dados (`validate_database.py`)
- ✅ Estrutura de tabelas
- ✅ Chaves primárias e estrangeiras
- ✅ Constraints UNIQUE
- ✅ Integridade referencial

### 5. Testes de Endpoints (existentes)
- ✅ `test_endpoints_pacientes.py`
- ✅ `test_endpoints_medicos.py`
- ✅ `test_admin_relatorios.py`

---

## ▶️ Executando os Testes

### Opção 1: Executar TODOS os Testes (Recomendado)

```powershell
# Do diretório raiz do projeto
.\scripts\run-all-tests.ps1
```

Este script executa:
1. ✅ Testes de validadores
2. ✅ Testes de segurança
3. ✅ Testes de endpoints
4. ✅ Validação de banco de dados
5. ✅ Testes E2E (se app estiver rodando)
6. ✅ Relatório de cobertura

**Tempo estimado:** ~3 minutos

---

### Opção 2: Executar Testes Específicos

#### Testes de Validadores
```powershell
cd backend
pytest tests/test_validators_completo.py -v
```

#### Testes de Segurança
```powershell
cd backend
pytest tests/test_seguranca_completo.py -v
```

#### Testes E2E (requer aplicação rodando)
```powershell
# Primeiro, iniciar aplicação
docker-compose up -d

# Aguardar inicialização (~10 segundos)
Start-Sleep -Seconds 10

# Executar testes E2E
cd backend
pytest tests/test_e2e_selenium.py -v
```

#### Validação de Banco de Dados
```powershell
cd backend
python tests/validate_database.py
```

#### Testes Existentes de Endpoints
```powershell
cd backend
pytest tests/test_endpoints_pacientes.py -v
pytest tests/test_endpoints_medicos.py -v
pytest tests/test_admin_relatorios.py -v
```

---

### Opção 3: Testes com Cobertura de Código

```powershell
cd backend

# Executar todos os testes com relatório de cobertura
pytest --cov=app --cov-report=html --cov-report=term-missing

# Abrir relatório HTML
start htmlcov/index.html
```

---

## 📊 Interpretando Resultados

### Saída de Sucesso
```
================================ test session starts =================================
collected 140 items

tests/test_validators_completo.py::TestValidacaoCPF::test_cpf_valido PASSED [  1%]
tests/test_validators_completo.py::TestValidacaoCPF::test_cpf_invalido PASSED [ 2%]
...

================================ 140 passed in 45.23s ================================
```

### Saída com Falhas
```
FAILED tests/test_seguranca_completo.py::test_sql_injection - AssertionError
```

Verifique o traceback para detalhes do erro.

### Relatório de Cobertura
```
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
app/models/models.py                  245      5    98%   45-47
app/routers/auth.py                    85      2    98%   102-103
app/utils/validators.py                120      0   100%
-----------------------------------------------------------------
TOTAL                                1450     25    98%
```

---

## 🔍 Troubleshooting

### Erro: "ModuleNotFoundError"
**Solução:**
```powershell
pip install -r backend/requirements-test.txt
```

### Erro: "Connection refused" nos testes
**Causa:** Aplicação não está rodando

**Solução:**
```powershell
docker-compose up -d
```

### Erro: Testes E2E falham
**Causa:** ChromeDriver não instalado ou versão incompatível

**Solução:**
```powershell
# O webdriver-manager baixa automaticamente
# Se falhar, instale manualmente:
pip install --upgrade selenium webdriver-manager
```

### Erro: "Database does not exist" na validação de BD
**Causa:** Banco de dados não está inicializado

**Solução:**
```powershell
# Recriar containers
docker-compose down -v
docker-compose up -d

# Aguardar inicialização
Start-Sleep -Seconds 15
```

### Testes lentos
**Solução:** Executar em paralelo (requer pytest-xdist):
```powershell
pip install pytest-xdist
pytest -n auto  # Usa todos os cores disponíveis
```

### Screenshots de testes E2E não são criados
**Solução:**
```powershell
# Criar diretório de screenshots
mkdir backend/tests/screenshots
```

---

## 📝 Arquivos de Teste

### Estrutura de Diretórios
```
backend/tests/
├── conftest.py                      # Configurações e fixtures
├── test_validators_completo.py      # Testes de validadores
├── test_seguranca_completo.py       # Testes de segurança
├── test_e2e_selenium.py             # Testes E2E
├── validate_database.py             # Validação de BD
├── test_endpoints_pacientes.py      # Endpoints de pacientes
├── test_endpoints_medicos.py        # Endpoints de médicos
├── test_admin_relatorios.py         # Endpoints de admin
└── screenshots/                     # Screenshots de testes E2E
```

---

## 🎯 Melhores Práticas

### Antes de Commitar
```powershell
# Executar testes rapidamente
pytest backend/tests -v --tb=short

# Verificar apenas se não há erros críticos
pytest backend/tests -x  # Para no primeiro erro
```

### Integração Contínua
```yaml
# Exemplo .github/workflows/tests.yml
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=app --cov-report=xml
```

### Debugging de Testes
```powershell
# Executar um teste específico
pytest backend/tests/test_validators_completo.py::TestValidacaoCPF::test_cpf_valido -v

# Com mais detalhes
pytest backend/tests/test_validators_completo.py::test_specific -vv -s

# Com debugger
pytest backend/tests/test_validators_completo.py --pdb
```

---

## 📚 Documentação Adicional

- [Análise Completa](./docs/ANALISE_COMPLETA_TESTES.md)
- [Relatório Executivo](./docs/RELATORIO_EXECUTIVO_TESTES.md)
- [Documentação de Testes Existentes](./backend/tests/README_TESTES.md)

---

## ✅ Checklist Rápido

Antes de considerar os testes completos:

- [ ] Todos os testes passam sem erros
- [ ] Cobertura de código > 80%
- [ ] Validação de banco de dados sem erros
- [ ] Testes E2E executam com sucesso
- [ ] Sem vulnerabilidades de segurança detectadas
- [ ] Screenshots de falhas salvas (se houver)

---

## 🤝 Suporte

Em caso de dúvidas ou problemas:

1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Consulte a [documentação completa](./docs/RELATORIO_EXECUTIVO_TESTES.md)
3. Verifique os logs dos containers: `docker-compose logs`

---

**Última atualização:** 01/11/2025  
**Versão:** 1.0
