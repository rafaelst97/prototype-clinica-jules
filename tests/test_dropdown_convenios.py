"""
Teste automatizado para diagnosticar problema do dropdown de convênios
Captura logs do console, requisições de rede e estado do DOM
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def testar_dropdown_convenios():
    """Testa o carregamento do dropdown de convênios com diagnóstico completo"""
    
    # Configurar Chrome com logs habilitados
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Executar sem interface gráfica
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})
    
    print("\n" + "="*80)
    print("🔍 TESTE AUTOMATIZADO - DROPDOWN DE CONVÊNIOS")
    print("="*80 + "\n")
    
    driver = None
    try:
        # Inicializar driver
        print("⏳ Inicializando Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        print("✅ Chrome inicializado\n")
        
        # Habilitar captura de logs de rede
        driver.execute_cdp_cmd('Network.enable', {})
        
        # Carregar página de cadastro
        url = "http://localhost/paciente/cadastro.html"
        print(f"📄 Carregando página: {url}")
        driver.get(url)
        print("✅ Página carregada\n")
        
        # Aguardar alguns segundos para JavaScript carregar
        print("⏳ Aguardando JavaScript carregar (3 segundos)...")
        time.sleep(3)
        
        # Capturar logs do console
        print("\n" + "-"*80)
        print("📋 LOGS DO CONSOLE DO NAVEGADOR:")
        print("-"*80)
        console_logs = driver.get_log('browser')
        if console_logs:
            for log in console_logs:
                timestamp = log.get('timestamp', 'N/A')
                level = log.get('level', 'INFO')
                message = log.get('message', '')
                print(f"[{level}] {message}")
        else:
            print("⚠️  Nenhum log do console capturado")
        
        # Verificar requisições de rede via Performance logs
        print("\n" + "-"*80)
        print("🌐 REQUISIÇÕES DE REDE:")
        print("-"*80)
        perf_logs = driver.get_log('performance')
        api_requests = []
        
        for log in perf_logs:
            try:
                log_data = json.loads(log['message'])
                message = log_data.get('message', {})
                method = message.get('method', '')
                
                # Capturar requisições de rede
                if method == 'Network.responseReceived':
                    params = message.get('params', {})
                    response = params.get('response', {})
                    url_req = response.get('url', '')
                    status = response.get('status', 0)
                    
                    if 'planos-saude' in url_req or 'localhost:8000' in url_req:
                        api_requests.append({
                            'url': url_req,
                            'status': status,
                            'statusText': response.get('statusText', ''),
                            'mimeType': response.get('mimeType', '')
                        })
                        print(f"📡 {url_req}")
                        print(f"   Status: {status} {response.get('statusText', '')}")
                        print(f"   Content-Type: {response.get('mimeType', '')}")
            except:
                continue
        
        if not api_requests:
            print("⚠️  Nenhuma requisição à API capturada")
        
        # Verificar estado do dropdown
        print("\n" + "-"*80)
        print("📊 ESTADO DO DROPDOWN:")
        print("-"*80)
        
        try:
            # Localizar o select
            convenio_select = driver.find_element(By.ID, "convenio")
            print(f"✅ Elemento <select id='convenio'> encontrado")
            
            # Verificar se está visível
            is_visible = convenio_select.is_displayed()
            print(f"   Visível: {is_visible}")
            
            # Pegar todas as options
            options = convenio_select.find_elements(By.TAG_NAME, "option")
            print(f"   Número de opções: {len(options)}")
            
            print("\n   📋 OPÇÕES NO DROPDOWN:")
            for i, option in enumerate(options):
                value = option.get_attribute('value')
                text = option.text
                print(f"      [{i}] value='{value}' | text='{text}'")
            
            # Verificar se tem mais de 1 opção (além de Particular)
            if len(options) == 1:
                print("\n   ❌ PROBLEMA: Apenas 1 opção no dropdown (deveria ter 7: Particular + 6 convênios)")
            elif len(options) > 1:
                print(f"\n   ✅ Dropdown parece estar funcionando ({len(options)} opções)")
            
        except Exception as e:
            print(f"❌ Erro ao acessar dropdown: {str(e)}")
        
        # Verificar se o JavaScript foi carregado
        print("\n" + "-"*80)
        print("🔧 VERIFICAÇÃO DE SCRIPTS:")
        print("-"*80)
        
        scripts = driver.find_elements(By.TAG_NAME, "script")
        print(f"Total de scripts carregados: {len(scripts)}")
        
        for script in scripts:
            src = script.get_attribute('src')
            if src:
                print(f"   📜 {src}")
        
        # Testar se a função carregarPlanosSaude existe
        print("\n" + "-"*80)
        print("🔍 VERIFICANDO FUNÇÕES JAVASCRIPT:")
        print("-"*80)
        
        try:
            # Verificar se API_CONFIG existe
            api_config_exists = driver.execute_script("return typeof API_CONFIG !== 'undefined'")
            print(f"   API_CONFIG definido: {api_config_exists}")
            
            if api_config_exists:
                base_url = driver.execute_script("return API_CONFIG.BASE_URL")
                planos_endpoint = driver.execute_script("return API_CONFIG.ENDPOINTS.PACIENTE_PLANOS_SAUDE")
                print(f"   BASE_URL: {base_url}")
                print(f"   ENDPOINT: {planos_endpoint}")
            
            # Verificar se carregarPlanosSaude existe
            func_exists = driver.execute_script("return typeof carregarPlanosSaude === 'function'")
            print(f"   Função carregarPlanosSaude definida: {func_exists}")
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar JavaScript: {str(e)}")
        
        # Fazer requisição direta à API via JavaScript
        print("\n" + "-"*80)
        print("🧪 TESTE DIRETO DA API VIA JAVASCRIPT:")
        print("-"*80)
        
        try:
            result = driver.execute_async_script("""
                const callback = arguments[arguments.length - 1];
                
                fetch('http://localhost:8000/pacientes/planos-saude')
                    .then(response => {
                        return response.json().then(data => {
                            callback({
                                success: true,
                                status: response.status,
                                statusText: response.statusText,
                                data: data,
                                dataLength: data.length
                            });
                        });
                    })
                    .catch(error => {
                        callback({
                            success: false,
                            error: error.toString()
                        });
                    });
            """)
            
            if result.get('success'):
                print(f"   ✅ API respondeu com sucesso")
                print(f"   Status: {result['status']} {result['statusText']}")
                print(f"   Planos retornados: {result['dataLength']}")
                print(f"\n   📦 Dados retornados:")
                for plano in result['data']:
                    print(f"      - {plano.get('nome')} (ID: {plano.get('id_plano_saude')})")
            else:
                print(f"   ❌ Erro na requisição: {result.get('error')}")
                
        except Exception as e:
            print(f"   ❌ Erro ao executar fetch: {str(e)}")
        
        # Diagnóstico final
        print("\n" + "="*80)
        print("🎯 DIAGNÓSTICO FINAL:")
        print("="*80)
        
        # Contar opções novamente para diagnóstico final
        try:
            final_options = driver.find_element(By.ID, "convenio").find_elements(By.TAG_NAME, "option")
            opcoes_count = len(final_options)
            
            if opcoes_count == 1:
                print("\n❌ PROBLEMA CONFIRMADO:")
                print("   - O dropdown tem apenas 1 opção (Particular)")
                print("   - A API está funcionando e retorna 6 convênios")
                print("   - O JavaScript não está populando o dropdown")
                print("\n💡 POSSÍVEIS CAUSAS:")
                print("   1. Cache do navegador servindo JavaScript antigo")
                print("   2. Erro silencioso no JavaScript (verificar logs acima)")
                print("   3. Problema de timing (JavaScript executa antes do DOM estar pronto)")
                print("   4. CORS bloqueando a requisição (verificar Network logs)")
                
            elif opcoes_count > 6:
                print(f"\n✅ DROPDOWN FUNCIONANDO CORRETAMENTE!")
                print(f"   - {opcoes_count} opções encontradas (1 Particular + 6 convênios)")
                print("   - API respondendo corretamente")
                print("   - JavaScript populando o dropdown")
                
            else:
                print(f"\n⚠️  PROBLEMA PARCIAL:")
                print(f"   - Dropdown tem {opcoes_count} opções (esperado: 7)")
                print("   - Alguns convênios podem estar faltando")
                
        except Exception as e:
            print(f"\n❌ Erro no diagnóstico final: {str(e)}")
        
        print("\n" + "="*80 + "\n")
        
    except TimeoutException:
        print("❌ TIMEOUT: Página demorou muito para carregar")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL NO TESTE: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Browser fechado\n")


if __name__ == "__main__":
    testar_dropdown_convenios()
