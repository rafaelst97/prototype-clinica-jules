"""
Teste Automatizado - Dashboard Admin
Testa login e carregamento do dashboard administrativo
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def print_separator(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_admin_dashboard():
    """Testa login e dashboard do administrador"""
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = None
    
    try:
        print_separator("🚀 INICIANDO TESTE DO DASHBOARD ADMIN")
        
        # Inicializar driver (sem service, deixa o Selenium gerenciar)
        print("📦 Inicializando Chrome WebDriver...")
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Chrome: {e}")
            print("Tentando com ChromeDriverManager...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.set_page_load_timeout(30)
        print("✅ WebDriver inicializado com sucesso\n")
        
        # Acessar página de login
        login_url = "http://localhost/admin/login.html"
        print(f"🌐 Acessando: {login_url}")
        driver.get(login_url)
        time.sleep(2)
        print(f"✅ Página carregada: {driver.title}\n")
        
        # Preencher formulário
        print("📝 Preenchendo formulário de login...")
        
        usuario_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "usuario"))
        )
        usuario_input.clear()
        usuario_input.send_keys("admin@clinica.com")
        print("   ✓ Email preenchido: admin@clinica.com")
        
        senha_input = driver.find_element(By.ID, "senha")
        senha_input.clear()
        senha_input.send_keys("admin123")
        print("   ✓ Senha preenchida: admin123\n")
        
        # Capturar console logs antes do login
        print("📊 Logs do console antes do login:")
        logs = driver.get_log('browser')
        for log in logs[-5:]:  # Últimos 5 logs
            print(f"   {log['level']}: {log['message'][:100]}")
        
        # Fazer login
        print("\n🔐 Clicando em 'Entrar'...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()
        
        # Aguardar redirecionamento ou mensagem
        time.sleep(3)
        
        # Verificar URL atual
        current_url = driver.current_url
        print(f"📍 URL após login: {current_url}\n")
        
        # Capturar console logs após login
        print("📊 Logs do console após login:")
        logs = driver.get_log('browser')
        for log in logs[-10:]:  # Últimos 10 logs
            print(f"   {log['level']}: {log['message'][:150]}")
        print()
        
        # Verificar se redirecionou para dashboard
        if "dashboard" in current_url:
            print("✅ Redirecionado para dashboard!\n")
            
            # Aguardar carregamento
            print("⏳ Aguardando carregamento do dashboard...")
            time.sleep(5)
            
            # Verificar localStorage
            print("💾 Verificando localStorage:")
            token = driver.execute_script("return localStorage.getItem('token');")
            user_type = driver.execute_script("return localStorage.getItem('user_type');")
            user_id = driver.execute_script("return localStorage.getItem('user_id');")
            
            print(f"   Token: {'Presente' if token else 'AUSENTE'}")
            if token:
                print(f"   Token (primeiros 50 chars): {token[:50]}...")
            print(f"   User Type: {user_type}")
            print(f"   User ID: {user_id}\n")
            
            # Verificar título da página
            print(f"📄 Título da página: {driver.title}\n")
            
            # Verificar estatísticas nos cards
            print("📊 Verificando cards de estatísticas:")
            cards = driver.find_elements(By.CSS_SELECTOR, ".grid-2 .card:first-child h4")
            
            for i, card in enumerate(cards, 1):
                texto = card.text.strip()
                print(f"   Card {i}: {texto if texto else '(vazio)'}")
            print()
            
            # Verificar tabela de consultas
            print("📋 Verificando tabela de consultas:")
            tbody = driver.find_element(By.CSS_SELECTOR, ".card.mt-20 tbody")
            linhas = tbody.find_elements(By.TAG_NAME, "tr")
            print(f"   Total de linhas: {len(linhas)}")
            
            if len(linhas) > 0:
                primeira_linha = linhas[0].text.strip()
                print(f"   Primeira linha: {primeira_linha[:100]}")
            print()
            
            # Verificar alertas
            print("⚠️ Verificando alertas:")
            alertas = driver.find_elements(By.CSS_SELECTOR, ".card.mt-20:last-of-type .alert")
            print(f"   Total de alertas: {len(alertas)}")
            for i, alerta in enumerate(alertas, 1):
                print(f"   Alerta {i}: {alerta.text.strip()[:80]}")
            print()
            
            # Capturar logs finais do console
            print("📊 Logs finais do console:")
            logs = driver.get_log('browser')
            for log in logs[-15:]:  # Últimos 15 logs
                print(f"   {log['level']}: {log['message'][:200]}")
            print()
            
            # Verificar se há erros na página
            print("🔍 Verificando erros na página:")
            erros = driver.find_elements(By.CSS_SELECTOR, ".alert-error, .error-message")
            if erros:
                print(f"   ❌ Encontrados {len(erros)} erro(s):")
                for erro in erros:
                    print(f"      - {erro.text.strip()}")
            else:
                print("   ✅ Nenhum erro visível na página")
            print()
            
            # Screenshot final
            screenshot_path = "tests/admin_dashboard_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot salvo em: {screenshot_path}\n")
            
            print_separator("✅ TESTE CONCLUÍDO COM SUCESSO")
            
        else:
            print(f"❌ NÃO redirecionou para dashboard!")
            print(f"   URL atual: {current_url}\n")
            
            # Capturar erros visíveis
            print("🔍 Procurando mensagens de erro na página:")
            try:
                alertas = driver.find_elements(By.CSS_SELECTOR, ".alert, .error-message")
                if alertas:
                    for alerta in alertas:
                        print(f"   ⚠️ {alerta.text.strip()}")
                else:
                    print("   (Nenhuma mensagem de erro encontrada)")
            except Exception as e:
                print(f"   Erro ao buscar alertas: {e}")
            print()
            
            # Screenshot do erro
            screenshot_path = "tests/admin_login_error.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot do erro salvo em: {screenshot_path}\n")
            
            print_separator("❌ TESTE FALHOU")
        
        # Manter navegador aberto por 5 segundos para inspeção
        print("⏱️ Mantendo navegador aberto por 5 segundos para inspeção...")
        time.sleep(5)
        
    except Exception as e:
        print_separator("❌ ERRO DURANTE O TESTE")
        print(f"Erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}\n")
        
        if driver:
            # Screenshot do erro
            try:
                screenshot_path = "tests/admin_test_exception.png"
                driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot do erro salvo em: {screenshot_path}\n")
            except:
                pass
            
            # Capturar logs do console
            try:
                print("📊 Logs do console no momento do erro:")
                logs = driver.get_log('browser')
                for log in logs[-10:]:
                    print(f"   {log['level']}: {log['message'][:200]}")
            except:
                pass
        
        raise
        
    finally:
        if driver:
            print("\n🔚 Fechando navegador...")
            driver.quit()
            print("✅ Navegador fechado\n")

if __name__ == "__main__":
    test_admin_dashboard()
