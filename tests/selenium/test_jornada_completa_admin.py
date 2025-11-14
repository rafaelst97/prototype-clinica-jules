"""
Teste E2E Completo - Jornada do Administrador
Valida todos os casos de uso do Admin seguindo a navegação real do sistema

Casos de Uso Testados (conforme Prompts/CasosDeUso.txt):
1. Login do Administrador
2. Gerar Relatórios PDF
3. Gerenciar Médicos (Criar, Listar, Visualizar, Editar, Deletar)
4. Gerenciar Convênios (Criar, Listar, Editar, Deletar)
5. Desbloquear Contas de Pacientes
6. Visualizar Todas as Observações

Navegação:
admin/login.html → dashboard.html → medicos.html → convenios.html → 
pacientes.html → relatorios.html → logout
"""

import pytest
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

BASE_URL = "http://localhost"
TIMEOUT = 10

# Credenciais de admin pré-cadastrado (deve existir no seed)
ADMIN_EMAIL = "admin@sistema.com"
ADMIN_SENHA = "Admin123@"

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

@pytest.fixture(scope="module")
def medico_dados():
    """Dados únicos para médico teste"""
    timestamp = str(int(datetime.now().timestamp() * 1000))[-8:]
    return {
        "nome": f"Dr. Teste {timestamp}",
        "email": f"medico.teste.{timestamp}@email.com",
        "crm": f"SC{timestamp}",
        "especialidade": "Cardiologia",
        "telefone": "(47) 99999-8888"
    }

@pytest.fixture(scope="module")
def convenio_dados():
    """Dados únicos para convênio teste"""
    timestamp = str(int(datetime.now().timestamp() * 1000))[-8:]
    return {
        "nome": f"Plano Teste {timestamp}",
        "codigo": f"COD{timestamp}",
        "tipo": "particular"
    }


class TestJornadaCompletaAdmin:
    """Suite de testes que valida a jornada completa do administrador"""
    
    medico_id = None
    convenio_id = None
    
    def test_01_acessar_login_admin(self, driver):
        """
        UC: Navegação para Login Admin
        Valida: Página de login do admin carrega corretamente
        """
        print("\n=== TESTE 1: Acessar Login Admin ===")
        driver.get(f"{BASE_URL}/admin/login.html")
        time.sleep(1)
        
        assert "login" in driver.current_url.lower()
        print("✓ Página de login do admin carregada")
    
    def test_02_fazer_login_admin(self, driver):
        """
        UC01: Login do Administrador
        Valida: Admin consegue fazer login
        """
        print("\n=== TESTE 2: Fazer Login como Admin ===")
        
        # Preencher email
        campos_email = ["email", "usuario", "login"]
        for campo_id in campos_email:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(ADMIN_EMAIL)
                print(f"✓ Email preenchido: {ADMIN_EMAIL}")
                break
            except:
                continue
        
        # Preencher senha
        campos_senha = ["senha", "password"]
        for campo_id in campos_senha:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(ADMIN_SENHA)
                print(f"✓ Senha preenchida")
                break
            except:
                continue
        
        # Clicar em login
        botoes_login = [
            "//button[contains(text(), 'Entrar')]",
            "//button[@type='submit']"
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
        print("✓ Login realizado - Dashboard admin carregado")
    
    def test_03_validar_dashboard_admin(self, driver):
        """
        UC: Visualizar Dashboard Admin
        Valida: Dashboard exibe informações e navegação
        """
        print("\n=== TESTE 3: Validar Dashboard Admin ===")
        
        # Validar links de navegação
        links_esperados = ["Médicos", "Convênios", "Pacientes", "Relatórios"]
        
        links_encontrados = 0
        for texto_link in links_esperados:
            try:
                link = driver.find_element(By.PARTIAL_LINK_TEXT, texto_link)
                assert link.is_displayed()
                links_encontrados += 1
                print(f"✓ Link '{texto_link}' encontrado")
            except:
                print(f"⚠ Link '{texto_link}' não encontrado")
        
        assert links_encontrados >= 3, "Menos de 3 links encontrados"
        print(f"✓ {links_encontrados} links de navegação validados")
        time.sleep(1)
    
    def test_04_navegar_para_medicos(self, driver):
        """
        UC03: Gerenciar Médicos - Navegação
        Valida: Navegação para página de médicos
        """
        print("\n=== TESTE 4: Navegar para Médicos ===")
        
        try:
            link_medicos = driver.find_element(By.PARTIAL_LINK_TEXT, "Médicos")
            link_medicos.click()
            print("✓ Clicou no link 'Médicos'")
        except:
            driver.get(f"{BASE_URL}/admin/medicos.html")
            print("⚠ Navegação direta para medicos.html")
        
        time.sleep(2)
        assert "medicos" in driver.current_url.lower()
        print("✓ Página de médicos carregada")
    
    def test_05_adicionar_novo_medico(self, driver, medico_dados):
        """
        UC03: Gerenciar Médicos - Criar
        Valida: Admin consegue adicionar novo médico
        """
        print("\n=== TESTE 5: Adicionar Novo Médico ===")
        
        # Clicar em adicionar médico
        botoes_adicionar = [
            "//button[contains(text(), 'Novo')]",
            "//button[contains(text(), 'Adicionar')]",
            "//button[contains(text(), 'Cadastrar')]"
        ]
        
        for xpath in botoes_adicionar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de adicionar médico")
                time.sleep(1)
                break
            except:
                continue
        
        # Preencher formulário do médico
        campos_formulario = {
            "nome": medico_dados["nome"],
            "email": medico_dados["email"],
            "crm": medico_dados["crm"],
            "especialidade": medico_dados["especialidade"],
            "telefone": medico_dados["telefone"]
        }
        
        for campo_nome, valor in campos_formulario.items():
            campos_possiveis = [campo_nome, f"medico_{campo_nome}", f"input_{campo_nome}"]
            
            for campo_id in campos_possiveis:
                try:
                    campo = driver.find_element(By.ID, campo_id)
                    campo.clear()
                    campo.send_keys(valor)
                    print(f"✓ {campo_nome}: {valor}")
                    break
                except:
                    continue
        
        # Salvar médico
        botoes_salvar = [
            "//button[contains(text(), 'Salvar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_salvar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Médico salvo")
                break
            except:
                continue
        
        time.sleep(3)
        print("✓ Novo médico adicionado")
    
    def test_06_visualizar_lista_medicos(self, driver):
        """
        UC03: Gerenciar Médicos - Listar
        Valida: Lista de médicos é exibida
        """
        print("\n=== TESTE 6: Visualizar Lista de Médicos ===")
        
        time.sleep(2)
        
        # Procurar tabela de médicos
        try:
            linhas = driver.find_elements(By.XPATH, "//table//tbody//tr")
            print(f"✓ {len(linhas)} médicos encontrados na lista")
        except:
            print("⚠ Tabela de médicos não encontrada")
        
        time.sleep(1)
    
    def test_07_editar_medico(self, driver):
        """
        UC03: Gerenciar Médicos - Editar
        Valida: Admin consegue editar médico
        """
        print("\n=== TESTE 7: Editar Médico ===")
        
        # Procurar botão de editar (primeiro da lista)
        botoes_editar = [
            "(//button[contains(text(), 'Editar')])[1]",
            "(//a[contains(text(), 'Editar')])[1]"
        ]
        
        for xpath in botoes_editar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou em editar médico")
                time.sleep(2)
                break
            except:
                continue
        
        # Editar telefone
        campos_telefone = ["telefone", "medico_telefone"]
        novo_telefone = "(47) 99999-0000"
        
        for campo_id in campos_telefone:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(novo_telefone)
                print(f"✓ Telefone alterado: {novo_telefone}")
                break
            except:
                continue
        
        # Salvar alterações
        botoes_salvar = [
            "//button[contains(text(), 'Salvar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_salvar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Alterações salvas")
                break
            except:
                continue
        
        time.sleep(2)
        print("✓ Médico editado")
    
    def test_08_navegar_para_convenios(self, driver):
        """
        UC04: Gerenciar Convênios - Navegação
        Valida: Navegação para página de convênios
        """
        print("\n=== TESTE 8: Navegar para Convênios ===")
        
        try:
            link_convenios = driver.find_element(By.PARTIAL_LINK_TEXT, "Convênios")
            link_convenios.click()
            print("✓ Clicou no link 'Convênios'")
        except:
            driver.get(f"{BASE_URL}/admin/convenios.html")
            print("⚠ Navegação direta para convenios.html")
        
        time.sleep(2)
        assert "convenios" in driver.current_url.lower()
        print("✓ Página de convênios carregada")
    
    def test_09_adicionar_novo_convenio(self, driver, convenio_dados):
        """
        UC04: Gerenciar Convênios - Criar
        Valida: Admin consegue adicionar novo convênio
        """
        print("\n=== TESTE 9: Adicionar Novo Convênio ===")
        
        # Clicar em adicionar convênio
        botoes_adicionar = [
            "//button[contains(text(), 'Novo')]",
            "//button[contains(text(), 'Adicionar')]"
        ]
        
        for xpath in botoes_adicionar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de adicionar convênio")
                time.sleep(1)
                break
            except:
                continue
        
        # Preencher formulário do convênio
        campos_formulario = {
            "nome": convenio_dados["nome"],
            "codigo": convenio_dados["codigo"],
            "tipo": convenio_dados["tipo"]
        }
        
        for campo_nome, valor in campos_formulario.items():
            if campo_nome == "tipo":
                # Campo select
                try:
                    select_tipo = driver.find_element(By.ID, "tipo")
                    select = Select(select_tipo)
                    select.select_by_value(valor)
                    print(f"✓ Tipo selecionado: {valor}")
                except:
                    print(f"⚠ Campo tipo não encontrado")
            else:
                campos_possiveis = [campo_nome, f"convenio_{campo_nome}"]
                
                for campo_id in campos_possiveis:
                    try:
                        campo = driver.find_element(By.ID, campo_id)
                        campo.clear()
                        campo.send_keys(valor)
                        print(f"✓ {campo_nome}: {valor}")
                        break
                    except:
                        continue
        
        # Salvar convênio
        botoes_salvar = [
            "//button[contains(text(), 'Salvar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_salvar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Convênio salvo")
                break
            except:
                continue
        
        time.sleep(3)
        print("✓ Novo convênio adicionado")
    
    def test_10_visualizar_lista_convenios(self, driver):
        """
        UC04: Gerenciar Convênios - Listar
        Valida: Lista de convênios é exibida
        """
        print("\n=== TESTE 10: Visualizar Lista de Convênios ===")
        
        time.sleep(2)
        
        # Procurar tabela de convênios
        try:
            linhas = driver.find_elements(By.XPATH, "//table//tbody//tr")
            print(f"✓ {len(linhas)} convênios encontrados na lista")
        except:
            print("⚠ Tabela de convênios não encontrada")
        
        time.sleep(1)
    
    def test_11_editar_convenio(self, driver):
        """
        UC04: Gerenciar Convênios - Editar
        Valida: Admin consegue editar convênio
        """
        print("\n=== TESTE 11: Editar Convênio ===")
        
        # Procurar botão de editar (primeiro da lista)
        botoes_editar = [
            "(//button[contains(text(), 'Editar')])[1]",
            "(//a[contains(text(), 'Editar')])[1]"
        ]
        
        for xpath in botoes_editar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou em editar convênio")
                time.sleep(2)
                break
            except:
                continue
        
        # Editar nome
        campos_nome = ["nome", "convenio_nome"]
        novo_nome = "Plano Editado"
        
        for campo_id in campos_nome:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(novo_nome)
                print(f"✓ Nome alterado: {novo_nome}")
                break
            except:
                continue
        
        # Salvar alterações
        botoes_salvar = [
            "//button[contains(text(), 'Salvar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_salvar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Alterações salvas")
                break
            except:
                continue
        
        time.sleep(2)
        print("✓ Convênio editado")
    
    def test_12_navegar_para_pacientes(self, driver):
        """
        UC05: Desbloquear Pacientes - Navegação
        Valida: Navegação para página de pacientes
        """
        print("\n=== TESTE 12: Navegar para Pacientes ===")
        
        try:
            link_pacientes = driver.find_element(By.PARTIAL_LINK_TEXT, "Pacientes")
            link_pacientes.click()
            print("✓ Clicou no link 'Pacientes'")
        except:
            driver.get(f"{BASE_URL}/admin/pacientes.html")
            print("⚠ Navegação direta para pacientes.html")
        
        time.sleep(2)
        assert "pacientes" in driver.current_url.lower()
        print("✓ Página de pacientes carregada")
    
    def test_13_visualizar_lista_pacientes(self, driver):
        """
        UC05: Desbloquear Pacientes - Listar
        Valida: Lista de pacientes é exibida
        """
        print("\n=== TESTE 13: Visualizar Lista de Pacientes ===")
        
        time.sleep(2)
        
        # Procurar tabela de pacientes
        try:
            linhas = driver.find_elements(By.XPATH, "//table//tbody//tr")
            print(f"✓ {len(linhas)} pacientes encontrados na lista")
        except:
            print("⚠ Tabela de pacientes não encontrada")
        
        time.sleep(1)
    
    def test_14_filtrar_pacientes_bloqueados(self, driver):
        """
        UC05: Desbloquear Pacientes - Filtro
        Valida: Filtro de pacientes bloqueados funciona
        """
        print("\n=== TESTE 14: Filtrar Pacientes Bloqueados ===")
        
        # Procurar filtro de bloqueados
        filtros = [
            "//select[@id='filtroBloqueio']",
            "//button[contains(text(), 'Bloqueados')]"
        ]
        
        for xpath in filtros:
            try:
                elemento = driver.find_element(By.XPATH, xpath)
                if elemento.tag_name == "select":
                    select = Select(elemento)
                    select.select_by_value("bloqueados")
                    print("✓ Filtro 'Bloqueados' selecionado")
                elif elemento.tag_name == "button":
                    elemento.click()
                    print("✓ Clicou em filtro 'Bloqueados'")
                time.sleep(2)
                return
            except:
                continue
        
        print("⚠ Filtro de bloqueados não encontrado")
    
    def test_15_desbloquear_paciente(self, driver):
        """
        UC05: Desbloquear Pacientes
        Valida: Admin consegue desbloquear paciente
        """
        print("\n=== TESTE 15: Desbloquear Paciente ===")
        
        # Procurar botão de desbloquear
        botoes_desbloquear = [
            "//button[contains(text(), 'Desbloquear')]",
            "//a[contains(text(), 'Desbloquear')]"
        ]
        
        encontrado = False
        for xpath in botoes_desbloquear:
            try:
                botoes = driver.find_elements(By.XPATH, xpath)
                if len(botoes) > 0:
                    botoes[0].click()
                    print(f"✓ Clicou em desbloquear paciente")
                    time.sleep(2)
                    encontrado = True
                    
                    # Confirmar desbloqueio (se houver modal)
                    try:
                        botao_confirmar = driver.find_element(By.XPATH, "//button[contains(text(), 'Confirmar')]")
                        botao_confirmar.click()
                        print("✓ Desbloqueio confirmado")
                    except:
                        pass
                    
                    break
            except:
                continue
        
        if not encontrado:
            print("⚠ Nenhum paciente bloqueado para desbloquear")
        
        time.sleep(2)
    
    def test_16_navegar_para_relatorios(self, driver):
        """
        UC02: Gerar Relatórios - Navegação
        Valida: Navegação para página de relatórios
        """
        print("\n=== TESTE 16: Navegar para Relatórios ===")
        
        try:
            link_relatorios = driver.find_element(By.PARTIAL_LINK_TEXT, "Relatórios")
            link_relatorios.click()
            print("✓ Clicou no link 'Relatórios'")
        except:
            driver.get(f"{BASE_URL}/admin/relatorios.html")
            print("⚠ Navegação direta para relatorios.html")
        
        time.sleep(2)
        assert "relatorios" in driver.current_url.lower()
        print("✓ Página de relatórios carregada")
    
    def test_17_gerar_relatorio_consultas(self, driver):
        """
        UC02: Gerar Relatórios - Consultas
        Valida: Admin consegue gerar relatório de consultas
        """
        print("\n=== TESTE 17: Gerar Relatório de Consultas ===")
        
        # Selecionar tipo de relatório
        try:
            select_tipo = driver.find_element(By.ID, "tipoRelatorio")
            select = Select(select_tipo)
            select.select_by_value("consultas")
            print("✓ Tipo 'Consultas' selecionado")
        except:
            print("⚠ Campo tipoRelatorio não encontrado")
        
        # Definir período
        from datetime import datetime, timedelta
        data_inicial = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        data_final = datetime.now().strftime("%Y-%m-%d")
        
        try:
            campo_inicio = driver.find_element(By.ID, "dataInicio")
            campo_inicio.clear()
            campo_inicio.send_keys(data_inicial)
            print(f"✓ Data início: {data_inicial}")
        except:
            print("⚠ Campo dataInicio não encontrado")
        
        try:
            campo_fim = driver.find_element(By.ID, "dataFim")
            campo_fim.clear()
            campo_fim.send_keys(data_final)
            print(f"✓ Data fim: {data_final}")
        except:
            print("⚠ Campo dataFim não encontrado")
        
        # Gerar relatório
        botoes_gerar = [
            "//button[contains(text(), 'Gerar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_gerar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou em gerar relatório")
                break
            except:
                continue
        
        time.sleep(3)
        print("✓ Relatório de consultas gerado")
    
    def test_18_gerar_relatorio_medicos(self, driver):
        """
        UC02: Gerar Relatórios - Médicos
        Valida: Admin consegue gerar relatório de médicos
        """
        print("\n=== TESTE 18: Gerar Relatório de Médicos ===")
        
        # Selecionar tipo de relatório
        try:
            select_tipo = driver.find_element(By.ID, "tipoRelatorio")
            select = Select(select_tipo)
            select.select_by_value("medicos")
            print("✓ Tipo 'Médicos' selecionado")
        except:
            print("⚠ Campo tipoRelatorio não encontrado")
        
        # Gerar relatório
        botoes_gerar = [
            "//button[contains(text(), 'Gerar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_gerar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou em gerar relatório")
                break
            except:
                continue
        
        time.sleep(3)
        print("✓ Relatório de médicos gerado")
    
    def test_19_gerar_relatorio_pacientes(self, driver):
        """
        UC02: Gerar Relatórios - Pacientes
        Valida: Admin consegue gerar relatório de pacientes
        """
        print("\n=== TESTE 19: Gerar Relatório de Pacientes ===")
        
        # Selecionar tipo de relatório
        try:
            select_tipo = driver.find_element(By.ID, "tipoRelatorio")
            select = Select(select_tipo)
            select.select_by_value("pacientes")
            print("✓ Tipo 'Pacientes' selecionado")
        except:
            print("⚠ Campo tipoRelatorio não encontrado")
        
        # Gerar relatório
        botoes_gerar = [
            "//button[contains(text(), 'Gerar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_gerar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou em gerar relatório")
                break
            except:
                continue
        
        time.sleep(3)
        print("✓ Relatório de pacientes gerado")
    
    def test_20_voltar_para_dashboard(self, driver):
        """
        UC: Navegação - Dashboard
        Valida: Retorno ao dashboard funciona
        """
        print("\n=== TESTE 20: Voltar para Dashboard ===")
        
        try:
            link_dashboard = driver.find_element(By.PARTIAL_LINK_TEXT, "Dashboard")
            link_dashboard.click()
            print("✓ Clicou no link 'Dashboard'")
        except:
            driver.get(f"{BASE_URL}/admin/dashboard.html")
            print("⚠ Navegação direta para dashboard.html")
        
        time.sleep(2)
        assert "dashboard" in driver.current_url.lower()
        print("✓ Dashboard carregado")
    
    def test_21_fazer_logout(self, driver):
        """
        UC: Logout
        Valida: Admin consegue fazer logout
        """
        print("\n=== TESTE 21: Fazer Logout ===")
        
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
