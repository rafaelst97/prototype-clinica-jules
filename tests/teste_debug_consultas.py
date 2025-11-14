"""
Script de Teste Simples - Debug Carregamento de Consultas
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoAlertPresentException

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument('--start-maximized')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("🔧 Iniciando teste de debug...")
    
    # Login
    print("\n1️⃣  Fazendo login...")
    driver.get("http://localhost/paciente/login.html")
    time.sleep(2)
    
    driver.find_element(By.ID, "email").send_keys("paciente1@teste.com")
    driver.find_element(By.ID, "senha").send_keys("paciente123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)
    
    # Aceitar alert
    try:
        alert = driver.switch_to.alert
        print(f"  📢 Alert: {alert.text}")
        alert.accept()
        time.sleep(2)
    except NoAlertPresentException:
        pass
    
    print(f"  ✅ URL atual: {driver.current_url}")
    
    # Navegar para consultas
    print("\n2️⃣  Navegando para consultas...")
    driver.get("http://localhost/paciente/consultas.html")
    time.sleep(3)
    
    # Aceitar qualquer alert que aparecer
    for i in range(3):
        try:
            alert = driver.switch_to.alert
            print(f"  📢 Alert {i+1}: {alert.text}")
            alert.accept()
            time.sleep(1)
        except NoAlertPresentException:
            break
    
    # Capturar logs do console
    print("\n3️⃣  Capturando logs do console...")
    logs = driver.get_log('browser')
    if logs:
        print("  📋 Logs encontrados:")
        for log in logs:
            print(f"    {log['level']}: {log['message']}")
    else:
        print("  ℹ️  Nenhum log encontrado")
    
    # Verificar se a tabela foi renderizada
    print("\n4️⃣  Verificando tabela de consultas...")
    tbody = driver.find_element(By.CSS_SELECTOR, ".card:first-of-type tbody")
    print(f"  📊 Conteúdo da tabela: {tbody.text[:200]}")
    
    # Verificar se há botão de reagendar
    try:
        reagendar_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Reagendar')]")
        print(f"  🔘 Botões de reagendar encontrados: {len(reagendar_buttons)}")
    except:
        print("  ⚠️  Nenhum botão de reagendar encontrado")
    
    print("\n✅ Teste concluído!")
    input("\nPressione ENTER para fechar...")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    input("\nPressione ENTER para fechar...")
finally:
    driver.quit()
