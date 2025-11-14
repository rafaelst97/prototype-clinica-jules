const { chromium } = require('playwright');

(async () => {
    console.log('🧪 Iniciando teste de edição de convênio com descrição...\n');
    
    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // 1. Fazer login como admin
        console.log('1️⃣ Acessando página de login...');
        await page.goto('http://localhost/admin/login.html');
        await page.waitForLoadState('networkidle');
        await page.waitForSelector('#email', { timeout: 10000 });
        
        console.log('2️⃣ Fazendo login como administrador...');
        await page.fill('#email', 'admin@clinica.com');
        await page.fill('#senha', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);
        
        // 2. Navegar para página de convênios
        console.log('3️⃣ Navegando para página de convênios...');
        await page.goto('http://localhost/admin/convenios.html');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);
        
        // 3. Verificar se convênios foram carregados
        console.log('4️⃣ Verificando convênios carregados...');
        const conveniosRows = await page.locator('tbody tr').count();
        console.log(`   ✅ ${conveniosRows} convênios encontrados\n`);
        
        // 4. Clicar no primeiro botão Editar
        console.log('5️⃣ Clicando em Editar no primeiro convênio...');
        const primeiroEditarBtn = page.locator('button:has-text("Editar")').first();
        await primeiroEditarBtn.click();
        await page.waitForTimeout(1000);
        
        // 5. Verificar se formulário abriu
        const formVisivel = await page.locator('#formConvenio').isVisible();
        console.log(`   ✅ Formulário visível: ${formVisivel}\n`);
        
        // 6. Capturar valores atuais
        console.log('6️⃣ Capturando valores atuais do formulário...');
        const nomeAtual = await page.locator('#nomeConvenio').inputValue();
        const codigoAtual = await page.locator('#codigoConvenio').inputValue();
        const telefoneAtual = await page.locator('#telefoneConvenio').inputValue();
        const emailAtual = await page.locator('#emailConvenio').inputValue();
        const descricaoAtual = await page.locator('#descricaoConvenio').inputValue();
        
        console.log('   Valores atuais:');
        console.log(`   - Nome: "${nomeAtual}"`);
        console.log(`   - Código: "${codigoAtual}"`);
        console.log(`   - Telefone: "${telefoneAtual}"`);
        console.log(`   - Email: "${emailAtual}"`);
        console.log(`   - Descrição: "${descricaoAtual}"\n`);
        
        // 7. Preencher descrição
        const descricaoTeste = `Teste de descrição automatizado - ${Date.now()}`;
        console.log('7️⃣ Preenchendo campo descrição...');
        console.log(`   📝 Descrição a ser inserida: "${descricaoTeste}"\n`);
        
        await page.locator('#descricaoConvenio').clear();
        await page.locator('#descricaoConvenio').fill(descricaoTeste);
        await page.waitForTimeout(500);
        
        // Verificar se foi preenchido
        const descricaoPreenchida = await page.locator('#descricaoConvenio').inputValue();
        console.log(`   ✅ Campo preenchido com: "${descricaoPreenchida}"\n`);
        
        // 8. Capturar requisição de atualização
        console.log('8️⃣ Preparando para capturar requisição...');
        const requestPromise = page.waitForRequest(request => 
            request.url().includes('/admin/convenios/') && request.method() === 'PUT'
        );
        
        // 9. Clicar em Atualizar
        console.log('9️⃣ Clicando em Atualizar...');
        await page.click('button[type="submit"]');
        
        // Capturar dados enviados
        const request = await requestPromise;
        const postData = request.postDataJSON();
        
        console.log('\n📤 DADOS ENVIADOS NA REQUISIÇÃO:');
        console.log(JSON.stringify(postData, null, 2));
        console.log('');
        
        // 10. Aguardar resposta
        await page.waitForTimeout(2000);
        
        // 11. Verificar se formulário fechou
        const formFechou = await page.locator('#formConvenio').isHidden();
        console.log(`🔟 Formulário fechou após salvar: ${formFechou}\n`);
        
        // 12. Editar novamente para verificar se salvou
        console.log('1️⃣1️⃣ Abrindo formulário novamente para verificar...');
        await primeiroEditarBtn.click();
        await page.waitForTimeout(1000);
        
        const descricaoVerificacao = await page.locator('#descricaoConvenio').inputValue();
        console.log(`   📋 Descrição carregada: "${descricaoVerificacao}"\n`);
        
        // 13. Comparar
        if (descricaoVerificacao === descricaoTeste) {
            console.log('✅ ✅ ✅ SUCESSO! Descrição foi salva corretamente!');
        } else {
            console.log('❌ ❌ ❌ FALHA! Descrição NÃO foi salva!');
            console.log(`   Esperado: "${descricaoTeste}"`);
            console.log(`   Recebido: "${descricaoVerificacao}"`);
        }
        
        console.log('\n📊 Teste concluído!');
        
    } catch (error) {
        console.error('❌ Erro durante o teste:', error);
    } finally {
        await page.waitForTimeout(3000);
        await browser.close();
    }
})();
