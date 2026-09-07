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

# Estilo CSS para o Efeito de Alerta a Piscar (Blink)
st.markdown("""
    <style>
    @keyframes piscar {
        0% { opacity: 1; background-color: #ff4b4b; color: white; }
        50% { opacity: 0.3; background-color: #ffe6e6; color: black; }
        100% { opacity: 1; background-color: #ff4b4b; color: white; }
    }
    .alerta-piscar {
        animation: piscar 1s infinite;
        padding: 10px;
        border-radius: 8px;
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

if "pedidos_caixa" not in st.session_state:
    # Cada pedido terá: id, mesa, item, tipo (Bebida/Comida), qtd, preco, status (Pendente Caixa, Confirmado, Cozinha, Pronto)
    st.session_state.pedidos_caixa = []

if "stock" not in st.session_state:
    # Stock inicial de exemplo incluindo bebidas
    st.session_state.stock = pd.DataFrame([
        ["Água 0.5L", "Bebidas", 50, 300.0],
        ["Refrigerante Cola", "Bebidas", 40, 450.0],
        ["Cerveja Cuca", "Bebidas", 60, 500.0],
        ["Vinho Tinto", "Bebidas", 15, 4500.0],
        ["Frango à Grega", "Alimentos", 20, 3500.0],
        ["Bife a Cavalo", "Alimentos", 15, 4000.0]
    ], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

if "rh" not in st.session_state:
    st.session_state.rh = pd.DataFrame(columns=["Nome", "Categoria", "Telefone", "BI", "Faltas", "Desconto/Dia", "Turno"])

# Função Auxiliar para Gerar QR Code em Imagem Bytes
def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# Menu Lateral para Navegação por Perfil
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("Restaurante Gestão")
menu = st.sidebar.selectbox("Selecione o Painel:", [
    "🏠 Início / Boas-Vindas", 
    "📱 Cliente (Mesa / QR Code)", 
    "💻 Caixa Central", 
    "🍳 Cozinha", 
    "📦 Stock", 
    "👥 Recursos Humanos", 
    "👑 Administrador"
])

# 1. INÍCIO / BOAS-VINDAS
if menu == "🏠 Início / Boas-Vindas":
    st.title("Bem-vindo ao Sistema do Restaurante! 🍽️")
    st.markdown("""
    > *"A boa comida é a base da verdadeira felicidade."* — Aproveite o melhor ambiente da cidade!
    
    Este sistema gere as **30 mesas**, fluxo de pedidos entre **Caixa** e **Cozinha**, controlo de **Stock** (com baixa automática de bebidas) e **Recursos Humanos**.
    """)

# 2. CLIENTE (QR CODE / TABLET)
elif menu == "📱 Cliente (Mesa / QR Code)":
    st.title("📱 Pedido via QR Code / Tablet (Simulação)")
    
    # Simulação de parâmetro de mesa via URL ou seleção direta
    num_mesa = st.selectbox("Identificação da Mesa:", [i for i in range(1, 31)], format_func=lambda x: f"Mesa {x}")
    
    if st.session_state.mesas[num_mesa]["status"] == "Fechada":
        st.warning("⚠️ Esta mesa ainda está Fechada. Solicite a abertura ao Caixa ou Garçom.")
    else:
        st.success(f"✅ Mesa {num_mesa} aberta! Faça o seu pedido:")
        
        # Selecionar itens disponíveis no stock
        opcoes_stock = st.session_state.stock['Produto'].tolist()
        item_escolhido = st.selectbox("Selecione o Item do Cardápio:", opcoes_stock)
        
        # Identificar se é Bebida ou Comida com base no stock
        tipo_item = st.session_state.stock.loc[st.session_state.stock['Produto'] == item_escolhido, 'Categoria'].values[0]
        preco_item = st.session_state.stock.loc[st.session_state.stock['Produto'] == item_escolhido, 'Preço Unitário'].values[0]
        
        qtd_pedido = st.number_input("Quantidade:", min_value=1, value=1, step=1)
        obs = st.text_input("Observações (ex: Sem gelo, bem passado):")
        
        if st.button("Enviar Pedido para o Caixa"):
            novo_pedido = {
                "id": len(st.session_state.pedidos_caixa) + 1,
                "mesa": num_mesa,
                "item": item_escolhido,
                "tipo": tipo_item, # Bebidas ou Alimentos/Outros
                "quantidade": qtd_pedido,
                "preco_unitario": preco_item,
                "obs": obs,
                "status": "Pendente Caixa",
                "hora": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.pedidos_caixa.append(novo_pedido)
            st.success("🎉 Pedido enviado com sucesso para o Caixa! Aproveite o melhor ambiente do restaurante.")
            st.balloons()

# 3. CAIXA CENTRAL
elif menu == "💻 Caixa Central":
    st.title("💻 Caixa Central - Faturação, Mesas e Alertas")
    
    tab1, tab2, tab3 = st.tabs(["🔴 Alertas e Pedidos Pendentes", "🪑 Estado das 30 Mesas", "📦 Faturação e Histórico"])
    
    with tab1:
        st.subheader("Painel de Notificações de Pedidos")
        st.info("As mesas com pedidos pendentes piscam em alerta. Clique na mesa para confirmar os pedidos.")
        
        # Filtrar pedidos pendentes para o caixa
        pendentes = [p for p in st.session_state.pedidos_caixa if p["status"] == "Pendente Caixa"]
        
        if not pendentes:
            st.success("✨ Nenhum pedido pendente no momento. Tudo limpo!")
        else:
            # Identificar mesas que têm pedidos pendentes
            mesas_com_alerta = set(p["mesa"] for p in pendentes)
            
            st.markdown("### Mesas com Alerta Ativo:")
            cols_alerta = st.columns(min(len(mesas_com_alerta), 6))
            
            for idx, m_id in enumerate(mesas_com_alerta):
                with cols_alerta[idx % len(cols_alerta)]:
                    st.markdown(f'<div class="alerta-piscar">MESA {m_id}<br>PEDIDO NOVO!</div>', unsafe_allow_html=True)
            
            st.divider()
            st.markdown("### Detalhe dos Pedidos para Confirmação:")
            
            for p in pendentes:
                with st.expander(f"🔔 Mesa {p['mesa']} | {p['quantidade']}x {p['item']} ({p['tipo']}) - {p['hora']}"):
                    st.write(f"**Observação:** {p['obs'] if p['obs'] else 'Nenhuma'}")
                    st.write(f"**Preço Unitário:** {p['preco_unitario']} Kz | **Total:** {p['quantidade'] * p['preco_unitario']} Kz")
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button(f"Confirmar Pedido #{p['id']}", key=f"conf_{p['id']}"):
                            # Se for Bebida, desconta imediatamente do stock
                            if p["tipo"] == "Bebidas":
                                idx_stock = st.session_state.stock[st.session_state.stock['Produto'] == p['item']].index
                                if not idx_stock.empty:
                                    stock_atual = st.session_state.stock.at[idx_stock[0], 'Quantidade']
                                    if stock_atual >= p['quantidade']:
                                        st.session_state.stock.at[idx_stock[0], 'Quantidade'] = stock_atual - p['quantidade']
                                    else:
                                        st.error("⚠️ Stock insuficiente de bebidas para dar baixa!")
                                        continue
                            
                            # Atualiza status do pedido
                            for item_ped in st.session_state.pedidos_caixa:
                                if item_ped["id"] == p["id"]:
                                    item_ped["status"] = "Confirmado / Enviado Cozinha" if p["tipo"] == "Alimentos" else "Entregue/Confirmado"
                            
                            # Adiciona valor ao total da mesa
                            st.session_state.mesas[p['mesa']]["total"] += (p['quantidade'] * p['preco_unitario'])
                            st.success(f"Pedido da Mesa {p['mesa']} confirmado com sucesso!")
                            st.rerun()
                            
                    with col_b2:
                        if st.button(f"Rejeitar/Cancelar #{p['id']}", key=f"rej_{p['id']}"):
                            st.session_state.pedidos_caixa = [x for x in st.session_state.pedidos_caixa if x["id"] != p["id"]]
                            st.warning("Pedido cancelado.")
                            st.rerun()

    with tab2:
        st.subheader("Gestão de Abertura e Controlo das 30 Mesas")
        cols = st.columns(6)
        for i in range(1, 31):
            with cols[(i - 1) % 6]:
                status_atual = st.session_state.mesas[i]["status"]
                cor = "🟢 Aberta" if status_atual == "Aberta" else "🔴 Fechada"
                total_mesa = st.session_state.mesas[i]["total"]
                
                st.markdown(f"**Mesa {i}**")
                st.write(f"Estado: {cor}")
                st.write(f"Consumo: {total_mesa:,.2f} Kz")
                
                if status_atual == "Fechada":
                    if st.button(f"Abrir Mesa {i}", key=f"abrir_m_{i}"):
                        st.session_state.mesas[i]["status"] = "Aberta"
                        st.rerun()
                else:
                    if st.button(f"Fechar/Conta {i}", key=f"fechar_m_{i}"):
                        st.session_state.mesas[i]["status"] = "Fechada"
                        st.session_state.mesas[i]["total"] = 0.0
                        st.success(f"Mesa {i} fechada com sucesso!")
                        st.rerun()

    with tab3:
        st.subheader("Registo Geral de Faturação")
        historico_confirmados = [p for p in st.session_state.pedidos_caixa if p["status"] != "Pendente Caixa"]
        if historico_confirmados:
            st.dataframe(pd.DataFrame(historico_confirmados), use_container_width=True)
        else:
            st.info("Nenhum histórico faturado ainda.")

# 4. COZINHA
elif menu == "🍳 Cozinha":
    st.title("🍳 Painel da Cozinha (Pratos e Alimentos)")
    st.write("Pedidos de alimentos confirmados pelo caixa que requerem preparação:")
    
    # Apenas alimentos confirmados vão para a cozinha
    pedidos_cozinha = [p for p in st.session_state.pedidos_caixa if p["tipo"] == "Alimentos" and p["status"] == "Confirmado / Enviado Cozinha"]
    
    if not pedidos_cozinha:
        st.info("Nenhum prato pendente para a cozinha no momento.")
    else:
        for p in pedidos_cozinha:
            st.warning(f"**Mesa {p['mesa']}** | Prato: **{p['quantidade']}x {p['item']}** | Obs: {p['obs']} | Hora: {p['hora']}")
            if st.button(f"Prato Pronto (Avisar Caixa) - Pedido #{p['id']}", key=f"coz_pronto_{p['id']}"):
                for item_ped in st.session_state.pedidos_caixa:
                    if item_ped["id"] == p["id"]:
                        item_ped["status"] = "Pronto na Cozinha"
                st.success(f"Aviso enviado ao Caixa de que o prato da Mesa {p['mesa']} está pronto!")
                st.rerun()

# 5. STOCK
elif menu == "📦 Stock":
    st.title("📦 Armazém de Stock (Bebidas e Alimentos)")
    
    with st.form("form_stock"):
        prod = st.text_input("Nome do Produto")
        cat = st.selectbox("Categoria", ["Bebidas", "Alimentos", "Outros"])
        qtd = st.number_input("Quantidade Inicial", min_value=0, step=1)
        preco = st.number_input("Preço Unitário (Kz)", min_value=0.0, format="%.2f")
        cadastrar = st.form_submit_button("Registar no Stock")
        
        if cadastrar and prod:
            novo_item = pd.DataFrame([[prod, cat, qtd, preco]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
            st.session_state.stock = pd.concat([st.session_state.stock, novo_item], ignore_index=True)
            st.success(f"Produto '{prod}' registado com sucesso!")
            
    st.subheader("Inventário Atualizado em Tempo Real")
    st.dataframe(st.session_state.stock, use_container_width=True)

# 6. RECURSOS HUMANOS
elif menu == "👥 Recursos Humanos":
    st.title("👥 Gestão de Recursos Humanos")
    
    with st.form("form_rh"):
        st.write("Registar Colaborador (Cozinheiro, Garçon, Chefe de Sala, Limpeza, Comprador)")
        nome = st.text_input("Nome Completo")
        categoria = st.selectbox("Categoria", ["Cozinheiro", "Garçon", "Chefe de Sala", "Limpeza", "Comprador"])
        telefone = st.text_input("Telefone")
        bi = st.text_input("Número do B.I.")
        turno = st.selectbox("Turno de Trabalho", ["Turno 1 (Manhã)", "Turno 2 (Tarde/Noite)"])
        faltas = st.number_input("Número de Faltas", min_value=0, step=1)
        desconto_dia = st.number_input("Valor a Descontar por Dia (Kz)", min_value=0.0, format="%.2f")
        
        btn_rh = st.form_submit_button("Salvar Colaborador")
        if btn_rh and nome:
            novo_func = pd.DataFrame([[nome, categoria, telefone, bi, faltas, desconto_dia, turno]], 
                                     columns=["Nome", "Categoria", "Telefone", "BI", "Faltas", "Desconto/Dia", "Turno"])
            st.session_state.rh = pd.concat([st.session_state.rh, novo_func], ignore_index=True)
            st.success(f"Colaborador {nome} registado com sucesso!")
            
    st.subheader("Quadro de Pessoal")
    st.dataframe(st.session_state.rh, use_container_width=True)

# 7. ADMINISTRADOR
elif menu == "👑 Administrador":
    st.title("👑 Painel do Administrador - Links e QR Codes das 30 Mesas")
    
    st.subheader("Gerador de Códigos QR e Links de Acesso (30 Mesas)")
    st.info("Aqui o Administrador gere os links e descarrega ou visualiza os QR Codes para colocar em cada mesa.")
    
    # URL base simulada da aplicação
    url_base = st.text_input("URL Base da Aplicação (ex: https://teu-app.streamlit.app)", "http://localhost:8501")
    
    if st.button("Gerar Códigos QR para as 30 Mesas"):
        st.success("Códigos QR gerados com sucesso para todas as 30 mesas!")
        
    # Exibir grelha com os QR Codes de forma dinâmica
    cols_qr = st.columns(3)
    for i in range(1, 31):
        link_mesa = f"{url_base}/?mesa={i}"
        with cols_qr[(i - 1) % 3]:
            st.markdown(f"**Mesa {i}**")
            st.code(link_mesa, language="text")
            # Gerar e exibir imagem do QR code
            img_bytes = gerar_qrcode_bytes(link_mesa)
            st.image(img_bytes, width=150, caption=f"QR Code - Mesa {i}")
            st.divider()
