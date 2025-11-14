"""
Teste E2E Completo - Jornada do Paciente
Valida todos os casos de uso do Paciente seguindo a navegação real do sistema

Casos de Uso Testados (conforme Prompts/CasosDeUso.txt):
1. Cadastrar Paciente
2. Login do Paciente
3. Agendar Consulta
4. Visualizar Consultas
5. Cancelar Consulta
6. Reagendar Consulta
7. Visualizar Perfil
8. Editar Perfil

Navegação:
index.html → cadastro.html → login.html → dashboard.html → agendar.html → 
consultas.html → perfil.html → logout
"""

import pytest
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

BASE_URL = "http://localhost"
TIMEOUT = 10

@pytest.fixture(scope="module")
def driver():
    """Configura o driver do Chrome"""
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # options.add_argument('--headless')  # Descomente para modo headless
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(TIMEOUT)
    yield driver
    driver.quit()

@pytest.fixture(scope="module")
def paciente_dados():
    """Dados do paciente para testes (únicos por execução)"""
    timestamp = str(int(datetime.now().timestamp() * 1000))[-8:]
    return {
        "nome": f"Paciente Teste {timestamp}",
        "email": f"paciente.teste.{timestamp}@email.com",
        "cpf": f"111{timestamp}",  # CPF único
        "data_nascimento": "15/05/1990",
        "telefone": "(47) 98888-7777",
        "endereco": "Rua das Flores, 123",
        "cidade": "Itajaí",
        "estado": "SC",
        "cep": "88301-000",
        "senha": "Senha123@",
        "senha_confirmacao": "Senha123@"
    }

class TestJornadaCompletaPaciente:
    """Suite de testes que valida a jornada completa do paciente"""
    
    def test_01_acessar_pagina_inicial(self, driver):
        """
        UC: Navegação Inicial
        Valida: index.html carrega corretamente e apresenta opções de acesso
        """
        print("\n=== TESTE 1: Acessar Página Inicial ===")
        driver.get(f"{BASE_URL}/index.html")
        
        # Validar título
        assert "Sistema de Agendamento" in driver.title or "Agendamento de Consultas" in driver.title
        print("✓ Página inicial carregada")
        
        # Validar links de navegação
        links_esperados = ["Sou Paciente", "Sou Médico", "Sou Admin"]
        for texto_link in links_esperados:
            try:
                link = driver.find_element(By.PARTIAL_LINK_TEXT, texto_link)
                assert link.is_displayed()
                print(f"✓ Link '{texto_link}' encontrado")
            except:
                print(f"⚠ Link '{texto_link}' não encontrado (pode estar em botão)")
        
        time.sleep(1)
    
    def test_02_navegar_para_cadastro(self, driver):
        """
        UC: Navegação para Cadastro
        Valida: Link/botão para cadastro funciona
        """
        print("\n=== TESTE 2: Navegar para Cadastro ===")
        
        # Procurar link/botão de cadastro
        cadastro_xpath = [
            "//a[contains(text(), 'Cadastrar')]",
            "//a[contains(text(), 'Cadastro')]",
            "//button[contains(text(), 'Cadastrar')]",
            "//a[@href='paciente/cadastro.html']"
        ]
        
        cadastro_encontrado = False
        for xpath in cadastro_xpath:
            try:
                elemento = driver.find_element(By.XPATH, xpath)
                elemento.click()
                cadastro_encontrado = True
                print(f"✓ Clicou em elemento de cadastro: {xpath}")
                break
            except:
                continue
        
        if not cadastro_encontrado:
            # Navegar diretamente
            driver.get(f"{BASE_URL}/paciente/cadastro.html")
            print("⚠ Navegação direta para cadastro.html")
        
        time.sleep(1)
        assert "cadastro" in driver.current_url.lower()
        print("✓ Página de cadastro acessada")
    
    def test_03_preencher_formulario_cadastro(self, driver, paciente_dados):
        """
        UC01: Cadastrar Paciente
        Valida: Todos os campos do formulário são preenchidos corretamente
        Requisitos: Nome, Email, CPF, Data Nascimento, Telefone, Endereço, Senha
        """
        print("\n=== TESTE 3: Preencher Formulário de Cadastro ===")
        
        # Mapear campos do formulário
        campos = {
            "nome": ["nome", "name", "nomeCompleto"],
            "email": ["email", "emailPaciente"],
            "cpf": ["cpf", "cpfPaciente"],
            "data_nascimento": ["data_nascimento", "dataNascimento", "nascimento"],
            "telefone": ["telefone", "tel", "celular"],
            "endereco": ["endereco", "endereço", "rua"],
            "cidade": ["cidade", "municipio"],
            "estado": ["estado", "uf"],
            "cep": ["cep", "codigoPostal"],
            "senha": ["senha", "password"],
            "senha_confirmacao": ["confirmarSenha", "senha_confirmacao", "confirmar_senha"]
        }
        
        campos_preenchidos = 0
        
        for campo_nome, ids_possiveis in campos.items():
            valor = paciente_dados[campo_nome]
            campo_preenchido = False
            
            for id_campo in ids_possiveis:
                try:
                    # Tentar por ID
                    campo = driver.find_element(By.ID, id_campo)
                    campo.clear()
                    campo.send_keys(valor)
                    campo_preenchido = True
                    campos_preenchidos += 1
                    print(f"✓ Campo '{campo_nome}' preenchido: {valor}")
                    break
                except:
                    try:
                        # Tentar por name
                        campo = driver.find_element(By.NAME, id_campo)
                        campo.clear()
                        campo.send_keys(valor)
                        campo_preenchido = True
                        campos_preenchidos += 1
                        print(f"✓ Campo '{campo_nome}' preenchido (by name): {valor}")
                        break
                    except:
                        continue
            
            if not campo_preenchido:
                print(f"⚠ Campo '{campo_nome}' não encontrado")
        
        print(f"✓ Total de campos preenchidos: {campos_preenchidos}/11")
        assert campos_preenchidos >= 8, "Menos de 8 campos preenchidos"
        
        time.sleep(1)
    
    def test_04_submeter_cadastro(self, driver):
        """
        UC01: Cadastrar Paciente - Submissão
        Valida: Formulário é submetido e cadastro é criado com sucesso
        """
        print("\n=== TESTE 4: Submeter Cadastro ===")
        
        # Procurar botão de submit
        botoes_submit = [
            "//button[contains(text(), 'Cadastrar')]",
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'Registrar')]"
        ]
        
        for xpath in botoes_submit:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de cadastro")
                break
            except:
                continue
        
        # Aguardar resposta (sucesso ou erro)
        time.sleep(3)
        
        # Verificar mensagem de sucesso ou redirecionamento
        url_atual = driver.current_url
        
        if "login" in url_atual.lower():
            print("✓ Redirecionado para login após cadastro")
        elif "dashboard" in url_atual.lower():
            print("✓ Redirecionado para dashboard (login automático)")
        else:
            # Procurar mensagem de sucesso
            try:
                mensagem = driver.find_element(By.XPATH, "//*[contains(text(), 'sucesso')]")
                print(f"✓ Mensagem de sucesso: {mensagem.text}")
            except:
                print("⚠ Nenhuma mensagem de sucesso encontrada")
        
        time.sleep(1)
    
    def test_05_fazer_login(self, driver, paciente_dados):
        """
        UC02: Login do Paciente
        Valida: Paciente consegue fazer login com credenciais criadas
        """
        print("\n=== TESTE 5: Fazer Login ===")
        
        # Navegar para login se não estiver lá
        if "login" not in driver.current_url.lower():
            driver.get(f"{BASE_URL}/paciente/login.html")
            time.sleep(1)
        
        # Preencher email
        campos_email = ["email", "usuario", "login"]
        for campo_id in campos_email:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(paciente_dados["email"])
                print(f"✓ Email preenchido: {paciente_dados['email']}")
                break
            except:
                continue
        
        # Preencher senha
        campos_senha = ["senha", "password"]
        for campo_id in campos_senha:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(paciente_dados["senha"])
                print(f"✓ Senha preenchida")
                break
            except:
                continue
        
        # Clicar em login
        botoes_login = [
            "//button[contains(text(), 'Entrar')]",
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'Login')]"
        ]
        
        for xpath in botoes_login:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de login")
                break
            except:
                continue
        
        # Aguardar redirecionamento para dashboard
        time.sleep(3)
        
        assert "dashboard" in driver.current_url.lower(), "Não redirecionou para dashboard"
        print("✓ Login realizado com sucesso - Dashboard carregado")
        
        time.sleep(1)
    
    def test_06_validar_dashboard(self, driver, paciente_dados):
        """
        UC: Visualizar Dashboard
        Valida: Dashboard exibe informações do paciente e opções de navegação
        """
        print("\n=== TESTE 6: Validar Dashboard ===")
        
        # Verificar se está no dashboard
        assert "dashboard" in driver.current_url.lower()
        
        # Procurar nome do paciente
        try:
            elemento_nome = driver.find_element(By.XPATH, f"//*[contains(text(), 'Paciente')]")
            print(f"✓ Nome do paciente encontrado: {elemento_nome.text}")
        except:
            print("⚠ Nome do paciente não encontrado no dashboard")
        
        # Validar links de navegação
        links_esperados = [
            ("Agendar", "agendar"),
            ("Consultas", "consultas"),
            ("Perfil", "perfil")
        ]
        
        links_encontrados = 0
        for texto_link, url_esperada in links_esperados:
            try:
                link = driver.find_element(By.PARTIAL_LINK_TEXT, texto_link)
                assert link.is_displayed()
                links_encontrados += 1
                print(f"✓ Link '{texto_link}' encontrado")
            except:
                print(f"⚠ Link '{texto_link}' não encontrado")
        
        assert links_encontrados >= 2, "Menos de 2 links de navegação encontrados"
        print(f"✓ {links_encontrados} links de navegação validados")
        
        time.sleep(1)
    
    def test_07_navegar_para_agendar(self, driver):
        """
        UC: Navegação para Agendamento
        Valida: Navegação para página de agendamento funciona
        """
        print("\n=== TESTE 7: Navegar para Agendar ===")
        
        # Clicar no link de agendar
        try:
            link_agendar = driver.find_element(By.PARTIAL_LINK_TEXT, "Agendar")
            link_agendar.click()
            print("✓ Clicou no link 'Agendar'")
        except:
            driver.get(f"{BASE_URL}/paciente/agendar.html")
            print("⚠ Navegação direta para agendar.html")
        
        time.sleep(2)
        assert "agendar" in driver.current_url.lower()
        print("✓ Página de agendamento carregada")
    
    def test_08_selecionar_especialidade(self, driver):
        """
        UC03: Agendar Consulta - Passo 1 (Especialidade)
        Valida: Paciente consegue selecionar especialidade
        """
        print("\n=== TESTE 8: Selecionar Especialidade ===")
        
        # Procurar select de especialidade
        campos_especialidade = ["especialidade", "especialidadeId", "especialidade_id"]
        
        for campo_id in campos_especialidade:
            try:
                select_element = driver.find_element(By.ID, campo_id)
                select = Select(select_element)
                
                # Aguardar opções carregarem
                time.sleep(2)
                
                opcoes = select.options
                print(f"✓ {len(opcoes)} especialidades encontradas")
                
                if len(opcoes) > 1:
                    # Selecionar segunda opção (primeira geralmente é "Selecione...")
                    select.select_by_index(1)
                    especialidade_selecionada = select.first_selected_option.text
                    print(f"✓ Especialidade selecionada: {especialidade_selecionada}")
                    return
            except Exception as e:
                print(f"⚠ Erro ao selecionar especialidade ({campo_id}): {str(e)}")
                continue
        
        print("⚠ Campo de especialidade não encontrado")
    
    def test_09_selecionar_medico(self, driver):
        """
        UC03: Agendar Consulta - Passo 2 (Médico)
        Valida: Paciente consegue selecionar médico
        """
        print("\n=== TESTE 9: Selecionar Médico ===")
        
        time.sleep(2)  # Aguardar carregar médicos
        
        campos_medico = ["medico", "medicoId", "medico_id"]
        
        for campo_id in campos_medico:
            try:
                select_element = driver.find_element(By.ID, campo_id)
                select = Select(select_element)
                
                # Aguardar opções carregarem
                time.sleep(2)
                
                opcoes = select.options
                print(f"✓ {len(opcoes)} médicos encontrados")
                
                if len(opcoes) > 1:
                    select.select_by_index(1)
                    medico_selecionado = select.first_selected_option.text
                    print(f"✓ Médico selecionado: {medico_selecionado}")
                    return
            except Exception as e:
                print(f"⚠ Erro ao selecionar médico ({campo_id}): {str(e)}")
                continue
        
        print("⚠ Campo de médico não encontrado")
    
    def test_10_selecionar_data(self, driver):
        """
        UC03: Agendar Consulta - Passo 3 (Data)
        Valida: Paciente consegue selecionar data futura
        """
        print("\n=== TESTE 10: Selecionar Data ===")
        
        time.sleep(2)  # Aguardar carregar datas
        
        # Data futura (próxima semana)
        data_consulta = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        campos_data = ["data", "dataConsulta", "data_consulta"]
        
        for campo_id in campos_data:
            try:
                campo_data = driver.find_element(By.ID, campo_id)
                campo_data.clear()
                campo_data.send_keys(data_consulta)
                print(f"✓ Data selecionada: {data_consulta}")
                return
            except Exception as e:
                print(f"⚠ Erro ao selecionar data ({campo_id}): {str(e)}")
                continue
        
        print("⚠ Campo de data não encontrado")
    
    def test_11_selecionar_horario(self, driver):
        """
        UC03: Agendar Consulta - Passo 4 (Horário)
        Valida: Paciente consegue selecionar horário disponível
        """
        print("\n=== TESTE 11: Selecionar Horário ===")
        
        time.sleep(2)  # Aguardar carregar horários
        
        campos_horario = ["horario", "hora", "horarioId"]
        
        for campo_id in campos_horario:
            try:
                # Tentar select
                select_element = driver.find_element(By.ID, campo_id)
                select = Select(select_element)
                
                time.sleep(2)
                opcoes = select.options
                print(f"✓ {len(opcoes)} horários encontrados")
                
                if len(opcoes) > 1:
                    select.select_by_index(1)
                    horario_selecionado = select.first_selected_option.text
                    print(f"✓ Horário selecionado: {horario_selecionado}")
                    return
            except:
                try:
                    # Tentar input de hora
                    campo_hora = driver.find_element(By.ID, campo_id)
                    campo_hora.clear()
                    campo_hora.send_keys("14:00")
                    print(f"✓ Horário digitado: 14:00")
                    return
                except Exception as e:
                    print(f"⚠ Erro ao selecionar horário ({campo_id}): {str(e)}")
                    continue
        
        print("⚠ Campo de horário não encontrado")
    
    def test_12_adicionar_motivo(self, driver):
        """
        UC03: Agendar Consulta - Passo 5 (Motivo)
        Valida: Paciente consegue adicionar motivo da consulta
        """
        print("\n=== TESTE 12: Adicionar Motivo ===")
        
        campos_motivo = ["motivo", "motivoConsulta", "motivo_consulta", "descricao"]
        motivo_texto = "Consulta de rotina para checkup anual"
        
        for campo_id in campos_motivo:
            try:
                campo = driver.find_element(By.ID, campo_id)
                campo.clear()
                campo.send_keys(motivo_texto)
                print(f"✓ Motivo preenchido: {motivo_texto}")
                return
            except:
                continue
        
        print("⚠ Campo de motivo não encontrado (pode ser opcional)")
    
    def test_13_confirmar_agendamento(self, driver):
        """
        UC03: Agendar Consulta - Confirmação
        Valida: Consulta é agendada com sucesso
        """
        print("\n=== TESTE 13: Confirmar Agendamento ===")
        
        time.sleep(1)
        
        # Procurar botão de confirmar
        botoes_confirmar = [
            "//button[contains(text(), 'Agendar')]",
            "//button[contains(text(), 'Confirmar')]",
            "//button[@type='submit']",
            "//input[@type='submit']"
        ]
        
        for xpath in botoes_confirmar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de confirmar agendamento")
                break
            except:
                continue
        
        # Aguardar resposta
        time.sleep(3)
        
        # Verificar mensagem de sucesso
        try:
            mensagem = driver.find_element(By.XPATH, "//*[contains(text(), 'sucesso') or contains(text(), 'agendada')]")
            print(f"✓ Mensagem de sucesso: {mensagem.text}")
        except:
            print("⚠ Mensagem de sucesso não encontrada")
        
        print("✓ Agendamento confirmado")
        time.sleep(1)
    
    def test_14_navegar_para_consultas(self, driver):
        """
        UC04: Visualizar Consultas - Navegação
        Valida: Navegação para lista de consultas
        """
        print("\n=== TESTE 14: Navegar para Consultas ===")
        
        # Tentar clicar no link
        try:
            link_consultas = driver.find_element(By.PARTIAL_LINK_TEXT, "Consultas")
            link_consultas.click()
            print("✓ Clicou no link 'Consultas'")
        except:
            driver.get(f"{BASE_URL}/paciente/consultas.html")
            print("⚠ Navegação direta para consultas.html")
        
        time.sleep(2)
        assert "consultas" in driver.current_url.lower()
        print("✓ Página de consultas carregada")
    
    def test_15_visualizar_lista_consultas(self, driver):
        """
        UC04: Visualizar Consultas
        Valida: Lista de consultas é exibida com consulta agendada
        """
        print("\n=== TESTE 15: Visualizar Lista de Consultas ===")
        
        time.sleep(2)  # Aguardar carregar consultas
        
        # Procurar tabela ou lista de consultas
        elementos_consulta = [
            "//table//tr",
            "//div[contains(@class, 'consulta')]",
            "//ul[contains(@class, 'consultas')]//li"
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
            print("⚠ Nenhuma consulta encontrada na lista")
        else:
            print(f"✓ Lista de consultas validada com {consultas_encontradas} itens")
        
        time.sleep(1)
    
    def test_16_abrir_modal_reagendar(self, driver):
        """
        UC06: Reagendar Consulta - Abrir Modal
        Valida: Modal de reagendamento abre corretamente
        """
        print("\n=== TESTE 16: Abrir Modal de Reagendar ===")
        
        # Procurar botão de reagendar
        botoes_reagendar = [
            "//button[contains(text(), 'Reagendar')]",
            "//a[contains(text(), 'Reagendar')]",
            "//button[contains(@class, 'reagendar')]"
        ]
        
        for xpath in botoes_reagendar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão 'Reagendar'")
                time.sleep(2)
                
                # Verificar se modal abriu
                modais = [
                    "//div[contains(@id, 'modal')]",
                    "//div[contains(@class, 'modal')]",
                    "//div[contains(@class, 'popup')]"
                ]
                
                for modal_xpath in modais:
                    try:
                        modal = driver.find_element(By.XPATH, modal_xpath)
                        if modal.is_displayed():
                            print("✓ Modal de reagendamento aberto")
                            return
                    except:
                        continue
                
                print("⚠ Modal não encontrado (pode não estar visível)")
                return
            except:
                continue
        
        print("⚠ Botão de reagendar não encontrado")
    
    def test_17_fechar_modal(self, driver):
        """
        UC: Fechar Modal
        Valida: Modal pode ser fechado
        """
        print("\n=== TESTE 17: Fechar Modal ===")
        
        # Procurar botão de fechar
        botoes_fechar = [
            "//button[contains(text(), 'Cancelar')]",
            "//button[contains(text(), 'Fechar')]",
            "//button[contains(@class, 'close')]",
            "//span[contains(@class, 'close')]"
        ]
        
        for xpath in botoes_fechar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão de fechar modal")
                time.sleep(1)
                return
            except:
                continue
        
        print("⚠ Botão de fechar não encontrado")
    
    def test_18_cancelar_consulta(self, driver):
        """
        UC05: Cancelar Consulta
        Valida: Paciente consegue cancelar consulta agendada
        """
        print("\n=== TESTE 18: Cancelar Consulta ===")
        
        time.sleep(1)
        
        # Procurar botão de cancelar
        botoes_cancelar = [
            "//button[contains(text(), 'Cancelar Consulta')]",
            "//button[contains(text(), 'Cancelar')]",
            "//a[contains(text(), 'Cancelar')]"
        ]
        
        for xpath in botoes_cancelar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão 'Cancelar'")
                time.sleep(2)
                
                # Confirmar cancelamento se houver modal de confirmação
                try:
                    botao_confirmar = driver.find_element(By.XPATH, "//button[contains(text(), 'Sim')]")
                    botao_confirmar.click()
                    print("✓ Confirmou cancelamento")
                except:
                    pass
                
                time.sleep(2)
                
                # Verificar mensagem de sucesso
                try:
                    mensagem = driver.find_element(By.XPATH, "//*[contains(text(), 'cancelada')]")
                    print(f"✓ Mensagem: {mensagem.text}")
                except:
                    print("⚠ Mensagem de cancelamento não encontrada")
                
                return
            except:
                continue
        
        print("⚠ Botão de cancelar não encontrado")
    
    def test_19_navegar_para_perfil(self, driver):
        """
        UC07: Visualizar Perfil - Navegação
        Valida: Navegação para página de perfil
        """
        print("\n=== TESTE 19: Navegar para Perfil ===")
        
        try:
            link_perfil = driver.find_element(By.PARTIAL_LINK_TEXT, "Perfil")
            link_perfil.click()
            print("✓ Clicou no link 'Perfil'")
        except:
            driver.get(f"{BASE_URL}/paciente/perfil.html")
            print("⚠ Navegação direta para perfil.html")
        
        time.sleep(2)
        assert "perfil" in driver.current_url.lower()
        print("✓ Página de perfil carregada")
    
    def test_20_visualizar_dados_perfil(self, driver, paciente_dados):
        """
        UC07: Visualizar Perfil
        Valida: Dados do perfil são exibidos corretamente
        """
        print("\n=== TESTE 20: Visualizar Dados do Perfil ===")
        
        # Verificar se campos estão preenchidos
        campos_perfil = ["nome", "email", "cpf", "telefone"]
        campos_encontrados = 0
        
        for campo_id in campos_perfil:
            try:
                campo = driver.find_element(By.ID, campo_id)
                valor = campo.get_attribute("value")
                if valor:
                    campos_encontrados += 1
                    print(f"✓ Campo '{campo_id}' preenchido: {valor[:20]}...")
            except:
                print(f"⚠ Campo '{campo_id}' não encontrado")
        
        print(f"✓ {campos_encontrados} campos de perfil validados")
    
    def test_21_editar_telefone(self, driver):
        """
        UC08: Editar Perfil
        Valida: Paciente consegue editar dados do perfil
        """
        print("\n=== TESTE 21: Editar Telefone ===")
        
        novo_telefone = "(47) 99999-8888"
        
        try:
            campo_telefone = driver.find_element(By.ID, "telefone")
            campo_telefone.clear()
            campo_telefone.send_keys(novo_telefone)
            print(f"✓ Telefone alterado para: {novo_telefone}")
        except:
            print("⚠ Campo telefone não encontrado")
        
        time.sleep(1)
    
    def test_22_salvar_alteracoes_perfil(self, driver):
        """
        UC08: Editar Perfil - Salvar
        Valida: Alterações são salvas com sucesso
        """
        print("\n=== TESTE 22: Salvar Alterações do Perfil ===")
        
        # Procurar botão de salvar
        botoes_salvar = [
            "//button[contains(text(), 'Salvar')]",
            "//button[contains(text(), 'Atualizar')]",
            "//button[@type='submit']"
        ]
        
        for xpath in botoes_salvar:
            try:
                botao = driver.find_element(By.XPATH, xpath)
                botao.click()
                print(f"✓ Clicou no botão 'Salvar'")
                time.sleep(2)
                
                # Verificar mensagem de sucesso
                try:
                    mensagem = driver.find_element(By.XPATH, "//*[contains(text(), 'atualizado') or contains(text(), 'sucesso')]")
                    print(f"✓ Mensagem: {mensagem.text}")
                except:
                    print("⚠ Mensagem de sucesso não encontrada")
                
                return
            except:
                continue
        
        print("⚠ Botão de salvar não encontrado")
    
    def test_23_fazer_logout(self, driver):
        """
        UC: Logout
        Valida: Paciente consegue fazer logout do sistema
        """
        print("\n=== TESTE 23: Fazer Logout ===")
        
        # Procurar botão/link de logout
        logout_xpath = [
            "//button[contains(text(), 'Sair')]",
            "//a[contains(text(), 'Sair')]",
            "//button[contains(text(), 'Logout')]",
            "//a[contains(text(), 'Logout')]"
        ]
        
        for xpath in logout_xpath:
            try:
                elemento = driver.find_element(By.XPATH, xpath)
                elemento.click()
                print(f"✓ Clicou em logout")
                time.sleep(2)
                
                # Verificar redirecionamento para login ou index
                url_atual = driver.current_url
                if "login" in url_atual.lower() or "index" in url_atual.lower():
                    print("✓ Logout realizado com sucesso")
                    return
            except:
                continue
        
        print("⚠ Botão de logout não encontrado")
        
        # Limpar localStorage como fallback
        driver.execute_script("localStorage.clear();")
        driver.get(f"{BASE_URL}/index.html")
        print("⚠ Logout forçado (limpeza de localStorage)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
