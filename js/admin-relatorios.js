// Relatórios Admin - Integrado com API (4 novos relatórios)
let formulariosConfigurados = false;

document.addEventListener('DOMContentLoaded', async function() {
    requireAuth();
    requireUserType('administrador');
    
    if (!formulariosConfigurados) {
        await carregarMedicos();
        await carregarEspecialidades();
        await carregarEstatisticasGerais();
        configurarFormularios();
        formulariosConfigurados = true;
    }
});

// Carregar lista de médicos
async function carregarMedicos() {
    try {
        const medicos = await api.get(API_CONFIG.ENDPOINTS.ADMIN_MEDICOS_LISTAR);
        const select = document.getElementById('medico');
        
        if (select && medicos && medicos.length > 0) {
            select.innerHTML = '<option value="">Todos os médicos</option>';
            medicos.forEach(medico => {
                const option = document.createElement('option');
                option.value = medico.id_medico;
                option.textContent = `${medico.nome || 'Médico'} - CRM ${medico.crm}`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar médicos:', error);
    }
}

// Carregar lista de especialidades
async function carregarEspecialidades() {
    try {
        const especialidades = await api.get(API_CONFIG.ENDPOINTS.ESPECIALIDADES);
        const select = document.getElementById('especialidade');
        
        if (select && especialidades && especialidades.length > 0) {
            select.innerHTML = '<option value="">Todas as especialidades</option>';
            especialidades.forEach(esp => {
                const option = document.createElement('option');
                option.value = esp.id_especialidade;
                option.textContent = esp.nome;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar especialidades:', error);
    }
}

// Carregar estatísticas gerais
async function carregarEstatisticasGerais() {
    try {
        const stats = await api.get(API_CONFIG.ENDPOINTS.ADMIN_RELATORIO_ESTATISTICAS_GERAIS);
        const container = document.getElementById('estatisticasGerais');
        
        if (container && stats) {
            const especialidadesHtml = stats.especialidades_top && stats.especialidades_top.length > 0
                ? stats.especialidades_top.map((esp, idx) => 
                    `<p>${idx + 1}. ${esp.nome} - ${esp.total} consultas</p>`
                  ).join('')
                : '<p>Nenhum dado disponível</p>';
            
            container.innerHTML = `
                <div>
                    <h4 style="color: var(--primary-color);">Total de Consultas: ${stats.total_consultas}</h4>
                    <p>Realizadas: ${stats.realizadas} (${stats.perc_realizadas}%)</p>
                    <p>Agendadas: ${stats.agendadas} (${stats.perc_agendadas}%)</p>
                    <p>Canceladas: ${stats.canceladas} (${stats.perc_canceladas}%)</p>
                </div>
                <div>
                    <h4 style="color: var(--primary-color);">Especialidades Mais Procuradas:</h4>
                    ${especialidadesHtml}
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        const container = document.getElementById('estatisticasGerais');
        if (container) {
            container.innerHTML = '<p style="color: red; text-align: center;">Erro ao carregar estatísticas</p>';
        }
    }
}

// Configurar formulários de relatórios
function configurarFormularios() {
    // Relatório 1: Consultas por Médico
    const formMedico = document.getElementById('relatorioMedicoForm');
    if (formMedico) {
        // Remover listeners anteriores clonando o elemento
        const novoFormMedico = formMedico.cloneNode(true);
        formMedico.parentNode.replaceChild(novoFormMedico, formMedico);
        
        novoFormMedico.addEventListener('submit', async (e) => {
            e.preventDefault();
            const medicoId = document.getElementById('medico').value;
            const dataInicio = document.getElementById('periodoInicio').value;
            const dataFim = document.getElementById('periodoFim').value;
            
            const params = {};
            if (medicoId) params.medico_id = medicoId;
            if (dataInicio) params.data_inicio = dataInicio;
            if (dataFim) params.data_fim = dataFim;
            
            await gerarPDF(API_CONFIG.ENDPOINTS.ADMIN_RELATORIO_CONSULTAS_MEDICO, params);
        });
    }
    
    // Relatório 2: Consultas por Especialidade
    const formEspecialidade = document.getElementById('relatorioEspecialidadeForm');
    if (formEspecialidade) {
        // Remover listeners anteriores clonando o elemento
        const novoFormEspecialidade = formEspecialidade.cloneNode(true);
        formEspecialidade.parentNode.replaceChild(novoFormEspecialidade, formEspecialidade);
        
        novoFormEspecialidade.addEventListener('submit', async (e) => {
            e.preventDefault();
            const especialidadeId = document.getElementById('especialidade').value;
            const dataInicio = document.getElementById('periodoInicio2').value;
            const dataFim = document.getElementById('periodoFim2').value;
            
            const params = {};
            if (especialidadeId) params.especialidade_id = especialidadeId;
            if (dataInicio) params.data_inicio = dataInicio;
            if (dataFim) params.data_fim = dataFim;
            
            await gerarPDF(API_CONFIG.ENDPOINTS.ADMIN_RELATORIO_CONSULTAS_ESPECIALIDADE, params);
        });
    }
    
    // Relatório 3: Taxa de Cancelamentos
    const formCancelamento = document.getElementById('relatorioCancelamentoForm');
    if (formCancelamento) {
        // Remover listeners anteriores clonando o elemento
        const novoFormCancelamento = formCancelamento.cloneNode(true);
        formCancelamento.parentNode.replaceChild(novoFormCancelamento, formCancelamento);
        
        novoFormCancelamento.addEventListener('submit', async (e) => {
            e.preventDefault();
            const dataInicio = document.getElementById('periodoInicio3').value;
            const dataFim = document.getElementById('periodoFim3').value;
            const motivo = document.getElementById('motivoCancelamento').value;
            
            const params = {};
            if (dataInicio) params.data_inicio = dataInicio;
            if (dataFim) params.data_fim = dataFim;
            if (motivo) params.motivo = motivo;
            
            await gerarPDF(API_CONFIG.ENDPOINTS.ADMIN_RELATORIO_CANCELAMENTOS, params);
        });
    }
    
    // Relatório 4: Pacientes Mais Frequentes
    const formPaciente = document.getElementById('relatorioPacienteForm');
    if (formPaciente) {
        // Remover listeners anteriores clonando o elemento
        const novoFormPaciente = formPaciente.cloneNode(true);
        formPaciente.parentNode.replaceChild(novoFormPaciente, formPaciente);
        
        novoFormPaciente.addEventListener('submit', async (e) => {
            e.preventDefault();
            const dataInicio = document.getElementById('periodoInicio4').value;
            const dataFim = document.getElementById('periodoFim4').value;
            const limite = document.getElementById('quantidade').value;
            
            const params = {};
            if (dataInicio) params.data_inicio = dataInicio;
            if (dataFim) params.data_fim = dataFim;
            if (limite) params.limite = limite;
            
            await gerarPDF(API_CONFIG.ENDPOINTS.ADMIN_RELATORIO_PACIENTES_FREQUENTES, params);
        });
    }
}

// Função para gerar PDF e abrir em nova aba
async function gerarPDF(endpoint, params = {}) {
    console.log('=== GERANDO PDF ===');
    console.log('Endpoint:', endpoint);
    console.log('Parâmetros:', params);
    
    try {
        showLoading();
        
        // Adicionar formato PDF aos parâmetros
        params.formato = 'pdf';
        
        // Construir URL com query params
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(params)) {
            if (value) {
                queryParams.append(key, value);
            }
        }
        
        const url = `${API_CONFIG.BASE_URL}${endpoint}?${queryParams.toString()}`;
        const token = localStorage.getItem('token');
        
        console.log('Fazendo requisição PDF:', url);
        
        // Fazer requisição para obter PDF
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/pdf'
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Erro ao gerar PDF');
        }
        
        // Criar blob do PDF
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Abrir em nova aba
        const newWindow = window.open(blobUrl, '_blank');
        
        if (!newWindow) {
            // Se popup bloqueado, fazer download
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = `relatorio_${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            showMessage('PDF baixado! (popups bloqueados)', 'warning');
        } else {
            showMessage('PDF gerado com sucesso!', 'success');
        }
        
        // Limpar blob URL após 1 minuto
        setTimeout(() => window.URL.revokeObjectURL(blobUrl), 60000);
        
        hideLoading();
        
    } catch (error) {
        console.error('❌ ERRO ao gerar PDF:', error);
        showMessage('Erro ao gerar PDF: ' + error.message, 'error');
        hideLoading();
    }
}


// Exibir resultado do relatório
function exibirResultadoRelatorio(titulo, dados, tipo) {
    const container = document.getElementById('resultado-relatorio');
    if (!container) return;
    
    let html = `<h3>${titulo}</h3><div class="relatorio-dados">`;
    
    switch (tipo) {
        case 'consultas-periodo':
            html += `
                <p><strong>Total de Consultas:</strong> ${dados.total || 0}</p>
                <p><strong>Agendadas:</strong> ${dados.agendadas || 0}</p>
                <p><strong>Realizadas:</strong> ${dados.realizadas || 0}</p>
                <p><strong>Canceladas:</strong> ${dados.canceladas || 0}</p>
                <p><strong>Faltas:</strong> ${dados.faltas || 0}</p>
            `;
            break;
            
        case 'consultas-medico':
            html += `
                <p><strong>Médico:</strong> ${dados.medico?.nome || 'N/A'}</p>
                <p><strong>CRM:</strong> ${dados.medico?.crm || 'N/A'}</p>
                <p><strong>Total de Consultas:</strong> ${dados.total || 0}</p>
                <p><strong>Taxa de Realização:</strong> ${dados.taxa_realizacao || 0}%</p>
            `;
            break;
            
        case 'pacientes-ativos':
            html += '<table><thead><tr><th>Paciente</th><th>Total Consultas</th></tr></thead><tbody>';
            dados.forEach(item => {
                html += `<tr><td>${item.nome}</td><td>${item.total_consultas}</td></tr>`;
            });
            html += '</tbody></table>';
            break;
            
        case 'taxa-faltas':
            html += `
                <p><strong>Total de Consultas:</strong> ${dados.total_consultas || 0}</p>
                <p><strong>Total de Faltas:</strong> ${dados.total_faltas || 0}</p>
                <p><strong>Taxa de Faltas:</strong> ${dados.taxa_faltas || 0}%</p>
                <p><strong>Pacientes Bloqueados:</strong> ${dados.pacientes_bloqueados || 0}</p>
            `;
            break;
    }
    
    html += '</div>';
    container.innerHTML = html;
    container.style.display = 'block';
}

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

// Relatório de Consultas por Especialidade
document.getElementById('relatorioEspecialidadeForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const especialidade_id = document.getElementById('especialidade').value;
    const data_inicio = document.getElementById('periodoInicio2').value;
    const data_fim = document.getElementById('periodoFim2').value;
    
    await gerarPDF('/admin/relatorios/consultas-por-especialidade', {
        especialidade_id,
        data_inicio,
        data_fim
    });
});

// Relatório de Taxa de Cancelamento
document.getElementById('relatorioCancelamentoForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const data_inicio = document.getElementById('periodoInicio3').value;
    const data_fim = document.getElementById('periodoFim3').value;
    
    await gerarPDF('/admin/relatorios/cancelamentos', {
        data_inicio,
        data_fim
    });
});

// Relatório de Pacientes Frequentes
document.getElementById('relatorioPacienteForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const data_inicio = document.getElementById('periodoInicio4').value;
    const data_fim = document.getElementById('periodoFim4').value;
    
    await gerarPDF('/admin/relatorios/pacientes-frequentes', {
        data_inicio,
        data_fim
    });
});

