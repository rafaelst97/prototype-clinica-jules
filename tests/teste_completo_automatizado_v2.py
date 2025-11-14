"""
Script de Teste Automatizado Completo - Clínica Saúde+
Testa todas as funcionalidades do sistema de forma autônoma
"""
import time
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class ClinicaTester:
    def __init__(self):
        self.base_url = "http://localhost"
        self.driver = None
        self.test_results = []
        self.setup_driver()
        
    def setup_driver(self):
        """Configura o driver do Chrome"""
        print("🔧 Configurando Chrome WebDriver...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)
        print("✅ Driver configurado")
        
    def wait_and_find(self, by, value, timeout=10):
        """Espera e encontra elemento com timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"⚠️  Timeout ao buscar elemento: {value}")
            return None
            
    def wait_and_click(self, by, value, timeout=10):
        """Espera e clica em elemento"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            time.sleep(0.5)
            return True
        except TimeoutException:
            print(f"⚠️  Timeout ao clicar: {value}")
            return False
            
    def fill_input(self, by, value, text):
        """Preenche input e aguarda"""
        try:
            element = self.wait_and_find(by, value)
            if element:
                element.clear()
                element.send_keys(text)
                time.sleep(0.3)
                return True
        except Exception as e:
            print(f"⚠️  Erro ao preencher input {value}: {e}")
        return False
        
    def log_test(self, module, test_name, status, message=""):
        """Registra resultado do teste"""
        result = {
            "module": module,
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} [{module}] {test_name}: {status} {message}")
        
    def test_admin_login(self):
        """Testa login do administrador"""
        print("\n" + "="*60)
        print("MÓDULO ADMIN - LOGIN")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/admin/login.html")
            time.sleep(1)
            
            # Preencher formulário (admin usa 'usuario' não 'email')
            self.fill_input(By.ID, "usuario", "admin")
            self.fill_input(By.ID, "senha", "admin123")
            
            # Clicar em entrar
            self.wait_and_click(By.CSS_SELECTOR, "button[type='submit']")
            time.sleep(3)
            
            # Tentar aceitar alert se houver
            try:
                alert = self.driver.switch_to.alert
                print(f"  📢 Alert detectado: {alert.text}")
                alert.accept()
                time.sleep(1)
            except:
                pass
            
            # Verificar redirecionamento para dashboard
            if "dashboard" in self.driver.current_url:
                self.log_test("ADMIN", "Login", "PASS", "- Redirecionado para dashboard")
                return True
            else:
                # Debug: capturar mensagem de erro se houver
                try:
                    console_logs = self.driver.get_log('browser')
                    if console_logs:
                        print(f"  🔍 Console logs: {console_logs[-1]}")
                except:
                    pass
                self.log_test("ADMIN", "Login", "FAIL", f"- URL atual: {self.driver.current_url}")
                return False
                
        except Exception as e:
            self.log_test("ADMIN", "Login", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_admin_listar_medicos(self):
        """Testa listagem de médicos"""
        print("\n📋 Testando listagem de médicos...")
        
        try:
            self.driver.get(f"{self.base_url}/admin/medicos.html")
            time.sleep(2)
            
            # Verificar se a tabela existe
            tabela = self.wait_and_find(By.CSS_SELECTOR, "table")
            if tabela:
                # Contar médicos na tabela
                linhas = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                num_medicos = len(linhas)
                
                if num_medicos >= 3:  # Esperamos pelo menos 3 médicos do seed
                    self.log_test("ADMIN", "Listar Médicos", "PASS", f"- {num_medicos} médicos encontrados")
                    return True
                else:
                    self.log_test("ADMIN", "Listar Médicos", "WARN", f"- Apenas {num_medicos} médicos")
                    return True
            else:
                self.log_test("ADMIN", "Listar Médicos", "FAIL", "- Tabela não encontrada")
                return False
                
        except Exception as e:
            self.log_test("ADMIN", "Listar Médicos", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_admin_cadastrar_medico(self):
        """Testa cadastro de novo médico"""
        print("\n➕ Testando cadastro de médico...")
        
        try:
            self.driver.get(f"{self.base_url}/admin/medicos.html")
            time.sleep(1)
            
            # Clicar em novo médico
            if not self.wait_and_click(By.ID, "btnNovoMedico"):
                self.log_test("ADMIN", "Cadastrar Médico", "FAIL", "- Botão não encontrado")
                return False
                
            time.sleep(1)
            
            # Preencher formulário
            timestamp = datetime.now().strftime("%H%M%S")
            self.fill_input(By.ID, "nome", f"Dr. Teste {timestamp}")
            self.fill_input(By.ID, "email", f"teste{timestamp}@clinica.com")
            self.fill_input(By.ID, "cpf", f"999.888.777-{timestamp[-2:]}")
            self.fill_input(By.ID, "crm", f"CRM-{timestamp}")
            self.fill_input(By.ID, "senha", "senha123")
            self.fill_input(By.ID, "telefone", "(47) 99999-8888")
            
            # Selecionar especialidade
            try:
                select_especialidade = Select(self.wait_and_find(By.ID, "especialidadeId"))
                select_especialidade.select_by_index(1)  # Selecionar primeira especialidade
            except:
                pass
                
            # Salvar
            if self.wait_and_click(By.ID, "btnSalvar"):
                time.sleep(2)
                self.log_test("ADMIN", "Cadastrar Médico", "PASS", f"- Dr. Teste {timestamp}")
                return True
            else:
                self.log_test("ADMIN", "Cadastrar Médico", "FAIL", "- Botão salvar não funcionou")
                return False
                
        except Exception as e:
            self.log_test("ADMIN", "Cadastrar Médico", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_admin_listar_convenios(self):
        """Testa listagem de convênios"""
        print("\n📋 Testando listagem de convênios...")
        
        try:
            self.driver.get(f"{self.base_url}/admin/convenios.html")
            time.sleep(2)
            
            # Verificar se a tabela existe
            tabela = self.wait_and_find(By.CSS_SELECTOR, "table")
            if tabela:
                linhas = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                num_convenios = len(linhas)
                
                if num_convenios >= 4:  # Esperamos 4 convênios do seed
                    self.log_test("ADMIN", "Listar Convênios", "PASS", f"- {num_convenios} convênios")
                    return True
                else:
                    self.log_test("ADMIN", "Listar Convênios", "WARN", f"- {num_convenios} convênios")
                    return True
            else:
                self.log_test("ADMIN", "Listar Convênios", "FAIL", "- Tabela não encontrada")
                return False
                
        except Exception as e:
            self.log_test("ADMIN", "Listar Convênios", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_medico_login(self):
        """Testa login do médico"""
        print("\n" + "="*60)
        print("MÓDULO MÉDICO - LOGIN")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/medico/login.html")
            time.sleep(1)
            
            # Médico usa 'crm' para login
            self.fill_input(By.ID, "crm", "12345-SC")
            self.fill_input(By.ID, "senha", "medico123")
            
            self.wait_and_click(By.CSS_SELECTOR, "button[type='submit']")
            time.sleep(3)
            
            # Tentar aceitar alert se houver
            try:
                alert = self.driver.switch_to.alert
                print(f"  📢 Alert detectado: {alert.text}")
                alert.accept()
                time.sleep(1)
            except:
                pass
            
            if "dashboard" in self.driver.current_url:
                self.log_test("MEDICO", "Login", "PASS", "- Redirecionado para dashboard")
                return True
            else:
                self.log_test("MEDICO", "Login", "FAIL", f"- URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            self.log_test("MEDICO", "Login", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_medico_visualizar_consultas(self):
        """Testa visualização de consultas do médico"""
        print("\n📅 Testando visualização de consultas...")
        
        try:
            self.driver.get(f"{self.base_url}/medico/consultas.html")
            time.sleep(2)
            
            # Verificar se a página carregou
            titulo = self.wait_and_find(By.TAG_NAME, "h1")
            if titulo:
                self.log_test("MEDICO", "Visualizar Consultas", "PASS", "- Página carregada")
                return True
            else:
                self.log_test("MEDICO", "Visualizar Consultas", "FAIL", "- Página não carregou")
                return False
                
        except Exception as e:
            self.log_test("MEDICO", "Visualizar Consultas", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_medico_horarios(self):
        """Testa gerenciamento de horários"""
        print("\n⏰ Testando gerenciamento de horários...")
        
        try:
            self.driver.get(f"{self.base_url}/medico/horarios.html")
            time.sleep(2)
            
            # Verificar se existem horários listados
            lista = self.wait_and_find(By.ID, "listaHorarios")
            if lista:
                self.log_test("MEDICO", "Gerenciar Horários", "PASS", "- Página de horários OK")
                return True
            else:
                self.log_test("MEDICO", "Gerenciar Horários", "FAIL", "- Lista não encontrada")
                return False
                
        except Exception as e:
            self.log_test("MEDICO", "Gerenciar Horários", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_paciente_cadastro(self):
        """Testa cadastro de novo paciente"""
        print("\n" + "="*60)
        print("MÓDULO PACIENTE - CADASTRO")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/paciente/cadastro.html")
            time.sleep(1)
            
            timestamp = datetime.now().strftime("%H%M%S")
            
            # Preencher formulário
            self.fill_input(By.ID, "nome", f"Paciente Teste {timestamp}")
            self.fill_input(By.ID, "email", f"paciente{timestamp}@teste.com")
            self.fill_input(By.ID, "cpf", f"111.222.333-{timestamp[-2:]}")
            self.fill_input(By.ID, "senha", "teste123")
            self.fill_input(By.ID, "confirmarSenha", "teste123")
            self.fill_input(By.ID, "dataNascimento", "01/01/1990")
            self.fill_input(By.ID, "telefone", "(47) 98888-9999")
            
            # Enviar formulário
            if self.wait_and_click(By.CSS_SELECTOR, "button[type='submit']"):
                time.sleep(2)
                
                # Verificar se foi redirecionado para login
                if "login" in self.driver.current_url:
                    self.log_test("PACIENTE", "Cadastro", "PASS", f"- Paciente {timestamp} criado")
                    return timestamp  # Retorna timestamp para usar no login
                else:
                    self.log_test("PACIENTE", "Cadastro", "WARN", "- Cadastrado mas não redirecionou")
                    return timestamp
            else:
                self.log_test("PACIENTE", "Cadastro", "FAIL", "- Erro ao enviar formulário")
                return None
                
        except Exception as e:
            self.log_test("PACIENTE", "Cadastro", "FAIL", f"- Erro: {str(e)}")
            return None
            
    def test_paciente_login(self, email="paciente1@teste.com"):
        """Testa login do paciente"""
        print("\n🔐 Testando login de paciente...")
        
        try:
            self.driver.get(f"{self.base_url}/paciente/login.html")
            time.sleep(1)
            
            self.fill_input(By.ID, "email", email)
            self.fill_input(By.ID, "senha", "paciente123")
            
            self.wait_and_click(By.CSS_SELECTOR, "button[type='submit']")
            time.sleep(2)
            
            # Tentar aceitar alert se houver
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                time.sleep(1)
            except:
                pass
            
            if "dashboard" in self.driver.current_url:
                self.log_test("PACIENTE", "Login", "PASS", f"- Logado como {email}")
                return True
            else:
                self.log_test("PACIENTE", "Login", "FAIL", f"- URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            self.log_test("PACIENTE", "Login", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_paciente_agendar_consulta(self):
        """Testa agendamento de consulta"""
        print("\n📅 Testando agendamento de consulta...")
        
        try:
            self.driver.get(f"{self.base_url}/paciente/agendar.html")
            time.sleep(2)
            
            # Selecionar especialidade
            try:
                select_esp = Select(self.wait_and_find(By.ID, "especialidade"))
                select_esp.select_by_index(1)  # Primeira especialidade
                time.sleep(1)
            except:
                self.log_test("PACIENTE", "Agendar Consulta", "FAIL", "- Especialidade não encontrada")
                return False
                
            # Selecionar médico
            try:
                select_med = Select(self.wait_and_find(By.ID, "medico"))
                select_med.select_by_index(1)  # Primeiro médico
                time.sleep(1)
            except:
                self.log_test("PACIENTE", "Agendar Consulta", "FAIL", "- Médico não encontrado")
                return False
                
            # Selecionar data (próximo dia útil)
            data_consulta = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            self.fill_input(By.ID, "data", data_consulta)
            time.sleep(1)
            
            # Selecionar horário
            try:
                select_hora = Select(self.wait_and_find(By.ID, "horario", timeout=5))
                if len(select_hora.options) > 1:
                    select_hora.select_by_index(1)  # Primeiro horário disponível
                    time.sleep(1)
                else:
                    self.log_test("PACIENTE", "Agendar Consulta", "WARN", "- Sem horários disponíveis")
                    return False
            except:
                self.log_test("PACIENTE", "Agendar Consulta", "WARN", "- Horário não disponível")
                return False
                
            # Motivo
            self.fill_input(By.ID, "motivo", "Consulta de rotina - Teste automatizado")
            
            # Agendar
            if self.wait_and_click(By.ID, "btnAgendar"):
                time.sleep(2)
                self.log_test("PACIENTE", "Agendar Consulta", "PASS", f"- Data: {data_consulta}")
                return True
            else:
                self.log_test("PACIENTE", "Agendar Consulta", "FAIL", "- Botão agendar não funcionou")
                return False
                
        except Exception as e:
            self.log_test("PACIENTE", "Agendar Consulta", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def test_paciente_visualizar_consultas(self):
        """Testa visualização de consultas"""
        print("\n📋 Testando visualização de consultas...")
        
        try:
            # Aceitar qualquer alert pendente antes de navegar
            try:
                alert = self.driver.switch_to.alert
                print(f"  📢 Alert detectado antes da navegação: {alert.text}")
                alert.accept()
                time.sleep(1)
            except:
                pass
                
            self.driver.get(f"{self.base_url}/paciente/consultas.html")
            time.sleep(2)
            
            # Aceitar alert se houver após o carregamento
            try:
                alert = self.driver.switch_to.alert
                print(f"  📢 Alert detectado: {alert.text}")
                alert.accept()
                time.sleep(1)
            except:
                pass
            
            # Verificar se a página carregou
            titulo = self.wait_and_find(By.TAG_NAME, "h1")
            if titulo:
                self.log_test("PACIENTE", "Visualizar Consultas", "PASS", "- Página carregada")
                return True
            else:
                self.log_test("PACIENTE", "Visualizar Consultas", "FAIL", "- Página não carregou")
                return False
                
        except Exception as e:
            self.log_test("PACIENTE", "Visualizar Consultas", "FAIL", f"- Erro: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*60)
        print("🚀 INICIANDO TESTES AUTOMATIZADOS - CLÍNICA SAÚDE+")
        print("="*60)
        print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}\n")
        
        try:
            # Testes Admin
            self.test_admin_login()
            self.test_admin_listar_medicos()
            self.test_admin_cadastrar_medico()
            self.test_admin_listar_convenios()
            
            # Testes Médico
            self.test_medico_login()
            self.test_medico_visualizar_consultas()
            self.test_medico_horarios()
            
            # Testes Paciente
            timestamp = self.test_paciente_cadastro()
            self.test_paciente_login()  # Usa paciente existente
            self.test_paciente_agendar_consulta()
            self.test_paciente_visualizar_consultas()
            
        finally:
            self.print_summary()
            self.driver.quit()
            
    def print_summary(self):
        """Imprime sumário dos testes"""
        print("\n" + "="*60)
        print("📊 SUMÁRIO DOS TESTES")
        print("="*60)
        
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"\n✅ Testes Passados: {passed}/{total}")
        print(f"❌ Testes Falhados: {failed}/{total}")
        print(f"⚠️  Avisos: {warnings}/{total}")
        
        if failed > 0:
            print("\n❌ Testes que falharam:")
            for r in self.test_results:
                if r["status"] == "FAIL":
                    print(f"  - [{r['module']}] {r['test']}: {r['message']}")
                    
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}%")
        print(f"🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*60)
        
        return success_rate >= 80  # 80% de sucesso mínimo

if __name__ == "__main__":
    tester = ClinicaTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
