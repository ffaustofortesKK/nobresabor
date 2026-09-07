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

# Ficheiro local para partilhar o estado exato do caixa entre as abas na nuvem
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

# Estilo CSS para Animações, Espaçamentos e Alertas
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
    .mesa-alerta {
        animation: piscar-mesa 1s infinite;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .mesa-pronta {
        animation: piscar-pronto 1s infinite;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CAPTURA DE PARÂMETROS E ESTADO GLOBAL
# ==========================================
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

if "remocoes_log" not in st.session_state:
    st.session_state.remocoes_log = []

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
# ÁREA: CLIENTE (QR CODE)
# ==========================================
def area_cliente():
    num_mesa = mesa_detectada if (mesa_detectada and 1 <= mesa_detectada <= 30) else 1
    
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
                    st.success("Registo efetuado com sucesso! A abrir o menu...")
                    st.rerun()
                elif btn_reg:
                    st.warning("Por favor, preencha o seu nome e telefone.")
    else:
        cli = st.session_state.clientes_mesa[num_mesa]
        st.title(f"📱 NobreSabor | Mesa {num_mesa}")
        st.success(f"Bem-vindo, **{cli['nome']}**! A sua mesa está aberta.")
        
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo & Fatura", "🎉 Programas e Eventos"])
        
        with tab_menu:
            st.subheader("Faça o seu pedido por categorias")
            cat_escolhida = st.selectbox("Selecione a Categoria:", ["Bebidas", "Refeições", "Sobremesas"])
            
            stock_df = st.session_state.stock
            itens_cat = stock_df[stock_df['Categoria'] == cat_escolhida]
            
            if not itens_cat.empty:
                item_escolhido = st.selectbox("Escolha o Item:", itens_cat['Produto'].tolist())
                row_prod = itens_cat[itens_cat['Produto'] == item_escolhido].iloc[0]
                
                qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
                obs = st.text_input("Observações (ex: Sem gelo, bem passado):")
                
                if st.button("🚀 Enviar Pedido"):
                    novo_pedido = {
                        "item": item_escolhido,
                        "tipo": cat_escolhida,
                        "quantidade": qtd,
                        "preco": row_prod['Preço Unitário'],
                        "origem": f"Cliente ({cli['nome']})",
                        "obs": obs,
                        "status": "Pendente",
                        "cozinha_status": "Pendente" if cat_escolhida == "Refeições" else "N/A",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[num_mesa]["pedidos"].append(novo_pedido)
                    st.success("🎉 Pedido enviado com sucesso!")
                    st.rerun()
            else:
                st.warning("Nenhum item disponível nesta categoria.")
                
        with tab_consumo:
            st.subheader("📊 O Meu Consumo Atual")
            pedidos_mesa = st.session_state.mesas[num_mesa]["pedidos"]
            if not pedidos_mesa:
                st.info("Ainda não tem pedidos registados.")
            else:
                subtotal_geral = 0
                for p in pedidos_mesa:
                    total_item = p['quantidade'] * p['preco']
                    if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                        subtotal_geral += total_item
                    
                    estado_txt = p['status']
                    if p.get('cozinha_status') == "Aprovado":
                        estado_txt = "✅ Refeição Aprovada pela Cozinha"
                    elif p.get('cozinha_status') == "Recusado":
                        estado_txt = "❌ Refeição Recusada (Esgotado)"
                    elif p.get('cozinha_status') == "Feito":
                        estado_txt = "🍲 Refeição Pronta a Servir!"
                        
                    st.write(f"- **{p['quantidade']}x {p['item']}** ({p['tipo']}) | Preço: {p['preco']:,.2f} Kz | Subtotal: {total_item:,.2f} Kz | Estado: {estado_txt}")
                st.divider()
                st.markdown(f"### Total a Pagar: **{subtotal_geral:,.2f} Kz**")
                
        with tab_eventos:
            st.subheader("🎵 Programas e Eventos da Semana - NobreSabor")
            st.markdown("""
            * **Sexta-Feira de Serão:** Música ao vivo a partir das 20h.
            * **Sábado de Karaoke:** Com o Grupo FF Karaoke!
            * **Domingo em Família:** Almoços especiais e cinema comunitário.
            """)


# ==========================================
# ÁREA: COZINHA (CHEF)
# ==========================================
def area_cozinha():
    # Script JavaScript leve que atualiza a página automaticamente a cada 6 segundos nas abas operacionais
    st.markdown("""
        <script>
            setTimeout(function(){
                window.location.reload();
            }, 6000);
        </script>
    """, unsafe_allow_html=True)

    st.title("🍳 Área da Cozinha - Gestão de Refeições")
    
    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** O Administrador encerrou o caixa, pelo que esta secção foi bloqueada automaticamente.")
        return

    st.info("O Chef gere as refeições solicitadas, podendo Aprovar, Recusar ou marcar como Feito.")
    
    tem_pedidos = False
    for i in range(1, 31):
        dados_m = st.session_state.mesas[i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            if ped["tipo"] == "Refeições" and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
                tem_pedidos = True
                
                col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                with col_c1:
                    st.write(f"### 🍽️ Mesa {i}")
                    st.write(f"**Refeição:** {ped['item']} | **Quantidade:** {ped['quantidade']}")
                    st.write(f"Responsável/Origem: _{ped['origem']}_ | Obs: _{ped['obs']}_ | ⏰ {ped['hora']}")
                with col_c2:
                    estado_atual = ped.get('cozinha_status', 'Pendente')
                    st.write(f"Estado: **{estado_atual}**")
                with col_c3:
                    if estado_atual == "Pendente":
                        if st.button("✅ Aprovar", key=f"aprov_cz_{i}_{idx_p}"):
                            st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                            st.session_state.mesas[i]["pedidos"][idx_p]["status"] = "Confirmado"
                            st.session_state.mesas[i]["total"] += (ped['quantidade'] * ped['preco'])
                            st.success("Refeição aprovada!")
                            st.rerun()
                        if st.button("❌ Recusar (Esgotado)", key=f"rec_cz_{i}_{idx_p}"):
                            st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Recusado"
                            st.session_state.mesas[i]["pedidos"][idx_p]["status"] = "Recusado pela Cozinha"
                            st.warning("Refeição recusada!")
                            st.rerun()
                    elif estado_atual == "Aprovado":
                        if st.button("🍲 Marcar como Feito (Pronto)", key=f"feito_cz_{i}_{idx_p}"):
                            st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                            st.success("Marcado como pronto!")
                            st.rerun()
                st.divider()
                
    if not tem_pedidos:
        st.success("🎉 Não há refeições pendentes na cozinha!")


# ==========================================
# ÁREA: ADMINISTRADOR (FINANÇAS, STOCK, DCH)
# ==========================================
def area_administrador():
    st.markdown("<hr style='margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    st.title("👑 Painel do Administrador - NobreSabor")
    st.info("Painel Mestre: Controlo Financeiro, Stock e Recursos Humanos (DCH). É aqui que se faz a Abertura e Fecho do Caixa.")
    
    with st.expander("🔗 Links Oficiais do Sistema", expanded=True):
        st.text_input("Link Direto do Caixa:", f"{URL_OFICIAL}/?perfil=caixa")
        st.text_input("Link Direto da Cozinha:", f"{URL_OFICIAL}/?perfil=cozinha")
        st.caption("ℹ️ Nota: Ao fechar o caixa aqui, as abas de caixa e cozinha detetam o fecho automaticamente em poucos segundos.")
        
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    tab_fin, tab_stk, tab_dch = st.tabs(["💰 Finanças", "📦 Stock", "👥 DCH"])
    
    with tab_fin:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("💰 Gestão de Abertura de Caixa e Finanças")
        
        col_cx_status, col_cx_btn = st.columns([3, 1])
        with col_cx_status:
            if st.session_state.caixa_aberto:
                st.success("🟢 O Caixa encontra-se ABERTO e operacional para faturação.")
            else:
                st.error("🔴 O Caixa encontra-se FECHADO. Clique no botão ao lado para abrir o registo do dia.")
        with col_cx_btn:
            if st.session_state.caixa_aberto:
                if st.button("Fechar Caixa", type="secondary", key="btn_fechar_cx_adm"):
                    st.session_state.caixa_aberto = False
                    gravar_estado_caixa_disco(False)
                    st.success("Caixa fechado! O sistema bloqueará a cozinha e o caixa automaticamente.")
                    st.rerun()
            else:
                if st.button("Abrir Caixa", type="primary", key="btn_abrir_cx_adm"):
                    st.session_state.caixa_aberto = True
                    gravar_estado_caixa_disco(True)
                    st.success("Caixa aberto com sucesso!")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Histórico de Faturação e Vendas do Dia")
        if st.session_state.historico_vendas_definitivo:
            df_vendas = pd.DataFrame(st.session_state.historico_vendas_definitivo)
            st.dataframe(df_vendas, use_container_width=True)
        else:
            st.info("Ainda não existem vendas fechadas registadas.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_stk:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("📦 Gestão de Stock")
        with st.form("form_stock_adm"):
            np = st.text_input("Nome do Produto")
            cat = st.selectbox("Categoria", ["Bebidas", "Refeições", "Sobremesas"])
            qtd = st.number_input("Quantidade", min_value=0)
            prc = st.number_input("Preço (Kz)", min_value=0.0)
            if st.form_submit_button("Adicionar Produto") and np:
                novo_df = pd.DataFrame([[np, cat, qtd, prc]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                st.session_state.stock = pd.concat([st.session_state.stock, novo_df], ignore_index=True)
                st.success("Produto adicionado ao stock!")
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(st.session_state.stock, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_dch:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("👥 Recursos Humanos (DCH)")
        with st.form("form_rh_adm"):
            cc = st.text_input("Código do Colaborador")
            nc = st.text_input("Nome Completo")
            cat_func = st.selectbox("Categoria", ["Garçon", "Cozinheiro", "Caixa"])
            tel = st.text_input("Telefone")
            bi = st.text_input("Nº de Bilhete de Identidade (BI)")
            if st.form_submit_button("Registar Colaborador") and cc and nc:
                novo_rh = pd.DataFrame([[cc, nc, cat_func, tel, bi]], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                st.session_state.rh = pd.concat([st.session_state.rh, novo_rh], ignore_index=True)
                st.success("Colaborador registado com sucesso!")
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(st.session_state.rh, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS (?perfil=caixa)
# ==========================================
def area_caixa_mesas():
    # Script JavaScript leve que atualiza a página automaticamente a cada 6 segundos nas abas operacionais
    st.markdown("""
        <script>
            setTimeout(function(){
                window.location.reload();
            }, 6000);
        </script>
    """, unsafe_allow_html=True)

    st.title("💻 Controlo Geral de Mesas e Faturação (Caixa)")
    
    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** O Administrador fechou o caixa no Painel de Administração, pelo que esta secção foi bloqueada automaticamente.")
        return

    st.success("🟢 Caixa Aberto e Operacional. Pode gerir as mesas e faturar abaixo.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        if st.button("⬅️ Voltar à Visão Geral das Mesas"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Gestão Detalhada da Mesa {m_ativa}")
        dados_mesa = st.session_state.mesas[m_ativa]
        
        with st.expander(f"📷 QR Code e Link da Mesa {m_ativa}", expanded=True):
            link_mesa = f"{URL_OFICIAL}/?mesa={m_ativa}"
            st.code(link_mesa)
            if m_ativa in st.session_state.clientes_mesa:
                cli = st.session_state.clientes_mesa[m_ativa]
                st.info(f"👤 **Cliente:** {cli['nome']} | 📞 {cli['telefone']}")
            else:
                st.warning("👤 Nenhum cliente registado ainda.")
            st.image(gerar_qrcode_bytes(link_mesa), width=130)

        st.divider()
        st.write(f"**Total da Conta:** **{dados_mesa['total']:,.2f} Kz**")

        with st.expander("➕ Adicionar Pedido Manualmente (com Identificação de Garçon/Colaborador)"):
            prod_cx = st.selectbox("Produto:", st.session_state.stock['Produto'].tolist(), key=f"p_cx_{m_ativa}")
            row_cx = st.session_state.stock[st.session_state.stock['Produto'] == prod_cx].iloc[0]
            qtd_cx = st.number_input("Qtd:", min_value=1, value=1, key=f"q_cx_{m_ativa}")
            
            lista_garcons = st.session_state.rh[st.session_state.rh['Categoria'] == 'Garçon']
            if not lista_garcons.empty:
                garcon_escolhido = st.selectbox("Garçon / Colaborador Responsável:", [f"{row['Nome']} (Cód: {row['Código']})" for _, row in lista_garcons.iterrows()], key=f"g_cx_{m_ativa}")
            else:
                garcon_escolhido = "Caixa Balcão"
                
            if st.button("Registar na Mesa", key=f"b_cx_{m_ativa}"):
                novo_p_cx = {
                    "item": prod_cx,
                    "tipo": row_cx['Categoria'],
                    "quantidade": qtd_cx,
                    "preco": row_cx['Preço Unitário'],
                    "origem": f"Caixa (Registado com Garçon: {garcon_escolhido})",
                    "obs": "",
                    "status": "Confirmado" if row_cx['Categoria'] != "Refeições" else "Pendente",
                    "cozinha_status": "Pendente" if row_cx['Categoria'] == "Refeições" else "N/A",
                    "hora": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.mesas[m_ativa]["status"] = "Aberta"
                st.session_state.mesas[m_ativa]["pedidos"].append(novo_p_cx)
                if row_cx['Categoria'] != "Refeições":
                    st.session_state.mesas[m_ativa]["total"] += (qtd_cx * row_cx['Preço Unitário'])
                st.success("Adicionado com sucesso e associado ao garçom!")
                st.rerun()

        st.subheader("🛍️ Pedidos da Mesa")
        if not dados_mesa["pedidos"]:
            st.info("Nenhum pedido registado.")
        else:
            for idx, p in enumerate(dados_mesa["pedidos"]):
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{p['quantidade']}x {p['item']}** ({p['tipo']})")
                    st.write(f"**Origem/Responsável:** {p['origem']} | Estado: **{p['status']}**")
                with col2:
                    st.write(f"Subtotal: {p['quantidade'] * p['preco']:,.2f} Kz")
                    if p['tipo'] == "Bebidas" and p['status'] == "Pendente":
                        if st.button(f"Confirmar Bebida #{idx}", key=f"conf_beb_{m_ativa}_{idx}"):
                            st.session_state.mesas[m_ativa]["pedidos"][idx]["status"] = "Confirmado"
                            st.session_state.mesas[m_ativa]["total"] += (p['quantidade'] * p['preco'])
                            st.success("Bebida confirmada!")
                            st.rerun()
                with col3:
                    with st.form(f"form_rem_{m_ativa}_{idx}"):
                        justificativa = st.text_input("Justificativa:", key=f"just_{m_ativa}_{idx}")
                        btn_rem = st.form_submit_button("❌ Remover Item")
                        if btn_rem and justificativa:
                            st.session_state.remocoes_log.append({
                                "mesa": m_ativa,
                                "item": p['item'],
                                "quantidade": p['quantidade'],
                                "justificativa": justificativa,
                                "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            if p['status'] == "Confirmado":
                                st.session_state.mesas[m_ativa]["total"] -= (p['quantidade'] * p['preco'])
                            st.session_state.mesas[m_ativa]["pedidos"][idx]["status"] = "Anulado"
                            st.success("Item removido.")
                            st.rerun()
                st.divider()

            st.subheader("💳 Fechar Fatura")
            tipo_pagamento = st.selectbox("Forma de Pagamento:", ["Monetário (Dinheiro)", "Pagamento Automático TPA"])
            if st.button("💰 Concluir Pagamento e Fechar Mesa", type="primary"):
                cli_data = st.session_state.clientes_mesa.get(m_ativa, {"nome": "Cliente Balcão", "telefone": "N/A"})
                st.session_state.historico_vendas_definitivo.append({
                    "Nome": cli_data["nome"],
                    "Telefone": cli_data["telefone"],
                    "Mesa": m_ativa,
                    "Valor": dados_mesa["total"],
                    "Dia": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Pagamento": tipo_pagamento
                })
                st.success("Fatura fechada com sucesso!")
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                if m_ativa in st.session_state.clientes_mesa:
                    del st.session_state.clientes_mesa[m_ativa]
                st.rerun()

    else:
        st.subheader("Painel de Mesas")
        cols_por_linha = 6
        for linha in range(5):
            cols = st.columns(cols_por_linha)
            for c in range(cols_por_linha):
                num_mesa = linha * cols_por_linha + c + 1
                if num_mesa <= 30:
                    dados_m = st.session_state.mesas[num_mesa]
                    status_m = dados_m["status"]
                    
                    tem_pedido_pendente = any(p["status"] == "Pendente" or p.get("cozinha_status") == "Feito" for p in dados_m["pedidos"])
                    tem_refeicao_pronta = any(p.get("cozinha_status") == "Feito" for p in dados_m["pedidos"])
                    
                    classe_css = "mesa-fechada"
                    if status_m == "Aberta":
                        classe_css = "mesa-aberta"
                    if tem_refeicao_pronta:
                        classe_css = "mesa-pronta"
                    elif tem_pedido_pendente:
                        classe_css = "mesa-alerta"
                        
                    with cols[c]:
                        st.markdown(f"""
                            <div class="{classe_css}">
                                Mesa {num_mesa}<br>
                                <span style="font-size: 12px; font-weight: normal;">{status_m}</span>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Gerir Mesa {num_mesa}", key=f"btn_gerir_m_{num_mesa}", use_container_width=True):
                            st.session_state.mesa_ativa = num_mesa
                            st.rerun()
                        st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)


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
