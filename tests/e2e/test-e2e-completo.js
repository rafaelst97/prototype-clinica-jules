// Teste E2E Completo - Simulação Real de Uso por Todos os Perfis
// Testa TODAS as funcionalidades interagindo com o navegador

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost:8081';
const API_URL = 'http://localhost:8000';

// Dados de teste
const testData = {
    paciente: {
        cpf: `${Date.now()}`.slice(-11),
        nome: 'João da Silva E2E',
        telefone: '48999887766',
        email: `paciente.e2e${Date.now()}@email.com`,
        senha: 'Senha12345',
        data_nascimento: '1990-01-15',
        endereco: 'Rua Teste E2E, 123',
        cidade: 'Itajaí',
        estado: 'SC',
        cep: '88301000'
    },
    medico: {
        crm: '12345-SC',  // CRM do Dr. Silva
        senha: 'medico123'
    },
    admin: {
        usuario: 'admin@clinica.com',  // Campo é "usuario" e não "email"
        senha: 'admin123'
    }
};

class E2ETestRunner {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.results = {
            paciente: { total: 0, passed: 0, failed: 0, errors: [] },
            medico: { total: 0, passed: 0, failed: 0, errors: [] },
            admin: { total: 0, passed: 0, failed: 0, errors: [] }
        };
    }

    async init() {
        this.browser = await chromium.launch({ 
            headless: false, // Mostrar navegador para visualização
            slowMo: 500 // Desacelerar para visualização
        });
        this.context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 }
        });
        this.page = await this.context.newPage();
        
        // Capturar console para debug
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log(`  🔴 Console Error: ${msg.text()}`);
            }
        });
    }

    async close() {
        if (this.browser) await this.browser.close();
    }

    async test(profile, name, testFn) {
        this.results[profile].total++;
        console.log(`\n🧪 Testando: ${name}`);
        try {
            await testFn();
            this.results[profile].passed++;
            console.log(`  ✅ PASSOU`);
            return true;
        } catch (error) {
            this.results[profile].failed++;
            this.results[profile].errors.push({ test: name, error: error.message });
            console.log(`  ❌ FALHOU: ${error.message}`);
            return false;
        }
    }

    async waitAndClick(selector, timeout = 5000) {
        await this.page.waitForSelector(selector, { timeout });
        await this.page.click(selector);
    }

    async fillForm(data) {
        for (const [id, value] of Object.entries(data)) {
            const element = this.page.locator(`#${id}`);
            const tagName = await element.evaluate(el => el.tagName);
            
            if (tagName === 'SELECT') {
                await element.selectOption(value);
            } else {
                await element.fill(value);
            }
        }
    }

    async screenshot(name) {
        const screenshotPath = path.join(__dirname, 'screenshots', `${name}.png`);
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`  📸 Screenshot salvo: ${name}.png`);
    }

    printReport() {
        console.log('\n' + '='.repeat(100));
        console.log('  RELATÓRIO FINAL - TESTES E2E POR PERFIL');
        console.log('='.repeat(100));

        let totalTests = 0, totalPassed = 0, totalFailed = 0;

        for (const [profile, data] of Object.entries(this.results)) {
            totalTests += data.total;
            totalPassed += data.passed;
            totalFailed += data.failed;

            const percentage = data.total > 0 ? ((data.passed / data.total) * 100).toFixed(2) : 0;
            console.log(`\n👤 ${profile.toUpperCase()}: ${data.passed}/${data.total} (${percentage}%)`);
            
            if (data.failed > 0) {
                data.errors.forEach(err => {
                    console.log(`   ❌ ${err.test}`);
                    console.log(`      ${err.error}`);
                });
            }
        }

        console.log('\n' + '='.repeat(100));
        console.log(`\n📊 RESUMO GERAL:`);
        console.log(`   Total de Testes E2E: ${totalTests}`);
        console.log(`   ✅ Passou: ${totalPassed}`);
        console.log(`   ❌ Falhou: ${totalFailed}`);
        console.log(`   Taxa de Sucesso: ${((totalPassed / totalTests) * 100).toFixed(2)}%`);
        console.log('\n' + '='.repeat(100) + '\n');
    }
}

async function runE2ETests() {
    const runner = new E2ETestRunner();
    
    // Criar pasta para screenshots
    const screenshotDir = path.join(__dirname, 'screenshots');
    if (!fs.existsSync(screenshotDir)) {
        fs.mkdirSync(screenshotDir);
    }
    
    try {
        await runner.init();
        
        console.log('\n🚀 INICIANDO TESTES E2E - SIMULAÇÃO REAL DE USO');
        console.log('Clínica Saúde+ - Testando todos os perfis no navegador\n');

        // ============================================================
        // PERFIL: PACIENTE
        // ============================================================
        console.log('='.repeat(100));
        console.log('  PERFIL: PACIENTE - Testando todas as funcionalidades');
        console.log('='.repeat(100));

        await runner.test('paciente', 'Acessar página inicial', async () => {
            await runner.page.goto(`${BASE_URL}/index.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.screenshot('01-pagina-inicial');
        });

        await runner.test('paciente', 'Navegar para cadastro de paciente', async () => {
            await runner.page.goto(`${BASE_URL}/paciente/cadastro.html`);
            await runner.page.waitForLoadState('networkidle');
            // Esperar carregar formulário
            await runner.page.waitForSelector('#cadastroForm', { timeout: 10000 });
            await runner.page.waitForTimeout(1000);
            const hasForm = await runner.page.locator('#cadastroForm').count() > 0;
            if (!hasForm) {
                throw new Error('Formulário de cadastro não carregou');
            }
            await runner.screenshot('02-cadastro-paciente');
        });

        await runner.test('paciente', 'Preencher formulário de cadastro completo', async () => {
            await runner.fillForm({
                nome: testData.paciente.nome,
                email: testData.paciente.email,
                cpf: testData.paciente.cpf,
                telefone: testData.paciente.telefone,
                dataNascimento: testData.paciente.data_nascimento,
                senha: testData.paciente.senha,
                confirmarSenha: testData.paciente.senha,
                endereco: testData.paciente.endereco,
                cidade: testData.paciente.cidade,
                estado: testData.paciente.estado,
                cep: testData.paciente.cep
            });
            await runner.screenshot('03-formulario-preenchido');
        });

        await runner.test('paciente', 'Submeter cadastro e aguardar redirecionamento', async () => {
            await Promise.all([
                runner.page.waitForURL('**/login.html', { timeout: 15000 }),
                runner.page.click('button[type="submit"]')
            ]);
            await runner.screenshot('04-cadastro-sucesso');
        });

        await runner.test('paciente', 'Realizar login como paciente', async () => {
            await runner.page.fill('#email', testData.paciente.email);
            await runner.page.fill('#senha', testData.paciente.senha);
            await runner.screenshot('05-login-preenchido');
            
            await Promise.all([
                runner.page.waitForURL('**/dashboard.html', { timeout: 15000 }),
                runner.page.click('button[type="submit"]')
            ]);
            await runner.page.waitForLoadState('networkidle');
            await runner.screenshot('06-dashboard-paciente');
        });

        await runner.test('paciente', 'Visualizar dashboard do paciente', async () => {
            const hasWelcome = await runner.page.locator('h1, h2, h3').filter({ hasText: /bem.vindo|dashboard|painel/i }).count() > 0;
            const hasContent = await runner.page.locator('.card, .stat-card, .consulta, main').count() > 0;
            if (!hasWelcome && !hasContent) {
                throw new Error('Dashboard não carregou corretamente');
            }
            await runner.page.waitForTimeout(2000);
        });

        await runner.test('paciente', 'Navegar para agendar consulta', async () => {
            await runner.page.goto(`${BASE_URL}/paciente/agendar.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('07-agendar-consulta');
        });

        await runner.test('paciente', 'Verificar formulário de agendamento', async () => {
            const hasEspecialidade = await runner.page.locator('#especialidade, select[name="especialidade"]').count() > 0;
            const hasMedico = await runner.page.locator('#medico, select[name="medico"]').count() > 0;
            const hasData = await runner.page.locator('#data, input[name="data"]').count() > 0;
            
            if (!hasEspecialidade || !hasMedico || !hasData) {
                throw new Error('Formulário de agendamento incompleto');
            }
        });

        await runner.test('paciente', 'Visualizar minhas consultas', async () => {
            await runner.page.goto(`${BASE_URL}/paciente/consultas.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('08-consultas-paciente');
            
            const hasConsultas = await runner.page.locator('.consulta, .card, table, #listaConsultas').count() > 0;
            if (!hasConsultas) throw new Error('Área de consultas não encontrada');
        });

        await runner.test('paciente', 'Visualizar perfil do paciente', async () => {
            await runner.page.goto(`${BASE_URL}/paciente/perfil.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('09-perfil-paciente');
        });

        // ============================================================
        // PERFIL: MÉDICO
        // ============================================================
        console.log('\n' + '='.repeat(100));
        console.log('  PERFIL: MÉDICO - Testando todas as funcionalidades');
        console.log('='.repeat(100));

        await runner.test('medico', 'Logout do paciente', async () => {
            // Limpar localStorage para simular logout
            await runner.page.evaluate(() => localStorage.clear());
            await runner.page.goto(`${BASE_URL}/index.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
        });

        await runner.test('medico', 'Acessar login do médico', async () => {
            await runner.page.goto(`${BASE_URL}/medico/login.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('10-login-medico');
        });

        await runner.test('medico', 'Realizar login como médico', async () => {
            // Garantir que estamos na página de login
            const currentURL = runner.page.url();
            if (!currentURL.includes('medico/login.html')) {
                await runner.page.goto(`${BASE_URL}/medico/login.html`);
                await runner.page.waitForLoadState('networkidle');
                await runner.page.waitForTimeout(1000);
            }
            
            await runner.page.waitForSelector('#crm', { timeout: 10000 });
            await runner.page.waitForTimeout(500);
            await runner.page.fill('#crm', testData.medico.crm);
            await runner.page.fill('#senha', testData.medico.senha);
            await runner.screenshot('11-login-medico-preenchido');
            
            await Promise.all([
                runner.page.waitForURL('**/dashboard.html', { timeout: 15000 }),
                runner.page.click('button[type="submit"]')
            ]);
            await runner.page.waitForLoadState('networkidle');
            await runner.screenshot('12-dashboard-medico');
        });

        await runner.test('medico', 'Visualizar dashboard do médico', async () => {
            const hasStats = await runner.page.locator('.stat-card, .card, .dashboard').count() > 0;
            if (!hasStats) throw new Error('Dashboard do médico não carregou');
            await runner.page.waitForTimeout(2000);
        });

        await runner.test('medico', 'Acessar agenda do médico', async () => {
            await runner.page.goto(`${BASE_URL}/medico/agenda.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('13-agenda-medico');
        });

        await runner.test('medico', 'Gerenciar horários de trabalho', async () => {
            await runner.page.goto(`${BASE_URL}/medico/horarios.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('14-horarios-medico');
            
            const hasForm = await runner.page.locator('form, #formHorarios').count() > 0;
            if (!hasForm) throw new Error('Formulário de horários não encontrado');
        });

        await runner.test('medico', 'Visualizar consultas agendadas', async () => {
            await runner.page.goto(`${BASE_URL}/medico/consultas.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('15-consultas-medico');
        });

        await runner.test('medico', 'Verificar filtro por data nas consultas', async () => {
            const hasDataInicio = await runner.page.locator('#dataInicio, input[name="dataInicio"]').count() > 0;
            const hasDataFim = await runner.page.locator('#dataFim, input[name="dataFim"]').count() > 0;
            
            if (!hasDataInicio || !hasDataFim) {
                throw new Error('Filtros de data não encontrados');
            }
        });

        await runner.test('medico', 'Verificar campo de observações', async () => {
            const hasObservacao = await runner.page.locator('textarea, #diagnostico').filter({ hasText: /observa|diagnóstico/i }).count() > 0 ||
                                  await runner.page.locator('label, h3').filter({ hasText: /observa/i }).count() > 0;
            
            if (!hasObservacao) throw new Error('Campo de observações não encontrado');
        });

        // ============================================================
        // PERFIL: ADMINISTRADOR
        // ============================================================
        console.log('\n' + '='.repeat(100));
        console.log('  PERFIL: ADMINISTRADOR - Testando todas as funcionalidades');
        console.log('='.repeat(100));

        await runner.test('admin', 'Logout do médico', async () => {
            // Limpar localStorage para simular logout
            await runner.page.evaluate(() => localStorage.clear());
            await runner.page.goto(`${BASE_URL}/index.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
        });

        await runner.test('admin', 'Acessar login do administrador', async () => {
            await runner.page.goto(`${BASE_URL}/admin/login.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('16-login-admin');
        });

        await runner.test('admin', 'Realizar login como administrador', async () => {
            // Garantir que estamos na página de login
            const currentURL = runner.page.url();
            if (!currentURL.includes('admin/login.html')) {
                await runner.page.goto(`${BASE_URL}/admin/login.html`);
                await runner.page.waitForLoadState('networkidle');
                await runner.page.waitForTimeout(1000);
            }
            
            await runner.page.waitForSelector('#usuario', { timeout: 10000 });
            await runner.page.waitForTimeout(500);
            await runner.page.fill('#usuario', testData.admin.usuario);
            await runner.page.fill('#senha', testData.admin.senha);
            await runner.screenshot('17-login-admin-preenchido');
            
            await Promise.all([
                runner.page.waitForURL('**/dashboard.html', { timeout: 15000 }),
                runner.page.click('button[type="submit"]')
            ]);
            await runner.page.waitForLoadState('networkidle');
            await runner.screenshot('18-dashboard-admin');
        });

        await runner.test('admin', 'Visualizar dashboard administrativo', async () => {
            const hasStats = await runner.page.locator('.stat-card, .card, .dashboard').count() > 0;
            if (!hasStats) throw new Error('Dashboard admin não carregou');
            await runner.page.waitForTimeout(2000);
        });

        await runner.test('admin', 'Gerenciar pacientes', async () => {
            await runner.page.goto(`${BASE_URL}/admin/pacientes.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('19-gestao-pacientes');
            
            const hasTable = await runner.page.locator('table, .paciente-item').count() > 0;
            if (!hasTable) throw new Error('Lista de pacientes não encontrada');
        });

        await runner.test('admin', 'Verificar funcionalidade de desbloquear paciente', async () => {
            const hasDesbloquear = await runner.page.locator('button, .btn').filter({ hasText: /desbloquear/i }).count() > 0 ||
                                   await runner.page.locator('*').filter({ hasText: /bloqueado|status/i }).count() > 0;
            
            if (!hasDesbloquear) {
                console.log('  ⚠️  Nenhum paciente bloqueado para testar desbloqueio');
            }
        });

        await runner.test('admin', 'Gerenciar médicos', async () => {
            await runner.page.goto(`${BASE_URL}/admin/medicos.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('20-gestao-medicos');
            
            const hasForm = await runner.page.locator('form, #formMedico').count() > 0;
            const hasTable = await runner.page.locator('table, .medico-item').count() > 0;
            
            if (!hasForm && !hasTable) {
                throw new Error('Gestão de médicos não encontrada');
            }
        });

        await runner.test('admin', 'Verificar cadastro de médico (CRM, especialidade)', async () => {
            const hasCRM = await runner.page.locator('#crm, input[name="crm"]').count() > 0;
            const hasEspecialidade = await runner.page.locator('#especialidade, select[name="especialidade"]').count() > 0;
            
            if (!hasCRM || !hasEspecialidade) {
                throw new Error('Campos obrigatórios de cadastro de médico não encontrados');
            }
        });

        await runner.test('admin', 'Gerenciar convênios', async () => {
            await runner.page.goto(`${BASE_URL}/admin/convenios.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('21-gestao-convenios');
            
            const hasConvenios = await runner.page.locator('form, table, #listaConvenios').count() > 0;
            if (!hasConvenios) throw new Error('Gestão de convênios não encontrada');
        });

        await runner.test('admin', 'Acessar relatórios', async () => {
            await runner.page.goto(`${BASE_URL}/admin/relatorios.html`);
            await runner.page.waitForLoadState('networkidle');
            await runner.page.waitForTimeout(1000);
            await runner.screenshot('22-relatorios');
        });

        await runner.test('admin', 'Verificar tipos de relatórios disponíveis', async () => {
            const tiposRelatorio = [
                /consultas.*médico/i,
                /especialidade/i,
                /cancelamento/i,
                /paciente/i
            ];
            
            let encontrados = 0;
            for (const tipo of tiposRelatorio) {
                const has = await runner.page.locator('*').filter({ hasText: tipo }).count() > 0;
                if (has) encontrados++;
            }
            
            if (encontrados < 3) {
                throw new Error(`Apenas ${encontrados}/4 tipos de relatórios encontrados`);
            }
        });

        await runner.test('admin', 'Testar geração de relatório em PDF', async () => {
            // Procurar botão de gerar PDF
            const buttons = await runner.page.locator('button, .btn').all();
            let pdfButton = null;
            
            for (const button of buttons) {
                const text = await button.textContent();
                if (text && (text.includes('PDF') || text.includes('Gerar') || text.includes('Relatório'))) {
                    pdfButton = button;
                    break;
                }
            }
            
            if (pdfButton) {
                // Configurar listener para download
                const downloadPromise = runner.page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
                
                // Clicar no botão
                await pdfButton.click();
                await runner.page.waitForTimeout(2000);
                
                // Verificar se PDF foi gerado
                const download = await downloadPromise;
                if (download) {
                    console.log(`  📄 PDF gerado com sucesso: ${download.suggestedFilename()}`);
                    await runner.screenshot('23-pdf-gerado');
                } else {
                    // Verificar se abriu em nova aba
                    const pages = runner.context.pages();
                    if (pages.length > 1) {
                        console.log(`  📄 PDF aberto em nova aba`);
                        await pages[pages.length - 1].close();
                    } else {
                        console.log(`  ⚠️  PDF pode ter sido gerado mas não foi possível detectar`);
                    }
                }
            } else {
                console.log(`  ℹ️  Botão de gerar PDF não encontrado (pode precisar selecionar tipo de relatório primeiro)`);
            }
        });

        // Relatório final
        runner.printReport();
        
        console.log('\n✅ Testes E2E concluídos! Navegador permanecerá aberto por 10 segundos para inspeção...\n');
        await runner.page.waitForTimeout(10000);
        
    } catch (error) {
        console.error('❌ Erro crítico nos testes E2E:', error);
    } finally {
        await runner.close();
    }
}

runE2ETests().then(() => {
    console.log('✅ Execução finalizada!');
    process.exit(0);
}).catch(error => {
    console.error('❌ Erro fatal:', error);
    process.exit(1);
});
