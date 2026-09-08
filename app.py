import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
import os
import json

# Configuração da Página
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

ARQUIVO_ESTADO_CAIXA = "caixa_status.txt"
ARQUIVO_DADOS_MESAS = "mesas_dados.json"
ARQUIVO_HISTORICO_VENDAS = "historico_vendas.json"
ARQUIVO_SAIDAS_CAIXA = "saidas_caixa.json"

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

def carregar_mesas_disco():
    if os.path.exists(ARQUIVO_DADOS_MESAS):
        try:
            with open(ARQUIVO_DADOS_MESAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {str(i): {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "fatura_emitida": None} for i in range(1, 31)}

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
                return json.load(f)
        except:
            pass
    return []

def salvar_historico_vendas(hist_list):
    try:
        with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
            json.dump(hist_list, f, ensure_ascii=False, indent=4)
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

# Estilos CSS: Visual Compacto Estilo Tablet, Margens Reduzidas e Textos em BRANCO e NEGRITO
st.markdown("""
    <style>
    .stApp {
        background-color: #0c0c16;
        max-width: 960px;
        margin: 0 auto;
    }
    
    html, body, [class*="css"], .stMarkdown, p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    /* Redução drástica de margens e preenchimentos verticais */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    h1 {
        font-size: 1.6rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    h2 {
        font-size: 1.3rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    @keyframes borda-vermelha-piscar {
        0% { border: 2px solid #ff4b4b; box-shadow: 0 0 8px #ff4b4b; background-color: #1a0f0f; }
        50% { border: 2px solid #ffa0a0; box-shadow: none; background-color: #12121c; }
        100% { border: 2px solid #ff4b4b; box-shadow: 0 0 8px #ff4b4b; background-color: #1a0f0f; }
    }
    @keyframes flutuar-emoji {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
        100% { transform: translateY(0px); }
    }
    .emoji-refeicao-topo {
        font-size: 1.2em;
        text-align: center;
        margin-bottom: -6px;
        z-index: 10;
        position: relative;
        animation: flutuar-emoji 1.2s infinite ease-in-out;
    }
    .mesa-pronta-alerta {
        padding: 6px;
        border-radius: 8px;
        text-align: center;
        animation: borda-vermelha-piscar 1s infinite;
        color: #ff6b6b !important;
        font-size: 0.8em;
    }
    .mesa-aberta {
        padding: 6px;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #2ea44f;
        background-color: #0f2316;
        color: #4ac26b !important;
        font-size: 0.8em;
    }
    .mesa-fechada {
        padding: 6px;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #30363d;
        background-color: #161b22;
        color: #ffffff !important;
        font-size: 0.8em;
    }
    .bloco-seccao {
        padding: 12px 15px;
        border-radius: 10px;
        background-color: #141428;
        border: 1px solid #2a2a4a;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .fatura-box {
        background-color: #141428;
        border: 2px dashed #ffb703;
        padding: 15px;
        border-radius: 10px;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: bold !important;
        padding: 0.35rem 0.75rem !important;
        min-height: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Captura de Parâmetros da URL
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
    st.session_state.stock = pd.DataFrame([
        ["Água 0.5L", "Bebidas", 50, 300.0],
        ["Refrigerante Cola", "Bebidas", 40, 450.0],
        ["Cerveja Cuca", "Bebidas", 60, 500.0],
        ["Vinho Tinto", "Bebidas", 15, 4500.0],
        ["Frango à Grega", "Refeições", 20, 3500.0],
        ["Bife a Cavalo", "Refeições", 15, 4000.0],
        ["Pudim de Leite", "Sobremesas", 25, 1500.0],
        ["Salada de Frutas", "Sobremesas", 30, 1200.0]
    ], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

if "rh" not in st.session_state:
    st.session_state.rh = pd.DataFrame([
        ["G001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042"],
        ["G002", "Ana Paula", "Garçon", "912333444", "009876543LA031"]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])

URL_OFICIAL = "https://nobresabor.streamlit.app"

def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# ==========================================
# ÁREA: CLIENTE
# ==========================================
def area_cliente():
    if mesa_detectada and 1 <= mesa_detectada <= 30:
        num_mesa = mesa_detectada
    else:
        st.error("⚠️ Nenhum número de mesa detetado no link!")
        return

    mesas_data = carregar_mesas_disco()
    str_mesa = str(num_mesa)
    dados_m = mesas_data[str_mesa]

    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<div class='fatura-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🧾 Fatura / Recibo</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><b>Mesa:</b> {num_mesa} | <b>Data:</b> {fat['data']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><b>Cliente:</b> {fat['cliente']} | <b>Tel:</b> {fat['telefone']}</p>", unsafe_allow_html=True)
        st.divider()
        
        for item in fat['itens']:
            st.write(f"- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.2f} Kz")
        
        st.markdown(f"### Total Pago: **{fat['total']:,.2f} Kz**")
        st.markdown(f"<p><b>Pagamento:</b> {fat['pagamento_detalhe']}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<h3 style='text-align: center;'>🙏 Obrigado pela preferência!</h3>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not dados_m.get("cliente"):
        st.markdown("<h1 style='text-align: center;'>🍽️ Nobre Sabor</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>Registo de Entrada - Mesa {num_mesa}</h3>", unsafe_allow_html=True)
        st.divider()
        
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            with st.form(f"form_cli_{num_mesa}"):
                nome_cli = st.text_input("Nome:")
                tel_cli = st.text_input("Telefone:")
                whatsapp_opt = st.checkbox("Entrar no Grupo de WhatsApp?")
                
                btn_reg = st.form_submit_button("Entrar e Ver Menu", use_container_width=True)
                if btn_reg and nome_cli and tel_cli:
                    dados_m["cliente"] = {"nome": nome_cli, "telefone": tel_cli, "whatsapp": whatsapp_opt}
                    dados_m["status"] = "Aberta"
                    salvar_mesas_disco(mesas_data)
                    st.success("Registo efetuado!")
                    st.rerun()
                elif btn_reg:
                    st.warning("Preencha nome e telefone.")
    else:
        cli = dados_m["cliente"]
        st.title(f"📱 Mesa {num_mesa} - {cli['nome']}")
        
        categorias_disponiveis = st.session_state.stock['Categoria'].unique().tolist()
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Pedidos", "📊 Consumo", "🎉 Eventos"])
        
        with tab_menu:
            cat_escolhida = st.selectbox("Categoria:", categorias_disponiveis, key="cat_cli_sel")
            stock_df = st.session_state.stock
            itens_cat = stock_df[stock_df['Categoria'] == cat_escolhida]
            
            if not itens_cat.empty:
                with st.form(key=f"form_pedido_{num_mesa}", clear_on_submit=True):
                    item_escolhido = st.selectbox("Item:", itens_cat['Produto'].tolist())
                    qtd = st.number_input("Qtd:", min_value=1, value=1)
                    obs = st.text_input("Obs:")
                    
                    if st.form_submit_button("🚀 Enviar Pedido", use_container_width=True):
                        row_prod = itens_cat[itens_cat['Produto'] == item_escolhido].iloc[0]
                        is_refeicao = (cat_escolhida.lower() in ["refeições", "refeicoes", "pratos", "comida"])
                        novo_pedido = {
                            "item": item_escolhido,
                            "tipo": cat_escolhida,
                            "quantidade": int(qtd),
                            "preco": float(row_prod['Preço Unitário']),
                            "origem": f"Cliente ({cli['nome']})",
                            "obs": obs,
                            "status": "Confirmado" if not is_refeicao else "Pendente",
                            "cozinha_status": "N/A" if not is_refeicao else "Pendente",
                            "hora": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        dados_m["pedidos"].append(novo_pedido)
                        dados_m["status"] = "Aberta"
                        dados_m["total"] = float(sum(p['quantidade'] * p['preco'] for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"]))
                        salvar_mesas_disco(mesas_data)
                        
                        st.session_state[f"aviso_{num_mesa}"] = f"✅ Pedido de {qtd}x {item_escolhido} enviado!"
                        st.rerun()

            if f"aviso_{num_mesa}" in st.session_state:
                st.success(st.session_state[f"aviso_{num_mesa}"])
                del st.session_state[f"aviso_{num_mesa}"]
                
        with tab_consumo:
            for p in dados_m["pedidos"]:
                total_item = p['quantidade'] * p['preco']
                st.write(f"- {p['quantidade']}x {p['item']} | {total_item:,.2f} Kz")
            st.markdown(f"### Total: {dados_m['total']:,.2f} Kz")
                
        with tab_eventos:
            st.write("- Sexta: Música ao Vivo\n- Sábado: Karaoke")


# ==========================================
# ÁREA: COZINHA
# ==========================================
@st.fragment(run_every=6)
def area_cozinha():
    st.title("🍳 Cozinha - Refeições")
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ O Caixa está FECHADO.")
        return

    tem_pedidos = False
    for i in range(1, 31):
        str_i = str(i)
        dados_m = mesas_data[str_i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            cat_p = str(ped.get("tipo", "")).lower()
            if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
                tem_pedidos = True
                
                col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
                with col_c1:
                    st.write(f"**Mesa {i}:** {ped['item']} ({ped['quantidade']}x)")
                with col_c2:
                    st.write(f"[{ped.get('cozinha_status', 'Pendente')}]")
                with col_c3:
                    estado_atual = ped.get('cozinha_status', 'Pendente')
                    if estado_atual == "Pendente":
                        if st.button("✅", key=f"aprov_cz_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                            mesas_data[str_i]["pedidos"][idx_p]["status"] = "Confirmado"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
                    elif estado_atual == "Aprovado":
                        if st.button("🍲 Feito", key=f"feito_cz_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
                st.divider()
                
    if not tem_pedidos:
        st.success("🎉 Sem refeições pendentes!")


# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
def area_administrador():
    col_adm_title, col_adm_info = st.columns([3, 2])
    with col_adm_title:
        st.markdown("<h1>👑 Painel Administrativo</h1>", unsafe_allow_html=True)
    with col_adm_info:
        st.markdown(
            f"""<div style="text-align: right; padding-top: 5px;">
                <span style="background-color: #1a1a38; border: 1px solid #2a2a5a; padding: 4px 10px; border-radius: 12px; font-size: 0.75em;">
                    🟢 Online &nbsp;|&nbsp; 📅 {datetime.now().strftime("%d/%m/%Y")} &nbsp;|&nbsp; 🕒 {datetime.now().strftime("%H:%M")}
                </span>
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("<hr style='margin-top: 5px; margin-bottom: 10px; border-color: #2a2a4a;'>", unsafe_allow_html=True)
    
    with st.expander("🔗 Links do Sistema", expanded=False):
        st.text_input("Caixa:", f"{URL_OFICIAL}/?perfil=caixa")
        st.text_input("Cozinha:", f"{URL_OFICIAL}/?perfil=cozinha")
        
    tab_fin, tab_stk, tab_dch = st.tabs(["💰 Finanças", "📦 Stock", "👥 DCH"])
    
    with tab_fin:
        if "financas_autenticado" not in st.session_state:
            st.session_state.financas_autenticado = False

        if not st.session_state.financas_autenticado:
            st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
            st.subheader("🔒 Acesso Restrito - Finanças")
            with st.form("form_senha_financas"):
                senha_digitada = st.text_input("Senha:", type="password")
                if st.form_submit_button("Desbloquear", use_container_width=True):
                    if senha_digitada == "123123123":
                        st.session_state.financas_autenticado = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta!")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            if st.button("🔒 Bloquear Finanças", key="btn_bloquear_fin"):
                st.session_state.financas_autenticado = False
                st.rerun()

            hist_vendas = carregar_historico_vendas()
            t_dinheiro_v = sum(float(v.get('Valor Dinheiro', 0)) for v in hist_vendas)
            t_tpa_v = sum(float(v.get('Valor TPA', 0)) for v in hist_vendas)
            t_geral_v = t_dinheiro_v + t_tpa_v
            saidas_list = carregar_saidas_caixa()

            st.markdown(f"<div class='bloco-seccao'><b>Total:</b> {t_geral_v:,.2f} Kz | 💵 {t_dinheiro_v:,.2f} Kz | 💳 {t_tpa_v:,.2f} Kz</div>", unsafe_allow_html=True)

            st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
            col_cx_st, col_cx_bt = st.columns([2, 1])
            with col_cx_st:
                st.write(f"Estado do Caixa: **{'ABERTO' if st.session_state.caixa_aberto else 'FECHADO'}**")
            with col_cx_bt:
                if st.session_state.caixa_aberto:
                    if st.button("Fechar Caixa", key="btn_f_cx"):
                        st.session_state.caixa_aberto = False
                        gravar_estado_caixa_disco(False)
                        st.rerun()
                else:
                    if st.button("Abrir Caixa", key="btn_a_cx"):
                        st.session_state.caixa_aberto = True
                        gravar_estado_caixa_disco(True)
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
            st.subheader("📤 Saída de Caixa")
            with st.form("form_reg_saida"):
                desc_s = st.text_input("Motivo:")
                val_s = st.number_input("Valor (Kz):", min_value=0.0)
                resp_s = st.selectbox("Responsável:", st.session_state.rh['Nome'].tolist() if not st.session_state.rh.empty else ["Admin"])
                if st.form_submit_button("Registar Saída", use_container_width=True):
                    if desc_s and val_s > 0:
                        saidas_list.append({"Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Descrição": desc_s, "Valor": val_s, "Responsável": resp_s})
                        salvar_saidas_caixa(saidas_list)
                        st.success("Registado!")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_stk:
        sub_t_reg, sub_t_ger, sub_t_ed = st.tabs(["➕ Registar", "📦 Stock", "🛠️ Gerir"])
        
        with sub_t_reg:
            st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
            with st.form("form_prod_novo"):
                np = st.text_input("Produto:")
                cat = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas", "Entradas"])
                qtd = st.number_input("Qtd:", min_value=0, value=10)
                prc = st.number_input("Preço:", min_value=0.0, value=1000.0)
                if st.form_submit_button("Salvar", use_container_width=True):
                    if np:
                        novo_reg = pd.DataFrame([[np, cat, int(qtd), float(prc)]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                        st.session_state.stock = pd.concat([st.session_state.stock, novo_reg], ignore_index=True)
                        st.success("Adicionado!")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with sub_t_ger:
            st.dataframe(st.session_state.stock, use_container_width=True)

        with sub_t_ed:
            st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
            if not st.session_state.stock.empty:
                prod_sel = st.selectbox("Produto:", st.session_state.stock['Produto'].tolist())
                idx = st.session_state.stock[st.session_state.stock['Produto'] == prod_sel].index[0]
                if st.button("🗑️ Remover", use_container_width=True):
                    st.session_state.stock = st.session_state.stock.drop(idx).reset_index(drop=True)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_dch:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("👥 Recursos Humanos")
        with st.form("form_rh"):
            nome_col = st.text_input("Nome:")
            cat_f = st.selectbox("Cargo:", ["Garçon", "Cozinheiro", "Caixa"])
            tel_c = st.text_input("Telefone:")
            bi_c = st.text_input("BI:")
            if st.form_submit_button("Registar", use_container_width=True):
                if nome_col:
                    cod = f"G{len(st.session_state.rh)+1:03d}"
                    novo_rh = pd.DataFrame([[cod, nome_col, cat_f, tel_c, bi_c]], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                    st.session_state.rh = pd.concat([st.session_state.rh, novo_rh], ignore_index=True)
                    st.rerun()
        st.dataframe(st.session_state.rh, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS
# ==========================================
@st.fragment(run_every=6)
def area_caixa_mesas():
    st.title("💻 Controlo de Mesas e Caixa")
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()
    hist_vendas = carregar_historico_vendas()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ O Caixa está FECHADO.")
        return

    t_geral = sum(float(v.get('Valor Dinheiro', 0)) + float(v.get('Valor TPA', 0)) for v in hist_vendas)
    st.markdown(f"<div class='bloco-seccao' style='text-align: center;'><b>Total Acumulado:</b> {t_geral:,.2f} Kz</div>", unsafe_allow_html=True)

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        str_m = str(m_ativa)
        if st.button("⬅️ Voltar"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.subheader(f"🎛️ Mesa {m_ativa}")
        dados_m = mesas_data[str_m]
        
        if dados_m.get("fatura_emitida"):
            if st.button("🧹 Liberar Mesa", type="primary"):
                mesas_data[str_m] = {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "fatura_emitida": None}
                salvar_mesas_disco(mesas_data)
                del st.session_state.mesa_ativa
                st.rerun()
            return

        dados_m['total'] = float(sum(p['quantidade'] * p['preco'] for p in dados_m['pedidos'] if p['status'] not in ["Anulado", "Recusado pela Cozinha"]))
        salvar_mesas_disco(mesas_data)

        for p in dados_m['pedidos']:
            st.write(- {p['quantidade']}x {p['item']} | {(p['quantidade']*p['preco']):,.2f} Kz)

        st.markdown(f"### Total: {dados_m['total']:,.2f} Kz")

        if dados_m['total'] > 0:
            tp_pag = st.selectbox("Pagamento:", ["Dinheiro", "TPA", "Ambos"], key=f"pag_{m_ativa}")
            v_din = dados_m['total'] if tp_pag == "Dinheiro" else (0.0 if tp_pag == "TPA" else st.number_input("Dinheiro:", value=dados_m['total']/2))
            v_tpa = 0.0 if tp_pag == "Dinheiro" else (dados_m['total'] if tp_pag == "TPA" else dados_m['total'] - v_din)

            if st.button("💳 Fechar Conta", type="primary", key=f"btn_fec_{m_ativa}"):
                cli_nome = dados_m['cliente']['nome'] if dados_m.get('cliente') else 'Cliente'
                cli_tel = dados_m['cliente']['telefone'] if dados_m.get('cliente') else 'N/A'
                
                hist_vendas.append({
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Mesa": m_ativa, "Cliente": cli_nome,
                    "Valor Total": dados_m["total"], "Valor Dinheiro": v_din, "Valor TPA": v_tpa, "Modo Pagamento": tp_pag
                })
                salvar_historico_vendas(hist_vendas)

                dados_m["fatura_emitida"] = {"data": datetime.now().strftime("%Y-%m-%d %H:%M"), "cliente": cli_nome, "telefone": cli_tel, "itens": list(dados_m["pedidos"]), "total": dados_m["total"], "pagamento_detalhe": tp_pag}
                dados_m["status"] = "Fechada"
                salvar_mesas_disco(mesas_data)
                del st.session_state.mesa_ativa
                st.rerun()
    else:
        tab_b1, tab_b2, tab_b3 = st.tabs(["1-10", "11-20", "21-30"])
        blocos = [(tab_b1, range(1, 11)), (tab_b2, range(11, 21)), (tab_b3, range(21, 31))]
        
        for tab_a, intervalo in blocos:
            with tab_a:
                cols = st.columns(5)
                for c_idx, num_m in enumerate(intervalo):
                    d_m = mesas_data[str(num_m)]
                    d_m['total'] = sum(p['quantidade'] * p['preco'] for p in d_m['pedidos'] if p['status'] not in ["Anulado", "Recusado pela Cozinha"])
                    
                    pronta = any(("refei" in str(p.get("tipo","")).lower() or "prato" in str(p.get("tipo","")).lower()) and p.get("cozinha_status") == "Feito" for p in d_m['pedidos'])
                    cls = "mesa-pronta-alerta" if pronta else ("mesa-aberta" if d_m["status"] == "Aberta" else "mesa-fechada")
                    
                    with cols[c_idx % 5]:
                        st.markdown(f"<div class='{cls}'>{'🚨 Pronta<br>' if pronta else ''}Mesa {num_m}<br>{d_m['status']}<br>{d_m['total']:,.2f} Kz</div>", unsafe_allow_html=True)
                        if st.button(f"Gerir {num_m}", key=f"bm_{num_m}", use_container_width=True):
                            st.session_state.mesa_ativa = num_m
                            st.rerun()
                            
    salvar_mesas_disco(mesas_data)


# ==========================================
# ROTEADOR PRINCIPAL
# ==========================================
if mesa_detectada and 1 <= mesa_detectada <= 30:
    area_cliente()
elif perfil_url == "cozinha":
    area_cozinha()
elif perfil_url == "caixa":
    area_caixa_mesas()
else:
    area_administrador()
