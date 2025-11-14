# 🧪 Testes do Projeto

Esta pasta contém todos os testes do projeto organizados por tipo.

## 📁 Estrutura

```
tests/
├── e2e/                          # Testes End-to-End (Playwright)
│   ├── test-browser.js           # Teste básico de navegação
│   ├── test-requisitos.js        # Validação de requisitos
│   ├── test-completo-db-responsive.js  # Teste completo + responsividade
│   ├── test-conformidade-prompts.js    # Conformidade com Prompts
│   ├── test-e2e-completo.js      # Suite completa E2E
│   ├── test-manual-interativo.js # Teste manual interativo
│   ├── test-medico-completo.js   # Suite médico (90.9% sucesso)
│   ├── test-admin-*.js           # Testes admin (convenios, medicos, pacientes)
│   ├── test-validacao-unicidade.js # Validação dados únicos
│   └── test-*.js                 # Outros testes E2E
│
├── screenshots/                  # Screenshots dos testes (ignorado no git)
│   └── *.png
│
└── README.md                     # Este arquivo

backend/tests/                    # Testes unitários backend
├── conftest.py                   # Fixtures pytest
├── test_auth.py                  # Testes autenticação (16 testes)
├── test_endpoints_medicos.py     # Testes endpoints médicos (15 testes)
├── test_endpoints_pacientes.py   # Testes endpoints pacientes (13 testes)
├── test_admin_relatorios.py      # Testes admin e relatórios (17 testes)
├── test_models.py                # Testes models (8 testes)
└── test_validators.py            # Testes validators (13 testes)
```

## 🚀 Executando os Testes

### Frontend (E2E com Playwright)

```bash
# Teste básico
npm test

# Teste de requisitos
npm run test:requisitos

# Teste completo (DB + Responsividade)
npm run test:completo

# Suite médico completa
npm run test:medico

# Teste de conformidade com Prompts
npm run test:conformidade

# Suite E2E completa
npm run test:e2e

# Teste manual interativo
npm run test:manual
```

### Backend (Pytest)

```bash
cd backend
python -m pytest tests/ -v           # Todos os testes
python -m pytest tests/ -v --tb=short # Com stack trace curto
python -m pytest tests/test_auth.py -v # Apenas autenticação
```

## 📊 Cobertura de Testes

### Backend: 100% ✅
- **82/82 testes passando**
- Auth: 16/16 ✅
- Models: 8/8 ✅
- Validators: 13/13 ✅
- Endpoints Médicos: 15/15 ✅
- Endpoints Pacientes: 13/13 ✅
- Admin/Relatórios: 17/17 ✅

### Frontend: 90.9% ✅
- **10/11 testes E2E passando**
- Admin: CRUD completo ✅
- Médico: Login, horários, consultas, observações ✅
- Paciente: Cadastro, validações ✅

## 🔧 Configuração

### Pré-requisitos
- Node.js 18+
- Python 3.11+
- Docker + Docker Compose
- Playwright (instalado via `npx playwright install chromium`)

### Variáveis de Ambiente
Os testes usam as seguintes URLs:
- Frontend: `http://localhost:8081`
- Backend API: `http://localhost:8000`
- Banco de Dados: `localhost:5432` (PostgreSQL 15)

## 📝 Notas

- Screenshots são salvos em `tests/screenshots/` (ignorado pelo git)
- Testes E2E requerem Docker Compose rodando
- Backend tests usam banco de dados em memória (SQLite)
