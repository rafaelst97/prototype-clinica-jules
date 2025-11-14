"""
Testes para autenticação e controle de acesso
"""
import pytest
from datetime import timedelta
from jose import jwt
from app.config import settings
from app.utils.auth import verify_password, get_password_hash


def test_login_paciente(client, usuario_paciente):
    """Testa login de paciente com credenciais válidas"""
    dados = {
        "email": usuario_paciente.email,
        "senha": "senha123"
    }
    
    response = client.post("/auth/login", json=dados)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_medico(client, usuario_medico):
    """Testa login de médico com credenciais válidas"""
    dados = {
        "email": usuario_medico.email,
        "senha": "senha123"
    }
    
    response = client.post("/auth/login", json=dados)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_admin(client, usuario_admin):
    """Testa login de administrador com credenciais válidas"""
    dados = {
        "email": usuario_admin.email,
        "senha": "senha123"
    }
    
    response = client.post("/auth/login", json=dados)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_credenciais_invalidas(client, usuario_paciente):
    """Testa login com senha incorreta"""
    dados = {
        "email": usuario_paciente.email,
        "senha": "senha_errada"
    }
    
    response = client.post("/auth/login", json=dados)
    assert response.status_code == 401


def test_login_usuario_inexistente(client):
    """Testa login com usuário que não existe"""
    dados = {
        "email": "inexistente@test.com",
        "senha": "senha123"
    }
    
    response = client.post("/auth/login", json=dados)
    assert response.status_code == 401


def test_login_usuario_bloqueado(client, usuario_paciente, db):
    """Testa que usuário bloqueado não pode fazer login"""
    usuario_paciente.bloqueado = True
    db.commit()
    
    dados = {
        "email": usuario_paciente.email,
        "senha": "senha123"
    }
    
    response = client.post("/auth/login", json=dados)
    assert response.status_code == 403
    assert "bloqueado" in response.json()["detail"].lower()


def test_token_contem_tipo_e_id_usuario(client, usuario_paciente):
    """Testa que token JWT contém user_type e user_id"""
    dados = {
        "email": usuario_paciente.email,
        "senha": "senha123"
    }
    
    response = client.post("/auth/login", json=dados)
    token = response.json()["access_token"]
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "user_type" in payload
    assert payload["user_type"] == "paciente"
    assert "user_id" in payload
    assert payload["user_id"] == usuario_paciente.id_paciente


def test_acesso_endpoint_sem_token(client):
    """Testa acesso a endpoint protegido sem token"""
    response = client.get("/pacientes/consultas")
    assert response.status_code == 401 or response.status_code == 403


def test_acesso_endpoint_token_invalido(client):
    """Testa acesso com token inválido"""
    response = client.get(
        "/pacientes/consultas",
        headers={"Authorization": "Bearer token_invalido"}
    )
    assert response.status_code == 401 or response.status_code == 403


def test_acesso_endpoint_token_expirado(client, usuario_paciente):
    """Testa acesso com token expirado"""
    from app.utils.auth import create_access_token
    
    # Criar token com tempo de expiração negativo
    token = create_access_token(
        data={"sub": usuario_paciente.email, "user_type": "paciente"},
        expires_delta=timedelta(minutes=-30)
    )
    
    response = client.get(
        "/pacientes/consultas",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_paciente_nao_acessa_endpoint_medico(client, token_paciente):
    """Testa que paciente não pode acessar endpoints de médico"""
    response = client.get(
        "/medicos/consultas",
        headers={"Authorization": f"Bearer {token_paciente}"}
    )
    assert response.status_code == 403 or response.status_code == 404


def test_medico_nao_acessa_endpoint_admin(client, token_medico):
    """Testa que médico não pode acessar endpoints de admin"""
    response = client.get(
        "/admin/pacientes",
        headers={"Authorization": f"Bearer {token_medico}"}
    )
    assert response.status_code == 403 or response.status_code == 404


def test_paciente_nao_acessa_endpoint_admin(client, token_paciente):
    """Testa que paciente não pode acessar endpoints de admin"""
    response = client.get(
        "/admin/pacientes",
        headers={"Authorization": f"Bearer {token_paciente}"}
    )
    assert response.status_code == 403 or response.status_code == 404


def test_verificar_senha_correta(db):
    """Testa verificação de senha correta"""
    senha_hash = get_password_hash("senha123")
    assert verify_password("senha123", senha_hash) == True


def test_verificar_senha_incorreta(db):
    """Testa verificação de senha incorreta"""
    senha_hash = get_password_hash("senha123")
    assert verify_password("senha_errada", senha_hash) == False


def test_hash_senha_diferente(db):
    """Testa que mesma senha gera hashes diferentes"""
    hash1 = get_password_hash("senha123")
    hash2 = get_password_hash("senha123")
    
    # Hashes devem ser diferentes (devido ao salt)
    assert hash1 != hash2
    # Mas ambos devem validar a senha corretamente
    assert verify_password("senha123", hash1) == True
    assert verify_password("senha123", hash2) == True
