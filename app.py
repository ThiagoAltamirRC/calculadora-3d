import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página para dispositivos móveis
st.set_page_config(page_title="Calculadora Impressão 3D", page_icon="🖨️", layout="centered")

st.title("🖨️ Calculadora de Custo e Lucro - 3D")
st.write("Preencha os dados abaixo para calcular o custo real e o lucro da sua peça.")

# --- SEÇÃO 1: CONFIGURAÇÕES FIXAS (Valores Padrão) ---
with st.sidebar:
    st.header("⚙️ Configurações de Custo Fixo")
    st.write("Ajuste estes valores se os seus custos mudarem.")
    
    preco_filamento_kg = st.number_input("Preço do PETG (por Kg - R$)", value=110.00, step=5.0)
    tarifa_energia_kwh = st.number_input("Tarifa de Energia (kWh - R$)", value=0.85, step=0.05)
    consumo_impressora_kw = st.number_input("Consumo da Kobra (en kW)", value=0.15, step=0.01)
    valor_impressora = st.number_input("Valor da Máquina + Ace Pro (R$)", value=2800.00, step=100.0)
    vida_util_horas = st.number_input("Vida Útil da Máquina (Horas)", value=5000, step=500)
    valor_hora_trabalho = st.number_input("Sua Hora de Trabalho (R$)", value=20.00, step=1.0)
    taxa_falha_porcentagem = st.slider("Margem para Falhas/Insumos (%)", min_value=0, max_value=50, value=15)

# --- SEÇÃO 2: DADOS DA PEÇA ESPECÍFICA ---
st.subheader("📦 Dados da Peça Atual")

nome_peca = st.text_input("Nome do Modelo / Peça", value="Peça Customizada PETG")

col1, col2 = st.columns(2)
with col1:
    peso_peca = st.number_input("Peso da Peça + Suportes/Purga (gramas)", min_value=0.0, value=120.0, step=1.0)
    tempo_trabalho_horas = st.number_input("Seu tempo gasto (Horas)", min_value=0.0, value=0.25, step=0.05)

with col2:
    tempo_impressao_horas = st.number_input("Tempo de Impressão (Horas)", min_value=0.0, value=4.0, step=0.5)
    preco_venda_cliente = st.number_input("Preço de Venda ao Cliente (R$)", min_value=0.0, value=65.0, step=5.0)

# --- SEÇÃO 3: CÁLCULOS MATEMÁTICOS ---
custo_filamento = (preco_filamento_kg / 1000) * peso_peca
custo_energia = tempo_impressao_horas * consumo_impressora_kw * tarifa_energia_kwh
custo_depreciacao = tempo_impressao_horas * (valor_impressora / vida_util_horas)
custo_mao_obra = tempo_trabalho_horas * valor_hora_trabalho
custo_falhas = (custo_filamento + custo_energia) * (taxa_falha_porcentagem / 100)

custo_total = custo_filamento + custo_energia + custo_depreciacao + custo_mao_obra + custo_falhas
lucro_liquido = preco_venda_cliente - custo_total
margem_lucro = (lucro_liquido / preco_venda_cliente) * 100 if preco_venda_cliente > 0 else 0

# --- SEÇÃO 4: EXIBIÇÃO DOS RESULTADOS ---
st.markdown("---")
st.subheader("💰 Resumo Financeiro")

m1, m2, m3 = st.columns(3)
m1.metric(label="🔴 Custo Total", value=f"R$ {custo_total:.2f}")
m2.metric(label="🟢 Preço Cobrado", value=f"R$ {preco_venda_cliente:.2f}")
m3.metric(label="💵 Lucro Líquido", value=f"R$ {lucro_liquido:.2f}", delta=f"{margem_lucro:.1f}% Margem")

# --- SEÇÃO 5: GERAÇÃO DO RELATÓRIO PDF ---
def gerar_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#2E7D32'), spaceAfter=20)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1B5E20'), spaceBefore=15, spaceAfter=10)
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, leading=16)
    
    # Cabeçalho
    story.append(Paragraph(f"📄 Orçamento de Impressão 3D - {nome_peca}", title_style))
    story.append(Paragraph("Equipamento: Anycubic Kobra 4 + Ace Pro 2 | Material: PETG", text_style))
    story.append(Spacer(1, 15))
    
    # Tabela de Especificações
    story.append(Paragraph("📦 Dados Técnicos do Modelo", heading_style))
    dados_peca = [
        [Paragraph("<b>Métrica</b>", text_style), Paragraph("<b>Valor Informado</b>", text_style)],
        [Paragraph("Peso Total (com Suportes/Purga)", text_style), Paragraph(f"{peso_peca} g", text_style)],
        [Paragraph("Tempo de Execução", text_style), Paragraph(f"{tempo_impressao_horas} horas", text_style)]
    ]
    t1 = Table(dados_peca, colWidths=[250, 250])
    t1.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#E8F5E9')), ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey), ('PADDING', (0,0), (-1,-1), 8)]))
    story.append(t1)
    
    # Tabela de Custos Realizados
    story.append(Paragraph("💰 Detalhamento de Custos e Margens", heading_style))
    dados_custos = [
        [Paragraph("<b>Componente de Custo</b>", text_style), Paragraph("<b>Valor Estimado</b>", text_style)],
        [Paragraph("🧵 Matéria-prima (Filamento)", text_style), Paragraph(f"R$ {custo_filamento:.2f}", text_style)],
        [Paragraph("⚡ Consumo Elétrico", text_style), Paragraph(f"R$ {custo_energia:.2f}", text_style)],
        [Paragraph("🔧 Depreciação / Desgaste do Equipamento", text_style), Paragraph(f"R$ {custo_depreciacao:.2f}", text_style)],
        [Paragraph("⏳ Tempo de Mão de Obra", text_style), Paragraph(f"R$ {custo_mao_obra:.2f}", text_style)],
        [Paragraph("⚠️ Margem Operacional de Falhas", text_style), Paragraph(f"R$ {custo_falhas:.2f}", text_style)],
        [Paragraph("<b>🔴 CUSTO REAL DA PEÇA</b>", text_style), Paragraph(f"<b>R$ {custo_total:.2f}</b>", text_style)],
        [Paragraph("<b>🟢 PREÇO SUGERIDO AO CLIENTE</b>", text_style), Paragraph(f"<b>R$ {preco_venda_cliente:.2f}</b>", text_style)],
        [Paragraph("<b>💵 LUCRO LÍQUIDO OBTIDO</b>", text_style), Paragraph(f"<b>R$ {lucro_liquido:.2f} ({margem_lucro:.1f}%)</b>", text_style)]
    ]
    t2 = Table(dados_custos, colWidths=[250, 250])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (0,6), (1,6), colors.HexColor('#FFEBEE')),
        ('BACKGROUND', (0,7), (1,7), colors.HexColor('#E8F5E9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    story.append(t2)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Botão de download do PDF na interface
pdf_data = gerar_pdf()
st.download_button(
    label="📥 Baixar Relatório em PDF",
    data=pdf_data,
    file_name=f"orcamento_{nome_peca.lower().replace(' ', '_')}.pdf",
    mime="application/pdf",
    use_container_width=True
)
