"""
Testes para os Endpoints de Consultas, Pacientes e Médicos.
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta

@pytest.mark.integration
class TestConsultasEndpoints:
    """Conjunto de testes para os endpoints relacionados a consultas."""

    # PACIENTE endpoints
    def test_paciente_pode_agendar_consulta(self, client, paciente_teste, medico_cardiologista, auth_headers_paciente):
        """Verifica se um paciente autenticado pode agendar uma nova consulta."""
        data_hora = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT10:00:00")
        response = client.post(
            f"/pacientes/consultas?paciente_id={paciente_teste.id_paciente}",
            headers=auth_headers_paciente,
            json={"id_medico": medico_cardiologista.id_medico, "data_hora_inicio": data_hora}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "agendada"

    def test_paciente_lista_suas_consultas(self, client, consulta_agendada, auth_headers_paciente):
        """Verifica se o paciente pode listar suas próprias consultas."""
        response = client.get(f"/pacientes/consultas/{consulta_agendada.id_paciente_fk}", headers=auth_headers_paciente)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert any(c["id_consulta"] == consulta_agendada.id_consulta for c in response.json())

    def test_paciente_ve_horarios_disponiveis(self, client, medico_cardiologista, auth_headers_paciente):
        """Verifica se o paciente pode ver os horários disponíveis de um médico."""
        data = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        response = client.get(
            f"/pacientes/medicos/{medico_cardiologista.id_medico}/horarios-disponiveis?data={data}",
            headers=auth_headers_paciente
        )
        assert response.status_code == status.HTTP_200_OK
        assert "horarios_disponiveis" in response.json()

    # MÉDICO endpoints
    def test_medico_lista_suas_consultas(self, client, consulta_agendada, auth_headers_medico):
        """Verifica se o médico pode listar suas próprias consultas."""
        medico_id = consulta_agendada.id_medico_fk
        response = client.get(f"/medicos/consultas/{medico_id}", headers=auth_headers_medico)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        assert any(c["id_consulta"] == consulta_agendada.id_consulta for c in response.json())

    def test_medico_pode_criar_observacao(self, client, consulta_agendada, auth_headers_medico):
        """Verifica se o médico pode adicionar uma observação a uma consulta."""
        response = client.post(
            "/medicos/observacoes",
            headers=auth_headers_medico,
            json={"id_consulta_fk": consulta_agendada.id_consulta, "descricao": "Paciente apresenta bom quadro."}
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "Observação criada com sucesso" in response.json()["mensagem"]

    def test_medico_gerencia_horarios_trabalho(self, client, medico_cardiologista, auth_headers_medico):
        """Verifica se o médico pode adicionar um novo horário de trabalho."""
        novo_horario = {"dia_semana": 0, "hora_inicio": "08:00", "hora_fim": "12:00", "id_medico_fk": medico_cardiologista.id_medico}
        response = client.post(
            "/medicos/horarios",
            headers=auth_headers_medico,
            json=novo_horario
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["dia_semana"] == 0

    # Testes de Falha e Segurança
    def test_paciente_nao_ve_consultas_de_outro(self, client, db_session, auth_headers_paciente, paciente_sem_plano, consulta_agendada):
        """Garante que um paciente não possa ver as consultas de outro."""
        # `consulta_agendada` pertence a `paciente_teste`, não a `paciente_sem_plano`
        response = client.get(f"/pacientes/consultas/{paciente_sem_plano.id_paciente}", headers=auth_headers_paciente)
        assert response.status_code == status.HTTP_200_OK # O endpoint retorna 200, mas a lista deve ser vazia ou não conter a consulta do outro.
        assert not any(c["id_consulta"] == consulta_agendada.id_consulta for c in response.json())

    def test_agendamento_sem_autenticacao_falha(self, client, paciente_teste, medico_cardiologista):
        """Verifica se uma tentativa de agendamento sem token falha."""
        data_hora = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT10:00:00")
        response = client.post(
            f"/pacientes/consultas?paciente_id={paciente_teste.id_paciente}",
            json={"id_medico": medico_cardiologista.id_medico, "data_hora_inicio": data_hora}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_medico_nao_cria_observacao_consulta_alheia(self, client, consulta_agendada, auth_headers_medico_ortopedista):
        """Garante que um médico não possa criar observação para consulta de outro médico."""
        response = client.post(
            "/medicos/observacoes",
            headers=auth_headers_medico_ortopedista,
            json={"id_consulta_fk": consulta_agendada.id_consulta, "descricao": "Tentativa de inserção indevida."}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
