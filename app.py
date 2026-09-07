import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO

# Configuração da Página
st.set_page_config(
    page_title="Sistema de Gestão - Restaurante",
    page_icon="🍽️",
    layout="wide"
)

# Estilo CSS para Alertas Piscantes
st.markdown("""
    <style>
    @keyframes piscar-mesa {
        0% { background-color: #ff4b4b; color: white; transform: scale(1); }
        50% { background-color: #ffe6e6; color: black; transform: scale(1.03); }
        100% { background-color: #ff4b4b; color: white; transform: scale(1); }
    }
    .mesa-alerta {
        animation: piscar-mesa 1s infinite;
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

# Inicialização de Estados da Sessão
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

# Função para Gerar QR Code
def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

query_params = st.query_params
mesa_qr = query_params.get("mesa", None)

# Menu Lateral de Navegação
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("Restaurante Gestão")

menu_opcoes = [
    "📱 Cliente / QR Code (Mesa)", 
    "👨‍🍳 Garçon / Pedidos", 
    "💻 Caixa Central (Gestão Total)", 
    "👑 Administrador (Stock / QR Codes)",
    "👥 Recursos Humanos (DCH)"
]

menu = st.sidebar.selectbox("Navegação:", menu_opcoes)

# 1. CLIENTE (QR CODE DA MESA)
if menu == "📱 Cliente / QR Code (Mesa)" or mesa_qr:
    st.title("📱 Bem-vindo ao Nosso Restaurante 🍽️")
    
    if mesa_qr and str(mesa_qr).isdigit():
        num_mesa = int(mesa_qr)
        if not (1 <= num_mesa <= 30):
            num_mesa = 1
    else:
        num_mesa = st.selectbox("Selecione a sua Mesa:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
    
    st.info(f"📍 Está conectado à **Mesa {num_mesa}**.")
    
    if num_mesa not in st.session_state.clientes_mesa:
        st.subheader("📝 Registo de Acolhimento do Cliente")
        with st.form(f"form_cliente_{num_mesa}"):
            nome_cli = st.text_input("Nome Completo:")
            tel_cli = st.text_input("Número de Telefone / WhatsApp:")
            whatsapp_opt = st.checkbox("Deseja fazer parte do Grupo de WhatsApp do Restaurante?")
            
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
        st.success(f"Olá, **{cli['nome']}**! Mesa {num_mesa} ativa.")
        
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo", "🎉 Eventos"])
        
        with tab_menu:
            if not st.session_state.stock.empty:
                opcoes = st.session_state.stock['Produto'].tolist()
                item_escolhido = st.selectbox("Escolha o Item:", opcoes)
                
                row_prod = st.session_state.stock[st.session_state.stock['Produto'] == item_escolhido].iloc[0]
                tipo_item = row_prod['Categoria']
                preco_item = row_prod['Preço Unitário']
                
                qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
                obs = st.text_input("Observações (ex: Sem gelo):")
                
                if st.button("Enviar Pedido"):
                    st.session_state.mesas[num_mesa]["status"] = "Aberta"
                    
                    novo_pedido = {
                        "item": item_escolhido,
                        "tipo": tipo_item,
                        "quantidade": qtd,
                        "preco": preco_item,
                        "origem": f"Cliente ({cli['nome']})",
                        "obs": obs,
                        "status": "Pendente",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[num_mesa]["pedidos"].append(novo_pedido)
                    st.success("🎉 Pedido enviado com sucesso!")
                    st.balloons()
            else:
                st.warning("Cardápio indisponível.")
                
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
                    estado_txt = f"✅ {p['status']}" if p['status'] == "Confirmado" else (f"❌ {p['status']}" if p['status'] == "Anulado" else f"⏳ {p['status']}")
                    st.write(f"- **{p['quantidade']}x {p['item']}** ({p['tipo']}) | Preço: {p['preco']:,.2f} Kz | Subtotal: {total_item:,.2f} Kz | Estado: {estado_txt}")
                st.divider()
                st.markdown(f"### Total Consumido: **{subtotal_geral:,.2f} Kz**")
                
        with tab_eventos:
            st.subheader("🎵 Programação de Eventos")
            st.markdown("""
            * **Sexta-Feira de Serão:** Música ao vivo a partir das 20h.
            * **Sábado de Karaoke:** Com o Grupo FF Karaoke!
            * **Domingo em Família:** Almoços especiais e cinema comunitário.
            """)

# 2. GARÇON
elif menu == "👨‍🍳 Garçon / Pedidos":
    st.title("👨‍🍳 Painel do Garçon (Validação por Código DCH)")
    
    codigo_garcon = st.text_input("Insira o seu Código de Colaborador (DCH):", type="password")
    
    if codigo_garcon:
        validar_colab = st.session_state.rh[st.session_state.rh['Código'] == codigo_garcon]
        
        if validar_colab.empty:
            st.error("❌ Código de colaborador inválido ou não registado.")
        else:
            nome_g = validar_colab.iloc[0]['Nome']
            cat_g = validar_colab.iloc[0]['Categoria']
            st.success(f"✅ Colaborador validado: **{nome_g}** ({cat_g})")
            
            mesa_garcon = st.selectbox("Selecione a Mesa:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
            
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
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[mesa_garcon]["pedidos"].append(novo_pedido)
                    st.success(f"Pedido registado para a Mesa {mesa_garcon}!")

# 3. CAIXA CENTRAL (GESTÃO TOTAL VIA "GERIR MESA")
elif menu == "💻 Caixa Central (Gestão Total)":
    
    # Se existe uma mesa ativa selecionada, mostramos exclusivamente o painel de gestão detalhado dessa mesa
    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        
        if st.button("⬅️ Voltar à Visão Geral das Mesas"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Painel de Gestão Completo da Mesa {m_ativa}")
        
        dados_mesa = st.session_state.mesas[m_ativa]
        
        # Estado e Abertura / Fecho
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

        # Adicionar Pedido Diretamente pelo Caixa
        with st.expander("➕ Adicionar Novo Pedido a esta Mesa"):
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
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.mesas[m_ativa]["status"] = "Aberta"
                    st.session_state.mesas[m_ativa]["pedidos"].append(novo_ped_cx)
                    st.session_state.mesas[m_ativa]["total"] += (qtd_cx * row_p_cx['Preço Unitário'])
                    st.success("Pedido adicionado e confirmado com sucesso!")
                    st.rerun()

        # Histórico de Consumo e Controlo de Pedidos
        st.subheader("🛍️ Histórico de Consumo e Controlo de Pedidos")
        if not dados_mesa["pedidos"]:
            st.info("Nenhum pedido registado nesta mesa até o momento.")
        else:
            for idx, ped in enumerate(dados_mesa["pedidos"]):
                col_d1, col_d2, col_d3, col_d4 = st.columns([3, 2, 2, 2])
                with col_d1:
                    st.write(f"**{ped['quantidade']}x {ped['item']}** ({ped['tipo']})")
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
            
            # Fecho da Conta / Liquidação Total
            if st.button("🔓 Fechar Conta / Liquidar Fatura da Mesa", type="primary"):
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                if m_ativa in st.session_state.clientes_mesa:
                    del st.session_state.clientes_mesa[m_ativa]
                st.success(f"Mesa {m_ativa} fechada e conta liquidada com sucesso!")
                st.rerun()

    else:
        # Visão Geral das 30 Mesas
        st.title("💻 Caixa Central - Controlo das 30 Mesas")
        st.info("As mesas com novos pedidos piscam a vermelho. Clique em 'Gerir Mesa' para abrir o menu dedicado dessa mesa.")
        
        cols = st.columns(6)
        for i in range(1, 31):
            mesa_info = st.session_state.mesas[i]
            tem_pendentes = any(p["status"] == "Pendente" for p in mesa_info["pedidos"])
            
            with cols[(i - 1) % 6]:
                if tem_pendentes:
                    st.markdown(f'<div class="mesa-alerta">MESA {i}<br>🔔 NOVO PEDIDO!</div>', unsafe_allow_html=True)
                elif mesa_info["status"] == "Aberta":
                    st.markdown(f'<div class="mesa-aberta">Mesa {i}<br>Aberta ({mesa_info["total"]:,.2f} Kz)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="mesa-fechada">Mesa {i}<br>Fechada</div>', unsafe_allow_html=True)
                    
                if st.button(f"Gerir Mesa {i}", key=f"btn_m_{i}p"):
                    st.session_state.mesa_ativa = i
                    st.rerun()

# 4. ADMINISTRADOR (STOCK / QR CODES)
elif menu == "👑 Administrador (Stock / QR Codes)":
    st.title("👑 Painel do Administrador - Geração de QR Codes e Stock")
    st.info("Gere os QR Codes das 30 mesas e controle o armazém.")
    
    url_base = st.text_input("URL base da Aplicação (ex: http://192.168.X.X:8501 ou link do Streamlit Cloud)", "http://localhost:8501")
    
    cols_qr = st.columns(3)
    for i in range(1, 31):
        link_mesa = f"{url_base}/?mesa={i}"
        with cols_qr[(i - 1) % 3]:
            st.markdown(f"**Mesa {i}**")
            st.code(link_mesa, language="text")
            img_bytes = gerar_qrcode_bytes(link_mesa)
            st.image(img_bytes, width=140, caption=f"QR Code Mesa {i}")
            st.divider()

    st.subheader("📦 Gestão de Stock (Armazém)")
    with st.form("form_reg_stock"):
        st.write("Registar Novo Produto")
        novo_prod = st.text_input("Nome do Produto")
        cat_prod = st.selectbox("Categoria", ["Bebidas", "Alimentos", "Outros"])
        qtd_prod = st.number_input("Quantidade em Stock", min_value=0, step=1)
        preco_prod = st.number_input("Preço Unitário (Kz)", min_value=0.0, format="%.2f")
        
        btn_add = st.form_submit_button("Salvar no Stock")
        if btn_add and novo_prod:
            item_df = pd.DataFrame([[novo_prod, cat_prod, qtd_prod, preco_prod]], 
                                   columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
            st.session_state.stock = pd.concat([st.session_state.stock, item_df], ignore_index=True)
            st.success(f"Produto '{novo_prod}' adicionado!")
            
    st.dataframe(st.session_state.stock, use_container_width=True)

# 5. RECURSOS HUMANOS (DCH)
elif menu == "👥 Recursos Humanos (DCH)":
    st.title("👥 Gestão de Recursos Humanos (DCH)")
    st.info("Registo de colaboradores e garçons com código único.")
    
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
            st.success(f"Colaborador {nome_colab} registado!")
            
    st.dataframe(st.session_state.rh, use_container_width=True)
