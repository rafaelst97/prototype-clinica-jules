// Teste manual do login para debug
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const BASE_URL = 'http://localhost:8081';
    const API_URL = 'http://localhost:8000';
    
    // Dados únicos
    const timestamp = Date.now();
    const testData = {
        cpf: `${timestamp}`.slice(-11),
        email: `teste${timestamp}@email.com`,
        nome: 'João Teste',
        telefone: '47999887766',
        data_nascimento: '1990-01-01',
        senha: 'senha123456'
    };
    
    console.log('📝 Dados do teste:', testData);
    
    try {
        // 1. Criar paciente via API
        console.log('\n1️⃣ Criando paciente via API...');
        const response = await fetch(`${API_URL}/pacientes/cadastro`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        
        if (response.ok) {
            console.log('✅ Paciente criado com sucesso!');
        } else {
            const error = await response.json();
            console.error('❌ Erro ao criar paciente:', error);
            await browser.close();
            return;
        }
        
        // 2. Tentar login via frontend
        console.log('\n2️⃣ Acessando página de login...');
        await page.goto(`${BASE_URL}/paciente/login.html`);
        await page.waitForLoadState('networkidle');
        
        console.log('3️⃣ Preenchendo formulário...');
        await page.fill('#email', testData.email);
        await page.fill('#senha', testData.senha);
        
        console.log('4️⃣ Clicando no botão de login...');
        
        // Escutar eventos de console para ver mensagens
        page.on('console', msg => console.log('🖥️ Console:', msg.text()));
        
        // Escutar requisições de rede
        page.on('request', request => {
            if (request.url().includes('/login')) {
                console.log('📡 Requisição:', request.method(), request.url());
            }
        });
        
        page.on('response', async response => {
            if (response.url().includes('/login')) {
                console.log('📨 Resposta:', response.status(), response.url());
                try {
                    const body = await response.json();
                    console.log('📦 Body:', JSON.stringify(body, null, 2));
                } catch (e) {
                    console.log('❌ Não foi possível ler o body da resposta');
                }
            }
        });
        
        await page.click('button[type="submit"]');
        
        console.log('5️⃣ Aguardando navegação...');
        
        // Esperar até 20 segundos pela navegação
        try {
            await page.waitForURL('**/dashboard.html', { timeout: 20000 });
            console.log('✅ SUCESSO! Redirecionou para dashboard!');
            console.log('📍 URL atual:', page.url());
        } catch (error) {
            console.log('❌ FALHOU! Não redirecionou.');
            console.log('📍 URL atual:', page.url());
            
            // Ver se há mensagens na página
            const messages = await page.locator('.message, .alert').allTextContents();
            console.log('💬 Mensagens na página:', messages);
        }
        
        // Manter navegador aberto por 30 segundos para inspeção
        console.log('\n⏳ Mantendo navegador aberto por 30 segundos...');
        await page.waitForTimeout(30000);
        
    } catch (error) {
        console.error('❌ Erro:', error);
    } finally {
        await browser.close();
    }
})();
