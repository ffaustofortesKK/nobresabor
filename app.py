import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Gestão - Restaurante", page_icon="🍽️", layout="wide")

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 5px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍽️ Sistema Integrado de Gestão - NobreSabor")
st.markdown("Painel de Controlo Principal")

# Navegação principal por abas superiores (sem barra lateral)
top_tab1, top_tab2, top_tab3, top_tab4 = st.tabs(["📊 Administrador", "🍳 Cozinha", "💰 Caixa (Operacional)", "📈 Relatórios Gerais"])

with top_tab1:
    st.header("Painel do Administrador")
    st.markdown("Gerenciamento central do sistema.")
    
    # Sub-abas dentro do Administrador: Stock, DCH, Finanças
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📦 Stock", "👥 DCH (Departamento de Capital Humano)", "💵 Finanças"])
    
    with admin_tab1:
        st.subheader("Gestão de Stock")
        st.markdown("Controlo de inventário, produtos disponíveis e alertas de reposição.")
        
        stock_data = {
            "Código": ["P001", "P002", "P003", "P004"],
            "Produto": ["Arroz Especial", "Frango Congelado", "Óleo Vegetal", "Bebidas (Refrigerantes)"],
            "Quantidade Atual": [45, 120, 30, 85],
            "Unidade": ["Kg", "Kg", "Litros", "Unidades"],
            "Estado": ["Normal", "Crítico", "Normal", "Normal"]
        }
        df_stock = pd.DataFrame(stock_data)
        st.dataframe(df_stock, use_container_width=True)
        
        with st.form("add_stock_form"):
            st.write("Adicionar / Atualizar Item no Stock")
            col1, col2, col3 = st.columns(3)
            with col1:
                item_name = st.text_input("Nome do Produto")
            with col2:
                item_qty = st.number_input("Quantidade", min_value=0.0, value=10.0)
            with col3:
                item_unit = st.selectbox("Unidade", ["Kg", "Litros", "Unidades", "Caixas"])
            submitted_stock = st.form_submit_button("Guardar no Stock")
            if submitted_stock:
                st.success(f"Item '{item_name}' atualizado com sucesso!")

    with admin_tab2:
        st.subheader("Departamento de Capital Humano (DCH)")
        st.markdown("Gestão de colaboradores, turnos, presenças e folha de pagamentos.")
        
        dch_data = {
            "ID": ["EMP01", "EMP02", "EMP03"],
            "Nome": ["Cefas David", "Edna Anjinha", "Mawete Fortes"],
            "Cargo": ["Chefe de Cozinha", "Atendimento / Caixa", "Gestora Administrativa"],
            "Estado": ["Ativo", "Ativo", "Ativo"]
        }
        df_dch = pd.DataFrame(dch_data)
        st.dataframe(df_dch, use_container_width=True)
        
        if st.button("Registar Novo Colaborador"):
            st.info("Formulário de registo de colaborador aberto.")

    with admin_tab3:
        st.subheader("Finanças")
        st.markdown("Gestão financeira central: Registo do dia, Abertura de Caixa e Fecho de Caixa.")
        
        fin_sub1, fin_sub2, fin_sub3 = st.tabs(["📋 Registo do Dia", "🔓 Abertura de Caixa", "🔒 Fecho de Caixa"])
        
        with fin_sub1:
            st.markdown("### Registo Diário de Transações")
            trans_data = {
                "Hora": ["08:30", "10:15", "12:45", "14:20"],
                "Descrição": ["Fundo de Maneio Inicial", "Venda Balcão #101", "Venda Almoço #102", "Compra de Insumos"],
                "Tipo": ["Entrada", "Entrada", "Entrada", "Saída"],
                "Valor (Kz)": [50000.0, 25000.0, 78500.0, 15000.0]
            }
            df_trans = pd.DataFrame(trans_data)
            st.dataframe(df_trans, use_container_width=True)
            
            total_entradas = 50000.0 + 25000.0 + 78500.0
            total_saidas = 15000.0
            st.metric("Saldo Atual em Caixa", f"{total_entradas - total_saidas:,.2f} Kz")

        with fin_sub2:
            st.markdown("### Abertura de Caixa")
            with st.form("form_abertura_caixa"):
                operador = st.text_input("Nome do Operador / Caixa", value="Edna Anjinha")
                fundo_inicial = st.number_input("Valor de Fundo de Maneio (Kz)", min_value=0.0, value=50000.0, step=5000.0)
                observacoes_abertura = st.text_area("Observações de Abertura")
                btn_abrir = st.form_submit_button("Confirmar Abertura de Caixa")
                if btn_abrir:
                    st.success(f"Caixa aberto com sucesso por {operador} com fundo de {fundo_inicial:,.2f} Kz às {datetime.now().strftime('%H:%M')}.")

        with fin_sub3:
            st.markdown("### Fecho de Caixa")
            with st.form("form_fecho_caixa"):
                operador_fecho = st.text_input("Operador Responsável", value="Edna Anjinha")
                dinheiro_gaveta = st.number_input("Dinheiro Contado em Gaveta (Kz)", min_value=0.0, value=138500.0, step=1000.0)
                multicaixa = st.number_input("Total em Multicaixa / POS (Kz)", min_value=0.0, value=45000.0, step=1000.0)
                observacoes_fecho = st.text_area("Relatório / Justificativas de Fecho")
                btn_fechar = st.form_submit_button("Efetuar Fecho de Caixa")
                if btn_fechar:
                    st.success(f"Fecho de caixa efetuado com sucesso! Total apurado: {dinheiro_gaveta + multicaixa:,.2f} Kz.")

with top_tab2:
    st.header("Painel da Cozinha")
    st.markdown("Acompanhamento de pedidos em tempo real para a preparação na cozinha.")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.info("🔴 **Pendentes**\n- Pedido #12: Frango à Brasa (2x)\n- Pedido #13: Calulu de Peixe (1x)")
    with col_c2:
        st.warning("🟡 **Em Preparação**\n- Pedido #11: Funge com Carne (1x)")
    with col_c3:
        st.success("🟢 **Prontos para Servir**\n- Pedido #10: Kizaka com Peixe Grelhado")

with top_tab3:
    st.header("Caixa Operacional")
    st.markdown("Registo rápido de vendas e emissão de talões.")
    
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        st.selectbox("Selecionar Prato / Bebida", ["Prato do Dia", "Frango Grelhado", "Sumo Natural", "Água Mineral"])
        st.number_input("Quantidade", min_value=1, value=1)
        if st.button("Adicionar ao Pedido"):
            st.success("Item adicionado ao talão!")
    with col_v2:
        st.markdown("#### Resumo do Talão Atual")
        st.write("1x Prato do Dia - 3.500 Kz")
        st.write("2x Sumo Natural - 1.000 Kz")
        st.markdown("---")
        st.markdown("**Total: 4.500 Kz**")
        if st.button("Finalizar Venda / Pagamento", type="primary"):
            st.success("Venda registada com sucesso!")

with top_tab4:
    st.header("Relatórios Gerais")
    st.markdown("Visão geral de desempenho de vendas, stock e financeiro.")
    st.bar_chart({"Seg": 120, "Ter": 150, "Qua": 180, "Qui": 220, "Sex": 310, "Sáb": 450, "Dom": 390})
