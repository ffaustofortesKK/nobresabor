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

# Estilo CSS para o Efeito de Alerta a Piscar nas Mesas com Pedidos Pendentes
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

# Função para Gerar QR Code em Bytes
def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# Capturar parâmetro de URL do QR Code (ex: ?mesa=5)
query_params = st.query_params
mesa_qr = query_params.get("mesa", None)

# Menu Lateral
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("Restaurante Gestão")

menu_opcoes = [
    "📱 Cliente / QR Code (Mesa)", 
    "👨‍🍳 Garçon / Pedidos", 
    "💻 Caixa Central (30 Mesas)", 
    "📦 Administrador (Stock)",
    "👑 Gestão de Links e QR Codes"
]

# Se o link tiver parâmetro de mesa, direciona direto para o cliente
menu_inicial = 0 if mesa_qr else 0
menu = st.sidebar.selectbox("Navegação:", menu_opcoes, index=menu_inicial)

# 1. CLIENTE (QR CODE)
if menu == "📱 Cliente / QR Code (Mesa)":
    st.title("📱 Pedido via QR Code do Cliente")
    
    # Identificar a mesa pelo URL ou seleção manual
    if mesa_qr and str(mesa_qr).isdigit():
        num_mesa = int(mesa_qr)
        if not (1 <= num_mesa <= 30):
            num_mesa = 1
    else:
        num_mesa = st.selectbox("Número da sua Mesa:", [i for i in range(1, 31)])
    
    st.success(f"✅ Conectado à **Mesa {num_mesa}**. Faça o seu pedido abaixo:")
    st.markdown("> *«Aproveite o melhor ambiente e saboreie a nossa culinária!»*")
    
    if not st.session_state.stock.empty:
        opcoes = st.session_state.stock['Produto'].tolist()
        item_escolhido = st.selectbox("Escolha o Item:", opcoes)
        
        row_prod = st.session_state.stock[st.session_state.stock['Produto'] == item_escolhido].iloc[0]
        tipo_item = row_prod['Categoria']
        preco_item = row_prod['Preço Unitário']
        
        qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
        obs = st.text_input("Observações (ex: Sem gelo, bem passado):")
        
        if st.button("Enviar Pedido para o Caixa"):
            # Abertura automática da mesa ao submeter o pedido
            st.session_state.mesas[num_mesa]["status"] = "Aberta"
            
            novo_pedido = {
                "item": item_escolhido,
                "tipo": tipo_item,
                "quantidade": qtd,
                "preco": preco_item,
                "origem": f"Cliente (Mesa {num_mesa})",
                "obs": obs,
                "status": "Pendente",
                "hora": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.mesas[num_mesa]["pedidos"].append(novo_pedido)
            st.success("🎉 Pedido enviado com sucesso! A sua mesa foi aberta e o Caixa foi notificado.")
            st.balloons()
    else:
        st.warning("Armazém sem produtos registados.")

# 2. GARÇON
elif menu == "👨‍🍳 Garçon / Pedidos":
    st.title("👨‍🍳 Painel do Garçon (Registo de Pedidos por Mesa)")
    
    nome_garcon = st.text_input("Identificação do Garçon (Nome / Código):")
    mesa_garcon = st.selectbox("Selecione a Mesa a Atender:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
    
    if nome_garcon and not st.session_state.stock.empty:
        opcoes = st.session_state.stock['Produto'].tolist()
        item_g = st.selectbox("Item solicitado:", opcoes)
        
        row_prod = st.session_state.stock[st.session_state.stock['Produto'] == item_g].iloc[0]
        tipo_item = row_prod['Categoria']
        preco_item = row_prod['Preço Unitário']
        
        qtd_g = st.number_input("Quantidade:", min_value=1, value=1, step=1, key="qtd_g")
        obs_g = st.text_input("Observações:", key="obs_g")
        
        if st.button("Registar Pedido na Mesa"):
            # Abre a mesa automaticamente ao receber pedido do garçon
            st.session_state.mesas[mesa_garcon]["status"] = "Aberta"
            
            novo_pedido = {
                "item": item_g,
                "tipo": tipo_item,
                "quantidade": qtd_g,
                "preco": preco_item,
                "origem": f"Garçon ({nome_garcon})",
                "obs": obs_g,
                "status": "Pendente",
                "hora": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.mesas[mesa_garcon]["pedidos"].append(novo_pedido)
            st.success(f"Pedido registado pelo Garçon {nome_garcon} para a Mesa {mesa_garcon}!")
    elif not nome_garcon:
        st.info("Por favor, insira o seu nome de Garçon para continuar.")

# 3. CAIXA CENTRAL
elif menu == "💻 Caixa Central (30 Mesas)":
    st.title("💻 Caixa Central - Controlo das 30 Mesas e Vendas")
    st.info("As mesas com novos pedidos piscam a vermelho. Clique numa mesa para gerir os pedidos e liquidar a conta.")
    
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

    st.divider()

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        st.subheader(f"📋 Gestão da Mesa {m_ativa}")
        
        dados_mesa = st.session_state.mesas[m_ativa]
        st.write(f"**Estado:** {dados_mesa['status']} | **Total Consumido:** {dados_mesa['total']:,.2f} Kz")
        
        if not dados_mesa["pedidos"]:
            st.info("Nenhum pedido registado nesta mesa.")
        else:
            st.write("### Pedidos da Mesa:")
            for idx, ped in enumerate(dados_mesa["pedidos"]):
                col_d1, col_d2, col_d3 = st.columns([3, 2, 2])
                with col_d1:
                    st.write(f"**{ped['quantidade']}x {ped['item']}** ({ped['tipo']})")
                    st.write(f"Origem: _{ped['origem']}_ | Obs: {ped['obs']} | ⏰ {ped['hora']}")
                with col_d2:
                    st.write(f"Estado: **{ped['status']}**")
                    st.write(f"Subtotal: {ped['quantidade'] * ped['preco']:,.2f} Kz")
                with col_d3:
                    if ped["status"] == "Pendente":
                        if st.button(f"Confirmar #{idx}", key=f"conf_ped_{m_ativa}_{idx}"):
                            # Se for Bebida, desconta imediatamente do stock
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
                            st.success("Pedido confirmado com sucesso!")
                            st.rerun()
                            
            if st.button("🔓 Fechar Conta / Liquidar Mesa"):
                st.session_state.mesas[m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0}
                st.success(f"Mesa {m_ativa} fechada e conta liquidada com sucesso!")
                st.rerun()

# 4. ADMINISTRADOR (STOCK)
elif menu == "📦 Administrador (Stock)":
    st.title("📦 Painel do Administrador - Controlo de Stock")
    st.info("O Administrador controla exclusivamente o armazém, registando e gerindo o stock de bebidas e alimentos.")
    
    with st.form("form_reg_stock"):
        st.write("Registar Novo Produto no Armazém")
        novo_prod = st.text_input("Nome do Produto (Alimento / Bebida)")
        cat_prod = st.selectbox("Categoria", ["Bebidas", "Alimentos", "Outros"])
        qtd_prod = st.number_input("Quantidade em Stock", min_value=0, step=1)
        preco_prod = st.number_input("Preço Unitário (Kz)", min_value=0.0, format="%.2f")
        
        btn_add = st.form_submit_button("Salvar no Stock")
        if btn_add and novo_prod:
            item_df = pd.DataFrame([[novo_prod, cat_prod, qtd_prod, preco_prod]], 
                                   columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
            st.session_state.stock = pd.concat([st.session_state.stock, item_df], ignore_index=True)
            st.success(f"Produto '{novo_prod}' adicionado ao stock!")
            
    st.subheader("Inventário Atualizado")
    st.dataframe(st.session_state.stock, use_container_width=True)

# 5. GESTÃO DE LINKS E QR CODES
elif menu == "👑 Gestão de Links e QR Codes":
    st.title("👑 Geração de Códigos QR para as 30 Mesas")
    st.info("Copie ou utilize estes links/QR codes para colocar em cada uma das 30 mesas do restaurante.")
    
    url_base = st.text_input("URL base da Aplicação (ex: https://nobresabor.streamlit.app)", "http://localhost:8501")
    
    cols_qr = st.columns(3)
    for i in range(1, 31):
        link_mesa = f"{url_base}/?mesa={i}"
        with cols_qr[(i - 1) % 3]:
            st.markdown(f"**Mesa {i}**")
            st.code(link_mesa, language="text")
            img_bytes = gerar_qrcode_bytes(link_mesa)
            st.image(img_bytes, width=140, caption=f"QR Code Mesa {i}")
            st.divider()
