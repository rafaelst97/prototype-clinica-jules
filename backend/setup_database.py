"""
Script de Setup do Banco de Dados
Cria todas as tabelas e popula com dados iniciais
"""
import sys
import os

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models.models import (
    Base, Especialidade, PlanoSaude, Administrador,
    Medico, Paciente, HorarioTrabalho, Consulta, Observacao
)
from datetime import datetime, date, timedelta
from passlib.context import CryptContext

# Configurar hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    print("📦 Criando tabelas no banco de dados...")
    Base.metadata.drop_all(bind=engine)  # Drop se existir
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

def popular_dados_iniciais():
    """Popula o banco com dados de teste"""
    db = SessionLocal()
    
    try:
        print("\n🌱 Populando dados iniciais...")
        
        # 1. ESPECIALIDADES
        print("  → Criando especialidades...")
        especialidades = [
            Especialidade(nome="Cardiologia", descricao="Especialidade focada no coração e sistema cardiovascular"),
            Especialidade(nome="Dermatologia", descricao="Cuidados com a pele"),
            Especialidade(nome="Ortopedia", descricao="Tratamento de ossos e articulações"),
            Especialidade(nome="Pediatria", descricao="Cuidados com crianças e adolescentes"),
            Especialidade(nome="Ginecologia", descricao="Saúde da mulher"),
            Especialidade(nome="Oftalmologia", descricao="Cuidados com os olhos"),
            Especialidade(nome="Neurologia", descricao="Sistema nervoso"),
            Especialidade(nome="Psiquiatria", descricao="Saúde mental")
        ]
        db.add_all(especialidades)
        db.commit()
        print(f"  ✅ {len(especialidades)} especialidades criadas")
        
        # 2. PLANOS DE SAÚDE
        print("  → Criando planos de saúde...")
        planos = [
            PlanoSaude(nome="Unimed", tipo="Empresarial", registro_ans="123456", telefone="(47) 3333-4444"),
            PlanoSaude(nome="Bradesco Saúde", tipo="Individual", registro_ans="654321", telefone="(47) 3333-5555"),
            PlanoSaude(nome="SulAmérica", tipo="Familiar", registro_ans="789012", telefone="(47) 3333-6666"),
            PlanoSaude(nome="Amil", tipo="Empresarial", registro_ans="345678", telefone="(47) 3333-7777"),
            PlanoSaude(nome="Particular", tipo="Particular", registro_ans=None, telefone=None)
        ]
        db.add_all(planos)
        db.commit()
        print(f"  ✅ {len(planos)} planos de saúde criados")
        
        # 3. ADMINISTRADOR
        print("  → Criando administrador...")
        admin = Administrador(
            nome="Admin Sistema",
            cpf="00000000000",
            telefone="(47) 99999-0000",
            email="admin@clinica.com",
            senha=pwd_context.hash("admin123"),
            cargo="Administrador Geral"
        )
        db.add(admin)
        db.commit()
        print(f"  ✅ Administrador criado (email: admin@clinica.com, senha: admin123)")
        
        # 4. MÉDICOS
        print("  → Criando médicos...")
        medicos_data = [
            {"nome": "Dr. João Silva", "crm": "12345-SC", "especialidade_id": 1, "email": "joao.silva@clinica.com"},
            {"nome": "Dra. Maria Santos", "crm": "23456-SC", "especialidade_id": 2, "email": "maria.santos@clinica.com"},
            {"nome": "Dr. Pedro Oliveira", "crm": "34567-SC", "especialidade_id": 3, "email": "pedro.oliveira@clinica.com"},
            {"nome": "Dra. Ana Costa", "crm": "45678-SC", "especialidade_id": 4, "email": "ana.costa@clinica.com"},
            {"nome": "Dra. Carla Ferreira", "crm": "56789-SC", "especialidade_id": 5, "email": "carla.ferreira@clinica.com"},
        ]
        
        medicos = []
        for i, med_data in enumerate(medicos_data, 1):
            medico = Medico(
                nome=med_data["nome"],
                crm=med_data["crm"],
                cpf=f"{i:011d}",
                telefone=f"(47) 98888-{i:04d}",
                email=med_data["email"],
                senha=pwd_context.hash("medico123"),
                id_especialidade_fk=med_data["especialidade_id"]
            )
            medicos.append(medico)
        
        db.add_all(medicos)
        db.commit()
        print(f"  ✅ {len(medicos)} médicos criados (senha padrão: medico123)")
        
        # 5. HORÁRIOS DE TRABALHO DOS MÉDICOS
        print("  → Criando horários de trabalho...")
        horarios = []
        for medico in medicos:
            # Segunda a Sexta - Manhã
            for dia in range(1, 6):  # 1=Segunda, 5=Sexta
                horarios.append(HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia,
                    hora_inicio="08:00:00",
                    hora_fim="12:00:00",
                    duracao_consulta=30
                ))
            # Segunda a Sexta - Tarde
            for dia in range(1, 6):
                horarios.append(HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia,
                    hora_inicio="14:00:00",
                    hora_fim="18:00:00",
                    duracao_consulta=30
                ))
        
        db.add_all(horarios)
        db.commit()
        print(f"  ✅ {len(horarios)} horários de trabalho criados")
        
        # 6. PACIENTES
        print("  → Criando pacientes...")
        pacientes_data = [
            {"nome": "Carlos Souza", "cpf": "12345678901", "email": "carlos@email.com", "plano": 1},
            {"nome": "Juliana Alves", "cpf": "23456789012", "email": "juliana@email.com", "plano": 2},
            {"nome": "Roberto Lima", "cpf": "34567890123", "email": "roberto@email.com", "plano": 3},
            {"nome": "Fernanda Rocha", "cpf": "45678901234", "email": "fernanda@email.com", "plano": 1},
            {"nome": "Lucas Martins", "cpf": "56789012345", "email": "lucas@email.com", "plano": 4},
            {"nome": "Patricia Gomes", "cpf": "67890123456", "email": "patricia@email.com", "plano": 5},
            {"nome": "Rafael Castro", "cpf": "78901234567", "email": "rafael@email.com", "plano": 2},
            {"nome": "Amanda Silva", "cpf": "89012345678", "email": "amanda@email.com", "plano": 1},
        ]
        
        pacientes = []
        for i, pac_data in enumerate(pacientes_data, 1):
            data_nasc = date(1980 + i, (i % 12) + 1, (i % 28) + 1)
            paciente = Paciente(
                nome=pac_data["nome"],
                cpf=pac_data["cpf"],
                data_nascimento=data_nasc,
                telefone=f"(47) 97777-{i:04d}",
                email=pac_data["email"],
                senha=pwd_context.hash("paciente123"),
                endereco=f"Rua Exemplo, {i*100}",
                id_plano_saude_fk=pac_data["plano"],
                esta_bloqueado=False,
                faltas_consecutivas=0
            )
            pacientes.append(paciente)
        
        db.add_all(pacientes)
        db.commit()
        print(f"  ✅ {len(pacientes)} pacientes criados (senha padrão: paciente123)")
        
        # 7. CONSULTAS
        print("  → Criando consultas de exemplo...")
        consultas = []
        hoje = datetime.now()
        
        # Consultas passadas (realizadas)
        for i in range(5):
            data_passada = hoje - timedelta(days=7+i)
            consulta = Consulta(
                id_paciente_fk=pacientes[i % len(pacientes)].id_paciente,
                id_medico_fk=medicos[i % len(medicos)].id_medico,
                data_hora_inicio=data_passada.replace(hour=10, minute=0, second=0, microsecond=0),
                data_hora_fim=data_passada.replace(hour=10, minute=30, second=0, microsecond=0),
                status="realizada"
            )
            consultas.append(consulta)
        
        # Consultas futuras (agendadas)
        for i in range(8):
            data_futura = hoje + timedelta(days=1+i)
            hora = 9 + (i % 8)
            consulta = Consulta(
                id_paciente_fk=pacientes[i % len(pacientes)].id_paciente,
                id_medico_fk=medicos[i % len(medicos)].id_medico,
                data_hora_inicio=data_futura.replace(hour=hora, minute=0, second=0, microsecond=0),
                data_hora_fim=data_futura.replace(hour=hora, minute=30, second=0, microsecond=0),
                status="agendada"
            )
            consultas.append(consulta)
        
        db.add_all(consultas)
        db.commit()
        print(f"  ✅ {len(consultas)} consultas criadas")
        
        # 8. OBSERVAÇÕES
        print("  → Criando observações...")
        observacoes = []
        for i, consulta in enumerate([c for c in consultas if c.status == "realizada"][:3]):
            obs = Observacao(
                id_consulta_fk=consulta.id_consulta,
                descricao=f"Paciente apresentou melhora. Tratamento deve continuar por mais 30 dias.",
                data_criacao=consulta.data_hora_inicio
            )
            observacoes.append(obs)
        
        db.add_all(observacoes)
        db.commit()
        print(f"  ✅ {len(observacoes)} observações criadas")
        
        print("\n✅ Banco de dados populado com sucesso!")
        print("\n📝 CREDENCIAIS DE ACESSO:")
        print("   ADMIN:")
        print("     Email: admin@clinica.com")
        print("     Senha: admin123")
        print("\n   MÉDICOS:")
        print("     Email: [nome]@clinica.com (ex: joao.silva@clinica.com)")
        print("     Senha: medico123")
        print("\n   PACIENTES:")
        print("     Email: [nome]@email.com (ex: carlos@email.com)")
        print("     Senha: paciente123")
        
    except Exception as e:
        print(f"\n❌ Erro ao popular dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Função principal"""
    print("=" * 60)
    print("🏥 SETUP DO BANCO DE DADOS - CLÍNICA DE SAÚDE")
    print("=" * 60)
    
    try:
        criar_tabelas()
        popular_dados_iniciais()
        
        print("\n" + "=" * 60)
        print("✅ SETUP COMPLETO!")
        print("=" * 60)
        print("\n💡 Próximos passos:")
        print("   1. Inicie o servidor: uvicorn app.main:app --reload")
        print("   2. Acesse: http://localhost:8000/docs")
        print("   3. Teste os endpoints com as credenciais acima")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O SETUP: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
