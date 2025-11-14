// Script de teste do navegador com Playwright
const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Iniciando navegador...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100 // Slow motion para visualizar
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capturar logs do console
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    const emoji = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '📝';
    console.log(`${emoji} [CONSOLE ${type.toUpperCase()}]: ${text}`);
  });
  
  // Capturar erros
  page.on('pageerror', error => {
    console.log('💥 [PAGE ERROR]:', error.message);
  });
  
  // Capturar requisições
  page.on('request', request => {
    console.log(`📤 [REQUEST]: ${request.method()} ${request.url()}`);
  });
  
  page.on('response', response => {
    const status = response.status();
    const emoji = status >= 200 && status < 300 ? '✅' : '❌';
    console.log(`📥 [RESPONSE ${emoji}]: ${status} ${response.url()}`);
  });
  
  try {
    console.log('🌐 Navegando para o cadastro...\n');
    await page.goto('http://localhost:8081/paciente/cadastro.html');
    
    console.log('📝 Preenchendo formulário...\n');
    
    // Preencher campos
    await page.fill('#cpf', '12345678901');
    await page.fill('#nome', 'Teste da Silva');
    await page.fill('#telefone', '11987654321');
    await page.fill('#email', 'teste@email.com');
    await page.fill('#dataNascimento', '1990-01-01');
    await page.fill('#senha', 'Senha123456');
    await page.fill('#confirmarSenha', 'Senha123456');
    
    console.log('📸 Tirando screenshot antes do submit...');
    await page.screenshot({ path: 'cadastro-preenchido.png' });
    
    console.log('🖱️ Clicando em Cadastrar...\n');
    await page.click('button[type="submit"]');
    
    // Aguardar resposta ou redirecionamento
    await page.waitForTimeout(3000);
    
    console.log('📸 Tirando screenshot depois do submit...');
    await page.screenshot({ path: 'cadastro-resultado.png' });
    
    console.log('\n✅ Teste concluído! Screenshots salvos.');
    
  } catch (error) {
    console.error('❌ Erro durante o teste:', error.message);
    await page.screenshot({ path: 'cadastro-erro.png' });
  }
  
  // Manter navegador aberto por 10 segundos para você ver
  console.log('\n⏳ Mantendo navegador aberto por 10 segundos...');
  await page.waitForTimeout(10000);
  
  await browser.close();
  console.log('\n👋 Navegador fechado.');
})();
