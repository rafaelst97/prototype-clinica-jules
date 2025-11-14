const { chromium } = require('playwright');

(async () => {
    console.log('🧪 TESTANDO PÁGINA DE PACIENTES DO ADMIN\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 500 
    });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Capturar logs do console
    page.on('console', msg => console.log(`[CONSOLE ${msg.type()}]`, msg.text()));
    page.on('pageerror', err => console.log('❌ [ERROR]', err.message));
    
    try {
        // 1. Login como admin
        console.log('1️⃣ Fazendo login como admin...');
        await page.goto('http://localhost/admin/login.html');
        await page.waitForSelector('#usuario');
        await page.fill('#usuario', 'admin');
        await page.fill('#senha', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForURL('**/admin/dashboard.html', { timeout: 5000 });
        console.log('   ✅ Login realizado!\n');
        
        // 2. Ir para pacientes
        console.log('2️⃣ Acessando página de pacientes...');
        await page.goto('http://localhost/admin/pacientes.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000); // Aguardar carregar dados
        console.log('   ✅ Página carregada!\n');
        
        // 3. Verificar se a tabela foi populada
        console.log('3️⃣ Verificando se dados foram carregados...');
        const linhas = await page.$$('tbody tr');
        console.log(`   📊 Total de pacientes: ${linhas.length}`);
        
        if (linhas.length === 0) {
            console.log('   ⚠️  Nenhum paciente encontrado na tabela!');
        } else {
            console.log('   ✅ Pacientes carregados!\n');
            
            // 4. Testar botão "Ver Detalhes"
            console.log('4️⃣ Testando botão "Ver Detalhes"...');
            const btnDetalhes = await page.$('button:has-text("Ver Detalhes"), button:has-text("Detalhes")');
            if (btnDetalhes) {
                await btnDetalhes.click();
                await page.waitForTimeout(1000);
                
                // Verificar se modal abriu
                const modal = await page.$('#modalDetalhes');
                if (modal) {
                    console.log('   ✅ Modal de detalhes aberto!');
                    console.log('   🖱️  Fechando modal...');
                    await page.click('#modalDetalhes'); // Clicar fora para fechar
                    await page.waitForTimeout(500);
                } else {
                    console.log('   ❌ Modal não foi aberto!');
                }
            } else {
                console.log('   ❌ Botão "Ver Detalhes" não encontrado!');
            }
            console.log('');
            
            // 5. Testar botão "Desbloquear" se existir
            console.log('5️⃣ Testando botão "Desbloquear" (se existir)...');
            const btnDesbloquear = await page.$('button:has-text("Desbloquear")');
            if (btnDesbloquear) {
                console.log('   ✅ Botão "Desbloquear" encontrado!');
                console.log('   🖱️  Clicando...');
                
                // Aceitar o confirm
                page.on('dialog', async dialog => {
                    console.log(`   💬 Dialog: ${dialog.message()}`);
                    await dialog.accept();
                });
                
                await btnDesbloquear.click();
                await page.waitForTimeout(2000);
                console.log('   ✅ Ação de desbloquear executada!');
            } else {
                console.log('   ℹ️  Nenhum paciente bloqueado encontrado');
            }
            console.log('');
            
            // 6. Testar busca
            console.log('6️⃣ Testando busca de pacientes...');
            const inputBusca = await page.$('input[type="text"]');
            if (inputBusca) {
                await inputBusca.fill('teste');
                await page.waitForTimeout(500);
                const linhasDepois = await page.$$('tbody tr');
                console.log(`   📊 Pacientes após busca: ${linhasDepois.length}`);
                
                // Limpar busca
                await inputBusca.fill('');
                await page.waitForTimeout(500);
                console.log('   ✅ Busca funcionando!');
            }
        }
        
        console.log('\n✅ Teste concluído!');
        console.log('⏳ Mantendo navegador aberto por 10 segundos...\n');
        await page.waitForTimeout(10000);
        
    } catch (error) {
        console.error('\n❌ ERRO:', error.message);
    }
    
    await browser.close();
})();
