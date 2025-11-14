/**
 * Teste Interativo - Admin Convênios
 * Execute no Console do DevTools na página admin/convenios.html
 */

console.log('🧪 INICIANDO TESTES - Admin Convênios');
console.log('====================================\n');

async function testarAdminConvenios() {
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
    
    // Teste 3: Carregar lista de convênios
    console.log('\n📋 Teste 3: Carregar lista de convênios...');
    try {
        const convenios = await api.get('/admin/convenios');
        console.log(`✅ ${convenios.length} convênios carregados`);
        console.log('Convênios:', convenios.map(c => ({
            id: c.id,
            nome: c.nome,
            codigo: c.codigo,
            ativo: c.ativo
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
        const botoesEditar = document.querySelectorAll('button[onclick*="editarConvenio"]');
        const botoesDesativar = document.querySelectorAll('button[onclick*="desativarConvenio"]');
        const botoesAtivar = document.querySelectorAll('button[onclick*="ativarConvenio"]');
        console.log(`✅ Botões Editar: ${botoesEditar.length}`);
        console.log(`✅ Botões Desativar: ${botoesDesativar.length}`);
        console.log(`✅ Botões Ativar: ${botoesAtivar.length}`);
        testesPassaram++;
        
        // Teste 6: Testar edição do primeiro convênio
        if (convenios.length > 0 && convenios.some(c => c.ativo)) {
            console.log('\n📋 Teste 6: Testar edição de convênio...');
            const convenioPrimeiroAtivo = convenios.find(c => c.ativo);
            console.log('Tentando editar convênio:', convenioPrimeiroAtivo.nome);
            
            // Simular clique no botão Editar
            if (typeof editarConvenio === 'function') {
                await editarConvenio(convenioPrimeiroAtivo.id);
                
                // Verificar se formulário foi preenchido
                setTimeout(() => {
                    const formConvenio = document.getElementById('formConvenio');
                    const nomeInput = document.getElementById('nomeConvenio');
                    const codigoInput = document.getElementById('codigoConvenio');
                    
                    if (formConvenio && formConvenio.style.display !== 'none' && 
                        nomeInput && nomeInput.value === convenioPrimeiroAtivo.nome) {
                        console.log('✅ Formulário de edição aberto e preenchido corretamente');
                        console.log('   Nome:', nomeInput.value);
                        console.log('   Código:', codigoInput.value);
                        testesPassaram++;
                        
                        // Fechar formulário
                        formConvenio.style.display = 'none';
                    } else {
                        console.error('❌ Formulário não foi preenchido corretamente');
                        testesFalharam++;
                    }
                }, 500);
            } else {
                console.error('❌ Função editarConvenio não encontrada');
                testesFalharam++;
            }
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar convênios:', error);
        testesFalharam++;
    }
    
    // Resumo final (com delay para esperar teste assíncrono)
    setTimeout(() => {
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
    }, 1000);
}

// Executar testes
testarAdminConvenios();

console.log('\n\n💡 TESTES MANUAIS SUGERIDOS:');
console.log('1. Clique em "Editar" em um convênio e verifique se o formulário abre preenchido');
console.log('2. Modifique os dados e clique em "Atualizar"');
console.log('3. Clique em "Desativar" em um convênio ativo e confirme a ação');
console.log('4. Após desativar, verifique se o botão mudou para "Ativar"');
console.log('5. Clique em "Novo Convênio" e preencha o formulário');
console.log('6. Tente cadastrar com nome ou código duplicado e verifique a mensagem de erro');
