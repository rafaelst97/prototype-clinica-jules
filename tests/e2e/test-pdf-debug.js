const { chromium } = require('playwright');

(async () => {
    console.log('🔍 DEBUGANDO GERAÇÃO DE PDF\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 500 
    });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Capturar logs do console
    page.on('console', msg => {
        const type = msg.type();
        const text = msg.text();
        console.log(`[CONSOLE ${type.toUpperCase()}]`, text);
    });
    
    // Capturar erros
    page.on('pageerror', err => {
        console.log('❌ [PAGE ERROR]', err.message);
    });
    
    // Capturar requisições
    page.on('request', req => {
        if (req.url().includes('relatorio')) {
            console.log('📤 [REQUEST]', req.method(), req.url());
        }
    });
    
    // Capturar respostas
    page.on('response', async res => {
        if (res.url().includes('relatorio')) {
            console.log('📥 [RESPONSE]', res.status(), res.url());
            console.log('   Headers:', res.headers());
            if (res.status() !== 200) {
                console.log('   Body:', await res.text().catch(() => 'N/A'));
            }
        }
    });
    
    try {
        // 1. Login como admin
        console.log('\n1️⃣ Fazendo login como admin...');
        await page.goto('http://localhost/admin/login.html', { waitUntil: 'domcontentloaded' });
        await page.waitForSelector('#usuario', { timeout: 10000 });
        await page.fill('#usuario', 'admin');
        await page.fill('#senha', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL('**/admin/dashboard.html', { timeout: 10000 });
        console.log('   ✅ Login realizado!');
        
        // 2. Ir para relatórios
        console.log('\n2️⃣ Acessando página de relatórios...');
        await page.goto('http://localhost/admin/relatorios.html');
        await page.waitForLoadState('networkidle');
        console.log('   ✅ Página carregada!');
        
        // Verificar token antes de continuar
        const tokenPresente = await page.evaluate(() => {
            return !!localStorage.getItem('token');
        });
        console.log(`   Token no localStorage: ${tokenPresente ? '✅ SIM' : '❌ NÃO'}`);
        
        if (!tokenPresente) {
            console.log('   ⚠️  Token perdido! Tentando relogar...');
            // Verificar se ainda temos o token em algum lugar
            const token = await page.evaluate(() => localStorage.getItem('token'));
            console.log('   Token encontrado:', token);
        }
        
        // 3. Verificar se a função existe
        console.log('\n3️⃣ Verificando função gerarPDF...');
        const funcExists = await page.evaluate(() => {
            return typeof gerarPDF === 'function';
        });
        console.log(`   ${funcExists ? '✅' : '❌'} Função gerarPDF existe:`, funcExists);
        
        // 4. Verificar se API_CONFIG existe
        console.log('\n4️⃣ Verificando API_CONFIG...');
        const apiConfig = await page.evaluate(() => {
            return typeof API_CONFIG !== 'undefined' ? API_CONFIG : null;
        });
        console.log(`   ${apiConfig ? '✅' : '❌'} API_CONFIG:`, apiConfig);
        
        // 5. Verificar se há erros de carregamento de scripts
        console.log('\n5️⃣ Verificando scripts carregados...');
        const scripts = await page.$$eval('script[src]', scripts => 
            scripts.map(s => ({ src: s.src, loaded: !s.error }))
        );
        console.log('   Scripts:', scripts.filter(s => s.src.includes('admin') || s.src.includes('api')));
        
        // 6. Tentar clicar no botão
        console.log('\n6️⃣ Clicando no botão Gerar PDF...');
        await page.waitForSelector('#relatorioMedicoForm button[type="submit"]', { timeout: 5000 });
        
        // Preencher período (necessário para gerar relatório)
        const hoje = new Date().toISOString().split('T')[0];
        await page.fill('#periodoInicio', hoje);
        await page.fill('#periodoFim', hoje);
        
        console.log('   🖱️  Clicando...');
        await page.click('#relatorioMedicoForm button[type="submit"]');
        
        // Aguardar 3 segundos para ver o que acontece
        console.log('\n⏳ Aguardando 3 segundos para observar...');
        await page.waitForTimeout(3000);
        
        // Verificar quantas abas existem
        const pages = context.pages();
        console.log(`\n📊 Total de abas abertas: ${pages.length}`);
        if (pages.length > 1) {
            console.log('   ✅ Nova aba foi aberta!');
            const newPage = pages[pages.length - 1];
            console.log('   URL da nova aba:', newPage.url());
        } else {
            console.log('   ❌ Nenhuma nova aba foi aberta');
        }
        
    } catch (error) {
        console.error('\n❌ ERRO:', error.message);
    }
    
    console.log('\n⏳ Mantendo navegador aberto por 10 segundos para inspeção...');
    await page.waitForTimeout(10000);
    
    await browser.close();
    console.log('\n✅ Debug concluído!');
})();
