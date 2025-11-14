// Perfil do Paciente - Integrado com API
let pacienteId = null;

// Função para formatar telefone
function formatarTelefone(valor) {
    // Remove tudo que não é dígito
    valor = valor.replace(/\D/g, '');
    
    // Limita a 11 dígitos
    if (valor.length > 11) {
        valor = valor.substring(0, 11);
    }
    
    // Aplica a máscara
    if (valor.length <= 10) {
        // Formato: (XX) XXXX-XXXX
        valor = valor.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
    } else {
        // Formato: (XX) XXXXX-XXXX
        valor = valor.replace(/^(\d{2})(\d{5})(\d{0,4}).*/, '($1) $2-$3');
    }
    
    return valor;
}

// Função para formatar CPF
function formatarCPF(valor) {
    // Remove tudo que não é dígito
    valor = valor.replace(/\D/g, '');
    
    // Limita a 11 dígitos
    if (valor.length > 11) {
        valor = valor.substring(0, 11);
    }
    
    // Aplica a máscara: XXX.XXX.XXX-XX
    valor = valor.replace(/^(\d{3})(\d{3})(\d{3})(\d{0,2}).*/, '$1.$2.$3-$4');
    
    return valor;
}

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('paciente');
    
    pacienteId = api.getUserId();
    await carregarDadosPerfil();
    await verificarStatusBloqueio();
    
    setupFormListeners();
});

async function carregarDadosPerfil() {
    try {
        console.log('📊 Carregando perfil do paciente:', pacienteId);
        const perfil = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_PERFIL(pacienteId));
        console.log('✅ Perfil carregado do PostgreSQL:', perfil);
        
        // Atualizar nome na navbar
        const nomeNavbar = document.querySelector('.nav-user span strong');
        if (nomeNavbar) {
            // Pegar apenas o primeiro nome
            const primeiroNome = perfil.nome.split(' ')[0];
            nomeNavbar.textContent = primeiroNome;
        }
        
        // Preencher campos do formulário
        document.getElementById('nome').value = perfil.nome || '';
        
        // Preencher CPF com máscara
        const cpfInput = document.getElementById('cpf');
        if (cpfInput && perfil.cpf) {
            cpfInput.value = formatarCPF(perfil.cpf);
        }
        
        // Preencher telefone com máscara
        const telefoneInput = document.getElementById('telefone');
        if (telefoneInput && perfil.telefone) {
            telefoneInput.value = formatarTelefone(perfil.telefone);
        }
        
        // Email (campo desabilitado - não pode ser alterado)
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.value = perfil.email || '';
            emailInput.disabled = true;
        }
        
        // Carregar e selecionar convênio
        if (perfil.plano_saude) {
            await carregarConvenios(perfil.id_plano_saude_fk);
        } else {
            await carregarConvenios(null);
        }
        
    } catch (error) {
        console.error('❌ Erro ao carregar perfil:', error);
        showMessage('Erro ao carregar dados do perfil.', 'error');
    }
}

async function carregarConvenios(planoIdSelecionado) {
    try {
        console.log('🏥 Carregando convênios do PostgreSQL...');
        const planos = await api.get(API_CONFIG.ENDPOINTS.PACIENTE_PLANOS_SAUDE);
        const selectConvenio = document.getElementById('convenio');
        
        if (!selectConvenio) {
            console.error('❌ Select de convênio não encontrado');
            return;
        }
        
        // Limpar opções existentes e adicionar opção "Particular" (sem ID)
        selectConvenio.innerHTML = '<option value="">Particular (sem convênio)</option>';
        
        // Adicionar planos do banco de dados, exceto "Particular" duplicado
        planos.forEach(plano => {
            // Ignorar plano "Particular" do banco (evitar duplicação)
            if (plano.nome.toLowerCase().includes('particular')) {
                return;
            }
            
            const option = document.createElement('option');
            option.value = plano.id_plano_saude;
            option.textContent = plano.nome;
            
            if (plano.id_plano_saude === planoIdSelecionado) {
                option.selected = true;
            }
            selectConvenio.appendChild(option);
        });
        
        // Se nenhum plano foi selecionado (null), selecionar "Particular"
        if (!planoIdSelecionado) {
            selectConvenio.value = '';
        }
        
        console.log(`✅ Convênios carregados. Selecionado: ID=${planoIdSelecionado || 'Particular'}`);
        
    } catch (error) {
        console.error('❌ Erro ao carregar convênios:', error);
        showMessage('Erro ao carregar lista de convênios.', 'error');
    }
}

async function verificarStatusBloqueio() {
    try {
        const status = await verificarBloqueio(pacienteId);
        
        if (status.bloqueado) {
            // Exibir aviso de bloqueio
            const avisoHTML = `
                <div class="alert alert-warning" style="background: #fff3cd; border: 1px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                    <strong>⚠️ CONTA BLOQUEADA</strong><br>
                    Sua conta está bloqueada devido a ${status.motivo}.<br>
                    Entre em contato com a administração para regularizar sua situação.
                </div>
            `;
            
            const container = document.querySelector('.main-content');
            container.insertAdjacentHTML('afterbegin', avisoHTML);
        }
    } catch (error) {
        console.error('Erro ao verificar bloqueio:', error);
    }
}

function setupFormListeners() {
    // Aplicar máscara de telefone
    aplicarMascaraTelefone();
    
    // Form de atualização de perfil
    document.getElementById('perfilForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Remover máscara do telefone antes de enviar
        const telefoneFormatado = document.getElementById('telefone').value;
        const telefoneLimpo = telefoneFormatado.replace(/\D/g, '');
        
        // Obter convênio selecionado (vazio = null, senão = ID do plano)
        const convenioSelect = document.getElementById('convenio');
        const convenioValue = convenioSelect.value;
        const planoId = convenioValue ? parseInt(convenioValue) : null;
        
        const dadosAtualizados = {
            nome: document.getElementById('nome').value,
            telefone: telefoneLimpo,
            id_plano_saude_fk: planoId
        };
        
        console.log('📤 Enviando atualização para PostgreSQL:', dadosAtualizados);
        
        try {
            const resultado = await api.put(API_CONFIG.ENDPOINTS.PACIENTE_PERFIL_ATUALIZAR(pacienteId), dadosAtualizados);
            console.log('✅ Perfil atualizado:', resultado);
            showMessage('Informações atualizadas com sucesso!', 'success');
            await carregarDadosPerfil();
        } catch (error) {
            console.error('❌ Erro ao atualizar perfil:', error);
            let mensagemErro = 'Erro ao atualizar informações. Tente novamente.';
            
            if (error.response && error.response.detail) {
                if (typeof error.response.detail === 'string') {
                    mensagemErro = error.response.detail;
                } else if (Array.isArray(error.response.detail)) {
                    mensagemErro = error.response.detail.map(err => err.msg || err).join(', ');
                }
            }
            
            showMessage(mensagemErro, 'error');
        }
    });
    
    // Form de alteração de senha
    document.getElementById('senhaForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const senhaAtual = document.getElementById('senhaAtual').value;
        const novaSenha = document.getElementById('novaSenha').value;
        const confirmarNovaSenha = document.getElementById('confirmarNovaSenha').value;
        
        // Validações
        if (!senhaAtual || !novaSenha || !confirmarNovaSenha) {
            showMessage('Preencha todos os campos de senha!', 'error');
            return;
        }
        
        if (novaSenha.length < 8 || novaSenha.length > 20) {
            showMessage('A senha deve ter entre 8 e 20 caracteres!', 'error');
            return;
        }
        
        if (novaSenha !== confirmarNovaSenha) {
            showMessage('A nova senha e a confirmação não coincidem!', 'error');
            return;
        }
        
        if (senhaAtual === novaSenha) {
            showMessage('A nova senha deve ser diferente da senha atual!', 'error');
            return;
        }
        
        console.log('🔐 Alterando senha...');
        
        try {
            const resultado = await api.put(API_CONFIG.ENDPOINTS.PACIENTE_ALTERAR_SENHA(pacienteId), {
                senha_atual: senhaAtual,
                senha_nova: novaSenha
            });
            
            console.log('✅ Senha alterada:', resultado);
            showMessage('Senha alterada com sucesso!', 'success');
            document.getElementById('senhaForm').reset();
            
        } catch (error) {
            console.error('❌ Erro ao alterar senha:', error);
            let mensagemErro = 'Erro ao alterar senha. Tente novamente.';
            
            if (error.response && error.response.detail) {
                if (typeof error.response.detail === 'string') {
                    mensagemErro = error.response.detail;
                } else if (Array.isArray(error.response.detail)) {
                    mensagemErro = error.response.detail.map(err => err.msg || err).join(', ');
                }
            }
            
            showMessage(mensagemErro, 'error');
        }
    });
}

function showMessage(message, type) {
    if (type === 'error') {
        alert('ERRO: ' + message);
    } else {
        alert(message);
    }
}

// Função para aplicar máscara de telefone
function aplicarMascaraTelefone() {
    const telefoneInput = document.getElementById('telefone');
    
    if (telefoneInput) {
        // Aplica máscara no valor inicial (se houver)
        if (telefoneInput.value) {
            telefoneInput.value = formatarTelefone(telefoneInput.value);
        }
        
        // Aplica máscara durante a digitação
        telefoneInput.addEventListener('input', function(e) {
            e.target.value = formatarTelefone(e.target.value);
        });
        
        // Validação ao sair do campo
        telefoneInput.addEventListener('blur', function(e) {
            const valor = e.target.value.replace(/\D/g, '');
            
            if (valor.length > 0 && valor.length < 10) {
                showMessage('Telefone deve ter no mínimo 10 dígitos (com DDD)', 'error');
                e.target.focus();
            }
        });
    }
}
