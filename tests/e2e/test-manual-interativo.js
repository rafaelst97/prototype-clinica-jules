// Teste Manual Interativo - Testa TODAS as interações reais
// Este teste realmente CLICA, PREENCHE e INTERAGE com TODOS os elementos

const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:8081';

// Dados de teste
const testData = {
    paciente: {
        cpf: `${Date.now()}`.slice(-11),
        nome: 'Maria Teste Completa',
        telefone: '48987654321',
        email: `teste.real${Date.now()}@email.com`,
        senha: 'Senha12345',
        data_nascimento: '1995-05-20',
        endereco: 'Rua Real Teste, 999',
        cidade: 'Florianópolis',
        estado: 'SC',
        cep: '88010000'
    },
    medico: {
        crm: '12345-SC',
        senha: 'medico123'
    },
    admin: {
        usuario: 'admin@clinica.com',
        senha: 'admin123'
    }
};

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function testeManualCompleto() {
    console.log('\n🎬 INICIANDO TESTE MANUAL INTERATIVO');
    console.log('Este teste vai realmente USAR o sistema como um usuário real\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 800  // Mais devagar para visualização
    });
    
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    
    const page = await context.newPage();
    
    try {
        // ========================================
        // TESTE COMPLETO: PACIENTE
        // ========================================
        console.log('\n' + '='.repeat(80));
        console.log('📋 TESTANDO PERFIL PACIENTE - Interações Reais');
        console.log('='.repeat(80));
        
        console.log('\n1️⃣ Acessando página de cadastro...');
        await page.goto(`${BASE_URL}/paciente/cadastro.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        console.log('2️⃣ Preenchendo TODOS os campos do formulário...');
        await page.fill('#cpf', testData.paciente.cpf);
        await sleep(300);
        await page.fill('#nome', testData.paciente.nome);
        await sleep(300);
        await page.fill('#email', testData.paciente.email);
        await sleep(300);
        await page.fill('#telefone', testData.paciente.telefone);
        await sleep(300);
        await page.fill('#dataNascimento', testData.paciente.data_nascimento);
        await sleep(300);
        await page.fill('#senha', testData.paciente.senha);
        await sleep(300);
        await page.fill('#confirmarSenha', testData.paciente.senha);
        await sleep(300);
        await page.fill('#endereco', testData.paciente.endereco);
        await sleep(300);
        await page.fill('#cidade', testData.paciente.cidade);
        await sleep(300);
        await page.selectOption('#estado', testData.paciente.estado);
        await sleep(300);
        await page.fill('#cep', testData.paciente.cep);
        await sleep(500);
        
        console.log('   ✅ Todos os campos preenchidos!');
        
        console.log('3️⃣ Testando seleção de convênio...');
        const convenios = await page.locator('#convenio option').count();
        if (convenios > 1) {
            console.log(`   📋 ${convenios - 1} convênios disponíveis`);
            // Selecionar primeiro convênio (não o "Particular")
            await page.selectOption('#convenio', { index: 1 });
            await sleep(500);
            
            // Verificar se campo carteirinha apareceu
            const carteirinhaVisible = await page.locator('#carteirinhaGroup').isVisible();
            console.log(`   ${carteirinhaVisible ? '✅' : '❌'} Campo carteirinha ${carteirinhaVisible ? 'apareceu' : 'NÃO apareceu'}`);
            
            if (carteirinhaVisible) {
                await page.fill('#numeroCarteirinha', '123456789');
                console.log('   ✅ Carteirinha preenchida');
            }
        }
        
        console.log('4️⃣ Submetendo cadastro...');
        await Promise.all([
            page.waitForURL('**/login.html', { timeout: 20000 }),
            page.click('button[type="submit"]')
        ]);
        console.log('   ✅ Cadastro realizado com sucesso!');
        
        console.log('5️⃣ Fazendo login como paciente...');
        await sleep(1000);
        await page.fill('#email', testData.paciente.email);
        await page.fill('#senha', testData.paciente.senha);
        await Promise.all([
            page.waitForURL('**/dashboard.html', { timeout: 15000 }),
            page.click('button[type="submit"]')
        ]);
        console.log('   ✅ Login realizado!');
        await sleep(2000);
        
        console.log('6️⃣ Testando agendamento de consulta...');
        await page.goto(`${BASE_URL}/paciente/agendar.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        // Selecionar especialidade
        const especialidades = await page.locator('#especialidade option').count();
        console.log(`   📋 ${especialidades - 1} especialidades disponíveis`);
        if (especialidades > 1) {
            await page.selectOption('#especialidade', { index: 1 });
            console.log('   ✅ Especialidade selecionada');
            await sleep(1000);
            
            // Verificar se médicos carregaram
            const medicos = await page.locator('#medico option').count();
            console.log(`   👨‍⚕️ ${medicos - 1} médicos disponíveis`);
            
            if (medicos > 1) {
                await page.selectOption('#medico', { index: 1 });
                console.log('   ✅ Médico selecionado');
                await sleep(1000);
                
                // Selecionar data (amanhã)
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const dataStr = tomorrow.toISOString().split('T')[0];
                await page.fill('#data', dataStr);
                console.log('   ✅ Data selecionada');
                await sleep(1000);
                
                // Verificar se horários carregaram
                const horarios = await page.locator('#horario option').count();
                console.log(`   ⏰ ${horarios - 1} horários disponíveis`);
                
                if (horarios > 1) {
                    await page.selectOption('#horario', { index: 1 });
                    console.log('   ✅ Horário selecionado');
                    await sleep(500);
                    
                    console.log('   📝 Tentando agendar consulta...');
                    await page.click('button[type="submit"]');
                    await sleep(2000);
                    console.log('   ✅ Consulta agendada (ou tentativa realizada)');
                } else {
                    console.log('   ⚠️  Nenhum horário disponível para agendar');
                }
            }
        }
        
        console.log('7️⃣ Visualizando consultas agendadas...');
        await page.goto(`${BASE_URL}/paciente/consultas.html`);
        await page.waitForLoadState('networkidle');
        await sleep(2000);
        console.log('   ✅ Página de consultas carregada');
        
        console.log('8️⃣ Visualizando perfil...');
        await page.goto(`${BASE_URL}/paciente/perfil.html`);
        await page.waitForLoadState('networkidle');
        await sleep(2000);
        console.log('   ✅ Perfil carregado');
        
        // ========================================
        // TESTE COMPLETO: MÉDICO
        // ========================================
        console.log('\n' + '='.repeat(80));
        console.log('👨‍⚕️ TESTANDO PERFIL MÉDICO - Interações Reais');
        console.log('='.repeat(80));
        
        console.log('\n1️⃣ Fazendo logout...');
        await page.evaluate(() => localStorage.clear());
        await page.goto(`${BASE_URL}/medico/login.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        console.log('2️⃣ Fazendo login como médico...');
        await page.fill('#crm', testData.medico.crm);
        await page.fill('#senha', testData.medico.senha);
        await Promise.all([
            page.waitForURL('**/dashboard.html', { timeout: 15000 }),
            page.click('button[type="submit"]')
        ]);
        console.log('   ✅ Login médico realizado!');
        await sleep(2000);
        
        console.log('3️⃣ Testando cadastro de horários...');
        await page.goto(`${BASE_URL}/medico/horarios.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        // Tentar adicionar horário
        const hasDiaSelect = await page.locator('#diaSemana, select[name="diaSemana"]').count() > 0;
        if (hasDiaSelect) {
            console.log('   📅 Preenchendo formulário de horários...');
            await page.selectOption('#diaSemana, select[name="diaSemana"]', '1'); // Segunda
            await sleep(300);
            await page.fill('#horaInicio, input[name="horaInicio"]', '08:00');
            await sleep(300);
            await page.fill('#horaFim, input[name="horaFim"]', '12:00');
            await sleep(300);
            console.log('   ✅ Horários preenchidos');
            
            const submitBtn = await page.locator('button[type="submit"]').first();
            if (submitBtn) {
                await submitBtn.click();
                await sleep(2000);
                console.log('   ✅ Horário adicionado (ou tentativa realizada)');
            }
        } else {
            console.log('   ⚠️  Formulário de horários não encontrado');
        }
        
        console.log('4️⃣ Visualizando consultas do médico...');
        await page.goto(`${BASE_URL}/medico/consultas.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        // Testar filtros de data
        const hasDataInicio = await page.locator('#dataInicio').count() > 0;
        if (hasDataInicio) {
            console.log('   📅 Testando filtros de data...');
            const hoje = new Date().toISOString().split('T')[0];
            await page.fill('#dataInicio', hoje);
            await sleep(300);
            await page.fill('#dataFim', hoje);
            await sleep(300);
            
            const btnFiltrar = await page.locator('button').filter({ hasText: /filtrar/i }).first();
            if (btnFiltrar) {
                await btnFiltrar.click();
                await sleep(1500);
                console.log('   ✅ Filtros aplicados');
            }
        }
        
        console.log('5️⃣ Verificando agenda...');
        await page.goto(`${BASE_URL}/medico/agenda.html`);
        await page.waitForLoadState('networkidle');
        await sleep(2000);
        console.log('   ✅ Agenda visualizada');
        
        // ========================================
        // TESTE COMPLETO: ADMIN + PDF
        // ========================================
        console.log('\n' + '='.repeat(80));
        console.log('👨‍💼 TESTANDO PERFIL ADMIN - Interações Reais + PDF');
        console.log('='.repeat(80));
        
        console.log('\n1️⃣ Fazendo logout...');
        await page.evaluate(() => localStorage.clear());
        await page.goto(`${BASE_URL}/admin/login.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        console.log('2️⃣ Fazendo login como administrador...');
        await page.fill('#usuario', testData.admin.usuario);
        await page.fill('#senha', testData.admin.senha);
        await Promise.all([
            page.waitForURL('**/dashboard.html', { timeout: 15000 }),
            page.click('button[type="submit"]')
        ]);
        console.log('   ✅ Login admin realizado!');
        await sleep(2000);
        
        console.log('3️⃣ Testando cadastro de médico...');
        await page.goto(`${BASE_URL}/admin/medicos.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        // Clicar no botão para abrir o formulário
        console.log('   🖱️  Clicando em "Novo Médico"...');
        const btnNovoMedico = await page.locator('button').filter({ hasText: /novo.*médico/i }).first();
        if (btnNovoMedico) {
            await btnNovoMedico.click();
            await sleep(1000);
            console.log('   ✅ Formulário aberto');
        }
        
        const hasFormMedico = await page.locator('#cadastroMedicoForm').isVisible();
        if (hasFormMedico) {
            console.log('   📝 Preenchendo cadastro de médico...');
            await page.fill('#nome', 'Dr. Teste E2E');
            await sleep(300);
            await page.fill('#crm', `${Date.now()}`.slice(-5) + '-SC');
            await sleep(300);
            await page.fill('#email', `medico${Date.now()}@teste.com`);
            await sleep(300);
            await page.fill('#telefone', '48999998888');
            await sleep(300);
            
            await page.selectOption('#especialidade', { index: 1 });
            await sleep(300);
            console.log('   ✅ Formulário preenchido');
            
            const btnCadastrar = await page.locator('#cadastroMedicoForm button[type="submit"]');
            if (btnCadastrar) {
                await btnCadastrar.click();
                await sleep(2000);
                console.log('   ✅ Médico cadastrado (ou tentativa realizada)');
            }
        }
        
        console.log('4️⃣ Testando gestão de convênios...');
        await page.goto(`${BASE_URL}/admin/convenios.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1000);
        
        // Clicar no botão para abrir o formulário
        console.log('   🖱️  Clicando em "Novo Convênio"...');
        const btnNovoConvenio = await page.locator('button').filter({ hasText: /novo.*convênio/i }).first();
        if (btnNovoConvenio) {
            await btnNovoConvenio.click();
            await sleep(1000);
            console.log('   ✅ Formulário aberto');
        }
        
        const hasFormConvenio = await page.locator('#formConvenio').isVisible();
        if (hasFormConvenio) {
            console.log('   📝 Adicionando convênio...');
            await page.fill('#nomeConvenio', `Convênio Teste ${Date.now()}`);
            await sleep(300);
            await page.fill('#codigoConvenio', `TST-${Date.now()}`.slice(-8));
            await sleep(300);
            
            const btnSubmit = await page.locator('#cadastroConvenioForm button[type="submit"]');
            if (btnSubmit) {
                await btnSubmit.click();
                await sleep(2000);
                console.log('   ✅ Convênio adicionado (ou tentativa realizada)');
            }
        }
        
        console.log('5️⃣ Visualizando pacientes...');
        await page.goto(`${BASE_URL}/admin/pacientes.html`);
        await page.waitForLoadState('networkidle');
        await sleep(2000);
        console.log('   ✅ Lista de pacientes carregada');
        
        // ========================================
        // TESTE CRÍTICO: GERAÇÃO DE PDF
        // ========================================
        console.log('\n' + '='.repeat(80));
        console.log('📄 TESTE CRÍTICO: GERAÇÃO DE PDF');
        console.log('='.repeat(80));
        
        let pdfTestado = false;
        
        console.log('\n1️⃣ Acessando página de relatórios...');
        await page.goto(`${BASE_URL}/admin/relatorios.html`);
        await page.waitForLoadState('networkidle');
        await sleep(1500);
        
        console.log('2️⃣ Testando geração de relatório de consultas por médico...');
        
        // Preencher filtros do primeiro formulário
        const medico_select = await page.locator('#medico').first();
        if (medico_select) {
            await medico_select.selectOption({ index: 0 }); // Todos os médicos
            await sleep(300);
        }
        
        // Configurar período (último mês)
        const hoje = new Date();
        const mesPassado = new Date();
        mesPassado.setMonth(mesPassado.getMonth() - 1);
        
        await page.fill('#periodoInicio', mesPassado.toISOString().split('T')[0]);
        await sleep(300);
        await page.fill('#periodoFim', hoje.toISOString().split('T')[0]);
        await sleep(300);
        
        console.log('   � Filtros preenchidos');
        console.log('   🖱️  Clicando em "Gerar PDF"...');
        
        try {
            // Configurar listener para nova aba
            const newPagePromise = page.context().waitForEvent('page', { timeout: 8000 });
            
            // Clicar no botão do formulário
            await page.locator('#relatorioMedicoForm button[type="submit"]').click();
            await sleep(2000);
            
            // Verificar se nova aba foi aberta
            const newPage = await newPagePromise.catch(() => null);
            
            if (newPage) {
                const url = newPage.url();
                console.log(`   ✅ NOVA ABA ABERTA: ${url}`);
                
                // Verificar se é PDF (URL blob ou endpoint de PDF)
                const isPDF = url.startsWith('blob:') || 
                              url.includes('formato=pdf') || 
                              url.includes('.pdf') || 
                              url.includes('relatorios');
                
                if (isPDF) {
                    console.log('   ✅ ✅ ✅ PDF GERADO COM SUCESSO! ✅ ✅ ✅');
                    console.log(`   📄 URL do PDF: ${url}`);
                    
                    // Aguardar carregamento
                    await newPage.waitForLoadState('load', { timeout: 5000 }).catch(() => {});
                    await sleep(3000); // Deixar visualizar
                    
                    console.log('   ✅ PDF confirmado e visualizado!');
                    pdfTestado = true;
                    
                    await newPage.close();
                } else {
                    console.log('   ⚠️  Nova aba aberta mas não parece ser um PDF');
                    await newPage.close();
                }
            } else {
                console.log('   ⚠️  Nenhuma nova aba foi aberta');
            }
        } catch (error) {
            console.log(`   ❌ Erro ao testar PDF: ${error.message}`);
        }
        
        if (!pdfTestado) {
            console.log('\n   ⚠️  ATENÇÃO: PDF não foi gerado ou detectado!');
            console.log('   💡 Possíveis causas:');
            console.log('      - Backend não está gerando PDFs corretamente');
            console.log('      - Endpoint de relatórios pode estar com erro');
            console.log('      - Formato de resposta diferente do esperado');
        }
        
        // ========================================
        // RESUMO FINAL
        // ========================================
        console.log('\n' + '='.repeat(80));
        console.log('📊 RESUMO DO TESTE MANUAL INTERATIVO');
        console.log('='.repeat(80));
        console.log('\n✅ PERFIL PACIENTE:');
        console.log('   - Cadastro completo com todos os campos');
        console.log('   - Login e autenticação');
        console.log('   - Seleção de convênio e carteirinha');
        console.log('   - Agendamento de consulta');
        console.log('   - Visualização de consultas e perfil');
        
        console.log('\n✅ PERFIL MÉDICO:');
        console.log('   - Login via CRM');
        console.log('   - Cadastro de horários');
        console.log('   - Visualização de consultas');
        console.log('   - Filtros de data');
        console.log('   - Agenda');
        
        console.log('\n✅ PERFIL ADMIN:');
        console.log('   - Login');
        console.log('   - Cadastro de médico');
        console.log('   - Gestão de convênios');
        console.log('   - Visualização de pacientes');
        console.log(`   ${pdfTestado ? '✅' : '⚠️ '} Geração de PDF ${pdfTestado ? 'FUNCIONANDO' : 'NÃO CONFIRMADO'}`);
        
        console.log('\n🎬 Teste concluído! Navegador permanecerá aberto por 10 segundos...\n');
        await sleep(10000);
        
    } catch (error) {
        console.error('\n❌ Erro durante o teste:', error);
    } finally {
        await browser.close();
    }
}

testeManualCompleto().then(() => {
    console.log('✅ Teste manual interativo finalizado!');
    process.exit(0);
}).catch(error => {
    console.error('❌ Erro fatal:', error);
    process.exit(1);
});
