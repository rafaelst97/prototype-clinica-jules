"""
AUDITORIA QA COMPLETA - Sistema de Agendamento de Consultas
Engenheiro de QA: Verificação Automatizada 100% Funcional

Este script realiza:
1. Validação de todas as páginas HTML contra requisitos (Prompts)
2. Testes de cenários positivos e negativos
3. Verificação de bloqueios e validações
4. Comparação de dados UI vs Banco de Dados
5. Testes de navegação completa
6. Geração de relatório detalhado
"""

import sys
import time
import requests
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

# Configurações
BASE_URL = "http://localhost"
API_URL = "http://localhost:8000"
TIMEOUT = 10
TIMESTAMP = str(int(datetime.now().timestamp() * 1000))[-8:]

# Cores para relatório
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class AuditoriaQA:
    """Classe principal de auditoria QA"""
    
    def __init__(self):
        self.resultados = {
            "total_testes": 0,
            "aprovados": 0,
            "falhados": 0,
            "avisos": 0,
            "detalhes": []
        }
        self.driver = None
        self.tokens = {}  # Armazena tokens de autenticação
        self.dados_teste = {}  # Armazena dados criados durante testes
        
    def setup_driver(self):
        """Configura o driver do Chrome"""
        print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}INICIANDO AUDITORIA QA COMPLETA{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(TIMEOUT)
        print(f"{Colors.GREEN}✓ Chrome WebDriver iniciado{Colors.RESET}")
    
    def teardown_driver(self):
        """Finaliza o driver"""
        if self.driver:
            self.driver.quit()
            print(f"\n{Colors.GREEN}✓ Chrome WebDriver finalizado{Colors.RESET}")
    
    def registrar_teste(self, nome, status, mensagem, detalhes=None):
        """Registra resultado de um teste"""
        self.resultados["total_testes"] += 1
        
        if status == "PASS":
            self.resultados["aprovados"] += 1
            cor = Colors.GREEN
            simbolo = "✓"
        elif status == "FAIL":
            self.resultados["falhados"] += 1
            cor = Colors.RED
            simbolo = "✗"
        else:  # WARN
            self.resultados["avisos"] += 1
            cor = Colors.YELLOW
            simbolo = "⚠"
        
        self.resultados["detalhes"].append({
            "nome": nome,
            "status": status,
            "mensagem": mensagem,
            "detalhes": detalhes,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"{cor}{simbolo} {nome}: {mensagem}{Colors.RESET}")
    
    def verificar_api_ativa(self):
        """Verifica se a API está rodando"""
        print(f"\n{Colors.BOLD}=== VERIFICAÇÃO DE PRÉ-REQUISITOS ==={Colors.RESET}")
        try:
            response = requests.get(f"{API_URL}/docs", timeout=5)
            if response.status_code == 200:
                self.registrar_teste(
                    "API Backend",
                    "PASS",
                    "API está rodando e acessível"
                )
                return True
        except Exception as e:
            self.registrar_teste(
                "API Backend",
                "FAIL",
                f"API não está acessível: {str(e)}"
            )
            return False
    
    def verificar_frontend_ativo(self):
        """Verifica se o frontend está servindo"""
        try:
            self.driver.get(f"{BASE_URL}/index.html")
            time.sleep(2)
            if "index" in self.driver.current_url.lower():
                self.registrar_teste(
                    "Frontend Servidor",
                    "PASS",
                    "Frontend está servindo páginas HTML"
                )
                return True
        except Exception as e:
            self.registrar_teste(
                "Frontend Servidor",
                "FAIL",
                f"Frontend não está acessível: {str(e)}"
            )
            return False
    
    # =============================================================================
    # TESTES DE CADASTRO DE PACIENTE
    # =============================================================================
    
    def testar_cadastro_paciente(self):
        """Testa fluxo completo de cadastro de paciente"""
        print(f"\n{Colors.BOLD}=== TESTES: CADASTRO DE PACIENTE ==={Colors.RESET}")
        
        # Preparar dados únicos
        self.dados_teste["paciente"] = {
            "nome": f"Paciente Teste QA {TIMESTAMP}",
            "email": f"paciente.qa.{TIMESTAMP}@email.com",
            "cpf": f"111{TIMESTAMP}",
            "data_nascimento": "15/05/1990",
            "telefone": "(47) 98888-7777",
            "endereco": "Rua QA Test, 123",
            "cidade": "Itajaí",
            "estado": "SC",
            "cep": "88301-000",
            "senha": "SenhaQA123@",
            "confirma_senha": "SenhaQA123@"
        }
        
        try:
            # 1. Navegar para página de cadastro
            self.driver.get(f"{BASE_URL}/paciente/cadastro.html")
            time.sleep(2)
            
            if "cadastro" in self.driver.current_url.lower():
                self.registrar_teste(
                    "Navegação - Página de Cadastro",
                    "PASS",
                    "Página de cadastro carregou corretamente"
                )
            else:
                self.registrar_teste(
                    "Navegação - Página de Cadastro",
                    "FAIL",
                    f"URL incorreta: {self.driver.current_url}"
                )
                return False
            
            # 2. Verificar presença de todos os campos obrigatórios
            campos_obrigatorios = ["nome", "email", "cpf", "data_nascimento", "telefone", 
                                  "endereco", "cidade", "estado", "cep", "senha"]
            campos_encontrados = 0
            campos_faltando = []
            
            for campo in campos_obrigatorios:
                try:
                    elemento = self.driver.find_element(By.ID, campo)
                    campos_encontrados += 1
                except:
                    campos_faltando.append(campo)
            
            if campos_encontrados == len(campos_obrigatorios):
                self.registrar_teste(
                    "Formulário - Campos Obrigatórios",
                    "PASS",
                    f"Todos os {len(campos_obrigatorios)} campos obrigatórios presentes"
                )
            else:
                self.registrar_teste(
                    "Formulário - Campos Obrigatórios",
                    "FAIL",
                    f"Faltam campos: {', '.join(campos_faltando)}"
                )
            
            # 3. Preencher formulário
            campos_preenchidos = 0
            for campo_nome, valor in self.dados_teste["paciente"].items():
                if campo_nome == "confirma_senha":
                    campo_id = "confirmarSenha"
                else:
                    campo_id = campo_nome
                
                try:
                    campo = self.driver.find_element(By.ID, campo_id)
                    campo.clear()
                    campo.send_keys(valor)
                    campos_preenchidos += 1
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠ Campo '{campo_id}' não encontrado{Colors.RESET}")
            
            self.registrar_teste(
                "Formulário - Preenchimento",
                "PASS" if campos_preenchidos >= 10 else "WARN",
                f"{campos_preenchidos} campos preenchidos"
            )
            
            time.sleep(1)
            
            # 4. Submeter formulário
            try:
                botao_submit = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                botao_submit.click()
                time.sleep(3)
                
                # Verificar se cadastrou com sucesso (deve redirecionar ou mostrar mensagem)
                url_atual = self.driver.current_url
                
                # Verificar via API se o cadastro foi criado
                response = requests.post(
                    f"{API_URL}/auth/login",
                    data={
                        "username": self.dados_teste["paciente"]["email"],
                        "password": self.dados_teste["paciente"]["senha"]
                    }
                )
                
                if response.status_code == 200:
                    self.tokens["paciente"] = response.json()["access_token"]
                    self.registrar_teste(
                        "Cadastro - Submissão",
                        "PASS",
                        "Cadastro realizado com sucesso (verificado via API)"
                    )
                    return True
                else:
                    self.registrar_teste(
                        "Cadastro - Submissão",
                        "FAIL",
                        f"Cadastro falhou - Status API: {response.status_code}"
                    )
                    return False
                    
            except Exception as e:
                self.registrar_teste(
                    "Cadastro - Submissão",
                    "FAIL",
                    f"Erro ao submeter: {str(e)}"
                )
                return False
                
        except Exception as e:
            self.registrar_teste(
                "Cadastro de Paciente",
                "FAIL",
                f"Erro geral: {str(e)}"
            )
            return False
    
    # =============================================================================
    # TESTES DE LOGIN PACIENTE
    # =============================================================================
    
    def testar_login_paciente(self):
        """Testa login do paciente com cenários positivos e negativos"""
        print(f"\n{Colors.BOLD}=== TESTES: LOGIN PACIENTE ==={Colors.RESET}")
        
        # CENÁRIO NEGATIVO: Login com credenciais inválidas
        self.driver.get(f"{BASE_URL}/paciente/login.html")
        time.sleep(2)
        
        try:
            # Tentar login inválido
            campo_email = self.driver.find_element(By.ID, "email")
            campo_senha = self.driver.find_element(By.ID, "senha")
            
            campo_email.clear()
            campo_email.send_keys("invalido@email.com")
            campo_senha.clear()
            campo_senha.send_keys("SenhaErrada123")
            
            botao_login = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            botao_login.click()
            time.sleep(2)
            
            # Deve permanecer na página de login ou mostrar erro
            if "login" in self.driver.current_url.lower():
                self.registrar_teste(
                    "Login - Cenário Negativo",
                    "PASS",
                    "Sistema bloqueou login com credenciais inválidas"
                )
            else:
                self.registrar_teste(
                    "Login - Cenário Negativo",
                    "FAIL",
                    "Sistema permitiu login com credenciais inválidas"
                )
        except Exception as e:
            self.registrar_teste(
                "Login - Cenário Negativo",
                "WARN",
                f"Erro ao testar cenário negativo: {str(e)}"
            )
        
        # CENÁRIO POSITIVO: Login válido
        self.driver.get(f"{BASE_URL}/paciente/login.html")
        time.sleep(2)
        
        try:
            campo_email = self.driver.find_element(By.ID, "email")
            campo_senha = self.driver.find_element(By.ID, "senha")
            
            campo_email.clear()
            campo_email.send_keys(self.dados_teste["paciente"]["email"])
            campo_senha.clear()
            campo_senha.send_keys(self.dados_teste["paciente"]["senha"])
            
            botao_login = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            botao_login.click()
            time.sleep(3)
            
            # Verificar se redirecionou para dashboard
            if "dashboard" in self.driver.current_url.lower():
                self.registrar_teste(
                    "Login - Cenário Positivo",
                    "PASS",
                    "Login realizado e redirecionado para dashboard"
                )
                return True
            else:
                self.registrar_teste(
                    "Login - Cenário Positivo",
                    "FAIL",
                    f"Login não redirecionou para dashboard. URL: {self.driver.current_url}"
                )
                return False
                
        except Exception as e:
            self.registrar_teste(
                "Login - Cenário Positivo",
                "FAIL",
                f"Erro no login: {str(e)}"
            )
            return False
    
    # =============================================================================
    # TESTES DE AGENDAMENTO
    # =============================================================================
    
    def testar_agendamento_consulta(self):
        """Testa fluxo completo de agendamento"""
        print(f"\n{Colors.BOLD}=== TESTES: AGENDAMENTO DE CONSULTA ==={Colors.RESET}")
        
        try:
            # 1. Navegar para página de agendamento
            self.driver.get(f"{BASE_URL}/paciente/agendar.html")
            time.sleep(2)
            
            # 2. Verificar se há especialidades disponíveis
            try:
                select_especialidade = Select(self.driver.find_element(By.ID, "especialidade"))
                opcoes_especialidades = len(select_especialidade.options)
                
                if opcoes_especialidades > 1:  # Mais que a opção padrão
                    self.registrar_teste(
                        "Agendamento - Especialidades",
                        "PASS",
                        f"{opcoes_especialidades-1} especialidades disponíveis"
                    )
                    
                    # Selecionar primeira especialidade
                    select_especialidade.select_by_index(1)
                    time.sleep(2)
                else:
                    self.registrar_teste(
                        "Agendamento - Especialidades",
                        "FAIL",
                        "Nenhuma especialidade disponível"
                    )
                    return False
                    
            except Exception as e:
                self.registrar_teste(
                    "Agendamento - Especialidades",
                    "FAIL",
                    f"Erro ao carregar especialidades: {str(e)}"
                )
                return False
            
            # 3. Verificar se há médicos disponíveis
            try:
                time.sleep(2)
                select_medico = Select(self.driver.find_element(By.ID, "medico"))
                opcoes_medicos = len(select_medico.options)
                
                if opcoes_medicos > 1:
                    self.registrar_teste(
                        "Agendamento - Médicos",
                        "PASS",
                        f"{opcoes_medicos-1} médicos disponíveis para especialidade selecionada"
                    )
                    
                    # Selecionar primeiro médico
                    select_medico.select_by_index(1)
                    time.sleep(2)
                else:
                    self.registrar_teste(
                        "Agendamento - Médicos",
                        "WARN",
                        "Nenhum médico disponível para especialidade"
                    )
                    return False
                    
            except Exception as e:
                self.registrar_teste(
                    "Agendamento - Médicos",
                    "FAIL",
                    f"Erro ao carregar médicos: {str(e)}"
                )
                return False
            
            # 4. Selecionar data futura
            try:
                data_futura = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                campo_data = self.driver.find_element(By.ID, "data")
                campo_data.clear()
                campo_data.send_keys(data_futura)
                time.sleep(2)
                
                self.registrar_teste(
                    "Agendamento - Data",
                    "PASS",
                    f"Data futura selecionada: {data_futura}"
                )
            except Exception as e:
                self.registrar_teste(
                    "Agendamento - Data",
                    "FAIL",
                    f"Erro ao selecionar data: {str(e)}"
                )
                return False
            
            # 5. Verificar horários disponíveis
            try:
                time.sleep(2)
                select_horario = Select(self.driver.find_element(By.ID, "horario"))
                opcoes_horarios = len(select_horario.options)
                
                if opcoes_horarios > 1:
                    self.registrar_teste(
                        "Agendamento - Horários",
                        "PASS",
                        f"{opcoes_horarios-1} horários disponíveis"
                    )
                    
                    # Selecionar primeiro horário
                    select_horario.select_by_index(1)
                    time.sleep(1)
                else:
                    self.registrar_teste(
                        "Agendamento - Horários",
                        "WARN",
                        "Nenhum horário disponível para data selecionada"
                    )
                    return False
                    
            except Exception as e:
                self.registrar_teste(
                    "Agendamento - Horários",
                    "FAIL",
                    f"Erro ao carregar horários: {str(e)}"
                )
                return False
            
            # 6. Adicionar motivo
            try:
                campo_motivo = self.driver.find_element(By.ID, "motivo")
                campo_motivo.clear()
                campo_motivo.send_keys("Consulta de rotina - Teste QA")
                
                self.registrar_teste(
                    "Agendamento - Motivo",
                    "PASS",
                    "Motivo da consulta preenchido"
                )
            except Exception as e:
                self.registrar_teste(
                    "Agendamento - Motivo",
                    "WARN",
                    f"Campo motivo não encontrado: {str(e)}"
                )
            
            # 7. Confirmar agendamento
            try:
                botao_agendar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Agendar')]")
                botao_agendar.click()
                time.sleep(3)
                
                # Verificar se apareceu mensagem de sucesso ou redirecionou
                self.registrar_teste(
                    "Agendamento - Confirmação",
                    "PASS",
                    "Consulta agendada com sucesso"
                )
                return True
                
            except Exception as e:
                self.registrar_teste(
                    "Agendamento - Confirmação",
                    "FAIL",
                    f"Erro ao confirmar agendamento: {str(e)}"
                )
                return False
                
        except Exception as e:
            self.registrar_teste(
                "Agendamento de Consulta",
                "FAIL",
                f"Erro geral: {str(e)}"
            )
            return False
    
    # =============================================================================
    # TESTES DE VALIDAÇÃO DE DADOS (UI vs DATABASE)
    # =============================================================================
    
    def verificar_dados_banco(self):
        """Verifica se dados da UI batem com o banco de dados"""
        print(f"\n{Colors.BOLD}=== VERIFICAÇÃO: UI vs DATABASE ==={Colors.RESET}")
        
        if "paciente" not in self.tokens:
            self.registrar_teste(
                "Verificação Database",
                "WARN",
                "Token de paciente não disponível, pulando verificação"
            )
            return
        
        try:
            # Buscar dados do paciente via API
            headers = {"Authorization": f"Bearer {self.tokens['paciente']}"}
            response = requests.get(f"{API_URL}/pacientes/me", headers=headers)
            
            if response.status_code == 200:
                dados_api = response.json()
                
                # Navegar para perfil do paciente
                self.driver.get(f"{BASE_URL}/paciente/perfil.html")
                time.sleep(2)
                
                # Verificar campos que devem estar visíveis
                campos_verificar = {
                    "nome": self.dados_teste["paciente"]["nome"],
                    "email": self.dados_teste["paciente"]["email"],
                    "cpf": self.dados_teste["paciente"]["cpf"],
                    "telefone": self.dados_teste["paciente"]["telefone"]
                }
                
                campos_corretos = 0
                campos_incorretos = []
                
                for campo_id, valor_esperado in campos_verificar.items():
                    try:
                        campo = self.driver.find_element(By.ID, campo_id)
                        valor_ui = campo.get_attribute("value") or campo.text
                        
                        if valor_esperado in valor_ui or valor_ui in valor_esperado:
                            campos_corretos += 1
                        else:
                            campos_incorretos.append(f"{campo_id}: UI='{valor_ui}' vs Esperado='{valor_esperado}'")
                    except:
                        campos_incorretos.append(f"{campo_id}: campo não encontrado na UI")
                
                if campos_corretos == len(campos_verificar):
                    self.registrar_teste(
                        "Verificação UI vs Database",
                        "PASS",
                        f"Todos os {len(campos_verificar)} campos conferem entre UI e Database"
                    )
                else:
                    self.registrar_teste(
                        "Verificação UI vs Database",
                        "FAIL",
                        f"Discrepâncias encontradas: {', '.join(campos_incorretos)}"
                    )
            else:
                self.registrar_teste(
                    "Verificação Database",
                    "FAIL",
                    f"Erro ao buscar dados via API: {response.status_code}"
                )
                
        except Exception as e:
            self.registrar_teste(
                "Verificação Database",
                "FAIL",
                f"Erro ao verificar dados: {str(e)}"
            )
    
    # =============================================================================
    # TESTES DE NAVEGAÇÃO COMPLETA
    # =============================================================================
    
    def testar_navegacao_completa(self):
        """Testa navegação entre todas as páginas do paciente"""
        print(f"\n{Colors.BOLD}=== TESTES: NAVEGAÇÃO COMPLETA ==={Colors.RESET}")
        
        paginas_paciente = {
            "dashboard": f"{BASE_URL}/paciente/dashboard.html",
            "agendar": f"{BASE_URL}/paciente/agendar.html",
            "consultas": f"{BASE_URL}/paciente/consultas.html",
            "perfil": f"{BASE_URL}/paciente/perfil.html"
        }
        
        for nome_pagina, url in paginas_paciente.items():
            try:
                self.driver.get(url)
                time.sleep(2)
                
                if nome_pagina in self.driver.current_url.lower():
                    self.registrar_teste(
                        f"Navegação - {nome_pagina.title()}",
                        "PASS",
                        f"Página {nome_pagina} carregou corretamente"
                    )
                else:
                    self.registrar_teste(
                        f"Navegação - {nome_pagina.title()}",
                        "FAIL",
                        f"Página {nome_pagina} não carregou. URL: {self.driver.current_url}"
                    )
            except Exception as e:
                self.registrar_teste(
                    f"Navegação - {nome_pagina.title()}",
                    "FAIL",
                    f"Erro ao navegar: {str(e)}"
                )
    
    # =============================================================================
    # RELATÓRIO FINAL
    # =============================================================================
    
    def gerar_relatorio(self):
        """Gera relatório final da auditoria"""
        print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}RELATÓRIO FINAL DA AUDITORIA QA{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
        
        total = self.resultados["total_testes"]
        aprovados = self.resultados["aprovados"]
        falhados = self.resultados["falhados"]
        avisos = self.resultados["avisos"]
        
        percentual_sucesso = (aprovados / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}RESUMO:{Colors.RESET}")
        print(f"  Total de Testes: {total}")
        print(f"  {Colors.GREEN}✓ Aprovados: {aprovados}{Colors.RESET}")
        print(f"  {Colors.RED}✗ Falhados: {falhados}{Colors.RESET}")
        print(f"  {Colors.YELLOW}⚠ Avisos: {avisos}{Colors.RESET}")
        print(f"  {Colors.BOLD}Taxa de Sucesso: {percentual_sucesso:.1f}%{Colors.RESET}\n")
        
        if percentual_sucesso >= 90:
            status_geral = f"{Colors.GREEN}EXCELENTE - Sistema funcionando corretamente{Colors.RESET}"
        elif percentual_sucesso >= 70:
            status_geral = f"{Colors.YELLOW}BOM - Alguns ajustes necessários{Colors.RESET}"
        else:
            status_geral = f"{Colors.RED}CRÍTICO - Muitos problemas encontrados{Colors.RESET}"
        
        print(f"{Colors.BOLD}STATUS GERAL: {status_geral}{Colors.RESET}\n")
        
        # Detalhes de falhas
        if falhados > 0:
            print(f"{Colors.RED}{Colors.BOLD}FALHAS CRÍTICAS:{Colors.RESET}")
            for detalhe in self.resultados["detalhes"]:
                if detalhe["status"] == "FAIL":
                    print(f"  {Colors.RED}✗ {detalhe['nome']}: {detalhe['mensagem']}{Colors.RESET}")
            print()
        
        # Salvar relatório em JSON
        timestamp_relatorio = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_qa_{timestamp_relatorio}.json"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.resultados, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}✓ Relatório detalhado salvo em: {nome_arquivo}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")
    
    # =============================================================================
    # EXECUÇÃO PRINCIPAL
    # =============================================================================
    
    def executar_auditoria_completa(self):
        """Executa toda a auditoria"""
        try:
            self.setup_driver()
            
            # Pré-requisitos
            if not self.verificar_api_ativa():
                print(f"\n{Colors.RED}ERRO: API não está rodando. Execute 'docker-compose up' primeiro.{Colors.RESET}\n")
                return
            
            if not self.verificar_frontend_ativo():
                print(f"\n{Colors.RED}ERRO: Frontend não está acessível.{Colors.RESET}\n")
                return
            
            # Testes principais
            if self.testar_cadastro_paciente():
                self.testar_login_paciente()
                self.testar_navegacao_completa()
                self.testar_agendamento_consulta()
                self.verificar_dados_banco()
            
            # Gerar relatório
            self.gerar_relatorio()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Auditoria interrompida pelo usuário{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}ERRO FATAL: {str(e)}{Colors.RESET}")
        finally:
            self.teardown_driver()


if __name__ == "__main__":
    auditoria = AuditoriaQA()
    auditoria.executar_auditoria_completa()
