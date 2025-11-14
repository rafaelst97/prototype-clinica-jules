// Gerenciar Médicos - Admin - Integrado com API
let medicos = [];
let especialidades = [];
let conveniosMedicos = {}; // Armazena convênios por médico (temporário até backend implementar)

// Carregar convênios do localStorage
function carregarConveniosLocalStorage() {
    const stored = localStorage.getItem('convenios_medicos');
    if (stored) {
        try {
            conveniosMedicos = JSON.parse(stored);
        } catch (e) {
            conveniosMedicos = {};
        }
    }
}

// Salvar convênios no localStorage
function salvarConveniosLocalStorage() {
    localStorage.setItem('convenios_medicos', JSON.stringify(conveniosMedicos));
}

document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM carregado - iniciando admin-medicos.js');
    requireAuth();
    requireUserType('administrador');
    
    console.log('Aguardando 100ms antes de carregar especialidades...');
    await new Promise(resolve => setTimeout(resolve, 100));
    
    carregarConveniosLocalStorage(); // Carregar convênios salvos
    await carregarEspecialidades();
    await carregarMedicos();
    configurarFormularioCadastro();
});

// Carregar especialidades
async function carregarEspecialidades() {
    try {
        console.log('Carregando especialidades do endpoint:', API_CONFIG.ENDPOINTS.ESPECIALIDADES);
        especialidades = await api.get(API_CONFIG.ENDPOINTS.ESPECIALIDADES);
        console.log('Especialidades carregadas:', especialidades);
        console.log('Tipo de especialidades:', typeof especialidades, Array.isArray(especialidades));
        
        const select = document.getElementById('especialidade');
        console.log('Select encontrado:', select);
        
        if (select && especialidades && especialidades.length > 0) {
            select.innerHTML = '<option value="">Selecione...</option>';
            especialidades.forEach(esp => {
                console.log('Adicionando especialidade:', esp);
                const option = document.createElement('option');
                option.value = esp.id_especialidade;
                option.textContent = esp.nome;
                select.appendChild(option);
            });
            console.log('Especialidades adicionadas ao select:', especialidades.length);
        } else {
            console.warn('Nenhuma especialidade carregada ou select não encontrado');
            if (select) {
                select.innerHTML = '<option value="">Nenhuma especialidade encontrada</option>';
            }
        }
    } catch (error) {
        console.error('Erro ao carregar especialidades:', error);
        const select = document.getElementById('especialidade');
        if (select) {
            select.innerHTML = '<option value="">Erro ao carregar especialidades</option>';
        }
        showMessage('Erro ao carregar especialidades: ' + error.message, 'error');
    }
}

// Carregar lista de médicos
async function carregarMedicos() {
    try {
        showLoading();
        medicos = await api.get(API_CONFIG.ENDPOINTS.ADMIN_MEDICOS_LISTAR);
        renderizarMedicos();
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar médicos:', error);
        showMessage('Erro ao carregar médicos: ' + error.message, 'error');
        hideLoading();
    }
}

// Renderizar lista de médicos
function renderizarMedicos() {
    const tbody = document.querySelector('tbody');
    
    if (!tbody) return;
    
    if (medicos.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 30px;">Nenhum médico cadastrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = medicos.map(medico => {
        const especialidade = medico.especialidade || {};
        const convenios = conveniosMedicos[medico.id_medico] || [];
        const conveniosTexto = convenios.length > 0 ? convenios.join(', ') : 'Não informado';
        
        return `
            <tr>
                <td>${medico.nome || 'N/A'}</td>
                <td>${medico.crm || 'N/A'}</td>
                <td>${especialidade.nome || 'N/A'}</td>
                <td>${conveniosTexto}</td>
                <td><span style="color: var(--tertiary-color);"><i class="fas fa-check-circle"></i> Ativo</span></td>
                <td>
                    <button class="btn btn-secondary" style="padding: 5px 10px; margin-right: 5px;" onclick="verDetalhesMedico(${medico.id_medico})" title="Ver detalhes">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                    <button class="btn btn-primary" style="padding: 5px 10px; margin-right: 5px;" onclick="editarMedico(${medico.id_medico})" title="Editar médico">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-outline" style="padding: 5px 10px;" onclick="desativarMedico(${medico.id_medico})" title="Excluir médico">
                        <i class="fas fa-trash"></i> Excluir
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Configurar formulário de cadastro
function configurarFormularioCadastro() {
    const btnNovo = document.querySelector('.btn-primary');
    const formCadastro = document.getElementById('formCadastro');
    const form = document.getElementById('cadastroMedicoForm');
    
    if (btnNovo && formCadastro) {
        btnNovo.addEventListener('click', async () => {
            console.log('Botão Novo Médico clicado - abrindo formulário');
            formCadastro.style.display = 'block';
            form.reset();
            
            // Recarregar especialidades ao abrir o formulário
            console.log('Recarregando especialidades...');
            await carregarEspecialidades();
        });
    }
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await cadastrarMedico();
        });
    }
    
    // Botão cancelar
    const btnCancelar = formCadastro?.querySelector('.btn-outline');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', () => {
            resetarFormulario();
        });
    }
    
    // Adicionar máscara de telefone
    const telefoneInput = document.getElementById('telefone');
    if (telefoneInput && typeof maskPhone !== 'undefined') {
        telefoneInput.addEventListener('input', (e) => {
            e.target.value = maskPhone(e.target.value);
        });
    }
    
    // Adicionar máscara de CPF
    const cpfInput = document.getElementById('cpf');
    if (cpfInput && typeof maskCPF !== 'undefined') {
        cpfInput.addEventListener('input', (e) => {
            e.target.value = maskCPF(e.target.value);
        });
    }
}

// Cadastrar novo médico
async function cadastrarMedico() {
    const form = document.getElementById('cadastroMedicoForm');
    const btnSubmit = form.querySelector('button[type="submit"]');
    const originalText = btnSubmit.innerHTML;
    
    try {
        // Coletar convênios selecionados
        const conveniosSelecionados = Array.from(
            document.querySelectorAll('input[name="convenios"]:checked')
        ).map(cb => cb.value);
        
        const dados = {
            nome: document.getElementById('nome').value.trim(),
            cpf: document.getElementById('cpf').value.replace(/\D/g, ''), // Remove formatação
            email: document.getElementById('email').value.trim(),
            senha: document.getElementById('senha').value,
            crm: document.getElementById('crm').value.trim(),
            telefone: document.getElementById('telefone').value.replace(/\D/g, '') || null,
            id_especialidade_fk: parseInt(document.getElementById('especialidade').value)
        };
        
        // Validações
        if (!dados.nome || !dados.cpf || !dados.email || !dados.senha || !dados.crm || !dados.id_especialidade_fk) {
            showMessage('Por favor, preencha todos os campos obrigatórios!', 'error');
            return;
        }
        
        if (conveniosSelecionados.length === 0) {
            showMessage('Selecione pelo menos um convênio aceito!', 'error');
            return;
        }
        
        if (dados.cpf.length !== 11) {
            showMessage('CPF inválido! Deve ter 11 dígitos.', 'error');
            return;
        }
        
        if (dados.senha.length < 8) {
            showMessage('A senha deve ter no mínimo 8 caracteres!', 'error');
            return;
        }
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando...';
        
        const medicoNovo = await api.post(API_CONFIG.ENDPOINTS.ADMIN_MEDICO_CRIAR, dados);
        
        // Salvar convênios no localStorage
        conveniosMedicos[medicoNovo.id_medico] = conveniosSelecionados;
        salvarConveniosLocalStorage();
        
        showMessage('Médico cadastrado com sucesso!', 'success');
        document.getElementById('formCadastro').style.display = 'none';
        form.reset();
        await carregarMedicos();
        
    } catch (error) {
        console.error('Erro ao cadastrar médico:', error);
        showMessage('Erro ao cadastrar médico: ' + error.message, 'error');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
    }
}

// Ver detalhes do médico
async function verDetalhesMedico(medicoId) {
    try {
        showLoading();
        const medico = await api.get(`/admin/medicos/${medicoId}`);
        hideLoading();
        
        const especialidade = medico.especialidade || {};
        const convenios = conveniosMedicos[medicoId] || [];
        const conveniosHtml = convenios.length > 0 
            ? convenios.map(c => `<span style="background: #e0e0e0; padding: 3px 10px; border-radius: 12px; margin-right: 5px; display: inline-block; margin-bottom: 5px;">${c}</span>`).join('')
            : '<span style="color: #999;">Não informado</span>';
        
        const detalhesHtml = `
            <div style="background: white; padding: 30px; border-radius: 10px; max-width: 700px; margin: 0 auto;">
                <h3 style="margin-bottom: 25px; color: var(--primary-color); border-bottom: 2px solid var(--primary-color); padding-bottom: 10px;">
                    <i class="fas fa-user-md"></i> Detalhes do Médico
                </h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div>
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #666;">Nome Completo:</strong><br>
                            <span style="font-size: 1.1em;">${medico.nome || 'N/A'}</span>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #666;">CPF:</strong><br>
                            ${formatarCPF(medico.cpf)}
                        </div>
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #666;">Email:</strong><br>
                            ${medico.email || 'N/A'}
                        </div>
                    </div>
                    <div>
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #666;">CRM:</strong><br>
                            <span style="font-size: 1.1em; color: var(--primary-color);">${medico.crm || 'N/A'}</span>
                        </div>
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #666;">Telefone:</strong><br>
                            ${formatarTelefone(medico.telefone) || 'Não informado'}
                        </div>
                        <div style="margin-bottom: 15px;">
                            <strong style="color: #666;">Especialidade:</strong><br>
                            <span style="background: var(--primary-color); color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.9em;">
                                ${especialidade.nome || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                    <strong style="color: #666; display: block; margin-bottom: 10px;">Convênios Aceitos:</strong>
                    <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                        ${conveniosHtml}
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 25px; border-top: 1px solid #eee; padding-top: 20px;">
                    <button onclick="fecharModal()" class="btn btn-secondary" style="flex: 1;">
                        <i class="fas fa-times"></i> Fechar
                    </button>
                    <button onclick="fecharModal(); editarMedico(${medico.id_medico});" class="btn btn-primary" style="flex: 1;">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                </div>
            </div>
        `;
        
        mostrarModal(detalhesHtml);
        
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
        showMessage('Erro ao carregar detalhes do médico: ' + error.message, 'error');
        hideLoading();
    }
}

// Editar médico
async function editarMedico(medicoId) {
    try {
        showLoading();
        const medico = await api.get(`/admin/medicos/${medicoId}`);
        hideLoading();
        
        // Preencher formulário com dados atuais
        document.getElementById('nome').value = medico.nome || '';
        document.getElementById('cpf').value = formatarCPF(medico.cpf) || '';
        document.getElementById('email').value = medico.email || '';
        document.getElementById('crm').value = medico.crm || '';
        document.getElementById('telefone').value = formatarTelefone(medico.telefone) || '';
        document.getElementById('especialidade').value = medico.id_especialidade_fk || '';
        
        // Carregar convênios salvos
        const conveniosSalvos = conveniosMedicos[medicoId] || [];
        document.querySelectorAll('input[name="convenios"]').forEach(checkbox => {
            checkbox.checked = conveniosSalvos.includes(checkbox.value);
        });
        
        // Mostrar campo senha mas torná-lo opcional na edição
        const senhaGroup = document.getElementById('senha').closest('.form-group');
        if (senhaGroup) {
            senhaGroup.style.display = 'block';
            document.getElementById('senha').required = false;
            document.getElementById('senha').placeholder = 'Deixe em branco para manter a senha atual';
        }
        
        // Alterar título e botão do formulário
        document.querySelector('#formCadastro .card-header h3').innerHTML = '<i class="fas fa-edit"></i> Editar Médico';
        const btnSubmit = document.querySelector('#btnSalvar');
        btnSubmit.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
        btnSubmit.onclick = async (e) => {
            e.preventDefault();
            await salvarEdicaoMedico(medicoId);
        };
        
        // Mostrar formulário
        document.getElementById('formCadastro').style.display = 'block';
        document.getElementById('formCadastro').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Erro ao carregar médico para edição:', error);
        showMessage('Erro ao carregar dados do médico: ' + error.message, 'error');
        hideLoading();
    }
}

// Salvar edição do médico
async function salvarEdicaoMedico(medicoId) {
    const form = document.getElementById('cadastroMedicoForm');
    const btnSubmit = document.querySelector('#btnSalvar');
    const originalText = btnSubmit.innerHTML;
    
    try {
        // Coletar convênios selecionados
        const conveniosSelecionados = Array.from(
            document.querySelectorAll('input[name="convenios"]:checked')
        ).map(cb => cb.value);
        
        const dados = {
            nome: document.getElementById('nome').value.trim(),
            cpf: document.getElementById('cpf').value.replace(/\D/g, ''),
            email: document.getElementById('email').value.trim(),
            crm: document.getElementById('crm').value.trim(),
            id_especialidade_fk: parseInt(document.getElementById('especialidade').value)
        };
        
        // Adicionar telefone apenas se preenchido
        const telefone = document.getElementById('telefone').value.replace(/\D/g, '');
        if (telefone) {
            dados.telefone = telefone;
        }
        
        // Adicionar senha apenas se foi preenchida
        const senha = document.getElementById('senha').value;
        if (senha && senha.trim()) {
            if (senha.length < 8) {
                showMessage('A senha deve ter no mínimo 8 caracteres!', 'error');
                return;
            }
            dados.senha = senha;
        }
        
        // Validações
        if (!dados.nome || !dados.cpf || !dados.email || !dados.crm || !dados.id_especialidade_fk) {
            showMessage('Por favor, preencha todos os campos obrigatórios!', 'error');
            return;
        }
        
        if (conveniosSelecionados.length === 0) {
            showMessage('Selecione pelo menos um convênio aceito!', 'error');
            return;
        }
        
        if (dados.cpf.length !== 11) {
            showMessage('CPF inválido! Deve ter 11 dígitos.', 'error');
            return;
        }
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
        
        console.log('DEBUG: Dados sendo enviados para atualização:', dados);
        
        await api.put(API_CONFIG.ENDPOINTS.ADMIN_MEDICO_ATUALIZAR(medicoId), dados);
        
        // Atualizar convênios no localStorage
        conveniosMedicos[medicoId] = conveniosSelecionados;
        salvarConveniosLocalStorage();
        
        showMessage('Médico atualizado com sucesso!', 'success');
        
        // Resetar formulário para modo cadastro
        resetarFormulario();
        
        await carregarMedicos();
        
    } catch (error) {
        console.error('Erro ao atualizar médico:', error);
        showMessage('Erro ao atualizar médico: ' + error.message, 'error');
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
    }
}

// Resetar formulário para modo cadastro
function resetarFormulario() {
    const form = document.getElementById('cadastroMedicoForm');
    const formCadastro = document.getElementById('formCadastro');
    
    // Esconder formulário
    formCadastro.style.display = 'none';
    
    // Limpar campos
    form.reset();
    
    // Restaurar título
    document.querySelector('#formCadastro .card-header h3').innerHTML = 'Cadastrar Novo Médico';
    
    // Restaurar botão
    const btnSubmit = document.querySelector('#btnSalvar');
    btnSubmit.innerHTML = '<i class="fas fa-check"></i> Cadastrar Médico';
    btnSubmit.onclick = null;
    btnSubmit.disabled = false;
    
    // Mostrar campo senha e torná-lo obrigatório
    const senhaGroup = document.getElementById('senha').closest('.form-group');
    if (senhaGroup) {
        senhaGroup.style.display = 'block';
        const senhaInput = document.getElementById('senha');
        senhaInput.required = true;
        senhaInput.placeholder = 'Senha de acesso';
    }
    
    // Reabilitar campos que foram desabilitados na edição
    document.getElementById('cpf').disabled = false;
    document.getElementById('email').disabled = false;
    document.getElementById('crm').disabled = false;
    document.getElementById('telefone').disabled = false;
    
    // Restaurar estilo dos campos
    document.getElementById('cpf').style.backgroundColor = '';
    document.getElementById('email').style.backgroundColor = '';
    document.getElementById('crm').style.backgroundColor = '';
    document.getElementById('telefone').style.backgroundColor = '';
}

// Desativar médico
async function desativarMedico(medicoId) {
    if (!confirm('Deseja realmente desativar este médico? Consultas futuras serão mantidas.')) {
        return;
    }
    
    try {
        showLoading();
        await api.delete(`/admin/medicos/${medicoId}`);
        showMessage('Médico desativado com sucesso!', 'success');
        await carregarMedicos();
        hideLoading();
    } catch (error) {
        console.error('Erro ao desativar:', error);
        showMessage('Erro ao desativar médico: ' + error.message, 'error');
        hideLoading();
    }
}

// Ativar médico
async function ativarMedico(medicoId) {
    if (!confirm('Deseja realmente reativar este médico?')) {
        return;
    }
    
    try {
        showLoading();
        await api.put(`/admin/medicos/${medicoId}/ativar`, {});
        showMessage('Médico reativado com sucesso!', 'success');
        await carregarMedicos();
        hideLoading();
    } catch (error) {
        console.error('Erro ao ativar:', error);
        showMessage('Erro ao reativar médico: ' + error.message, 'error');
        hideLoading();
    }
}

// Funções auxiliares
function formatarDataHora(dataHora) {
    if (!dataHora) return 'N/A';
    const d = new Date(dataHora);
    return d.toLocaleDateString('pt-BR') + ' às ' + d.toLocaleTimeString('pt-BR');
}

function mostrarModal(html) {
    const modal = document.createElement('div');
    modal.id = 'modalDetalhes';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        overflow-y: auto;
        padding: 20px;
    `;
    modal.innerHTML = html;
    modal.onclick = (e) => {
        if (e.target === modal) fecharModal();
    };
    document.body.appendChild(modal);
}

function fecharModal() {
    const modal = document.getElementById('modalDetalhes');
    if (modal) modal.remove();
}

function showLoading() {
    const loading = document.createElement('div');
    loading.id = 'loading';
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255,255,255,0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    loading.innerHTML = '<i class="fas fa-spinner fa-spin" style="font-size: 48px; color: var(--primary-color);"></i>';
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.remove();
}

function showMessage(message, type) {
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-warning';
    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-exclamation-triangle';
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10001;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    alert.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
    document.body.appendChild(alert);
    
    setTimeout(() => alert.remove(), 5000);
}

function formatarCPF(cpf) {
    if (!cpf) return 'N/A';
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

// Função para formatar telefone
function formatarTelefone(telefone) {
    if (!telefone) return '';
    telefone = telefone.replace(/\D/g, '');
    if (telefone.length === 11) {
        return telefone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    } else if (telefone.length === 10) {
        return telefone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return telefone;
}

// Função para abrir modal de nova especialidade
function abrirModalNovaEspecialidade() {
    const html = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
            <h3 style="margin-bottom: 20px; color: var(--primary-color);">
                <i class="fas fa-plus-circle"></i> Nova Especialidade
            </h3>
            
            <form id="formNovaEspecialidade" onsubmit="event.preventDefault(); criarEspecialidade();">
                <div class="form-group">
                    <label for="nomeEspecialidade">Nome da Especialidade *</label>
                    <input type="text" id="nomeEspecialidade" class="form-control" required 
                           placeholder="Ex: Neurologia" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                </div>
                
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="button" onclick="fecharModal()" class="btn btn-outline" style="flex: 1;">
                        <i class="fas fa-times"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" style="flex: 1;">
                        <i class="fas fa-check"></i> Cadastrar
                    </button>
                </div>
            </form>
        </div>
    `;
    
    mostrarModal(html);
}

// Função para criar especialidade
async function criarEspecialidade() {
    const nome = document.getElementById('nomeEspecialidade').value.trim();
    
    if (!nome) {
        showMessage('Por favor, informe o nome da especialidade!', 'error');
        return;
    }
    
    try {
        showLoading();
        
        const dados = {
            nome: nome
        };
        
        await api.post(API_CONFIG.ENDPOINTS.ADMIN_ESPECIALIDADES, dados);
        
        showMessage('Especialidade cadastrada com sucesso!', 'success');
        fecharModal();
        
        // Recarregar lista de especialidades
        await carregarEspecialidades();
        
        // Selecionar a nova especialidade
        const select = document.getElementById('especialidade');
        const novaEspecialidade = especialidades.find(e => e.nome === nome);
        if (novaEspecialidade && select) {
            select.value = novaEspecialidade.id_especialidade;
        }
        
        hideLoading();
    } catch (error) {
        console.error('Erro ao criar especialidade:', error);
        
        if (error.message.includes('409') || error.message.includes('já cadastrada')) {
            showMessage('Esta especialidade já está cadastrada!', 'error');
        } else {
            showMessage('Erro ao cadastrar especialidade: ' + error.message, 'error');
        }
        
        hideLoading();
    }
}
