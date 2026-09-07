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

# URL Oficial do Sistema
URL_OFICIAL = "https://nobresabor.streamlit.app"

# Função Auxiliar para Gerar QR Code em Bytes
def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# ==========================================
# 2. CAPTURA ROBUSTA DOS PARÂMETROS DA URL
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
# 3. MENU LATERAL E ROTEAMENTO INTELIGENTE
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
    # Por padrão, abre no Administrador para gerar os links e controlar o sistema
    menu_opcoes = [
        "👑 Administrador",
        "💻 Caixa & Gestão de Mesas", 
        "🍳 Cozinha (Chef)",
        "👨‍🍳 Garçon"
    ]
    menu_selecionado = st.sidebar.selectbox("Selecione a Área:", menu_opcoes)


# ==========================================
# ÁREA: CLIENTE (AUTOMATIZADO POR QR CODE)
# ==========================================
def area_cliente():
    num_mesa = mesa_detectada if (mesa_detectada and 1 <= mesa_detectada <= 30) else 1
    
    if num_mesa not in st.session_state.clientes_mesa:
        st.markdown("<h1 style='text-align: center;'>🍽️ Bem-vindo ao Restaurante Nobre Sabor</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: gray;'>Faça o seu registo - Mesa {num_mesa}</h3>", unsafe_allow_html=True)
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
        st.success(f"Bem-vindo, **{cli['nome']}**! A sua mesa está aberta e pronta a receber pedidos.")
        
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
                    st.success("🎉 Pedido enviado com sucesso para a cozinha/caixa!")
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
                    if p['status'] != "Anulado" and p['status'] != "Recusado pela Cozinha":
                        subtotal_geral += total_item
                    
                    estado_txt = p['status']
                    if p.get('cozinha_status') == "Aprovado":
                        estado_txt = "✅ Aprovado pela Cozinha"
                    elif p.get('cozinha_status') == "Recusado":
                        estado_txt = "❌ Recusado (Esgotado)"
                        
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
# ÁREA: COZINHA (CHEF) - COM APROVAÇÃO E RECUSA
# ==========================================
def area_cozinha():
    st.title("🍳 Área da Cozinha - Gestão de Pratos")
    st.info("A cozinha recebe os pedidos de alimentos. Pode Aprovar (se houver stock) ou Recusar (se a refeição estiver esgotada, notificando o caixa).")
    
    tem_pedidos_cozinha = False
    
    for i in range(1, 31):
        dados_m = st.session_state.mesas[i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            if ped["tipo"] == "Alimentos" and ped["status"] != "Anulado" and ped.get("cozinha_status", "Pendente") == "Pendente":
                tem_pedidos_cozinha = True
                col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                with col_c1:
                    st.write(f"### 🍽️ Mesa {i}")
                    st.write(f"**Prato:** {ped['quantidade']}x {ped['item']}")
                    st.write(f"Observações: _{ped['obs']}_ | ⏰ {ped['hora']}")
                with col_c2:
                    st.write("Estado: **Aguardando Avaliação ⏳**")
                with col_c3:
                    if st.button(f"✅ Aprovar Prato", key=f"aprovar_cz_{i}_{idx_p}"):
                        st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                        st.session_state.mesas[i]["pedidos"][idx_p]["status"] = "Confirmado"
                        # Soma ao total da mesa
                        st.session_state.mesas[i]["total"] += (ped['quantidade'] * ped['preco'])
                        st.success(f"Prato aprovado para a Mesa {i}!")
                        st.rerun()
                    if st.button(f"❌ Recusar (Esgotado)", key=f"recusar_cz_{i}_{idx_p}"):
                        st.session_state.mesas[i]["pedidos"][idx_p]["cozinha_status"] = "Recusado"
                        st.session_state.mesas[i]["pedidos"][idx_p]["status"] = "Recusado pela Cozinha"
                        st.warning(f"Pedido recusado e notificação enviada ao caixa!")
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
# ÁREA: CAIXA & GESTÃO DE MESAS (COM QR CODES E ALERTAS DE RECUSA)
# ==========================================
def area_caixa():
    st.title("💻 Caixa - Controlo Geral e Mesas")
    
    if not st.session_state.caixa_aberto:
        st.error("🔴 O CAIXA ENCONTRA-SE ATUALMENTE FECHADO.")
        st.warning("O Administrador é o responsável por abrir e fechar o caixa no painel administrativo.")
        return
    else:
        st.success("🟢 Caixa Aberto e Operacional")

    st.divider()

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        
        if st.button("⬅️ Voltar à Visão Geral das Mesas"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Caixa - Gestão Detalhada da Mesa {m_ativa}")
        
        dados_mesa = st.session_state.mesas[m_ativa]
        
        # Secção com o Link e QR Code Integrado
        with st.expander(f"📷 Código QR e Link Direto da Mesa {m_ativa} (Para Impressão)", expanded=True):
            link_mesa = f"{URL_OFICIAL}/?mesa={m_ativa}"
            
            col_qr1, col_qr2 = st.columns([2, 1])
            with col_qr1:
                st.write("Link direto para esta mesa:")
                st.code(link_mesa, language="text")
                if m_ativa in st.session_state.clientes_mesa:
                    cli_atual = st.session_state.clientes_mesa[m_ativa]
                    st.info(f"👤 **Cliente Registado:** {cli_atual['nome']} | 📞 {cli_atual['telefone']} | Grupo WhatsApp: {'Sim ✅' if cli_atual['whatsapp'] else 'Não ❌'}")
                else:
                    st.warning("👤 Nenhum cliente registado nesta mesa ainda (aguardando leitura do QR code).")
            with col_qr2:
                img_bytes = gerar_qrcode_bytes(link_mesa)
                st.image(img_bytes, width=150, caption=f"QR Code Oficial - Mesa {m_ativa}")
                st.download_button(
                    label=f"📥 Baixar QR Mesa {m_ativa}",
                    data=img_bytes,
                    file_name=f"qrcode_mesa_{m_ativa}.png",
                    mime="image/png",
                    key=f"down_qr_{m_ativa}"
                )

        st.divider()

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
                    if m_ativa in st.session_state.clientes_mesa:
                        del st.session_state.clientes_mesa[m_ativa]
                    st.rerun()

        st.divider()

        st.subheader("🛍️ Histórico de Consumo e Controlo de Pedidos")
        if not dados_mesa["pedidos"]:
            st.info("Nenhum pedido registado nesta mesa até o momento.")
        else:
            for idx, ped in enumerate(dados_mesa["pedidos"]):
                col_d1, col_d2, col_d3 = st.columns([3, 2, 2])
                with col_d1:
                    st.write(f"**{ped['quantidade']}x {ped['item']}** ({ped['tipo']})")
                    st.write(f"Origem: _{ped['origem']}_ | Obs: {ped['obs']} | ⏰ {ped['hora']}")
                with col_d2:
                    st.write(f"Estado: **{ped['status']}**")
                    if ped.get('cozinha_status') == "Recusado":
                        st.error("⚠️ Recusado pela Cozinha: Esgotado!")
                    st.write(f"Subtotal: {ped['quantidade'] * ped['preco']:,.2f} Kz")
                with col_d3:
                    if ped["status"] == "Pendente" and ped["tipo"] == "Bebidas":
                        if st.button(f"Confirmar Bebida #{idx}", key=f"conf_beb_{m_ativa}_{idx}"):
                            st.session_state.mesas[m_ativa]["pedidos"][idx]["status"] = "Confirmado"
                            st.session_state.mesas[m_ativa]["total"] += (ped['quantidade'] * ped['preco'])
                            st.success("Bebida confirmada!")
                            st.rerun()
                    elif ped["status"] == "Pendente" and ped["tipo"] == "Alimentos":
                        st.info("Aguardando aprovação da Cozinha 🍳")
                st.divider()
            
            if st.button("🔓 Fechar Conta / Liquidar Fatura da Mesa", type="primary"):
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                if m_ativa in st.session_state.clientes_mesa:
                    del st.session_state.clientes_mesa[m_ativa]
                st.success(f"Mesa {m_ativa} fechada e conta liquidada com sucesso!")
                st.rerun()

    else:
        st.info("💡 Clique numa mesa para gerir pedidos, ver o QR code ou fechar a conta.")
        
        cols = st.columns(6)
        for i in range(1, 31):
            mesa_info = st.session_state.mesas[i]
            tem_pendentes = any(p["status"] == "Pendente" for p in mesa_info["pedidos"])
            tem_recusados = any(p.get("cozinha_status") == "Recusado" for p in mesa_info["pedidos"])
            
            with cols[(i - 1) % 6]:
                if tem_recusados:
                    st.markdown(f'<div class="mesa-alerta">MESA {i}<br>❌ PEDIDO RECUSADO!</div>', unsafe_allow_html=True)
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
# ÁREA: ADMINISTRADOR (GERADOR DOS LINKS PRINCIPAIS)
# ==========================================
def area_administrador():
    st.title("👑 Painel do Administrador - NobreSabor")
    st.info("Aqui controla a abertura/fecho do Caixa, gere o stock, Recursos Humanos e obtém os links diretos para os perfis de Caixa e Cozinha.")
    
    # Secção com os Links Diretos para o Administrador copiar/partilhar
    with st.expander("🔗 Links Oficiais dos Módulos do Sistema", expanded=True):
        st.write("Utilize os links abaixo para abrir cada perfil dedicado nos dispositivos do restaurante:")
        
        link_caixa = f"{URL_OFICIAL}/?perfil=caixa"
        link_cozinha = f"{URL_OFICIAL}/?perfil=cozinha"
        
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.text_input("Link Direto do Caixa:", link_caixa, key="link_cx_adm")
        with col_l2:
            st.text_input("Link Direto da Cozinha:", link_cozinha, key="link_cz_adm")
            
    tab_adm_cx, tab_adm_stock, tab_adm_drh = st.tabs(["💰 Controlo de Caixa", "📦 Stock", "👥 Recursos Humanos"])
    
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


# ==========================================
# EXECUÇÃO DO ROTEADOR PRINCIPAL
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
