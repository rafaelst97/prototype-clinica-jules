"""
Testes de Endpoints Admin
Performance: ~2-3 segundos total
"""
import pytest
from fastapi import status


@pytest.mark.integration
class TestAdminEndpoints:
    """Suite de testes dos endpoints de administração"""
    
    def test_listar_pacientes(self, client, auth_headers_admin, paciente_teste):
        """Teste: Listar todos os pacientes"""
        response = client.get("/admin/pacientes", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["nome"] == "Carlos Teste"
    
    def test_buscar_paciente_por_id(self, client, auth_headers_admin, paciente_teste):
        """Teste: Buscar paciente por ID"""
        response = client.get(
            f"/admin/pacientes/{paciente_teste.id_paciente}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id_paciente"] == paciente_teste.id_paciente
        assert data["nome"] == "Carlos Teste"
    
    def test_bloquear_paciente(self, client, auth_headers_admin, paciente_teste):
        """Teste: Bloquear paciente"""
        response = client.post(
            f"/admin/pacientes/{paciente_teste.id_paciente}/bloquear",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["esta_bloqueado"] is True
    
    def test_desbloquear_paciente(self, client, auth_headers_admin, db_session, paciente_teste):
        """Teste: Desbloquear paciente"""
        # Bloquear primeiro
        paciente_teste.esta_bloqueado = True
        db_session.commit()
        
        # Desbloquear
        response = client.post(
            f"/admin/pacientes/{paciente_teste.id_paciente}/desbloquear",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["esta_bloqueado"] is False
    
    def test_listar_medicos(self, client, auth_headers_admin, medico_cardiologista):
        """Teste: Listar todos os médicos"""
        response = client.get("/admin/medicos", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_buscar_medico_por_id(self, client, auth_headers_admin, medico_cardiologista):
        """Teste: Buscar médico por ID"""
        response = client.get(
            f"/admin/medicos/{medico_cardiologista.id_medico}",
            headers=auth_headers_admin
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id_medico"] == medico_cardiologista.id_medico
        assert data["crm"] == "CRM-12345"
    
    def test_listar_consultas(self, client, auth_headers_admin):
        """Teste: Listar todas as consultas"""
        response = client.get("/admin/consultas", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
    
    def test_listar_especialidades(self, client, auth_headers_admin, especialidade_cardiologia):
        """Teste: Listar especialidades"""
        response = client.get("/admin/especialidades", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(e["nome"] == "Cardiologia" for e in data)
    
    def test_criar_especialidade(self, client, auth_headers_admin):
        """Teste: Criar nova especialidade"""
        response = client.post(
            "/admin/especialidades",
            headers=auth_headers_admin,
            json={"nome": "Neurologia"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["nome"] == "Neurologia"
    
    def test_admin_nao_autenticado(self, client):
        """Teste: Acesso negado sem autenticação"""
        response = client.get("/admin/pacientes")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_token_invalido(self, client):
        """Teste: Token inválido"""
        headers = {"Authorization": "Bearer token_invalido"}
        response = client.get("/admin/pacientes", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
