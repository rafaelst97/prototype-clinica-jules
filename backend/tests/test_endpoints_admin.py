"""
Testes para os Endpoints de Administração
"""
import pytest
from fastapi import status

@pytest.mark.integration
class TestAdminEndpoints:
    """Conjunto de testes para os endpoints administrativos."""

    def test_listar_pacientes_sucesso(self, client, auth_headers_admin, paciente_teste):
        """Verifica se a listagem de pacientes funciona e retorna dados corretos."""
        response = client.get("/admin/pacientes", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(p["id_paciente"] == paciente_teste.id_paciente for p in data)

    def test_buscar_paciente_por_id_sucesso(self, client, auth_headers_admin, paciente_teste):
        """Verifica a busca de um paciente específico por ID."""
        response = client.get(f"/admin/pacientes/{paciente_teste.id_paciente}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id_paciente"] == paciente_teste.id_paciente

    def test_desbloquear_paciente_sucesso(self, client, auth_headers_admin, paciente_bloqueado):
        """Verifica se é possível desbloquear um paciente."""
        response = client.post(f"/admin/pacientes/{paciente_bloqueado.id_paciente}/desbloquear", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["esta_bloqueado"] is False

    def test_listar_medicos_sucesso(self, client, auth_headers_admin, medico_cardiologista):
        """Verifica a listagem de médicos."""
        response = client.get("/admin/medicos", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(m["id_medico"] == medico_cardiologista.id_medico for m in data)

    def test_criar_medico_sucesso(self, client, auth_headers_admin, especialidade_ortopedia):
        """Verifica a criação de um novo médico."""
        novo_medico = {
            "nome": "Dra. Teste", "crm": "CRM-99999", "email": "dra.teste@saude.com",
            "senha": "senha123", "id_especialidade_fk": especialidade_ortopedia.id_especialidade,
            "cpf": "12345678901"
        }
        response = client.post("/admin/medicos", headers=auth_headers_admin, json=novo_medico)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["crm"] == "CRM-99999"

    def test_atualizar_medico_sucesso(self, client, auth_headers_admin, medico_cardiologista):
        """Verifica a atualização dos dados de um médico."""
        update_data = {"nome": "Dr. João Silva Atualizado", "crm": "CRM-12345-NEW"}
        response = client.put(f"/admin/medicos/{medico_cardiologista.id_medico}", headers=auth_headers_admin, json=update_data)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["nome"] == "Dr. João Silva Atualizado"

    def test_excluir_medico_sucesso(self, client, auth_headers_admin, medico_ortopedista):
        """Verifica a exclusão de um médico."""
        response = client.delete(f"/admin/medicos/{medico_ortopedista.id_medico}", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        assert "removido com sucesso" in response.json()["mensagem"]

    def test_listar_planos_saude_sucesso(self, client, auth_headers_admin, plano_unimed):
        """Verifica a listagem de planos de saúde."""
        response = client.get("/admin/planos-saude", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert any(p["nome"] == "Unimed" for p in response.json())

    def test_gerar_relatorio_sucesso(self, client, auth_headers_admin):
        """Verifica a geração de um relatório."""
        response = client.get("/admin/relatorios/consultas-por-medico", headers=auth_headers_admin)
        assert response.status_code == status.HTTP_200_OK
        # A resposta deve ser um PDF
        assert response.headers['content-type'] == 'application/pdf'

    def test_acesso_negado_para_nao_admin(self, client, auth_headers_paciente):
        """Garante que usuários não-admin não acessem endpoints de admin."""
        response = client.get("/admin/pacientes", headers=auth_headers_paciente)
        assert response.status_code == status.HTTP_403_FORBIDDEN
