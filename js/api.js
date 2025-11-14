// Configuração da API
const API_CONFIG = {
    BASE_URL: window.ENV?.API_URL || 'http://localhost:8000',
    ENDPOINTS: {
        // Auth
        LOGIN: '/auth/login',
        LOGIN_CRM: '/auth/login/crm',
        ALTERAR_SENHA: '/auth/alterar-senha',
        VERIFICAR_TOKEN: '/auth/verificar-token',
        
        // Pacientes
        PACIENTE_CADASTRO: '/pacientes/cadastro',
        PACIENTE_PERFIL: (id) => `/pacientes/perfil/${id}`,
        PACIENTE_PERFIL_ATUALIZAR: (id) => `/pacientes/perfil/${id}`,
        PACIENTE_ALTERAR_SENHA: (id) => `/pacientes/perfil/${id}/senha`,
        PACIENTE_CONSULTAS: '/pacientes/consultas',
        PACIENTE_CONSULTAS_LISTAR: (id) => `/pacientes/consultas/${id}`,
        PACIENTE_CONSULTA_CANCELAR: (id) => `/pacientes/consultas/${id}`,
        PACIENTE_CONSULTA_REAGENDAR: (id) => `/pacientes/consultas/${id}/reagendar`,
        PACIENTE_MEDICOS: '/pacientes/medicos',
        PACIENTE_HORARIOS_DISPONIVEIS: (id) => `/pacientes/medicos/${id}/horarios-disponiveis`,
        PACIENTE_ESPECIALIDADES: '/pacientes/especialidades',
        PACIENTE_PLANOS_SAUDE: '/pacientes/planos-saude',
        
        // Médicos
        MEDICO_PERFIL: (id) => `/medicos/perfil/${id}`,
        MEDICO_CONSULTAS: (id) => `/medicos/consultas/${id}`,
        MEDICO_CONSULTAS_HOJE: (id) => `/medicos/consultas/hoje/${id}`,
        MEDICO_CONSULTA_STATUS: (id) => `/medicos/consultas/${id}/status`,
        MEDICO_HORARIOS: '/medicos/horarios',
        MEDICO_HORARIOS_LISTAR: (id) => `/medicos/horarios/${id}`,
        MEDICO_HORARIO_EXCLUIR: (id) => `/medicos/horarios/${id}`,
        MEDICO_OBSERVACOES: '/medicos/observacoes',
        MEDICO_OBSERVACAO_ATUALIZAR: (id) => `/medicos/observacoes/${id}`,
        MEDICO_OBSERVACAO_VER: (consultaId) => `/medicos/observacoes/${consultaId}`,
        
        // Admin
        ADMIN_DASHBOARD: '/admin/dashboard',
        ADMIN_CONSULTAS: '/admin/consultas',
        ADMIN_MEDICOS: '/admin/medicos',
        ADMIN_MEDICOS_LISTAR: '/admin/medicos',
        ADMIN_MEDICO: (id) => `/admin/medicos/${id}`,
        ADMIN_MEDICO_CRIAR: '/admin/medicos',
        ADMIN_MEDICO_ATUALIZAR: (id) => `/admin/medicos/${id}`,
        ADMIN_MEDICO_EXCLUIR: (id) => `/admin/medicos/${id}`,
        ADMIN_PACIENTES: '/admin/pacientes',
        ADMIN_PACIENTES_LISTAR: '/admin/pacientes',
        ADMIN_PACIENTE: (id) => `/admin/pacientes/${id}`,
        ADMIN_PACIENTE_DESBLOQUEAR: (id) => `/admin/pacientes/${id}/desbloquear`,
        ADMIN_PLANOS_SAUDE: '/admin/planos-saude',
        ADMIN_PLANOS_SAUDE_ESTATISTICAS: '/admin/planos-saude/estatisticas',
        ADMIN_PLANO_SAUDE: (id) => `/admin/planos-saude/${id}`,
        ADMIN_ESPECIALIDADES: '/admin/especialidades',
        ESPECIALIDADES: '/admin/especialidades',
        ADMIN_OBSERVACAO: (id) => `/admin/observacoes/${id}`,
        ADMIN_RELATORIO_CONSULTAS_MEDICO: '/admin/relatorios/consultas-por-medico',
        ADMIN_RELATORIO_CONSULTAS_ESPECIALIDADE: '/admin/relatorios/consultas-por-especialidade',
        ADMIN_RELATORIO_CANCELAMENTOS: '/admin/relatorios/cancelamentos',
        ADMIN_RELATORIO_PACIENTES_FREQUENTES: '/admin/relatorios/pacientes-frequentes',
        ADMIN_RELATORIO_ESTATISTICAS_GERAIS: '/admin/relatorios/estatisticas-gerais'
    }
};

// Classe para gerenciar requisições HTTP
class APIClient {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.token = localStorage.getItem('token');
        this.userType = localStorage.getItem('user_type');
        this.userId = localStorage.getItem('user_id');
    }

    // Armazena o token e informações do usuário
    setToken(token, userType, userId) {
        this.token = token;
        this.userType = userType;
        this.userId = userId;
        localStorage.setItem('token', token);
        localStorage.setItem('user_type', userType);
        localStorage.setItem('user_id', userId);
    }

    // Remove o token e informações do usuário
    clearToken() {
        this.token = null;
        this.userType = null;
        this.userId = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user_type');
        localStorage.removeItem('user_id');
    }

    // Obtém o tipo de usuário
    getUserType() {
        return this.userType || localStorage.getItem('user_type');
    }

    // Obtém o ID do usuário
    getUserId() {
        return this.userId || localStorage.getItem('user_id');
    }

    // Headers padrão
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (includeAuth && this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    // GET request
    async get(endpoint, params = {}) {
        try {
            let url = `${this.baseURL}${endpoint}`;
            
            // Adicionar query parameters se existirem
            if (Object.keys(params).length > 0) {
                const queryString = new URLSearchParams(params).toString();
                url += `?${queryString}`;
            }

            const response = await fetch(url, {
                method: 'GET',
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('GET Error:', error);
            throw error;
        }
    }

    // POST request
    async post(endpoint, data = {}, includeAuth = true) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: this.getHeaders(includeAuth),
                body: JSON.stringify(data)
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('POST Error:', error);
            throw error;
        }
    }

    // PUT request
    async put(endpoint, data = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'PUT',
                headers: this.getHeaders(),
                body: JSON.stringify(data)
            });

            return await this.handleResponse(response);
        } catch (error) {
            console.error('PUT Error:', error);
            throw error;
        }
    }

    // DELETE request
    async delete(endpoint, data = null) {
        try {
            const options = {
                method: 'DELETE',
                headers: this.getHeaders()
            };

            // Adiciona body se houver dados
            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.baseURL}${endpoint}`, options);

            return await this.handleResponse(response);
        } catch (error) {
            console.error('DELETE Error:', error);
            throw error;
        }
    }

    // Processa a resposta
    async handleResponse(response) {
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            // Tratar erro de autenticação
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/index.html';
                throw new Error('Sessão expirada. Faça login novamente.');
            }

            // Tratar erro de email duplicado
            if (response.status === 409) {
                throw new Error('Este email já está cadastrado. Tente fazer login ou use outro email.');
            }

            // Tratar erro de CPF duplicado
            if (response.status === 400 && data.detail && data.detail.includes('CPF')) {
                throw new Error('Este CPF já está cadastrado no sistema.');
            }

            throw new Error(data.detail || 'Erro na requisição');
        }

        return data;
    }

    // Login com email e senha
    async login(email, senha) {
        const response = await this.post(API_CONFIG.ENDPOINTS.LOGIN, { email, senha }, false);
        if (response.access_token) {
            this.setToken(response.access_token, response.user_type, response.user_id);
        }
        return response;
    }

    // Login de médico com CRM
    async loginCRM(crm, senha) {
        const response = await this.post(API_CONFIG.ENDPOINTS.LOGIN_CRM, { crm, senha }, false);
        if (response.access_token) {
            this.setToken(response.access_token, response.user_type, response.user_id);
        }
        return response;
    }

    // Alterar senha
    async alterarSenha(senhaAtual, senhaNova) {
        const userType = this.getUserType();
        const userId = this.getUserId();
        return await this.post(API_CONFIG.ENDPOINTS.ALTERAR_SENHA, {
            user_type: userType,
            user_id: userId,
            senha_atual: senhaAtual,
            senha_nova: senhaNova
        });
    }

    // Verificar token
    async verificarToken() {
        try {
            return await this.get(API_CONFIG.ENDPOINTS.VERIFICAR_TOKEN);
        } catch (error) {
            this.clearToken();
            return null;
        }
    }

    // Logout
    logout() {
        this.clearToken();
        window.location.href = '/index.html';
    }

    // Verificar se está autenticado
    isAuthenticated() {
        return !!this.token;
    }

    // Obter dados do usuário atual
    async getCurrentUser() {
        const userType = this.getUserType();
        const userId = this.getUserId();
        
        if (!userType || !userId) {
            throw new Error('Usuário não autenticado');
        }

        // Endpoint dinâmico baseado no tipo de usuário
        let endpoint;
        if (userType === 'paciente') {
            endpoint = API_CONFIG.ENDPOINTS.PACIENTE_PERFIL(userId);
        } else if (userType === 'medico') {
            endpoint = API_CONFIG.ENDPOINTS.MEDICO_PERFIL(userId);
        } else if (userType === 'administrador') {
            // Admin não tem perfil próprio, retorna dados básicos
            return { user_type: userType, user_id: userId };
        }

        return await this.get(endpoint);
    }
}

// Instância global da API
const api = new APIClient();
