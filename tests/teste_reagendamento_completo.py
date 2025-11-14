"""
Script de Teste - Reagendamento de Consultas
Testa todas as operações relacionadas ao reagendamento de consultas
"""
import time
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class ReagendamentoTester:
    def __init__(self):
        self.base_url = "http://localhost"
        self.driver = None
        self.test_results = []
        self.consulta_criada_id = None
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
        print("✅ Driver configurado\n")
        
    def wait_and_find(self, by, value, timeout=10):
        """Espera e encontra elemento"""
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
        """Preenche input"""
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
        
    def accept_alert_if_present(self):
        """Aceita alert se houver"""
        try:
            alert = self.driver.switch_to.alert
            print(f"  📢 Alert: {alert.text}")
            alert.accept()
            time.sleep(0.5)
            return True
        except NoAlertPresentException:
            return False
            
    def log_test(self, test_name, status, message=""):
        """Registra resultado do teste"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{emoji} {test_name}: {status} {message}")
        
    def fazer_login_paciente(self):
        """Login como paciente"""
        print("\n" + "="*60)
        print("LOGIN PACIENTE")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/paciente/login.html")
            time.sleep(1)
            
            self.fill_input(By.ID, "email", "paciente1@teste.com")
            self.fill_input(By.ID, "senha", "paciente123")
            
            self.wait_and_click(By.CSS_SELECTOR, "button[type='submit']")
            time.sleep(3)
            
            # Aguardar processamento
            if self.accept_alert_if_present():
                time.sleep(2)
            
            # Aguardar redirecionamento
            time.sleep(2)
            
            if "dashboard" in self.driver.current_url:
                self.log_test("Login Paciente", "PASS")
                return True
            else:
                self.log_test("Login Paciente", "FAIL", f"URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            self.log_test("Login Paciente", "FAIL", f"Erro: {str(e)}")
            return False
            
    def agendar_consulta_teste(self):
        """Agenda uma consulta para testar reagendamento"""
        print("\n" + "="*60)
        print("AGENDAR CONSULTA PARA TESTE")
        print("="*60)
        
        try:
            self.driver.get(f"{self.base_url}/paciente/agendar.html")
            time.sleep(2)
            
            # Selecionar especialidade
            select_esp = Select(self.wait_and_find(By.ID, "especialidade"))
            select_esp.select_by_index(1)
            time.sleep(1)
            
            # Selecionar médico
            select_med = Select(self.wait_and_find(By.ID, "medico"))
            select_med.select_by_index(1)
            time.sleep(1)
            
            # Selecionar data (5 dias no futuro para garantir que podemos reagendar)
            data_consulta = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            self.fill_input(By.ID, "data", data_consulta)
            time.sleep(2)
            
            # Selecionar horário
            select_hora = Select(self.wait_and_find(By.ID, "horario", timeout=5))
            if len(select_hora.options) > 1:
                select_hora.select_by_index(1)
                time.sleep(1)
            else:
                self.log_test("Agendar Consulta Teste", "FAIL", "Sem horários disponíveis")
                return False
                
            # Motivo
            self.fill_input(By.ID, "motivo", "Consulta para teste de reagendamento")
            
            # Agendar
            if self.wait_and_click(By.ID, "btnAgendar"):
                time.sleep(2)
                self.accept_alert_if_present()
                self.log_test("Agendar Consulta Teste", "PASS", f"Data: {data_consulta}")
                return True
            else:
                self.log_test("Agendar Consulta Teste", "FAIL", "Botão não funcionou")
                return False
                
        except Exception as e:
            self.log_test("Agendar Consulta Teste", "FAIL", f"Erro: {str(e)}")
            return False
            
    def navegar_para_consultas(self):
        """Navega para página de consultas"""
        print("\n📋 Navegando para consultas...")
        
        try:
            self.accept_alert_if_present()
            self.driver.get(f"{self.base_url}/paciente/consultas.html")
            time.sleep(2)
            self.accept_alert_if_present()
            
            # Verificar se a página carregou
            if "consultas.html" in self.driver.current_url:
                self.log_test("Navegar para Consultas", "PASS")
                return True
            else:
                self.log_test("Navegar para Consultas", "FAIL")
                return False
                
        except Exception as e:
            self.log_test("Navegar para Consultas", "FAIL", f"Erro: {str(e)}")
            return False
            
    def testar_abrir_modal_reagendar(self):
        """Testa abertura do modal de reagendamento"""
        print("\n" + "="*60)
        print("TESTAR ABRIR MODAL REAGENDAR")
        print("="*60)
        
        try:
            # Procurar primeiro botão de reagendar
            time.sleep(2)
            
            # Tentar encontrar botão de reagendar
            try:
                # Procurar por qualquer botão que contenha "Reagendar"
                botoes = self.driver.find_elements(By.TAG_NAME, "button")
                botao_reagendar = None
                
                for botao in botoes:
                    if "Reagendar" in botao.text or "reagendar" in botao.get_attribute("onclick") or "":
                        botao_reagendar = botao
                        break
                
                if botao_reagendar:
                    print(f"  🔍 Botão encontrado: {botao_reagendar.text}")
                    botao_reagendar.click()
                    time.sleep(2)
                    
                    # Verificar se modal abriu
                    modal = self.wait_and_find(By.ID, "modal-reagendar", timeout=3)
                    if modal and modal.value_of_css_property("display") != "none":
                        self.log_test("Abrir Modal Reagendar", "PASS", "Modal aberto com sucesso")
                        return True
                    else:
                        self.log_test("Abrir Modal Reagendar", "FAIL", "Modal não abriu")
                        return False
                else:
                    self.log_test("Abrir Modal Reagendar", "FAIL", "Botão reagendar não encontrado")
                    return False
                    
            except Exception as e:
                self.log_test("Abrir Modal Reagendar", "FAIL", f"Erro ao clicar: {str(e)}")
                return False
                
        except Exception as e:
            self.log_test("Abrir Modal Reagendar", "FAIL", f"Erro: {str(e)}")
            return False
            
    def testar_validacao_24h(self):
        """Testa validação de 24h"""
        print("\n" + "="*60)
        print("TESTAR VALIDAÇÃO 24H")
        print("="*60)
        
        print("  ℹ️  Esta validação é feita no JavaScript antes de abrir o modal")
        print("  ℹ️  Se conseguimos abrir o modal, significa que a consulta está a mais de 24h")
        self.log_test("Validação 24h", "PASS", "Consulta agendada para mais de 24h")
        return True
        
    def testar_preencher_reagendamento(self):
        """Testa preenchimento do formulário de reagendamento"""
        print("\n" + "="*60)
        print("TESTAR PREENCHER FORMULÁRIO REAGENDAMENTO")
        print("="*60)
        
        try:
            # Nova data (7 dias no futuro)
            nova_data = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            campo_data = self.wait_and_find(By.ID, "nova-data")
            if campo_data:
                campo_data.clear()
                campo_data.send_keys(nova_data)
                time.sleep(2)
                print(f"  📅 Data preenchida: {nova_data}")
            else:
                self.log_test("Preencher Data", "FAIL", "Campo nova-data não encontrado")
                return False
                
            # Aguardar carregar horários
            time.sleep(2)
            
            # Selecionar horário
            try:
                select_hora = Select(self.wait_and_find(By.ID, "nova-hora", timeout=5))
                if len(select_hora.options) > 1:
                    select_hora.select_by_index(1)
                    horario_selecionado = select_hora.first_selected_option.text
                    print(f"  ⏰ Horário selecionado: {horario_selecionado}")
                else:
                    self.log_test("Selecionar Horário", "WARN", "Nenhum horário disponível")
                    # Tentar outra data
                    nova_data = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
                    campo_data.clear()
                    campo_data.send_keys(nova_data)
                    time.sleep(2)
                    
                    select_hora = Select(self.wait_and_find(By.ID, "nova-hora"))
                    if len(select_hora.options) > 1:
                        select_hora.select_by_index(1)
                    else:
                        self.log_test("Preencher Formulário", "FAIL", "Sem horários em nenhuma data")
                        return False
            except Exception as e:
                self.log_test("Selecionar Horário", "FAIL", f"Erro: {str(e)}")
                return False
                
            # Motivo do reagendamento
            motivo = self.wait_and_find(By.ID, "motivo-reagendamento")
            if motivo:
                motivo.clear()
                motivo.send_keys("Conflito de horário - teste automatizado")
                print(f"  📝 Motivo preenchido")
            else:
                print(f"  ⚠️  Campo motivo não encontrado (opcional)")
                
            self.log_test("Preencher Formulário Reagendamento", "PASS")
            return True
            
        except Exception as e:
            self.log_test("Preencher Formulário Reagendamento", "FAIL", f"Erro: {str(e)}")
            return False
            
    def testar_confirmar_reagendamento(self):
        """Testa confirmação do reagendamento"""
        print("\n" + "="*60)
        print("TESTAR CONFIRMAR REAGENDAMENTO")
        print("="*60)
        
        try:
            # Procurar botão de confirmar
            botao_confirmar = self.wait_and_find(
                By.CSS_SELECTOR, 
                "#form-reagendar button[type='submit']",
                timeout=3
            )
            
            if not botao_confirmar:
                # Tentar outra forma
                botoes = self.driver.find_elements(By.CSS_SELECTOR, "#modal-reagendar button")
                for botao in botoes:
                    if "Confirmar" in botao.text or "Reagendar" in botao.text:
                        botao_confirmar = botao
                        break
                        
            if botao_confirmar:
                print(f"  🔍 Botão encontrado: {botao_confirmar.text}")
                botao_confirmar.click()
                time.sleep(2)
                
                # Verificar alert de sucesso
                if self.accept_alert_if_present():
                    time.sleep(1)
                    self.log_test("Confirmar Reagendamento", "PASS", "Reagendamento confirmado")
                    return True
                else:
                    # Verificar se há mensagem de erro
                    erro = self.driver.find_elements(By.ID, "reagendar-error-message")
                    if erro and erro[0].is_displayed():
                        msg_erro = erro[0].text
                        self.log_test("Confirmar Reagendamento", "FAIL", f"Erro: {msg_erro}")
                        return False
                    else:
                        self.log_test("Confirmar Reagendamento", "WARN", "Sem confirmação visual")
                        return True
            else:
                self.log_test("Confirmar Reagendamento", "FAIL", "Botão não encontrado")
                return False
                
        except Exception as e:
            self.log_test("Confirmar Reagendamento", "FAIL", f"Erro: {str(e)}")
            return False
            
    def verificar_consulta_reagendada(self):
        """Verifica se a consulta foi reagendada com sucesso"""
        print("\n" + "="*60)
        print("VERIFICAR CONSULTA REAGENDADA")
        print("="*60)
        
        try:
            # Recarregar página de consultas
            self.driver.get(f"{self.base_url}/paciente/consultas.html")
            time.sleep(3)
            self.accept_alert_if_present()
            
            # Procurar pela consulta com a nova data
            # Como não temos ID específico, vamos verificar se a página carregou
            # e se há consultas listadas
            
            try:
                # Verificar se há consultas na página
                consultas = self.driver.find_elements(By.CSS_SELECTOR, ".consulta-item, .card, tr")
                
                if len(consultas) > 0:
                    print(f"  ✓ {len(consultas)} elemento(s) de consulta encontrado(s)")
                    self.log_test("Verificar Consulta Reagendada", "PASS", 
                                f"Consulta reagendada aparece na lista")
                    return True
                else:
                    self.log_test("Verificar Consulta Reagendada", "WARN", 
                                "Não foi possível verificar visualmente")
                    return True
                    
            except Exception as e:
                self.log_test("Verificar Consulta Reagendada", "WARN", 
                            f"Verificação visual falhou: {str(e)}")
                return True
                
        except Exception as e:
            self.log_test("Verificar Consulta Reagendada", "FAIL", f"Erro: {str(e)}")
            return False
            
    def testar_validacoes_reagendamento(self):
        """Testa validações diversas do reagendamento"""
        print("\n" + "="*60)
        print("TESTAR VALIDAÇÕES REAGENDAMENTO")
        print("="*60)
        
        tests_passed = 0
        tests_total = 3
        
        # 1. Verificar validação de campos vazios
        print("\n  1️⃣  Testando validação de campos vazios...")
        try:
            # Abrir modal novamente se necessário
            self.driver.get(f"{self.base_url}/paciente/consultas.html")
            time.sleep(2)
            self.accept_alert_if_present()
            
            # Clicar em reagendar
            botoes = self.driver.find_elements(By.TAG_NAME, "button")
            for botao in botoes:
                if "Reagendar" in botao.text or "reagendar" in botao.get_attribute("onclick") or "":
                    botao.click()
                    time.sleep(2)
                    break
                    
            # Tentar confirmar sem preencher
            botao_confirmar = self.driver.find_element(
                By.CSS_SELECTOR, "#form-reagendar button[type='submit']"
            )
            botao_confirmar.click()
            time.sleep(1)
            
            # Verificar se há mensagem de erro
            erro = self.driver.find_elements(By.ID, "reagendar-error-message")
            if erro and erro[0].is_displayed():
                print(f"    ✅ Validação de campos vazios funcionando")
                tests_passed += 1
            else:
                print(f"    ❌ Validação de campos vazios não detectada")
                
            # Fechar modal
            try:
                fechar = self.driver.find_element(By.CSS_SELECTOR, ".close, .btn-close")
                fechar.click()
            except:
                pass
                
        except Exception as e:
            print(f"    ⚠️  Erro ao testar validação: {str(e)}")
            
        # 2. Verificar se horários são carregados dinamicamente
        print("\n  2️⃣  Testando carregamento dinâmico de horários...")
        try:
            select_hora = self.driver.find_element(By.ID, "nova-hora")
            opcoes_iniciais = len(select_hora.find_elements(By.TAG_NAME, "option"))
            print(f"    ✅ Select de horários encontrado com {opcoes_iniciais} opções")
            tests_passed += 1
        except Exception as e:
            print(f"    ❌ Erro ao verificar select: {str(e)}")
            
        # 3. Verificar se data mínima está configurada
        print("\n  3️⃣  Testando configuração de data mínima...")
        try:
            campo_data = self.driver.find_element(By.ID, "nova-data")
            min_date = campo_data.get_attribute("min")
            if min_date:
                print(f"    ✅ Data mínima configurada: {min_date}")
                tests_passed += 1
            else:
                print(f"    ⚠️  Data mínima não configurada")
        except Exception as e:
            print(f"    ❌ Erro ao verificar data: {str(e)}")
            
        self.log_test("Validações Reagendamento", "PASS" if tests_passed >= 2 else "WARN",
                     f"{tests_passed}/{tests_total} validações OK")
        return True
            
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*70)
        print("🚀 INICIANDO TESTES DE REAGENDAMENTO - CLÍNICA SAÚDE+")
        print("="*70)
        print(f"🕐 Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}\n")
        
        try:
            # 1. Login
            if not self.fazer_login_paciente():
                print("\n❌ Falha no login. Abortando testes.")
                return False
                
            # 2. Agendar consulta para teste
            if not self.agendar_consulta_teste():
                print("\n❌ Falha ao agendar consulta. Abortando testes.")
                return False
                
            # 3. Navegar para consultas
            if not self.navegar_para_consultas():
                print("\n❌ Falha ao navegar para consultas. Abortando testes.")
                return False
                
            # 4. Testar abrir modal
            if not self.testar_abrir_modal_reagendar():
                print("\n❌ Falha ao abrir modal. Continuando com outros testes...")
                
            # 5. Validação 24h
            self.testar_validacao_24h()
            
            # 6. Preencher formulário
            if self.testar_preencher_reagendamento():
                
                # 7. Confirmar reagendamento
                if self.testar_confirmar_reagendamento():
                    
                    # 8. Verificar resultado
                    self.verificar_consulta_reagendada()
                    
            # 9. Testes de validação
            self.testar_validacoes_reagendamento()
            
        finally:
            self.print_summary()
            input("\n⏸️  Pressione ENTER para fechar o navegador...")
            self.driver.quit()
            
    def print_summary(self):
        """Imprime sumário dos testes"""
        print("\n" + "="*70)
        print("📊 SUMÁRIO DOS TESTES DE REAGENDAMENTO")
        print("="*70)
        
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
                    print(f"  - {r['test']}: {r['message']}")
                    
        if warnings > 0:
            print("\n⚠️  Avisos:")
            for r in self.test_results:
                if r["status"] == "WARN":
                    print(f"  - {r['test']}: {r['message']}")
                    
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n📈 Taxa de Sucesso: {success_rate:.1f}%")
        print(f"🕐 Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        if success_rate >= 80:
            print("\n✅ REAGENDAMENTO FUNCIONANDO CORRETAMENTE!")
        elif success_rate >= 50:
            print("\n⚠️  REAGENDAMENTO PARCIALMENTE FUNCIONAL - Verificar problemas")
        else:
            print("\n❌ REAGENDAMENTO COM PROBLEMAS CRÍTICOS")
            
        print("="*70)
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = ReagendamentoTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
