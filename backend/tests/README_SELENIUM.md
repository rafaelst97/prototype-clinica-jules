# Testes E2E com Selenium

## 📋 Visão Geral

Estes testes simulam interações reais de usuários no navegador, validando toda a jornada de uso do sistema.

## 🎯 Casos de Uso Cobertos

### Módulo Paciente (8 testes)
- ✅ UC3: Cadastrar-se no Sistema
- ✅ UC4: Agendar Consulta
- ✅ UC5: Visualizar Consultas Agendadas
- ✅ UC6: Cancelar/Reagendar Consulta
- ✅ Visualizar Perfil

### Módulo Médico (9 testes)
- ✅ UC7: Gerenciar Horários Disponíveis
- ✅ UC8: Visualizar Consultas Agendadas
- ✅ UC9: Registrar Observações
- ✅ UC10: Bloquear Horários Específicos
- ✅ Visualizar Agenda e Dashboard

### Módulo Admin (12 testes)
- ✅ UC12: Gerar Relatórios em PDF
- ✅ UC13: Gerenciar Cadastro de Médicos
- ✅ UC14: Gerenciar Planos de Saúde
- ✅ UC15: Desbloquear Contas de Pacientes
- ✅ UC16: Visualizar Observações
- ✅ Dashboard e Navegação

## 🚀 Como Executar

### Pré-requisitos

1. **Google Chrome instalado** (versão recente)
2. **Dependências instaladas**:
   ```bash
   pip install selenium==4.15.2 webdriver-manager==4.0.1
   ```

3. **Servidor rodando**: O sistema deve estar acessível em `http://localhost:8000`

### Iniciar o Servidor

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend (se necessário servidor HTTP)
# O Chrome pode abrir arquivos HTML diretamente, mas para evitar CORS:
python -m http.server 8080
```

### Executar Testes

```bash
# Executar todos os testes Selenium
pytest tests/test_selenium_*.py -v

# Executar módulo específico
pytest tests/test_selenium_paciente.py -v
pytest tests/test_selenium_medico.py -v
pytest tests/test_selenium_admin.py -v

# Executar teste específico
pytest tests/test_selenium_paciente.py::TestCadastroPaciente::test_cadastro_paciente_sucesso -v
```

## 🔧 Configuração

### Modo Headless (sem interface gráfica)

Edite `tests/conftest_selenium.py` e descomente a linha:

```python
chrome_options.add_argument("--headless")
```

### Ajustar Timeouts

Modifique os valores em `conftest_selenium.py`:

```python
driver.implicitly_wait(10)  # Espera implícita (segundos)
```

## 📸 Screenshots

Os testes podem capturar screenshots em caso de falha. Para habilitar:

```python
# Em conftest_selenium.py, adicione:
@pytest.fixture(scope="function")
def driver_with_screenshots(driver):
    yield driver
    if hasattr(driver, 'save_screenshot'):
        driver.save_screenshot(f"screenshot_{datetime.now().timestamp()}.png")
```

## 🐛 Troubleshooting

### ChromeDriver não encontrado
O WebDriver Manager baixa automaticamente. Se houver erro:
```bash
pip install --upgrade webdriver-manager
```

### Timeout nos testes
- Aumente o `implicitly_wait` em `conftest_selenium.py`
- Verifique se o servidor está rodando
- Verifique se as páginas HTML estão acessíveis

### Elemento não encontrado
- Verifique se os IDs dos elementos no HTML correspondem aos seletores
- Use `time.sleep(1)` temporariamente para debug
- Verifique o console do navegador

## 📊 Relatório de Execução

```bash
# Gerar relatório HTML
pytest tests/test_selenium_*.py --html=report.html --self-contained-html

# Com cobertura
pytest tests/test_selenium_*.py --cov=app --cov-report=html
```

## 🎯 Próximos Passos

1. ✅ Criar testes Selenium para todos os módulos
2. ⏳ Executar testes e validar interface
3. ⏳ Capturar screenshots de sucesso
4. ⏳ Documentar casos de teste com evidências
5. ⏳ Integrar com CI/CD (GitHub Actions)

## 📝 Notas Importantes

- **Dados de Teste**: Use `seed_data.py` para popular dados iniciais
- **Limpeza**: Cada teste limpa o localStorage antes de executar
- **Isolamento**: Testes são independentes e podem rodar em qualquer ordem
- **Performance**: Modo headless é ~30% mais rápido
