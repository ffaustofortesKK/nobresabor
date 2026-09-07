import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# Configuração da Página
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

# Estilo CSS para Animações e Alertas
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. INICIALIZAÇÃO DE ESTADOS DA SESSÃO
# ==========================================
if "caixa_aberto" not in st.session_state:
    st.session_state.caixa_aberto = False

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

# ==========================================
# 2. CAPTURA DE PARÂMETROS DA URL
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

# ==========================================
# 3. ROTEAMENTO DE PERFIS
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("NobreSabor - Gestão")

if mesa_detectada and 1 <= mesa_detectada <= 30:
    st.sidebar.success(f"📱 Atendimento Digital (Mesa {mesa_detectada})")
    menu_selecionado = "📱 Cliente"
elif perfil_url == "caixa":
    st.sidebar.success("💻 Perfil: Caixa Direto")
    menu_selecionado = "💻 Caixa & Gestão de Mesas"
elif perfil_url == "cozinha":
    st.sidebar.success("🍳 Perfil: Cozinha Direta")
    menu_selecionado = "🍳 Cozinha (Chef)"
else:
    menu_opcoes = [
        "👑 Administrador",
        "💻 Caixa & Gestão de Mesas", 
        "🍳 Cozinha (Chef)",
        "👨‍🍳 Garçon"
    ]
    menu_selecionado = st.sidebar.selectbox("Selecione a Área:", menu_opcoes)


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
                
                if st.button("📥 Gerar Fatura Digital para Impressão/Visualização"):
                    st.info("Fatura gerada com sucesso! Apresente ao caixa ou aguarde fecho.")
                    for p in pedidos_mesa:
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                            st.write(f"• {p['quantidade']}x {p['item']} - {p['quantidade']*p['preco']:,.2f} Kz")
                    st.success(f"TOTAL FATURA: {subtotal_geral:,.2f} Kz")
                
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
    st.title("🍳 Área da Cozinha - Gestão de Refeições")
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
                            st.success("Marcado como pronto! O caixa foi notificado com emoji a piscar.")
                            st.rerun()
                st.divider()
                
    if not tem_pedidos:
        st.success("🎉 Não há refeições pendentes na cozinha!")


# ==========================================
# ÁREA: GARÇON
# ==========================================
def area_garcon():
    st.title("👨‍🍳 Área do Garçon")
    codigo_garcon = st.text_input("Insira o seu Código de Colaborador:", type="password")
    
    if codigo_garcon:
        validar = st.session_state.rh[st.session_state.rh['Código'] == codigo_garcon]
        if validar.empty:
            st.error("❌ Código inválido.")
        else:
            nome_g = validar.iloc[0]['Nome']
            st.success(f"✅ Colaborador: {nome_g}")
            mesa_g = st.selectbox("Mesa:", [i for i in range(1, 31)])
            prod_g = st.selectbox("Produto:", st.session_state.stock['Produto'].tolist())
            row_p = st.session_state.stock[st.session_state.stock['Produto'] == prod_g].iloc[0]
            qtd_g = st.number_input("Quantidade:", min_value=1, value=1)
            
            if st.button("Lançar Pedido"):
                novo_p = {
                    "item": prod_g,
                    "tipo": row_p['Categoria'],
                    "quantidade": qtd_g,
                    "preco": row_p['Preço Unitário'],
                    "origem": f"Garçon ({nome_g}) [Cód: {codigo_garcon}]",
                    "obs": "",
                    "status": "Pendente",
                    "cozinha_status": "Pendente" if row_p['Categoria'] == "Refeições" else "N/A",
                    "hora": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.mesas[mesa_g]["status"] = "Aberta"
                st.session_state.mesas[mesa_g]["pedidos"].append(novo_p)
                st.success("Pedido lançado com o seu nome registado!")


# ==========================================
# ÁREA: CAIXA & GESTÃO DE MESAS (EXCLUSIVO DO CAIXA)
# ==========================================
def area_caixa():
    st.title("💻 Caixa - Controlo Geral e Mesas")
    
    col_cx_status, col_cx_btn = st.columns([3, 1])
    with col_cx_status:
        if st.session_state.caixa_aberto:
            st.success("🟢 O Caixa encontra-se ABERTO e operacional.")
        else:
            st.error("🔴 O Caixa encontra-se FECHADO.")
    with col_cx_btn:
        if st.session_state.caixa_aberto:
            if st.button("Fechar Caixa", type="secondary"):
                st.session_state.caixa_aberto = False
                st.rerun()
        else:
            if st.button("Abrir Caixa", type="primary"):
                st.session_state.caixa_aberto = True
                st.rerun()

    if not st.session_state.caixa_aberto:
        st.warning("Abra o caixa para poder aceder à gestão das mesas e pagamentos.")
        return

    st.divider()

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
                st.info(f"👤 **Cliente:** {cli['nome']} | 📞 {cli['telefone']} | WhatsApp: {'Sim ✅' if cli['whatsapp'] else 'Não ❌'}")
            else:
                st.warning("👤 Nenhum cliente registado ainda.")
            st.image(gerar_qrcode_bytes(link_mesa), width=130)

        st.divider()
        st.write(f"**Total da Conta:** **{dados_mesa['total']:,.2f} Kz**")

        # Registo manual pelo Caixa com identificação do Garçon / Responsável
        with st.expander("➕ Adicionar Pedido Manualmente (com Identificação de Garçon)"):
            prod_cx = st.selectbox("Produto:", st.session_state.stock['Produto'].tolist(), key=f"p_cx_{m_ativa}")
            row_cx = st.session_state.stock[st.session_state.stock['Produto'] == prod_cx].iloc[0]
            qtd_cx = st.number_input("Qtd:", min_value=1, value=1, key=f"q_cx_{m_ativa}")
            
            # Seleção do Garçon associado ao lançamento no caixa
            lista_garcons = st.session_state.rh[st.session_state.rh['Categoria'] == 'Garçon']
            if not lista_garcons.empty:
                garcon_escolhido = st.selectbox("Garçon Responsável pelo Pedido:", [f"{row['Nome']} (Cód: {row['Código']})" for _, row in lista_garcons.iterrows()], key=f"g_cx_{m_ativa}")
            else:
                garcon_escolhido = "Caixa Balcão"
                
            if st.button("Registar na Mesa", key=f"b_cx_{m_ativa}"):
                novo_p_cx = {
                    "item": prod_cx,
                    "tipo": row_cx['Categoria'],
                    "quantidade": qtd_cx,
                    "preco": row_cx['Preço Unitário'],
                    "origem": f"Caixa (Registado por: {garcon_escolhido})",
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
                    if p.get('cozinha_status') == "Recusado":
                        st.error("⚠️ Recusado pela Cozinha (Esgotado)!")
                with col2:
                    st.write(f"Subtotal: {p['quantidade'] * p['preco']:,.2f} Kz")
                    if p['tipo'] == "Bebidas" and p['status'] == "Pendente":
                        if st.button(f"Confirmar Saída Bebida #{idx}", key=f"conf_beb_{m_ativa}_{idx}l"):
                            st.session_state.mesas[m_ativa]["pedidos"][idx]["status"] = "Confirmado"
                            st.session_state.mesas[m_ativa]["total"] += (p['quantidade'] * p['preco'])
                            st.success("Bebida confirmada e saída de stock autorizada!")
                            st.rerun()
                with col3:
                    with st.form(f"form_rem_{m_ativa}_{idx}"):
                        justificativa = st.text_input("Justificativa para remover:", key=f"just_{m_ativa}_{idx}")
                        btn_rem = st.form_submit_button("❌ Remover Item")
                        if btn_rem:
                            if not justificativa:
                                st.warning("Preencha a justificativa para remover o item!")
                            else:
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
                                st.success("Item removido e reportado.")
                                st.rerun()
                st.divider()

            st.subheader("💳 Fechar Fatura e Pagamento")
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
                
                st.success(f"Fatura fechada com sucesso via {tipo_pagamento}!")
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                if m_ativa in st.session_state.clientes_mesa:
                    del st.session_state.clientes_mesa[m_ativa]
                st.rerun()

    else:
        st.info("💡 As mesas com novos pedidos piscam a vermelho. As mesas com refeição pronta piscam a Laranja com 🍲.")
        cols = st.columns(6)
        for i in range(1, 31):
            m_info = st.session_state.mesas[i]
            tem_pendente = any(p["status"] == "Pendente" for p in m_info["pedidos"])
            tem_pronto = any(p.get("cozinha_status") == "Feito" for p in m_info["pedidos"])
            tem_recusado = any(p.get("cozinha_status") == "Recusado" for p in m_info["pedidos"])
            
            with cols[(i - 1) % 6]:
                if tem_pronto:
                    st.markdown(f'<div class="mesa-pronta">MESA {i}<br>🍲 PRATO PRONTO!</div>', unsafe_allow_html=True)
                elif tem_recusado:
                    st.markdown(f'<div class="mesa-alerta">MESA {i}<br>❌ RECUSADO!</div>', unsafe_allow_html=True)
                elif tem_pendente:
                    st.markdown(f'<div class="mesa-alerta">MESA {i}<br>🔔 NOVO PEDIDO!</div>', unsafe_allow_html=True)
                elif m_info["status"] == "Aberta":
                    st.markdown(f'<div class="mesa-aberta">Mesa {i}<br>({m_info["total"]:,.2f} Kz)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="mesa-fechada">Mesa {i}<br>Fechada</div>', unsafe_allow_html=True)
                    
                if st.button(f"Gerir Mesa {i}", key=f"btn_m_{i}"):
                    st.session_state.mesa_ativa = i
                    st.rerun()


# ==========================================
# ÁREA: ADMINISTRADOR (ABERTURA DE CAIXA, STOCK E RH)
# ==========================================
def area_administrador():
    st.title("👑 Painel do Administrador - NobreSabor")
    st.info("Painel Mestre: Abertura/Fecho de Caixa, Gestão de Stock e Recursos Humanos.")
    
    with st.expander("🔗 Links Oficiais do Sistema", expanded=True):
        st.text_input("Link Direto do Caixa:", f"{URL_OFICIAL}/?perfil=caixa")
        st.text_input("Link Direto da Cozinha:", f"{URL_OFICIAL}/?perfil=cozinha")
        
    tab1, tab3, tab4 = st.tabs(["💰 Controlo de Caixa", "📦 Stock", "👥 RH"])
    
    with tab1:
        st.subheader("Estado do Caixa (Abertura / Fecho)")
        if st.session_state.caixa_aberto:
            st.success("O Caixa encontra-se atualmente **ABERTO** e operacional para o operador.")
            if st.button("🔴 Fechar o Caixa"):
                st.session_state.caixa_aberto = False
                st.rerun()
        else:
            st.error("O Caixa encontra-se atualmente **FECHADO**.")
            if st.button("🟢 Abrir o Caixa"):
                st.session_state.caixa_aberto = True
                st.success("Caixa aberto com sucesso!")
                st.rerun()
            
    with tab3:
        st.subheader("📦 Gestão de Stock")
        with st.form("form_stock"):
            np = st.text_input("Nome do Produto")
            cat = st.selectbox("Categoria", ["Bebidas", "Refeições", "Sobremesas"])
            qtd = st.number_input("Quantidade", min_value=0)
            prc = st.number_input("Preço (Kz)", min_value=0.0)
            if st.form_submit_button("Adicionar") and np:
                novo_df = pd.DataFrame([[np, cat, qtd, prc]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                st.session_state.stock = pd.concat([st.session_state.stock, novo_df], ignore_index=True)
                st.success("Produto adicionado!")
        st.dataframe(st.session_state.stock, use_container_width=True)
        
    with tab4:
        st.subheader("👥 Recursos Humanos")
        with st.form("form_rh"):
            cc = st.text_input("Código")
            nc = st.text_input("Nome")
            cat_func = st.selectbox("Categoria", ["Garçon", "Cozinheiro", "Caixa"])
            tel = st.text_input("Telefone")
            bi = st.text_input("BI")
            if st.form_submit_button("Registar") and cc and nc:
                novo_rh = pd.DataFrame([[cc, nc, cat_func, tel, bi]], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                st.session_state.rh = pd.concat([st.session_state.rh, novo_rh], ignore_index=True)
                st.success("Colaborador registado!")
        st.dataframe(st.session_state.rh, use_container_width=True)


# ==========================================
# ROTEADOR PRINCIPAL
# ==========================================
if mesa_detectada and 1 <= mesa_detectada <= 30:
    area_cliente()
elif perfil_url == "caixa" or menu_selecionado == "💻 Caixa & Gestão de Mesas":
    area_caixa()
elif perfil_url == "cozinha" or menu_selecionado == "🍳 Cozinha (Chef)":
    area_cozinha()
elif menu_selecionado == "👨‍🍳 Garçon":
    area_garcon()
elif menu_selecionado == "👑 Administrador":
    area_administrador()
else:
    area_administrador()
