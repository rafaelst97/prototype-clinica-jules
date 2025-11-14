# 🔧 CORREÇÃO: Cadastro e Login de Paciente

## ❌ Problema Identificado

O cadastro de paciente não estava funcionando devido a:

1. **Campo extra sendo enviado**: O JavaScript estava enviando o campo `endereco` que não existe no schema do backend
2. **Validação de senha**: Falta de validação no frontend para senha alfanumérica (letras + números)
3. **Mensagens de erro**: Caracteres especiais mal formatados nas mensagens

## ✅ Correções Aplicadas

### 1. Removido campo `endereco` do cadastro
**Arquivo:** `js/paciente-cadastro.js`

```javascript
// ANTES (ERRADO):
const dadosCadastro = {
    nome: document.getElementById('nome').value,
    email: document.getElementById('email').value,
    senha: senha,
    cpf: cpfValue,
    data_nascimento: document.getElementById('dataNascimento').value,
    telefone: telefoneValue,
    endereco: document.getElementById('endereco').value || null, // ❌ CAMPO NÃO EXISTE NO SCHEMA
    id_plano_saude_fk: document.getElementById('convenio').value ? parseInt(document.getElementById('convenio').value) : null
};

// DEPOIS (CORRETO):
const dadosCadastro = {
    nome: document.getElementById('nome').value,
    email: document.getElementById('email').value,
    senha: senha,
    cpf: cpfValue,
    data_nascimento: document.getElementById('dataNascimento').value,
    telefone: telefoneValue,
    id_plano_saude_fk: document.getElementById('convenio').value ? parseInt(document.getElementById('convenio').value) : null
};
```

### 2. Adicionada validação de senha alfanumérica
**Arquivo:** `js/paciente-cadastro.js`

```javascript
// Validar se a senha é alfanumérica (contém letras E números)
const temLetra = /[a-zA-Z]/.test(senha);
const temNumero = /[0-9]/.test(senha);

if (!temLetra || !temNumero) {
    showMessage('A senha deve conter letras e números (alfanumérica)!', 'error');
    return;
}
```

### 3. Corrigidas mensagens de erro
```javascript
// Mensagens agora com encoding correto:
- 'A senha deve ter entre 8 e 20 caracteres alfanuméricos!'
- 'A senha deve conter letras e números (alfanumérica)!'
- 'As senhas não coincidem!'
- 'CPF inválido! Deve conter 11 dígitos.'
- 'Telefone inválido! Deve conter 10 ou 11 dígitos.'
```

## 🧪 Como Testar o Cadastro

### 1. Acessar página de cadastro
```
http://localhost/paciente/cadastro.html
```

### 2. Preencher o formulário com dados válidos

**Exemplo de dados válidos:**
- Nome: `João da Silva`
- Email: `joao.silva@email.com`
- CPF: `123.456.789-01`
- Data de Nascimento: `01/01/1990`
- Telefone: `(47) 99999-9999`
- Senha: `senha123` (✅ contém letras e números)
- Confirmar Senha: `senha123`
- Plano de Saúde: (opcional)

**❌ Senhas que NÃO funcionarão:**
- `senha` (sem números)
- `12345678` (sem letras)
- `abc123` (menos de 8 caracteres)

### 3. Submeter o formulário
- Deve aparecer mensagem: "Cadastro realizado com sucesso! Redirecionando..."
- Deve redirecionar para a página de login após 2 segundos

### 4. Fazer login
```
http://localhost/paciente/login.html
```

**Credenciais:**
- Email: `joao.silva@email.com`
- Senha: `senha123`

### 5. Verificar redirecionamento
- Deve redirecionar para: `dashboard.html`
- Deve mostrar nome do paciente na interface

## 🔍 Verificar no Backend

### Endpoint de Cadastro
```
POST http://localhost:8000/pacientes/cadastro
```

**Body (JSON):**
```json
{
  "nome": "João da Silva",
  "cpf": "12345678901",
  "email": "joao.silva@email.com",
  "senha": "senha123",
  "telefone": "47999999999",
  "data_nascimento": "1990-01-01",
  "id_plano_saude_fk": null
}
```

**Resposta esperada (201 Created):**
```json
{
  "id_paciente": 1,
  "nome": "João da Silva",
  "cpf": "12345678901",
  "email": "joao.silva@email.com",
  "telefone": "47999999999",
  "data_nascimento": "1990-01-01",
  "esta_bloqueado": false,
  "id_plano_saude_fk": null,
  "plano_saude": null
}
```

### Endpoint de Login
```
POST http://localhost:8000/auth/login
```

**Body (JSON):**
```json
{
  "email": "joao.silva@email.com",
  "senha": "senha123"
}
```

**Resposta esperada (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_type": "paciente",
  "user_id": 1
}
```

## 📝 Validações do Backend

### Schema: PacienteCreate
```python
class PacienteCreate(BaseModel):
    nome: str                              # Obrigatório
    cpf: str                               # Obrigatório, 11 dígitos
    email: EmailStr                        # Obrigatório, formato válido
    senha: str                             # Obrigatório, 8-20 caracteres, alfanumérica
    telefone: Optional[str] = None         # Opcional
    data_nascimento: date                  # Obrigatório
    id_plano_saude_fk: Optional[int] = None # Opcional
```

### Validações de Senha
```python
@validator('senha')
def validar_senha_alfanumerica(cls, v):
    if len(v) < 8 or len(v) > 20:
        raise ValueError('Senha deve ter entre 8 e 20 caracteres')
    
    tem_letra = any(c.isalpha() for c in v)
    tem_numero = any(c.isdigit() for c in v)
    
    if not (tem_letra and tem_numero):
        raise ValueError('Senha deve conter letras e números (alfanumérica)')
    
    return v
```

### Validações de CPF
```python
@validator('cpf')
def validar_cpf_formato(cls, v):
    if v:
        cpf_limpo = v.replace('.', '').replace('-', '').replace(' ', '')
        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            raise ValueError('CPF deve conter 11 dígitos')
    return v
```

## 🚨 Possíveis Erros

### Erro 409: Email já cadastrado
```json
{
  "detail": "Email já cadastrado no sistema"
}
```
**Solução:** Use outro email ou faça login com o email existente

### Erro 409: CPF já cadastrado
```json
{
  "detail": "CPF já cadastrado no sistema"
}
```
**Solução:** Use outro CPF ou faça login com o CPF existente

### Erro 422: Validação falhou
```json
{
  "detail": [
    {
      "loc": ["body", "senha"],
      "msg": "Senha deve conter letras e números (alfanumérica)",
      "type": "value_error"
    }
  ]
}
```
**Solução:** Verifique se a senha contém letras E números

### Erro 401: Login falhou
```json
{
  "detail": "Email ou senha incorretos"
}
```
**Solução:** Verifique email e senha

### Erro 403: Paciente bloqueado
```json
{
  "detail": "Conta bloqueada por faltas consecutivas. Entre em contato com a administração."
}
```
**Solução:** Solicite desbloqueio ao administrador

## ✅ Checklist de Teste

- [ ] Cadastro com senha alfanumérica funciona
- [ ] Cadastro com senha sem números é rejeitado
- [ ] Cadastro com senha sem letras é rejeitado
- [ ] Cadastro com CPF inválido é rejeitado
- [ ] Cadastro com email duplicado é rejeitado
- [ ] Login com credenciais corretas funciona
- [ ] Login com senha errada é rejeitado
- [ ] Redirecionamento para dashboard funciona
- [ ] Token JWT é armazenado no localStorage
- [ ] Dados do usuário são carregados corretamente

## 🎯 Resultado Esperado

✅ **Cadastro realizado com sucesso**  
✅ **Login funcionando**  
✅ **Dashboard carregando**  
✅ **Sessão persistindo**  

---

**Data da correção:** 02/11/2025  
**Arquivos modificados:** `js/paciente-cadastro.js`

