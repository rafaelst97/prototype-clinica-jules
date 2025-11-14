from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from app.models import (
    Consulta, Medico, Paciente, Especialidade, 
    StatusConsulta, Usuario
)


def gerar_relatorio_consultas_por_medico(
    db: Session,
    data_inicio: date = None,
    data_fim: date = None
) -> Dict[str, Any]:
    """
    Gera relatório de quantidade de consultas por médico
    Caso de Uso: Gerar Relatórios em PDF - Quantidade de consultas por médico
    """
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    resultados = db.query(
        Medico.id,
        Usuario.nome.label('medico_nome'),
        Especialidade.nome.label('especialidade'),
        func.count(Consulta.id).label('total_consultas'),
        func.sum(
            case(
                (Consulta.status == StatusConsulta.REALIZADA, 1),
                else_=0
            )
        ).label('consultas_realizadas'),
        func.sum(
            case(
                (Consulta.status == StatusConsulta.CANCELADA, 1),
                else_=0
            )
        ).label('consultas_canceladas')
    ).join(
        Usuario, Medico.usuario_id == Usuario.id
    ).join(
        Especialidade, Medico.especialidade_id == Especialidade.id
    ).outerjoin(
        Consulta, Medico.id == Consulta.medico_id
    ).filter(
        and_(
            Consulta.data >= data_inicio,
            Consulta.data <= data_fim
        )
    ).group_by(
        Medico.id, Usuario.nome, Especialidade.nome
    ).all()
    
    dados = []
    for r in resultados:
        dados.append({
            'medico_nome': r.medico_nome,
            'especialidade': r.especialidade,
            'total_consultas': r.total_consultas or 0,
            'consultas_realizadas': r.consultas_realizadas or 0,
            'consultas_canceladas': r.consultas_canceladas or 0
        })
    
    return {
        'tipo': 'consultas_por_medico',
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'dados': dados
    }


def gerar_relatorio_consultas_por_especialidade(
    db: Session,
    data_inicio: date = None,
    data_fim: date = None
) -> Dict[str, Any]:
    """
    Gera relatório de quantidade de consultas por especialidade
    Caso de Uso: Gerar Relatórios em PDF - Quantidade de consultas por especialidade
    """
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    resultados = db.query(
        Especialidade.nome.label('especialidade'),
        func.count(Consulta.id).label('total_consultas'),
        func.count(func.distinct(Medico.id)).label('total_medicos')
    ).join(
        Medico, Especialidade.id == Medico.especialidade_id
    ).outerjoin(
        Consulta, Medico.id == Consulta.medico_id
    ).filter(
        and_(
            Consulta.data >= data_inicio,
            Consulta.data <= data_fim
        )
    ).group_by(
        Especialidade.nome
    ).all()
    
    dados = []
    for r in resultados:
        dados.append({
            'especialidade': r.especialidade,
            'total_consultas': r.total_consultas or 0,
            'total_medicos': r.total_medicos or 0
        })
    
    return {
        'tipo': 'consultas_por_especialidade',
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'dados': dados
    }


def gerar_relatorio_cancelamentos(
    db: Session,
    data_inicio: date = None,
    data_fim: date = None
) -> Dict[str, Any]:
    """
    Gera relatório de taxa de cancelamentos e remarcações
    Caso de Uso: Gerar Relatórios em PDF - Taxa de cancelamentos e remarcações
    """
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    total_consultas = db.query(func.count(Consulta.id)).filter(
        and_(
            Consulta.data >= data_inicio,
            Consulta.data <= data_fim
        )
    ).scalar() or 0
    
    total_cancelamentos = db.query(func.count(Consulta.id)).filter(
        and_(
            Consulta.data >= data_inicio,
            Consulta.data <= data_fim,
            Consulta.status == StatusConsulta.CANCELADA
        )
    ).scalar() or 0
    
    # Para remarcações, consideramos cancelamentos com motivo que menciona reagendamento
    total_remarcacoes = db.query(func.count(Consulta.id)).filter(
        and_(
            Consulta.data >= data_inicio,
            Consulta.data <= data_fim,
            Consulta.status == StatusConsulta.CANCELADA,
            Consulta.motivo_cancelamento.ilike('%reagend%')
        )
    ).scalar() or 0
    
    taxa_cancelamento = (total_cancelamentos / total_consultas * 100) if total_consultas > 0 else 0
    
    return {
        'tipo': 'cancelamentos_remarcacoes',
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'dados': {
            'total_consultas': total_consultas,
            'total_cancelamentos': total_cancelamentos,
            'total_remarcacoes': total_remarcacoes,
            'taxa_cancelamento': round(taxa_cancelamento, 2)
        }
    }


def gerar_relatorio_pacientes_frequentes(
    db: Session,
    data_inicio: date = None,
    data_fim: date = None,
    limite: int = 20
) -> Dict[str, Any]:
    """
    Gera relatório de pacientes que mais consultaram no período
    Caso de Uso: Gerar Relatórios em PDF - Pacientes que mais consultaram no período
    """
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()
    
    resultados = db.query(
        Paciente.id,
        Usuario.nome.label('paciente_nome'),
        Paciente.cpf,
        func.count(Consulta.id).label('total_consultas'),
        func.max(Consulta.data).label('ultima_consulta')
    ).join(
        Usuario, Paciente.usuario_id == Usuario.id
    ).join(
        Consulta, Paciente.id == Consulta.paciente_id
    ).filter(
        and_(
            Consulta.data >= data_inicio,
            Consulta.data <= data_fim
        )
    ).group_by(
        Paciente.id, Usuario.nome, Paciente.cpf
    ).order_by(
        func.count(Consulta.id).desc()
    ).limit(limite).all()
    
    dados = []
    for r in resultados:
        dados.append({
            'paciente_nome': r.paciente_nome,
            'cpf': r.cpf,
            'total_consultas': r.total_consultas or 0,
            'ultima_consulta': r.ultima_consulta.isoformat() if r.ultima_consulta else None
        })
    
    return {
        'tipo': 'pacientes_frequentes',
        'data_inicio': data_inicio.isoformat(),
        'data_fim': data_fim.isoformat(),
        'dados': dados
    }


def criar_pdf_relatorio(dados_relatorio: Dict[str, Any]) -> BytesIO:
    """
    Cria um PDF a partir dos dados do relatório
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitulo_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Título
    elementos.append(Paragraph("Clínica Saúde+", titulo_style))
    elementos.append(Paragraph("Sistema de Agendamento de Consultas", subtitulo_style))
    elementos.append(Spacer(1, 0.3*inch))
    
    tipo = dados_relatorio.get('tipo', '')
    data_inicio = dados_relatorio.get('data_inicio', '')
    data_fim = dados_relatorio.get('data_fim', '')
    
    # Cabeçalho do relatório
    if tipo == 'consultas_por_medico':
        elementos.append(Paragraph("Relatório de Consultas por Médico", styles['Heading2']))
    elif tipo == 'consultas_por_especialidade':
        elementos.append(Paragraph("Relatório de Consultas por Especialidade", styles['Heading2']))
    elif tipo == 'cancelamentos_remarcacoes':
        elementos.append(Paragraph("Relatório de Cancelamentos e Remarcações", styles['Heading2']))
    elif tipo == 'pacientes_frequentes':
        elementos.append(Paragraph("Relatório de Pacientes Frequentes", styles['Heading2']))
    
    elementos.append(Paragraph(f"Período: {data_inicio} a {data_fim}", subtitulo_style))
    elementos.append(Spacer(1, 0.3*inch))
    
    # Dados do relatório
    dados = dados_relatorio.get('dados', [])
    
    if tipo == 'consultas_por_medico':
        tabela_dados = [['Médico', 'Especialidade', 'Total', 'Realizadas', 'Canceladas']]
        for item in dados:
            tabela_dados.append([
                item['medico_nome'],
                item['especialidade'],
                str(item['total_consultas']),
                str(item['consultas_realizadas']),
                str(item['consultas_canceladas'])
            ])
    
    elif tipo == 'consultas_por_especialidade':
        tabela_dados = [['Especialidade', 'Total Consultas', 'Total Médicos']]
        for item in dados:
            tabela_dados.append([
                item['especialidade'],
                str(item['total_consultas']),
                str(item['total_medicos'])
            ])
    
    elif tipo == 'cancelamentos_remarcacoes':
        tabela_dados = [['Métrica', 'Valor']]
        tabela_dados.append(['Total de Consultas', str(dados['total_consultas'])])
        tabela_dados.append(['Total de Cancelamentos', str(dados['total_cancelamentos'])])
        tabela_dados.append(['Total de Remarcações', str(dados['total_remarcacoes'])])
        tabela_dados.append(['Taxa de Cancelamento (%)', f"{dados['taxa_cancelamento']}%"])
    
    elif tipo == 'pacientes_frequentes':
        tabela_dados = [['Paciente', 'CPF', 'Total Consultas', 'Última Consulta']]
        for item in dados:
            tabela_dados.append([
                item['paciente_nome'],
                item['cpf'],
                str(item['total_consultas']),
                item['ultima_consulta'] or 'N/A'
            ])
    
    # Criar tabela
    tabela = Table(tabela_dados)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elementos.append(tabela)
    elementos.append(Spacer(1, 0.5*inch))
    
    # Rodapé
    data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
    rodape = Paragraph(
        f"Relatório gerado em: {data_geracao}",
        ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, alignment=TA_RIGHT)
    )
    elementos.append(rodape)
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    return buffer
