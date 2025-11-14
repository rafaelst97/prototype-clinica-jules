# 🏥 Sistema Clínica Saúde+# Sistema de Agendamento de Consultas - Clínica Saúde+



Sistema completo de gerenciamento de clínicas médicas com funcionalidades para pacientes, médicos e administradores.## 📋 Descrição do Projeto



[![Backend Tests](https://github.com/rafaelst97/prototype-melhoria/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/rafaelst97/prototype-melhoria/actions/workflows/backend-tests.yml)Protótipo de navegação para o Sistema de Agendamento de Consultas Médicas da Clínica Saúde+. Este projeto foi desenvolvido como parte da disciplina de Melhoria de Processos de Software da UNIVALI.

[![Deploy to GitHub Pages](https://github.com/rafaelst97/prototype-melhoria/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/rafaelst97/prototype-melhoria/actions/workflows/deploy-pages.yml)

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/rafaelst97/prototype-melhoria/releases/tag/v2.0.0)## 🎯 Objetivo

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Fornecer um sistema web responsivo que permita aos pacientes agendarem consultas de forma simples e rápida, e que dê aos médicos e à administração da clínica maior controle sobre horários, disponibilidade e relatórios.

## 📋 Sobre o Projeto

## 🏗️ Estrutura do Projeto

O **Clínica Saúde+** é um sistema web fullstack desenvolvido para otimizar a gestão de clínicas médicas, oferecendo:

```

- 👤 **Portal do Paciente**: Agendamento de consultas, visualização de histórico e gerenciamento de perfilProjeto/

- 👨‍⚕️ **Portal do Médico**: Gestão de agenda, horários de atendimento, observações médicas e bloqueios de horários│

- 👨‍💼 **Portal Administrativo**: Gerenciamento completo de pacientes, médicos, convênios e relatórios├── index.html                 # Página inicial com seleção de módulos

├── docker-compose.yml         # Configuração Docker

## 🚀 Tecnologias├── nginx.conf                 # Configuração Nginx

│

### Backend├── css/

- **Python 3.11** com **FastAPI**│   └── style.css             # Estilos globais do sistema

- **PostgreSQL 15** como banco de dados│

- **SQLAlchemy** ORM├── js/                        # Scripts JavaScript

- **Alembic** para migrações│   ├── api.js                # Cliente API REST

- **Pytest** para testes automatizados│   ├── masks.js              # Máscaras de input (CPF, telefone, etc)

- **JWT** para autenticação│   ├── paciente-*.js         # Scripts do módulo paciente

- **Docker** e **Docker Compose** para containerização│   ├── medico-*.js           # Scripts do módulo médico

│   └── admin-*.js            # Scripts do módulo admin

### Frontend│

- **HTML5**, **CSS3**, **JavaScript ES6+**├── paciente/                  # Módulo do Paciente

- **Font Awesome** para ícones│   ├── login.html            # Login de paciente

- **Responsive Design** para mobile/tablet/desktop│   ├── cadastro.html         # Cadastro de novo paciente

- **Nginx** como servidor web│   ├── dashboard.html        # Painel principal do paciente

│   ├── agendar.html          # Agendamento de consultas

## 👥 Equipe de Desenvolvimento│   ├── consultas.html        # Visualização de consultas

│   └── perfil.html           # Edição de perfil

- **CAIO CÉSAR SABINO SOARES**│

- **JÚLIA CANSIAN ROCHA**├── medico/                    # Módulo do Médico

- **RAFAEL DOS SANTOS**│   ├── login.html            # Login de médico (via CRM)

│   ├── dashboard.html        # Painel principal do médico

*Projeto desenvolvido como parte da disciplina de Melhoria de Processo de Software - UNIVALI*│   ├── agenda.html           # Visualização da agenda

│   ├── consultas.html        # Detalhes e observações

## 📦 Instalação e Execução│   └── horarios.html         # Gerenciamento de horários

│

### Pré-requisitos├── admin/                     # Módulo Administrativo

│   ├── login.html            # Login do administrador

- Docker Desktop instalado│   ├── dashboard.html        # Painel administrativo

- Git│   ├── medicos.html          # Gerenciamento de médicos

- Navegador web moderno│   ├── pacientes.html        # Gerenciamento de pacientes

│   ├── relatorios.html       # Geração de relatórios PDF

### Passo a passo│   └── convenios.html        # Gerenciamento de convênios

│

1. **Clone o repositório**├── backend/                   # Backend FastAPI

```bash│   ├── app/                  # Código da aplicação

git clone https://github.com/rafaelst97/prototype-melhoria.git│   │   ├── routers/         # Endpoints REST

cd prototype-melhoria│   │   ├── models/          # Models SQLAlchemy

```│   │   ├── schemas/         # Schemas Pydantic

│   │   └── utils/           # Utilidades (auth, validators, relatórios)

2. **Inicie os containers**│   ├── tests/               # Testes unitários (82 testes - 100%)

```bash│   ├── alembic/             # Migrações de banco de dados

docker-compose up -d│   └── requirements.txt     # Dependências Python

```│

├── tests/                     # Testes E2E

3. **Aguarde a inicialização** (aproximadamente 30 segundos)│   ├── e2e/                 # Scripts Playwright (13 testes)

│   ├── screenshots/         # Screenshots dos testes

4. **Acesse o sistema**│   └── README.md            # Documentação dos testes

- Frontend: http://localhost│

- Backend API: http://localhost:8000├── scripts/                   # Scripts utilitários

- Documentação da API: http://localhost:8000/docs│   ├── start.ps1            # Iniciar projeto (Windows)

│   ├── start.sh             # Iniciar projeto (Linux/Mac)

### Usuários de Teste│   ├── abrir-site.bat       # Abrir no navegador

│   └── README.md            # Documentação dos scripts

#### Paciente│

- Email: `maria@email.com`├── docs/                      # Documentação do projeto

- Senha: `paciente123`│   ├── RESUMO_EXECUTIVO.md

│   ├── STATUS_PROJETO_COMPLETO.md

#### Médico│   ├── TESTES_AUTOMATIZADOS.md

- Email: `joao1@clinica.com`│   └── ...                  # Outros documentos

- Senha: `medico123`│

└── Prompts/                   # Prompts de IA usados no projeto

#### Administrador    ├── ArquiteturaSistema.txt

- Email: `admin@clinica.com`    ├── CasosDeUso.txt

- Senha: `admin123`    ├── MER_Estrutura.txt

    └── ...

## 📁 Estrutura do Projeto```



```## 🚀 Funcionalidades Principais

prototype-melhoria/

├── backend/                 # API FastAPI### 1. Módulo Paciente

│   ├── app/- ✅ Cadastro com CPF, nome, telefone, e-mail e convênio

│   │   ├── models/         # Modelos SQLAlchemy- ✅ Login com e-mail e senha (8-20 caracteres)

│   │   ├── routers/        # Endpoints da API- ✅ Agendamento de consultas por especialidade, médico e horário

│   │   ├── schemas/        # Schemas Pydantic- ✅ Visualização de consultas futuras e passadas

│   │   ├── services/       # Lógica de negócio- ✅ Cancelamento/remarcação de consultas (até 24h antes)

│   │   └── utils/          # Utilitários- ✅ Edição de perfil

│   ├── tests/              # Testes automatizados

│   ├── alembic/            # Migrações do banco### 2. Módulo Médico

│   └── requirements.txt    # Dependências Python- ✅ Login com CRM e senha

├── admin/                   # Portal administrativo- ✅ Visualização de consultas por data

├── medico/                  # Portal do médico- ✅ Cadastro e edição de horários de atendimento

├── paciente/                # Portal do paciente- ✅ Registro de observações pós-consulta

├── js/                      # Scripts JavaScript- ✅ Bloqueio de horários em caso de imprevistos

├── css/                     # Estilos CSS

├── docs/                    # Documentação adicional### 3. Módulo Administrativo

├── .github/- ✅ Cadastro e edição de médicos (nome, CRM, especialidade, convênios)

│   └── workflows/          # CI/CD GitHub Actions- ✅ Visualização e gerenciamento de pacientes

├── docker-compose.yml      # Orquestração Docker- ✅ Geração de relatórios em PDF:

├── nginx.conf              # Configuração Nginx  - Consultas por médico ou especialidade

└── init.sql                # Script inicial do banco  - Taxa de cancelamentos e remarcações

```  - Pacientes mais frequentes

- ✅ Controle de convênios aceitos

## 🎯 Funcionalidades Principais

## 📏 Regras de Negócio Implementadas

### 👤 Portal do Paciente

- ✅ Cadastro e autenticação1. **Cancelamentos**: Consultas só podem ser canceladas/remarcadas até 24h antes

- ✅ Agendamento de consultas2. **Limite de agendamentos**: Cada paciente pode ter no máximo 2 consultas futuras

- ✅ Visualização de consultas (agendadas, realizadas, canceladas)3. **Agenda médica**: Médicos definem horários semanalmente, sistema evita conflitos

- ✅ Gerenciamento de perfil4. **Bloqueio por faltas**: 3 faltas consecutivas bloqueiam novos agendamentos (requer liberação administrativa)

- ✅ Reagendamento e cancelamento de consultas

- ✅ Validação de bloqueio após 3 faltas consecutivas## 🎨 Design e Responsividade



### 👨‍⚕️ Portal do Médico- ✅ Design moderno e responsivo

- ✅ Dashboard com estatísticas- ✅ Cores e identidade visual consistente

- ✅ Agenda diária de consultas- ✅ Navegação intuitiva entre módulos

- ✅ Histórico completo de consultas- ✅ Feedback visual para ações do usuário

- ✅ Observações médicas (CRUD completo)- ✅ Adaptável para desktop, tablet e mobile

- ✅ Gerenciamento de horários de atendimento

- ✅ Bloqueio de horários específicos (férias, compromissos)## 🔧 Tecnologias Utilizadas

- ✅ Máscaras de CPF e telefone

- ✅ Validação de conflitos de horários### Frontend

- **HTML5**: Estrutura das páginas

### 👨‍💼 Portal Administrativo- **CSS3**: Estilização e responsividade

- ✅ Dashboard com métricas gerais- **JavaScript (Vanilla)**: Interatividade e validações

- ✅ Gerenciamento de pacientes (CRUD)- **Font Awesome**: Ícones

- ✅ Gerenciamento de médicos (CRUD)

- ✅ Gerenciamento de convênios (CRUD)### Backend

- ✅ Relatórios diversos:- **Python 3.11+**: Linguagem principal

  - Consultas por médico- **FastAPI**: Framework web RESTful

  - Consultas por especialidade- **SQLAlchemy**: ORM para banco de dados

  - Taxa de cancelamentos- **Pydantic**: Validação de dados

  - Pacientes mais frequentes- **PostgreSQL 15**: Banco de dados relacional

- **JWT**: Autenticação e autorização

## 🔒 Segurança- **ReportLab**: Geração de relatórios PDF

- **Alembic**: Migrações de banco de dados

- Autenticação via JWT tokens

- Senhas criptografadas com bcrypt### DevOps & Testes

- Validação de permissões por tipo de usuário- **Docker + Docker Compose**: Containerização

- Proteção contra SQL Injection (SQLAlchemy ORM)- **Nginx**: Servidor web

- CORS configurado- **Playwright**: Testes E2E

- Validação de dados com Pydantic- **Pytest**: Testes unitários (82 testes - 100% conformidade)



## 🧪 Testes## 🚀 Como Executar o Projeto



```bash### Pré-requisitos

# Executar todos os testes- Docker Desktop instalado e rodando

cd backend- Git (opcional, para clonar o repositório)

python -m pytest tests/ -v- Node.js 18+ (opcional, para rodar testes E2E)



# Executar com cobertura### Opção 1: Usando Scripts (Recomendado)

python -m pytest tests/ -v --cov=app --cov-report=html

```**Windows:**

```powershell

## 📊 Banco de Dados.\scripts\start.ps1

```

### Modelo Entidade-Relacionamento

**Linux/Mac:**

O sistema utiliza as seguintes entidades principais:```bash

chmod +x scripts/start.sh

- **Paciente**: Dados pessoais, convênio, telefone./scripts/start.sh

- **Médico**: Dados pessoais, CRM, especialidade```

- **Administrador**: Credenciais administrativas

- **Consulta**: Agendamentos com status e relacionamentos### Opção 2: Docker Compose Manual

- **HorarioTrabalho**: Horários semanais dos médicos

- **BloqueioHorario**: Períodos bloqueados para agendamento```bash

- **Observacao**: Anotações médicas das consultas# Iniciar todos os serviços

- **Especialidade**: Especialidades médicasdocker-compose up -d

- **PlanoSaude**: Convênios aceitos

# Verificar status

### Migrationsdocker-compose ps



```bash# Ver logs

# Criar nova migrationdocker-compose logs -f

cd backend

alembic revision --autogenerate -m "Descrição da mudança"# Parar serviços

docker-compose down

# Aplicar migrations```

alembic upgrade head

### Opção 3: Abrir no Navegador

# Reverter migration

alembic downgrade -1**Windows:**

``````cmd

.\scripts\abrir-site.bat

## 🌐 Deploy```



### GitHub Pages (Frontend Demo)Ou acesse manualmente: **http://localhost:8081**



O frontend está disponível em: https://rafaelst97.github.io/prototype-melhoria/### URLs de Acesso



*Nota: Para funcionalidade completa, execute localmente com Docker Compose*- **Frontend**: http://localhost:8081

- **Backend API**: http://localhost:8000

### Codespaces- **API Docs (Swagger)**: http://localhost:8000/docs

- **pgAdmin**: http://localhost:5050 (admin@admin.com / admin)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/rafaelst97/prototype-melhoria)

## 🧪 Executando Testes

O projeto está configurado para rodar no GitHub Codespaces com ambiente pré-configurado.

### Testes Backend (Pytest)

## 🐛 Problemas Conhecidos e Soluções

```bash

### Docker não iniciacd backend

```bashpython -m pytest tests/ -v

# Limpar containers e volumes```

docker-compose down -v

docker-compose up -d --build**Resultado esperado:** 82/82 testes passando ✅

```

### Testes Frontend (Playwright)

### Banco de dados não conecta

```bash```bash

# Verificar status do container PostgreSQL# Instalar Playwright (primeira vez)

docker psnpx playwright install chromium

docker logs clinica_db

# Executar todos os testes

# Recriar banco de dadosnpm test

docker-compose down -v

docker-compose up -d# Testes específicos

```npm run test:medico        # Suite médico completa

npm run test:conformidade  # Validação contra requisitos

### Erros de CORSnpm run test:e2e          # Suite E2E completa

- Verifique se está acessando via `http://localhost` e não `http://127.0.0.1````

- Backend está configurado para aceitar requisições do localhost

**Resultado esperado:** 10/11 testes passando (90.9%) ✅

## 📝 Changelog

Veja mais detalhes em [tests/README.md](tests/README.md)

### v2.0.0 (Novembro 2025)

- ✨ Implementação completa do módulo médico## 📖 Como Usar

- ✨ Sistema de observações médicas

- ✨ Bloqueio de horários específicos1. **Abra o arquivo `index.html`** no seu navegador

- ✨ Máscaras de CPF e telefone2. **Selecione o módulo desejado**:

- ✨ Toast notifications redesenhadas   - **Paciente**: Para agendar e gerenciar consultas

- ✨ Validações de conflito de horários   - **Médico**: Para gerenciar agenda e atendimentos

- ✨ Integração total com PostgreSQL   - **Administração**: Para gerenciar a clínica

- 🔧 Correção de bugs no agendamento

- 🔧 Melhorias na UI/UX### Credenciais de Teste (Simuladas)

- 📚 Documentação completa

**Paciente:**

### v1.0.0 (Outubro 2025)- E-mail: qualquer@email.com

- 🎉 Versão inicial do sistema- Senha: qualquer senha (8-20 caracteres)

- ✅ Módulos de paciente e admin funcionais

- ✅ Backend FastAPI completo**Médico:**

- ✅ Docker Compose configurado- CRM: qualquer CRM

- ✅ Testes automatizados- Senha: qualquer senha



## 🤝 Contribuindo**Administrador:**

- Usuário: admin

1. Fork o projeto- Senha: qualquer senha

2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)

3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)> **Nota**: Este é um protótipo de navegação. As credenciais são simuladas e não há validação real de banco de dados.

4. Push para a branch (`git push origin feature/NovaFuncionalidade`)

5. Abra um Pull Request## 📊 Próximos Passos para Implementação



## 📄 Licença1. **Backend**: Desenvolver API REST com Node.js ou Python

2. **Banco de Dados**: Implementar MySQL ou PostgreSQL

Este projeto é licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.3. **Autenticação**: Sistema de autenticação JWT

4. **Notificações**: E-mail/SMS para lembretes de consulta

## 📞 Contato5. **Relatórios PDF**: Implementar geração real de PDFs

6. **Testes**: Testes unitários e de integração

- **Repositório**: https://github.com/rafaelst97/prototype-melhoria7. **Deploy**: Hospedagem em servidor cloud

- **Issues**: https://github.com/rafaelst97/prototype-melhoria/issues

## 👥 Equipe de Desenvolvimento

## 🙏 Agradecimentos

- **Disciplina**: Melhoria de Processos de Software

- UNIVALI - Universidade do Vale do Itajaí- **Instituição**: UNIVALI - Escola Politécnica

- Professores da disciplina de Melhoria de Processo de Software- **Professora**: Daniela S. Moreira da Silva

- Comunidade open-source pelos frameworks utilizados- **Data**: Outubro de 2025



---## 📝 Documentação de Processos



⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!Este projeto segue as práticas de Melhoria de Processos de Software, incluindo:



*Desenvolvido com ❤️ pela equipe Clínica Saúde+*- ✅ Planejamento de escopo e requisitos

- ✅ Cronograma de entregas
- ✅ Métricas de qualidade
- ✅ Documentação e acompanhamento

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos.

---

**Clínica Saúde+** - Sistema de Agendamento de Consultas Médicas
#   p r o t o t y p e - c l i n i c a - j u l e s  
 #   p r o t o t y p e - c l i n i c a - j u l e s  
 