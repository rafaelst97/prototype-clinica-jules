// Login do Paciente
document.getElementById('loginForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    console.log('🔐 Formulário de login submetido');
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    console.log('📧 Email:', email);
    console.log('🔑 Senha length:', senha.length);
    
    // Validação básica
    if (senha.length < 8 || senha.length > 20) {
        console.log('❌ Senha inválida (tamanho)');
        showMessage('A senha deve ter entre 8 e 20 caracteres!', 'error');
        return;
    }
    
    try {
        console.log('📡 Enviando requisição de login...');
        // Fazer login via API (agora salva user_type e user_id automaticamente)
        const response = await api.login(email, senha);
        console.log('✅ Resposta do login:', response);
        
        // Verificar se é realmente um paciente
        if (response.user_type !== 'paciente') {
            showMessage('Acesso não autorizado. Esta área é exclusiva para pacientes.', 'error');
            api.logout();
            return;
        }
        
        // Obter dados completos do usuário
        const user = await api.getCurrentUser();
        
        // Verificar se paciente está bloqueado
        if (verificarBloqueio(user)) {
            api.logout();
            return;
        }
        
        // Armazenar nome do usuário
        localStorage.setItem('userName', user.nome);
        // token, user_type e user_id já foram salvos pelo api.login()
        
        showMessage('Login realizado com sucesso!', 'success');
        
        // Redirecionar para dashboard
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        
    } catch (error) {
        console.error('❌ Erro no login:', error);
        
        // Exibir mensagem de erro
        const errorText = error.message || 'E-mail ou senha inválidos';
        const errorMessageElement = document.getElementById('error-message');
        
        if (errorMessageElement) {
            errorMessageElement.textContent = errorText;
            errorMessageElement.style.display = 'block';
        } else {
            // Fallback
            alert(errorText);
        }
    }
});

// Função para verificar bloqueio do paciente
function verificarBloqueio(user) {
    if (user.bloqueado) {
        const errorMessageElement = document.getElementById('error-message');
        const mensagem = `Acesso bloqueado. Motivo: ${user.motivo_bloqueio || 'Não especificado'}. Entre em contato com a administração.`;
        
        if (errorMessageElement) {
            errorMessageElement.textContent = mensagem;
            errorMessageElement.style.display = 'block';
        } else {
            alert(mensagem);
        }
        return true;
    }
    return false;
}

// Função genérica para exibir mensagens
function showMessage(message, type) {
    const errorMessageElement = document.getElementById('error-message');
    if (errorMessageElement) {
        errorMessageElement.textContent = message;
        errorMessageElement.style.display = 'block';
        errorMessageElement.style.backgroundColor = type === 'success' ? '#e8f5e9' : '#ffebee';
        errorMessageElement.style.color = type === 'success' ? '#2e7d32' : '#d32f2f';
        errorMessageElement.style.borderColor = type === 'success' ? '#81c784' : '#ef9a9a';
        
        // Esconde a mensagem após 5 segundos
        setTimeout(() => {
            errorMessageElement.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}
