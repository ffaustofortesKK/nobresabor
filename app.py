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
        .stTabs [data-baseweb="tab"] { background-color: #000000; color: #aaaaaa; font-size: 0.75rem; }
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

    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<h4 style='text-align:center; font-size:0.9rem; color:#ffffff;'>🧾 Fatura Emitida</h4>", unsafe_allow_html=True)
        for item in fat['itens']:
            st.markdown(f"<span style='font-size:0.7rem; color:#cccccc;'>- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.0f}Kz</span>", unsafe_allow_html=True)
        st.markdown(f"<b style='font-size:0.8rem; color:#ffffff;'>Total: {fat['total']:,.2f}Kz</b>", unsafe_allow_html=True)
        try:
            pdf_path = gerar_pdf_fatura(fat, num_mesa)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 PDF", data=f, file_name=f"Fatura_{num_mesa}.pdf", use_container_width=True)
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if not dados_m.get("cliente"):
        st.markdown(f"<h4 style='text-align:center; font-size:0.9rem; color:#ffffff;'>🍽️ Mesa {num_mesa} - Registo</h4>", unsafe_allow_html=True)
        with st.form(f"fc_{num_mesa}"):
            nome = st.text_input("Nome:", placeholder="Seu nome")
            tel = st.text_input("Telemóvel:", placeholder="Contacto")
            nif = st.text_input("NIF (Opcional):", placeholder="NIF")
            whatsapp = st.checkbox("Entrar no Grupo WhatsApp?")
            if st.form_submit_button("Entrar", use_container_width=True) and nome and tel:
                dados_m["cliente"] = {"nome": nome, "telefone": tel, "nif": nif, "whatsapp": whatsapp}
                dados_m["status"] = "Aberta"
                salvar_mesas_disco(mesas_data)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        cli = dados_m["cliente"]
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.75rem; color:#ffb703; margin-bottom:6px; text-align:center; background:#111111; padding:5px; border-radius:6px;'>Mesa {num_mesa} | Cliente: <b>{cli['nome']}</b></div>", unsafe_allow_html=True)
        
        t_menu, t_cons, t_ev = st.tabs(["📋 Pedir", "📊 Consumo", "🎉 Eventos"])
        
        with t_menu:
            cat = st.selectbox("Cat:", st.session_state.stock['Categoria'].unique().tolist(), key="c_cat")
            itens = st.session_state.stock[st.session_state.stock['Categoria'] == cat]
            if not itens.empty:
                with st.form(f"fp_{num_mesa}", clear_on_submit=True):
                    prod = st.selectbox("Item:", itens['Produto'].tolist())
                    qtd = st.number_input("Qtd:", 1, 99, 1)
                    if st.form_submit_button("🚀 Enviar", use_container_width=True):
                        p_row = itens[itens['Produto'] == prod].iloc[0]
                        is_ref = cat.lower() in ["refeições", "refeicoes", "pratos", "comida"]
                        dados_m["pedidos"].append({
                            "item": prod, "tipo": cat, "quantidade": int(qtd),
                            "preco": float(p_row['Preço Unitário']), "origem": f"Cliente ({cli['nome']})",
                            "obs": "", "status": "Confirmado" if not is_ref else "Pendente",
                            "cozinha_status": "N/A" if not is_ref else "Pendente", "hora": datetime.now().strftime("%H:%M")
                        })
                        dados_m["total"] = float(sum(p['quantidade']*p['preco'] for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"]))
                        salvar_mesas_disco(mesas_data)
                        st.rerun()

        with t_cons:
            total_parcial = 0
            for p in dados_m["pedidos"]:
                t_item = p['quantidade'] * p['preco']
                if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                    total_parcial += t_item
                st.markdown(f"<span style='font-size:0.7rem; color:#cccccc;'>• {p['quantidade']}x {p['item']} ({t_item:,.0f}Kz) — <b>{p['status']}</b></span>", unsafe_allow_html=True)
            
            st.markdown(f"<b style='font-size:0.75rem; color:#ffffff;'>Parcial: {total_parcial:,.2f}Kz</b>", unsafe_allow_html=True)
            
            if dados_m.get("solicitou_fecho"):
                if st.button("Cancelar Fecho", key=f"cf_{num_mesa}"):
                    dados_m["solicitou_fecho"] = False
                    salvar_mesas_disco(mesas_data)
                    st.rerun()
            else:
                if st.button("🔔 Pedir Fecho", type="primary", use_container_width=True):
                    dados_m["solicitou_fecho"] = True
                    salvar_mesas_disco(mesas_data)
                    st.rerun()

        with t_ev:
            st.markdown("<span style='font-size:0.7rem; color:#cccccc;'>Sexta: Música ao Vivo<br>Sábado: Karaoke (Grupo FF)</span>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
# ==========================================
# ÁREA: COZINHA
# ==========================================
@st.fragment(run_every=6)
def area_cozinha():
    st.title("🍳 Área da Cozinha - Gestão de Refeições")
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO pela Administração.**")
        return

    tab_pendentes, tab_historico_cozinha = st.tabs(["🔥 Pedidos Pendentes e Ativos", "📋 Histórico de Pratos Preparados no Dia"])

    with tab_pendentes:
        st.subheader("Pedidos de Refeições vindos das Mesas / Caixa")
        tem_pedidos = False
        for i in range(1, 31):
            str_i = str(i)
            dados_m = mesas_data[str_i]
            for idx_p, ped in enumerate(dados_m["pedidos"]):
                cat_p = str(ped.get("tipo", "")).lower()
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito" and ped.get("cozinha_status") != "Entregue":
                    tem_pedidos = True
                    
                    col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                    with col_c1:
                        st.write(f"### 🍽️ Mesa {i}")
                        st.write(f"**Refeição:** {ped['item']} | **Qtd:** {ped['quantidade']}")
                        st.write(f"Obs: _{ped.get('obs', 'Nenhuma')}_ | Hora: `{ped.get('hora', 'N/A')}`")
                    with col_c2:
                        st.write(f"Estado: **{ped.get('cozinha_status', 'Pendente')}**")
                    with col_c3:
                        estado_atual = ped.get('cozinha_status', 'Pendente')
                        if estado_atual == "Pendente":
                            if st.button("✅ Aprovar", key=f"aprov_cz_{i}_{idx_p}"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                                mesas_data[str_i]["pedidos"][idx_p]["status"] = "Confirmado"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                            if st.button("❌ Recusar", key=f"rec_cz_{i}_{idx_p}"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Recusado"
                                mesas_data[str_i]["pedidos"][idx_p]["status"] = "Recusado pela Cozinha"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif estado_atual == "Aprovado":
                            if st.button("🍲 Marcar Feito", key=f"feito_cz_{i}_{idx_p}"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                    st.divider()
                    
        if not tem_pedidos:
            st.success("🎉 Sem refeições pendentes de momento!")

    with tab_historico_cozinha:
        st.subheader("📋 Registo de Pratos Preparados e Finalizados")
        
        lista_pratos_feitos = []
        for i in range(1, 31):
            str_i = str(i)
            dados_m = mesas_data[str_i]
            for ped in dados_m["pedidos"]:
                cat_p = str(ped.get("tipo", "")).lower()
                c_status = ped.get("cozinha_status", "")
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and c_status in ["Feito", "Entregue"]:
                    lista_pratos_feitos.append({
                        "Mesa": i,
                        "Prato / Refeição": ped['item'],
                        "Quantidade": ped['quantidade'],
                        "Observações": ped.get('obs', ''),
                        "Hora": ped.get('hora', ''),
                        "Estado na Cozinha": c_status
                    })
        
        if not lista_pratos_feitos:
            st.info("Ainda nenhum prato foi finalizado hoje.")
        else:
            df_feitos = pd.DataFrame(lista_pratos_feitos)
            st.dataframe(df_feitos, use_container_width=True)
            st.markdown(f"### Total de Pratos Preparados: **{sum(item['Quantidade'] for item in lista_pratos_feitos)} unidades**")

# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS (AUTOMÁTICO)
# ==========================================
@st.fragment(run_every=5)
def area_caixa_mesas():
    # Injeção de CSS para o formato circular e animações
    st.markdown("""
        <style>
        @keyframes oscilarVermelho {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            50% { transform: scale(1.06); box-shadow: 0 0 15px 8px rgba(239, 68, 68, 0.9); background-color: #ef4444 !important; color: #fff !important; }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        @keyframes oscilarVerde {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 194, 107, 0.7); }
            50% { transform: scale(1.06); box-shadow: 0 0 15px 8px rgba(74, 194, 107, 0.9); background-color: #4ac26b !important; color: #000 !important; }
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
            border: 2px solid #333355;
            border-radius: 50%;
            width: 95px;
            height: 95px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            margin: 0 auto 8px auto;
            color: #fff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .mesa-aberta { background-color: #1f3b2c; border: 2px solid #4ac26b; }
        .mesa-fechada { background-color: #141420; }
        </style>
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
    mesas_data = carregar_mesas_disco()
    hist_vendas = carregar_historico_vendas()

    hora_abertura_turno = sessao_op.get("hora_abertura", "2000-01-01 00:00:00")
    vendas_turno = [
        v for v in hist_vendas 
        if v.get("Data", "") >= hora_abertura_turno and v.get("Operador", sessao_op['operador']) == sessao_op['operador']
    ]

    total_dinheiro_vendas = sum(float(v.get('Valor Dinheiro', 0)) for v in vendas_turno)
    total_tpa_vendas = sum(float(v.get('Valor TPA', 0)) for v in vendas_turno)
    
    saldo_inicial_turno = float(sessao_op.get("saldo_inicial", 0.0))
    saldo_em_caixa_fisico = saldo_inicial_turno + total_dinheiro_vendas

    # Layout superior de saldos
    st.markdown(f"""
        <div style="background-color: #141428; padding: 14px 18px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #2a2a4a; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 0.95rem; color: #a0a0c0;">Saldo em Caixa (Dinheiro):</span> <b style="color: #4ac26b;">{saldo_em_caixa_fisico:,.2f} Kz</b> | 
                <span style="font-size: 0.95rem; color: #a0a0c0;">TPA:</span> <b style="color: #ffb703;">{total_tpa_vendas:,.2f} Kz</b>
            </div>
            <div>
                <span style="font-size: 0.9rem;">👤 Operador: <b>{sessao_op['operador']}</b> ({sessao_op['periodo']})</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ABAS DE NAVEGAÇÃO DO CAIXA (Atualizado para 3 abas)
    aba_operador_1, aba_operador_2, aba_operador_3 = st.tabs([
        "🗺️ Mesas & Operações", 
        "📚 Histórico de Vendas por Cliente", 
        "🔒 Fecho de Caixa / Resumo"
    ])

    # --- ABA 3 (ANTIGA 4): FECHO DE CAIXA / RESUMO ---
    with aba_operador_3:
        st.markdown("### 🔒 Auditoria e Fecho de Caixa do Período")
        st.info("Reveja abaixo todo o movimento do seu turno, itens vendidos, quantidades e valores acumulados. Quando estiver seguro, poderá efetuar o fecho do período.")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("Saldo Inicial (Fundo)", f"{saldo_inicial_turno:,.2f} Kz")
        with col_res2:
            st.metric("Vendas em Dinheiro", f"{total_dinheiro_vendas:,.2f} Kz")
        with col_res3:
            st.metric("Vendas em TPA", f"{total_tpa_vendas:,.2f} Kz")
            
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
            
            col_t1, col_t2, col_t3, col_t4 = st.columns([2, 1, 1, 1.2])
            with col_t1: st.markdown("**Produto / Item**")
            with col_t2: st.markdown("**Qtd Total**")
            with col_t3: st.markdown("**Preço Unit.**")
            with col_t4: st.markdown("**Subtotal**")
            st.divider()
            
            for prod, dados in itens_consolidados.items():
                col_i1, col_i2, col_i3, col_i4 = st.columns([2, 1, 1, 1.2])
                with col_i1: st.write(prod)
                with col_i2: st.write(str(dados["quantidade"]))
                with col_i3: st.write(f"{dados['preco']:,.2f} Kz")
                with col_i4: st.write(f"{dados['total']:,.2f} Kz")
            
            st.markdown("---")
            total_geral_turno = sum(d["total"] for d in itens_consolidados.values())
            
            st.markdown(f"### 💰 Faturação Total do Turno: **{total_geral_turno:,.2f} Kz**")
            st.markdown(f"### 💵 Valor de Caixa (Dinheiro em Gaveta): **{saldo_em_caixa_fisico:,.2f} Kz**")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔒 Fechar Período de Caixa com Segurança", type="primary", use_container_width=True):
                sessao_op["logado"] = False
                sessao_op["operador"] = "Nenhum"
                sessao_op["turno_aberto"] = False
                sessao_op["saldo_inicial"] = 0.0
                salvar_sessao_operador(sessao_op)
                st.success("Período de caixa encerrado com sucesso! Sessão terminada.")
                st.rerun()
        else:
            st.info("Ainda não existem vendas registadas neste turno.")

    # --- ABA 2: HISTÓRICO DE VENDAS ---
    with aba_operador_2:
        st.markdown("### 🔍 Histórico Detalhado de Vendas por Mesa / Cliente")
        if hist_vendas:
            pesquisa_cli = st.text_input("Filtrar por Nome do Cliente ou Telefone:", placeholder="Digite o nome ou telemóvel...", key="filtro_hist_cli_caixa")
            
            vendas_filtradas = hist_vendas
            if pesquisa_cli:
                vendas_filtradas = [
                    v for v in hist_vendas 
                    if pesquisa_cli.lower() in str(v.get("Cliente", "")).lower() or pesquisa_cli in str(v.get("Telefone", ""))
                ]
            
            for v_item in reversed(vendas_filtradas):
                cli_info = v_item.get("Cliente", "Desconhecido")
                tel_info = v_item.get("Telefone", "N/A")
                mesa_origem = v_item.get("Mesa", "?")
                total_v = v_item.get("Total", 0.0)
                data_v = v_item.get("Data", "")
                op_v = v_item.get("Operador", "")
                
                with st.expander(f"Mesa {mesa_origem} — Cliente: {cli_info} ({tel_info}) | Total: {total_v:,.2f} Kz | Data: {data_v}"):
                    st.write(f"**Operador responsável:** {op_v}")
                    st.write(f"**Forma de Pagamento:** Dinheiro: {v_item.get('Valor Dinheiro', 0):,.2f} Kz | TPA: {v_item.get('Valor TPA', 0):,.2f} Kz")
                    st.write("**Itens Consumidos:**")
                    for p in v_item.get("pedidos", []):
                        st.markdown(f"- {p.get('quantidade', 1)}x {p.get('item')} ({p.get('preco', 0):,.2f} Kz)")
        else:
            st.info("Ainda não existem registos no histórico de vendas.")

    # --- ABA 1: MESAS & OPERAÇÕES ---
    with aba_operador_1:
        col_esq, col_dir = st.columns([0.85, 1.15])

        with col_dir:
            st.markdown("#### 🗺️ Mesas")
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
                    
                    tem_pronto = any(
                        p.get("cozinha_status") == "Feito" 
                        for p in dados_m["pedidos"] 
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )

                    tem_bebida = any(
                        "bebida" in str(p.get("categoria", "")).lower() or 
                        any(palavra in str(p.get("item", "")).lower() for palavra in ["sumo", "cerveja", "refrigerante", "vinho", "agua", "cocktail", "whisky"])
                        for p in dados_m["pedidos"]
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )

                    tem_sobremesa = any(
                        "sobremesa" in str(p.get("categoria", "")).lower() or 
                        any(palavra in str(p.get("item", "")).lower() for palavra in ["gelado", "bolo", "pudim", "doce", "torta", "sobremesa"])
                        for p in dados_m["pedidos"]
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )
                    
                    simbolos_topo_lista = []
                    if solicitou_fecho:
                        classe_css = "mesa-conta-solicitada"
                        simbolos_topo_lista.append("💵")
                    elif tem_pronto:
                        classe_css = "mesa-pronta-alerta"
                        simbolos_topo_lista.append("🍲")
                    elif status_m == "Aberta" or cli_m:
                        classe_css = "mesa-aberta"
                    else:
                        classe_css = "mesa-fechada"

                    if tem_bebida:
                        simbolos_topo_lista.append("🍹")
                    if tem_sobremesa:
                        simbolos_topo_lista.append("🍰")

                    simbolo_topo = " ".join(simbolos_topo_lista)

                    with cols[c]:
                        nome_cliente_curto = cli_m['nome'].split()[0] if cli_m and isinstance(cli_m, dict) and cli_m.get('nome') else "Livre"
                        
                        st.markdown(f"""
                            <div class="mesa-circle {classe_css}">
                                <div style="font-size: 0.65rem; line-height: 1.1; min-height: 14px;">{simbolo_topo}</div>
                                <span style="font-size: 0.8rem; font-weight: bold;">Mesa {mesa_idx}</span>
                                <span style="font-size: 0.6rem; color: #ddd;">{nome_cliente_curto}</span>
                                <span style="font-size: 0.55rem; color: #ffb703;">{total_m:,.0f}Kz</span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"Gerir #{mesa_idx}", key=f"btn_gerir_mesa_cx_{mesa_idx}", use_container_width=True):
                            st.session_state.mesa_selecionada_caixa = mesa_idx
                            st.rerun()
                        
                    mesa_idx += 1

        with col_esq:
            with st.container():
                m_sel = st.session_state.get("mesa_selecionada_caixa", 1)
                dados_m_sel = mesas_data[str(m_sel)]
                
                cli_atual = dados_m_sel.get("cliente")
                nome_cliente_titulo = cli_atual.get('nome') if cli_atual and isinstance(cli_atual, dict) and cli_atual.get('nome') else "Livre"
                
                st.markdown(f"### ⚙️ Mesa {m_sel} — <span style='color: #ffb703;'>({nome_cliente_titulo})</span>", unsafe_allow_html=True)
                
                # --- EXIBIÇÃO DO QR CODE DA MESA ---
                with st.expander(f"📱 Ver QR Code da Mesa {m_sel}", expanded=False):
                    url_mesa = f"https://nobresabor.streamlit.app/?mesa={m_sel}"
                    st.markdown(f"**Link de acesso rápido para a Mesa {m_sel}:**")
                    st.code(url_mesa, language="text")
                    
                    import urllib.parse
                    url_encoded = urllib.parse.quote(url_mesa, safe="")
                    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={url_encoded}"
                    
                    col_qr1, col_qr2, col_qr3 = st.columns([1, 2, 1])
                    with col_qr2:
                        st.image(qr_image_url, caption=f"QR Code - Mesa {m_sel}", use_container_width=True)

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
                            st.markdown(f"- **{q}x {p.get('item')}** ({preco_u:,.2f} Kz) — **{subtotal_item:,.2f} Kz**")
                        with col_it2:
                            if st.button(f"🗑️ Anular Item", key=f"btn_anular_item_cx_{m_sel}_{idx_p}", use_container_width=True):
                                p['status'] = "Anulado"
                                
                                novo_total = sum(
                                    float(item.get('quantidade', 1)) * float(item.get('preco', 0.0)) 
                                    for item in dados_m_sel["pedidos"] 
                                    if item.get('status') not in ["Anulado", "Recusado pela Cozinha"]
                                )
                                dados_m_sel["total"] = novo_total
                                
                                if not any(item.get('status') not in ["Anulado", "Recusado pela Cozinha"] for item in dados_m_sel["pedidos"]):
                                    dados_m_sel["total"] = 0.0
                                
                                mesas_data[str(m_sel)] = dados_m_sel
                                salvar_mesas_disco(mesas_data)
                                st.success(f"Item '{p.get('item')}' anulado com sucesso!")
                                st.rerun()
                else:
                    st.info("Ainda não existem registos ativos nesta mesa.")

                total_a_pagar = dados_m_sel.get("total", 0.0)
                st.markdown(f"### 💵 Total Atual da Mesa: **{total_a_pagar:,.2f} Kz**")
                
                if total_a_pagar > 0 or cli_atual:
                    st.markdown("---")
                    st.markdown("### 💳 Processar Pagamento e Emitir Recibo")
                    tipo_pagamento = st.selectbox("Forma de Pagamento:", ["Dinheiro", "TPA", "Misto"], key=f"pag_tipo_mesa_{m_sel}")
                    
                    v_dinheiro = 0.0
                    v_tpa = 0.0
                    if tipo_pagamento == "Dinheiro":
                        v_dinheiro = total_a_pagar
                    elif tipo_pagamento == "TPA":
                        v_tpa = total_a_pagar
                    else:
                        v_dinheiro = st.number_input("Valor em Dinheiro:", value=0.0, key=f"din_mesa_{m_sel}")
                        v_tpa = st.number_input("Valor em TPA:", value=max(0.0, total_a_pagar - v_dinheiro), key=f"tpa_mesa_{m_sel}")

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
                        
                        mesas_data[str(m_sel)] = {
                            "status": "Fechada",
                            "cliente": None,
                            "pedidos": [],
                            "total": 0.0,
                            "garcon": "",
                            "solicitou_fecho": False
                        }
                        salvar_mesas_disco(mesas_data)
                        
                        st.success(f"Conta da Mesa {m_sel} encerrada com sucesso!")
                        st.rerun()
                else:
                    st.info(f"Mesa {m_sel} encontra-se totalmente livre e sem consumos pendentes.")
                                                                                          
        # ==========================================
        # BOTÃO ADICIONAR ITEM DIRETAMENTE PELO CAIXA
        # ==========================================
        with st.expander("➕ Adicionar Bebida / Comida / Sobremesa (Caixa)", expanded=False):
            stock_df_cx = st.session_state.stock
            if stock_df_cx.empty:
                st.warning("O stock está vazio. Adicione itens no painel do ADM.")
            else:
                cat_dispo_cx = stock_df_cx['Categoria'].unique().tolist()
                cat_sel_cx = st.selectbox("Categoria:", cat_dispo_cx, key=f"cat_cx_add_{m_sel}")
                
                itens_filtrados_cx = stock_df_cx[stock_df_cx['Categoria'] == cat_sel_cx]['Produto'].tolist()
                
                with st.form(key=f"form_adicionar_item_caixa_{m_sel}"):
                    prod_sel_cx = st.selectbox("Produto / Item:", itens_filtrados_cx)
                    qtd_cx = st.number_input("Quantidade:", min_value=1, value=1, step=1, key=f"qtd_cx_{m_sel}")
                    obs_cx = st.text_input("Observações:", key=f"obs_cx_{m_sel}")
                    
                    btn_add_cx = st.form_submit_button("🚀 Adicionar à Mesa", use_container_width=True)
                    if btn_add_cx:
                        row_p_cx = stock_df_cx[stock_df_cx['Produto'] == prod_sel_cx].iloc[0]
                        is_refeicao_cx = (cat_sel_cx.lower() in ["refeições", "refeicoes", "pratos", "comida"])
                        
                        novo_pedido_cx = {
                            "item": prod_sel_cx,
                            "tipo": cat_sel_cx,
                            "quantidade": int(qtd_cx),
                            "preco": float(row_p_cx['Preço Unitário']),
                            "origem": f"Caixa ({sessao_op['operador']})",
                            "obs": obs_cx,
                            "status": "Confirmado" if not is_refeicao_cx else "Pendente",
                            "cozinha_status": "N/A" if not is_refeicao_cx else "Pendente",
                            "hora": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        dados_m_sel["pedidos"].append(novo_pedido_cx)
                        dados_m_sel["status"] = "Aberta"
                        
                        total_atualizado_cx = sum(
                            p['quantidade'] * p['preco'] 
                            for p in dados_m_sel["pedidos"] 
                            if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                        )
                        dados_m_sel["total"] = float(total_atualizado_cx)
                        
                        salvar_mesas_disco(mesas_data)
                        st.success(f"Adicionado com sucesso: {qtd_cx}x {prod_sel_cx}!")
                        st.rerun()

        pedidos_sel = dados_m_sel["pedidos"]
        if not pedidos_sel:
            st.info("Esta mesa não tem pedidos efetuados.")
        else:
            subtotal_m_sel = 0
            for idx_p, p in enumerate(pedidos_sel):
                t_item = p['quantidade'] * p['preco']
                if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                    subtotal_m_sel += t_item
                
                st.write(f"- {p['quantidade']}x {p['item']} ({t_item:,.2f} Kz) [{p['status']}]")
                
                # Opção de Anular com Justificação Obrigatória
                if p['status'] != "Anulado":
                    with st.expander(f"🗑️ Anular Item: {p['item']} (Mesa {m_sel})"):
                        justificacao_anulacao = st.text_input(f"Motivo da devolução/anulação:", key=f"just_anul_{m_sel}_{idx_p}")
                        if st.button(f"Confirmar Anulação do Item", key=f"btn_conf_anul_{m_sel}_{idx_p}"):
                            if justificacao_anulacao.strip():
                                # Marca como anulado na mesa (corrigido o fecho de parênteses)
                                mesas_data[str(m_sel)]['pedidos'][idx_p]['status'] = "Anulado"
                                total_novo = sum(x['quantidade']*x['preco'] for x in mesas_data[str(m_sel)]['pedidos'] if x['status'] not in ["Anulado", "Recusado pela Cozinha"])
                                mesas_data[str(m_sel)]['total'] = float(total_novo)
                                salvar_mesas_disco(mesas_data)
                                
                                # Regista em Vendas Excluídas para o ADM
                                vendas_exc = carregar_vendas_excluidas()
                                vendas_exc.append({
                                    "Data/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "Mesa": m_sel,
                                    "Produto": p['item'],
                                    "Quantidade": p['quantidade'],
                                    "Preço Unitário": p['preco'],
                                    "Preço Total": t_item,
                                    "Utilizador": sessao_op['operador'],
                                    "Observação": justificacao_anulacao
                                })
                                salvar_vendas_excluidas(vendas_exc)
                                
                                st.success("Item anulado e justificação enviada para o ADM!")
                                st.rerun()
                            else:
                                st.warning("Por favor, preencha o motivo/justificação da anulação.")

            st.markdown(f"#### Total Atual da Mesa: **{subtotal_m_sel:,.2f} Kz**")
            
            with st.form(f"form_pagamento_mesa_{m_sel}"):
                st.markdown("#### 💳 Processar Pagamento e Emitir Recibo")
                tipo_pagamento = st.selectbox("Forma de Pagamento:", ["Dinheiro", "TPA", "Misto (Dinheiro + TPA)"])
                
                val_dinheiro = 0.0
                val_tpa = 0.0
                if tipo_pagamento == "Dinheiro":
                    val_dinheiro = subtotal_m_sel
                elif tipo_pagamento == "TPA":
                    val_tpa = subtotal_m_sel
                else:
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        val_dinheiro = st.number_input("Dinheiro (Kz):", min_value=0.0, value=0.0)
                    with col_m2:
                        val_tpa = st.number_input("TPA (Kz):", min_value=0.0, value=0.0)

                btn_concluir_pagamento = st.form_submit_button("✅ Concluir Pagamento & Libertar Mesa", use_container_width=True)
                if btn_concluir_pagamento and subtotal_m_sel > 0:
                    itens_validos_fatura = [
                        {
                            "item": p['item'],
                            "quantidade": p['quantidade'],
                            "preco": p['preco']
                        }
                        for p in pedidos_sel if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    ]
                    
                    fatura_dados = {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": cli_info['nome'] if cli_info else "Consumidor Final",
                        "telefone": cli_info.get('telefone', 'N/A') if cli_info else "N/A",
                        "nif": cli_info.get('nif', '') if cli_info else "",
                        "itens": itens_validos_fatura,
                        "total": subtotal_m_sel,
                        "pagamento_detalhe": tipo_pagamento,
                        "Valor Dinheiro": val_dinheiro,
                        "Valor TPA": val_tpa
                    }
                    
                    hist = carregar_historico_vendas()
                    hist.append({
                        "Data": fatura_dados["data"],
                        "Operador": sessao_op['operador'],
                        "Mesa": m_sel,
                        "Garçon": dados_m_sel.get("garcon", "Não atribuído"),
                        "Cliente": fatura_dados["cliente"],
                        "Valor Total": subtotal_m_sel,
                        "Pagamento": tipo_pagamento,
                        "Valor Dinheiro": val_dinheiro,
                        "Valor TPA": val_tpa,
                        "itens": itens_validos_fatura
                    })
                    salvar_historico_vendas(hist)
                    
                    atend_list = carregar_atendimentos_garcon()
                    atend_list.append({
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Garçon": dados_m_sel.get("garcon", "Não atribuído"),
                        "Mesa": m_sel,
                        "Valor Venda": subtotal_m_sel
                    })
                    salvar_atendimentos_garcon(atend_list)
                    
                    # Guarda a fatura emitida na mesa para que o cliente veja a mensagem de agradecimento e a fatura final,
                    # e limpa os pedidos, total e dados do cliente para resetar a mesa.
                    mesas_data[str(m_sel)]["fatura_emitida"] = fatura_dados
                    mesas_data[str(m_sel)]["pedidos"] = []
                    mesas_data[str(m_sel)]["total"] = 0.0
                    mesas_data[str(m_sel)]["status"] = "Fechada"
                    mesas_data[str(m_sel)]["cliente"] = None
                    mesas_data[str(m_sel)]["garcon"] = "Não atribuído"
                    salvar_mesas_disco(mesas_data)
                    
                    st.success("Pagamento efetuado com sucesso e perfil de cliente encerrado com mensagem de agradecimento!")
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
