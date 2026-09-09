import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from fpdf import FPDF
import qrcode
from io import BytesIO

# Configuração da Página
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

# Estilos CSS
st.markdown("""
    <style>
    .stApp, body, html {
        background-color: #0c0c16 !important;
    }
    
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 85% !important;
        margin: 0 auto !important;
        background-color: #0c0c16 !important;
    }

    html, body, [class*="css"], .stMarkdown, p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    input, select, option {
        color: #000000 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *, div[role="listbox"] * {
        color: #000000 !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .mesa-circle {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        margin: 0 auto 2px auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    .mesa-aberta {
        border: 3px solid #2ea44f;
        background-color: #0f2316;
        color: #4ac26b !important;
    }

    .mesa-fechada {
        border: 3px solid #30363d;
        background-color: #161b22;
        color: #ffffff !important;
    }

    .mesa-pronta-alerta {
        border: 3px solid #ff4b4b;
        background-color: #2b0d0d;
        color: #ff6b6b !important;
        animation: borda-vermelha-piscar 1s infinite;
    }

    @keyframes borda-vermelha-piscar {
        0% { border: 3px solid #ff4b4b; box-shadow: 0 0 10px #ff4b4b; }
        50% { border: 3px solid #ffa0a0; box-shadow: none; }
        100% { border: 3px solid #ff4b4b; box-shadow: 0 0 10px #ff4b4b; }
    }

    .piscar-alerta {
        animation: piscar-aviso 1s infinite;
        color: #ff4b4b !important;
    }

    @keyframes piscar-aviso {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .fatura-box {
        background-color: #141428;
        border: 2px dashed #ffb703;
        padding: 20px;
        border-radius: 10px;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: bold !important;
        padding: 4px 8px !important;
        font-size: 0.85rem !important;
        color: #000000 !important;
    }
    
    .stButton>button p, .stButton>button span {
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ESTADO_CAIXA = "caixa_status.txt"
ARQUIVO_DADOS_MESAS = "mesas_dados.json"
ARQUIVO_HISTORICO_VENDAS = "historico_vendas.json"
ARQUIVO_SAIDAS_CAIXA = "saidas_caixa.json"
ARQUIVO_STOCK = "stock_dados.json"
ARQUIVO_FECHOS_CAIXA = "fechos_caixa_historico.json"
ARQUIVO_ATENDIMENTOS_GARCON = "atendimentos_garcon.json"
ARQUIVO_RH_COLABORADORES = "rh_colaboradores.json"
ARQUIVO_VENDAS_EXCLUIDAS = "vendas_excluidas.json"
ARQUIVO_SESSAO_CAIXA_OPERADOR = "sessao_caixa_operador.json"

def ler_estado_caixa_disco():
    if os.path.exists(ARQUIVO_ESTADO_CAIXA):
        try:
            with open(ARQUIVO_ESTADO_CAIXA, "r") as f:
                return f.read().strip() == "aberto"
        except:
            pass
    return False

def gravar_estado_caixa_disco(aberto: bool):
    try:
        with open(ARQUIVO_ESTADO_CAIXA, "w") as f:
            f.write("aberto" if aberto else "fechado")
    except:
        pass

def carregar_sessao_operador():
    if os.path.exists(ARQUIVO_SESSAO_CAIXA_OPERADOR):
        try:
            with open(ARQUIVO_SESSAO_CAIXA_OPERADOR, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"logado": False, "operador": "Nenhum", "periodo": "N/A", "turno_aberto": False, "saldo_inicial": 0.0, "hora_abertura": ""}

def salvar_sessao_operador(sessao_dict):
    try:
        with open(ARQUIVO_SESSAO_CAIXA_OPERADOR, "w", encoding="utf-8") as f:
            json.dump(sessao_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_mesas_disco():
    if os.path.exists(ARQUIVO_DADOS_MESAS):
        try:
            with open(ARQUIVO_DADOS_MESAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {str(i): {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "garcon": "Não atribuído", "fatura_emitida": None} for i in range(1, 31)}

def salvar_mesas_disco(mesas_dict):
    try:
        with open(ARQUIVO_DADOS_MESAS, "w", encoding="utf-8") as f:
            json.dump(mesas_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_historico_vendas():
    if os.path.exists(ARQUIVO_HISTORICO_VENDAS):
        try:
            with open(ARQUIVO_HISTORICO_VENDAS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if dados:
                    return dados
        except:
            pass
    return []

def salvar_historico_vendas(hist_list):
    try:
        with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
            json.dump(hist_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_fechos_caixa():
    if os.path.exists(ARQUIVO_FECHOS_CAIXA):
        try:
            with open(ARQUIVO_FECHOS_CAIXA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_fechos_caixa(fechos_list):
    try:
        with open(ARQUIVO_FECHOS_CAIXA, "w", encoding="utf-8") as f:
            json.dump(fechos_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_saidas_caixa():
    if os.path.exists(ARQUIVO_SAIDAS_CAIXA):
        try:
            with open(ARQUIVO_SAIDAS_CAIXA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_saidas_caixa(saidas_list):
    try:
        with open(ARQUIVO_SAIDAS_CAIXA, "w", encoding="utf-8") as f:
            json.dump(saidas_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_vendas_excluidas():
    if os.path.exists(ARQUIVO_VENDAS_EXCLUIDAS):
        try:
            with open(ARQUIVO_VENDAS_EXCLUIDAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_vendas_excluidas(exc_list):
    try:
        with open(ARQUIVO_VENDAS_EXCLUIDAS, "w", encoding="utf-8") as f:
            json.dump(exc_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_atendimentos_garcon():
    if os.path.exists(ARQUIVO_ATENDIMENTOS_GARCON):
        try:
            with open(ARQUIVO_ATENDIMENTOS_GARCON, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_atendimentos_garcon(atend_list):
    try:
        with open(ARQUIVO_ATENDIMENTOS_GARCON, "w", encoding="utf-8") as f:
            json.dump(atend_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_rh_disco():
    if os.path.exists(ARQUIVO_RH_COLABORADORES):
        try:
            df_loaded = pd.read_json(ARQUIVO_RH_COLABORADORES)
            if not df_loaded.empty:
                return df_loaded
        except:
            pass
    return pd.DataFrame([
        ["G001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042"],
        ["G002", "Ana Paula", "Garçon", "912333444", "009876543LA031"]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])

def salvar_rh_disco(df):
    try:
        df.to_json(ARQUIVO_RH_COLABORADORES, orient="split", index=False)
    except:
        pass

def carregar_stock_disco():
    if os.path.exists(ARQUIVO_STOCK):
        try:
            df_loaded = pd.read_json(ARQUIVO_STOCK)
            if not df_loaded.empty:
                return df_loaded
        except:
            pass
    return pd.DataFrame([
        ["Água 0.5L", "Bebidas", 50, 300.0],
        ["Refrigerante Cola", "Bebidas", 40, 450.0],
        ["Cerveja Cuca", "Bebidas", 60, 500.0],
        ["Vinho Tinto", "Bebidas", 15, 4500.0],
        ["Frango à Grega", "Refeições", 20, 3500.0],
        ["Bife a Cavalo", "Refeições", 15, 4000.0],
        ["Pudim de Leite", "Sobremesas", 25, 1500.0],
        ["Salada de Frutas", "Sobremesas", 30, 1200.0]
    ], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

def salvar_stock_disco(df):
    try:
        df.to_json(ARQUIVO_STOCK, orient="split", index=False)
    except:
        pass

def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def gerar_pdf_fatura(fat_data, num_mesa):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Restaurante Nobre Sabor", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Fatura / Recibo — Mesa {num_mesa}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Data: {fat_data['data']}", ln=True)
    pdf.cell(0, 7, f"Cliente: {fat_data['cliente']}", ln=True)
    pdf.cell(0, 7, f"Telefone: {fat_data['telefone']}", ln=True)
    if fat_data.get('nif'):
        pdf.cell(0, 7, f"NIF: {fat_data['nif']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, "Descrição do Item", 1)
    pdf.cell(20, 8, "Qtd", 1, align="C")
    pdf.cell(40, 8, "Preço Unit.", 1, align="R")
    pdf.cell(40, 8, "Total", 1, align="R", ln=True)
    
    pdf.set_font("Arial", "", 10)
    for item in fat_data['itens']:
        sub_item = item['quantidade'] * item['preco']
        pdf.cell(90, 8, str(item['item']), 1)
        pdf.cell(20, 8, str(item['quantidade']), 1, align="C")
        pdf.cell(40, 8, f"{item['preco']:,.2f} Kz", 1, align="R")
        pdf.cell(40, 8, f"{sub_item:,.2f} Kz", 1, align="R", ln=True)
        
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Forma de Pagamento: {fat_data['pagamento_detalhe']}", ln=True)
    
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, f"Total Pago: {fat_data['total']:,.2f} Kz", ln=True, align="R")
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Muito obrigado pela sua preferência! Volte sempre ao Restaurante Nobre Sabor.", ln=True, align="C")
    
    nome_arquivo = f"fatura_mesa_{num_mesa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# Parâmetros URL
mesa_detectada = None
perfil_url = None

try:
    query_params = st.query_params
    if "mesa" in query_params:
        mesa_detectada = int(query_params.get("mesa"))
    if "perfil" in query_params:
        perfil_url = query_params.get("perfil")
except Exception:
    try:
        old_params = st.experimental_get_query_params()
        if "mesa" in old_params:
            mesa_detectada = int(old_params["mesa"][0])
        if "perfil" in old_params:
            perfil_url = old_params["perfil"][0]
    except Exception:
        pass

st.session_state.caixa_aberto = ler_estado_caixa_disco()

if "stock" not in st.session_state:
    st.session_state.stock = carregar_stock_disco()

if "rh" not in st.session_state:
    st.session_state.rh = carregar_rh_disco()

# ==========================================
# ÁREA: CLIENTE (MICRO-TABLET ESTREITO E COMPACTO)
# ==========================================
@st.fragment(run_every=4)
def area_cliente():
    st.markdown("""
        <style>
        .tablet-container { max-width: 320px; margin: 0 auto; background: #000000; border: 4px solid #111111; border-radius: 12px; padding: 6px; }
        .stButton button { padding: 0.2rem 0.4rem; font-size: 0.75rem; background-color: #111111; color: #ffffff; border: 1px solid #333333; }
        .stButton button:hover { background-color: #222222; border-color: #555555; }
        .element-container, .stTextInput, .stSelectbox { margin-bottom: -0.5rem !important; }
        .stTabs [data-baseweb="tab-list"] { background-color: #000000; }
        .stTabs [data-baseweb="tab"] { background-color: #000000; color: #aaaaaa; font-size: 0.70rem; }
        .stTabs [aria-selected="true"] { background-color: #111111 !important; color: #ffb703 !important; }
        @media (max-width: 400px) { .tablet-container { border: none; padding: 0; background: #000000; } }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tablet-container">', unsafe_allow_html=True)

    if not (mesa_detectada and 1 <= mesa_detectada <= 30):
        st.error("⚠️ Mesa inválida! Escaneie o QR correto.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    num_mesa = mesa_detectada
    mesas_data = carregar_mesas_disco()
    dados_m = mesas_data[str(num_mesa)]

    # 1. SE A FATURA JÁ FOI EMITIDA PELO CAIXA (Exibe Fatura Digital e Agradecimento)
    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<h4 style='text-align:center; font-size:0.9rem; color:#ffffff;'>🧾 Fatura Digital</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:0.75rem; color:#ffb703;'><b>Restaurante Nobre Sabor</b></p>", unsafe_allow_html=True)
        
        for item in fat['itens']:
            st.markdown(f"<span style='font-size:0.7rem; color:#cccccc;'>- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.0f}Kz</span>", unsafe_allow_html=True)
            
        st.markdown(f"<b style='font-size:0.8rem; color:#ffffff;'>Total Pago: {fat['total']:,.2f}Kz</b>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='background-color: #111118; padding: 10px; border-radius: 6px; border: 1px solid #ffb703; text-align: center; margin: 10px 0;'>
                <p style='color: #4ac26b; font-size: 0.8rem; font-weight: bold; margin-bottom: 4px;'>🙏 Muito Obrigado!</p>
                <p style='color: #cccccc; font-size: 0.7rem; line-height: 1.2;'>Agradecemos a sua preferência por ter estado connosco no <b>Restaurante Nobre Sabor</b>. Volte sempre!</p>
            </div>
        """, unsafe_allow_html=True)

        try:
            pdf_path = gerar_pdf_fatura(fat, num_mesa)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Descarregar PDF", data=f, file_name=f"Fatura_NobreSabor_Mesa_{num_mesa}.pdf", use_container_width=True)
        except Exception:
            pass
            
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 2. SE O CLIENTE AINDA NÃO ESTÁ REGISTADO (Boas-vindas e Registo)
    if not dados_m.get("cliente"):
        st.markdown(f"""
            <div style='text-align: center; background: #111118; padding: 12px; border-radius: 8px; border: 1px solid #ffb703; margin-bottom: 10px;'>
                <h4 style='font-size:0.95rem; color:#ffffff; margin-bottom: 4px;'>✨ Bem-vindo(a) ao Nobre Sabor!</h4>
                <p style='font-size:0.75rem; color:#cccccc; margin: 0;'>Por favor, faça o seu registo para iniciar o atendimento na <b>Mesa {num_mesa}</b>.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form(f"fc_{num_mesa}"):
            nome = st.text_input("Seu Nome:", placeholder="Ex: João Silva")
            tel = st.text_input("Telemóvel:", placeholder="Ex: 923456789")
            nif = st.text_input("NIF (Opcional):", placeholder="NIF para fatura")
            whatsapp = st.checkbox("Deseja entrar no Grupo WhatsApp do Restaurante?")
            
            if st.form_submit_button("Entrar e Começar", use_container_width=True) and nome and tel:
                dados_m["cliente"] = {"nome": nome, "telefone": tel, "nif": nif, "whatsapp": whatsapp}
                dados_m["status"] = "Aberta"
                salvar_mesas_disco(mesas_data)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 3. CLIENTE REGISTADO: ABAS DE PEDIDOS, CONSUMO E EVENTOS
    else:
        cli = dados_m["cliente"]
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.75rem; color:#ffb703; margin-bottom:6px; text-align:center; background:#111111; padding:5px; border-radius:6px;'>Mesa {num_mesa} | <b>{cli['nome']}</b></div>", unsafe_allow_html=True)
        
        t_menu, t_cons, t_ev = st.tabs(["📋 Fazer Pedido", "📊 Consultar Conta", "🎉 Eventos"])
        
        # --- ABA 1: FAZER PEDIDO (Com Refeições, Bebidas, Sobremesas e Outros) ---
        with t_menu:
            categorias_fixas = ["Bebidas", "Refeições", "Sobremesas", "Outros"]
            
            # Garantir compatibilidade com itens de utilidades na categoria Outros
            if 'stock' in st.session_state and not st.session_state.stock.empty:
                stock_df = st.session_state.stock.copy()
                # Adiciona itens utilitários predefinidos caso não estejam na base de stock
                utilitarios_extras = [
                    {"Categoria": "Outros", "Produto": "Copo", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Guardanapos", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Talheres", "Preço Unitário": 0.0}
                ]
                import pandas as pd
                stock_df = pd.concat([stock_df, pd.DataFrame(utilitarios_extras)], ignore_index=True)
            else:
                import pandas as pd
                stock_df = pd.DataFrame([
                    {"Categoria": "Outros", "Produto": "Copo", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Guardanapos", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Talheres", "Preço Unitário": 0.0}
                ])

            cats_disponiveis = [c for c in categorias_fixas if c in stock_df['Categoria'].unique().tolist()]
            if not cats_disponiveis:
                cats_disponiveis = stock_df['Categoria'].unique().tolist()

            cat = st.selectbox("Categoria:", cats_disponiveis, key="c_cat")
            itens = stock_df[stock_df['Categoria'] == cat]
            
            if not itens.empty:
                with st.form(f"fp_{num_mesa}", clear_on_submit=True):
                    prod = st.selectbox("Item:", itens['Produto'].tolist())
                    qtd = st.number_input("Quantidade:", 1, 99, 1)
                    obs_cliente = st.text_input("Observação (opcional):", placeholder="Ex: Sem gelo, bem passado...")
                    
                    if st.form_submit_button("🚀 Enviar Pedido", use_container_width=True):
                        p_row = itens[itens['Produto'] == prod].iloc[0]
                        preco_unit = float(p_row['Preço Unitário']) if 'Preço Unitário' in p_row else 0.0
                        
                        is_ref = cat.lower() in ["refeições", "refeicoes", "pratos", "comida"]
                        
                        dados_m["pedidos"].append({
                            "item": prod, 
                            "tipo": cat, 
                            "quantidade": int(qtd),
                            "preco": preco_unit, 
                            "origem": f"Cliente ({cli['nome']})",
                            "observacao": obs_cliente, 
                            "status": "Confirmado" if not is_ref else "Pendente",
                            "cozinha_status": "N/A" if not is_ref else "Pendente", 
                            "hora": datetime.now().strftime("%H:%M")
                        })
                        
                        dados_m["total"] = float(sum(p['quantidade']*p['preco'] for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"]))
                        salvar_mesas_disco(mesas_data)
                        st.success("Pedido enviado com sucesso!")
                        st.rerun()

        # --- ABA 2: CONSULTAR CONTA & PEDIR FECHO ---
        with t_cons:
            total_parcial = 0
            for p in dados_m["pedidos"]:
                t_item = p['quantidade'] * p['preco']
                if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                    total_parcial += t_item
                st.markdown(f"<span style='font-size:0.7rem; color:#cccccc;'>• {p['quantidade']}x {p['item']} ({t_item:,.0f}Kz) — <b>{p['status']}</b></span>", unsafe_allow_html=True)
            
            st.markdown(f"<b style='font-size:0.75rem; color:#ffffff;'>Total Parcial: {total_parcial:,.2f}Kz</b>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 6px 0; border-color: #222;'>", unsafe_allow_html=True)
            
            if dados_m.get("solicitou_fecho"):
                st.info("⏳ Pedido de fecho enviado ao caixa. Aguarde o atendimento.")
                if st.button("Cancelar Pedido de Fecho", key=f"cf_{num_mesa}", use_container_width=True):
                    dados_m["solicitou_fecho"] = False
                    salvar_mesas_disco(mesas_data)
                    st.rerun()
            else:
                if st.button("🔔 Pedir Conta / Fechar", type="primary", use_container_width=True):
                    dados_m["solicitou_fecho"] = True
                    salvar_mesas_disco(mesas_data)
                    st.success("Conta solicitada ao caixa com sucesso!")
                    st.rerun()

        # --- ABA 3: EVENTOS ---
        with t_ev:
            st.markdown("<span style='font-size:0.7rem; color:#cccccc;'><b>Agenda Cultural - Nobre Sabor:</b><br>• Sexta-feira: Música ao Vivo<br>• Sábado: Karaoke (Grupo FF)</span>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS (CIRCULAR INTERATIVO & ADIÇÃO DE PEDIDOS)
# ==========================================
@st.fragment(run_every=5)
def area_caixa_mesas():
    # Injeção de CSS para círculos interativos, compactos e alertas
    st.markdown("""
        <style>
        @keyframes oscilarVermelho {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            50% { transform: scale(1.04); box-shadow: 0 0 10px 5px rgba(239, 68, 68, 0.9); background-color: #ef4444 !important; color: #fff !important; }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        @keyframes oscilarVerde {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 194, 107, 0.7); }
            50% { transform: scale(1.04); box-shadow: 0 0 10px 5px rgba(74, 194, 107, 0.9); background-color: #4ac26b !important; color: #000 !important; }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 194, 107, 0); }
        }
        .mesa-conta-solicitada {
            animation: oscilarVermelho 1.2s infinite ease-in-out;
            border: 2px solid #fff !important;
        }
        .mesa-pronta-alerta {
            animation: oscilarVerde 1.2s infinite ease-in-out;
            border: 2px solid #fff !important;
        }
        .mesa-circle {
            background-color: #1a1a2e;
            border: 1.5px solid #333355;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin: 0 auto;
            color: #fff;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            overflow: hidden;
            padding: 2px;
        }
        .mesa-aberta { background-color: #1f3b2c; border: 1.5px solid #4ac26b; }
        .mesa-fechada { background-color: #141420; }
        
        .pedido-item-compacto {
            margin-bottom: 2px !important;
            padding-bottom: 2px !important;
            line-height: 1.2 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    mesas_data = carregar_mesas_disco()

    # --- VERIFICAÇÃO DE PEDIDOS PRONTOS QUE AINDA NÃO FORAM SILENCIADOS ---
    tem_mesas_prontas_com_alerta = False
    for str_m, dados_m in mesas_data.items():
        tem_pronto = any(p.get("cozinha_status") == "Feito" for p in dados_m.get("pedidos", []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"])
        silenciado_pelo_operador = st.session_state.get(f"silenciar_alarme_mesa_{str_m}", False)
        
        if tem_pronto and not silenciado_pelo_operador:
            tem_mesas_prontas_com_alerta = True
            break

    # Se houver mesas prontas, garantimos um botão de ativação de áudio caso o navegador bloqueie o autoplay
    if tem_mesas_prontas_com_alerta:
        if not st.session_state.get("audio_liberado_usuario", False):
            if st.button("🔊 CLIQUE AQUI PARA ATIVAR O SOM DOS PRONTOS", type="primary", use_container_width=True):
                st.session_state["audio_liberado_usuario"] = True
                st.rerun()

    # Injeção de áudio via Web Audio API (só toca se o utilizador já tiver interagido/liberado)
    if tem_mesas_prontas_com_alerta and st.session_state.get("audio_liberado_usuario", False):
        st.markdown("""
            <script>
            if (!window.audioAlertaInterval) {
                window.audioAlertaInterval = setInterval(() => {
                    try {
                        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.type = 'sine';
                        osc.frequency.value = 587.33; // Nota D5
                        gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start();
                        osc.stop(audioCtx.currentTime + 0.25);
                    } catch(e) {}
                }, 1200);
            }
            </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <script>
            if (window.audioAlertaInterval) {
                clearInterval(window.audioAlertaInterval);
                window.audioAlertaInterval = null;
            }
            </script>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-bottom:8px;'>💻 Controlo do Caixa - Operador</h3>", unsafe_allow_html=True)
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO pela Administração.** O administrador precisa abrir o dia.")
        return

    sessao_op = carregar_sessao_operador()

    # 1. LOGIN DO OPERADOR DE CAIXA
    if not sessao_op["logado"]:
        with st.form("form_login_caixa_operador"):
            st.markdown("### 🔐 Autenticação do Funcionário de Caixa")
            utilizador_input = st.text_input("Utilizador:")
            periodo_input = st.selectbox("Período:", ["Dia", "Noite"])
            senha_input = st.text_input("Senha:", type="password")
            
            btn_login_cx = st.form_submit_button("Entrar no Caixa", use_container_width=True)
            if btn_login_cx:
                if utilizador_input and senha_input:
                    sessao_op["logado"] = True
                    sessao_op["operador"] = utilizador_input
                    sessao_op["periodo"] = periodo_input
                    sessao_op["turno_aberto"] = False
                    sessao_op["saldo_inicial"] = 0.0
                    sessao_op["hora_abertura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    salvar_sessao_operador(sessao_op)
                    st.success(f"Bem-vindo(a), {utilizador_input}! Faça agora a abertura do período.")
                    st.rerun()
                else:
                    st.warning("Preencha o utilizador e a senha.")
        return

    # 2. ABERTURA DO CAIXA DO PERÍODO
    if not sessao_op["turno_aberto"]:
        st.markdown(f"""
            <div style="background-color: #141428; padding: 15px; border-radius: 8px; border: 1px solid #ffb703; margin-bottom: 15px;">
                <p>👤 <b>Utilizador:</b> {sessao_op['operador']}</p>
                <p>⏰ <b>Período:</b> {sessao_op['periodo']}</p>
                <p style="color: #ffb703;">O saldo inicial provém estritamente do valor atribuído pelo ADM. Clique abaixo para abrir o seu turno.</p>
            </div>
        """, unsafe_allow_html=True)
        
        saidas_todas = carregar_saidas_caixa()
        saidas_destinadas = [s for s in saidas_todas if s.get("Destino Utilizador") == sessao_op['operador'] and s.get("Período") == sessao_op['periodo']]
        saldo_inicial_recebido = sum(float(s['Valor']) for s in saidas_destinadas)
        
        if saidas_destinadas:
            st.success(f"💵 Entrada detetada vinda do ADM: **{saldo_inicial_recebido:,.2f} Kz**")
        else:
            st.info("💵 Sem fundo de maneio atribuído pelo ADM (A iniciar com 0.00 Kz).")

        col_op1, col_op2 = st.columns(2)
        with col_op1:
            if st.button("🟢 Abertura do Caixa do Período", type="primary", use_container_width=True):
                sessao_op["turno_aberto"] = True
                sessao_op["saldo_inicial"] = saldo_inicial_recebido
                sessao_op["hora_abertura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                salvar_sessao_operador(sessao_op)
                st.success("Caixa aberto com sucesso para este período!")
                st.rerun()
        with col_op2:
            if st.button("🚪 Terminar Sessão / Sair", use_container_width=True):
                sessao_op["logado"] = False
                sessao_op["operador"] = "Nenhum"
                sessao_op["turno_aberto"] = False
                sessao_op["saldo_inicial"] = 0.0
                salvar_sessao_operador(sessao_op)
                st.rerun()
        return  

    # 3. CAIXA EM FUNCIONAMENTO
    hist_vendas = carregar_historico_vendas()
    cardapio_data = carregar_cardapio_disco() if 'carregar_cardapio_disco' in globals() else {}

    hora_abertura_turno = sessao_op.get("hora_abertura", "2000-01-01 00:00:00")
    vendas_turno = [
        v for v in hist_vendas 
        if v.get("Data", "") >= hora_abertura_turno and v.get("Operador", sessao_op['operador']) == sessao_op['operador']
    ]

    total_dinheiro_vendas = sum(float(v.get('Valor Dinheiro', 0)) for v in vendas_turno)
    total_tpa_vendas = sum(float(v.get('Valor TPA', 0)) for v in vendas_turno)
    
    saldo_inicial_turno = float(sessao_op.get("saldo_inicial", 0.0))
    saldo_em_caixa_fisico = saldo_inicial_turno + total_dinheiro_vendas

    # Layout superior
    st.markdown(f"""
        <div style="background-color: #141428; padding: 12px 16px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #2a2a4a; display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <span style="font-size: 0.9rem; color: #ffb703; font-weight: bold;">Saldo em Caixa:</span><br>
                <span style="font-size: 0.85rem; color: #a0a0c0; margin-left: 10px;">Dinheiro:</span> <b style="color: #4ac26b;">{saldo_em_caixa_fisico:,.2f} Kz</b><br>
                <span style="font-size: 0.85rem; color: #a0a0c0; margin-left: 10px;">TPA:</span> <b style="color: #ffb703;">{total_tpa_vendas:,.2f} Kz</b>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.95rem; color: #fff;">Operador : <b>{sessao_op['operador']}</b></span><br>
                <span style="font-size: 0.75rem; color: #888;">Período: {sessao_op['periodo']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ABAS DE NAVEGAÇÃO DO CAIXA
    aba_operador_1, aba_operador_2, aba_operador_3, aba_operador_4 = st.tabs([
        "🗺️ Mesas & Operações", 
        "📱 QR Codes das Mesas", 
        "📚 Histórico de Vendas", 
        "🔒 Fecho de Caixa"
    ])

    # --- ABA 4: FECHO DE CAIXA ---
    with aba_operador_4:
        st.markdown("### 🔒 Auditoria e Fecho de Caixa do Período")
        st.info("Reveja abaixo todo o movimento do seu turno, itens vendidos, quantidades e valores acumulados.")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1: st.metric("Saldo Inicial (Fundo)", f"{saldo_inicial_turno:,.2f} Kz")
        with col_res2: st.metric("Vendas em Dinheiro", f"{total_dinheiro_vendas:,.2f} Kz")
        with col_res3: st.metric("Vendas em TPA", f"{total_tpa_vendas:,.2f} Kz")
            
        st.markdown("---")
        st.markdown("#### 📦 Extrato de Produtos Vendidos no Turno")
        
        if vendas_turno:
            itens_consolidados = {}
            for v in vendas_turno:
                for p in v.get("pedidos", []):
                    if p.get('status') in ["Anulado", "Recusado pela Cozinha"]:
                        continue
                    nome_prod = p.get('item', 'Desconhecido')
                    qtd_prod = int(p.get('quantidade', 1))
                    preco_prod = float(p.get('preco', 0.0))
                    
                    if nome_prod not in itens_consolidados:
                        itens_consolidados[nome_prod] = {"quantidade": 0, "total": 0.0, "preco": preco_prod}
                    itens_consolidados[nome_prod]["quantidade"] += qtd_prod
                    itens_consolidados[nome_prod]["total"] += (qtd_prod * preco_prod)
            
            for prod, dados in itens_consolidados.items():
                st.write(f"- **{dados['quantidade']}x** {prod} — {dados['total']:,.2f} Kz")
            
            total_geral_turno = sum(d["total"] for d in itens_consolidados.values())
            st.markdown(f"### 💰 Faturação Total do Turno: **{total_geral_turno:,.2f} Kz**")
            
            if st.button("🔒 Fechar Período de Caixa com Segurança", type="primary", use_container_width=True):
                sessao_op["logado"] = False
                sessao_op["operador"] = "Nenhum"
                sessao_op["turno_aberto"] = False
                sessao_op["saldo_inicial"] = 0.0
                salvar_sessao_operador(sessao_op)
                st.success("Período de caixa encerrado com sucesso!")
                st.rerun()
        else:
            st.info("Ainda não existem vendas registadas neste turno.")

    # --- ABA 3: HISTÓRICO DE VENDAS ---
    with aba_operador_3:
        st.markdown("### 🔍 Histórico Detalhado de Vendas por Mesa / Cliente")
        if hist_vendas:
            pesquisa_cli = st.text_input("Filtrar por Nome do Cliente ou Telefone:", placeholder="Digite o nome...", key="filtro_hist_cli_caixa")
            vendas_filtradas = [v for v in hist_vendas if pesquisa_cli.lower() in str(v.get("Cliente", "")).lower() or pesquisa_cli in str(v.get("Telefone", ""))] if pesquisa_cli else hist_vendas
            
            for v_item in reversed(vendas_filtradas):
                with st.expander(f"Mesa {v_item.get('Mesa', '?')} — Cliente: {v_item.get('Cliente', 'Desconhecido')} | Total: {v_item.get('Total', 0.0):,.2f} Kz"):
                    st.write(f"**Operador:** {v_item.get('Operador', '')} | **Data:** {v_item.get('Data', '')}")
                    for p in v_item.get("pedidos", []):
                        st.markdown(f"- {p.get('quantidade', 1)}x {p.get('item')} ({p.get('preco', 0):,.2f} Kz)")
        else:
            st.info("Sem registos no histórico de vendas.")

    # --- ABA 2: QR CODES DAS MESAS ---
    with aba_operador_2:
        st.markdown("### 📱 Gestão de QR Codes para Auto-Atendimento nas Mesas")
        st.info("Aqui pode visualizar e descarregar os códigos QR correspondentes a cada mesa para os clientes efetuarem pedidos.")
        
        col_qr1, col_qr2 = st.columns(2)
        with col_qr1:
            mesa_qr_sel = st.selectbox("Selecione a Mesa para o QR Code:", list(range(1, 31)), key="select_mesa_qr_caixa")
        
        try:
            import qrcode
            from io import BytesIO
            
            # Gerador visual do QR Code para a mesa selecionada
            url_mesa = f"https://seuapp.streamlit.app/?mesa={mesa_qr_sel}"
            img_qr = qrcode.make(url_mesa)
            buf = BytesIO()
            img_qr.save(buf, format="PNG")
            
            st.markdown(f"#### QR Code - Mesa {mesa_qr_sel}")
            st.image(buf.getvalue(), width=250)
            st.caption(Link de Acesso: `{url_mesa}` text)
        except ImportError:
            st.warning("A biblioteca 'qrcode' não está instalada no ambiente Python. Instale com `pip install qrcode[pil]` para gerar as imagens.")

    # --- ABA 1: MESAS & OPERAÇÕES ---
    with aba_operador_1:
        col_esq, col_dir = st.columns([1.2, 0.8])

        with col_dir:
            st.markdown("#### MESAS")
            
            cols_grelha = 3
            rows = 10
            mesa_idx = 1
            
            for r in range(rows):
                cols = st.columns(cols_grelha)
                for c in range(cols_grelha):
                    if mesa_idx > 30:
                        break
                    str_m = str(mesa_idx)
                    dados_m = mesas_data[str_m]
                    
                    status_m = dados_m.get("status", "Fechada")
                    total_m = dados_m.get("total", 0.0)
                    cli_m = dados_m.get("cliente")
                    solicitou_fecho = dados_m.get("solicitou_fecho", False)
                    
                    tem_pronto = any(p.get("cozinha_status") == "Feito" for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"])
                    tem_bebida = any("bebida" in str(p.get("categoria", "")).lower() or any(w in str(p.get("item", "")).lower() for w in ["sumo", "cerveja", "refrigerante", "vinho", "agua"]) for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"])
                    tem_sobremesa = any("sobremesa" in str(p.get("categoria", "")).lower() for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"])
                    
                    simbolos_topo_lista = []
                    if tem_pronto: simbolos_topo_lista.append("🍲")
                    if tem_bebida: simbolos_topo_lista.append("🍹")
                    if tem_sobremesa: simbolos_topo_lista.append("🍰")
                    simbolo_topo = " ".join(simbolos_topo_lista)

                    if solicitou_fecho:
                        classe_css = "mesa-conta-solicitada"
                    elif tem_pronto:
                        classe_css = "mesa-pronta-alerta"
                    elif status_m == "Aberta" or cli_m:
                        classe_css = "mesa-aberta"
                    else:
                        classe_css = "mesa-fechada"

                    with cols[c]:
                        nome_cliente_curto = cli_m['nome'].split()[0] if cli_m and isinstance(cli_m, dict) and cli_m.get('nome') else "Livre"
                        
                        # Bloco superior com o Sino interativo para silenciar o alarme ao clicar diretamente nele
                        if solicitou_fecho or tem_pronto:
                            badge_html = '<div style="text-align: center; margin-bottom: 2px; white-space: nowrap;">'
                            if solicitou_fecho:
                                badge_html += '<span style="background-color: #ef4444; color: white; font-size: 0.65rem; font-weight: bold; padding: 2px 4px; border-radius: 4px; margin-right: 2px;">Pediu Conta 💵</span>'
                            badge_html += '</div>'
                            st.markdown(badge_html, unsafe_allow_html=True)
                            
                            # Botão específico para clicar diretamente em cima do Sino do Prato e calar o alarme desta mesa
                            if tem_pronto:
                                if st.button("🔔 Prato", key=f"btn_sino_{mesa_idx}", use_container_width=True):
                                    st.session_state[f"silenciar_alarme_mesa_{str_m}"] = True
                                    st.session_state.mesa_selecionada_caixa = mesa_idx
                                    st.rerun()

                        # Círculo interativo da mesa
                        conteudo_circulo = f"""
                            <div class="mesa-circle {classe_css}">
                                <div style="font-size: 0.45rem; line-height: 1; text-align: center; white-space: nowrap;">{simbolo_topo}</div>
                                <span style="font-size: 0.65rem; font-weight: bold; line-height: 1.1;">Mesa {mesa_idx}</span>
                                <span style="font-size: 0.45rem; color: #bbb; line-height: 1;">{nome_cliente_curto}</span>
                                <span style="font-size: 0.45rem; color: #ffb703; line-height: 1;">{total_m:,.0f}K</span>
                            </div>
                        """
                        st.markdown(conteudo_circulo, unsafe_allow_html=True)
                        
                        # Botão para gerir a mesa (ao clicar aqui, seleciona a mesa, cessa o alarme e abre os detalhes)
                        if st.button(f"Gerir Mesa {mesa_idx}", key=f"btn_gerir_mesa_cx_{mesa_idx}", use_container_width=True):
                            st.session_state.mesa_selecionada_caixa = mesa_idx
                            st.session_state[f"silenciar_alarme_mesa_{str_m}"] = True
                            st.session_state[f"adicionando_pedido_cx_{mesa_idx}"] = False
                            st.rerun()
                        
                    mesa_idx += 1

        with col_esq:
            with st.container():
                m_sel = st.session_state.get("mesa_selecionada_caixa", 1)
                dados_m_sel = mesas_data[str(m_sel)]
                
                cli_atual = dados_m_sel.get("cliente")
                nome_cliente_titulo = cli_atual.get('nome') if cli_atual and isinstance(cli_atual, dict) and cli_atual.get('nome') else "Livre"
                
                # Cabeçalho da Mesa selecionada
                st.markdown(f"### ⚙️ Pedido da Mesa {m_sel} - {nome_cliente_titulo}", unsafe_allow_html=True)
                
                # --- BOTÃO PARA ADICIONAR PEDIDO PELO CAIXA ---
                if st.button("➕ Adicionar Pedido a esta Mesa", key=f"btn_toggle_add_pedido_{m_sel}", type="secondary", use_container_width=True):
                    st.session_state[f"adicionando_pedido_cx_{m_sel}"] = not st.session_state.get(f"adicionando_pedido_cx_{m_sel}", False)
                    st.rerun()

                # --- SEÇÃO DE ADIÇÃO DE PEDIDO COM AS CATEGORIAS DO CLIENTE ---
                if st.session_state.get(f"adicionando_pedido_cx_{m_sel}", False):
                    with st.container():
                        st.markdown(f"<div style='background: #161625; padding: 12px; border-radius: 8px; border: 1px solid #ffb703; margin-bottom: 15px;'>", unsafe_allow_html=True)
                        st.markdown("#### 🛒 Registar Novo Item para o Cliente")
                        
                        if cardapio_data:
                            categorias_disponiveis = ["Refeições", "Bebidas", "Sobremesas"]
                            categorias_validas = [cat for cat in categorias_disponiveis if cat in cardapio_data]
                            if not categorias_validas:
                                categorias_validas = list(cardapio_data.keys())

                            cat_escolhida = st.selectbox("Escolha a Categoria:", categorias_validas, key=f"cx_cat_{m_sel}")
                            
                            itens_da_cat = cardapio_data.get(cat_escolhida, {})
                            if itens_da_cat:
                                lista_itens_formatada = {f"{item_nome} — {item_info.get('preco', 0.0):,.2f} Kz": item_nome for item_nome, item_info in itens_da_cat.items()}
                                item_selecionado_label = st.selectbox("Escolha o Item:", list(lista_itens_formatada.keys()), key=f"cx_item_label_{m_sel}")
                                
                                nome_item_escolhido = lista_itens_formatada[item_selecionado_label]
                                dados_item = itens_da_cat[nome_item_escolhido]
                                preco_unitario = float(dados_item.get("preco", 0.0))
                                
                                qtd_adicionar = st.number_input("Quantidade:", min_value=1, value=1, step=1, key=f"cx_qtd_{m_sel}")
                                obs_item = st.text_input("Observações (ex: sem gelo, bem passado):", key=f"cx_obs_{m_sel}")
                                
                                if st.button("📥 Confirmar e Enviar Pedido", type="primary", key=f"cx_salvar_novo_ped_{m_sel}", use_container_width=True):
                                    novo_item_reg = {
                                        "item": nome_item_escolhido,
                                        "quantidade": int(qtd_adicionar),
                                        "preco": preco_unitario,
                                        "categoria": cat_escolhida,
                                        "observacao": obs_item,
                                        "status": "Pendente",
                                        "cozinha_status": "Pendente",
                                        "origem": f"Caixa ({sessao_op['operador']})"
                                    }
                                    
                                    if not dados_m_sel.get("cliente"):
                                        dados_m_sel["cliente"] = {"nome": "Cliente Balcão", "telefone": "N/A"}
                                        dados_m_sel["status"] = "Aberta"
                                    
                                    dados_m_sel["pedidos"].append(novo_item_reg)
                                    
                                    novo_total = sum(float(i.get('quantidade', 1)) * float(i.get('preco', 0.0)) for i in dados_m_sel["pedidos"] if i.get('status') not in ["Anulado", "Recusado pela Cozinha"])
                                    dados_m_sel["total"] = novo_total
                                    
                                    mesas_data[str(m_sel)] = dados_m_sel
                                    salvar_mesas_disco(mesas_data)
                                    
                                    st.session_state[f"adicionando_pedido_cx_{m_sel}"] = False
                                    st.success(f"Item '{nome_item_escolhido}' adicionado com sucesso à Mesa {m_sel}!")
                                    st.rerun()
                            else:
                                st.warning("Esta categoria não possui itens disponíveis no momento.")
                        else:
                            st.warning("O cardápio está vazio ou indisponível.")
                        
                        st.markdown("</div>", unsafe_allow_html=True)

                # --- LISTA DOS PEDIDOS ---
                st.markdown("#### 📋 Pedidos da Mesa")
                pedidos_mesa = dados_m_sel.get("pedidos", [])
                pedidos_ativos = [p for p in pedidos_mesa if p.get('status') not in ["Anulado", "Recusado pela Cozinha"]]
                
                if pedidos_ativos:
                    for idx_p, p in enumerate(pedidos_mesa):
                        if p.get('status') in ["Anulado", "Recusado pela Cozinha"]:
                            continue
                        q = p.get('quantidade', 1)
                        preco_u = p.get('preco', 0.0)
                        subtotal_item = q * preco_u
                        
                        col_it1, col_it2 = st.columns([2.2, 1])
                        with col_it1:
                            st.markdown(f"<div class='pedido-item-compacto'>- <b>{q}x {p.get('item')}</b> ({preco_u:,.2f} Kz) — <b>{subtotal_item:,.2f} Kz</b></div>", unsafe_allow_html=True)
                        with col_it2:
                            if st.button(f"🗑️ Anular", key=f"btn_anular_item_cx_{m_sel}_{idx_p}", use_container_width=True):
                                st.session_state[f"abrindo_anulacao_{m_sel}_{idx_p}"] = True
                        
                        if st.session_state.get(f"abrindo_anulacao_{m_sel}_{idx_p}", False):
                            with st.container():
                                st.markdown(f"<div style='background: #1e1e2f; padding: 10px; border-radius: 6px; border: 1px solid #ef4444; margin-bottom: 8px;'>", unsafe_allow_html=True)
                                motivo_anulacao = st.text_input(f"Motivo da anulação para: {p.get('item')}", key=f"motivo_anulacao_txt_{m_sel}_{idx_p}")
                                
                                col_j1, col_j2 = st.columns(2)
                                with col_j1:
                                    if st.button("Confirmar Anulação", type="primary", key=f"conf_anular_{m_sel}_{idx_p}", use_container_width=True):
                                        if motivo_anulacao.strip():
                                            p['status'] = "Anulado"
                                            p['motivo_anulacao'] = motivo_anulacao
                                            
                                            novo_total = sum(float(item.get('quantidade', 1)) * float(item.get('preco', 0.0)) for item in dados_m_sel["pedidos"] if item.get('status') not in ["Anulado", "Recusado pela Cozinha"])
                                            dados_m_sel["total"] = novo_total if novo_total > 0 else 0.0
                                            mesas_data[str(m_sel)] = dados_m_sel
                                            salvar_mesas_disco(mesas_data)
                                            
                                            vendas_excluidas = carregar_vendas_excluidas() if 'carregar_vendas_excluidas' in globals() else []
                                            reg_excluido = {
                                                "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                "Caixa": sessao_op['operador'],
                                                "Mesa": m_sel,
                                                "Item": p.get('item'),
                                                "Quantidade": q,
                                                "Valor": subtotal_item,
                                                "Motivo": motivo_anulacao,
                                                "Período": sessao_op['periodo']
                                            }
                                            vendas_excluidas.append(reg_excluido)
                                            salvar_vendas_excluidas(vendas_excluidas) if 'salvar_vendas_excluidas' in globals() else None
                                            
                                            st.session_state[f"abrindo_anulacao_{m_sel}_{idx_p}"] = False
                                            st.success("Item anulado e registado na auditoria do Administrador!")
                                            st.rerun()
                                        else:
                                            st.warning("Insira uma justificativa obrigatória.")
                                with col_j2:
                                    if st.button("Cancelar", key=f"fechar_anular_{m_sel}_{idx_p}", use_container_width=True):
                                        st.session_state[f"abrindo_anulacao_{m_sel}_{idx_p}"] = False
                                        st.rerun()
                                st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("Sem consumos ativos nesta mesa.")

                total_a_pagar = dados_m_sel.get("total", 0.0)
                st.markdown(f"### 💵 Total: **{total_a_pagar:,.2f} Kz**")
                
                if total_a_pagar > 0 or cli_atual:
                    st.markdown("---")
                    st.markdown("### 💳 Pagamento")
                    tipo_pagamento = st.selectbox("Forma:", ["Dinheiro", "TPA", "Misto"], key=f"pag_tipo_mesa_{m_sel}")
                    
                    v_dinheiro, v_tpa = 0.0, 0.0
                    if tipo_pagamento == "Dinheiro":
                        v_dinheiro = total_a_pagar
                    elif tipo_pagamento == "TPA":
                        v_tpa = total_a_pagar
                    else:
                        v_dinheiro = st.number_input("Dinheiro:", value=0.0, key=f"din_mesa_{m_sel}")
                        v_tpa = st.number_input("TPA:", value=max(0.0, total_a_pagar - v_dinheiro), key=f"tpa_mesa_{m_sel}")

                    if st.button("✅ Fechar Conta e Emitir Recibo", type="primary", use_container_width=True, key=f"btn_fechar_conta_mesa_{m_sel}"):
                        nome_c = cli_atual.get("nome", "Cliente Balcão") if isinstance(cli_atual, dict) else "Cliente Balcão"
                        tel_c = cli_atual.get("telefone", "N/A") if isinstance(cli_atual, dict) else "N/A"
                        
                        registo_venda = {
                            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Mesa": m_sel,
                            "Cliente": nome_c,
                            "Telefone": tel_c,
                            "Operador": sessao_op['operador'],
                            "Período": sessao_op['periodo'],
                            "Valor Dinheiro": v_dinheiro,
                            "Valor TPA": v_tpa,
                            "Total": total_a_pagar,
                            "pedidos": dados_m_sel.get("pedidos", [])
                        }
                        
                        hist_vendas.append(registo_venda)
                        salvar_historico_vendas(hist_vendas)
                        
                        # Limpa também a flag de silenciamento ao fechar a mesa
                        st.session_state[f"silenciar_alarme_mesa_{str(m_sel)}"] = False
                        
                        mesas_data[str(m_sel)] = {
                            "status": "Fechada", "cliente": None, "pedidos": [], "total": 0.0, "garcon": "", "solicitou_fecho": False
                        }
                        salvar_mesas_disco(mesas_data)
                        st.success(f"Conta da Mesa {m_sel} encerrada!")
                        st.rerun()
                                                                                   
# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
def area_administrador():
    st.markdown("<h1>👑 Painel do Administrador - NobreSabor</h1>", unsafe_allow_html=True)
    
    if "financas_autenticado" not in st.session_state:
        st.session_state.financas_autenticado = False

    if not st.session_state.financas_autenticado:
        with st.form("form_senha_financas"):
            st.markdown("### 🔒 Autenticação de Administrador")
            senha_digitada = st.text_input("Introduza a Senha de Administrador:", type="password")
            if st.form_submit_button("Desbloquear Painel"):
                if senha_digitada == "123123123":
                    st.session_state.financas_autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
        return

    col_btn_sair, col_links_rapidos = st.columns([1, 3])
    with col_btn_sair:
        if st.button("🔒 Bloquear Painel / Sair"):
            st.session_state.financas_autenticado = False
            st.rerun()
            
    with col_links_rapidos:
        st.markdown("<div style='text-align: right; color: #ffb703; font-size: 0.95rem; margin-bottom: 4px;'>🔗 Acessos Rápidos (Abrir noutra janela sem fechar o ADM):</div>", unsafe_allow_html=True)
        col_lnk1, col_lnk2 = st.columns(2)
        with col_lnk1:
            st.link_button("💻 Abrir Painel do Caixa", "?perfil=caixa", use_container_width=True)
        with col_lnk2:
            st.link_button("🍳 Abrir Painel da Cozinha", "?perfil=cozinha", use_container_width=True)
            
    st.success("Painel de Administração desbloqueado com sucesso.")
    st.markdown("---")

    vendas_exc_check = carregar_vendas_excluidas()
    tem_novas_exclusoes = len(vendas_exc_check) > 0
    
    nome_aba_excluidas = "🚨 Vendas Excluídas"
    if tem_novas_exclusoes:
        nome_aba_excluidas = "🚨 Vendas Excluídas (NOVO!)"

    tab_fin, tab_fechos_cx, tab_saidas, tab_stk, tab_dch, tab_exc = st.tabs([
        "💰 Finanças & Abertura do Dia", 
        "📋 Fechos de Período (Caixa)", 
        "💸 Saídas de Caixa", 
        "📦 Stock & Menu", 
        "👥 DCH (Colaboradores & Bónus)",
        nome_aba_excluidas
    ])
    
    with tab_fin:
        st.subheader("⚙️ Controlo Geral de Abertura e Fecho do Dia (Caixa e Cozinha)")
        
        if "financa_aba_autenticada" not in st.session_state:
            st.session_state.financa_aba_autenticada = False

        if not st.session_state.financa_aba_autenticada:
            with st.form("form_senha_aba_financa"):
                st.markdown("#### 🔒 Acesso Restrito à Aba Finanças")
                senha_fin = st.text_input("Introduza a senha de acesso às Finanças:", type="password")
                if st.form_submit_button("Desbloquear Finanças"):
                    if senha_fin == "123123123":
                        st.session_state.financa_aba_autenticada = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta!")
        else:
            if st.button("🔒 Bloquear Aba Finanças"):
                st.session_state.financa_aba_autenticada = False
                st.rerun()
                
            st.markdown("---")
            st.session_state.caixa_aberto = ler_estado_caixa_disco()
            
            col_adm_c1, col_adm_c2 = st.columns([1, 3])
            with col_adm_c1:
                if st.session_state.caixa_aberto:
                    if st.button("🔒 Fechar Dia do Restaurante", type="primary"):
                        gravar_estado_caixa_disco(False)
                        st.session_state.caixa_aberto = False
                        st.success("Dia fechado com sucesso! Caixa e Cozinha bloqueados.")
                        st.rerun()
                else:
                    if st.button("🟢 Abrir Dia do Restaurante", type="primary"):
                        gravar_estado_caixa_disco(True)
                        st.session_state.caixa_aberto = True
                        st.success("Dia aberto com sucesso! Caixa e Cozinha desbloqueados.")
                        st.rerun()
            with col_adm_c2:
                if st.session_state.caixa_aberto:
                    st.info("🟢 O Sistema encontra-se atualmente **ABERTO** (Caixa e Cozinha operacionais).")
                else:
                    st.warning("🔴 O Sistema encontra-se atualmente **FECHADO** pelo Administrador.")

            sessao_op_adm = carregar_sessao_operador()
            hist_vendas_adm = carregar_historico_vendas()
            
            hora_abertura_adm = sessao_op_adm.get("hora_abertura", "2000-01-01 00:00:00")
            vendas_turno_adm = [
                v for v in hist_vendas_adm 
                if v.get("Data", "") >= hora_abertura_adm and v.get("Operador", sessao_op_adm.get('operador')) == sessao_op_adm.get('operador')
            ]
            
            vendas_dinheiro_adm = sum(float(v.get('Valor Dinheiro', 0)) for v in vendas_turno_adm)
            fundo_inicial_adm = float(sessao_op_adm.get("saldo_inicial", 0.0))
            saldo_fisico_atual = fundo_inicial_adm + vendas_dinheiro_adm
            
            operador_atual_nome = sessao_op_adm.get("operador", "Nenhum") if sessao_op_adm.get("logado") else "Nenhum operador logado"
            periodo_atual_nome = sessao_op_adm.get("periodo", "N/A")

            st.markdown(f"""
                <div style="background-color: #141428; padding: 12px 16px; border-radius: 8px; border: 1px solid #ffb703; margin-top: 10px; margin-bottom: 15px;">
                    <span style="font-size: 1rem; color: #ffb703;">💵 <b>Saldo Disponível em Caixa:</b> <span style="color: #4ac26b;">{saldo_fisico_atual:,.2f} Kz</span></span><br>
                    <span style="font-size: 0.9rem; color: #d0d0e0;">👤 <b>Funcionário em Caixa:</b> {operador_atual_nome} (Período: {periodo_atual_nome}) | Fundo Inicial: {fundo_inicial_adm:,.2f} Kz | Vendas Dinheiro: {vendas_dinheiro_adm:,.2f} Kz</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("📊 Histórico Geral de Vendas")
            hist_vendas = carregar_historico_vendas()
            
            if not hist_vendas:
                st.info("Ainda não existem vendas faturadas registadas.")
            else:
                df_vendas = pd.DataFrame(hist_vendas)
                st.dataframe(df_vendas, use_container_width=True)
                total_geral_faturado = df_vendas['Valor Total'].sum() if 'Valor Total' in df_vendas.columns else 0
                st.markdown(f"### Faturação Total Acumulada: **{total_geral_faturado:,.2f} Kz**")

    with tab_fechos_cx:
        st.subheader("📋 Relatórios de Fecho de Período enviados pelos Operadores")
        fechos_registados = carregar_fechos_caixa()
        
        if not fechos_registados:
            st.info("Nenhum fecho de período registado pelos operadores de caixa ainda.")
        else:
            df_fechos = pd.DataFrame(fechos_registados)
            st.dataframe(df_fechos, use_container_width=True)
            total_fechos_acumulado = df_fechos['Total Fecho'].sum() if 'Total Fecho' in df_fechos.columns else 0
            st.markdown(f"### Total Registado em Fechos de Período: **{total_fechos_acumulado:,.2f} Kz**")

    with tab_saidas:
        st.subheader("💸 Gestão e Registo de Saídas de Caixa (Atribuição de Fundo / Troco)")
        st.write("Quando o ADM faz uma saída para o caixa, deve selecionar o utilizador recetor e o período correspondente.")
        
        with st.form("form_registar_saida"):
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                motivo_saida = st.text_input("Motivo da Saída (Ex: Fundo de Maneio, Trocos):")
                lista_utilizadores_padrao = ["Carlos", "Ana", "OperadorCaixa1", "OperadorCaixa2"]
                destino_utilizador = st.selectbox("Destinatário (Utilizador do Caixa):", lista_utilizadores_padrao)
            with col_sc2:
                valor_saida = st.number_input("Valor da Saída / Fundo (Kz):", min_value=0.0, value=20000.0, step=1000.0)
                periodo_destino = st.selectbox("Período Destino:", ["Noite", "Dia"])
            
            responsavel_saida = st.text_input("Autorizado por (ADM):", value="Administração")
            
            btn_salvar_saida = st.form_submit_button("🚀 Registar Saída e Enviar para o Caixa", use_container_width=True)
            if btn_salvar_saida and motivo_saida and valor_saida > 0:
                saidas_list = carregar_saidas_caixa()
                nova_saida = {
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Motivo": motivo_saida,
                    "Destino Utilizador": destino_utilizador,
                    "Período": periodo_destino,
                    "Valor": float(valor_saida),
                    "Responsável": responsavel_saida
                }
                saidas_list.append(nova_saida)
                salvar_saidas_caixa(saidas_list)
                st.success(f"Saída registada e enviada com sucesso para o utilizador {destino_utilizador} ({periodo_destino})!")
                st.rerun()

        st.divider()
        st.markdown("#### Histórico de Saídas de Caixa")
        saidas_registadas = carregar_saidas_caixa()
        if not saidas_registadas:
            st.info("Nenhuma saída de caixa registada.")
        else:
            df_saidas = pd.DataFrame(saidas_registadas)
            st.dataframe(df_saidas, use_container_width=True)
            total_saidas = df_saidas['Valor'].sum() if 'Valor' in df_saidas.columns else 0
            st.markdown(f"### Total Retirado em Saídas: **{total_saidas:,.2f} Kz**")

    with tab_stk:
        st.subheader("📦 Gestão de Stock e Produtos/Pratos")
        
        with st.form("form_add_produto"):
            st.markdown("#### Adicionar / Atualizar Item no Menu")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                novo_produto = st.text_input("Nome do Produto/Prato:")
                nova_categoria = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas", "Entradas", "Outros"])
            with col_s2:
                nova_qtd = st.number_input("Quantidade em Stock:", min_value=0, value=10)
                novo_preco = st.number_input("Preço Unitário (Kz):", min_value=0.0, value=500.0, step=100.0)
                
            btn_salvar_prod = st.form_submit_button("💾 Salvar / Atualizar Produto", use_container_width=True)
            if btn_salvar_prod and novo_produto:
                df_stk = st.session_state.stock
                if not df_stk.empty and novo_produto in df_stk['Produto'].values:
                    df_stk.loc[df_stk['Produto'] == novo_produto, ['Categoria', 'Quantidade', 'Preço Unitário']] = [nova_categoria, nova_qtd, novo_preco]
                    st.success(f"Produto '{novo_produto}' atualizado com sucesso!")
                else:
                    novo_df_linha = pd.DataFrame([[novo_produto, nova_categoria, nova_qtd, novo_preco]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                    st.session_state.stock = pd.concat([df_stk, novo_df_linha], ignore_index=True)
                    st.success(f"Produto '{novo_produto}' adicionado com sucesso!")
                
                salvar_stock_disco(st.session_state.stock)
                st.rerun()

        st.divider()
        st.markdown("#### Lista Atual de Produtos")
        st.dataframe(st.session_state.stock, use_container_width=True)
        
        if not st.session_state.stock.empty:
            with st.form("form_del_produto"):
                produto_a_remover = st.selectbox("Selecionar produto para remover:", st.session_state.stock['Produto'].tolist())
                btn_remover = st.form_submit_button("🗑️ Remover Produto Selecionado", use_container_width=True)
                if btn_remover:
                    st.session_state.stock = st.session_state.stock[st.session_state.stock['Produto'] != produto_a_remover].reset_index(drop=True)
                    salvar_stock_disco(st.session_state.stock)
                    st.success(f"Produto '{produto_a_remover}' removido!")
                    st.rerun()
        
    with tab_dch:
        st.subheader("👥 DCH — Cadastramento de Colaboradores & Bónus Acumulados")
        st.write("Faça o registo da equipa (Garçons) e consulte o acumulado de bónus por mesas atendidas (**500 Kz por mesa**).")
        
        with st.expander("➕ Cadastrar Novo Colaborador / Garçon", expanded=False):
            with st.form("form_cadastrar_colaborador"):
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    cod_func = st.text_input("Código do Funcionário (Ex: G003):")
                    nome_func = st.text_input("Nome Completo:")
                    cat_func = st.selectbox("Categoria / Cargo:", ["Garçon", "Chefe de Sala", "Bartender", "Outro"])
                with col_r2:
                    tel_func = st.text_input("Telefone:")
                    bi_func = st.text_input("Nº de BI:")
                
                btn_salvar_func = st.form_submit_button("💾 Salvar Colaborador", use_container_width=True)
                if btn_salvar_func and cod_func and nome_func:
                    df_rh = carregar_rh_disco()
                    if not df_rh.empty and (cod_func in df_rh['Código'].values):
                        df_rh.loc[df_rh['Código'] == cod_func, ['Nome', 'Categoria', 'Telefone', 'BI']] = [nome_func, cat_func, tel_func, bi_func]
                        st.success(f"Colaborador '{nome_func}' atualizado com sucesso!")
                    else:
                        nova_linha_rh = pd.DataFrame([[cod_func, nome_func, cat_func, tel_func, bi_func]], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                        df_rh = pd.concat([df_rh, nova_linha_rh], ignore_index=True)
                        st.success(f"Colaborador '{nome_func}' registado com sucesso!")
                    
                    salvar_rh_disco(df_rh)
                    st.rerun()

        st.markdown("#### 📋 Lista de Colaboradores Cadastrados")
        df_rh_atual = carregar_rh_disco()
        st.dataframe(df_rh_atual, use_container_width=True)

        if not df_rh_atual.empty:
            with st.form("form_remover_colaborador"):
                func_remover = st.selectbox("Selecionar colaborador para remover:", df_rh_atual['Nome'].tolist())
                btn_rem_func = st.form_submit_button("🗑️ Remover Colaborador Selecionado", use_container_width=True)
                if btn_rem_func:
                    df_rh_atual = df_rh_atual[df_rh_atual['Nome'] != func_remover].reset_index(drop=True)
                    salvar_rh_disco(df_rh_atual)
                    st.success(f"Colaborador '{func_remover}' removido com sucesso!")
                    st.rerun()

        st.markdown("---")
        st.subheader("🏆 Resumo de Bónus Acumulados por Atendimento de Mesas")
        atendimentos = carregar_atendimentos_garcon()
        if not atendimentos:
            st.info("Ainda não existem mesas atendidas registadas para calcular bónus.")
        else:
            df_atend = pd.DataFrame(atendimentos)
            
            df_resumo_bonus = df_atend.groupby("Garçon").agg(
                Mesas_Atendidas=("Mesa", "count"),
                Total_Vendido=("Valor Venda", "sum")
            ).reset_index()
            
            VALOR_POR_PONTO = 500.0
            df_resumo_bonus["Bónus Acumulado (Kz)"] = df_resumo_bonus["Mesas_Atendidas"] * VALOR_POR_PONTO
            
            st.dataframe(df_resumo_bonus, use_container_width=True)
            
            st.markdown("#### 📋 Histórico Detalhado de Atendimentos")
            st.dataframe(df_atend, use_container_width=True)

    with tab_exc:
        if tem_novas_exclusoes:
            st.markdown("<h3 class='piscar-alerta'>🚨 ALERTA: Existem Vendas/Itens Excluídos e Anulados pelos Operadores!</h3>", unsafe_allow_html=True)
        else:
            st.subheader("🚨 Registo de Vendas e Itens Excluídos / Anulados")

        vendas_excluidas_list = carregar_vendas_excluidas()
        if not vendas_excluidas_list:
            st.info("Nenhum item ou venda foi excluído ou anulado até ao momento.")
        else:
            df_exc = pd.DataFrame(vendas_excluidas_list)
            st.dataframe(df_exc, use_container_width=True)
            
            if st.button("🧹 Limpar / Marcar como Visto o Registo de Excluídos"):
                salvar_vendas_excluidas([])
                st.success("Registo limpo com sucesso!")
                st.rerun()

# ==========================================
# ROTEADOR PRINCIPAL DA APLICAÇÃO
# ==========================================
def main():
    if mesa_detectada is not None:
        area_cliente()
    elif perfil_url == "caixa":
        area_caixa_mesas()
    elif perfil_url == "cozinha":
        area_cozinha()
    else:
        area_administrador()

if __name__ == "__main__":
    main()
