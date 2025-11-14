// Gerenciar Convênios - Admin
let convenios = [];
let convenioEditando = null;

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('administrador');
    
    await carregarConvenios();
    configurarFormularioCadastro();
});

// Carregar lista de convênios com estatísticas
async function carregarConvenios() {
    try {
        showLoading();
        convenios = await api.get(API_CONFIG.ENDPOINTS.ADMIN_PLANOS_SAUDE_ESTATISTICAS);
        renderizarConvenios();
        renderizarEstatisticas();
        hideLoading();
    } catch (error) {
        console.error('Erro ao carregar convênios:', error);
        showMessage('Erro ao carregar convênios: ' + error.message, 'error');
        hideLoading();
    }
}

// Renderizar lista de convênios
function renderizarConvenios() {
    const tbody = document.querySelector('tbody');
    
    if (!tbody) return;
    
    if (convenios.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 30px;">Nenhum convênio cadastrado</td></tr>';
        return;
    }
    
    tbody.innerHTML = convenios.map(convenio => {
        const statusHtml = '<span style="color: var(--tertiary-color);"><i class="fas fa-check-circle"></i> Ativo</span>';
        
        // Truncar cobertura_info se for muito longa
        const cobertura = convenio.cobertura_info 
            ? (convenio.cobertura_info.length > 50 
                ? convenio.cobertura_info.substring(0, 50) + '...' 
                : convenio.cobertura_info)
            : 'Sem informações';
        
        return `
            <tr>
                <td><strong>${convenio.nome || 'N/A'}</strong></td>
                <td>${cobertura}</td>
                <td style="text-align: center;">${convenio.qtd_pacientes || 0}</td>
                <td style="text-align: center;">${convenio.consultas_mes || 0}</td>
                <td>${statusHtml}</td>
                <td>
                    <button class="btn btn-secondary" style="padding: 5px 10px; margin-right: 5px;" onclick="editarConvenio(${convenio.id_plano_saude})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-outline" style="padding: 5px 10px; margin-right: 5px;" onclick="verDetalhes(${convenio.id_plano_saude})">
                        <i class="fas fa-eye"></i> Detalhes
                    </button>
                    <button class="btn" style="padding: 5px 10px; margin-right: 5px; background-color: #dc3545; color: white; border: none;" onclick="excluirConvenio(${convenio.id_plano_saude}, '${convenio.nome}')">
                        <i class="fas fa-trash"></i> Excluir
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Renderizar estatísticas
function renderizarEstatisticas() {
    const distribuicaoDiv = document.querySelector('.grid-2 > div:first-child');
    const consultasDiv = document.querySelector('.grid-2 > div:last-child');
    
    if (!distribuicaoDiv || !consultasDiv) return;
    
    // Ordenar por quantidade de pacientes
    const conveniosOrdenados = [...convenios].sort((a, b) => b.qtd_pacientes - a.qtd_pacientes);
    
    // Distribuição de pacientes
    let distribuicaoHtml = '<h4 style="color: var(--primary-color);">Distribuição de Pacientes</h4>';
    conveniosOrdenados.forEach(convenio => {
        distribuicaoHtml += `<p>${convenio.nome}: ${convenio.qtd_pacientes} (${convenio.percentual_pacientes}%)</p>`;
    });
    
    distribuicaoDiv.innerHTML = distribuicaoHtml;
    
    // Consultas este mês
    let consultasHtml = '<h4 style="color: var(--primary-color);">Consultas Este Mês</h4>';
    conveniosOrdenados.forEach(convenio => {
        consultasHtml += `<p>${convenio.nome}: ${convenio.consultas_mes} consultas</p>`;
    });
    
    consultasDiv.innerHTML = consultasHtml;
}

// Configurar formulário de cadastro
function configurarFormularioCadastro() {
    const btnNovo = document.querySelector('.btn-primary');
    
    if (btnNovo) {
        btnNovo.addEventListener('click', () => {
            convenioEditando = null;
            abrirModalFormulario('Novo Convênio', 'Cadastrar');
        });
    }
}

// Cadastrar novo convênio
async function cadastrarConvenio() {
    const form = document.getElementById('modalForm');
    const btnSubmit = form.querySelector('button[type="submit"]');
    const originalText = btnSubmit.innerHTML;
    
    try {
        const dados = {
            nome: document.getElementById('modalNomeConvenio').value,
            cobertura_info: document.getElementById('modalCoberturaConvenio').value.trim() || null
        };
        
        // Validações
        if (!dados.nome) {
            showMessage('Por favor, preencha o nome do convênio!', 'error');
            return;
        }
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cadastrando...';
        
        await api.post(API_CONFIG.ENDPOINTS.ADMIN_PLANOS_SAUDE, dados);
        
        showMessage('Convênio cadastrado com sucesso!', 'success');
        fecharModal();
        await carregarConvenios();
        
    } catch (error) {
        console.error('Erro ao cadastrar convênio:', error);
        showMessage('Erro ao cadastrar convênio: ' + error.message, 'error');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
    }
}

// Editar convênio
async function editarConvenio(convenioId) {
    try {
        convenioEditando = convenios.find(c => c.id_plano_saude === convenioId);
        
        if (!convenioEditando) {
            showMessage('Convênio não encontrado!', 'error');
            return;
        }
        
        abrirModalFormulario('Editar Convênio', 'Atualizar', {
            nome: convenioEditando.nome || '',
            cobertura: convenioEditando.cobertura_info || ''
        });
        
    } catch (error) {
        console.error('Erro ao editar convênio:', error);
        showMessage('Erro ao carregar dados do convênio: ' + error.message, 'error');
    }
}

// Atualizar convênio
async function atualizarConvenio() {
    const form = document.getElementById('modalForm');
    const btnSubmit = form.querySelector('button[type="submit"]');
    const originalText = btnSubmit.innerHTML;
    
    try {
        const dados = {
            nome: document.getElementById('modalNomeConvenio').value,
            cobertura_info: document.getElementById('modalCoberturaConvenio').value
        };
        
        // Validações
        if (!dados.nome) {
            showMessage('Por favor, preencha o nome do convênio!', 'error');
            return;
        }
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Atualizando...';
        
        await api.put(`${API_CONFIG.ENDPOINTS.ADMIN_PLANOS_SAUDE}/${convenioEditando.id_plano_saude}`, dados);
        
        showMessage('Convênio atualizado com sucesso!', 'success');
        fecharModal();
        convenioEditando = null;
        await carregarConvenios();
        
    } catch (error) {
        console.error('Erro ao atualizar convênio:', error);
        showMessage('Erro ao atualizar convênio: ' + error.message, 'error');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
    }
}

// Desativar convênio
// Excluir convênio
async function excluirConvenio(convenioId, nomeConvenio) {
    if (!confirm(`⚠️ ATENÇÃO!\n\nDeseja realmente excluir o convênio "${nomeConvenio}"?\n\nEsta ação não pode ser desfeita!\n\nOBS: Não será possível excluir se houver pacientes vinculados a este convênio.`)) {
        return;
    }
    
    try {
        showLoading();
        const response = await api.delete(`${API_CONFIG.ENDPOINTS.ADMIN_PLANOS_SAUDE}/${convenioId}`);
        showMessage(response.mensagem || 'Convênio excluído com sucesso!', 'success');
        await carregarConvenios();
        hideLoading();
    } catch (error) {
        console.error('Erro ao excluir:', error);
        hideLoading();
        
        // Mensagem específica para erro de pacientes vinculados
        if (error.message && error.message.includes('paciente')) {
            showMessage(error.message, 'error');
        } else {
            showMessage('Erro ao excluir convênio: ' + error.message, 'error');
        }
    }
}

// Funções auxiliares
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

// Ver detalhes do convênio
function verDetalhes(id) {
    const convenio = convenios.find(c => c.id_plano_saude === id);
    if (!convenio) {
        showMessage('Convênio não encontrado', 'error');
        return;
    }
    
    const detalhesHtml = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
            <h3 style="margin-bottom: 20px; color: var(--primary-color);">
                <i class="fas fa-building"></i> Detalhes do Convênio
            </h3>
            
            <div style="margin-bottom: 15px;">
                <strong>Nome:</strong> ${convenio.nome}
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Cobertura:</strong> ${convenio.cobertura_info || 'Sem informações'}
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Pacientes Cadastrados:</strong> ${convenio.qtd_pacientes}
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Percentual de Pacientes:</strong> ${convenio.percentual_pacientes}%
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Consultas Este Mês:</strong> ${convenio.consultas_mes}
            </div>
            
            <button onclick="fecharModal()" class="btn btn-secondary" style="margin-top: 20px;">
                <i class="fas fa-times"></i> Fechar
            </button>
        </div>
    `;
    
    mostrarModal(detalhesHtml);
}

// Mostrar modal
function mostrarModal(html) {
    const modal = document.createElement('div');
    modal.id = 'modal-overlay';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 20px;';
    modal.innerHTML = html;
    
    modal.onclick = (e) => {
        if (e.target === modal) fecharModal();
    };
    
    document.body.appendChild(modal);
}

// Abrir modal com formulário
function abrirModalFormulario(titulo, textoBotao, dados = {}) {
    const modalHtml = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;">
            <h3 style="margin-bottom: 20px; color: var(--primary-color);">
                <i class="fas ${convenioEditando ? 'fa-edit' : 'fa-plus-circle'}"></i> ${titulo}
            </h3>
            
            <form id="modalForm">
                <div class="form-group">
                    <label for="modalNomeConvenio">Nome do Convênio *</label>
                    <input type="text" id="modalNomeConvenio" name="modalNomeConvenio" required 
                           placeholder="Digite o nome do convênio" value="${dados.nome || ''}" 
                           style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px;">
                </div>

                <div class="form-group" style="margin-top: 15px;">
                    <label for="modalCoberturaConvenio">Informações de Cobertura</label>
                    <textarea id="modalCoberturaConvenio" name="modalCoberturaConvenio" rows="4" 
                              placeholder="Ex: Cobertura nacional, consultas ilimitadas, exames laboratoriais incluídos..."
                              style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; resize: vertical;">${dados.cobertura || ''}</textarea>
                </div>

                <div class="form-actions" style="margin-top: 20px; display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="button" class="btn btn-outline" onclick="fecharModal()">
                        <i class="fas fa-times"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> ${textoBotao}
                    </button>
                </div>
            </form>
        </div>
    `;
    
    mostrarModal(modalHtml);
    
    // Adicionar evento de submit ao formulário
    const form = document.getElementById('modalForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (convenioEditando) {
                await atualizarConvenio();
            } else {
                await cadastrarConvenio();
            }
        });
    }
}

// Fechar modal
function fecharModal() {
    const modal = document.getElementById('modal-overlay');
    if (modal) modal.remove();
    convenioEditando = null;
}
