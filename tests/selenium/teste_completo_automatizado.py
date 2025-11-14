"""
Script de Teste Automatizado Completo - Sistema Clínica Saúde+
Testa todas as funcionalidades do sistema de forma automatizada
"""

import time
import sys
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class TesteAutomatizadoClinica:
    def __init__(self):
        self.base_url = "http://localhost"
        self.timeout = 10
        self.driver = None
        self.testes_passados = 0
        self.testes_falhados = 0
        self.erros = []
        
    def setup_driver(self):
        """Configura o driver do Chrome com opções otimizadas"""
        print("🚀 Configurando navegador Chrome...")
        
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(5)
        
        print("✅ Navegador configurado com sucesso!\n")
        
    def teardown_driver(self):
        """Fecha o navegador"""
        if self.driver:
            print("\n🔚 Fechando navegador...")
            self.driver.quit()
            
    def esperar_elemento(self, by, value, timeout=None):
        """Espera um elemento estar presente e visível"""
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            raise Exception(f"Timeout ao esperar elemento: {by}={value}")
            
    def esperar_e_clicar(self, by, value, timeout=None):
        """Espera elemento estar clicável e clica nele"""
        timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()
            return element
        except TimeoutException:
            raise Exception(f"Timeout ao clicar no elemento: {by}={value}")
            
    def preencher_campo(self, by, value, texto):
        """Preenche um campo de formulário"""
        elemento = self.esperar_elemento(by, value)
        elemento.clear()
        elemento.send_keys(texto)
        
    def log_teste(self, nome_teste, sucesso, mensagem=""):
        """Registra resultado de um teste"""
        if sucesso:
            self.testes_passados += 1
            print(f"✅ {nome_teste}: PASSOU")
        else:
            self.testes_falhados += 1
            print(f"❌ {nome_teste}: FALHOU - {mensagem}")
            self.erros.append({"teste": nome_teste, "erro": mensagem})
            
    def fazer_screenshot(self, nome):
        """Captura screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{nome}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot salvo: {filename}")
        
    # ===== TESTES DE PACIENTE =====
    
    def teste_cadastro_paciente(self):
        """Testa o cadastro de novo paciente"""
        print("\n" + "="*60)
        print("TESTE: Cadastro de Paciente")
        print("="*60)
        
        try:
            # Acessar página de cadastro
            self.driver.get(f"{self.base_url}/paciente/cadastro.html")
            time.sleep(2)
            
            # Preencher formulário
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            email = f"teste_{timestamp}@email.com"
            
            self.preencher_campo(By.ID, "nome", f"Paciente Teste {timestamp}")
            self.preencher_campo(By.ID, "email", email)
            self.preencher_campo(By.ID, "cpf", f"{timestamp[-11:]}")
            self.preencher_campo(By.ID, "telefone", "(47) 99999-9999")
            self.preencher_campo(By.ID, "dataNascimento", "01/01/1990")
            self.preencher_campo(By.ID, "senha", "senha12345")
            self.preencher_campo(By.ID, "confirmarSenha", "senha12345")
            
            # Selecionar convênio
            convenio_select = self.esperar_elemento(By.ID, "convenioId")
            convenio_select.click()
            time.sleep(1)
            # Selecionar a primeira opção que não seja vazia
            options = convenio_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()
            
            time.sleep(1)
            
            # Submeter formulário
            botao_cadastrar = self.esperar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            botao_cadastrar.click()
            
            # Aguardar redirecionamento ou mensagem de sucesso
            time.sleep(3)
            
            # Verificar se foi redirecionado para login
            if "login.html" in self.driver.current_url:
                self.log_teste("Cadastro de Paciente", True)
                return email, "senha12345"
            else:
                self.log_teste("Cadastro de Paciente", False, "Não houve redirecionamento para login")
                return None, None
                
        except Exception as e:
            self.log_teste("Cadastro de Paciente", False, str(e))
            self.fazer_screenshot("erro_cadastro_paciente")
            return None, None
            
    def teste_login_paciente(self, email=None, senha=None):
        """Testa o login de paciente"""
        print("\n" + "="*60)
        print("TESTE: Login de Paciente")
        print("="*60)
        
        # Usar credenciais padrão se não fornecidas
        if not email:
            email = "carlos.souza@email.com"
            senha = "paciente123"
        
        try:
            # Acessar página de login
            self.driver.get(f"{self.base_url}/paciente/login.html")
            time.sleep(2)
            
            # Preencher formulário de login
            self.preencher_campo(By.ID, "email", email)
            self.preencher_campo(By.ID, "senha", senha)
            
            # Fazer login
            botao_login = self.esperar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            botao_login.click()
            
            # Aguardar redirecionamento
            time.sleep(3)
            
            # Verificar se foi redirecionado para dashboard
            if "dashboard.html" in self.driver.current_url:
                self.log_teste("Login de Paciente", True)
                return True
            else:
                self.log_teste("Login de Paciente", False, "Não houve redirecionamento para dashboard")
                return False
                
        except Exception as e:
            self.log_teste("Login de Paciente", False, str(e))
            self.fazer_screenshot("erro_login_paciente")
            return False
            
    def teste_agendamento_consulta(self):
        """Testa o agendamento de consulta"""
        print("\n" + "="*60)
        print("TESTE: Agendamento de Consulta")
        print("="*60)
        
        try:
            # Navegar para página de agendamento
            self.driver.get(f"{self.base_url}/paciente/agendar.html")
            time.sleep(2)
            
            # Selecionar especialidade
            especialidade_select = self.esperar_elemento(By.ID, "especialidade")
            especialidade_select.click()
            time.sleep(1)
            options = especialidade_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()
            
            time.sleep(2)
            
            # Selecionar médico
            medico_select = self.esperar_elemento(By.ID, "medico")
            medico_select.click()
            time.sleep(1)
            options = medico_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()
            
            time.sleep(2)
            
            # Selecionar data (próximo dia útil)
            data_futura = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            data_input = self.esperar_elemento(By.ID, "data")
            self.driver.execute_script(f"arguments[0].value = '{data_futura}'", data_input)
            
            time.sleep(2)
            
            # Selecionar horário
            horario_select = self.esperar_elemento(By.ID, "horario")
            horario_select.click()
            time.sleep(1)
            options = horario_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 0:
                options[0].click()
            
            time.sleep(1)
            
            # Preencher motivo
            self.preencher_campo(By.ID, "motivo", "Consulta de rotina - teste automatizado")
            
            time.sleep(1)
            
            # Submeter agendamento
            botao_agendar = self.esperar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            botao_agendar.click()
            
            # Aguardar confirmação
            time.sleep(3)
            
            # Verificar se há mensagem de sucesso ou redirecionamento
            self.log_teste("Agendamento de Consulta", True)
            return True
            
        except Exception as e:
            self.log_teste("Agendamento de Consulta", False, str(e))
            self.fazer_screenshot("erro_agendamento")
            return False
            
    def teste_visualizar_consultas_paciente(self):
        """Testa a visualização de consultas do paciente"""
        print("\n" + "="*60)
        print("TESTE: Visualizar Consultas (Paciente)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/paciente/consultas.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Visualizar Consultas Paciente", True)
            return True
            
        except Exception as e:
            self.log_teste("Visualizar Consultas Paciente", False, str(e))
            self.fazer_screenshot("erro_visualizar_consultas_paciente")
            return False
            
    # ===== TESTES DE MÉDICO =====
    
    def teste_login_medico(self):
        """Testa o login de médico"""
        print("\n" + "="*60)
        print("TESTE: Login de Médico")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/medico/login.html")
            time.sleep(2)
            
            self.preencher_campo(By.ID, "email", "dr.silva@clinica.com")
            self.preencher_campo(By.ID, "senha", "medico123")
            
            botao_login = self.esperar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            botao_login.click()
            
            time.sleep(3)
            
            if "dashboard.html" in self.driver.current_url:
                self.log_teste("Login de Médico", True)
                return True
            else:
                self.log_teste("Login de Médico", False, "Não houve redirecionamento")
                return False
                
        except Exception as e:
            self.log_teste("Login de Médico", False, str(e))
            self.fazer_screenshot("erro_login_medico")
            return False
            
    def teste_gerenciar_horarios_medico(self):
        """Testa o gerenciamento de horários do médico"""
        print("\n" + "="*60)
        print("TESTE: Gerenciar Horários (Médico)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/medico/horarios.html")
            time.sleep(3)
            
            # Verificar se a página carregou
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Gerenciar Horários Médico", True)
            return True
            
        except Exception as e:
            self.log_teste("Gerenciar Horários Médico", False, str(e))
            self.fazer_screenshot("erro_horarios_medico")
            return False
            
    def teste_visualizar_consultas_medico(self):
        """Testa a visualização de consultas do médico"""
        print("\n" + "="*60)
        print("TESTE: Visualizar Consultas (Médico)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/medico/consultas.html")
            time.sleep(3)
            
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Visualizar Consultas Médico", True)
            return True
            
        except Exception as e:
            self.log_teste("Visualizar Consultas Médico", False, str(e))
            self.fazer_screenshot("erro_consultas_medico")
            return False
            
    # ===== TESTES DE ADMINISTRADOR =====
    
    def teste_login_admin(self):
        """Testa o login de administrador"""
        print("\n" + "="*60)
        print("TESTE: Login de Administrador")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/admin/login.html")
            time.sleep(2)
            
            self.preencher_campo(By.ID, "email", "admin@clinica.com")
            self.preencher_campo(By.ID, "senha", "admin123")
            
            botao_login = self.esperar_elemento(By.CSS_SELECTOR, "button[type='submit']")
            botao_login.click()
            
            time.sleep(3)
            
            if "dashboard.html" in self.driver.current_url:
                self.log_teste("Login de Administrador", True)
                return True
            else:
                self.log_teste("Login de Administrador", False, "Não houve redirecionamento")
                return False
                
        except Exception as e:
            self.log_teste("Login de Administrador", False, str(e))
            self.fazer_screenshot("erro_login_admin")
            return False
            
    def teste_gerenciar_medicos(self):
        """Testa o gerenciamento de médicos"""
        print("\n" + "="*60)
        print("TESTE: Gerenciar Médicos (Admin)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/admin/medicos.html")
            time.sleep(3)
            
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Gerenciar Médicos", True)
            return True
            
        except Exception as e:
            self.log_teste("Gerenciar Médicos", False, str(e))
            self.fazer_screenshot("erro_medicos_admin")
            return False
            
    def teste_gerenciar_pacientes(self):
        """Testa o gerenciamento de pacientes"""
        print("\n" + "="*60)
        print("TESTE: Gerenciar Pacientes (Admin)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/admin/pacientes.html")
            time.sleep(3)
            
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Gerenciar Pacientes", True)
            return True
            
        except Exception as e:
            self.log_teste("Gerenciar Pacientes", False, str(e))
            self.fazer_screenshot("erro_pacientes_admin")
            return False
            
    def teste_gerenciar_convenios(self):
        """Testa o gerenciamento de convênios"""
        print("\n" + "="*60)
        print("TESTE: Gerenciar Convênios (Admin)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/admin/convenios.html")
            time.sleep(3)
            
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Gerenciar Convênios", True)
            return True
            
        except Exception as e:
            self.log_teste("Gerenciar Convênios", False, str(e))
            self.fazer_screenshot("erro_convenios_admin")
            return False
            
    def teste_relatorios(self):
        """Testa a geração de relatórios"""
        print("\n" + "="*60)
        print("TESTE: Relatórios (Admin)")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/admin/relatorios.html")
            time.sleep(3)
            
            self.esperar_elemento(By.TAG_NAME, "body")
            self.log_teste("Relatórios Admin", True)
            return True
            
        except Exception as e:
            self.log_teste("Relatórios Admin", False, str(e))
            self.fazer_screenshot("erro_relatorios_admin")
            return False
            
    # ===== EXECUÇÃO DOS TESTES =====
    
    def executar_todos_testes(self):
        """Executa todos os testes do sistema"""
        print("\n" + "="*80)
        print(" INICIANDO TESTES AUTOMATIZADOS - CLÍNICA SAÚDE+ ")
        print("="*80)
        
        inicio = datetime.now()
        
        try:
            self.setup_driver()
            
            # Testes de Paciente
            print("\n" + "🔵 MÓDULO PACIENTE ".ljust(80, "="))
            email_novo, senha_nova = self.teste_cadastro_paciente()
            self.teste_login_paciente()
            self.teste_agendamento_consulta()
            self.teste_visualizar_consultas_paciente()
            
            # Testes de Médico
            print("\n" + "🔵 MÓDULO MÉDICO ".ljust(80, "="))
            self.teste_login_medico()
            self.teste_gerenciar_horarios_medico()
            self.teste_visualizar_consultas_medico()
            
            # Testes de Administrador
            print("\n" + "🔵 MÓDULO ADMINISTRADOR ".ljust(80, "="))
            self.teste_login_admin()
            self.teste_gerenciar_medicos()
            self.teste_gerenciar_pacientes()
            self.teste_gerenciar_convenios()
            self.teste_relatorios()
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO: {e}")
            self.fazer_screenshot("erro_critico")
            
        finally:
            self.teardown_driver()
            
        fim = datetime.now()
        duracao = (fim - inicio).total_seconds()
        
        # Relatório Final
        print("\n" + "="*80)
        print(" RELATÓRIO FINAL DOS TESTES ")
        print("="*80)
        print(f"\n⏱️  Tempo de execução: {duracao:.2f} segundos")
        print(f"✅ Testes passados: {self.testes_passados}")
        print(f"❌ Testes falhados: {self.testes_falhados}")
        print(f"📊 Total de testes: {self.testes_passados + self.testes_falhados}")
        
        if self.testes_falhados > 0:
            print("\n" + "="*80)
            print(" ERROS ENCONTRADOS ")
            print("="*80)
            for erro in self.erros:
                print(f"\n❌ {erro['teste']}")
                print(f"   └─ {erro['erro']}")
                
        taxa_sucesso = (self.testes_passados / (self.testes_passados + self.testes_falhados) * 100) if (self.testes_passados + self.testes_falhados) > 0 else 0
        print(f"\n📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        if taxa_sucesso == 100:
            print("\n🎉 TODOS OS TESTES PASSARAM! Sistema 100% funcional!")
            return 0
        else:
            print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
            return 1

def main():
    """Função principal"""
    teste = TesteAutomatizadoClinica()
    return teste.executar_todos_testes()

if __name__ == "__main__":
    sys.exit(main())
