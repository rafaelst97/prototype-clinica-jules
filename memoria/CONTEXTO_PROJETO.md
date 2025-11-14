# 📋 Memória do Projeto - Clínica Saúde+

> **Sistema de Agendamento de Consultas Médicas**  
> Este documento consolida todas as especificações, regras de negócio e arquitetura do projeto.  
> Use como referência em todas as futuras solicitações.

---

## 📚 Índice

1. [Estudo de Caso](#estudo-de-caso)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Casos de Uso](#casos-de-uso)
4. [Modelo Entidade-Relacionamento (MER)](#modelo-entidade-relacionamento-mer)
5. [Diagrama de Classes (UML)](#diagrama-de-classes-uml)
6. [Regras de Negócio](#regras-de-negócio)
7. [Tecnologias Utilizadas](#tecnologias-utilizadas)

---

## 🎯 Estudo de Caso

### Contexto
**UNIVALI - Universidade do Vale do Itajaí**  
**Escola Politécnica**  
**Disciplina:** Melhoria de Processos de Software  
**Professora:** Daniela S. Moreira da Silva

### Sobre a Clínica Saúde+

A **Clínica Saúde+** é uma clínica de especialidades médicas que atende pacientes de forma particular e por convênios.

### ⚠️ Importante: Ambiente de Desenvolvimento

Este projeto utiliza **Docker** para gerenciar toda a infraestrutura:

- 🐳 **Docker Compose**: Orquestra 4 containers
- 🗄️ **PostgreSQL 15**: Banco de dados via Docker (container `clinica_db`)
- 🚀 **Backend**: FastAPI em container Python (container `clinica_backend`)
- 🌐 **Frontend**: Nginx servindo arquivos estáticos (container `clinica_frontend`)
- 🔧 **pgAdmin**: Interface web para administração do banco (container `clinica_pgadmin`)

**Comando para iniciar:** `docker-compose up -d`  
**Porta do Backend:** `http://localhost:8000`  
**Porta do Frontend:** `http://localhost:80`  
**Porta do pgAdmin:** `http://localhost:5050`

#### Problemas Atuais
O agendamento atual é manual (telefone ou presencial) e registrado em agenda física, causando:

- ❌ **Conflito de horários**
- ❌ **Dificuldade no controle de consultas canceladas ou remarcadas**
- ❌ **Falta de relatórios gerenciais para os administradores**
- ❌ **Tempo elevado de espera para pacientes conseguirem um atendimento**

#### Solução
Desenvolver um **sistema web responsivo** de Agendamento de Consultas Médicas.

### Objetivo
Fornecer um sistema que permita aos pacientes agendarem consultas de forma simples e rápida, e que dê aos médicos e à administração da clínica maior controle sobre horários, disponibilidade e relatórios.

---

## 🏗️ Arquitetura do Sistema

### Arquitetura em Camadas

```
┌─────────────────────────────────────┐
│         CAMADA FRONTEND             │
│  ┌──────────────┐  ┌──────────────┐│
│  │  Navegador   │  │  JavaScript  ││
│  │     Web      │  │   ES6+       ││
│  └──────────────┘  └──────────────┘│
└─────────────────────────────────────┘
              ↕ HTTP/JSON
┌─────────────────────────────────────┐
│         CAMADA BACKEND              │
│  ┌──────────────────────────────┐  │
│  │      Python + FastAPI        │  │
│  │      Lógica de Negócio       │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
              ↕ SQL Queries
┌─────────────────────────────────────┐
│    CAMADA BANCO DE DADOS            │
│  ┌──────────────────────────────┐  │
│  │       PostgreSQL 15          │  │
│  │    Armazenamento de Dados    │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Componentes

#### **Frontend**
- **Navegador Web**: Interface do usuário, Páginas responsivas
- **JavaScript**: Lógica do frontend, Interação com usuário, Requisições HTTP

#### **Backend**
- **Python (FastAPI)**: Lógica de negócio, API REST, Processamento de dados
- **Container Docker**: `clinica_backend` (Python 3.11)

#### **Banco de Dados**
- **PostgreSQL 15**: Armazenamento de dados, Consultas SQL, Persistência
- **Container Docker**: `clinica_db` (postgres:15-alpine)
- **Encoding**: UTF-8 (client_encoding=utf8)

### Fluxos de Comunicação

1. **Navegador Web** ↔ **JavaScript** (Executa/Atualiza Interface)
2. **Frontend (JavaScript)** → **Backend (Python)** (HTTP Requests)
3. **Backend (Python)** → **Frontend (JavaScript)** (JSON Response)
4. **Backend (Python)** ↔ **Banco de Dados (PostgreSQL)** (SQL Queries/Dados)

---

## 👥 Casos de Uso

### Ator: Paciente

| Caso de Uso | Descrição |
|-------------|-----------|
| **Cadastrar Paciente** | Registro inicial no sistema |
| **Login do Paciente** | Autenticação no sistema |
| **Agendar Consulta** | Agendar nova consulta com médico |
| **Visualizar Consultas** | Ver consultas futuras e passadas |
| **Cancelar Consulta** | Cancelar consulta agendada (RN1) |
| **Reagendar Consulta** | Remarcar consulta existente (RN1) |

### Ator: Médico

| Caso de Uso | Descrição |
|-------------|-----------|
| **Gerenciar Horários de Trabalho** | Definir disponibilidade semanal |
| **Visualizar Consultas Agendadas** | Ver consultas por data |
| **Registrar Observações da Consulta** | Adicionar notas pós-consulta |
| **Bloquear Horários** | Bloquear slots em caso de imprevistos |
| **Visualizar Observações da Consulta** | Acessar notas de consultas |

### Ator: Administrador

| Caso de Uso | Descrição |
|-------------|-----------|
| **Gerar Relatórios em PDF** | Criar relatórios gerenciais |
| **Gerenciar Cadastro de Médicos** | CRUD de médicos |
| **Gerenciar Planos de Saúde** | CRUD de convênios |
| **Desbloquear Contas de Pacientes** | Liberar pacientes bloqueados (RN4) |
| **Visualizar Observações da Consulta** | Acessar notas de consultas |

---

## 🗄️ Modelo Entidade-Relacionamento (MER)

### Entidades e Atributos

#### **ESPECIALIDADE**
- `id_especialidade` (PK)
- `nome` (UK - Unique Key)

#### **PLANO_SAUDE**
- `id_plano_saude` (PK)
- `nome`
- `cobertura_info`

#### **ADMINISTRADOR**
- `id_admin` (PK)
- `nome`
- `email` (UK)
- `senha_hash`
- `papel`

#### **MEDICO**
- `id_medico` (PK)
- `nome`
- `cpf` (UK)
- `email` (UK)
- `senha_hash`
- `crm` (UK)
- `id_especialidade_fk` (FK → ESPECIALIDADE)

#### **PACIENTE**
- `id_paciente` (PK)
- `nome`
- `cpf` (UK)
- `email` (UK)
- `senha_hash`
- `telefone`
- `data_nascimento`
- `esta_bloqueado` (boolean)
- `id_plano_saude_fk` (FK → PLANO_SAUDE, Nullable)

#### **RELATORIO**
- `id_relatorio` (PK)
- `tipo`
- `data_geracao`
- `dados_resultado`
- `id_admin_fk` (FK → ADMINISTRADOR)

#### **HORARIO_TRABALHO**
- `id_horario` (PK)
- `dia_semana` (0-6, onde 0=Segunda)
- `hora_inicio` (Time)
- `hora_fim` (Time)
- `id_medico_fk` (FK → MEDICO)

#### **CONSULTA**
- `id_consulta` (PK)
- `data_hora_inicio` (DateTime)
- `data_hora_fim` (DateTime)
- `status` (enum: 'agendada', 'realizada', 'cancelada')
- `id_paciente_fk` (FK → PACIENTE)
- `id_medico_fk` (FK → MEDICO)

#### **OBSERVACAO**
- `id_observacao` (PK)
- `descricao` (Text)
- `data_criacao` (DateTime)
- `id_consulta_fk` (FK → CONSULTA)

### Relacionamentos

```
MEDICO (N) ──────── (1) ESPECIALIDADE
  └─ MEDICO.id_especialidade_fk → ESPECIALIDADE.id_especialidade

PACIENTE (N) ──────── (0..1) PLANO_SAUDE
  └─ PACIENTE.id_plano_saude_fk → PLANO_SAUDE.id_plano_saude (Nullable)

RELATORIO (N) ──────── (1) ADMINISTRADOR
  └─ RELATORIO.id_admin_fk → ADMINISTRADOR.id_admin

HORARIO_TRABALHO (N) ──────── (1) MEDICO
  └─ HORARIO_TRABALHO.id_medico_fk → MEDICO.id_medico

CONSULTA (N) ──────── (1) PACIENTE
  └─ CONSULTA.id_paciente_fk → PACIENTE.id_paciente

CONSULTA (N) ──────── (1) MEDICO
  └─ CONSULTA.id_medico_fk → MEDICO.id_medico

OBSERVACAO (N) ──────── (1) CONSULTA
  └─ OBSERVACAO.id_consulta_fk → CONSULTA.id_consulta
```

---

## 📐 Diagrama de Classes (UML)

### Hierarquia de Classes

```
Usuario (Classe Base)
├── Pessoa
│   ├── Paciente
│   └── Medico
└── Administrador
```

### Classes Principais

#### **Usuario** (Classe Base)
```
- id: int
- nome: string
- email: string
- senha: string (hash)
+ fazerLogin(email, senha): boolean
+ alterarSenha(novaSenha): void
```

#### **Pessoa** (herda de Usuario)
```
- cpf: string
- dataNascimento: Date
+ getIdade(): int
```

#### **Paciente** (herda de Pessoa)
```
- telefone: string
- estaBloqueado: boolean
+ agendarConsulta(idMedico, dataHora): Consulta
+ visualizarMinhasConsultas(): List<Consulta>
+ cancelarConsulta(idConsulta): boolean
+ reagendarConsulta(idConsulta, novaDataHora): boolean
```

#### **Medico** (herda de Pessoa)
```
- crm: string
+ gerenciarHorarios(listaHorarios): boolean
+ visualizarConsultasAgendadas(): List<Consulta>
+ registrarObservacao(idConsulta, texto): Observacao
+ bloquearHorario(dataHora): void
```

#### **Administrador** (herda de Usuario)
```
- papel: string
+ cadastrarMedico(dadosMedico): Medico
+ gerenciarPlanoSaude(dadosPlano): PlanoSaude
+ desbloquearPaciente(idPaciente): boolean
+ gerarRelatorio(tipo, parametros): Relatorio
```

#### **HorarioTrabalho**
```
- id: int
- diaSemana: int
- horaInicio: Time
- horaFim: Time
```

#### **Especialidade**
```
- id: int
- nome: string
```

#### **Consulta**
```
- id: int
- dataHoraInicio: DateTime
- dataHoraFim: DateTime
- status: string
+ confirmar(): void
+ cancelar(): void
```

#### **Observacao**
```
- id: int
- descricao: string
- dataCriacao: DateTime
```

#### **PlanoSaude**
```
- id: int
- nome: string
- cobertura: string
```

#### **Relatorio**
```
- id: int
- tipo: string
- dataGeracao: Date
- dados: string
```

### Associações entre Classes

| Classe A | Cardinalidade | Classe B | Descrição |
|----------|---------------|----------|-----------|
| Medico | (1) --- (N) | HorarioTrabalho | Médico possui múltiplos horários |
| Medico | (1) --- (1) | Especialidade | Médico pertence a uma especialidade |
| Medico | (1) --- (0..N) | Consulta | Médico atende consultas |
| Paciente | (1) --- (0..N) | Consulta | Paciente agenda consultas |
| Consulta | (1) --- (0..1) | Observacao | Consulta pode ter observação |
| Administrador | (1) --- (0..N) | PlanoSaude | Admin cadastra planos de saúde |
| Administrador | (1) --- (0..N) | Relatorio | Admin gera relatórios |

---

## 📜 Regras de Negócio

### RN1: Prazo de Cancelamento/Reagendamento
**Consultas só podem ser canceladas ou remarcadas até 24h antes do horário agendado.**

- ✅ Validação no backend
- ✅ Feedback claro ao usuário
- ✅ Aplicado em: `cancelar_consulta()` e `reagendar_consulta()`

### RN2: Limite de Consultas Futuras
**Cada paciente pode ter no máximo 2 consultas futuras agendadas por vez.**

- ✅ Validação antes de criar nova consulta
- ✅ Contagem apenas de consultas com status 'agendada'
- ✅ Aplicado em: `criar_consulta()`

### RN3: Prevenção de Conflitos
**Cada médico define seus horários disponíveis semanalmente, e o sistema deve evitar conflitos de agendamento.**

- ✅ Verificação de disponibilidade em `HORARIO_TRABALHO`
- ✅ Validação de consultas já agendadas no mesmo horário
- ✅ Aplicado em: `horarios_disponiveis()` e `criar_consulta()`

### RN4: Bloqueio de Paciente por Faltas
**Se o paciente faltar a 3 consultas seguidas sem aviso, o sistema deve bloquear novos agendamentos até liberação pela administração.**

- ✅ Campo `esta_bloqueado` em PACIENTE
- ✅ Validação ao tentar agendar consulta
- ✅ Função administrativa para desbloquear

---

## 🛠️ Tecnologias Utilizadas

### Frontend
- **HTML5**: Estrutura das páginas
- **CSS3**: Estilização e design responsivo
- **JavaScript ES6+**: Lógica do cliente
- **Font Awesome 6.4.0**: Ícones
- **Fetch API**: Requisições HTTP

### Backend
- **Python 3.11**: Linguagem principal
- **FastAPI**: Framework web assíncrono
- **SQLAlchemy**: ORM para banco de dados
- **Alembic**: Migrações de banco
- **Pydantic**: Validação de dados
- **bcrypt**: Hash de senhas
- **JWT**: Autenticação por tokens
- **python-jose**: Gerenciamento JWT
- **Uvicorn**: Servidor ASGI

### Banco de Dados
- **PostgreSQL 15**: Banco relacional via Docker
- **UTF-8 Encoding**: Suporte a caracteres especiais (client_encoding=utf8)
- **Imagem Docker**: postgres:15-alpine
- **Porta**: 5432 (mapeada para localhost)
- **Credenciais**:
  - Database: `clinica_saude`
  - User: `clinica_user`
  - Password: `clinica_password`

### Infraestrutura Docker
- **Docker**: Containerização de toda a aplicação
- **Docker Compose**: Orquestração de containers
- **Nginx**: Servidor web para frontend (container)
- **pgAdmin**: Interface de administração do PostgreSQL (container)

### Containers Docker (4 containers)

| Container | Imagem | Porta | Função |
|-----------|--------|-------|--------|
| **clinica_db** | postgres:15-alpine | 5432 | Banco de dados PostgreSQL |
| **clinica_backend** | Python 3.11 | 8000 | API FastAPI |
| **clinica_frontend** | nginx:alpine | 80 | Frontend estático |
| **clinica_pgadmin** | dpage/pgadmin4 | 5050 | Administração do banco |

#### Comandos Docker Úteis
```bash
# Iniciar todos os containers
docker-compose up -d

# Ver logs do backend
docker-compose logs -f backend

# Ver logs do banco
docker-compose logs -f db

# Parar todos os containers
docker-compose down

# Acessar PostgreSQL via CLI
docker exec -it clinica_db psql -U clinica_user -d clinica_saude

# Rebuild após mudanças
docker-compose up -d --build
```

---

## 📋 Funcionalidades Implementadas

### ✅ Módulo Paciente
- [x] Cadastro com CPF, nome, telefone, e-mail, convênio
- [x] Login com e-mail e senha (8-20 caracteres alfanuméricos)
- [x] Agendamento de consultas (especialidade → médico → horário)
- [x] Visualização de consultas futuras e passadas
- [x] Cancelamento de consultas (com validação 24h)
- [x] Reagendamento de consultas (com validação 24h)
- [x] Dashboard com resumo de consultas
- [x] Validação de limite de 2 consultas futuras

### 🚧 Módulo Médico (Pendente)
- [ ] Cadastro e edição de horários de atendimento
- [ ] Visualização das consultas agendadas por data
- [ ] Registro de observações após a consulta
- [ ] Bloqueio de horários em caso de imprevistos

### 🚧 Módulo Administrativo (Pendente)
- [ ] Cadastro e edição de médicos
- [ ] Relatórios em PDF
- [ ] Controle de convênios aceitos
- [ ] Desbloquear pacientes

---

## 🔑 Endpoints da API

### Autenticação
- `POST /api/auth/login` - Login de usuário
- `POST /api/auth/logout` - Logout de usuário

### Pacientes
- `POST /api/pacientes/` - Criar paciente
- `GET /api/pacientes/{id}` - Buscar paciente
- `GET /api/pacientes/consultas?paciente_id={id}` - Listar consultas do paciente
- `POST /api/pacientes/consultas?paciente_id={id}` - Criar consulta
- `PUT /api/pacientes/consultas/{id}/reagendar?paciente_id={id}` - Reagendar consulta
- `DELETE /api/pacientes/consultas/{id}?paciente_id={id}` - Cancelar consulta

### Médicos
- `GET /api/medicos/` - Listar médicos
- `GET /api/medicos/{id}` - Buscar médico
- `GET /api/medicos/{id}/horarios-disponiveis` - Horários disponíveis do médico

### Especialidades
- `GET /api/especialidades/` - Listar especialidades

### Planos de Saúde
- `GET /api/planos-saude/` - Listar planos

---

## 🔐 Autenticação e Autorização

### LocalStorage
O sistema armazena as seguintes informações:
- `token`: JWT token de autenticação
- `user_type`: Tipo do usuário ('paciente', 'medico', 'administrador')
- `user_id`: ID do usuário logado

### Role Mapping
- `administrador` → `admin` (conversão automática no frontend)

### Proteção de Rotas
- `auth-guard.js`: Verifica autenticação e redireciona se necessário
- `requiresAuth()`: Função para proteger páginas específicas

---

## 📊 Status do Projeto

### Última Atualização: 03/11/2025

#### ✅ Concluído
- Arquitetura do sistema definida
- Banco de dados PostgreSQL configurado
- Backend FastAPI com endpoints principais
- Autenticação JWT implementada
- Módulo Paciente 100% funcional
- Validações de regras de negócio (RN1, RN2, RN3)
- Encoding UTF-8 corrigido
- Frontend responsivo para pacientes

#### 🚧 Em Desenvolvimento
- Módulo Médico
- Módulo Administrativo
- Geração de relatórios PDF

#### 📝 Pendente
- Testes automatizados E2E completos
- Documentação da API (Swagger/OpenAPI)
- Deploy em produção

---

## 📞 Contato e Suporte

**Instituição:** UNIVALI - Universidade do Vale do Itajaí  
**Disciplina:** Melhoria de Processos de Software  
**Professora:** Daniela S. Moreira da Silva

---

**Última atualização:** 03 de Novembro de 2025  
**Versão do documento:** 1.0  
**Branch ativa:** backend-integration
