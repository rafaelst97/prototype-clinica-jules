// Função auxiliar para exibir mensagens (caso api.js não esteja carregado)
if (typeof showMessage === 'undefined') {
    function showMessage(message, type = 'success') {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        const alertHTML = `
            <div class="alert ${alertClass}" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px; padding: 15px; background: ${type === 'success' ? '#d4edda' : '#f8d7da'}; color: ${type === 'success' ? '#155724' : '#721c24'}; border-radius: 5px;">
                ${message}
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHTML);
        
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) alert.remove();
        }, 3000);
    }
}

// Login do Admin
document.getElementById('loginAdminForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const usuario = document.getElementById('usuario').value;
    const senha = document.getElementById('senha').value;
    
    if (!usuario || !senha) {
        showMessage('Por favor, preencha todos os campos!', 'error');
        return;
    }
    
    try {
        // Converter "admin" para "admin@clinica.com" se necessário
        let email = usuario;
        if (usuario === 'admin' || usuario === 'administrador') {
            email = 'admin@clinica.com';
        } else if (!usuario.includes('@')) {
            // Se não for um email, adicionar @clinica.com
            email = `${usuario}@clinica.com`;
        }
        
        console.log('Tentando login com email:', email);
        
        // Fazer login via API (agora salva user_type e user_id automaticamente)
        const response = await api.login(email, senha);
        
        console.log('Resposta do login:', response);
        
        // Verificar se é realmente um administrador
        if (response.user_type !== 'administrador') {
            showMessage('Acesso não autorizado. Esta área é exclusiva para administradores.', 'error');
            api.logout();
            return;
        }
        
        // token, user_type e user_id já foram salvos pelo api.login()
        
        console.log('Login realizado com sucesso!');
        showMessage('Login realizado com sucesso!', 'success');
        
        // Redirecionar para dashboard
        setTimeout(() => {
            window.location.href = 'dashboard.html';
        }, 1000);
        
    } catch (error) {
        console.error('Erro no login:', error);
        showMessage('Erro ao fazer login: ' + error.message, 'error');
    }
});
