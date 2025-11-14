// Teste Completo - Validação com Banco de Dados e Responsividade Total
// Clínica Saúde+ - Verificação de persistência e design responsivo

const { chromium } = require('playwright');

// Configuração
const BASE_URL = 'http://localhost:8081';
const API_URL = 'http://localhost:8000';

// Viewports para teste de responsividade
const VIEWPORTS = {
    desktop: { width: 1920, height: 1080, name: 'Desktop' },
    laptop: { width: 1366, height: 768, name: 'Laptop' },
    tablet: { width: 768, height: 1024, name: 'Tablet' },
    mobile: { width: 375, height: 667, name: 'Mobile' }
};

// Lista completa de todas as páginas do sistema
const TODAS_PAGINAS = {
    publicas: [
        { path: '/index.html', name: 'Página Inicial' }
    ],
    paciente: [
        { path: '/paciente/login.html', name: 'Login Paciente' },
        { path: '/paciente/cadastro.html', name: 'Cadastro Paciente' },
        { path: '/paciente/dashboard.html', name: 'Dashboard Paciente' },
        { path: '/paciente/agendar.html', name: 'Agendar Consulta' },
        { path: '/paciente/consultas.html', name: 'Minhas Consultas' },
        { path: '/paciente/perfil.html', name: 'Perfil Paciente' }
    ],
    medico: [
        { path: '/medico/login.html', name: 'Login Médico' },
        { path: '/medico/dashboard.html', name: 'Dashboard Médico' },
        { path: '/medico/consultas.html', name: 'Consultas Médico' },
        { path: '/medico/horarios.html', name: 'Horários Médico' },
        { path: '/medico/agenda.html', name: 'Agenda Médico' }
    ],
    admin: [
        { path: '/admin/login.html', name: 'Login Admin' },
        { path: '/admin/dashboard.html', name: 'Dashboard Admin' },
        { path: '/admin/pacientes.html', name: 'Gestão Pacientes' },
        { path: '/admin/medicos.html', name: 'Gestão Médicos' },
        { path: '/admin/convenios.html', name: 'Gestão Convênios' },
        { path: '/admin/relatorios.html', name: 'Relatórios Admin' }
    ]
};

// Dados de teste
const testData = {
    paciente: {
        cpf: `${Date.now()}`.slice(-11),
        nome: 'João Silva Teste DB',
        telefone: '48999887766',
        email: `teste.db${Date.now()}@email.com`,
        senha: 'Senha12345',
        data_nascimento: '1990-01-15',
        endereco: 'Rua Teste, 123',
        cidade: 'Itajaí',
        estado: 'SC',
        cep: '88301000'
    },
    medico: {
        email: 'dr.silva@clinica.com',
        senha: 'medico123'
    },
    admin: {
        email: 'admin@clinica.com',
        senha: 'admin123'
    }
};

class TestRunner {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.results = {
            total: 0,
            passed: 0,
            failed: 0,
            errors: []
        };
    }

    async init() {
        this.browser = await chromium.launch({ headless: true });
        this.context = await this.browser.newContext();
        this.page = await this.context.newPage();
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async test(name, testFn) {
        this.results.total++;
        try {
            await testFn();
            this.results.passed++;
            console.log(`✅ ${name}`);
            return true;
        } catch (error) {
            this.results.failed++;
            this.results.errors.push({ test: name, error: error.message });
            console.log(`❌ ${name}`);
            console.log(`   ${error.message}`);
            return false;
        }
    }

    // Verificar dados no banco via API
    async verificarDadosBanco(endpoint, filtro, expectedData) {
        try {
            const response = await fetch(`${API_URL}${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`API retornou status ${response.status}`);
            }
            
            const data = await response.json();
            
            // Se é uma lista, procurar o item
            const item = Array.isArray(data) 
                ? data.find(filtro) 
                : data;
            
            if (!item) {
                throw new Error('Dados não encontrados no banco');
            }
            
            // Verificar campos esperados
            for (const [key, value] of Object.entries(expectedData)) {
                if (item[key] !== value) {
                    throw new Error(`Campo ${key}: esperado '${value}', encontrado '${item[key]}'`);
                }
            }
            
            return item;
        } catch (error) {
            throw new Error(`Erro ao verificar banco: ${error.message}`);
        }
    }

    // Testar responsividade de uma página
    async testarResponsividade(url, viewport) {
        await this.page.setViewportSize(viewport);
        await this.page.goto(url);
        await this.page.waitForLoadState('networkidle');
        
        // Verificar se página renderizou
        const bodyVisible = await this.page.locator('body').isVisible();
        if (!bodyVisible) {
            throw new Error('Página não renderizou');
        }
        
        // Verificar scroll horizontal (problema comum em páginas não responsivas)
        const scrollWidth = await this.page.evaluate(() => document.documentElement.scrollWidth);
        const clientWidth = await this.page.evaluate(() => document.documentElement.clientWidth);
        
        if (scrollWidth > clientWidth + 5) { // tolerância de 5px
            throw new Error(`Scroll horizontal detectado: ${scrollWidth}px > ${clientWidth}px`);
        }
        
        // Verificar elementos visíveis principais
        const hasHeader = await this.page.locator('header, .header, nav, .navbar').count() > 0;
        const hasMain = await this.page.locator('main, .container, .content').count() > 0;
        
        if (!hasHeader && !hasMain) {
            throw new Error('Estrutura básica da página não encontrada');
        }
        
        return true;
    }

    printReport() {
        console.log('\n' + '='.repeat(80));
        console.log('  RELATÓRIO FINAL DE TESTES - BANCO DE DADOS E RESPONSIVIDADE');
        console.log('='.repeat(80));
        console.log(`\nTotal de Testes: ${this.results.total}`);
        console.log(`✅ Passou: ${this.results.passed}`);
        console.log(`❌ Falhou: ${this.results.failed}`);
        console.log(`\nTaxa de Sucesso: ${((this.results.passed / this.results.total) * 100).toFixed(2)}%`);
        
        if (this.results.failed > 0) {
            console.log('\n📋 Testes que falharam:');
            this.results.errors.forEach(err => {
                console.log(`  ❌ ${err.test}`);
                console.log(`     ${err.error}`);
            });
        }
        
        console.log('\n' + '='.repeat(80) + '\n');
    }
}

async function runTests() {
    const runner = new TestRunner();
    
    try {
        await runner.init();
        
        console.log('\n🚀 INICIANDO VALIDAÇÃO COMPLETA COM BD E RESPONSIVIDADE');
        console.log('Clínica Saúde+ - Sistema de Agendamento de Consultas\n');
        
        // ============================================================
        // PARTE 1: TESTES DE PERSISTÊNCIA NO BANCO DE DADOS
        // ============================================================
        console.log('='.repeat(80));
        console.log('  PARTE 1: VALIDAÇÃO DE PERSISTÊNCIA NO BANCO DE DADOS');
        console.log('='.repeat(80) + '\n');
        
        // 1. Cadastro de Paciente e verificação no BD
        await runner.test('DB1: Cadastro de paciente persiste no banco', async () => {
            const response = await fetch(`${API_URL}/pacientes/cadastro`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testData.paciente)
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(`Erro ao cadastrar: ${JSON.stringify(error)}`);
            }
            
            const paciente = await response.json();
            testData.paciente.id = paciente.id;
            
            // Fazer login para obter token
            const loginResponse = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: testData.paciente.email,
                    senha: testData.paciente.senha
                })
            });
            
            const loginData = await loginResponse.json();
            runner.token = loginData.access_token;
            
            // Verificar dados no banco via API /auth/me
            const meResponse = await fetch(`${API_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${runner.token}` }
            });
            
            const userData = await meResponse.json();
            
            if (userData.email !== testData.paciente.email) {
                throw new Error('Email não corresponde no banco');
            }
            
            if (userData.tipo !== 'paciente') {
                throw new Error('Tipo de usuário incorreto no banco');
            }
        });
        
        // 2. Login de Médico e verificação de dados
        await runner.test('DB2: Login de médico retorna dados corretos do banco', async () => {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testData.medico)
            });
            
            if (!response.ok) {
                throw new Error('Falha no login do médico');
            }
            
            const { access_token } = await response.json();
            
            const meResponse = await fetch(`${API_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${access_token}` }
            });
            
            const userData = await meResponse.json();
            
            if (userData.tipo !== 'medico') {
                throw new Error(`Tipo incorreto: esperado 'medico', obtido '${userData.tipo}'`);
            }
        });
        
        // 3. Login de Admin e verificação
        await runner.test('DB3: Login de admin retorna dados corretos do banco', async () => {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(testData.admin)
            });
            
            if (!response.ok) {
                throw new Error('Falha no login do admin');
            }
            
            const { access_token } = await response.json();
            
            const meResponse = await fetch(`${API_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${access_token}` }
            });
            
            const userData = await meResponse.json();
            
            if (userData.tipo !== 'admin') {
                throw new Error(`Tipo incorreto: esperado 'admin', obtido '${userData.tipo}'`);
            }
        });
        
        // 4. Listar convênios (endpoint público)
        await runner.test('DB4: Listagem de convênios retorna dados do banco', async () => {
            const response = await fetch(`${API_URL}/pacientes/convenios`);
            
            if (!response.ok) {
                throw new Error('Erro ao listar convênios');
            }
            
            const convenios = await response.json();
            
            if (!Array.isArray(convenios)) {
                throw new Error('Resposta não é uma lista');
            }
            
            if (convenios.length === 0) {
                throw new Error('Nenhum convênio encontrado no banco');
            }
        });
        
        // 5. Listar especialidades
        await runner.test('DB5: Listagem de especialidades retorna dados do banco', async () => {
            const response = await fetch(`${API_URL}/pacientes/especialidades`);
            
            if (!response.ok) {
                throw new Error('Erro ao listar especialidades');
            }
            
            const especialidades = await response.json();
            
            if (!Array.isArray(especialidades)) {
                throw new Error('Resposta não é uma lista');
            }
            
            if (especialidades.length === 0) {
                throw new Error('Nenhuma especialidade encontrada no banco');
            }
        });
        
        // ============================================================
        // PARTE 2: TESTES DE RESPONSIVIDADE EM TODAS AS TELAS
        // ============================================================
        console.log('\n' + '='.repeat(80));
        console.log('  PARTE 2: VALIDAÇÃO DE RESPONSIVIDADE EM TODAS AS TELAS');
        console.log('='.repeat(80) + '\n');
        
        // Testar cada página em cada viewport
        for (const [viewportName, viewport] of Object.entries(VIEWPORTS)) {
            console.log(`\n📱 Testando ${viewport.name} (${viewport.width}x${viewport.height})`);
            console.log('-'.repeat(80));
            
            // Páginas públicas
            for (const pagina of TODAS_PAGINAS.publicas) {
                await runner.test(
                    `${viewport.name}: ${pagina.name}`,
                    async () => {
                        await runner.testarResponsividade(
                            `${BASE_URL}${pagina.path}`,
                            viewport
                        );
                    }
                );
            }
            
            // Páginas do paciente
            for (const pagina of TODAS_PAGINAS.paciente) {
                await runner.test(
                    `${viewport.name}: ${pagina.name}`,
                    async () => {
                        await runner.testarResponsividade(
                            `${BASE_URL}${pagina.path}`,
                            viewport
                        );
                    }
                );
            }
            
            // Páginas do médico
            for (const pagina of TODAS_PAGINAS.medico) {
                await runner.test(
                    `${viewport.name}: ${pagina.name}`,
                    async () => {
                        await runner.testarResponsividade(
                            `${BASE_URL}${pagina.path}`,
                            viewport
                        );
                    }
                );
            }
            
            // Páginas do admin
            for (const pagina of TODAS_PAGINAS.admin) {
                await runner.test(
                    `${viewport.name}: ${pagina.name}`,
                    async () => {
                        await runner.testarResponsividade(
                            `${BASE_URL}${pagina.path}`,
                            viewport
                        );
                    }
                );
            }
        }
        
        // Relatório final
        runner.printReport();
        
    } catch (error) {
        console.error('❌ Erro crítico nos testes:', error);
    } finally {
        await runner.close();
    }
}

// Executar testes
runTests().then(() => {
    console.log('✅ Testes finalizados!');
    process.exit(0);
}).catch(error => {
    console.error('❌ Erro fatal:', error);
    process.exit(1);
});
