# 🧪 Testes Automatizados de Interface - Clínica Saúde+

## 📋 Descrição

Suite completa de testes automatizados E2E (End-to-End) para validar todas as funcionalidades e regras de negócio do sistema.

## 🎯 Cobertura de Testes

### ✅ Módulo Paciente
- **Cadastro** (4 testes)
  - `test_001`: Acessar página de cadastro
  - `test_002`: Validar campos obrigatórios
  - `test_003`: Cadastro completo com sucesso
  - `test_004`: Cadastro com email duplicado

- **Login/Logout** (3 testes)
  - `test_005`: Login com credenciais válidas
  - `test_006`: Login com credenciais inválidas
  - `test_007`: Realizar logout

- **Agendamento de Consultas** (4 testes)
  - `test_008`: Acessar página de agendamento
  - `test_009`: Carregar especialidades
  - `test_010`: Agendar consulta com sucesso
  - `test_011`: Validar limite de 2 consultas futuras **(RN2)**

- **Visualização** (2 testes)
  - `test_012`: Visualizar dashboard
  - `test_013`: Visualizar lista de consultas

- **Cancelamento** (3 testes)
  - `test_014`: Abrir modal de cancelamento
  - `test_015`: Cancelar consulta com sucesso
  - `test_016`: Validar prazo de 24h **(RN1)**

- **Reagendamento** (2 testes)
  - `test_017`: Abrir modal de reagendamento
  - `test_018`: Reagendar consulta com sucesso **(RN1)**

### 🚧 Regras de Negócio Testadas

- **RN1**: Cancelamento/Reagendamento até 24h antes
- **RN2**: Máximo de 2 consultas futuras por paciente
- **RN3**: Prevenção de conflitos de horário
- **RN4**: Bloqueio após 3 faltas consecutivas

## 🔧 Pré-requisitos

### 1. Instalar Python 3.11+
```bash
python --version
```

### 2. Instalar Chrome/Chromium
Os testes usam Chrome WebDriver (Selenium).

### 3. Instalar Dependências
```bash
# Navegar até a pasta tests
cd tests

# Instalar dependências
pip install -r requirements-tests.txt
```

### 4. Sistema em Execução
```bash
# Iniciar containers Docker
docker-compose up -d

# Verificar se estão rodando
docker-compose ps
```

**URLs necessárias:**
- Frontend: http://localhost:80
- Backend: http://localhost:8000

## 🚀 Executar Testes

### Todos os Testes
```bash
# Executar todos os testes com relatório HTML
pytest tests/test_interface_completo.py -v --html=report.html --self-contained-html
```

### Testes Específicos
```bash
# Apenas testes de cadastro
pytest tests/test_interface_completo.py::TestCadastroPaciente -v

# Apenas testes de login
pytest tests/test_interface_completo.py::TestLoginPaciente -v

# Apenas testes de agendamento
pytest tests/test_interface_completo.py::TestAgendamentoConsulta -v

# Apenas testes de cancelamento
pytest tests/test_interface_completo.py::TestCancelamentoConsulta -v

# Apenas testes de reagendamento
pytest tests/test_interface_completo.py::TestReagendamentoConsulta -v
```

### Executar Teste Individual
```bash
# Exemplo: apenas teste 010
pytest tests/test_interface_completo.py::TestAgendamentoConsulta::test_010_agendar_consulta_sucesso -v
```

### Executar em Paralelo (mais rápido)
```bash
pytest tests/test_interface_completo.py -v -n 4
```

### Com Relatório Detalhado
```bash
pytest tests/test_interface_completo.py -v --html=report.html --self-contained-html --capture=no
```

## 📊 Interpretar Resultados

### Saída do Console
```
tests/test_interface_completo.py::TestCadastroPaciente::test_001_acessar_pagina_cadastro PASSED [ 5%]
tests/test_interface_completo.py::TestCadastroPaciente::test_002_cadastro_campos_obrigatorios PASSED [10%]
...
========================= 20 passed in 180.50s =========================
```

### Relatório HTML
Abrir `report.html` no navegador para ver:
- ✅ Testes passados
- ❌ Testes falhados
- ⚠️ Testes pulados
- 📊 Tempo de execução
- 📸 Screenshots (se implementado)
- 📝 Logs detalhados

### Status dos Testes
- **PASSED** ✅ - Teste passou
- **FAILED** ❌ - Teste falhou (bug encontrado)
- **SKIPPED** ⏭️ - Teste pulado
- **ERROR** 🔴 - Erro na execução do teste

## 🐛 Debugging

### Ver Logs Detalhados
```bash
pytest tests/test_interface_completo.py -v -s --log-cli-level=DEBUG
```

### Pausar em Falha
```bash
pytest tests/test_interface_completo.py -v --pdb
```

### Executar com Screenshot em Falha
Adicionar ao código:
```python
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get('driver') or item.funcargs.get('driver_logado')
        if driver:
            driver.save_screenshot(f"screenshots/error_{item.name}.png")
```

## 📝 Estrutura dos Testes

```python
class TestCadastroPaciente:
    """Agrupa testes relacionados a cadastro"""
    
    @pytest.fixture
    def driver(self):
        """Setup e teardown do navegador"""
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    def test_001_exemplo(self, driver):
        """Teste individual"""
        # Arrange (preparar)
        driver.get("http://localhost/cadastro.html")
        
        # Act (executar)
        driver.find_element(By.ID, "nome").send_keys("Teste")
        
        # Assert (verificar)
        assert driver.title == "Cadastro"
```

## ⚙️ Configuração

### Alterar URLs
Editar em `test_interface_completo.py`:
```python
BASE_URL = "http://localhost:80"
BACKEND_URL = "http://localhost:8000"
```

### Alterar Timeout
```python
TIMEOUT = 10  # segundos
```

### Usar Modo Headless (sem interface gráfica)
```python
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)
```

## 🔍 Casos de Teste Detalhados

### RN1: Prazo de 24h
**Teste 016**: Valida que consultas não podem ser canceladas/reagendadas com menos de 24h de antecedência.

**Como funciona:**
1. Agendar consulta para amanhã
2. Tentar cancelar (deve funcionar)
3. Agendar consulta para hoje à noite
4. Tentar cancelar (deve falhar com erro)

### RN2: Limite de 2 Consultas
**Teste 011**: Valida que paciente não pode ter mais de 2 consultas futuras.

**Como funciona:**
1. Agendar 1ª consulta (sucesso)
2. Agendar 2ª consulta (sucesso)
3. Agendar 3ª consulta (deve falhar com erro)

### RN3: Conflitos de Horário
**Teste 020**: Valida que apenas horários disponíveis são exibidos.

**Como funciona:**
1. Selecionar médico e data
2. Verificar horários disponíveis
3. Confirmar que horários ocupados não aparecem

### RN4: Bloqueio por 3 Faltas
**Teste 019**: Valida bloqueio automático após 3 faltas consecutivas.

**Requer:**
- Paciente com 3 consultas marcadas como "faltou"
- Campo `esta_bloqueado = true`
- Tentativa de agendar deve retornar erro

## 📈 Métricas de Qualidade

### Tempo de Execução Esperado
- **Testes rápidos** (smoke): ~30s
- **Suite completa**: ~3-5min
- **Com screenshots**: ~7-10min

### Taxa de Sucesso Esperada
- **Desenvolvimento**: 80-90%
- **Homologação**: 95-98%
- **Produção**: 99%+

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r tests/requirements-tests.txt
      - name: Run tests
        run: pytest tests/test_interface_completo.py -v --html=report.html
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: report.html
```

## 📞 Suporte

**Problemas Comuns:**

1. **"ChromeDriver not found"**
   - Instalar: `pip install webdriver-manager`
   - Usar: `ChromeDriverManager().install()`

2. **"Connection refused"**
   - Verificar se Docker está rodando
   - Verificar portas: `docker-compose ps`

3. **"Element not found"**
   - Aumentar timeout
   - Verificar seletores CSS/XPath
   - Adicionar `time.sleep()` temporário

4. **Testes muito lentos**
   - Usar modo headless
   - Executar em paralelo com `-n`
   - Reduzir `time.sleep()`

## 📄 Licença

Este projeto é parte do trabalho acadêmico da disciplina de Melhoria de Processos de Software - UNIVALI.

---

**Última atualização:** 03/11/2025  
**Versão:** 1.0  
**Testes criados:** 20  
**Cobertura:** Módulo Paciente Completo
