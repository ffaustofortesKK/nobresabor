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

# Estilo CSS para Alertas e Animações das Mesas
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
        ["Frango à Grega", "Alimentos", 20, 3500.0],
        ["Bife a Cavalo", "Alimentos", 15, 4000.0]
    ], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

if "rh" not in st.session_state:
    st.session_state.rh = pd.DataFrame([
        ["G001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042"],
        ["G002", "Ana Paula", "Garçon", "912333444", "009876543LA031"]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])

if "clientes_mesa" not in st.session_state:
    st.session_state.clientes_mesa = {}

# Função Auxiliar para Gerar QR Code
def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# ==========================================
# 2. CAPTURA AUTOMÁTICA DA MESA VIA URL / QR CODE
# ==========================================
query_params = st.query_params
mesa_detectada = None

if "mesa" in query_params:
    try:
        mesa_detectada = int(query_params.get("mesa"))
    except:
        pass

if not mesa_detectada and "path" in query_params:
    path_val = query_params.get("path", "")
    if "mesa" in path_val:
        try:
            partes = path_val.split("mesa")
            num_str = partes[1].split("/")[0]
            mesa_detectada = int(num_str)
        except:
            pass


# ==========================================
# 3. MENU LATERAL E ROTEAMENTO INTELIGENTE
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("NobreSabor - Gestão")

if mesa_detectada and 1 <= mesa_detectada <= 30:
    st.sidebar.success(f"📱 Atendimento Digital (Mesa {mesa_detectada})")
    menu_selecionado = "📱 Cliente"
else:
    menu_opcoes = [
        "💻 Caixa & Gestão de Mesas", 
        "🍳 Cozinha (Chef)",
        "👨‍🍳 Garçon", 
        "👑 Administrador",
        "📱 Cliente (Manual)"
    ]
    menu_selecionado = st.sidebar.selectbox("Selecione a Área:", menu_opcoes)


# ==========================================
# ÁREA: CLIENTE (AUTOMATIZADO POR QR CODE)
# ==========================================
def area_cliente():
    if mesa_detectada and 1 <= mesa_detectada <= 30:
        num_mesa = mesa_detectada
    else:
        num_mesa = st.selectbox("Selecione a sua Mesa:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
    
    st.title(f"📱 NobreSabor - Atendimento Digital | Mesa {num_mesa} 🍽️")
    st.info(f"📍 Conexão direta estabelecida com sucesso para a **Mesa {num_mesa}**.")
    
    if num_mesa not in st.session_state.clientes_mesa:
        st.subheader("📝 Registo Inicial do Cliente")
        with st.form(f"form_cli_{num_mesa}"):
            nome_cli = st.text_input("Nome Completo:")
            tel_cli = st.text_input("Número de Telefone / WhatsApp:")
            whatsapp_opt = st.checkbox("Deseja participar do Grupo de WhatsApp do Restaurante?")
            
            btn_reg = st.form_submit_button("Entrar e Ver Menu")
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
        st.success(f"Bem-vindo, **{cli['nome']}**! A sua mesa está pronta a receber pedidos.")
        
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo", "🎉 Eventos"])
        
        with tab_menu:
            if not st.session_state.stock.empty:
                opcoes = st.session_state.stock['Produto'].tolist()
                item_escolhido = st.selectbox("Escolha o Item do Cardápio:", opcoes)
                
                row_prod = st.session_state.stock[st.session_state.stock['Produto'] == item_escolhido].iloc[0]
                tipo_item = row_prod['Categoria']
                preco_item = row_prod['Preço Unitário']
                
                qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
                obs = st.text_input("Observações (ex: Sem gelo, carne bem passada):")
                
                if st.button("🚀 Enviar Pedido para o Caixa / Cozinha"):
                    st.session_state.mesas[num_mesa]["status"] = "Aberta"
                    novo_pedido = {
                        "item": item_escolhido,
                        "tipo": tipo_item,
                        "quantidade": qtd,
                        "preco": preco_item,
                        "origem": f"Cliente ({cli['nome']})",
                        "obs": obs,
                        "status": "Pendente",
                        "cozinha_status": "Pendente" if tipo_item == "Alimentos" else "N/A",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[num_mesa]["pedidos"].append(novo_pedido)
                    st.success("🎉 Pedido enviado com sucesso!")
                    st.balloons()
            else:
                st.warning("Cardápio indisponível no momento.")
                
        with tab_consumo:
            st.subheader("📊 Controlo do seu Consumo Atual")
            pedidos_mesa = st.session_state.mesas[num_mesa]["pedidos"]
            if not pedidos_mesa:
                st.info("Ainda não tem pedidos registados.")
            else:
                subtotal_geral = 0
                for p in pedidos_mesa:
                    total_item = p['quantidade'] * p['preco']
                    if p['status'] != "Anulado":
                        subtotal_geral += total_item
                    
                    estado_extra = ""
                    if p['tipo'] == "Alimentos":
                        if p.get('cozinha_status') == "Pronto":
                            estado_extra = " | 🍲 Prato Pronto!"
                        else:
                            estado_extra = " | 🍳 Na Cozinha..."
                            
                    estado_txt = f"✅ {p['status']}{estado_extra}" if p['status'] == "Confirmado" else (f"❌ {p['status']}" if p['status'] == "Anulado" else f"⏳ {p['status']}")
                    st.write(f"- **{p['quantidade']}x {p['item']}** ({p['tipo']}) | Preço: {p['preco']:,.2f} Kz | Subtotal: {total_item:,.2f} Kz | Estado: {estado_txt}")
                st.divider()
                st.markdown(f"### Total Consumido: **{subtotal_geral:,.2f} Kz**")
                
        with tab_eventos:
            st.subheader("🎵 Programação de Eventos - NobreSabor")
            st.markdown("""
            * **Sexta-Feira de Serão:** Música ao vivo a partir das 20h.
            * **Sábado de Karaoke:** Com o Grupo FF Karaoke!
            * **Domingo em Família:** Almoços especiais e cinema comunitário.
            """)


# ==========================================
# ÁREA: COZINHA (CHEF)
# ==========================================
def area_cozinha():
    st.title("🍳 Área da Cozinha - Gestão de Pratos")
    st.info("Aqui o Chefe de Cozinha visualiza todos os pedidos de alimentos pendentes, prepara e clica em 'Pronto' para avisar o Caixa.")
    
    tem_pedidos_cozinha = False
    
    for i in range(1, 31):
        dados_m = st.session_state.mesas[i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            if ped["tipo"] == "Alimentos" and ped["status"] != "Anulado" and ped.get("cozinha_status", "Pendente") == "Pendente":
                tem_pedidos_cozinha = True
                col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
                with col_c1:
                    st.write(f"### 🍽️ Mesa {i}")
                    st.write(f"**Item:** {ped['quantidade']}x {ped['item']}")
                    st.write(f"Observações: _{ped['obs']}_ | ⏰ {ped['hora']}")
                with col_c2:
                    st.write(f"Estado Atual: **Em Preparação**")
                with col_c3:
                    if st.button(f"✅ Prato Pronto (Mesa {i} - #{idx_p})", key=f"btn_prato_pronto_{i}_{idx_p}"):
                        st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Pronto"
                        st.success(f"Pronto assinalado para a Mesa {i}!")
                        st.rerun()
                st.divider()
                
    if not tem_pedidos_cozinha:
        st.success("🎉 Não há pratos pendentes na cozinha de momento!")


# ==========================================
# ÁREA: GARÇON
# ==========================================
def area_garcon():
    st.title("👨‍🍳 Área do Garçon - Lançamento de Pedidos")
    codigo_garcon = st.text_input("Insira o seu Código de Colaborador (DCH):", type="password")
    
    if codigo_garcon:
        validar_colab = st.session_state.rh[st.session_state.rh['Código'] == codigo_garcon]
        
        if validar_colab.empty:
            st.error("❌ Código de colaborador inválido ou não registado.")
        else:
            nome_g = validar_colab.iloc[0]['Nome']
            cat_g = validar_colab.iloc[0]['Categoria']
            st.success(f"✅ Colaborador validado: **{nome_g}** ({cat_g})")
            
            mesa_garcon = st.selectbox("Selecione a Mesa de Destino:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
            
            if not st.session_state.stock.empty:
                opcoes = st.session_state.stock['Produto'].tolist()
                item_g = st.selectbox("Item solicitado:", opcoes)
                
                row_prod = st.session_state.stock[st.session_state.stock['Produto'] == item_g].iloc[0]
                tipo_item = row_prod['Categoria']
                preco_item = row_prod['Preço Unitário']
                
                qtd_g = st.number_input("Quantidade:", min_value=1, value=1, step=1, key="qtd_g")
                obs_g = st.text_input("Observações:", key="obs_g")
                
                if st.button("Registar Pedido na Mesa"):
                    st.session_state.mesas[mesa_garcon]["status"] = "Aberta"
                    novo_pedido = {
                        "item": item_g,
                        "tipo": tipo_item,
                        "quantidade": qtd_g,
                        "preco": preco_item,
                        "origem": f"Garçon ({nome_g})",
                        "obs": obs_g,
                        "status": "Pendente",
                        "cozinha_status": "Pendente" if tipo_item == "Alimentos" else "N/A",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[mesa_garcon]["pedidos"].append(novo_pedido)
                    st.success(f"Pedido lançado com sucesso para a Mesa {mesa_garcon}!")


# ==========================================
# ÁREA: CAIXA & GESTÃO DE MESAS
# ==========================================
def area_caixa():
    st.title("💻 Caixa - Controlo Geral e Mesas")
    
    # Controlo de Abertura/Fecho do Caixa
    col_cx_st1, col_cx_st2 = st.columns([3, 1])
    with col_cx_st1:
        if st.session_state.caixa_aberto:
            st.success("🟢 CAIXA ABERTO E OPERACIONAL")
        else:
            st.error("🔴 CAIXA FECHADO PELO ADMINISTRADOR")
            st.warning("O Administrador é quem abre e fecha o caixa. Contacte a administração se necessário.")
            return
    
    st.divider()

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        
        if st.button("⬅️ Voltar à Visão Geral das Mesas"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Caixa - Gestão Detalhada da Mesa {m_ativa}")
        
        dados_mesa = st.session_state.mesas[m_ativa]
        
        col_st1, col_st2 = st.columns([2, 2])
        with col_st1:
            st.write(f"**Estado Atual:** {dados_mesa['status']} | **Total da Conta:** **{dados_mesa['total']:,.2f} Kz**")
        with col_st2:
            if dados_mesa['status'] == "Fechada":
                if st.button(f"🟢 Abrir Mesa {m_ativa} Manualmente"):
                    st.session_state.mesas[m_ativa]["status"] = "Aberta"
                    st.success(f"Mesa {m_ativa} aberta com sucesso!")
                    st.rerun()
            else:
                if st.button(f"🔴 Fechar / Bloquear Mesa {m_ativa}"):
                    st.session_state.mesas[m_ativa]["status"] = "Fechada"
                    st.rerun()

        st.divider()

        with st.expander("➕ Adicionar Novo Pedido Manualmente a esta Mesa"):
            if not st.session_state.stock.empty:
                prod_cx = st.selectbox("Selecione o Produto:", st.session_state.stock['Produto'].tolist(), key=f"prod_cx_{m_ativa}")
                row_p_cx = st.session_state.stock[st.session_state.stock['Produto'] == prod_cx].iloc[0]
                qtd_cx = st.number_input("Quantidade:", min_value=1, value=1, step=1, key=f"qtd_cx_{m_ativa}")
                obs_cx = st.text_input("Observações (opcional):", key=f"obs_cx_{m_ativa}")
                
                if st.button("Lançar Pedido na Mesa", key=f"btn_lanca_cx_{m_ativa}"):
                    novo_ped_cx = {
                        "item": prod_cx,
                        "tipo": row_p_cx['Categoria'],
                        "quantidade": qtd_cx,
                        "preco": row_p_cx['Preço Unitário'],
                        "origem": "Caixa",
                        "obs": obs_cx,
                        "status": "Confirmado",
                        "cozinha_status": "Pronto" if row_p_cx['Categoria'] == "Alimentos" else "N/A",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[m_ativa]["status"] = "Aberta"
                    st.session_state.mesas[m_ativa]["pedidos"].append(novo_ped_cx)
                    st.session_state.mesas[m_ativa]["total"] += (qtd_cx * row_p_cx['Preço Unitário'])
                    st.success("Pedido adicionado e confirmado com sucesso!")
                    st.rerun()

        st.subheader("🛍️ Histórico de Consumo e Controlo de Pedidos")
        if not dados_mesa["pedidos"]:
            st.info("Nenhum pedido registado nesta mesa até o momento.")
        else:
            for idx, ped in enumerate(dados_mesa["pedidos"]):
                col_d1, col_d2, col_d3, col_d4 = st.columns([3, 2, 2, 2])
                with col_d1:
                    status_cozinha_txt = f" | 🍲 Prato Pronto!" if ped.get('cozinha_status') == "Pronto" else (" | 🍳 Na Cozinha..." if ped['tipo'] == "Alimentos" else "")
                    st.write(f"**{ped['quantidade']}x {ped['item']}** ({ped['tipo']}){status_cozinha_txt}")
                    st.write(f"Origem: _{ped['origem']}_ | Obs: {ped['obs']} | ⏰ {ped['hora']}")
                with col_d2:
                    st.write(f"Estado: **{ped['status']}**")
                    st.write(f"Subtotal: {ped['quantidade'] * ped['preco']:,.2f} Kz")
                with col_d3:
                    if ped["status"] == "Pendente":
                        if st.button(f"Confirmar #{idx}", key=f"conf_ped_{m_ativa}_{idx}"):
                            if ped["tipo"] == "Bebidas":
                                idx_st = st.session_state.stock[st.session_state.stock['Produto'] == ped['item']].index
                                if not idx_st.empty:
                                    qtd_atual = st.session_state.stock.at[idx_st[0], 'Quantidade']
                                    if qtd_atual >= ped['quantidade']:
                                        st.session_state.stock.at[idx_st[0], 'Quantidade'] = qtd_atual - ped['quantidade']
                                    else:
                                        st.error("⚠️ Stock insuficiente de bebidas!")
                                        continue
                            
                            st.session_state.mesas[m_ativa]["pedidos"][idx]["status"] = "Confirmado"
                            st.session_state.mesas[m_ativa]["total"] += (ped['quantidade'] * ped['preco'])
                            st.success("Pedido confirmado!")
                            st.rerun()
                with col_d4:
                    if ped["status"] != "Anulado":
                        if st.button(f"❌ Anular #{idx}", key=f"anular_ped_{m_ativa}_{idx}"):
                            if ped["status"] == "Confirmado":
                                st.session_state.mesas[m_ativa]["total"] -= (ped['quantidade'] * ped['preco'])
                            st.session_state.mesas[m_ativa]["pedidos"][idx]["status"] = "Anulado"
                            st.warning("Pedido anulado.")
                            st.rerun()
            
            st.divider()
            if st.button("🔓 Fechar Conta / Liquidar Fatura da Mesa", type="primary"):
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                if m_ativa in st.session_state.clientes_mesa:
                    del st.session_state.clientes_mesa[m_ativa]
                st.success(f"Mesa {m_ativa} fechada e conta liquidada com sucesso!")
                st.rerun()

    else:
        st.info("As mesas com novos pedidos piscam a vermelho. As mesas com pratos prontos na cozinha piscam com o emoji 🍲 a avisar o caixa.")
        
        cols = st.columns(6)
        for i in range(1, 31):
            mesa_info = st.session_state.mesas[i]
            tem_pendentes = any(p["status"] == "Pendente" for p in mesa_info["pedidos"])
            tem_prato_pronto = any(p.get("cozinha_status") == "Pronto" and p["status"] == "Confirmado" for p in mesa_info["pedidos"])
            
            with cols[(i - 1) % 6]:
                if tem_prato_pronto:
                    st.markdown(f'<div class="mesa-pronta">MESA {i}<br>🍲 PRATO PRONTO!</div>', unsafe_allow_html=True)
                elif tem_pendentes:
                    st.markdown(f'<div class="mesa-alerta">MESA {i}<br>🔔 NOVO PEDIDO!</div>', unsafe_allow_html=True)
                elif mesa_info["status"] == "Aberta":
                    st.markdown(f'<div class="mesa-aberta">Mesa {i}<br>Aberta ({mesa_info["total"]:,.2f} Kz)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="mesa-fechada">Mesa {i}<br>Fechada</div>', unsafe_allow_html=True)
                    
                if st.button(f"Gerir Mesa {i}", key=f"btn_m_{i}p"):
                    st.session_state.mesa_ativa = i
                    st.rerun()


# ==========================================
# ÁREA: ADMINISTRADOR (CAIXA, STOCK, DRH, QR CODES)
# ==========================================
def area_administrador():
    st.title("👑 Painel do Administrador")
    st.info("Aqui controla a abertura/fecho do Caixa, faz o registo de stock, gere o DRH e extrai os QR codes individuais de cada mesa.")
    
    tab_adm_cx, tab_adm_stock, tab_adm_drh, tab_adm_qr = st.tabs(["💰 Controlo de Caixa", "📦 Stock", "👥 Recursos Humanos", "📷 QR Codes das Mesas"])
    
    with tab_adm_cx:
        st.subheader("Gestão do Estado do Caixa")
        if st.session_state.caixa_aberto:
            st.success("O Caixa encontra-se atualmente **ABERTO**.")
            if st.button("🔴 Fechar o Caixa"):
                st.session_state.caixa_aberto = False
                st.success("Caixa fechado com sucesso!")
                st.rerun()
        else:
            st.error("O Caixa encontra-se atualmente **FECHADO**.")
            if st.button("🟢 Abrir o Caixa"):
                st.session_state.caixa_aberto = True
                st.success("Caixa aberto com sucesso!")
                st.rerun()
                
    with tab_adm_stock:
        st.subheader("Gestão de Armazém e Stock")
        with st.form("form_reg_stock"):
            novo_prod = st.text_input("Nome do Produto")
            cat_prod = st.selectbox("Categoria", ["Bebidas", "Alimentos", "Outros"])
            qtd_prod = st.number_input("Quantidade em Stock", min_value=0, step=1)
            preco_prod = st.number_input("Preço Unitário (Kz)", min_value=0.0, format="%.2f")
            
            btn_add = st.form_submit_button("Salvar no Stock")
            if btn_add and novo_prod:
                item_df = pd.DataFrame([[novo_prod, cat_prod, qtd_prod, preco_prod]], 
                                       columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                st.session_state.stock = pd.concat([st.session_state.stock, item_df], ignore_index=True)
                st.success(f"Produto '{novo_prod}' adicionado com sucesso!")
                
        st.dataframe(st.session_state.stock, use_container_width=True)
        
    with tab_adm_drh:
        st.subheader("Gestão de Recursos Humanos (DRH)")
        with st.form("form_dch"):
            cod_colab = st.text_input("Código do Colaborador (ex: G003)")
            nome_colab = st.text_input("Nome Completo")
            cat_colab = st.selectbox("Categoria", ["Garçon", "Cozinheiro", "Chefe de Sala", "Limpeza", "Comprador"])
            tel_colab = st.text_input("Telefone")
            bi_colab = st.text_input("Número do B.I.")
            
            btn_salvar_dch = st.form_submit_button("Registar Colaborador")
            if btn_salvar_dch and cod_colab and nome_colab:
                novo_func = pd.DataFrame([[cod_colab, nome_colab, cat_colab, tel_colab, bi_colab]], 
                                         columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                st.session_state.rh = pd.concat([st.session_state.rh, novo_func], ignore_index=True)
                st.success(f"Colaborador {nome_colab} registado com sucesso!")
                
        st.dataframe(st.session_state.rh, use_container_width=True)
        
    with tab_adm_qr:
        st.subheader("Gerador de QR Codes por Mesa")
        dominio_base = st.text_input("Domínio / URL base do Sistema (ex: http://localhost:8501)", "http://localhost:8501")
        mesa_selecionada_adm = st.selectbox("Selecione a Mesa para obter o QR Code Individual:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
        
        st.divider()
        col_det1, col_det2 = st.columns([2, 1])
        link_mesa_limpo = f"{dominio_base.rstrip('/')}/cliente/mesa{mesa_selecionada_adm}/qr"
        link_qrcode_executavel = f"{dominio_base.rstrip('/')}/?mesa={mesa_selecionada_adm}"
        
        with col_det1:
            st.write("Copie o link amigável para configurar nas placas de mesa:")
            st.code(link_mesa_limpo, language="text")
            st.write("Link direto de execução no sistema:")
            st.code(link_qrcode_executavel, language="text")
            
        with col_det2:
            img_bytes = gerar_qrcode_bytes(link_qrcode_executavel)
            st.image(img_bytes, width=180, caption=f"QR Code Oficial - Mesa {mesa_selecionada_adm}")
            st.download_button(
                label=f"📥 Descarregar QR Code Mesa {mesa_selecionada_adm}",
                data=img_bytes,
                file_name=f"qrcode_mesa_{mesa_selecionada_adm}.png",
                mime="image/png"
            )


# ==========================================
# EXECUÇÃO DO ROTEADOR PRINCIPAL
# ==========================================
if menu_selecionado == "📱 Cliente" or mesa_detectada:
    area_cliente()
elif menu_selecionado == "💻 Caixa & Gestão de Mesas":
    area_caixa()
elif menu_selecionado == "🍳 Cozinha (Chef)":
    area_cozinha()
elif menu_selecionado == "👨‍🍳 Garçon":
    area_garcon()
elif menu_selecionado == "👑 Administrador":
    area_administrador()
else:
    area_cliente()
