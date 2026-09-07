import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(
    page_title="Sistema de Gestão - Restaurante",
    page_icon="🍽️",
    layout="wide"
)

# Inicialização de Estados da Sessão (Simulando Banco de Dados temporário)
if "mesas" not in st.session_state:
    st.session_state.mesas = {i: {"status": "Fechada", "pedidos": [], "total": 0.0} for i in range(1, 31)}

if "pedidos_cozinha" not in st.session_state:
    st.session_state.pedidos_cozinha = []

if "stock" not in st.session_state:
    st.session_state.stock = pd.DataFrame(columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

if "rh" not in st.session_state:
    st.session_state.rh = pd.DataFrame(columns=["Nome", "Categoria", "Telefone", "BI", "Faltas", "Desconto/Dia", "Turno"])

# Menu Lateral para Navegação por Perfil
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("Restaurante Gestão")
menu = st.sidebar.selectbox("Selecione o Painel:", ["🏠 Início / Boas-Vindas", "📱 Cliente (Mesa / QR Code)", "💻 Caixa Central", "🍳 Cozinha", "📦 Stock", "👥 Recursos Humanos", "👑 Administrador"])

# 1. INÍCIO / BOAS-VINDAS
if menu == "🏠 Início / Boas-Vindas":
    st.title("Bem-vindo ao Sistema do Restaurante! 🍽️")
    st.markdown("""
    > *"A boa comida é a base da verdadeira felicidade."* — Aproveite o melhor ambiente da cidade!
    
    Este sistema foi desenhado para otimizar o atendimento das **30 mesas**, controlando o fluxo entre o **Caixa**, a **Cozinha**, o **Armazém de Stock** e os **Recursos Humanos**.
    """)
    st.info("Utilize o menu lateral para alternar entre os painéis conforme a sua permissão.")

# 2. CLIENTE (QR CODE / TABLET)
elif menu == "📱 Cliente (Mesa / QR Code)":
    st.title("📱 Pedido via QR Code / Tablet")
    
    # Seleção da Mesa
    mesa_selecionada = st.selectbox("Selecione a sua Mesa:", [f"Mesa {i}" for i in range(1, 31)])
    num_mesa = int(mesa_selecionada.split(" ")[1])
    
    # Verificar se a mesa está aberta pelo caixa
    if st.session_state.mesas[num_mesa]["status"] == "Fechada":
        st.warning("⚠️ Esta mesa ainda não foi aberta pelo Caixa. Por favor, solicite a abertura ao garçom ou ao caixa.")
    else:
        st.success(f"✅ {mesa_selecionada} aberta! Faça o seu pedido abaixo:")
        
        # Simulação de Cardápio
        categoria = st.radio("Escolha:", ["Bebidas", "Comidas"])
        if categoria == "Bebidas":
            item = st.selectbox("Selecione a Bebida:", ["Água 0.5L", "Refrigerante", "Cerveja", "Vinho da Casa"])
        else:
            item = st.selectbox("Selecione o Prato:", ["Frango à Grega", "Bife a Cavalo", "Calulu de Peixe", "Mufete Completo"])
            
        obs = st.text_input("Observações (ex: Sem gelo, bem passado):")
        
        if st.button("Enviar Pedido"):
            pedido_info = {"mesa": num_mesa, "item": item, "tipo": categoria, "obs": obs, "status": "Pendente Caixa", "hora": datetime.now().strftime("%H:%M:%S")}
            st.session_state.pedidos_cozinha.append(pedido_info)
            st.success("🎉 Pedido enviado com sucesso! Aguarde a confirmação do Caixa.")
            st.markdown("### 😊 Obrigado por escolher o nosso espaço!")
            st.balloons()

# 3. CAIXA CENTRAL
elif menu == "💻 Caixa Central":
    st.title("💻 Caixa Central - Faturação e Controlo")
    
    tab1, tab2, tab3 = st.tabs(["Abertura de Mesas", "Confirmação de Bebidas", "Pedidos e Alertas"])
    
    with tab1:
        st.subheader("Gestão de Abertura de Mesas (30 Mesas)")
        cols = st.columns(6)
        for i in range(1, 31):
            with cols[(i - 1) % 6]:
                status_atual = st.session_state.mesas[i]["status"]
                cor = "🟢" if status_atual == "Aberta" else "🔴"
                st.write(f"{cor} **Mesa {i}**")
                if status_atual == "Fechada":
                    if st.button(f"Abrir {i}", key=f"abrir_{i}"):
                        st.session_state.mesas[i]["status"] = "Aberta"
                        st.rerun()
                else:
                    if st.button(f"Fechar {i}", key=f"fechar_{i}"):
                        st.session_state.mesas[i]["status"] = "Fechada"
                        st.rerun()
                        
    with tab2:
        st.subheader("Confirmação de Bebidas Pendentes")
        st.info("O caixa só confirma o pedido após verificar a entrega física da bebida.")
        # Aqui listaremos os pedidos de bebidas pendentes para confirmação rápida
        st.write("Nenhuma bebida pendente no momento.")

    with tab3:
        st.subheader("Alertas e Controlo de Pratos (30 min)")
        st.write("Monitoramento de atrasos nos pratos solicitados.")

# 4. COZINHA
elif menu == "🍳 Cozinha":
    st.title("🍳 Painel da Cozinha")
    st.write("Acompanhe os pedidos aceites pelo caixa e gerencie o tempo de preparo (Alerta de 30 minutos).")
    
    if not st.session_state.pedidos_cozinha:
        st.info("Nenhum pedido na fila.")
    else:
        for idx, p in enumerate(st.session_state.pedidos_cozinha):
            st.warning(f"**Mesa {p['mesa']}** | Item: **{p['item']}** ({p['tipo']}) | Hora: {p['hora']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Prato Pronto ✅", key=f"pronto_{idx}"):
                    st.success(f"Mesa {p['mesa']}: {p['item']} pronto! Alerta enviado ao Caixa.")
            with col2:
                if st.button(f"Cancelar ❌", key=f"canc_{idx}"):
                    st.session_state.pedidos_cozinha.pop(idx)
                    st.rerun()

# 5. STOCK
elif menu == "📦 Stock":
    st.title("📦 Armazém de Stock (Bebidas e Alimentos)")
    
    with st.form("form_stock"):
        prod = st.text_input("Nome do Produto (Alimento / Bebida)")
        cat = st.selectbox("Categoria", ["Bebidas", "Alimentos", "Outros"])
        qtd = st.number_input("Quantidade", min_value=0, step=1)
        preco = st.number_input("Preço Unitário (Kz)", min_value=0.0, format="%.2f")
        cadastrar = st.form_submit_button("Registar Produto")
        
        if cadastrar and prod:
            novo_item = pd.DataFrame([[prod, cat, qtd, preco]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
            st.session_state.stock = pd.concat([st.session_state.stock, novo_item], ignore_index=True)
            st.success(f"Produto '{prod}' registado com sucesso!")
            
    st.subheader("Inventário Atual")
    st.dataframe(st.session_state.stock, use_container_width=True)

# 6. RECURSOS HUMANOS
elif menu == "👥 Recursos Humanos":
    st.title("👥 Gestão de Recursos Humanos")
    
    with st.form("form_rh"):
        st.write("Registar Funcionário")
        nome = st.text_input("Nome Completo")
        categoria = st.selectbox("Categoria", ["Cozinheiro", "Garçon", "Chefe de Sala", "Limpeza", "Comprador"])
        telefone = st.text_input("Telefone")
        bi = st.text_input("Número do B.I.")
        turno = st.selectbox("Turno de Trabalho", ["Turno 1 (Manhã)", "Turno 2 (Tarde/Noite)"])
        faltas = st.number_input("Número de Faltas", min_value=0, step=1)
        desconto_dia = st.number_input("Valor a Descontar por Dia (Kz)", min_value=0.0, format="%.2f")
        
        btn_rh = st.form_submit_button("Salvar Funcionário")
        if btn_rh and nome:
            novo_func = pd.DataFrame([[nome, categoria, telefone, bi, faltas, desconto_dia, turno]], 
                                     columns=["Nome", "Categoria", "Telefone", "BI", "Faltas", "Desconto/Dia", "Turno"])
            st.session_state.rh = pd.concat([st.session_state.rh, novo_func], ignore_index=True)
            st.success(f"Funcionário {nome} registado com sucesso!")
            
    st.subheader("Lista de Colaboradores")
    st.dataframe(st.session_state.rh, use_container_width=True)

# 7. ADMINISTRADOR
elif menu == "👑 Administrador":
    st.title("👑 Painel do Administrador")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Controlo de Caixa")
        if st.button("🔓 Abertura Geral de Caixa"):
            st.success("Caixa aberto pelo Administrador!")
        if st.button("🔒 Fecho Geral de Caixa"):
            st.info("Caixa fechado com sucesso.")
            
    with col2:
        st.subheader("Geração de Links e QR Codes")
        st.write("Aqui o Administrador centraliza os links gerados pelo Caixa para monitoramento.")
        st.info("Link do Caixa: `[Ativo]`\n\nLink da Cozinha: `[Ativo]`\n\nCódigos QR das 30 Mesas: `[Gerados]`")
