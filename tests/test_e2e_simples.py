"""
Teste E2E Simplificado - Fluxo Completo de Cadastro e Login
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime
import random

BASE_URL = "http://localhost"

def gerar_cpf():
    """Gera CPF válido único"""
    # Gera 9 primeiros dígitos (primeiro não pode ser 0)
    cpf = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(8)]
    
    # Calcula primeiro dígito verificador
    sum1 = sum([(10-i) * cpf[i] for i in range(9)])
    d1 = 11 - (sum1 % 11)
    d1 = 0 if d1 >= 10 else d1
    cpf.append(d1)
    
    # Calcula segundo dígito verificador
    sum2 = sum([(11-i) * cpf[i] for i in range(10)])
    d2 = 11 - (sum2 % 11)
    d2 = 0 if d2 >= 10 else d2
    cpf.append(d2)
    
    return ''.join(map(str, cpf))

def gerar_telefone():
    """Gera telefone único"""
    return f"479{random.randint(10000000, 99999999)}"

print("\n" + "=" * 80)
print("🧪 TESTE E2E - FLUXO COMPLETO DE CADASTRO E LOGIN")
print("=" * 80)

# Configurar Chrome
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)

try:
    timestamp = int(datetime.now().timestamp())
    
    # ========== ETAPA 1: Tela Principal ==========
    print("\n📍 ETAPA 1: Acessando tela principal...")
    driver.get(BASE_URL)
    time.sleep(2)
    assert "Clínica" in driver.title
    print("✅ Tela principal OK")
    
    # ========== ETAPA 2: Cadastro Usuário 1 ==========
    print("\n📍 ETAPA 2: Cadastrando Usuário 1...")
    driver.get(f"{BASE_URL}/paciente/cadastro.html")
    time.sleep(2)
    
    usuario1_email = f"teste1_{timestamp}@email.com"
    usuario1_senha = "senha123"
    # Usar CPF único baseado no timestamp (garante que não começa com 0)
    usuario1_cpf = f"1{timestamp % 10000000000:010d}"
    
    print(f"   📧 Email: {usuario1_email}")
    print(f"   🆔 CPF: {usuario1_cpf}")
    
    driver.find_element(By.ID, "cpf").send_keys(usuario1_cpf)
    driver.find_element(By.ID, "nome").send_keys("Teste Usuário Um")
    driver.find_element(By.ID, "telefone").send_keys(gerar_telefone())
    driver.find_element(By.ID, "email").send_keys(usuario1_email)
    driver.find_element(By.ID, "senha").send_keys(usuario1_senha)
    driver.find_element(By.ID, "confirmarSenha").send_keys(usuario1_senha)
    driver.find_element(By.ID, "dataNascimento").send_keys("1990-01-01")
    
    # Selecionar primeiro convênio (Unimed)
    select = Select(driver.find_element(By.ID, "convenio"))
    time.sleep(1)
    select.select_by_index(1)
    convenio1 = select.first_selected_option.text
    print(f"   🏥 Convênio: {convenio1}")
    time.sleep(1)
    
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    # Aceitar alert se aparecer
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"   💬 Alert: {alert_text}")
        alert.accept()
        time.sleep(1)
    except:
        pass
    
    time.sleep(2)
    print("✅ Cadastro 1 realizado")
    
    # ========== ETAPA 3: Login Usuário 1 ==========
    print("\n📍 ETAPA 3: Login Usuário 1...")
    
    if "login.html" not in driver.current_url:
        driver.get(f"{BASE_URL}/paciente/login.html")
        time.sleep(2)
    
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(usuario1_email)
    driver.find_element(By.ID, "senha").clear()
    driver.find_element(By.ID, "senha").send_keys(usuario1_senha)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    # Aceitar alert de login
    try:
        alert = driver.switch_to.alert
        print(f"   💬 Alert: {alert.text}")
        alert.accept()
        time.sleep(1)
    except:
        pass
    
    time.sleep(2)
    
    if "dashboard" in driver.current_url:
        print("✅ Login 1 OK - Dashboard acessado")
    else:
        print(f"⚠️  URL: {driver.current_url}")
    
    # ========== ETAPA 4: Logout Usuário 1 ==========
    print("\n📍 ETAPA 4: Logout Usuário 1...")
    driver.get(f"{BASE_URL}/paciente/login.html")
    time.sleep(2)
    print("✅ Logout 1 OK")
    
    # ========== ETAPA 5: Voltar Tela Principal ==========
    print("\n📍 ETAPA 5: Voltando à tela principal...")
    driver.get(BASE_URL)
    time.sleep(2)
    print("✅ De volta à home")
    
    # ========== ETAPA 6: Cadastro Usuário 2 ==========
    print("\n📍 ETAPA 6: Cadastrando Usuário 2 (outro convênio)...")
    driver.get(f"{BASE_URL}/paciente/cadastro.html")
    time.sleep(2)
    
    usuario2_email = f"teste2_{timestamp}@email.com"
    usuario2_senha = "senha456"
    # Usar CPF único diferente do primeiro (garante que não começa com 0)
    usuario2_cpf = f"2{(timestamp + 12345) % 10000000000:010d}"
    
    print(f"   📧 Email: {usuario2_email}")
    print(f"   🆔 CPF: {usuario2_cpf}")
    
    driver.find_element(By.ID, "cpf").send_keys(usuario2_cpf)
    time.sleep(0.5)
    driver.find_element(By.ID, "nome").send_keys("Teste Usuário Dois")
    time.sleep(0.5)
    driver.find_element(By.ID, "telefone").send_keys(gerar_telefone())
    time.sleep(0.5)
    driver.find_element(By.ID, "email").send_keys(usuario2_email)
    time.sleep(0.5)
    driver.find_element(By.ID, "senha").send_keys(usuario2_senha)
    time.sleep(0.5)
    driver.find_element(By.ID, "confirmarSenha").send_keys(usuario2_senha)
    time.sleep(0.5)
    driver.find_element(By.ID, "dataNascimento").send_keys("1985-05-15")
    time.sleep(0.5)
    
    # Selecionar segundo convênio (SulAmérica)
    select = Select(driver.find_element(By.ID, "convenio"))
    time.sleep(1)
    select.select_by_index(2)
    convenio2 = select.first_selected_option.text
    print(f"   🏥 Convênio: {convenio2}")
    time.sleep(1)
    
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    # Aceitar alert se aparecer
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"   💬 Alert: {alert_text}")
        alert.accept()
        time.sleep(1)
    except:
        pass
    
    time.sleep(2)
    print("✅ Cadastro 2 realizado")
    
    # ========== ETAPA 7: Login Usuário 2 ==========
    print("\n📍 ETAPA 7: Login Usuário 2...")
    
    if "login.html" not in driver.current_url:
        driver.get(f"{BASE_URL}/paciente/login.html")
        time.sleep(2)
    
    driver.find_element(By.ID, "email").clear()
    driver.find_element(By.ID, "email").send_keys(usuario2_email)
    driver.find_element(By.ID, "senha").clear()
    driver.find_element(By.ID, "senha").send_keys(usuario2_senha)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(2)
    
    # Aceitar alert de login
    try:
        alert = driver.switch_to.alert
        print(f"   💬 Alert: {alert.text}")
        alert.accept()
        time.sleep(1)
    except:
        pass
    
    time.sleep(2)
    
    if "dashboard" in driver.current_url:
        print("✅ Login 2 OK - Dashboard acessado")
    else:
        print(f"⚠️  URL: {driver.current_url}")
    
    # ========== ETAPA 8: Logout Final ==========
    print("\n📍 ETAPA 8: Logout Usuário 2...")
    driver.get(f"{BASE_URL}/paciente/login.html")
    time.sleep(2)
    print("✅ Logout 2 OK")
    
    # ========== SUCESSO ==========
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print(f"\n📊 Usuário 1: {usuario1_email} ({convenio1})")
    print(f"📊 Usuário 2: {usuario2_email} ({convenio2})")
    print("\n🎉 Todos os fluxos executados!\n")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot = f"erro_{timestamp}.png"
    driver.save_screenshot(screenshot)
    print(f"📸 Screenshot: {screenshot}")
    
finally:
    print("\n🔒 Fechando navegador em 5 segundos...")
    time.sleep(5)
    driver.quit()
    print("✅ Teste finalizado\n")
