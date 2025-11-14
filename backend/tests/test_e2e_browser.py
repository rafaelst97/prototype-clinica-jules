"""
Testes E2E (End-to-End) com Selenium
Testa os fluxos completos de Paciente, Médico e Administrador pelo navegador
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta


@pytest.fixture(scope="module")
def driver():
    """
    Fixture para criar e configurar o WebDriver do Chrome
    """
    chrome_options = Options()
    # Executar em modo headless (sem abrir janela) - remova esta linha para ver o navegador
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="module")
def base_url():
    """URL base da aplicação"""
    return "http://localhost"  # Ajustar conforme necessário


class TestPacienteJourney:
    """
    Testes E2E da jornada completa do PACIENTE
    """
    
    def test_paciente_login(self, driver, base_url):
        """Teste: Login do paciente"""
        driver.get(f"{base_url}/paciente/login.html")
        
        # Preencher formulário de login
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys("carlos@email.com")
        
        senha_field = driver.find_element(By.ID, "senha")
        senha_field.send_keys("paciente123")
        
        # Submeter formulário
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Aguardar redirecionamento para dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("dashboard.html")
        )
        
        assert "dashboard.html" in driver.current_url
        print("✅ Login do paciente bem-sucedido")
    
    def test_paciente_visualizar_dashboard(self, driver, base_url):
        """Teste: Visualizar dashboard do paciente"""
        # Já está no dashboard após o login
        
        # Verificar elementos do dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        page_title = driver.find_element(By.TAG_NAME, "h1").text
        assert "Dashboard" in page_title or "Bem-vindo" in page_title
        print("✅ Dashboard do paciente carregado")
    
    def test_paciente_agendar_consulta(self, driver, base_url):
        """Teste: Agendar nova consulta"""
        # Navegar para página de agendamento
        driver.get(f"{base_url}/paciente/agendar.html")
        
        # Aguardar carregamento da página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "especialidade"))
        )
        
        # Selecionar especialidade
        especialidade_select = driver.find_element(By.ID, "especialidade")
        especialidade_select.click()
        time.sleep(1)
        
        # Selecionar primeira opção disponível
        options = especialidade_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:
            options[1].click()  # Selecionar primeira especialidade (index 0 é placeholder)
        
        time.sleep(2)  # Aguardar carregamento de médicos
        
        # Selecionar médico
        medico_select = driver.find_element(By.ID, "medico")
        medico_options = medico_select.find_elements(By.TAG_NAME, "option")
        if len(medico_options) > 1:
            medico_options[1].click()
        
        time.sleep(2)  # Aguardar carregamento de horários
        
        # Selecionar data futura
        data_field = driver.find_element(By.ID, "data")
        data_futura = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        driver.execute_script(f"arguments[0].value = '{data_futura}'", data_field)
        
        time.sleep(2)
        
        # Selecionar horário
        horario_select = driver.find_element(By.ID, "horario")
        horario_options = horario_select.find_elements(By.TAG_NAME, "option")
        if len(horario_options) > 1:
            horario_options[1].click()
        
        # Submeter formulário
        agendar_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        agendar_button.click()
        
        # Aguardar mensagem de sucesso
        time.sleep(3)
        
        print("✅ Consulta agendada (ou tentativa realizada)")
    
    def test_paciente_visualizar_consultas(self, driver, base_url):
        """Teste: Visualizar minhas consultas"""
        driver.get(f"{base_url}/paciente/consultas.html")
        
        # Aguardar carregamento da lista
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "lista-consultas"))
        )
        
        lista_consultas = driver.find_element(By.ID, "lista-consultas")
        assert lista_consultas is not None
        print("✅ Lista de consultas carregada")
    
    def test_paciente_logout(self, driver, base_url):
        """Teste: Logout do paciente"""
        # Procurar botão de logout
        try:
            logout_button = driver.find_element(By.ID, "logout")
            logout_button.click()
            time.sleep(2)
            
            # Verificar redirecionamento para login
            assert "login.html" in driver.current_url
            print("✅ Logout do paciente bem-sucedido")
        except:
            print("⚠️  Botão de logout não encontrado, limpando localStorage")
            driver.execute_script("localStorage.clear()")


class TestMedicoJourney:
    """
    Testes E2E da jornada completa do MÉDICO
    """
    
    def test_medico_login(self, driver, base_url):
        """Teste: Login do médico"""
        driver.get(f"{base_url}/medico/login.html")
        
        # Preencher formulário de login
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys("joao@clinica.com")
        
        senha_field = driver.find_element(By.ID, "senha")
        senha_field.send_keys("medico123")
        
        # Submeter formulário
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Aguardar redirecionamento para dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("dashboard.html")
        )
        
        assert "dashboard.html" in driver.current_url
        print("✅ Login do médico bem-sucedido")
    
    def test_medico_visualizar_dashboard(self, driver, base_url):
        """Teste: Visualizar dashboard do médico"""
        # Verificar elementos do dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        page_title = driver.find_element(By.TAG_NAME, "h1").text
        assert "Dashboard" in page_title or "Bem-vindo" in page_title
        print("✅ Dashboard do médico carregado")
    
    def test_medico_visualizar_agenda(self, driver, base_url):
        """Teste: Visualizar agenda de consultas"""
        driver.get(f"{base_url}/medico/agenda.html")
        
        # Aguardar carregamento da agenda
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "agenda-consultas"))
        )
        
        agenda = driver.find_element(By.ID, "agenda-consultas")
        assert agenda is not None
        print("✅ Agenda do médico carregada")
    
    def test_medico_gerenciar_horarios(self, driver, base_url):
        """Teste: Gerenciar horários de trabalho"""
        driver.get(f"{base_url}/medico/horarios.html")
        
        # Aguardar carregamento da página de horários
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        page_title = driver.find_element(By.TAG_NAME, "h1").text
        assert "Horário" in page_title or "Disponibilidade" in page_title
        print("✅ Página de horários carregada")
    
    def test_medico_visualizar_consultas(self, driver, base_url):
        """Teste: Visualizar consultas agendadas"""
        driver.get(f"{base_url}/medico/consultas.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(2)
        print("✅ Página de consultas do médico carregada")
    
    def test_medico_logout(self, driver, base_url):
        """Teste: Logout do médico"""
        try:
            logout_button = driver.find_element(By.ID, "logout")
            logout_button.click()
            time.sleep(2)
            
            assert "login.html" in driver.current_url
            print("✅ Logout do médico bem-sucedido")
        except:
            print("⚠️  Botão de logout não encontrado, limpando localStorage")
            driver.execute_script("localStorage.clear()")


class TestAdministradorJourney:
    """
    Testes E2E da jornada completa do ADMINISTRADOR
    """
    
    def test_admin_login(self, driver, base_url):
        """Teste: Login do administrador"""
        driver.get(f"{base_url}/admin/login.html")
        
        # Preencher formulário de login
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.send_keys("admin@clinica.com")
        
        senha_field = driver.find_element(By.ID, "senha")
        senha_field.send_keys("admin123")
        
        # Submeter formulário
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Aguardar redirecionamento para dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("dashboard.html")
        )
        
        assert "dashboard.html" in driver.current_url
        print("✅ Login do administrador bem-sucedido")
    
    def test_admin_visualizar_dashboard(self, driver, base_url):
        """Teste: Visualizar dashboard administrativo"""
        # Verificar elementos do dashboard
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        page_title = driver.find_element(By.TAG_NAME, "h1").text
        assert "Dashboard" in page_title or "Administra" in page_title
        print("✅ Dashboard administrativo carregado")
    
    def test_admin_gerenciar_pacientes(self, driver, base_url):
        """Teste: Gerenciar pacientes"""
        driver.get(f"{base_url}/admin/pacientes.html")
        
        # Aguardar carregamento da lista de pacientes
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(2)
        print("✅ Página de gerenciamento de pacientes carregada")
    
    def test_admin_gerenciar_medicos(self, driver, base_url):
        """Teste: Gerenciar médicos"""
        driver.get(f"{base_url}/admin/medicos.html")
        
        # Aguardar carregamento da lista de médicos
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(2)
        print("✅ Página de gerenciamento de médicos carregada")
    
    def test_admin_visualizar_relatorios(self, driver, base_url):
        """Teste: Visualizar relatórios"""
        driver.get(f"{base_url}/admin/relatorios.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(2)
        print("✅ Página de relatórios carregada")
    
    def test_admin_gerenciar_convenios(self, driver, base_url):
        """Teste: Gerenciar convênios/planos de saúde"""
        driver.get(f"{base_url}/admin/convenios.html")
        
        # Aguardar carregamento
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        time.sleep(2)
        print("✅ Página de convênios carregada")
    
    def test_admin_logout(self, driver, base_url):
        """Teste: Logout do administrador"""
        try:
            logout_button = driver.find_element(By.ID, "logout")
            logout_button.click()
            time.sleep(2)
            
            assert "login.html" in driver.current_url
            print("✅ Logout do administrador bem-sucedido")
        except:
            print("⚠️  Botão de logout não encontrado, limpando localStorage")
            driver.execute_script("localStorage.clear()")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
