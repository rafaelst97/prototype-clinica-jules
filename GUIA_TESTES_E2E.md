# 🌐 Guia de Testes E2E (End-to-End) com Selenium

## 📋 Pré-requisitos

1. **Python 3.13+** instalado
2. **Google Chrome** instalado
3. **Dependências Python** instaladas:
   ```bash
   pip install selenium webdriver-manager pytest
   ```

4. **Aplicação rodando:**
   - Backend (FastAPI) na porta 8000
   - Frontend (HTML/JS) na porta 80

---

## 🚀 Como Executar

### **Passo 1: Iniciar o Backend**

Abra um terminal e execute:

```powershell
cd "c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\backend"
python -m uvicorn app.main:app --reload --port 8000
```

Aguarde até ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### **Passo 2: Iniciar o Frontend**

Abra **outro terminal** e execute:

```powershell
cd "c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto"
python -m http.server 80
```

> **Nota:** No Windows, pode ser necessário executar como Administrador para usar a porta 80.

Se der erro, use a porta 8080:
```powershell
python -m http.server 8080
```

E atualize `base_url` no arquivo de teste para `http://localhost:8080`

### **Passo 3: Executar os Testes E2E**

Abra um **terceiro terminal** e execute:

```powershell
cd "c:\Users\rafae\OneDrive - UNIVALI\Melhoria de Processo de Software\Projeto\backend"

# Executar todos os testes E2E
python -m pytest tests/test_e2e_browser.py -v -s

# Executar apenas testes do paciente
python -m pytest tests/test_e2e_browser.py::TestPacienteJourney -v -s

# Executar apenas testes do médico
python -m pytest tests/test_e2e_browser.py::TestMedicoJourney -v -s

# Executar apenas testes do admin
python -m pytest tests/test_e2e_browser.py::TestAdministradorJourney -v -s
```

---

## 🎥 Modos de Execução

### **Modo com Interface (Padrão)**
Por padrão, você verá o Chrome abrindo e executando os testes automaticamente.

### **Modo Headless (Sem Interface)**
Para executar sem abrir o navegador, edite o arquivo `test_e2e_browser.py`:

Descomente a linha:
```python
chrome_options.add_argument("--headless")
```

---

## 📊 Saída Esperada

```
tests/test_e2e_browser.py::TestPacienteJourney::test_paciente_login PASSED
✅ Login do paciente bem-sucedido

tests/test_e2e_browser.py::TestPacienteJourney::test_paciente_visualizar_dashboard PASSED
✅ Dashboard do paciente carregado

tests/test_e2e_browser.py::TestPacienteJourney::test_paciente_agendar_consulta PASSED
✅ Consulta agendada (ou tentativa realizada)

tests/test_e2e_browser.py::TestPacienteJourney::test_paciente_visualizar_consultas PASSED
✅ Lista de consultas carregada

tests/test_e2e_browser.py::TestPacienteJourney::test_paciente_logout PASSED
✅ Logout do paciente bem-sucedido

tests/test_e2e_browser.py::TestMedicoJourney::test_medico_login PASSED
✅ Login do médico bem-sucedido

tests/test_e2e_browser.py::TestMedicoJourney::test_medico_visualizar_dashboard PASSED
✅ Dashboard do médico carregado

tests/test_e2e_browser.py::TestMedicoJourney::test_medico_visualizar_agenda PASSED
✅ Agenda do médico carregada

tests/test_e2e_browser.py::TestMedicoJourney::test_medico_gerenciar_horarios PASSED
✅ Página de horários carregada

tests/test_e2e_browser.py::TestMedicoJourney::test_medico_visualizar_consultas PASSED
✅ Página de consultas do médico carregada

tests/test_e2e_browser.py::TestMedicoJourney::test_medico_logout PASSED
✅ Logout do médico bem-sucedido

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_login PASSED
✅ Login do administrador bem-sucedido

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_visualizar_dashboard PASSED
✅ Dashboard administrativo carregado

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_gerenciar_pacientes PASSED
✅ Página de gerenciamento de pacientes carregada

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_gerenciar_medicos PASSED
✅ Página de gerenciamento de médicos carregada

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_visualizar_relatorios PASSED
✅ Página de relatórios carregada

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_gerenciar_convenios PASSED
✅ Página de convênios carregada

tests/test_e2e_browser.py::TestAdministradorJourney::test_admin_logout PASSED
✅ Logout do administrador bem-sucedido

==================== 18 passed in 87.23s ====================
```

---

## 🔍 O Que os Testes Validam

### **Jornada do Paciente** (5 testes)
1. ✅ Login com credenciais corretas
2. ✅ Dashboard carrega com informações
3. ✅ Formulário de agendamento funciona
4. ✅ Lista de consultas é exibida
5. ✅ Logout funciona corretamente

### **Jornada do Médico** (5 testes)
1. ✅ Login com credenciais de médico
2. ✅ Dashboard médico carrega
3. ✅ Agenda de consultas é exibida
4. ✅ Página de gerenciamento de horários funciona
5. ✅ Logout funciona

### **Jornada do Administrador** (6 testes)
1. ✅ Login com credenciais de admin
2. ✅ Dashboard administrativo carrega
3. ✅ Página de gerenciamento de pacientes funciona
4. ✅ Página de gerenciamento de médicos funciona
5. ✅ Página de relatórios é acessível
6. ✅ Página de convênios/planos funciona
7. ✅ Logout funciona

---

## ⚠️ Solução de Problemas

### **Problema: "Chrome driver not found"**
**Solução:**
```powershell
python -m pip install --upgrade webdriver-manager
```

### **Problema: "Port 80 já está em uso"**
**Solução:** Use porta alternativa
```powershell
python -m http.server 8080
```
E no teste, mude:
```python
return "http://localhost:8080"
```

### **Problema: "Connection refused"**
**Solução:** Verifique se backend e frontend estão rodando:
```powershell
# Verificar backend
curl http://localhost:8000/docs

# Verificar frontend
curl http://localhost/index.html
```

### **Problema: "Element not found"**
**Solução:** Aumentar timeout no teste:
```python
driver.implicitly_wait(15)  # Aumentar de 10 para 15
```

### **Problema: Teste falha intermitentemente**
**Solução:** Adicionar mais `time.sleep()` entre ações:
```python
button.click()
time.sleep(2)  # Aguardar processamento
```

---

## 🎯 Credenciais de Teste

Os testes usam as seguintes credenciais (devem estar no banco):

**Paciente:**
- Email: `carlos@email.com`
- Senha: `paciente123`

**Médico:**
- Email: `joao@clinica.com`
- Senha: `medico123`

**Administrador:**
- Email: `admin@clinica.com`
- Senha: `admin123`

> ⚠️ **Importante:** Execute o script de seed data antes dos testes:
> ```bash
> cd backend
> python seed_data.py
> ```

---

## 📸 Screenshots Automáticos

Para capturar screenshots durante os testes, adicione no código:

```python
def test_meu_teste(driver):
    driver.get("http://localhost/paciente/login.html")
    
    # Capturar screenshot
    driver.save_screenshot("screenshots/login.png")
    
    # ... resto do teste
```

---

## 🔄 Executar Testes Continuamente

Para executar os testes sempre que houver mudanças nos arquivos:

```powershell
# Instalar pytest-watch
pip install pytest-watch

# Executar
cd backend
ptw tests/test_e2e_browser.py -v
```

---

## 📊 Gerar Relatório HTML

Para gerar um relatório HTML dos testes:

```powershell
pip install pytest-html

python -m pytest tests/test_e2e_browser.py --html=relatorio_e2e.html --self-contained-html
```

O relatório será salvo em `relatorio_e2e.html`

---

## 🎓 Boas Práticas

1. ✅ Sempre execute `seed_data.py` antes dos testes E2E
2. ✅ Mantenha backend e frontend rodando durante os testes
3. ✅ Use `time.sleep()` moderadamente (só quando necessário)
4. ✅ Limpe localStorage entre testes de diferentes usuários
5. ✅ Feche o navegador após todos os testes (fixture já faz isso)
6. ✅ Execute os testes em ordem (paciente → médico → admin)

---

## 🚀 CI/CD (Opcional)

Para executar os testes E2E em CI/CD (GitHub Actions):

```yaml
# .github/workflows/e2e-tests.yml
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
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install selenium webdriver-manager pytest
      
      - name: Start backend
        run: |
          cd backend
          python -m uvicorn app.main:app --port 8000 &
          sleep 10
      
      - name: Start frontend
        run: |
          python -m http.server 8080 &
          sleep 5
      
      - name: Run E2E tests
        run: |
          cd backend
          pytest tests/test_e2e_browser.py -v
```

---

**🎉 Pronto! Agora você pode executar testes E2E completos do sistema! 🎉**

---

*Última atualização: 26/01/2025*
