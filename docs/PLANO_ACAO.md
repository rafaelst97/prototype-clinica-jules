# 🎯 Plano de Ação - Correções e Melhorias
## Sistema Clínica Saúde+

**Documento:** Plano de Implementação  
**Versão:** 1.0  
**Data:** 20 de outubro de 2025  
**Responsável:** Equipe de Desenvolvimento  
**Status:** 🔴 Aguardando Execução

---

## 📋 Sumário Executivo

### Objetivo
Completar os **15% de requisitos faltantes** para atingir **100% de conformidade** com o enunciado do projeto Clínica Saúde+.

### Escopo
- **Fase 1:** Correções críticas (8h) - Bloqueadores de entrega
- **Fase 2:** Melhorias importantes (12h) - Qualidade e usabilidade
- **Fase 3:** Polimento (8h) - Excelência e profissionalismo

### Prazo Total
**28 horas** de desenvolvimento (~4-5 dias úteis)

### Prioridade
🔴 **ALTA** - Alguns requisitos são explícitos no enunciado

---

## 🔴 Fase 1: Correções Críticas (8 horas)

### 1.1 Geração de Relatórios PDF ⏱️ 3h

**Problema:**
Enunciado exige "Relatórios em PDF", mas sistema apenas retorna JSON.

**Impacto:** 🔴 CRÍTICO - Requisito explícito não atendido

**Solução:**

#### Passo 1: Instalar Biblioteca (5 min)

```bash
# backend/requirements.txt
# Adicionar:
reportlab==4.0.7
pillow==10.1.0
```

```bash
# Reinstalar dependências
docker-compose down
docker-compose build backend
docker-compose up -d
```

#### Passo 2: Criar Gerador de PDF (1h 30min)

**Arquivo:** `backend/app/utils/pdf_generator.py`

```python
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
from typing import List, Dict

class PDFReportGenerator:
    """Gerador de relatórios PDF para o sistema"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
    
    def _criar_estilos_customizados(self):
        """Cria estilos personalizados para o PDF"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12
        ))
    
    def gerar_relatorio_consultas_medico(self, dados: Dict) -> BytesIO:
        """
        Gera relatório PDF de consultas por médico
        
        Args:
            dados: {
                'data_inicio': str,
                'data_fim': str,
                'medicos': [
                    {
                        'nome': str,
                        'crm': str,
                        'especialidade': str,
                        'total': int,
                        'realizadas': int,
                        'canceladas': int,
                        'faltas': int
                    }
                ]
            }
        
        Returns:
            BytesIO: Buffer com o PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        elements = []
        
        # Cabeçalho
        title = Paragraph("Relatório de Consultas por Médico", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Período
        periodo_text = f"Período: {dados['data_inicio']} a {dados['data_fim']}"
        periodo = Paragraph(periodo_text, self.styles['Normal'])
        elements.append(periodo)
        elements.append(Spacer(1, 0.2*inch))
        
        # Estatísticas gerais
        total_geral = sum(m['total'] for m in dados['medicos'])
        realizadas_geral = sum(m['realizadas'] for m in dados['medicos'])
        canceladas_geral = sum(m['canceladas'] for m in dados['medicos'])
        
        stats_text = f"""
        <b>Resumo Geral:</b><br/>
        Total de Consultas: {total_geral}<br/>
        Realizadas: {realizadas_geral} ({realizadas_geral/total_geral*100:.1f}%)<br/>
        Canceladas: {canceladas_geral} ({canceladas_geral/total_geral*100:.1f}%)
        """
        stats = Paragraph(stats_text, self.styles['Normal'])
        elements.append(stats)
        elements.append(Spacer(1, 0.3*inch))
        
        # Tabela de médicos
        subtitle = Paragraph("Detalhamento por Médico", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        table_data = [
            ['Médico', 'CRM', 'Especialidade', 'Total', 'Realizadas', 'Canceladas', 'Faltas']
        ]
        
        for medico in dados['medicos']:
            table_data.append([
                medico['nome'],
                medico['crm'],
                medico['especialidade'],
                str(medico['total']),
                str(medico['realizadas']),
                str(medico['canceladas']),
                str(medico.get('faltas', 0))
            ])
        
        # Total
        table_data.append([
            'TOTAL',
            '',
            '',
            str(total_geral),
            str(realizadas_geral),
            str(canceladas_geral),
            ''
        ])
        
        table = Table(table_data, colWidths=[2*inch, 0.8*inch, 1.5*inch, 0.7*inch, 0.9*inch, 0.9*inch, 0.7*inch])
        
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corpo
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            
            # Total (última linha)
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(table)
        
        # Rodapé
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"""
        <i>Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i><br/>
        <i>Sistema Clínica Saúde+ - Gestão de Consultas Médicas</i>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        # Gerar PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def gerar_relatorio_taxa_cancelamentos(self, dados: Dict) -> BytesIO:
        """Gera relatório de taxa de cancelamentos e remarcações"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        elements = []
        
        # Título
        title = Paragraph("Relatório de Cancelamentos e Remarcações", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Período
        periodo = Paragraph(f"Período: {dados['data_inicio']} a {dados['data_fim']}", self.styles['Normal'])
        elements.append(periodo)
        elements.append(Spacer(1, 0.2*inch))
        
        # Resumo
        total = dados['total_consultas']
        canceladas = dados['total_canceladas']
        remarcadas = dados['total_remarcadas']
        taxa_cancel = (canceladas / total * 100) if total > 0 else 0
        taxa_remarc = (remarcadas / total * 100) if total > 0 else 0
        
        resumo_text = f"""
        <b>Resumo Geral:</b><br/>
        Total de Consultas: {total}<br/>
        Cancelamentos: {canceladas} ({taxa_cancel:.1f}%)<br/>
        Remarcações: {remarcadas} ({taxa_remarc:.1f}%)<br/>
        Taxa de Sucesso: {100 - taxa_cancel - taxa_remarc:.1f}%
        """
        resumo = Paragraph(resumo_text, self.styles['Normal'])
        elements.append(resumo)
        elements.append(Spacer(1, 0.3*inch))
        
        # Tabela por especialidade
        subtitle = Paragraph("Cancelamentos por Especialidade", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        table_data = [['Especialidade', 'Total', 'Canceladas', 'Taxa (%)']]
        for esp in dados['por_especialidade']:
            taxa = (esp['canceladas'] / esp['total'] * 100) if esp['total'] > 0 else 0
            table_data.append([
                esp['nome'],
                str(esp['total']),
                str(esp['canceladas']),
                f"{taxa:.1f}%"
            ])
        
        table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
        # Rodapé
        elements.append(Spacer(1, 0.5*inch))
        footer = Paragraph(f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", self.styles['Normal'])
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def gerar_relatorio_pacientes_frequentes(self, dados: Dict) -> BytesIO:
        """Gera relatório dos pacientes que mais consultaram"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        elements = []
        
        # Título
        title = Paragraph("Relatório de Pacientes Mais Frequentes", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Período
        periodo = Paragraph(f"Período: {dados['data_inicio']} a {dados['data_fim']}", self.styles['Normal'])
        elements.append(periodo)
        elements.append(Spacer(1, 0.2*inch))
        
        # Tabela
        table_data = [['#', 'Paciente', 'CPF', 'Convênio', 'Total Consultas', 'Última Consulta']]
        
        for idx, pac in enumerate(dados['pacientes'], start=1):
            table_data.append([
                str(idx),
                pac['nome'],
                pac['cpf'],
                pac['convenio'] or 'Particular',
                str(pac['total_consultas']),
                pac['ultima_consulta']
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        elements.append(table)
        
        # Rodapé
        elements.append(Spacer(1, 0.5*inch))
        footer = Paragraph(f"<i>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", self.styles['Normal'])
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
```

#### Passo 3: Criar Endpoints de Relatórios (1h)

**Arquivo:** `backend/app/routers/admin.py`

Adicionar ao final do arquivo:

```python
from fastapi.responses import StreamingResponse
from app.utils.pdf_generator import PDFReportGenerator
from sqlalchemy import func, case
from datetime import date

pdf_generator = PDFReportGenerator()

@router.get("/relatorios/pdf/consultas-medico")
async def gerar_pdf_consultas_medico(
    data_inicio: date,
    data_fim: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin)
):
    """
    Gera relatório PDF de consultas por médico
    
    - **data_inicio**: Data inicial do período (YYYY-MM-DD)
    - **data_fim**: Data final do período (YYYY-MM-DD)
    """
    
    # Buscar dados
    consultas = db.query(
        Medico.nome,
        Medico.crm,
        Especialidade.nome.label('especialidade'),
        func.count(Consulta.id).label('total'),
        func.sum(case((Consulta.status == 'realizada', 1), else_=0)).label('realizadas'),
        func.sum(case((Consulta.status == 'cancelada', 1), else_=0)).label('canceladas'),
        func.sum(case((Consulta.status == 'falta', 1), else_=0)).label('faltas')
    ).join(
        Consulta, Medico.id == Consulta.medico_id
    ).join(
        Especialidade, Medico.especialidade_id == Especialidade.id
    ).filter(
        Consulta.data_hora.between(data_inicio, data_fim)
    ).group_by(
        Medico.id, Medico.nome, Medico.crm, Especialidade.nome
    ).all()
    
    # Preparar dados para o PDF
    dados = {
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),
        'medicos': [
            {
                'nome': c.nome,
                'crm': c.crm,
                'especialidade': c.especialidade,
                'total': int(c.total),
                'realizadas': int(c.realizadas or 0),
                'canceladas': int(c.canceladas or 0),
                'faltas': int(c.faltas or 0)
            }
            for c in consultas
        ]
    }
    
    # Gerar PDF
    pdf_buffer = pdf_generator.gerar_relatorio_consultas_medico(dados)
    
    # Retornar como download
    filename = f"relatorio_consultas_medico_{data_inicio}_{data_fim}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/relatorios/pdf/taxa-cancelamentos")
async def gerar_pdf_taxa_cancelamentos(
    data_inicio: date,
    data_fim: date,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin)
):
    """Gera relatório PDF de taxa de cancelamentos e remarcações"""
    
    # Total de consultas
    total_consultas = db.query(Consulta).filter(
        Consulta.data_hora.between(data_inicio, data_fim)
    ).count()
    
    # Canceladas
    total_canceladas = db.query(Consulta).filter(
        Consulta.data_hora.between(data_inicio, data_fim),
        Consulta.status == 'cancelada'
    ).count()
    
    # Remarcadas (assumindo que você adicione um status 'remarcada' ou campo específico)
    total_remarcadas = 0  # Implementar quando adicionar remarcação
    
    # Por especialidade
    por_especialidade = db.query(
        Especialidade.nome,
        func.count(Consulta.id).label('total'),
        func.sum(case((Consulta.status == 'cancelada', 1), else_=0)).label('canceladas')
    ).join(
        Medico, Consulta.medico_id == Medico.id
    ).join(
        Especialidade, Medico.especialidade_id == Especialidade.id
    ).filter(
        Consulta.data_hora.between(data_inicio, data_fim)
    ).group_by(
        Especialidade.nome
    ).all()
    
    dados = {
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),
        'total_consultas': total_consultas,
        'total_canceladas': total_canceladas,
        'total_remarcadas': total_remarcadas,
        'por_especialidade': [
            {
                'nome': esp.nome,
                'total': int(esp.total),
                'canceladas': int(esp.canceladas or 0)
            }
            for esp in por_especialidade
        ]
    }
    
    pdf_buffer = pdf_generator.gerar_relatorio_taxa_cancelamentos(dados)
    
    filename = f"relatorio_cancelamentos_{data_inicio}_{data_fim}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/relatorios/pdf/pacientes-frequentes")
async def gerar_pdf_pacientes_frequentes(
    data_inicio: date,
    data_fim: date,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin)
):
    """Gera relatório PDF dos pacientes que mais consultaram no período"""
    
    pacientes = db.query(
        Paciente.nome_completo,
        Paciente.cpf,
        Convenio.nome.label('convenio'),
        func.count(Consulta.id).label('total_consultas'),
        func.max(Consulta.data_hora).label('ultima_consulta')
    ).join(
        Consulta, Paciente.id == Consulta.paciente_id
    ).outerjoin(
        Convenio, Paciente.convenio_id == Convenio.id
    ).filter(
        Consulta.data_hora.between(data_inicio, data_fim)
    ).group_by(
        Paciente.id, Paciente.nome_completo, Paciente.cpf, Convenio.nome
    ).order_by(
        func.count(Consulta.id).desc()
    ).limit(limit).all()
    
    dados = {
        'data_inicio': data_inicio.strftime('%d/%m/%Y'),
        'data_fim': data_fim.strftime('%d/%m/%Y'),
        'pacientes': [
            {
                'nome': p.nome_completo,
                'cpf': p.cpf,
                'convenio': p.convenio,
                'total_consultas': int(p.total_consultas),
                'ultima_consulta': p.ultima_consulta.strftime('%d/%m/%Y')
            }
            for p in pacientes
        ]
    }
    
    pdf_buffer = pdf_generator.gerar_relatorio_pacientes_frequentes(dados)
    
    filename = f"relatorio_pacientes_frequentes_{data_inicio}_{data_fim}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

#### Passo 4: Testar (30min)

```bash
# Reiniciar backend
docker-compose restart backend

# Testar via Swagger UI
# http://localhost:8000/docs
# GET /admin/relatorios/pdf/consultas-medico
# Parâmetros: data_inicio=2025-10-01, data_fim=2025-10-31
```

---

### 1.2 Validação de 24h para Cancelamento ⏱️ 1h

**Problema:**
Regra de negócio "cancelamento até 24h antes" não é validada.

**Impacto:** 🔴 CRÍTICO - Permite cancelamento a qualquer momento

**Solução:**

#### Passo 1: Criar Função de Validação (15min)

**Arquivo:** `backend/app/utils/validators.py`

Adicionar:

```python
from datetime import datetime, timedelta
from fastapi import HTTPException

def validar_prazo_24h(data_hora_consulta: datetime, acao: str = "cancelamento") -> bool:
    """
    Valida se a ação está sendo feita com pelo menos 24h de antecedência
    
    Args:
        data_hora_consulta: Data e hora da consulta
        acao: Nome da ação (para mensagem de erro)
    
    Returns:
        bool: True se válido
    
    Raises:
        HTTPException: Se prazo não for respeitado
    """
    agora = datetime.now()
    limite = data_hora_consulta - timedelta(hours=24)
    
    if agora > limite:
        horas_restantes = (data_hora_consulta - agora).total_seconds() / 3600
        raise HTTPException(
            status_code=400,
            detail=f"{acao.capitalize()} permitido apenas até 24h antes da consulta. " +
                   f"Faltam apenas {horas_restantes:.1f} horas para a consulta."
        )
    
    return True
```

#### Passo 2: Aplicar no Endpoint de Cancelamento (30min)

**Arquivo:** `backend/app/routers/pacientes.py`

Atualizar:

```python
from app.utils.validators import validar_prazo_24h

@router.delete("/consultas/{consulta_id}/cancelar")
async def cancelar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_paciente)
):
    """
    Cancela uma consulta agendada
    
    **Regra:** Cancelamento permitido apenas até 24h antes da consulta
    """
    
    # Buscar consulta
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.paciente_id == current_user.paciente.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta.status != 'agendada':
        raise HTTPException(
            status_code=400,
            detail=f"Consulta com status '{consulta.status}' não pode ser cancelada"
        )
    
    # ✅ VALIDAR PRAZO DE 24H
    validar_prazo_24h(consulta.data_hora, "cancelamento")
    
    # Cancelar
    consulta.status = 'cancelada'
    consulta.updated_at = datetime.now()
    db.commit()
    
    return {
        "message": "Consulta cancelada com sucesso",
        "consulta_id": consulta.id,
        "data_hora": consulta.data_hora
    }
```

#### Passo 3: Criar Teste (15min)

**Arquivo:** `backend/tests/test_validators.py` (criar)

```python
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.utils.validators import validar_prazo_24h

def test_validar_prazo_24h_valido():
    """Teste: Prazo maior que 24h deve passar"""
    data_futura = datetime.now() + timedelta(hours=48)
    assert validar_prazo_24h(data_futura) == True

def test_validar_prazo_24h_invalido():
    """Teste: Prazo menor que 24h deve falhar"""
    data_proxima = datetime.now() + timedelta(hours=12)
    
    with pytest.raises(HTTPException) as exc_info:
        validar_prazo_24h(data_proxima)
    
    assert exc_info.value.status_code == 400
    assert "24h" in exc_info.value.detail

def test_validar_prazo_24h_limite():
    """Teste: Exatamente 24h deve passar"""
    data_limite = datetime.now() + timedelta(hours=24, minutes=5)
    assert validar_prazo_24h(data_limite) == True
```

---

### 1.3 Implementar Remarcação de Consultas ⏱️ 2h

**Problema:**
Funcionalidade explícita no enunciado está ausente.

**Impacto:** 🔴 CRÍTICO - Requisito obrigatório não implementado

**Solução:**

#### Passo 1: Criar Schema (15min)

**Arquivo:** `backend/app/schemas/schemas.py`

Adicionar:

```python
class ConsultaRemarcar(BaseModel):
    """Schema para remarcação de consulta"""
    nova_data_hora: datetime = Field(..., description="Nova data e hora da consulta")
    novo_horario_id: Optional[int] = Field(None, description="ID do novo horário disponível (se aplicável)")
    motivo: Optional[str] = Field(None, max_length=200, description="Motivo da remarcação")
    
    @validator('nova_data_hora')
    def validar_data_futura(cls, v):
        if v <= datetime.now():
            raise ValueError('A nova data deve ser futura')
        return v
```

#### Passo 2: Criar Endpoint (1h 15min)

**Arquivo:** `backend/app/routers/pacientes.py`

Adicionar:

```python
@router.patch("/consultas/{consulta_id}/remarcar", response_model=ConsultaResponse)
async def remarcar_consulta(
    consulta_id: int,
    dados: ConsultaRemarcar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_paciente)
):
    """
    Remarca uma consulta existente para nova data/hora
    
    **Regras:**
    - Apenas consultas agendadas podem ser remarcadas
    - Remarcação permitida até 24h antes da consulta atual
    - Nova data deve estar disponível na agenda do médico
    - Não pode haver conflito com outras consultas
    """
    
    # 1. Buscar consulta
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.paciente_id == current_user.paciente.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta.status != 'agendada':
        raise HTTPException(
            status_code=400,
            detail=f"Apenas consultas agendadas podem ser remarcadas. Status atual: {consulta.status}"
        )
    
    # 2. Validar prazo de 24h da consulta ATUAL
    validar_prazo_24h(consulta.data_hora, "remarcação")
    
    # 3. Validar que nova data é futura
    if dados.nova_data_hora <= datetime.now():
        raise HTTPException(status_code=400, detail="Nova data deve ser futura")
    
    # 4. Verificar se médico tem horário disponível no dia/hora solicitado
    dia_semana_map = {
        0: 'segunda', 1: 'terca', 2: 'quarta',
        3: 'quinta', 4: 'sexta', 5: 'sabado', 6: 'domingo'
    }
    dia_semana = dia_semana_map[dados.nova_data_hora.weekday()]
    nova_hora = dados.nova_data_hora.time()
    
    horario_disponivel = db.query(HorarioDisponivel).filter(
        HorarioDisponivel.medico_id == consulta.medico_id,
        HorarioDisponivel.dia_semana == dia_semana,
        HorarioDisponivel.hora_inicio <= nova_hora,
        HorarioDisponivel.hora_fim > nova_hora
    ).first()
    
    if not horario_disponivel:
        raise HTTPException(
            status_code=400,
            detail=f"Médico não tem horário disponível em {dia_semana} às {nova_hora}"
        )
    
    # 5. Verificar conflitos com outras consultas
    conflito = db.query(Consulta).filter(
        Consulta.medico_id == consulta.medico_id,
        Consulta.data_hora == dados.nova_data_hora,
        Consulta.status == 'agendada',
        Consulta.id != consulta_id  # Excluir a própria consulta
    ).first()
    
    if conflito:
        raise HTTPException(
            status_code=400,
            detail="Horário já está ocupado com outra consulta"
        )
    
    # 6. Verificar bloqueios
    bloqueio = db.query(BloqueioHorario).filter(
        BloqueioHorario.medico_id == consulta.medico_id,
        BloqueioHorario.data_hora == dados.nova_data_hora
    ).first()
    
    if bloqueio:
        raise HTTPException(
            status_code=400,
            detail=f"Horário bloqueado pelo médico. Motivo: {bloqueio.motivo}"
        )
    
    # 7. Guardar histórico (opcional - adicionar campo na tabela se quiser)
    # consulta.data_hora_original = consulta.data_hora
    # consulta.motivo_remarcacao = dados.motivo
    
    # 8. Remarcar
    consulta.data_hora = dados.nova_data_hora
    if dados.novo_horario_id:
        consulta.horario_id = dados.novo_horario_id
    consulta.updated_at = datetime.now()
    
    db.commit()
    db.refresh(consulta)
    
    return {
        "message": "Consulta remarcada com sucesso",
        "consulta": consulta
    }
```

#### Passo 3: Testar (30min)

```python
# backend/tests/test_remarcacao.py
def test_remarcar_consulta_sucesso(client, paciente_autenticado):
    # Criar consulta para daqui 48h
    consulta = criar_consulta(data_hora=now() + timedelta(hours=48))
    
    # Remarcar para daqui 72h
    nova_data = (now() + timedelta(hours=72)).isoformat()
    response = client.patch(
        f"/pacientes/consultas/{consulta.id}/remarcar",
        json={"nova_data_hora": nova_data}
    )
    
    assert response.status_code == 200
    assert "remarcada com sucesso" in response.json()["message"]

def test_remarcar_consulta_menos_24h(client):
    # Consulta daqui 12h
    consulta = criar_consulta(data_hora=now() + timedelta(hours=12))
    
    # Tentar remarcar deve falhar
    response = client.patch(
        f"/pacientes/consultas/{consulta.id}/remarcar",
        json={"nova_data_hora": (now() + timedelta(hours=48)).isoformat()}
    )
    
    assert response.status_code == 400
    assert "24h" in response.json()["detail"]
```

---

### 1.4 Bloqueio Automático por 3 Faltas ⏱️ 2h

**Problema:**
Regra crítica do enunciado não funciona. Campo `bloqueado` existe mas nunca é alterado.

**Impacto:** 🔴 CRÍTICO - Regra de negócio não implementada

**Solução:**

#### Passo 1: Adicionar Função de Verificação (45min)

**Arquivo:** `backend/app/utils/validators.py`

Adicionar:

```python
from sqlalchemy.orm import Session
from app.models.models import Consulta, Paciente

def verificar_e_bloquear_por_faltas(paciente_id: int, db: Session) -> dict:
    """
    Verifica se paciente tem 3 faltas consecutivas e bloqueia se necessário.
    
    Args:
        paciente_id: ID do paciente
        db: Sessão do banco de dados
    
    Returns:
        dict: {
            'bloqueado': bool,
            'faltas_consecutivas': int,
            'mensagem': str
        }
    """
    
    # Buscar últimas consultas do paciente (ordenadas por data decrescente)
    consultas = db.query(Consulta).filter(
        Consulta.paciente_id == paciente_id
    ).order_by(
        Consulta.data_hora.desc()
    ).limit(10).all()
    
    if len(consultas) < 3:
        return {
            'bloqueado': False,
            'faltas_consecutivas': 0,
            'mensagem': 'Não há consultas suficientes para verificação'
        }
    
    # Contar faltas consecutivas (começando da mais recente)
    faltas_consecutivas = 0
    for consulta in consultas:
        if consulta.status == 'falta':
            faltas_consecutivas += 1
        elif consulta.status == 'realizada':
            # Se teve consulta realizada, quebra a sequência de faltas
            break
        # Cancelamentos não quebram nem contam
    
    # Bloquear se atingiu 3 faltas consecutivas
    if faltas_consecutivas >= 3:
        paciente = db.query(Paciente).get(paciente_id)
        
        if not paciente.bloqueado:
            paciente.bloqueado = True
            paciente.motivo_bloqueio = "3 faltas consecutivas sem aviso"
            paciente.data_bloqueio = datetime.now()
            db.commit()
            
            return {
                'bloqueado': True,
                'faltas_consecutivas': faltas_consecutivas,
                'mensagem': f'Paciente bloqueado por {faltas_consecutivas} faltas consecutivas'
            }
        else:
            return {
                'bloqueado': True,
                'faltas_consecutivas': faltas_consecutivas,
                'mensagem': 'Paciente já estava bloqueado'
            }
    
    return {
        'bloqueado': False,
        'faltas_consecutivas': faltas_consecutivas,
        'mensagem': f'{faltas_consecutivas} falta(s) consecutiva(s) registrada(s)'
    }
```

#### Passo 2: Criar Endpoint para Marcar Falta (45min)

**Arquivo:** `backend/app/routers/medicos.py`

Adicionar:

```python
from app.utils.validators import verificar_e_bloquear_por_faltas

@router.patch("/consultas/{consulta_id}/marcar-falta")
async def marcar_falta(
    consulta_id: int,
    observacao: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_medico)
):
    """
    Marca paciente como faltante na consulta
    
    **Atenção:** Se paciente tiver 3 faltas consecutivas, será bloqueado automaticamente
    """
    
    # Buscar consulta
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == current_user.medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta.status != 'agendada':
        raise HTTPException(
            status_code=400,
            detail=f"Apenas consultas agendadas podem ser marcadas como falta. Status atual: {consulta.status}"
        )
    
    # Marcar falta
    consulta.status = 'falta'
    if observacao:
        consulta.observacoes = observacao
    consulta.updated_at = datetime.now()
    db.commit()
    
    # Verificar e bloquear por faltas consecutivas
    resultado_bloqueio = verificar_e_bloquear_por_faltas(consulta.paciente_id, db)
    
    return {
        "message": "Paciente marcado como faltante",
        "consulta_id": consulta.id,
        "bloqueio": resultado_bloqueio
    }

@router.patch("/consultas/{consulta_id}/marcar-realizada")
async def marcar_realizada(
    consulta_id: int,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_medico)
):
    """Marca consulta como realizada (com observações opcionais)"""
    
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == current_user.medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta.status != 'agendada':
        raise HTTPException(status_code=400, detail="Apenas consultas agendadas podem ser marcadas como realizadas")
    
    consulta.status = 'realizada'
    if observacoes:
        consulta.observacoes = observacoes
    consulta.updated_at = datetime.now()
    db.commit()
    
    return {
        "message": "Consulta marcada como realizada",
        "consulta_id": consulta.id
    }
```

#### Passo 3: Endpoint Admin para Desbloquear (30min)

**Arquivo:** `backend/app/routers/admin.py`

Adicionar:

```python
@router.patch("/pacientes/{paciente_id}/desbloquear")
async def desbloquear_paciente(
    paciente_id: int,
    justificativa: str = Field(..., min_length=10, max_length=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin)
):
    """
    Desbloqueia paciente que foi bloqueado por faltas
    
    **Requer:** Justificativa obrigatória
    """
    
    paciente = db.query(Paciente).get(paciente_id)
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    if not paciente.bloqueado:
        raise HTTPException(status_code=400, detail="Paciente não está bloqueado")
    
    # Desbloquear
    paciente.bloqueado = False
    motivo_anterior = paciente.motivo_bloqueio
    paciente.motivo_bloqueio = None
    paciente.data_bloqueio = None
    
    # Registrar no histórico (se tiver tabela de auditoria)
    # HistoricoDesbloqueio(paciente_id=paciente_id, justificativa=justificativa, ...)
    
    db.commit()
    
    return {
        "message": "Paciente desbloqueado com sucesso",
        "paciente_id": paciente.id,
        "motivo_bloqueio_anterior": motivo_anterior,
        "justificativa_desbloqueio": justificativa
    }

@router.get("/pacientes/bloqueados")
async def listar_pacientes_bloqueados(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_admin)
):
    """Lista todos os pacientes bloqueados"""
    
    pacientes = db.query(Paciente).filter(
        Paciente.bloqueado == True
    ).all()
    
    return {
        "total": len(pacientes),
        "pacientes": [
            {
                "id": p.id,
                "nome": p.nome_completo,
                "cpf": p.cpf,
                "motivo_bloqueio": p.motivo_bloqueio,
                "data_bloqueio": p.data_bloqueio
            }
            for p in pacientes
        ]
    }
```

---

## 📦 Checklist Fase 1

- [ ] 1.1 Relatórios PDF implementados (3h)
  - [ ] Biblioteca ReportLab instalada
  - [ ] Classe PDFReportGenerator criada
  - [ ] Endpoint /relatorios/pdf/consultas-medico
  - [ ] Endpoint /relatorios/pdf/taxa-cancelamentos
  - [ ] Endpoint /relatorios/pdf/pacientes-frequentes
  - [ ] Testado via Swagger
  
- [ ] 1.2 Validação 24h implementada (1h)
  - [ ] Função validar_prazo_24h criada
  - [ ] Aplicada no cancelamento
  - [ ] Testada com sucesso
  
- [ ] 1.3 Remarcação implementada (2h)
  - [ ] Schema ConsultaRemarcar criado
  - [ ] Endpoint PATCH /consultas/{id}/remarcar
  - [ ] Validações completas
  - [ ] Testado
  
- [ ] 1.4 Bloqueio por faltas (2h)
  - [ ] Função verificar_e_bloquear_por_faltas
  - [ ] Endpoint marcar-falta criado
  - [ ] Endpoint desbloquear criado
  - [ ] Endpoint listar-bloqueados criado
  - [ ] Testado

**Total Fase 1:** ✅ 0/4 tarefas | ⏱️ 8 horas

---

## 🟡 Fase 2: Melhorias Importantes (12 horas)

### 2.1 Endpoint de Observações Médicas ⏱️ 1h

**Problema:**
Campo `observacoes` existe mas não há endpoint específico para adicionar.

**Solução:**

```python
# backend/app/schemas/schemas.py
class ConsultaObservacao(BaseModel):
    observacoes: str = Field(..., min_length=10, max_length=1000)

# backend/app/routers/medicos.py
@router.patch("/consultas/{consulta_id}/observacoes")
async def adicionar_observacao(
    consulta_id: int,
    dados: ConsultaObservacao,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_medico)
):
    """
    Adiciona observações pós-consulta
    
    **Visibilidade:** Apenas médico e administração
    **Requisito:** Consulta deve estar com status 'realizada'
    """
    
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == current_user.medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta.status != 'realizada':
        raise HTTPException(
            status_code=400,
            detail="Observações só podem ser adicionadas em consultas realizadas"
        )
    
    consulta.observacoes = dados.observacoes
    consulta.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Observação adicionada com sucesso"}
```

---

### 2.2 Validações de CPF e CRM ⏱️ 1h

**Solução:**

```python
# backend/app/utils/validators.py
import re

def validar_cpf(cpf: str) -> bool:
    """Valida formato e dígitos verificadores do CPF brasileiro"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validar dígitos verificadores
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    
    if int(cpf[9]) != digito1:
        return False
    
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    
    return int(cpf[10]) == digito2

def validar_crm(crm: str, uf: str) -> bool:
    """Valida formato do CRM brasileiro"""
    crm = re.sub(r'[^0-9]', '', crm)
    
    if not (4 <= len(crm) <= 6):
        return False
    
    ufs_validos = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                   'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                   'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
    
    return uf in ufs_validos

# Aplicar nos schemas
# backend/app/schemas/schemas.py
from app.utils.validators import validar_cpf, validar_crm

class PacienteCreate(BaseModel):
    cpf: str
    
    @validator('cpf')
    def validar_cpf_brasileiro(cls, v):
        if not validar_cpf(v):
            raise ValueError('CPF inválido')
        return v

class MedicoCreate(BaseModel):
    crm: str
    uf_crm: str = Field(..., max_length=2)
    
    @validator('crm')
    def validar_crm_valido(cls, v, values):
        uf = values.get('uf_crm')
        if uf and not validar_crm(v, uf):
            raise ValueError('CRM inválido')
        return v
```

---

### 2.3 Integração Frontend Completa ⏱️ 4h

**Arquivo:** `js/api.js`

Adicionar métodos:

```javascript
// Agendamento
async agendarConsulta(dados) {
    return await this.post('/pacientes/consultas', dados);
}

async remarcarConsulta(consultaId, dados) {
    return await this.patch(`/pacientes/consultas/${consultaId}/remarcar`, dados);
}

async cancelarConsulta(consultaId) {
    return await this.delete(`/pacientes/consultas/${consultaId}/cancelar`);
}

async listarConsultas(filtros = {}) {
    const params = new URLSearchParams(filtros);
    return await this.get(`/pacientes/consultas?${params}`);
}

// Médico
async listarConsultasMedico(data = null) {
    const params = data ? `?data=${data}` : '';
    return await this.get(`/medicos/consultas${params}`);
}

async marcarFalta(consultaId, observacao = null) {
    return await this.patch(`/medicos/consultas/${consultaId}/marcar-falta`, 
        observacao ? { observacao } : {});
}

async adicionarObservacao(consultaId, observacao) {
    return await this.patch(`/medicos/consultas/${consultaId}/observacoes`, 
        { observacoes: observacao });
}

// Admin
async gerarRelatorioPDF(tipo, parametros) {
    const params = new URLSearchParams(parametros);
    const response = await fetch(`${this.baseURL}/admin/relatorios/pdf/${tipo}?${params}`, {
        headers: { 'Authorization': `Bearer ${this.getToken()}` }
    });
    
    if (!response.ok) throw new Error('Erro ao gerar relatório');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio_${tipo}_${Date.now()}.pdf`;
    a.click();
}
```

**Integrar páginas:**
- `paciente/dashboard.js`
- `paciente/agendar.js`
- `paciente/consultas.js`
- `medico/agenda.js`
- `admin/relatorios.js`

---

### 2.4 Testes Unitários Básicos ⏱️ 6h

**Arquivo:** `backend/tests/test_regras_negocio.py`

```python
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

def test_cancelamento_24h(client):
    """Teste: Não deve permitir cancelamento com menos de 24h"""
    # Implementar
    pass

def test_bloqueio_3_faltas(client):
    """Teste: Deve bloquear após 3 faltas consecutivas"""
    # Implementar
    pass

def test_limite_2_consultas(client):
    """Teste: Não deve permitir mais de 2 consultas futuras"""
    # Implementar
    pass

def test_remarcacao_valida(client):
    """Teste: Deve permitir remarcação com prazo válido"""
    # Implementar
    pass
```

---

## 📊 Resumo do Plano

| Fase | Tarefas | Tempo | Prioridade | Status |
|------|---------|-------|------------|--------|
| **Fase 1** | Correções críticas | 8h | 🔴 Alta | Pendente |
| **Fase 2** | Melhorias importantes | 12h | 🟡 Média | Pendente |
| **Fase 3** | Polimento | 8h | 🔵 Baixa | Pendente |
| **TOTAL** | | **28h** | | **0%** |

---

## ✅ Critérios de Aceitação

### Fase 1 (Obrigatório)
- [ ] Todos relatórios PDF funcionando
- [ ] Validação 24h implementada
- [ ] Remarcação funcionando
- [ ] Bloqueio por faltas operacional

### Fase 2 (Recomendado)
- [ ] Observações médicas funcionando
- [ ] CPF/CRM validados
- [ ] Frontend integrado
- [ ] Testes passando

### Fase 3 (Desejável)
- [ ] Logs estruturados
- [ ] CI/CD configurado
- [ ] Documentação completa

---

## 📅 Cronograma Sugerido

| Dia | Período | Atividade | Horas |
|-----|---------|-----------|-------|
| **Dia 1** | Manhã | 1.1 Relatórios PDF | 3h |
| | Tarde | 1.2 Validação 24h + 1.3 Remarcação (início) | 2h |
| **Dia 2** | Manhã | 1.3 Remarcação (fim) + 1.4 Bloqueio faltas | 3h |
| | Tarde | 2.1 Observações + 2.2 Validações | 2h |
| **Dia 3** | Manhã | 2.3 Frontend integração | 4h |
| | Tarde | 2.4 Testes | 3h |
| **Dia 4** | Manhã | 2.4 Testes (fim) + Revisão | 3h |
| | Tarde | Fase 3 (opcional) | 4h |

---

## 🎯 Próximos Passos

1. **Revisar este documento** com a equipe
2. **Aprovar o plano** e recursos necessários
3. **Iniciar Fase 1 - Tarefa 1.1** (Relatórios PDF)
4. **Acompanhar progresso** diariamente
5. **Validar cada entrega** antes de prosseguir

---

**Documento elaborado por:** GitHub Copilot Assistant  
**Aprovado por:** _______________  
**Data de Início:** ___/___/2025  
**Data Prevista de Conclusão:** ___/___/2025
