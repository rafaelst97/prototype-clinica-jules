# 🐛 BUGS ENCONTRADOS - Testes E2E de Interface

**Data:** 01/11/2025  
**Método:** Testes automatizados com Selenium  
**Escopo:** Interface frontend - Formulários, validações e fluxos

---

## ❌ BUGS CRÍTICOS

### BUG #1: Validação de Senha Alfanumérica Ausente no Frontend
**Severidade:** 🔴 CRÍTICA  
**Arquivo:** `/js/paciente-cadastro.js`  
**Descrição:** O frontend NÃO valida se a senha contém letras E números antes de enviar ao backend.

**Comportamento Esperado:**
- Senha deve conter pelo menos uma letra E um número
- Erro deve ser mostrado ANTES de enviar ao servidor

**Comportamento Atual:**
- Frontend aceita senha "12345678" (apenas números)
- Frontend aceita senha "senhasenha" (apenas letras)
- Validação só acontece no backend, gerando erro após submit

**Impacto:**
- Usuário perde tempo preenchendo formulário
- Experiência ruim (erro só após envio)
- Possibilidade de tentar burlar validação

**Reprodução:**
1. Acessar `/paciente/cadastro.html`
2. Preencher campo senha com "12345678"
3. Preencher confirmar senha com "12345678"
4. Clicar em cadastrar
5. ❌ Não mostra erro ANTES do envio

**Teste que detectou:** `test_validacao_senha_sem_letras`

---

### BUG #2: Validação de Senhas Diferentes Ausente
**Severidade:** 🟡 MÉDIA  
**Arquivo:** `/js/paciente-cadastro.js`  
**Descrição:** Frontend não compara senha e confirmação antes de enviar.

**Comportamento Esperado:**
- Se senha ≠ confirmação, mostrar erro imediatamente
- Erro deve aparecer em tempo real (onblur ou onchange)

**Comportamento Atual:**
- Permite senhas diferentes sem aviso
- Validação só acontece no backend

**Impacto:**
- Usuário descobre erro tarde demais
- Frustração na experiência

**Reprodução:**
1. Acessar `/paciente/cadastro.html`
2. Senha: "senha123"
3. Confirmar: "senha456"
4. ❌ Não mostra alerta de diferença

**Teste que detectou:** `test_validacao_senhas_diferentes`

---

### BUG #3: Email Duplicado Não Mostra Mensagem Clara
**Severidade:** 🟡 MÉDIA  
**Arquivo:** `/js/paciente-cadastro.js`  
**Descrição:** Ao tentar cadastrar com email já existente, mensagem de erro não aparece claramente.

**Comportamento Esperado:**
- Mensagem visível: "Email já cadastrado"
- Sugestão: link para recuperar senha ou fazer login

**Comportamento Atual:**
- Erro não é exibido ou não é claro
- Usuário fica sem entender o problema

**Impacto:**
- Confusão do usuário
- Possíveis tentativas repetidas

**Reprodução:**
1. Cadastrar paciente com email X
2. Tentar cadastrar novamente com mesmo email
3. ❌ Mensagem não aparece ou não é clara

**Teste que detectou:** `test_validacao_email_duplicado`

---

## ✅ TESTES QUE PASSARAM

### Validações Funcionando Corretamente:

✅ **Página carrega com todos elementos** (`test_pagina_cadastro_carrega_corretamente`)  
✅ **Máscara de CPF aplicada** - Formato: 123.456.789-00 (`test_mascara_cpf_formatacao_completa`)  
✅ **Máscara de Telefone** - Celular e fixo (`test_mascara_telefone_celular_e_fixo`)  
✅ **Máscara de CEP** - Formato: 88330-000 (`test_mascara_cep_completa`)  
✅ **Validação senha curta** - Bloqueia < 8 caracteres (`test_validacao_senha_muito_curta`)  
✅ **Validação senha longa** - Bloqueia > 20 caracteres (`test_validacao_senha_muito_longa`)  
✅ **Validação senha sem números** - Bloqueia senha apenas com letras (`test_validacao_senha_sem_numeros`)  
✅ **Validação CPF inválido** - Testado (`test_validacao_cpf_invalido`)  
✅ **Cadastro completo** - Fluxo funciona quando dados válidos (`test_cadastro_completo_valido`)  

---

## 📊 RESUMO ESTATÍSTICO

**Total de testes executados:** 12  
**Testes aprovados:** 9 (75%)  
**Testes reprovados:** 3 (25%)  

**Taxa de conformidade:** 75%  
**Bugs críticos:** 1  
**Bugs médios:** 2  

---

## 🔧 RECOMENDAÇÕES DE CORREÇÃO

### Para BUG #1 (Senha Alfanumérica):
```javascript
// Adicionar em paciente-cadastro.js
function validarSenhaAlfanumerica(senha) {
    const temLetra = /[a-zA-Z]/.test(senha);
    const temNumero = /[0-9]/.test(senha);
    
    if (!temLetra || !temNumero) {
        mostrarErro('senha', 'A senha deve conter letras E números');
        return false;
    }
    return true;
}
```

### Para BUG #2 (Senhas Diferentes):
```javascript
// Adicionar evento onblur
document.getElementById('confirmarSenha').addEventListener('blur', function() {
    const senha = document.getElementById('senha').value;
    const confirmar = this.value;
    
    if (senha !== confirmar) {
        mostrarErro('confirmarSenha', 'As senhas não coincidem');
    }
});
```

### Para BUG #3 (Email Duplicado):
```javascript
// Melhorar tratamento de erro no catch
.catch(error => {
    if (error.message.includes('email') || error.message.includes('já existe')) {
        mostrarErro('email', 'Este email já está cadastrado. <a href="login.html">Fazer login</a>');
    }
});
```

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Corrigir bugs identificados no frontend
2. ⏳ Executar testes de login completo
3. ⏳ Executar testes de agendamento
4. ⏳ Executar testes de dashboard admin
5. ⏳ Executar testes de segurança (XSS, SQL Injection)
6. ⏳ Executar testes de navegação
7. ⏳ Validar correções com reexecução dos testes

---

**Gerado automaticamente pelos testes E2E**
