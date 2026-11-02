import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configuração da página para dispositivos móveis
st.set_page_config(page_title="Calculadora Impressão 3D - Altamirab", page_icon="👨‍💻", layout="centered")

st.title("Calculadora de Custo e Lucro 3D - AltamirLab  👨‍💻")
st.write("Preencha os dados abaixo para calcular o custo real e o lucro da sua peça.")

# --- SEÇÃO 1: CONFIGURAÇÕES FIXAS (Valores Padrão - Apenas para você) ---
with st.sidebar:
    st.header("⚙️ Configurações de Custo Fixo")
    st.write("Ajuste estes valores se os seus custos mudarem.")
    
    preco_filamento_kg = st.number_input("Preço do PETG (por Kg - R$)", value=110.00, step=5.0)
    tarifa_energia_kwh = st.number_input("Tarifa de Energia (kWh - R$)", value=0.96, step=0.05)
    consumo_impressora_kw = st.number_input("Consumo da Kobra (em kW)", value=0.35, step=0.01)
    valor_impressora = st.number_input("Valor da Máquina + Ace Pro (R$)", value=3000.00, step=100.0)
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

# --- SEÇÃO 3: CÁLCULOS MATEMÁTICOS EM TEMPO REAL ---
custo_filamento = (preco_filamento_kg / 1000) * peso_peca
custo_energia = tempo_impressao_horas * consumo_impressora_kw * tarifa_energia_kwh
custo_depreciacao = tempo_impressao_horas * (valor_impressora / vida_util_horas)
custo_mao_obra = tempo_trabalho_horas * valor_hora_trabalho
custo_falhas = (custo_filamento + custo_energia) * (taxa_falha_porcentagem / 100)

custo_total = custo_filamento + custo_energia + custo_depreciacao + custo_mao_obra + custo_falhas
lucro_liquido = preco_venda_cliente - custo_total
margem_lucro = (lucro_liquido / preco_venda_cliente) * 100 if preco_venda_cliente > 0 else 0

# --- SEÇÃO 4: EXIBIÇÃO DOS RESULTADOS (Para você ver na tela) ---
st.markdown("---")
st.subheader("💰 Resumo Financeiro Intermediário")

m1, m2, m3 = st.columns(3)
m1.metric(label="🔴 Seu Custo Real", value=f"R$ {custo_total:.2f}")
m2.metric(label="🟢 Preço Cobrado", value=f"R$ {preco_venda_cliente:.2f}")
m3.metric(label="💵 Lucro Líquido", value=f"R$ {lucro_liquido:.2f}", delta=f"{margem_lucro:.1f}% Margem")

with st.expander("🔍 Ver detalhes dos seus custos internos (Não saem no PDF)"):
    st.write(f"🧵 Filamento: R$ {custo_filamento:.2f}")
    st.write(f"⚡ Energia: R$ {custo_energia:.2f}")
    st.write(f"🔧 Desgaste da Kobra: R$ {custo_depreciacao:.2f}")
    st.write(f"⏳ Sua mão de obra: R$ {custo_mao_obra:.2f}")
    st.write(f"⚠️ Margem de perdas: R$ {custo_falhas:.2f}")

# --- SEÇÃO 5: GERAÇÃO DO RELATÓRIO PDF COMERCIAL (Para o cliente) ---
def gerar_pdf_comercial():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1B5E20'), spaceAfter=5)
    subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.gray, spaceAfter=20)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#2E7D32'), spaceBefore=15, spaceAfter=10)
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=11, leading=16)
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=12, leading=16)
    
    # Cabeçalho do Orçamento
    story.append(Paragraph("📄 ORÇAMENTO DE IMPRESSÃO 3D", title_style))
    story.append(Paragraph("Documento gerado para fins de validação de serviços e fornecimento de peças.", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Tabela de Especificações do Serviço
    story.append(Paragraph("📦 Detalhes do Modelo e Material", heading_style))
    dados_peca = [
        [Paragraph("<b>Item / Descrição</b>", text_style), Paragraph("<b>Especificação Técnica</b>", text_style)],
        [Paragraph("Nome do Modelo Comercial", text_style), Paragraph(nome_peca, text_style)],
        [Paragraph("Material de Fabricação", text_style), Paragraph("PETG de Alta Resistência", text_style)],
        [Paragraph("Massa Final Estimada (Volume)", text_style), Paragraph(f"{peso_peca} g", text_style)],
        [Paragraph("Processo de Fabricação", text_style), Paragraph("FDM (Modelagem por Fusão Depositada)", text_style)]
    ]
    t1 = Table(dados_peca, colWidths=[240, 240])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#E8F5E9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t1)
    
    # Tabela de Preço Final Comercial
    story.append(Paragraph("💰 Condições Financeiras", heading_style))
    dados_comerciais = [
        [Paragraph("<b>Serviço Contratado</b>", text_style), Paragraph("<b>Valor Final</b>", text_style)],
        [Paragraph("Produção, Acabamento e Inspeção de Qualidade 3D", text_style), Paragraph(f"R$ {preco_venda_cliente:.2f}", text_style)],
        [Paragraph("<b>VALOR TOTAL DO INVESTIMENTO</b>", bold_style), Paragraph(f"<b>R$ {preco_venda_cliente:.2f}</b>", bold_style)]
    ]
    t2 = Table(dados_comerciais, colWidths=[330, 150])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (0,2), (1,2), colors.HexColor('#E8F5E9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t2)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Botão de download do PDF na interface
pdf_data = gerar_pdf_comercial()
st.download_button(
    label="📥 Baixar Orçamento Comercial para Cliente (PDF)",
    data=pdf_data,
    file_name=f"orcamento_{nome_peca.lower().replace(' ', '_')}.pdf",
    mime="application/pdf",
    use_container_width=True
)
