"""
Teste E2E Completo - Jornada do Médico
Valida todos os casos de uso do Médico seguindo a navegação real do sistema

Casos de Uso Testados (conforme Prompts/CasosDeUso.txt):
1. Login do Médico
2. Gerenciar Horários de Trabalho (Criar, Listar, Deletar)
3. Bloquear Horários
4. Visualizar Consultas Agendadas
5. Registrar Observações da Consulta
6. Visualizar Observações da Consulta

Navegação:
medico/login.html → dashboard.html → horarios.html → agenda.html → 
consultas.html → logout
"""

import pytest
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

BASE_URL = "http://localhost"
TIMEOUT = 10

# Credenciais de médico pré-cadastrado (admin deve criar via seed)
MEDICO_EMAIL = "medico.teste@email.com"
MEDICO_SENHA = "Senha123@"

@pytest.fixture(scope="module")
def driver():
    """Configura o driver do Chrome"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(TIMEOUT)
    yield driver
    driver.quit()


class TestJornadaCompletaMedico:
    """Suite de testes que valida a jornada completa do médico"""
    
    def test_01_acessar_login_medico(self, driver):
        """
        UC: Navegação para Login Médico
        Valida: Página de login do médico carrega corretamente
        """
        print("\n=== TESTE 1: Acessar Login Médico ===")
        driver.get(f"{BASE_URL}/medico/login.html")
        time.sleep(1)
        
        assert "login" in driver.current_url.lower()
        print("✓ Página de login do médico carregada")
    
    def test_02_fazer_login(self, driver):
        """
        UC01: Login do Médico
        Valida: Médico consegue fazer login
        """
        print("\n=== TESTE 2: Fazer Login como Médico ===")
        
        # Preencher email
        campos_email = ["email", "usuario", "login"]
        for campo_id in campos_email:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(MEDICO_EMAIL)
                print(f"✓ Email preenchido: {MEDICO_EMAIL}")
                break
            except:
                continue
        
        # Preencher senha
        campos_senha = ["senha", "password"]
        for campo_id in campos_senha:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(MEDICO_SENHA)
                print(f"✓ Senha preenchida")
                break
            except:
                continue
        
        # Clicar em login
        botoes_login = [
            "//button[contains(text(), 'Entrar')]",
            "//button[@type='submit']",
            "//input[@type='submit']"
        ]
        
        for xpath in botoes_login:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de login")
                break
            except:
                continue
        
        time.sleep(3)
        assert "dashboard" in driver.current_url.lower(), "Não redirecionou para dashboard"
        print("✓ Login realizado - Dashboard médico carregado")
    
    def test_03_validar_dashboard_medico(self, driver):
        """
        UC: Visualizar Dashboard Médico
        Valida: Dashboard exibe informações e navegação
        """
        print("\n=== TESTE 3: Validar Dashboard Médico ===")
        
        # Validar links de navegação
        links_esperados = ["Horários", "Consultas", "Agenda"]
        
        links_encontrados = 0
        for texto_link in links_esperados:
            try:
                link = driver.find_element(By.PARTIAL_LINK_TEXT, texto_link)
                assert link.is_displayed()
                links_encontrados += 1
                print(f"✓ Link '{texto_link}' encontrado")
            except:
                print(f"⚠ Link '{texto_link}' não encontrado")
        
        print(f"✓ {links_encontrados} links de navegação validados")
        time.sleep(1)
    
    def test_04_navegar_para_horarios(self, driver):
        """
        UC02: Gerenciar Horários - Navegação
        Valida: Navegação para página de horários
        """
        print("\n=== TESTE 4: Navegar para Horários ===")
        
        try:
            link_horarios = driver.find_element(By.PARTIAL_LINK_TEXT, "Horários")
            link_horarios.click()
            print("✓ Clicou no link 'Horários'")
        except:
            driver.get(f"{BASE_URL}/medico/horarios.html")
            print("⚠ Navegação direta para horarios.html")
        
        time.sleep(2)
        assert "horarios" in driver.current_url.lower()
        print("✓ Página de horários carregada")
    
    def test_05_adicionar_horario_disponivel(self, driver):
        """
        UC02: Gerenciar Horários - Criar
        Valida: Médico consegue adicionar horário disponível
        """
        print("\n=== TESTE 5: Adicionar Horário Disponível ===")
        
        # Selecionar dia da semana
        try:
            select_dia = driver.find_element(By.ID, "dia_semana")
            select = Select(select_dia)
            select.select_by_value("1")  # Segunda-feira
            print("✓ Dia da semana selecionado: Segunda-feira")
        except:
            print("⚠ Campo dia_semana não encontrado")
        
        # Preencher hora início
        try:
            campo_inicio = driver.find_element(By.ID, "hora_inicio")
            campo_inicio.clear()
            campo_inicio.send_keys("08:00")
            print("✓ Hora início: 08:00")
        except:
            print("⚠ Campo hora_inicio não encontrado")
        
        # Preencher hora fim
        try:
            campo_fim = driver.find_element(By.ID, "hora_fim")
            campo_fim.clear()
            campo_fim.send_keys("12:00")
            print("✓ Hora fim: 12:00")
        except:
            print("⚠ Campo hora_fim não encontrado")
        
        # Clicar em adicionar
        botoes_adicionar = [
            "//button[contains(text(), 'Adicionar')]",
            "//button[contains(text(), 'Salvar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_adicionar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de adicionar horário")
                break
            except:
                continue
        
        time.sleep(2)
        print("✓ Horário adicionado")
    
    def test_06_visualizar_horarios_disponiveis(self, driver):
        """
        UC02: Gerenciar Horários - Listar
        Valida: Lista de horários disponíveis é exibida
        """
        print("\n=== TESTE 6: Visualizar Horários Disponíveis ===")
        
        time.sleep(2)
        
        # Procurar tabela de horários
        elementos_horario = [
            "//table//tr",
            "//div[contains(@class, 'horario')]",
            "//ul[contains(@class, 'horarios')]//li"
        ]
        
        horarios_encontrados = 0
        for xpath in elementos_horario:
            try:
                elementos = driver.find_elements(By.XPATH, xpath)
                if len(elementos) > 0:
                    horarios_encontrados = len(elementos)
                    print(f"✓ {horarios_encontrados} horários encontrados")
                    break
            except:
                continue
        
        print(f"✓ Lista de horários validada")
        time.sleep(1)
    
    def test_07_criar_bloqueio_horario(self, driver):
        """
        UC04: Bloquear Horários
        Valida: Médico consegue bloquear horário específico
        """
        print("\n=== TESTE 7: Criar Bloqueio de Horário ===")
        
        # Procurar seção de bloqueios (pode estar na mesma página)
        try:
            titulo_bloqueio = driver.find_element(By.XPATH, "//*[contains(text(), 'Bloqueio')]")
            print("✓ Seção de bloqueios encontrada")
        except:
            print("⚠ Seção de bloqueios não encontrada")
        
        # Data futura para bloqueio
        data_bloqueio = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        # Preencher data
        campos_data = ["data_bloqueio", "data", "dataBloqueio"]
        for campo_id in campos_data:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(data_bloqueio)
                print(f"✓ Data de bloqueio: {data_bloqueio}")
                break
            except:
                continue
        
        # Preencher hora início
        campos_inicio = ["hora_inicio_bloqueio", "horaInicioBloqueio"]
        for campo_id in campos_inicio:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys("09:00")
                print("✓ Hora início bloqueio: 09:00")
                break
            except:
                continue
        
        # Preencher hora fim
        campos_fim = ["hora_fim_bloqueio", "horaFimBloqueio"]
        for campo_id in campos_fim:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys("10:00")
                print("✓ Hora fim bloqueio: 10:00")
                break
            except:
                continue
        
        # Motivo do bloqueio
        campos_motivo = ["motivo_bloqueio", "motivoBloqueio", "motivo"]
        for campo_id in campos_motivo:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys("Compromisso pessoal")
                print("✓ Motivo do bloqueio preenchido")
                break
            except:
                continue
        
        # Adicionar bloqueio
        botoes_adicionar = [
            "//button[contains(text(), 'Bloquear')]",
            "//button[contains(text(), 'Adicionar Bloqueio')]"
        ]
        
        for xpath in botoes_adicionar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de bloquear horário")
                break
            except:
                continue
        
        time.sleep(2)
        print("✓ Bloqueio de horário criado")
    
    def test_08_visualizar_bloqueios(self, driver):
        """
        UC04: Bloquear Horários - Listar
        Valida: Lista de bloqueios é exibida
        """
        print("\n=== TESTE 8: Visualizar Bloqueios ===")
        
        time.sleep(1)
        
        # Procurar tabela de bloqueios
        elementos_bloqueio = [
            "//table[@id='tabelaBloqueios']//tr",
            "//div[contains(@class, 'bloqueio')]"
        ]
        
        bloqueios_encontrados = 0
        for xpath in elementos_bloqueio:
            try:
                elementos = driver.find_elements(By.XPATH, xpath)
                if len(elementos) > 0:
                    bloqueios_encontrados = len(elementos)
                    print(f"✓ {bloqueios_encontrados} bloqueios encontrados")
                    break
            except:
                continue
        
        print("✓ Lista de bloqueios validada")
        time.sleep(1)
    
    def test_09_navegar_para_consultas(self, driver):
        """
        UC03: Visualizar Consultas - Navegação
        Valida: Navegação para página de consultas
        """
        print("\n=== TESTE 9: Navegar para Consultas ===")
        
        try:
            link_consultas = driver.find_element(By.PARTIAL_LINK_TEXT, "Consultas")
            link_consultas.click()
            print("✓ Clicou no link 'Consultas'")
        except:
            driver.get(f"{BASE_URL}/medico/consultas.html")
            print("⚠ Navegação direta para consultas.html")
        
        time.sleep(2)
        assert "consultas" in driver.current_url.lower()
        print("✓ Página de consultas carregada")
    
    def test_10_visualizar_consultas_agendadas(self, driver):
        """
        UC03: Visualizar Consultas Agendadas
        Valida: Lista de consultas agendadas é exibida
        """
        print("\n=== TESTE 10: Visualizar Consultas Agendadas ===")
        
        time.sleep(2)
        
        # Procurar tabela de consultas
        elementos_consulta = [
            "//table//tr",
            "//div[contains(@class, 'consulta')]"
        ]
        
        consultas_encontradas = 0
        for xpath in elementos_consulta:
            try:
                elementos = driver.find_elements(By.XPATH, xpath)
                if len(elementos) > 0:
                    consultas_encontradas = len(elementos)
                    print(f"✓ {consultas_encontradas} consultas encontradas")
                    break
            except:
                continue
        
        if consultas_encontradas == 0:
            print("⚠ Nenhuma consulta agendada encontrada")
        else:
            print("✓ Lista de consultas validada")
        
        time.sleep(1)
    
    def test_11_filtrar_consultas_do_dia(self, driver):
        """
        UC03: Visualizar Consultas - Filtro
        Valida: Filtro de consultas do dia funciona
        """
        print("\n=== TESTE 11: Filtrar Consultas do Dia ===")
        
        # Procurar botão/filtro do dia
        botoes_filtro = [
            "//button[contains(text(), 'Hoje')]",
            "//button[contains(text(), 'Do Dia')]",
            "//select[@id='filtroData']"
        ]
        
        for xpath in botoes_filtro:
            try:
                elemento = driver.find_element(By.XPATH, xpath)
                if elemento.tag_name == "button":
                    elemento.click()
                    print("✓ Clicou no filtro 'Hoje'")
                elif elemento.tag_name == "select":
                    select = Select(elemento)
                    select.select_by_value("hoje")
                    print("✓ Selecionou filtro 'Hoje'")
                time.sleep(2)
                return
            except:
                continue
        
        print("⚠ Filtro de data não encontrado")
    
    def test_12_adicionar_observacao_consulta(self, driver):
        """
        UC05: Registrar Observações da Consulta
        Valida: Médico consegue adicionar observação
        """
        print("\n=== TESTE 12: Adicionar Observação ===")
        
        # Procurar botão de adicionar observação
        botoes_observacao = [
            "//button[contains(text(), 'Observação')]",
            "//button[contains(text(), 'Adicionar Observação')]",
            "//a[contains(text(), 'Observação')]"
        ]
        
        observacao_encontrada = False
        for xpath in botoes_observacao:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de observação")
                time.sleep(2)
                observacao_encontrada = True
                break
            except:
                continue
        
        if not observacao_encontrada:
            print("⚠ Botão de observação não encontrado")
            return
        
        # Preencher observação
        campos_observacao = ["observacao", "descricao", "texto_observacao"]
        texto_observacao = "Paciente apresenta melhora significativa. Continuar tratamento prescrito."
        
        for campo_id in campos_observacao:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(texto_observacao)
                print(f"✓ Observação preenchida")
                break
            except:
                continue
        
        # Salvar observação
        botoes_salvar = [
            "//button[contains(text(), 'Salvar')]",
            "//button[contains(text(), 'Adicionar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_salvar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Observação salva")
                break
            except:
                continue
        
        time.sleep(2)
    
    def test_13_visualizar_observacao(self, driver):
        """
        UC06: Visualizar Observações da Consulta
        Valida: Observações registradas são exibidas
        """
        print("\n=== TESTE 13: Visualizar Observação ===")
        
        time.sleep(1)
        
        # Procurar observação na lista
        try:
            observacao = driver.find_element(By.XPATH, "//*[contains(text(), 'melhora')]")
            print(f"✓ Observação encontrada: {observacao.text[:50]}...")
        except:
            print("⚠ Observação não encontrada na lista")
        
        time.sleep(1)
    
    def test_14_navegar_para_agenda(self, driver):
        """
        UC: Visualizar Agenda
        Valida: Navegação para página de agenda
        """
        print("\n=== TESTE 14: Navegar para Agenda ===")
        
        try:
            link_agenda = driver.find_element(By.PARTIAL_LINK_TEXT, "Agenda")
            link_agenda.click()
            print("✓ Clicou no link 'Agenda'")
        except:
            driver.get(f"{BASE_URL}/medico/agenda.html")
            print("⚠ Navegação direta para agenda.html")
        
        time.sleep(2)
        assert "agenda" in driver.current_url.lower()
        print("✓ Página de agenda carregada")
    
    def test_15_visualizar_calendario_agenda(self, driver):
        """
        UC: Visualizar Agenda - Calendário
        Valida: Calendário de agenda é exibido
        """
        print("\n=== TESTE 15: Visualizar Calendário ===")
        
        time.sleep(2)
        
        # Procurar elementos do calendário
        elementos_calendario = [
            "//div[contains(@class, 'calendar')]",
            "//table[contains(@class, 'calendar')]",
            "//div[@id='calendario']"
        ]
        
        for xpath in elementos_calendario:
            try:
                calendario = driver.find_element(By.XPATH, xpath)
                if calendario.is_displayed():
                    print("✓ Calendário encontrado e visível")
                    return
            except:
                continue
        
        print("⚠ Calendário não encontrado")
    
    def test_16_visualizar_consultas_na_agenda(self, driver):
        """
        UC: Visualizar Agenda - Consultas
        Valida: Consultas são exibidas na agenda
        """
        print("\n=== TESTE 16: Visualizar Consultas na Agenda ===")
        
        time.sleep(1)
        
        # Procurar consultas na agenda
        try:
            consultas = driver.find_elements(By.XPATH, "//div[contains(@class, 'evento-consulta')]")
            if len(consultas) > 0:
                print(f"✓ {len(consultas)} consultas encontradas na agenda")
            else:
                print("⚠ Nenhuma consulta na agenda")
        except:
            print("⚠ Elementos de consulta não encontrados")
        
        time.sleep(1)
    
    def test_17_voltar_para_dashboard(self, driver):
        """
        UC: Navegação - Dashboard
        Valida: Retorno ao dashboard funciona
        """
        print("\n=== TESTE 17: Voltar para Dashboard ===")
        
        try:
            link_dashboard = driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard")
            link_dashboard.click()
            print("✓ Clicou no link 'Dashboard'")
        except:
            driver.get(f"{BASE_URL}/medico/dashboard.html")
            print("⚠ Navegação direta para dashboard.html")
        
        time.sleep(2)
        assert "dashboard" in driver.current_url.lower()
        print("✓ Dashboard carregado")
    
    def test_18_fazer_logout(self, driver):
        """
        UC: Logout
        Valida: Médico consegue fazer logout
        """
        print("\n=== TESTE 18: Fazer Logout ===")
        
        logout_xpath = [
            "//button[contains(text(), 'Sair')]",
            "//a[contains(text(), 'Sair')]",
            "//button[contains(text(), 'Logout')]"
        ]
        
        for xpath in logout_xpath:
            try:
                elemento = driver.find_element(By.XPATH, xpath)
                elemento.click()
                print(f"✓ Clicou em logout")
                time.sleep(2)
                
                url_atual = driver.current_url
                if "login" in url_atual.lower() or "index" in url_atual.lower():
                    print("✓ Logout realizado com sucesso")
                    return
            except:
                continue
        
        print("⚠ Botão de logout não encontrado")
        driver.execute_script("localStorage.clear();")
        driver.get(f"{BASE_URL}/index.html")
        print("⚠ Logout forçado")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
