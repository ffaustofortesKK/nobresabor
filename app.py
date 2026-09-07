import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
import os

# Configuração da Página
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

ARQUIVO_ESTADO_CAIXA = "caixa_status.txt"

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

# Estilos CSS
st.markdown("""
    <style>
    @keyframes piscar-mesa {
        0% { background-color: #ff4b4b; color: white; transform: scale(1); }
        50% { background-color: #ffe6e6; color: black; transform: scale(1.03); }
        100% { background-color: #ff4b4b; color: white; transform: scale(1); }
    }
    @keyframes piscar-pronto {
        0% { background-color: #ff8c00; color: white; transform: scale(1); }
        50% { background-color: #fffacd; color: black; transform: scale(1.03); }
        100% { background-color: #ff8c00; color: white; transform: scale(1); }
    }
    .mesa-aberta {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .mesa-fechada {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .bloco-seccao {
        padding: 25px;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        margin-bottom: 30px;
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

# Sincroniza o estado com o disco central do servidor
estado_atual_disco = ler_estado_caixa_disco()
st.session_state.caixa_aberto = estado_atual_disco

if "mesas" not in st.session_state:
    st.session_state.mesas = {
        i: {"status": "Fechada", "pedidos": [], "total": 0.0} for i in range(1, 31)
    }

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

if "clientes_mesa" not in st.session_state:
    st.session_state.clientes_mesa = {}

if "historico_vendas_definitivo" not in st.session_state:
    st.session_state.historico_vendas_definitivo = []

URL_OFICIAL = "https://nobresabor.streamlit.app"

def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# Sidebar dinâmica
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("NobreSabor - Gestão")
st.sidebar.divider()
if st.session_state.caixa_aberto:
    st.sidebar.success("🟢 Caixa Aberto")
else:
    st.sidebar.error("🔴 Caixa Fechado")

# ==========================================
# ÁREA: CLIENTE
# ==========================================
def area_cliente():
    # Fixa a mesa na sessão para nunca se perder ao submeter formulários ou atualizar
    if "mesa_cliente_atual" not in st.session_state:
        if mesa_detectada and 1 <= mesa_detectada <= 30:
            st.session_state.mesa_cliente_atual = mesa_detectada
        else:
            st.session_state.mesa_cliente_atual = 1
            
    num_mesa = st.session_state.mesa_cliente_atual
    
    if num_mesa not in st.session_state.clientes_mesa:
        st.markdown("<h1 style='text-align: center;'>🍽️ Bem-vindo ao Restaurante Nobre Sabor</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: gray;'>Registo de Entrada - Mesa {num_mesa}</h3>", unsafe_allow_html=True)
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form(f"form_cli_{num_mesa}"):
                nome_cli = st.text_input("Nome:")
                tel_cli = st.text_input("Telefone:")
                whatsapp_opt = st.checkbox("Deseja entrar no Grupo de WhatsApp do Restaurante?")
                
                btn_reg = st.form_submit_button("Entrar e Ver Menu", use_container_width=True)
                if btn_reg and nome_cli and tel_cli:
                    st.session_state.clientes_mesa[num_mesa] = {
                        "nome": nome_cli,
                        "telefone": tel_cli,
                        "whatsapp": whatsapp_opt
                    }
                    st.session_state.mesas[num_mesa]["status"] = "Aberta"
                    st.success("Registo efetuado com sucesso!")
                    st.rerun()
                elif btn_reg:
                    st.warning("Preencha o seu nome e telefone.")
    else:
        cli = st.session_state.clientes_mesa[num_mesa]
        st.title(f"📱 NobreSabor | Mesa {num_mesa}")
        st.success(f"Bem-vindo, **{cli['nome']}**!")
        
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo & Fatura", "🎉 Programas"])
        
        with tab_menu:
            cat_escolhida = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas"])
            stock_df = st.session_state.stock
            itens_cat = stock_df[stock_df['Categoria'] == cat_escolhida]
            
            if not itens_cat.empty:
                item_escolhido = st.selectbox("Item:", itens_cat['Produto'].tolist())
                row_prod = itens_cat[itens_cat['Produto'] == item_escolhido].iloc[0]
                qtd = st.number_input("Quantidade:", min_value=1, value=1)
                obs = st.text_input("Observações:")
                
                if st.button("🚀 Enviar Pedido"):
                    is_refeicao = (cat_escolhida == "Refeições")
                    novo_pedido = {
                        "item": item_escolhido,
                        "tipo": cat_escolhida,
                        "quantidade": qtd,
                        "preco": row_prod['Preço Unitário'],
                        "origem": f"Cliente ({cli['nome']})",
                        "obs": obs,
                        "status": "Confirmado" if not is_refeicao else "Pendente",
                        "cozinha_status": "N/A" if not is_refeicao else "Pendente",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[num_mesa]["pedidos"].append(novo_pedido)
                    st.session_state.mesas[num_mesa]["status"] = "Aberta"
                    
                    st.success("Pedido enviado com sucesso!")
                    st.rerun()
                
        with tab_consumo:
            st.subheader("O Meu Consumo")
            pedidos_mesa = st.session_state.mesas[num_mesa]["pedidos"]
            if not pedidos_mesa:
                st.info("Ainda não tem pedidos.")
            else:
                subtotal_geral = 0
                for p in pedidos_mesa:
                    total_item = p['quantidade'] * p['preco']
                    if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                        subtotal_geral += total_item
                    st.write(f"- {p['quantidade']}x {p['item']} | {total_item:,.2f} Kz ({p['status']})")
                st.markdown(f"### Total: {subtotal_geral:,.2f} Kz")
                
        with tab_eventos:
            st.subheader("Eventos da Semana")
            st.markdown("- Sexta: Música ao Vivo\n- Sábado: Karaoke (Grupo FF Karaoke)")


# ==========================================
# ÁREA: COZINHA (Com Fragmento Auto-Executável)
# ==========================================
@st.fragment(run_every=6)
def area_cozinha():
    st.title("🍳 Área da Cozinha - Gestão de Refeições")
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** A cozinha foi encerrada automaticamente.")
        return

    st.caption("🔄 Esta secção atualiza-se sozinha em segundo plano (sem dar F5 na página).")
    
    tem_pedidos = False
    for i in range(1, 31):
        dados_m = st.session_state.mesas[i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            if ped["tipo"] == "Refeições" and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
                tem_pedidos = True
                
                col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                with col_c1:
                    st.write(f"### 🍽️ Mesa {i}")
                    st.write(f"**Refeição:** {ped['item']} | **Qtd:** {ped['quantidade']}")
                    st.write(f"Origem: _{ped['origem']}_ | Obs: _{ped['obs']}_")
                with col_c2:
                    st.write(f"Estado: **{ped.get('cozinha_status', 'Pendente')}**")
                with col_c3:
                    estado_atual = ped.get('cozinha_status', 'Pendente')
                    if estado_atual == "Pendente":
                        if st.button("✅ Aprovar", key=f"aprov_cz_{i}_{idx_p}"):
                            st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                            st.session_state.mesas[i]["pedidos"][idx_p]["status"] = "Confirmado"
                            st.rerun()
                        if st.button("❌ Recusar", key=f"rec_cz_{i}_{idx_p}"):
                            st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Recusado"
                            st.session_state.mesas[i]["pedidos"][idx_p]["status"] = "Recusado pela Cozinha"
                            st.rerun()
                    elif estado_atual == "Aprovado":
                        if st.button("🍲 Marcar Feito", key=f"feito_cz_{i}_{idx_p}"):
                            st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                            st.rerun()
                st.divider()
                
    if not tem_pedidos:
        st.success("🎉 Sem refeições pendentes de momento!")


# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
def area_administrador():
    st.markdown("<hr style='margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    st.title("👑 Painel do Administrador - NobreSabor")
    
    with st.expander("🔗 Links Oficiais do Sistema", expanded=True):
        st.text_input("Link Direto do Caixa:", f"{URL_OFICIAL}/?perfil=caixa")
        st.text_input("Link Direto da Cozinha:", f"{URL_OFICIAL}/?perfil=cozinha")
        
    tab_fin, tab_stk, tab_dch = st.tabs(["💰 Finanças", "📦 Stock", "👥 DCH"])
    
    with tab_fin:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("💰 Controlo de Caixa")
        
        col_cx_status, col_cx_btn = st.columns([3, 1])
        with col_cx_status:
            if st.session_state.caixa_aberto:
                st.success("🟢 O Caixa encontra-se ABERTO.")
            else:
                st.error("🔴 O Caixa encontra-se FECHADO.")
        with col_cx_btn:
            if st.session_state.caixa_aberto:
                if st.button("Fechar Caixa", type="secondary", key="btn_fechar_cx_adm"):
                    st.session_state.caixa_aberto = False
                    gravar_estado_caixa_disco(False)
                    st.success("Caixa fechado com sucesso! As abas de caixa e cozinha serão encerradas automaticamente.")
                    st.rerun()
            else:
                if st.button("Abrir Caixa", type="primary", key="btn_abrir_cx_adm"):
                    st.session_state.caixa_aberto = True
                    gravar_estado_caixa_disco(True)
                    st.success("Caixa aberto com sucesso!")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Histórico de Vendas")
        if st.session_state.historico_vendas_definitivo:
            st.dataframe(pd.DataFrame(st.session_state.historico_vendas_definitivo), use_container_width=True)
        else:
            st.info("Sem vendas registadas.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_stk:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("📦 Stock")
        with st.form("form_stock_adm"):
            np = st.text_input("Produto")
            cat = st.selectbox("Categoria", ["Bebidas", "Refeições", "Sobremesas"])
            qtd = st.number_input("Quantidade", min_value=0)
            prc = st.number_input("Preço (Kz)", min_value=0.0)
            if st.form_submit_button("Adicionar") and np:
                novo_df = pd.DataFrame([[np, cat, qtd, prc]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                st.session_state.stock = pd.concat([st.session_state.stock, novo_df], ignore_index=True)
                st.rerun()
        st.dataframe(st.session_state.stock, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_dch:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("👥 Recursos Humanos")
        with st.form("form_rh_adm"):
            cc = st.text_input("Código")
            nc = st.text_input("Nome")
            cat_func = st.selectbox("Categoria", ["Garçon", "Cozinheiro", "Caixa"])
            tel = st.text_input("Telefone")
            bi = st.text_input("BI")
            if st.form_submit_button("Registar") and cc:
                novo_rh = pd.DataFrame([[cc, nc, cat_func, tel, bi]], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                st.session_state.rh = pd.concat([st.session_state.rh, novo_rh], ignore_index=True)
                st.rerun()
        st.dataframe(st.session_state.rh, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS (Com Fragmento Auto-Executável)
# ==========================================
@st.fragment(run_every=6)
def area_caixa_mesas():
    st.title("💻 Controlo Geral de Mesas e Faturação (Caixa)")
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** O Administrador encerrou o caixa, pelo que esta secção foi bloqueada automaticamente.")
        return

    st.success("🟢 Caixa Aberto. Atualização inteligente em segundo plano ativa.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        if st.button("⬅️ Voltar à Visão Geral"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Gestão da Mesa {m_ativa}")
        dados_mesa = st.session_state.mesas[m_ativa]
        
        # Cálculo automático do total da mesa
        total_calculado = sum(
            p['quantidade'] * p['preco'] 
            for p in dados_mesa['pedidos'] 
            if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
        )
        dados_mesa['total'] = total_calculado

        with st.expander("📷 QR Code", expanded=False):
            link_mesa = f"{URL_OFICIAL}/?mesa={m_ativa}"
            st.code(link_mesa)
            st.image(gerar_qrcode_bytes(link_mesa), width=130)

        st.subheader("📝 Pedidos Lançados na Mesa")
        if not dados_mesa['pedidos']:
            st.info("Nenhum pedido efetuado nesta mesa ainda.")
        else:
            for idx_p, p in enumerate(dados_mesa['pedidos']):
                col_p1, col_p2, col_p3 = st.columns([3, 2, 2])
                with col_p1:
                    st.write(f"- {p['quantidade']}x {p['item']} ({p['tipo']})")
                    if p['obs']:
                        st.caption(f"Obs: {p['obs']}")
                with col_p2:
                    st.write(f"**{(p['quantidade'] * p['preco']):,.2f} Kz**")
                with col_p3:
                    st.write(f"Estado: `{p['status']}`")

        st.markdown(f"### Total a Pagar: **{dados_mesa['total']:,.2f} Kz**")

        if st.button("💳 Fechar Conta e Faturar", type="primary"):
            if dados_mesa['total'] > 0:
                st.session_state.historico_vendas_definitivo.append({
                    "Nome": "Cliente Mesa", "Telefone": "N/A", "Mesa": m_ativa,
                    "Valor": dados_mesa["total"], "Dia": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Pagamento": "Dinheiro/TPA"
                })
                st.success("Conta fechada com sucesso!")
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                if m_ativa in st.session_state.clientes_mesa:
                    del st.session_state.clientes_mesa[m_ativa]
                st.rerun()
            else:
                st.warning("A mesa não tem valor a faturar.")
    else:
        cols_por_linha = 6
        for linha in range(5):
            cols = st.columns(cols_por_linha)
            for c in range(cols_por_linha):
                num_mesa = linha * cols_por_linha + c + 1
                if num_mesa <= 30:
                    dados_m = st.session_state.mesas[num_mesa]
                    status_m = dados_m["status"]
                    
                    dados_m['total'] = sum(
                        p['quantidade'] * p['preco'] 
                        for p in dados_m['pedidos'] 
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )
                    
                    classe_css = "mesa-aberta" if status_m == "Aberta" else "mesa-fechada"
                    
                    with cols[c]:
                        st.markdown(f"""
                            <div class="{classe_css}">
                                Mesa {num_mesa}<br>{status_m}<br>
                                <span style="font-size: 0.8em;">{dados_m['total']:,.2f} Kz</span>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Gerir {num_mesa}", key=f"btn_m_{num_mesa}", use_container_width=True):
                            st.session_state.mesa_ativa = num_mesa
                            st.rerun()


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
