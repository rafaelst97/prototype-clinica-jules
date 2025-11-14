// Gerenciar Planos de Saúde - Admin - Integrado com API
let planosSaude = [];
let planoEditando = null;

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('administrador');
    
    await carregarPlanosSaude();
    configurarFormularioCadastro();
});

// Carregar lista de planos de saúde
async function carregarPlanosSaude() {
    try {
        showLoading();
        planosSaude = await api.get(API_CONFIG.ENDPOINTS.ADMIN_PLANOS_LISTAR);
        renderizarPlanosSaude();
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar planos de saúde:', error);
        showMessage('Erro ao carregar planos de saúde: ' + error.message, 'error');
        hideLoading();
    }
}

// Renderizar lista de planos
function renderizarPlanosSaude() {
    const tbody = document.querySelector('tbody');
    
    if (!tbody) return;
    
    if (planosSaude.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 30px;">Nenhum plano de saúde cadastrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = planosSaude.map(plano => {
        const ativo = plano.ativo !== false;
        
        const statusHtml = ativo ? 
            '<span style="color: var(--tertiary-color);"><i class="fas fa-check-circle"></i> Ativo</span>' :
            '<span style="color: var(--accent-color);"><i class="fas fa-times-circle"></i> Inativo</span>';
        
        return `
            <tr style="${!ativo ? 'opacity: 0.6; background: #f5f5f5;' : ''}">
                <td>${plano.nome || 'N/A'}</td>
                <td>${plano.tipo || 'N/A'}</td>
                <td>${plano.telefone || 'N/A'}</td>
                <td>${statusHtml}</td>
                <td>
                    ${ativo ? `
                        <button class="btn btn-secondary" style="padding: 5px 10px; margin-right: 5px;" onclick="editarPlano(${plano.id})">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="btn btn-outline" style="padding: 5px 10px;" onclick="desativarPlano(${plano.id})">
                            <i class="fas fa-ban"></i> Desativar
                        </button>
                    ` : `
                        <button class="btn btn-tertiary" style="padding: 5px 10px;" onclick="ativarPlano(${plano.id})">
                            <i class="fas fa-check"></i> Ativar
                        </button>
                    `}
                </td>
            </tr>
        `;
    }).join('');
}

// Configurar formulário de cadastro
function configurarFormularioCadastro() {
    const btnNovo = document.querySelector('.btn-primary');
    const formCadastro = document.getElementById('formCadastro');
    const form = document.getElementById('cadastroPlanoForm');
    
    if (btnNovo && formCadastro) {
        btnNovo.addEventListener('click', () => {
            formCadastro.style.display = 'block';
            form.reset();
            planoEditando = null;
            document.getElementById('tituloForm').textContent = 'Novo Plano de Saúde';
        });
    }
    
    if (form) {
        form.addEventListener('submit', salvarPlano);
    }
    
    // Botão cancelar
    const btnCancelar = document.getElementById('btnCancelar');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', () => {
            formCadastro.style.display = 'none';
            form.reset();
            planoEditando = null;
        });
    }
}

// Salvar plano
async function salvarPlano(event) {
    event.preventDefault();
    
    const dados = {
        nome: document.getElementById('nome').value.trim(),
        tipo: document.getElementById('tipo').value,
        registro_ans: document.getElementById('registro_ans').value.trim() || null,
        telefone: document.getElementById('telefone').value.trim() || null
    };
    
    if (!dados.nome || !dados.tipo) {
        showMessage('Por favor, preencha todos os campos obrigatórios', 'error');
        return;
    }
    
    try {
        showLoading();
        
        if (planoEditando) {
            await api.put(API_CONFIG.ENDPOINTS.ADMIN_PLANO_ATUALIZAR(planoEditando), dados);
            showMessage('Plano atualizado com sucesso!', 'success');
        } else {
            await api.post(API_CONFIG.ENDPOINTS.ADMIN_PLANO_CRIAR, dados);
            showMessage('Plano cadastrado com sucesso!', 'success');
        }
        
        document.getElementById('formCadastro').style.display = 'none';
        document.getElementById('cadastroPlanoForm').reset();
        planoEditando = null;
        
        await carregarPlanosSaude();
        hideLoading();
    } catch (error) {
        console.error('Erro ao salvar plano:', error);
        showMessage('Erro ao salvar plano: ' + error.message, 'error');
        hideLoading();
    }
}

// Editar plano
async function editarPlano(planoId) {
    try {
        const plano = planosSaude.find(p => p.id === planoId);
        
        if (!plano) return;
        
        planoEditando = planoId;
        
        document.getElementById('tituloForm').textContent = 'Editar Plano de Saúde';
        document.getElementById('nome').value = plano.nome || '';
        document.getElementById('tipo').value = plano.tipo || '';
        document.getElementById('registro_ans').value = plano.registro_ans || '';
        document.getElementById('telefone').value = plano.telefone || '';
        
        document.getElementById('formCadastro').style.display = 'block';
        document.getElementById('nome').focus();
    } catch (error) {
        console.error('Erro ao editar plano:', error);
        showMessage('Erro ao carregar dados do plano', 'error');
    }
}

// Desativar plano
async function desativarPlano(planoId) {
    if (!confirm('Deseja realmente desativar este plano de saúde?')) {
        return;
    }
    
    try {
        showLoading();
        await api.delete(API_CONFIG.ENDPOINTS.ADMIN_PLANO_DELETAR(planoId));
        showMessage('Plano desativado com sucesso!', 'success');
        await carregarPlanosSaude();
        hideLoading();
    } catch (error) {
        console.error('Erro ao desativar plano:', error);
        showMessage('Erro ao desativar plano: ' + error.message, 'error');
        hideLoading();
    }
}

// Ativar plano
async function ativarPlano(planoId) {
    try {
        showLoading();
        await api.put(API_CONFIG.ENDPOINTS.ADMIN_PLANO_ATUALIZAR(planoId), { ativo: true });
        showMessage('Plano ativado com sucesso!', 'success');
        await carregarPlanosSaude();
        hideLoading();
    } catch (error) {
        console.error('Erro ao ativar plano:', error);
        showMessage('Erro ao ativar plano: ' + error.message, 'error');
        hideLoading();
    }
}

// Funções auxiliares
function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'block';
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
}

function showMessage(message, type = 'info') {
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        border-radius: 5px;
        z-index: 10000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}
