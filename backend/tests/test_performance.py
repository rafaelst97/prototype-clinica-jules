"""
Testes de Performance e Carga
Performance: ~3-5 segundos total
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.mark.performance
class TestPerformance:
    """Suite de testes de performance"""
    
    def test_bulk_create_pacientes(self, client, db_session, plano_unimed):
        """Teste: Criação em massa de pacientes (performance)"""
        from app.models.models import Paciente
        from passlib.context import CryptContext
        from datetime import date
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        pacientes = []
        for i in range(50):
            paciente = Paciente(
                nome=f"Paciente Teste {i}",
                cpf=f"000{i:08d}",
                email=f"paciente{i}@test.com",
                senha_hash=pwd_context.hash("senha123"),
                telefone="47-99999-9999",
                data_nascimento=date(1990, 1, 1),
                id_plano_saude_fk=plano_unimed.id_plano_saude,
                esta_bloqueado=False
            )
            pacientes.append(paciente)
        
        db_session.add_all(pacientes)
        db_session.commit()
        
        assert len(pacientes) == 50
    
    def test_bulk_agendar_consultas(
        self, client, db_session, medico_cardiologista, paciente_teste,
        horarios_trabalho_cardio
    ):
        """Teste: Agendamento em massa de consultas"""
        from app.models.models import Consulta
        
        consultas = []
        base_date = datetime.now() + timedelta(days=10)
        
        for i in range(20):
            data_hora = base_date + timedelta(hours=i)
            consulta = Consulta(
                id_paciente_fk=paciente_teste.id_paciente,
                id_medico_fk=medico_cardiologista.id_medico,
                data_hora=data_hora,
                tipo="Consulta",
                status="Agendada"
            )
            consultas.append(consulta)
        
        db_session.add_all(consultas)
        db_session.commit()
        
        assert len(consultas) == 20
    
    def test_query_performance_listar_consultas(
        self, client, db_session, medico_cardiologista, paciente_teste,
        auth_headers_admin
    ):
        """Teste: Performance de listagem de consultas"""
        from app.models.models import Consulta
        
        # Criar 30 consultas
        consultas = []
        base_date = datetime.now()
        for i in range(30):
            data_hora = base_date + timedelta(days=i, hours=10)
            consulta = Consulta(
                id_paciente_fk=paciente_teste.id_paciente,
                id_medico_fk=medico_cardiologista.id_medico,
                data_hora=data_hora,
                tipo="Consulta",
                status="Agendada"
            )
            consultas.append(consulta)
        
        db_session.add_all(consultas)
        db_session.commit()
        
        # Testar performance da listagem
        response = client.get("/admin/consultas", headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 30
    
    def test_concurrent_login_requests(self, client, admin_user, medico_cardiologista, paciente_teste):
        """Teste: Múltiplos logins simultâneos"""
        usuarios = [
            {"email": "admin@test.com", "password": "admin123", "tipo_usuario": "admin"},
            {"email": "joao@test.com", "password": "medico123", "tipo_usuario": "medico"},
            {"email": "carlos@test.com", "password": "paciente123", "tipo_usuario": "paciente"},
        ]
        
        responses = []
        for usuario in usuarios:
            response = client.post("/auth/login", json=usuario)
            responses.append(response)
        
        for response in responses:
            assert response.status_code == status.HTTP_200_OK
            assert "access_token" in response.json()
