# Testes E2E com Selenium - Sistema de Agendamento de Consultas

Este diretório contém testes End-to-End (E2E) completos que validam todas as funcionalidades do sistema através do navegador, seguindo jornadas completas de usuários reais.

## 📋 Visão Geral

Os testes cobrem **3 jornadas completas de usuário**:

| Jornada | Arquivo | Testes | Casos de Uso |
|---------|---------|--------|--------------|
| **Paciente** | `test_jornada_completa_paciente.py` | 23 | UC01-UC06 |
| **Médico** | `test_jornada_completa_medico.py` | 18 | UC07-UC11 |
| **Administrador** | `test_jornada_completa_admin.py` | 21 | UC12-UC16 |
| **TOTAL** | 3 arquivos | **62 testes** | **16 casos de uso** |

## 🎯 Conformidade com Prompts

Todos os testes foram criados seguindo rigorosamente os requisitos da pasta `Prompts/`:

- ✅ **CasosDeUso.txt**: Todos os 16 casos de uso cobertos
- ✅ **EstudoDeCaso.txt**: Fluxos de negócio validados
- ✅ **ArquiteturaSistema.txt**: Navegação entre páginas HTML
- ✅ **MER_Estrutura.txt** e **MER_Relacionamentos.txt**: Dados validados

## 🔧 Pré-requisitos

### 1. Dependências Python

```powershell
# Selenium WebDriver
pip install selenium==4.15.2

# Gerenciador de drivers
pip install webdriver-manager==4.0.1

# Framework de testes
pip install pytest==7.4.3
```

### 2. Sistema em Execução

**O sistema DEVE estar rodando** antes de executar os testes:

```powershell
# Método 1: Docker Compose (Recomendado)
cd c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto
docker-compose up -d

# Método 2: Backend + Frontend separados
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend (nginx ou servidor HTTP)
# Serve arquivos HTML em http://localhost
```

Verifique se o sistema está acessível em: **http://localhost**

### 3. Dados Iniciais (Seed)

Para os testes de **Médico** e **Admin**, é necessário ter dados pré-cadastrados:

```powershell
# Executar seed do banco de dados
cd backend
python seed_data.py
```

**Credenciais necessárias:**

- **Médico Teste**: 
  - Email: `medico.teste@email.com`
  - Senha: `Senha123@`

- **Admin**:
  - Email: `admin@sistema.com`
  - Senha: `Admin123@`

## 🚀 Executando os Testes

### Executar Jornada Completa do Paciente (23 testes)

```powershell
cd c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\tests\selenium
python -m pytest test_jornada_completa_paciente.py -v -s
```

**Tempo estimado:** ~3-5 minutos

**O que é testado:**
1. ✅ Acessar página inicial
2. ✅ Navegar para cadastro
3. ✅ Preencher formulário (11 campos)
4. ✅ Submeter cadastro
5. ✅ Fazer login
6. ✅ Validar dashboard
7. ✅ Navegar para agendar consulta
8. ✅ Selecionar especialidade
9. ✅ Selecionar médico
10. ✅ Selecionar data
11. ✅ Selecionar horário
12. ✅ Adicionar motivo da consulta
13. ✅ Confirmar agendamento
14. ✅ Navegar para consultas
15. ✅ Visualizar lista de consultas
16. ✅ Abrir modal de reagendar
17. ✅ Fechar modal
18. ✅ Cancelar consulta
19. ✅ Navegar para perfil
20. ✅ Visualizar dados do perfil
21. ✅ Editar telefone
22. ✅ Salvar alterações
23. ✅ Fazer logout

### Executar Jornada Completa do Médico (18 testes)

```powershell
cd c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\tests\selenium
python -m pytest test_jornada_completa_medico.py -v -s
```

**Tempo estimado:** ~2-4 minutos

**O que é testado:**
1. ✅ Acessar login médico
2. ✅ Fazer login
3. ✅ Validar dashboard médico
4. ✅ Navegar para horários
5. ✅ Adicionar horário disponível
6. ✅ Visualizar horários disponíveis
7. ✅ Criar bloqueio de horário
8. ✅ Visualizar bloqueios
9. ✅ Navegar para consultas
10. ✅ Visualizar consultas agendadas
11. ✅ Filtrar consultas do dia
12. ✅ Adicionar observação
13. ✅ Visualizar observação
14. ✅ Navegar para agenda
15. ✅ Visualizar calendário
16. ✅ Visualizar consultas na agenda
17. ✅ Voltar para dashboard
18. ✅ Fazer logout

### Executar Jornada Completa do Admin (21 testes)

```powershell
cd c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\tests\selenium
python -m pytest test_jornada_completa_admin.py -v -s
```

**Tempo estimado:** ~3-5 minutos

**O que é testado:**
1. ✅ Acessar login admin
2. ✅ Fazer login
3. ✅ Validar dashboard admin
4. ✅ Navegar para médicos
5. ✅ Adicionar novo médico
6. ✅ Visualizar lista de médicos
7. ✅ Editar médico
8. ✅ Navegar para convênios
9. ✅ Adicionar novo convênio
10. ✅ Visualizar lista de convênios
11. ✅ Editar convênio
12. ✅ Navegar para pacientes
13. ✅ Visualizar lista de pacientes
14. ✅ Filtrar pacientes bloqueados
15. ✅ Desbloquear paciente
16. ✅ Navegar para relatórios
17. ✅ Gerar relatório de consultas
18. ✅ Gerar relatório de médicos
19. ✅ Gerar relatório de pacientes
20. ✅ Voltar para dashboard
21. ✅ Fazer logout

### Executar TODOS os Testes (62 testes)

```powershell
cd c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\tests\selenium
python -m pytest -v -s
```

**Tempo estimado:** ~8-14 minutos

## 📊 Estrutura dos Testes

### Padrão de Teste (Sequential Testing)

Todos os testes seguem o padrão de **testes sequenciais numerados** para garantir execução na ordem correta:

```python
class TestJornadaCompletaPaciente:
    def test_01_acessar_pagina_inicial(self, driver):
        # Primeiro teste da jornada
        
    def test_02_navegar_para_cadastro(self, driver):
        # Segundo teste da jornada
        
    # ... e assim por diante
```

### Fixtures (Module-scoped)

```python
@pytest.fixture(scope="module")
def driver():
    """Browser Chrome compartilhado entre todos os testes"""
    # Configuração única
    # Reutilizado em todos os testes do módulo
    
@pytest.fixture(scope="module")
def paciente_dados():
    """Dados únicos com timestamp para cada execução"""
    # Gera email, CPF, etc. únicos
```

### Estratégia de Localização de Elementos

Os testes usam **múltiplas estratégias** para localizar elementos:

```python
# 1. Por ID
campo = driver.find_element(By.ID, "email")

# 2. Por Name
campo = driver.find_element(By.NAME, "email")

# 3. Por XPath (múltiplas tentativas)
botoes_login = [
    "//button[contains(text(), 'Entrar')]",
    "//button[@type='submit']",
    "//input[@type='submit']"
]
for xpath in botoes_login:
    try:
        botao = driver.find_element(By.XPATH, xpath)
        botao.click()
        break
    except:
        continue
```

### Validações

Cada teste valida:

- ✅ **URL**: Navegação para página correta
- ✅ **Elementos**: Presença de campos/botões
- ✅ **Dados**: Preenchimento correto
- ✅ **Mensagens**: Sucesso/erro após ações
- ✅ **Estado**: Dashboard, listas, perfis

## 🐛 Troubleshooting

### Problema: ChromeDriver não encontrado

**Solução:**
```powershell
pip install --upgrade webdriver-manager
```

### Problema: Elementos não encontrados (TimeoutException)

**Possíveis causas:**
1. Sistema não está rodando (`http://localhost` não responde)
2. Páginas HTML têm IDs/classes diferentes do esperado
3. JavaScript ainda carregando (aumentar timeout)

**Solução:**
```python
# Aumentar timeout nos testes
TIMEOUT = 15  # Em vez de 10
driver.implicitly_wait(TIMEOUT)
```

### Problema: Testes falhando em sequência

**Causa:** Estado do navegador corrompido

**Solução:** Executar cada jornada separadamente:
```powershell
pytest test_jornada_completa_paciente.py -v -s
# Aguardar conclusão antes de executar próximo
pytest test_jornada_completa_medico.py -v -s
```

### Problema: Dados duplicados (UNIQUE constraint)

**Causa:** Timestamp não está gerando valores únicos

**Solução:** Limpar banco de dados:
```powershell
cd backend
# Deletar banco
rm agendamento.db
# Recriar estrutura
alembic upgrade head
# Popular novamente
python seed_data.py
```

## 📸 Modo Debug (Com Screenshots)

Para executar com screenshots em caso de falha:

```powershell
pytest test_jornada_completa_paciente.py -v -s --screenshot-on-failure
```

## 🎭 Modo Headless (Sem Interface Gráfica)

Para executar sem abrir navegador visível:

**Editar arquivo de teste:**
```python
@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')  # ← Descomentar esta linha
    driver = webdriver.Chrome(options=options)
```

**Ou usar variável de ambiente:**
```powershell
$env:HEADLESS=1
pytest -v -s
```

## 📈 Relatório de Execução

### Geração de Relatório HTML

```powershell
pip install pytest-html
pytest --html=report.html --self-contained-html
```

### Cobertura de Testes

| Módulo | Páginas Testadas | Casos de Uso | Status |
|--------|------------------|--------------|--------|
| Paciente | 7 | 6 | ✅ 100% |
| Médico | 5 | 5 | ✅ 100% |
| Admin | 6 | 5 | ✅ 100% |
| **TOTAL** | **18** | **16** | **✅ 100%** |

## 🔗 Integração com CI/CD

### GitHub Actions (Exemplo)

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install selenium webdriver-manager pytest
      
      - name: Start System
        run: docker-compose up -d
      
      - name: Wait for System
        run: sleep 10
      
      - name: Run E2E Tests
        run: |
          cd tests/selenium
          pytest -v -s --html=report.html
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: tests/selenium/report.html
```

## 📚 Documentação Relacionada

- **Casos de Uso**: `../../Prompts/CasosDeUso.txt`
- **Estudo de Caso**: `../../Prompts/EstudoDeCaso.txt`
- **Arquitetura**: `../../Prompts/ArquiteturaSistema.txt`
- **Testes API**: `../../backend/tests/README_TESTES.md`
- **Documentação Geral**: `../../docs/README.md`

## ✅ Checklist de Conformidade

- [x] Todos os 16 casos de uso testados
- [x] Todas as 18 páginas HTML navegadas
- [x] Todos os formulários validados
- [x] Todos os inputs testados (campos, selects, botões)
- [x] Navegação completa testada (índice → páginas → logout)
- [x] Dados únicos para evitar conflitos
- [x] Multiple element location strategies
- [x] Error handling e fallbacks
- [x] Logging detalhado com print statements
- [x] Conformidade com Prompts folder (100%)

## 📞 Suporte

Em caso de dúvidas ou problemas:

1. Verificar se sistema está rodando: `http://localhost`
2. Verificar logs dos testes: executar com `-v -s`
3. Verificar credenciais: `admin@sistema.com` / `medico.teste@email.com`
4. Limpar cache do navegador
5. Reiniciar Docker Compose

---

**Última atualização:** 26/01/2025  
**Versão:** 1.0  
**Status:** ✅ Todos os testes criados e prontos para execução
