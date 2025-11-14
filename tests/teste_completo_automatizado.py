"""
Script de Teste Automatizado Completo - Clínica Saúde+
Testa todas as funcionalidades do sistema (Paciente, Médico, Admin)
"""
import time
import random
import string
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys

# Configurações
BASE_URL = "http://localhost"
TIMEOUT = 10  # Timeout para espera de elementos
SCREENSHOT_DIR = "screenshots"

class TestadorClinica:
    def __init__(self):
        self.driver = None
        self.testes_executados = 0
        self.testes_sucesso = 0
        self.testes_falha = 0
        self.erros = []
        
    def setup_driver(self):
        """Configura o driver do Chrome"""
        print("🔧 Configurando navegador Chrome...")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        print("✅ Navegador configurado com sucesso!\n")
        
    def gerar_cpf(self):
        """Gera CPF aleatório para testes"""
        return ''.join([str(random.randint(0, 9)) for _ in range(11)])
    
    def gerar_email(self):
        """Gera email aleatório para testes"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"teste_{random_str}@clinica.com"
    
    def aguardar_elemento(self, by, value, timeout=TIMEOUT):
        """Aguarda elemento aparecer na página"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def aguardar_e_clicar(self, by, value, timeout=TIMEOUT):
        """Aguarda elemento ser clicável e clica"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return True
        except:
            return False
    
    def preencher_campo(self, by, value, texto):
        """Preenche um campo de formulário"""
        try:
            campo = self.aguardar_elemento(by, value)
            if campo:
                campo.clear()
                campo.send_keys(texto)
                return True
        except:
            pass
        return False
    
    def registrar_teste(self, nome, sucesso, erro=None):
        """Registra resultado de um teste"""
        self.testes_executados += 1
        if sucesso:
            self.testes_sucesso += 1
            print(f"✅ {nome}")
        else:
            self.testes_falha += 1
            print(f"❌ {nome}")
            if erro:
                self.erros.append(f"{nome}: {erro}")
                print(f"   Erro: {erro}")
    
    # ==================== TESTES DE PACIENTE ====================
    
    def testar_cadastro_paciente(self):
        """Testa cadastro de novo paciente"""
        print("\n📝 TESTE: Cadastro de Paciente")
        try:
            # Gerar dados aleatórios
            cpf = self.gerar_cpf()
            email = self.gerar_email()
            
            # Navegar para página de cadastro
            self.driver.get(f"{BASE_URL}/paciente/cadastro.html")
            time.sleep(1)
            
            # Preencher formulário
            self.preencher_campo(By.ID, "nome", "João Teste da Silva")
            self.preencher_campo(By.ID, "cpf", cpf)
            self.preencher_campo(By.ID, "email", email)
            self.preencher_campo(By.ID, "senha", "senha12345")
            self.preencher_campo(By.ID, "confirmarSenha", "senha12345")
            self.preencher_campo(By.ID, "telefone", "(47) 99999-9999")
            self.preencher_campo(By.ID, "dataNascimento", "01/01/1990")
            
            # Submeter formulário
            btn_submit = self.aguardar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            if btn_submit:
                btn_submit.click()
                time.sleep(2)
                
                # Verificar sucesso (pode redirecionar ou mostrar mensagem)
                url_atual = self.driver.current_url
                if "login" in url_atual.lower() or "sucesso" in self.driver.page_source.lower():
                    self.registrar_teste("Cadastro de Paciente", True)
                    return {"email": email, "senha": "senha12345", "cpf": cpf}
                else:
                    self.registrar_teste("Cadastro de Paciente", False, "Redirecionamento não ocorreu")
            else:
                self.registrar_teste("Cadastro de Paciente", False, "Botão de submit não encontrado")
                
        except Exception as e:
            self.registrar_teste("Cadastro de Paciente", False, str(e))
        
        return None
    
    def testar_login_paciente(self, email, senha):
        """Testa login de paciente"""
        print("\n🔐 TESTE: Login de Paciente")
        try:
            self.driver.get(f"{BASE_URL}/paciente/login.html")
            time.sleep(1)
            
            self.preencher_campo(By.ID, "email", email)
            self.preencher_campo(By.ID, "senha", senha)
            
            btn_login = self.aguardar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            if btn_login:
                btn_login.click()
                time.sleep(2)
                
                # Verificar se foi para dashboard
                url_atual = self.driver.current_url
                if "dashboard" in url_atual:
                    self.registrar_teste("Login de Paciente", True)
                    return True
                else:
                    self.registrar_teste("Login de Paciente", False, f"URL atual: {url_atual}")
            else:
                self.registrar_teste("Login de Paciente", False, "Botão de login não encontrado")
                
        except Exception as e:
            self.registrar_teste("Login de Paciente", False, str(e))
        
        return False
    
    def testar_agendar_consulta(self):
        """Testa agendamento de consulta"""
        print("\n📅 TESTE: Agendamento de Consulta")
        try:
            self.driver.get(f"{BASE_URL}/paciente/agendar.html")
            time.sleep(2)
            
            # Selecionar especialidade (primeiro disponível)
            select_especialidade = self.aguardar_elemento(By.ID, "especialidade")
            if select_especialidade:
                select = Select(select_especialidade)
                if len(select.options) > 1:
                    select.select_by_index(1)
                    time.sleep(1)
                    
                    # Selecionar médico (primeiro disponível)
                    select_medico = self.aguardar_elemento(By.ID, "medico")
                    if select_medico:
                        select_med = Select(select_medico)
                        if len(select_med.options) > 1:
                            select_med.select_by_index(1)
                            time.sleep(1)
                            
                            # Selecionar data (amanhã)
                            data_amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                            self.preencher_campo(By.ID, "data", data_amanha)
                            time.sleep(1)
                            
                            # Selecionar horário (primeiro disponível)
                            select_horario = self.aguardar_elemento(By.ID, "horario")
                            if select_horario:
                                select_hor = Select(select_horario)
                                if len(select_hor.options) > 0:
                                    select_hor.select_by_index(0)
                                    
                                    # Motivo da consulta
                                    self.preencher_campo(By.ID, "motivo", "Consulta de rotina")
                                    
                                    # Submeter
                                    btn_agendar = self.aguardar_elemento(By.CSS_SELECTOR, "button[type='submit']")
                                    if btn_agendar:
                                        btn_agendar.click()
                                        time.sleep(2)
                                        
                                        # Verificar sucesso
                                        if "sucesso" in self.driver.page_source.lower() or "agendada" in self.driver.page_source.lower():
                                            self.registrar_teste("Agendamento de Consulta", True)
                                            return True
            
            self.registrar_teste("Agendamento de Consulta", False, "Não foi possível completar agendamento")
                
        except Exception as e:
            self.registrar_teste("Agendamento de Consulta", False, str(e))
        
        return False
    
    def testar_visualizar_consultas(self):
        """Testa visualização de consultas do paciente"""
        print("\n👁️ TESTE: Visualização de Consultas")
        try:
            self.driver.get(f"{BASE_URL}/paciente/consultas.html")
            time.sleep(2)
            
            # Verificar se tabela de consultas existe
            tabela = self.aguardar_elemento(By.CSS_SELECTOR, "table, .consulta-card")
            if tabela:
                self.registrar_teste("Visualização de Consultas", True)
                return True
            else:
                self.registrar_teste("Visualização de Consultas", False, "Tabela não encontrada")
                
        except Exception as e:
            self.registrar_teste("Visualização de Consultas", False, str(e))
        
        return False
    
    # ==================== TESTES DE MÉDICO ====================
    
    def testar_login_medico(self):
        """Testa login de médico"""
        print("\n🔐 TESTE: Login de Médico")
        try:
            self.driver.get(f"{BASE_URL}/medico/login.html")
            time.sleep(1)
            
            # Usar credenciais do seed
            self.preencher_campo(By.ID, "crm", "12345-SC")
            self.preencher_campo(By.ID, "senha", "medico123")
            
            btn_login = self.aguardar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            if btn_login:
                btn_login.click()
                time.sleep(2)
                
                # Verificar se foi para dashboard
                url_atual = self.driver.current_url
                if "dashboard" in url_atual:
                    self.registrar_teste("Login de Médico", True)
                    return True
                else:
                    self.registrar_teste("Login de Médico", False, f"URL atual: {url_atual}")
            else:
                self.registrar_teste("Login de Médico", False, "Botão de login não encontrado")
                
        except Exception as e:
            self.registrar_teste("Login de Médico", False, str(e))
        
        return False
    
    def testar_visualizar_agenda_medico(self):
        """Testa visualização de agenda do médico"""
        print("\n📅 TESTE: Visualização de Agenda do Médico")
        try:
            self.driver.get(f"{BASE_URL}/medico/agenda.html")
            time.sleep(2)
            
            # Verificar se calendário ou lista de consultas existe
            elemento = self.aguardar_elemento(By.CSS_SELECTOR, ".calendar, table, .consulta-card")
            if elemento:
                self.registrar_teste("Visualização de Agenda do Médico", True)
                return True
            else:
                self.registrar_teste("Visualização de Agenda do Médico", False, "Agenda não encontrada")
                
        except Exception as e:
            self.registrar_teste("Visualização de Agenda do Médico", False, str(e))
        
        return False
    
    def testar_gerenciar_horarios_medico(self):
        """Testa gerenciamento de horários do médico"""
        print("\n⏰ TESTE: Gerenciamento de Horários")
        try:
            self.driver.get(f"{BASE_URL}/medico/horarios.html")
            time.sleep(2)
            
            # Verificar se formulário de horários existe
            form = self.aguardar_elemento(By.CSS_SELECTOR, "form, #formHorario")
            if form:
                self.registrar_teste("Gerenciamento de Horários", True)
                return True
            else:
                self.registrar_teste("Gerenciamento de Horários", False, "Formulário não encontrado")
                
        except Exception as e:
            self.registrar_teste("Gerenciamento de Horários", False, str(e))
        
        return False
    
    # ==================== TESTES DE ADMIN ====================
    
    def testar_login_admin(self):
        """Testa login de administrador"""
        print("\n🔐 TESTE: Login de Admin")
        try:
            self.driver.get(f"{BASE_URL}/admin/login.html")
            time.sleep(1)
            
            # Usar credenciais do seed
            self.preencher_campo(By.ID, "email", "admin@clinica.com")
            self.preencher_campo(By.ID, "senha", "admin123")
            
            btn_login = self.aguardar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            if btn_login:
                btn_login.click()
                time.sleep(2)
                
                # Verificar se foi para dashboard
                url_atual = self.driver.current_url
                if "dashboard" in url_atual:
                    self.registrar_teste("Login de Admin", True)
                    return True
                else:
                    self.registrar_teste("Login de Admin", False, f"URL atual: {url_atual}")
            else:
                self.registrar_teste("Login de Admin", False, "Botão de login não encontrado")
                
        except Exception as e:
            self.registrar_teste("Login de Admin", False, str(e))
        
        return False
    
    def testar_dashboard_admin(self):
        """Testa dashboard administrativo"""
        print("\n📊 TESTE: Dashboard Admin")
        try:
            self.driver.get(f"{BASE_URL}/admin/dashboard.html")
            time.sleep(2)
            
            # Verificar se estatísticas existem
            stats = self.aguardar_elemento(By.CSS_SELECTOR, ".stat-card, .card, .estatistica")
            if stats:
                self.registrar_teste("Dashboard Admin", True)
                return True
            else:
                self.registrar_teste("Dashboard Admin", False, "Estatísticas não encontradas")
                
        except Exception as e:
            self.registrar_teste("Dashboard Admin", False, str(e))
        
        return False
    
    def testar_listar_medicos_admin(self):
        """Testa listagem de médicos no admin"""
        print("\n👨‍⚕️ TESTE: Listar Médicos (Admin)")
        try:
            self.driver.get(f"{BASE_URL}/admin/medicos.html")
            time.sleep(2)
            
            # Verificar se tabela de médicos existe
            tabela = self.aguardar_elemento(By.CSS_SELECTOR, "table, .medico-card")
            if tabela:
                self.registrar_teste("Listar Médicos (Admin)", True)
                return True
            else:
                self.registrar_teste("Listar Médicos (Admin)", False, "Tabela não encontrada")
                
        except Exception as e:
            self.registrar_teste("Listar Médicos (Admin)", False, str(e))
        
        return False
    
    def testar_listar_pacientes_admin(self):
        """Testa listagem de pacientes no admin"""
        print("\n👥 TESTE: Listar Pacientes (Admin)")
        try:
            self.driver.get(f"{BASE_URL}/admin/pacientes.html")
            time.sleep(2)
            
            # Verificar se tabela de pacientes existe
            tabela = self.aguardar_elemento(By.CSS_SELECTOR, "table, .paciente-card")
            if tabela:
                self.registrar_teste("Listar Pacientes (Admin)", True)
                return True
            else:
                self.registrar_teste("Listar Pacientes (Admin)", False, "Tabela não encontrada")
                
        except Exception as e:
            self.registrar_teste("Listar Pacientes (Admin)", False, str(e))
        
        return False
    
    def testar_gerenciar_convenios_admin(self):
        """Testa gerenciamento de convênios no admin"""
        print("\n🏥 TESTE: Gerenciar Convênios (Admin)")
        try:
            self.driver.get(f"{BASE_URL}/admin/convenios.html")
            time.sleep(2)
            
            # Verificar se lista de convênios existe
            elemento = self.aguardar_elemento(By.CSS_SELECTOR, "table, .convenio-card, #listaConvenios")
            if elemento:
                self.registrar_teste("Gerenciar Convênios (Admin)", True)
                return True
            else:
                self.registrar_teste("Gerenciar Convênios (Admin)", False, "Lista não encontrada")
                
        except Exception as e:
            self.registrar_teste("Gerenciar Convênios (Admin)", False, str(e))
        
        return False
    
    # ==================== EXECUÇÃO DOS TESTES ====================
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        print("=" * 80)
        print("🧪 INICIANDO TESTES AUTOMATIZADOS - CLÍNICA SAÚDE+")
        print("=" * 80)
        
        try:
            self.setup_driver()
            
            # ===== TESTES DE PACIENTE =====
            print("\n" + "=" * 80)
            print("👤 MÓDULO PACIENTE")
            print("=" * 80)
            
            dados_paciente = self.testar_cadastro_paciente()
            
            if dados_paciente:
                self.testar_login_paciente(dados_paciente["email"], dados_paciente["senha"])
                self.testar_visualizar_consultas()
                self.testar_agendar_consulta()
            
            # ===== TESTES DE MÉDICO =====
            print("\n" + "=" * 80)
            print("👨‍⚕️ MÓDULO MÉDICO")
            print("=" * 80)
            
            if self.testar_login_medico():
                self.testar_visualizar_agenda_medico()
                self.testar_gerenciar_horarios_medico()
            
            # ===== TESTES DE ADMIN =====
            print("\n" + "=" * 80)
            print("👔 MÓDULO ADMINISTRATIVO")
            print("=" * 80)
            
            if self.testar_login_admin():
                self.testar_dashboard_admin()
                self.testar_listar_medicos_admin()
                self.testar_listar_pacientes_admin()
                self.testar_gerenciar_convenios_admin()
            
            # ===== RELATÓRIO FINAL =====
            self.exibir_relatorio()
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO: {e}")
            sys.exit(1)
        finally:
            self.finalizar()
    
    def exibir_relatorio(self):
        """Exibe relatório final dos testes"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DE TESTES")
        print("=" * 80)
        print(f"Total de Testes: {self.testes_executados}")
        print(f"✅ Sucesso: {self.testes_sucesso}")
        print(f"❌ Falha: {self.testes_falha}")
        
        if self.testes_falha > 0:
            print(f"\n⚠️ Taxa de Sucesso: {(self.testes_sucesso/self.testes_executados)*100:.1f}%")
            print("\n🔍 ERROS ENCONTRADOS:")
            for i, erro in enumerate(self.erros, 1):
                print(f"  {i}. {erro}")
        else:
            print(f"\n🎉 100% DE SUCESSO! Todos os {self.testes_executados} testes passaram!")
        
        print("=" * 80)
    
    def finalizar(self):
        """Finaliza o driver e limpa recursos"""
        print("\n🧹 Finalizando testes...")
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Navegador fechado com sucesso")
            except:
                print("⚠️ Erro ao fechar navegador")
        
        # Retornar código de saída apropriado
        if self.testes_falha > 0:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == "__main__":
    testador = TestadorClinica()
    testador.executar_todos_testes()
