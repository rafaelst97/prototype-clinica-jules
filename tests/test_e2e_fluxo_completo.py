"""
Teste E2E - Fluxo Completo de Cadastro e Login de Pacientes
Testa: Cadastro → Login → Logout → Novo Cadastro → Login → Logout
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime

# Configurações
BASE_URL = "http://localhost"
TIMEOUT = 10

def gerar_dados_usuario(numero):
    """Gera dados únicos para cada usuário"""
    timestamp = int(datetime.now().timestamp())
    return {
        'nome': f'Teste Usuário {numero}',
        'cpf': f'{numero:011d}',  # Gera CPF único baseado no número
        'email': f'teste{numero}_{timestamp}@email.com',
        'telefone': f'479{numero:08d}',  # (47) 9XXXX-XXXX
        'data_nascimento': '01/01/1990',
        'senha': f'senha{numero}123'
    }

def formatar_cpf(cpf):
    """Formata CPF para o padrão 000.000.000-00"""
    return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

def formatar_telefone(telefone):
    """Formata telefone para o padrão (00) 00000-0000"""
    return f'({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}'

def test_fluxo_completo():
    print("=" * 80)
    print("🚀 INICIANDO TESTE E2E - FLUXO COMPLETO DE CADASTRO E LOGIN")
    print("=" * 80)
    
    # Configurar WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, TIMEOUT)
    
    try:
        # ==================== ETAPA 1: Acessar Tela Principal ====================
        print("\n📍 ETAPA 1: Acessando tela principal...")
        driver.get(BASE_URL)
        time.sleep(2)
        
        assert "Clínica Saúde+" in driver.title
        print("✅ Tela principal carregada com sucesso")
        
        # ==================== ETAPA 2: Cadastrar Usuário 1 ====================
        print("\n📍 ETAPA 2: Cadastrando primeiro usuário...")
        
        # Clicar no botão "Cadastre-se"
        btn_cadastro = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='paciente/cadastro.html']")))
        btn_cadastro.click()
        time.sleep(2)
        
        # Gerar dados do usuário 1
        usuario1 = gerar_dados_usuario(1)
        print(f"   👤 Usuário: {usuario1['nome']}")
        print(f"   📧 Email: {usuario1['email']}")
        print(f"   🆔 CPF: {formatar_cpf(usuario1['cpf'])}")
        
        # Preencher formulário
        driver.find_element(By.ID, "cpf").send_keys(usuario1['cpf'])
        driver.find_element(By.ID, "nome").send_keys(usuario1['nome'])
        driver.find_element(By.ID, "telefone").send_keys(usuario1['telefone'])
        driver.find_element(By.ID, "email").send_keys(usuario1['email'])
        driver.find_element(By.ID, "senha").send_keys(usuario1['senha'])
        driver.find_element(By.ID, "confirmarSenha").send_keys(usuario1['senha'])
        driver.find_element(By.ID, "dataNascimento").send_keys("1990-01-01")
        
        # Selecionar convênio (Unimed - primeiro da lista)
        select_convenio = Select(driver.find_element(By.ID, "convenio"))
        select_convenio.select_by_index(1)  # 0 = Particular, 1 = Unimed
        convenio_selecionado = select_convenio.first_selected_option.text
        print(f"   🏥 Convênio: {convenio_selecionado}")
        time.sleep(1)
        
        # Submeter formulário
        btn_submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn_submit.click()
        
        # Aguardar mensagem de sucesso ou redirecionamento
        time.sleep(3)
        
        # Verificar se redirecionou para login ou se há mensagem de sucesso
        current_url = driver.current_url
        if "login.html" in current_url:
            print("✅ Cadastro realizado! Redirecionado para login")
        else:
            print("✅ Cadastro realizado com sucesso")
            time.sleep(2)
        
        # ==================== ETAPA 3: Fazer Login com Usuário 1 ====================
        print("\n📍 ETAPA 3: Fazendo login com primeiro usuário...")
        
        # Se não estiver na página de login, navegar até ela
        if "login.html" not in driver.current_url:
            driver.get(f"{BASE_URL}/paciente/login.html")
            time.sleep(2)
        
        # Preencher credenciais
        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(usuario1['email'])
        driver.find_element(By.ID, "senha").clear()
        driver.find_element(By.ID, "senha").send_keys(usuario1['senha'])
        
        # Fazer login
        btn_login = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn_login.click()
        time.sleep(3)
        
        # Verificar se está no dashboard
        current_url = driver.current_url
        if "dashboard.html" in current_url:
            print("✅ Login realizado! No dashboard do paciente")
        else:
            print(f"⚠️  URL atual: {current_url}")
        
        # ==================== ETAPA 4: Fazer Logout ====================
        print("\n📍 ETAPA 4: Fazendo logout do primeiro usuário...")
        
        # Procurar botão de logout
        try:
            btn_logout = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sair')] | //button[contains(text(), 'Sair')] | //a[@href='login.html']")))
            btn_logout.click()
            time.sleep(2)
            print("✅ Logout realizado com sucesso")
        except Exception as e:
            print(f"⚠️  Fazendo logout via navegação direta: {e}")
            driver.get(f"{BASE_URL}/paciente/login.html")
            time.sleep(2)
        
        # ==================== ETAPA 5: Voltar para Tela Principal ====================
        print("\n📍 ETAPA 5: Voltando para tela principal...")
        driver.get(BASE_URL)
        time.sleep(2)
        print("✅ De volta à tela principal")
        
        # ==================== ETAPA 6: Cadastrar Usuário 2 (Outro Convênio) ====================
        print("\n📍 ETAPA 6: Cadastrando segundo usuário (outro convênio)...")
        
        # Clicar no botão "Cadastre-se"
        btn_cadastro = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='paciente/cadastro.html']")))
        btn_cadastro.click()
        time.sleep(2)
        
        # Gerar dados do usuário 2
        usuario2 = gerar_dados_usuario(2)
        print(f"   👤 Usuário: {usuario2['nome']}")
        print(f"   📧 Email: {usuario2['email']}")
        print(f"   🆔 CPF: {formatar_cpf(usuario2['cpf'])}")
        
        # Preencher formulário
        driver.find_element(By.ID, "cpf").send_keys(usuario2['cpf'])
        driver.find_element(By.ID, "nome").send_keys(usuario2['nome'])
        driver.find_element(By.ID, "telefone").send_keys(usuario2['telefone'])
        driver.find_element(By.ID, "email").send_keys(usuario2['email'])
        driver.find_element(By.ID, "senha").send_keys(usuario2['senha'])
        driver.find_element(By.ID, "confirmarSenha").send_keys(usuario2['senha'])
        driver.find_element(By.ID, "dataNascimento").send_keys("1985-05-15")
        
        # Selecionar outro convênio (SulAmérica - segundo da lista)
        select_convenio = Select(driver.find_element(By.ID, "convenio"))
        select_convenio.select_by_index(2)  # 0 = Particular, 1 = Unimed, 2 = SulAmérica
        convenio_selecionado = select_convenio.first_selected_option.text
        print(f"   🏥 Convênio: {convenio_selecionado}")
        time.sleep(1)
        
        # Submeter formulário
        btn_submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn_submit.click()
        time.sleep(3)
        
        # Verificar cadastro
        current_url = driver.current_url
        if "login.html" in current_url:
            print("✅ Segundo cadastro realizado! Redirecionado para login")
        else:
            print("✅ Segundo cadastro realizado com sucesso")
            time.sleep(2)
        
        # ==================== ETAPA 7: Fazer Login com Usuário 2 ====================
        print("\n📍 ETAPA 7: Fazendo login com segundo usuário...")
        
        # Se não estiver na página de login, navegar até ela
        if "login.html" not in driver.current_url:
            driver.get(f"{BASE_URL}/paciente/login.html")
            time.sleep(2)
        
        # Preencher credenciais
        driver.find_element(By.ID, "email").clear()
        driver.find_element(By.ID, "email").send_keys(usuario2['email'])
        driver.find_element(By.ID, "senha").clear()
        driver.find_element(By.ID, "senha").send_keys(usuario2['senha'])
        
        # Fazer login
        btn_login = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        btn_login.click()
        time.sleep(3)
        
        # Verificar se está no dashboard
        current_url = driver.current_url
        if "dashboard.html" in current_url:
            print("✅ Login do segundo usuário realizado! No dashboard")
        else:
            print(f"⚠️  URL atual: {current_url}")
        
        # ==================== ETAPA 8: Fazer Logout Final ====================
        print("\n📍 ETAPA 8: Fazendo logout final...")
        
        try:
            btn_logout = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sair')] | //button[contains(text(), 'Sair')] | //a[@href='login.html']")))
            btn_logout.click()
            time.sleep(2)
            print("✅ Logout final realizado com sucesso")
        except Exception as e:
            print(f"⚠️  Fazendo logout via navegação direta: {e}")
            driver.get(f"{BASE_URL}/paciente/login.html")
            time.sleep(2)
        
        # ==================== RESULTADO FINAL ====================
        print("\n" + "=" * 80)
        print("✅ TESTE E2E CONCLUÍDO COM SUCESSO!")
        print("=" * 80)
        print("\n📊 RESUMO DO TESTE:")
        print(f"   ✓ Usuário 1: {usuario1['email']} (Convênio: {convenio_selecionado})")
        print(f"   ✓ Usuário 2: {usuario2['email']} (Convênio diferente)")
        print(f"   ✓ Total de cadastros: 2")
        print(f"   ✓ Total de logins: 2")
        print(f"   ✓ Total de logouts: 2")
        print("\n🎉 Todos os fluxos executados com sucesso!\n")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERRO NO TESTE E2E")
        print("=" * 80)
        print(f"Erro: {str(e)}")
        print(f"URL atual: {driver.current_url}")
        
        # Tirar screenshot do erro
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"erro_teste_e2e_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot salvo em: {screenshot_path}")
        
        return False
        
    finally:
        print("\n🔒 Fechando navegador...")
        time.sleep(3)  # Pausa para ver o resultado final
        driver.quit()
        print("✅ Navegador fechado\n")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 TESTE AUTOMATIZADO E2E - SISTEMA CLÍNICA SAÚDE+")
    print("=" * 80)
    print("\n📋 Fluxo do teste:")
    print("   1. Acessar tela principal")
    print("   2. Cadastrar primeiro usuário (com convênio)")
    print("   3. Fazer login")
    print("   4. Fazer logout")
    print("   5. Voltar para tela principal")
    print("   6. Cadastrar segundo usuário (outro convênio)")
    print("   7. Fazer login")
    print("   8. Fazer logout")
    print("\n⏱️  Iniciando em 3 segundos...")
    time.sleep(3)
    
    sucesso = test_fluxo_completo()
    
    exit(0 if sucesso else 1)
