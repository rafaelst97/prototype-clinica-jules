/**
 * Teste de Validação de Dados Únicos
 * Este script testa se o sistema previne cadastros duplicados de CPF, CRM e Email
 */

console.log('🔒 TESTE DE VALIDAÇÃO - Dados Únicos');
console.log('=====================================\n');

async function testarValidacaoUnicidade() {
    console.log('📋 Este teste vai verificar se o sistema previne cadastros duplicados\n');
    
    // Teste 1: Buscar um médico existente
    console.log('1️⃣ Buscando médicos existentes...');
    try {
        const medicos = await api.get('/admin/medicos');
        if (medicos.length === 0) {
            console.error('❌ Nenhum médico cadastrado. Cadastre um médico primeiro.');
            return;
        }
        
        const medicoExistente = medicos[0];
        console.log('✅ Médico encontrado:', {
            nome: medicoExistente.usuario?.nome,
            email: medicoExistente.usuario?.email,
            crm: medicoExistente.crm
        });
        
        // Teste 2: Tentar cadastrar médico com mesmo email
        console.log('\n2️⃣ Testando cadastro com email duplicado...');
        try {
            await api.post('/admin/medicos', {
                nome: 'Teste Duplicado',
                email: medicoExistente.usuario.email, // Email duplicado
                senha: 'senha12345',
                crm: 'CRM9999',
                especialidade_id: medicoExistente.especialidade_id
            });
            console.error('❌ FALHOU: Sistema permitiu email duplicado!');
        } catch (error) {
            if (error.message.includes('Email já cadastrado') || error.message.includes('409')) {
                console.log('✅ PASSOU: Sistema bloqueou email duplicado');
                console.log('   Mensagem:', error.message);
            } else {
                console.error('❌ Erro inesperado:', error.message);
            }
        }
        
        // Teste 3: Tentar cadastrar médico com mesmo CRM
        console.log('\n3️⃣ Testando cadastro com CRM duplicado...');
        try {
            await api.post('/admin/medicos', {
                nome: 'Teste Duplicado',
                email: 'novoemail@teste.com',
                senha: 'senha12345',
                crm: medicoExistente.crm, // CRM duplicado
                especialidade_id: medicoExistente.especialidade_id
            });
            console.error('❌ FALHOU: Sistema permitiu CRM duplicado!');
        } catch (error) {
            if (error.message.includes('CRM já cadastrado') || error.message.includes('409')) {
                console.log('✅ PASSOU: Sistema bloqueou CRM duplicado');
                console.log('   Mensagem:', error.message);
            } else {
                console.error('❌ Erro inesperado:', error.message);
            }
        }
        
        // Teste 4: Buscar um paciente existente
        console.log('\n4️⃣ Buscando pacientes existentes...');
        const pacientes = await api.get('/admin/pacientes');
        if (pacientes.length === 0) {
            console.warn('⚠️ Nenhum paciente cadastrado. Pulando testes de paciente.');
            return;
        }
        
        const pacienteExistente = pacientes[0];
        console.log('✅ Paciente encontrado:', {
            nome: pacienteExistente.usuario?.nome,
            email: pacienteExistente.usuario?.email,
            cpf: pacienteExistente.cpf
        });
        
        // Teste 5: Tentar cadastrar paciente com email duplicado
        console.log('\n5️⃣ Testando cadastro de paciente com email duplicado...');
        try {
            await api.post('/pacientes/cadastro', {
                nome: 'Teste Duplicado',
                email: pacienteExistente.usuario.email, // Email duplicado
                senha: 'senha12345',
                cpf: '12345678901',
                data_nascimento: '1990-01-01',
                telefone: '11999999999'
            }, false);
            console.error('❌ FALHOU: Sistema permitiu email duplicado para paciente!');
        } catch (error) {
            if (error.message.includes('Email já cadastrado') || error.message.includes('409')) {
                console.log('✅ PASSOU: Sistema bloqueou email duplicado');
                console.log('   Mensagem:', error.message);
            } else {
                console.error('❌ Erro inesperado:', error.message);
            }
        }
        
        // Teste 6: Tentar cadastrar paciente com CPF duplicado
        console.log('\n6️⃣ Testando cadastro de paciente com CPF duplicado...');
        try {
            await api.post('/pacientes/cadastro', {
                nome: 'Teste Duplicado',
                email: 'novoemail2@teste.com',
                senha: 'senha12345',
                cpf: pacienteExistente.cpf, // CPF duplicado
                data_nascimento: '1990-01-01',
                telefone: '11999999999'
            }, false);
            console.error('❌ FALHOU: Sistema permitiu CPF duplicado!');
        } catch (error) {
            if (error.message.includes('CPF já cadastrado') || error.message.includes('409')) {
                console.log('✅ PASSOU: Sistema bloqueou CPF duplicado');
                console.log('   Mensagem:', error.message);
            } else {
                console.error('❌ Erro inesperado:', error.message);
            }
        }
        
        console.log('\n\n====================================');
        console.log('✅ VALIDAÇÃO DE UNICIDADE COMPLETA');
        console.log('====================================');
        console.log('Todos os testes de duplicação foram executados.');
        console.log('Verifique se todos retornaram status HTTP 409 Conflict.');
        
    } catch (error) {
        console.error('❌ Erro ao executar testes:', error);
    }
}

// Executar testes
testarValidacaoUnicidade();
