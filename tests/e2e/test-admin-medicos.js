/**
 * Teste Interativo - Admin Médicos
 * Execute no Console do DevTools na página admin/medicos.html
 */

console.log('🧪 INICIANDO TESTES - Admin Médicos');
console.log('====================================\n');

async function testarAdminMedicos() {
    let testesPassaram = 0;
    let testesFalharam = 0;
    
    // Teste 1: Verificar se API está carregada
    console.log('📋 Teste 1: Verificar se api.js está carregado...');
    if (typeof api !== 'undefined') {
        console.log('✅ api.js carregado com sucesso');
        testesPassaram++;
    } else {
        console.error('❌ api.js não está carregado');
        testesFalharam++;
        return;
    }
    
    // Teste 2: Verificar token de autenticação
    console.log('\n📋 Teste 2: Verificar token de autenticação...');
    const token = localStorage.getItem('token');
    if (token) {
        console.log('✅ Token presente:', token.substring(0, 20) + '...');
        testesPassaram++;
    } else {
        console.error('❌ Token não encontrado. Faça login como administrador primeiro.');
        testesFalharam++;
        return;
    }
    
    // Teste 3: Carregar lista de médicos
    console.log('\n📋 Teste 3: Carregar lista de médicos...');
    try {
        const medicos = await api.get('/admin/medicos');
        console.log(`✅ ${medicos.length} médicos carregados`);
        console.log('Médicos:', medicos.map(m => ({
            id: m.id,
            nome: m.usuario?.nome,
            crm: m.crm,
            especialidade: m.especialidade?.nome,
            ativo: m.usuario?.ativo
        })));
        testesPassaram++;
        
        // Teste 4: Verificar renderização na tabela
        console.log('\n📋 Teste 4: Verificar renderização na tabela...');
        const tbody = document.querySelector('tbody');
        if (tbody) {
            const linhas = tbody.querySelectorAll('tr');
            console.log(`✅ Tabela renderizada com ${linhas.length} linhas`);
            testesPassaram++;
        } else {
            console.error('❌ Tabela não encontrada');
            testesFalharam++;
        }
        
        // Teste 5: Verificar botões de ação
        console.log('\n📋 Teste 5: Verificar botões de ação...');
        const botoesVer = document.querySelectorAll('button[onclick*="verDetalhesMedico"]');
        const botoesDesativar = document.querySelectorAll('button[onclick*="desativarMedico"]');
        const botoesAtivar = document.querySelectorAll('button[onclick*="ativarMedico"]');
        console.log(`✅ Botões Ver: ${botoesVer.length}`);
        console.log(`✅ Botões Desativar: ${botoesDesativar.length}`);
        console.log(`✅ Botões Ativar: ${botoesAtivar.length}`);
        testesPassaram++;
        
        // Teste 6: Testar abertura de detalhes do primeiro médico
        if (medicos.length > 0) {
            console.log('\n📋 Teste 6: Testar abertura de detalhes do primeiro médico...');
            const primeiroMedico = medicos[0];
            console.log('Tentando abrir detalhes do médico:', primeiroMedico.usuario?.nome);
            
            // Simular clique no botão Ver
            if (typeof verDetalhesMedico === 'function') {
                await verDetalhesMedico(primeiroMedico.id);
                
                // Verificar se modal foi aberto
                setTimeout(() => {
                    const modal = document.getElementById('modalDetalhes');
                    if (modal) {
                        console.log('✅ Modal de detalhes aberto com sucesso');
                        testesPassaram++;
                        
                        // Fechar modal após 2 segundos
                        setTimeout(() => {
                            if (typeof fecharModal === 'function') {
                                fecharModal();
                                console.log('✅ Modal fechado');
                            }
                        }, 2000);
                    } else {
                        console.error('❌ Modal não foi aberto');
                        testesFalharam++;
                    }
                }, 500);
            } else {
                console.error('❌ Função verDetalhesMedico não encontrada');
                testesFalharam++;
            }
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar médicos:', error);
        testesFalharam++;
    }
    
    // Teste 7: Verificar carregamento de especialidades
    console.log('\n📋 Teste 7: Verificar especialidades carregadas...');
    try {
        const especialidades = await api.get('/pacientes/especialidades');
        console.log(`✅ ${especialidades.length} especialidades carregadas`);
        console.log('Especialidades:', especialidades.map(e => e.nome));
        testesPassaram++;
        
        // Verificar se select foi preenchido
        const selectEsp = document.getElementById('especialidade');
        if (selectEsp && selectEsp.options.length > 1) {
            console.log(`✅ Select de especialidades preenchido com ${selectEsp.options.length - 1} opções`);
            testesPassaram++;
        }
    } catch (error) {
        console.error('❌ Erro ao carregar especialidades:', error);
        testesFalharam++;
    }
    
    // Resumo final
    console.log('\n\n====================================');
    console.log('📊 RESUMO DOS TESTES');
    console.log('====================================');
    console.log(`✅ Testes passaram: ${testesPassaram}`);
    console.log(`❌ Testes falharam: ${testesFalharam}`);
    console.log(`📈 Taxa de sucesso: ${((testesPassaram / (testesPassaram + testesFalharam)) * 100).toFixed(1)}%`);
    
    if (testesFalharam === 0) {
        console.log('\n🎉 TODOS OS TESTES PASSARAM!');
    } else {
        console.log('\n⚠️ Alguns testes falharam. Verifique os erros acima.');
    }
}

// Executar testes
testarAdminMedicos();

console.log('\n\n💡 TESTES MANUAIS SUGERIDOS:');
console.log('1. Clique em "Ver" em um médico e verifique se o modal abre com os dados corretos');
console.log('2. Clique em "Desativar" em um médico ativo e confirme a ação');
console.log('3. Após desativar, verifique se o botão mudou para "Ativar"');
console.log('4. Clique em "Novo Médico" e preencha o formulário');
console.log('5. Tente cadastrar com email duplicado e verifique a mensagem de erro');
console.log('6. Tente cadastrar com CRM duplicado e verifique a mensagem de erro');
