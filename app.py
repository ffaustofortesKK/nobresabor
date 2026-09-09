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

# Estilos CSS Profissionais e Compactos
st.markdown("""
    <style>
    .stApp, body, html {
        background-color: #0c0c16 !important;
    }
    
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 90% !important;
        margin: 0 auto !important;
        background-color: #0c0c16 !important;
    }

    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        color: #e2e8f0 !important;
        font-weight: 400 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    input, select, option {
        color: #000000 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *, div[role="listbox"] * {
        color: #000000 !important;
        font-weight: 400 !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .mesa-circle {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        margin: 0 auto 1px auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        overflow: hidden;
        padding: 1px;
    }

    .mesa-aberta {
        border: 2px solid #2ea44f;
        background-color: #0f2316;
        color: #4ac26b !important;
    }

    .mesa-fechada {
        border: 2px solid #21262d;
        background-color: #161b22;
        color: #8b949e !important;
    }

    @keyframes oscilarVermelho {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        50% { transform: scale(1.02); box-shadow: 0 0 8px 3px rgba(239, 68, 68, 0.9); background-color: #ef4444 !important; color: #fff !important; }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    
    @keyframes oscilarVerde {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 194, 107, 0.7); }
        50% { transform: scale(1.02); box-shadow: 0 0 8px 3px rgba(74, 194, 107, 0.9); background-color: #4ac26b !important; color: #000 !important; }
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

    .piscar-alerta {
        animation: piscar-aviso 1s infinite;
        color: #ff4b4b !important;
    }

    @keyframes piscar-aviso {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    .stButton>button {
        border-radius: 6px;
        font-weight: 500 !important;
        padding: 3px 6px !important;
        font-size: 0.8rem !important;
        color: #000000 !important;
    }
    
    .stButton>button p, .stButton>button span {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    .element-container {
        margin-bottom: 0.3rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Caminhos dos Ficheiros de Base de Dados Local
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
ARQUIVO_BLOQUEIOS_OPERADORES = "bloqueios_operadores.json"

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
    return {"logado": False, "operador": "Nenhum", "periodo": "N/A", "turno_aberto": False, "saldo_inicial": 0.0, "hora_abertura": "", "trancado": False, "tentativas_falhadas": 0}

def salvar_sessao_operador(sessao_dict):
    try:
        with open(ARQUIVO_SESSAO_CAIXA_OPERADOR, "w", encoding="utf-8") as f:
            json.dump(sessao_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_bloqueios():
    if os.path.exists(ARQUIVO_BLOQUEIOS_OPERADORES):
        try:
            with open(ARQUIVO_BLOQUEIOS_OPERADORES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_bloqueios(bloq_list):
    try:
        with open(ARQUIVO_BLOQUEIOS_OPERADORES, "w", encoding="utf-8") as f:
            json.dump(bloq_list, f, ensure_ascii=False, indent=4)
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
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
        except:
            pass
    return []

def salvar_fechos_caixa(fechos_list):
    try:
        with open(ARQUIVO_FECHOS_CAIXA, "w", encoding="utf-8") as f:
            json.dump(fechos_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro: {e}")

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
            df_loaded = pd.read_json(ARQUIVO_RH_COLABORADORES, orient="split")
            if not df_loaded.empty:
                if "Salário" not in df_loaded.columns:
                    df_loaded["Salário"] = 0.0
                return df_loaded
        except:
            pass
    return pd.DataFrame([
        ["NS0001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042", 75000.0],
        ["NS0002", "Ana Paula", "Operador de Caixa", "912333444", "009876543LA031", 85000.0]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI", "Salário"])

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

def gerar_imagem_qrcode_pil(url_texto):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
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
# ÁREA: CLIENTE
# ==========================================
@st.fragment(run_every=4)
def area_cliente():
    st.markdown("""
        <style>
        .tablet-container { max-width: 320px; margin: 0 auto; background: #000000; border: 3px solid #1a1a1a; border-radius: 10px; padding: 6px; }
        .stButton button { padding: 0.2rem 0.4rem; font-size: 0.75rem; background-color: #111111; color: #ffffff; border: 1px solid #333333; }
        .element-container, .stTextInput, .stSelectbox { margin-bottom: -0.4rem !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tablet-container">', unsafe_allow_html=True)

    if not (mesa_detectada and 1 <= mesa_detectada <= 30):
        st.error("⚠️ Mesa inválida!")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    num_mesa = mesa_detectada
    mesas_data = carregar_mesas_disco()
    dados_m = mesas_data[str(num_mesa)]

    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<h4 style='text-align:center; font-size:0.85rem;'>🧾 Fatura Digital</h4>", unsafe_allow_html=True)
        for item in fat['itens']:
            st.markdown(f"<span style='font-size:0.65rem; color:#cccccc;'>- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.0f}Kz</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:0.75rem;'><b>Total Pago: {fat['total']:,.2f}Kz</b></span>", unsafe_allow_html=True)
        try:
            pdf_path = gerar_pdf_fatura(fat, num_mesa)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Descarregar PDF", data=f, file_name=f"Fatura_Mesa_{num_mesa}.pdf", use_container_width=True)
        except Exception:
            pass
        st.markdown('</div>', unsafe_allow_html=True)
        return

    if not dados_m.get("cliente"):
        with st.form(f"fc_{num_mesa}"):
            nome = st.text_input("Seu Nome:")
            tel = st.text_input("Telemóvel:")
            nif = st.text_input("NIF (Opcional):")
            whatsapp = st.checkbox("Entrar no Grupo WhatsApp?")
            if st.form_submit_button("Entrar", use_container_width=True) and nome and tel:
                dados_m["cliente"] = {"nome": nome, "telefone": tel, "nif": nif, "whatsapp": whatsapp}
                dados_m["status"] = "Aberta"
                salvar_mesas_disco(mesas_data)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        cli = dados_m["cliente"]
        st.markdown(f"<div style='font-size:0.7rem; color:#ffb703; margin-bottom:4px; text-align:center; background:#111111; padding:4px;'>Mesa {num_mesa} | <b>{cli['nome']}</b></div>", unsafe_allow_html=True)
        t_menu, t_cons, t_ev = st.tabs(["📋 Pedido", "📊 Conta", "🎉 Eventos"])
        
        with t_menu:
            stock_df = st.session_state.stock.copy() if 'stock' in st.session_state and not st.session_state.stock.empty else pd.DataFrame(columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
            utilitarios_extras = pd.DataFrame([
                {"Categoria": "Outros", "Produto": "Copo", "Preço Unitário": 0.0},
                {"Categoria": "Outros", "Produto": "Guardanapos", "Preço Unitário": 0.0},
                {"Categoria": "Outros", "Produto": "Talheres", "Preço Unitário": 0.0}
            ])
            stock_df = pd.concat([stock_df, utilitarios_extras], ignore_index=True)
            cats_disponiveis = stock_df['Categoria'].unique().tolist()
            cat = st.selectbox("Categoria:", cats_disponiveis, key="c_cat")
            itens = stock_df[stock_df['Categoria'] == cat]
            
            if not itens.empty:
                with st.form(f"fp_{num_mesa}", clear_on_submit=True):
                    prod = st.selectbox("Item:", itens['Produto'].tolist())
                    qtd = st.number_input("Quantidade:", 1, 99, 1)
                    obs_cliente = st.text_input("Observação:")
                    if st.form_submit_button("🚀 Enviar", use_container_width=True):
                        p_row = itens[itens['Produto'] == prod].iloc[0]
                        preco_unit = float(p_row['Preço Unitário']) if 'Preço Unitário' in p_row else 0.0
                        is_ref = cat.lower() in ["refeições", "refeicoes", "pratos", "comida"]
                        dados_m["pedidos"].append({
                            "item": prod, "tipo": cat, "quantidade": int(qtd), "preco": preco_unit,
                            "origem": f"Cliente ({cli['nome']})", "observacao": obs_cliente,
                            "status": "Confirmado" if not is_ref else "Pendente",
                            "cozinha_status": "N/A" if not is_ref else "Pendente", "hora": datetime.now().strftime("%H:%M")
                        })
                        dados_m["total"] = float(sum(p['quantidade']*p['preco'] for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"]))
                        salvar_mesas_disco(mesas_data)
                        st.success("Enviado!")
                        st.rerun()

        with t_cons:
            total_parcial = 0
            for p in dados_m["pedidos"]:
                t_item = p['quantidade'] * p['preco']
                if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                    total_parcial += t_item
                st.markdown(f"<span style='font-size:0.65rem; color:#cccccc;'>• {p['quantidade']}x {p['item']} ({t_item:,.0f}Kz)</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:0.7rem;'><b>Total: {total_parcial:,.2f}Kz</b></span>", unsafe_allow_html=True)
            if dados_m.get("solicitou_fecho"):
                st.info("⏳ Conta solicitada.")
            else:
                if st.button("🔔 Pedir Conta", type="primary", use_container_width=True):
                    dados_m["solicitou_fecho"] = True
                    salvar_mesas_disco(mesas_data)
                    st.rerun()

        with t_ev:
            st.markdown("<span style='font-size:0.65rem;'><b>Agenda:</b><br>• Sexta: Música ao Vivo<br>• Sábado: Karaoke</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ÁREA: COZINHA
# ==========================================
@st.fragment(run_every=4)
def area_cozinha():
    st.title("🍳 Área da Cozinha")
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa está FECHADO.**")
        return

    tab_pendentes, tab_historico_cozinha = st.tabs(["🔥 Pedidos Pendentes", "📋 Histórico"])

    with tab_pendentes:
        tem_pedidos = False
        tem_novos_pendentes = False
        for i in range(1, 31):
            str_i = str(i)
            dados_m = mesas_data.get(str_i, {})
            for idx_p, ped in enumerate(dados_m.get("pedidos", [])):
                cat_p = str(ped.get("tipo", "")).lower()
                c_status = ped.get("cozinha_status", "Pendente")
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped.get("status") != "Anulado" and c_status != "Entregue":
                    tem_pedidos = True
                    if c_status == "Pendente":
                        tem_novos_pendentes = True
                    
                    col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                    with col_c1:
                        st.write(f"**Mesa {i}** | {ped.get('item')} (Qtd: {ped.get('quantidade')})")
                        st.write(f"Obs: _{ped.get('observacao', 'Nenhuma')}_")
                    with col_c2:
                        st.markdown(f"Estado: <b>{c_status}</b>", unsafe_allow_html=True)
                    with col_c3:
                        if c_status == "Pendente":
                            if st.button("✅ Aprovar", key=f"aprov_cz_{i}_{idx_p}"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                                mesas_data[str_i]["pedidos"][idx_p]["status"] = "Confirmado"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif c_status == "Aprovado":
                            if st.button("🍲 Marcar Feito", key=f"feito_cz_{i}_{idx_p}"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                                mesas_data[str_i]["alarme_prato_feito"] = True
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif c_status == "Feito":
                            st.info("Pronto")
                            if st.button("🚚 Entregue", key=f"entregue_cz_{i}_{idx_p}"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Entregue"
                                mesas_data[str_i]["alarme_prato_feito"] = False
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                    st.divider()
        if not tem_pedidos:
            st.success("Sem refeições ativas!")

        if tem_novos_pendentes:
            st.markdown("""
                <audio autoplay loop>
                  <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)

    with tab_historico_cozinha:
        lista_pratos_feitos = []
        for i in range(1, 31):
            for ped in mesas_data.get(str(i), {}).get("pedidos", []):
                cat_p = str(ped.get("tipo", "")).lower()
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped.get("cozinha_status") in ["Feito", "Entregue"]:
                    lista_pratos_feitos.append({"Mesa": i, "Prato": ped.get('item'), "Qtd": ped.get('quantidade'), "Estado": ped.get('cozinha_status')})
        if lista_pratos_feitos:
            st.dataframe(pd.DataFrame(lista_pratos_feitos), use_container_width=True)
        else:
            st.info("Sem pratos finalizados.")

# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS
# ==========================================
@st.fragment(run_every=3)
def area_caixa_mesas():
    mesas_data = carregar_mesas_disco()

    # DETEÇÃO ROBUSTA DE PRATOS PRONTOS PARA O ALARME SONORO DO CAIXA
    tem_mesas_prontas_com_alerta = False
    for str_m, dados_m in mesas_data.items():
        tem_pronto = any(p.get("cozinha_status") == "Feito" for p in dados_m.get("pedidos", []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"])
        silenciado_pelo_operador = st.session_state.get(f"silenciar_alarme_mesa_{str_m}", False)
        if tem_pronto and not silenciado_pelo_operador:
            tem_mesas_prontas_com_alerta = True
            break

    if tem_mesas_prontas_com_alerta:
        st.markdown("""
            <audio autoplay loop>
              <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
            </audio>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-bottom:6px;'>💻 Controlo do Caixa - Operador</h3>", unsafe_allow_html=True)
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se FECHADO.**")
        return

    sessao_op = carregar_sessao_operador()
    bloqueios_lista = carregar_bloqueios()
    operador_atual_str = sessao_op.get("operador", "")
    esta_bloqueado = any(b.get("Operador") == operador_atual_str and not b.get("Resolvido", False) for b in bloqueios_lista)

    if esta_bloqueado:
        st.error(f"🚨 **CONTA BLOQUEADA!** Contacte a Administração.")
        if st.button("Sair", use_container_width=True):
            sessao_op["logado"] = False
            salvar_sessao_operador(sessao_op)
            st.rerun()
        return

    if sessao_op.get("trancado", False) and sessao_op["logado"]:
        with st.form("form_destrancar_caixa"):
            st.markdown(f"<h3>🔒 CAIXA TRANCADO ({sessao_op['operador']})</h3>", unsafe_allow_html=True)
            senha_destrancar = st.text_input("Senha:", type="password")
            if st.form_submit_button("🔓 Destrancar", use_container_width=True):
                if senha_destrancar == "123123":
                    sessao_op["trancado"] = False
                    sessao_op["tentativas_falhadas"] = 0
                    salvar_sessao_operador(sessao_op)
                    st.rerun()
                else:
                    sessao_op["tentativas_falhadas"] = sessao_op.get("tentativas_falhadas", 0) + 1
                    salvar_sessao_operador(sessao_op)
                    if sessao_op["tentativas_falhadas"] >= 5:
                        bloqueios_lista.append({
                            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Operador": sessao_op['operador'],
                            "Senha Antiga (Correta)": "123123",
                            "Senha Errada Inserida": senha_destrancar,
                            "Resolvido": False
                        })
                        salvar_bloqueios(bloqueios_lista)
                        st.error("Bloqueado por excesso de tentativas!")
                        st.rerun()
                    else:
                        st.error("Senha incorreta!")
        return

    if not sessao_op["logado"]:
        df_rh_login = carregar_rh_disco()
        lista_nomes_colab = df_rh_login['Nome'].tolist() if not df_rh_login.empty else ["Carlos", "Ana"]
        with st.form("form_login_caixa_operador"):
            st.markdown("### 🔐 Autenticação")
            utilizador_input = st.selectbox("Utilizador:", lista_nomes_colab)
            periodo_input = st.selectbox("Período:", ["Dia", "Noite"])
            senha_input = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar", use_container_width=True) and utilizador_input and senha_input:
                sessao_op.update({"logado": True, "operador": utilizador_input, "periodo": periodo_input, "turno_aberto": False, "saldo_inicial": 0.0, "trancado": False, "tentativas_falhadas": 0, "hora_abertura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                salvar_sessao_operador(sessao_op)
                st.rerun()
        return

    if not sessao_op["turno_aberto"]:
        saidas_todas = carregar_saidas_caixa()
        saldo_inicial_recebido = sum(float(s['Valor']) for s in saidas_todas if s.get("Destino Utilizador") == sessao_op['operador'] and s.get("Período") == sessao_op['periodo'])
        st.info(f"Fundo atribuído: {saldo_inicial_recebido:,.2f} Kz")
        col_op1, col_op2 = st.columns(2)
        with col_op1:
            if st.button("🟢 Abrir Turno", type="primary", use_container_width=True):
                sessao_op.update({"turno_aberto": True, "saldo_inicial": saldo_inicial_recebido})
                salvar_sessao_operador(sessao_op)
                st.rerun()
        with col_op2:
            if st.button("🚪 Sair", use_container_width=True):
                sessao_op["logado"] = False
                salvar_sessao_operador(sessao_op)
                st.rerun()
        return

    hist_vendas = carregar_historico_vendas()
    stock_df_cx_card = carregar_stock_disco()
    hora_abertura_turno = sessao_op.get("hora_abertura", "2000-01-01 00:00:00")
    vendas_turno = [v for v in hist_vendas if v.get("Data", "") >= hora_abertura_turno and v.get("Operador") == sessao_op['operador']]

    total_dinheiro_vendas = sum(float(v.get('Valor Dinheiro', 0)) for v in vendas_turno)
    total_tpa_vendas = sum(float(v.get('Valor TPA', 0)) for v in vendas_turno)
    saldo_em_caixa_fisico = float(sessao_op.get("saldo_inicial", 0.0)) + total_dinheiro_vendas

    col_cab1, col_cab2 = st.columns([2.5, 1.5])
    with col_cab1:
        st.markdown(f"Dinheiro: <b>{saldo_em_caixa_fisico:,.2f} Kz</b> | TPA: <b>{total_tpa_vendas:,.2f} Kz</b>", unsafe_allow_html=True)
    with col_cab2:
        col_op_txt, col_op_btn = st.columns([1.3, 1])
        with col_op_txt:
            st.markdown(f"<b>{sessao_op['operador']}</b>", unsafe_allow_html=True)
        with col_op_btn:
            if st.button("🔒 Trancar", use_container_width=True):
                sessao_op["trancado"] = True
                salvar_sessao_operador(sessao_op)
                st.rerun()

    aba_operador_1, aba_operador_2, aba_operador_3 = st.tabs(["🗺️ Mesas", "📚 Vendas", "🔒 Fecho"])

    with aba_operador_3:
        if st.button("🔒 Fechar Período", type="primary", use_container_width=True):
            fechos = carregar_fechos_caixa()
            total_geral_turno = sum(float(p['quantidade'])*float(p['preco']) for v in vendas_turno for p in v.get('pedidos', []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"])
            fechos.append({"Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Operador": sessao_op['operador'], "Período": sessao_op['periodo'], "Total Fecho": total_geral_turno})
            salvar_fechos_caixa(fechos)
            sessao_op.update({"logado": False, "turno_aberto": False})
            salvar_sessao_operador(sessao_op)
            st.rerun()

    with aba_operador_2:
        for v_item in reversed(hist_vendas):
            st.write(f"Mesa {v_item.get('Mesa')} — {v_item.get('Cliente')} | {v_item.get('Valor Total', 0):,.2f} Kz")

    with aba_operador_1:
        col_esq, col_dir = st.columns([1.1, 0.9])
        with col_dir:
            st.markdown("<h4 style='text-align: right;'>MESAS</h4>", unsafe_allow_html=True)
            mesa_idx = 1
            for r in range(8):
                cols = st.columns(4)
                for c in range(4):
                    if mesa_idx > 30:
                        break
                    str_m = str(mesa_idx)
                    dados_m = mesas_data[str_m]
                    tem_pronto = any(p.get("cozinha_status") == "Feito" for p in dados_m.get("pedidos", []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"])
                    solic = dados_m.get("solicitou_fecho", False)
                    
                    classe_css = "mesa-conta-solicitada" if solic else ("mesa-pronta-alerta" if tem_pronto and not st.session_state.get(f"silenciar_alarme_mesa_{str_m}", False) else ("mesa-aberta" if dados_m.get("status") == "Aberta" else "mesa-fechada"))
                    
                    with cols[c]:
                        st.markdown(f'<div class="mesa-circle {classe_css}"><span style="font-size:0.6rem;">M{mesa_idx}</span></div>', unsafe_allow_html=True)
                        if st.button(f"M{mesa_idx}", key=f"btn_m_{mesa_idx}", use_container_width=True):
                            st.session_state.mesa_selecionada_caixa = mesa_idx
                            st.session_state[f"silenciar_alarme_mesa_{str_m}"] = True
                            st.rerun()
                    mesa_idx += 1

        with col_esq:
            m_sel = st.session_state.get("mesa_selecionada_caixa", 1)
            dados_m_sel = mesas_data[str(m_sel)]
            st.markdown(f"#### Mesa {m_sel}", unsafe_allow_html=True)
            for idx_p, p in enumerate(dados_m_sel.get("pedidos", [])):
                if p.get('status') not in ["Anulado", "Recusado pela Cozinha"]:
                    st.write(f"- {p.get('quantidade')}x {p.get('item')} ({p.get('preco')*p.get('quantidade'):,.0f}Kz)")
            if st.button("✅ Fechar Conta da Mesa", type="primary", use_container_width=True):
                total_a_pagar = dados_m_sel.get("total", 0.0)
                if total_a_pagar > 0:
                    hist_vendas.append({"Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Mesa": m_sel, "Cliente": "Balcão", "Operador": sessao_op['operador'], "Valor Total": total_a_pagar, "pedidos": dados_m_sel.get("pedidos", [])})
                    salvar_historico_vendas(hist_vendas)
                    mesas_data[str(m_sel)] = {"status": "Fechada", "cliente": None, "pedidos": [], "total": 0.0, "solicitou_fecho": False}
                    salvar_mesas_disco(mesas_data)
                    st.rerun()

# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
@st.fragment(run_every=4)
def area_administrador():
    st.markdown("<h1>👑 Painel do Administrador</h1>", unsafe_allow_html=True)
    if "financas_autenticado" not in st.session_state:
        st.session_state.financas_autenticado = False

    if not st.session_state.financas_autenticado:
        with st.form("form_senha_financas"):
            senha = st.text_input("Senha Admin:", type="password")
            if st.form_submit_button("Entrar") and senha == "123123123":
                st.session_state.financas_autenticado = True
                st.rerun()
        return

    if st.button("Sair"):
        st.session_state.financas_autenticado = False
        st.rerun()

    tab_fin, tab_fechos_cx, tab_saidas, tab_stk, tab_dch, tab_exc, tab_qr, tab_bloq = st.tabs([
        "💰 Finanças", "📋 Fechos", "💸 Saídas", "📦 Stock", "👥 DCH", "🚨 Vendas Excluídas", "🖨️ QR Codes", "🔓 Desbloqueio"
    ])
    
    with tab_fin:
        st.session_state.caixa_aberto = ler_estado_caixa_disco()
        if st.session_state.caixa_aberto:
            if st.button("🔒 Fechar Dia"):
                gravar_estado_caixa_disco(False)
                st.rerun()
        else:
            if st.button("🟢 Abrir Dia"):
                gravar_estado_caixa_disco(True)
                st.rerun()

    with tab_qr:
        st.subheader("🖨️ QR Codes das Mesas (1 a 30)")
        url_site = st.text_input("URL base:", value="https://nobresabor.streamlit.app")
        st.markdown("---")
        for linha in range(10):
            cols = st.columns(3)
            for c in range(3):
                num_mesa_qr = linha * 3 + c + 1
                if num_mesa_qr > 30:
                    break
                link_mesa = f"{url_site}/?mesa={num_mesa_qr}"
                with cols[c]:
                    st.markdown(f"**Mesa {num_mesa_qr}**")
                    st.text_input(f"Link M{num_mesa_qr}:", value=link_mesa, key=f"link_txt_mesa_{num_mesa_qr}")
                    qr_bytes = gerar_imagem_qrcode_pil(link_mesa)
                    st.image(qr_bytes, width=130)
                    st.download_button(f"📥 Baixar M{num_mesa_qr}", data=qr_bytes, file_name=f"qrcode_mesa_{num_mesa_qr}.png", mime="image/png", key=f"dl_qr_{num_mesa_qr}")

    with tab_bloq:
        bloqueios_data = carregar_bloqueios()
        bloqueios_ativos = [b for b in bloqueios_data if not b.get("Resolvido", False)]
        if not bloqueios_ativos:
            st.info("Nenhum operador bloqueado.")
        else:
            for idx_b, b_item in enumerate(bloqueios_ativos):
                st.write(f"Operador Bloqueado: {b_item.get('Operador')}")
                if st.button(f"Desbloquear {b_item.get('Operador')}", key=f"btn_desbl_{idx_b}"):
                    b_item["Resolvido"] = True
                    salvar_bloqueios(bloqueios_data)
                    st.rerun()

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
