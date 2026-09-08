import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import qrcode
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Restaurante Nobre Sabor",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Customizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .mesa-fechada { background-color: #e9ecef; border: 2px solid #ced4da; padding: 15px; border-radius: 10px; text-align: center; color: #495057; }
    .mesa-aberta { background-color: #d1e7dd; border: 2px solid #badbcc; padding: 15px; border-radius: 10px; text-align: center; color: #0f5132; }
    .mesa-pronta-alerta { background-color: #f8d7da; border: 2px solid #f5c2c7; padding: 15px; border-radius: 10px; text-align: center; color: #842029; animation: pulse 1.5s infinite; }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GESTÃO DE FICHEIROS E PERSISTÊNCIA (JSON)
# ==========================================
ARQUIVO_ESTADO_CAIXA = "estado_caixa.json"
ARQUIVO_MESAS = "mesas_estado.json"
ARQUIVO_HISTORICO = "historico_vendas.json"

def ler_estado_caixa_disco():
    if os.path.exists(ARQUIVO_ESTADO_CAIXA):
        try:
            with open(ARQUIVO_ESTADO_CAIXA, "r") as f:
                return json.load(f).get("aberto", False)
        except:
            return False
    return False

def salvar_estado_caixa_disco(estado):
    with open(ARQUIVO_ESTADO_CAIXA, "w") as f:
        json.dump({"aberto": estado}, f)

def carregar_mesas_disco():
    if os.path.exists(ARQUIVO_MESAS):
        try:
            with open(ARQUIVO_MESAS, "r") as f:
                return json.load(f)
        except:
            pass
    # Estrutura padrão para 30 mesas
    mesas_padrao = {}
    for i in range(1, 31):
        mesas_padrao[str(i)] = {
            "status": "Fechada",
            "cliente": None,
            "pedidos": [],
            "total": 0.0,
            "fatura_emitida": None
        }
    return mesas_padrao

def salvar_mesas_disco(mesas):
    with open(ARQUIVO_MESAS, "w") as f:
        json.dump(mesas, f)

def carregar_historico_vendas():
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_historico_vendas(historico):
    with open(ARQUIVO_HISTORICO, "w") as f:
        json.dump(historico, f)

# Inicialização do Session State
if 'caixa_aberto' not in st.session_state:
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

if 'menu_itens' not in st.session_state:
    st.session_state.menu_itens = pd.DataFrame([
        {"Item": "Frango à Brasa c/ Batata", "Categoria": "Pratos Principais", "Preço (Kz)": 4500.0, "Stock": 50},
        {"Item": "Calulu de Peixe", "Categoria": "Pratos Tradicionais", "Preço (Kz)": 6000.0, "Stock": 30},
        {"Item": "Muamba de Galinha", "Categoria": "Pratos Tradicionais", "Preço (Kz)": 6500.0, "Stock": 25},
        {"Item": "Sumo Natural de Maracujá", "Categoria": "Bebidas", "Preço (Kz)": 1500.0, "Stock": 100},
        {"Item": "Cuca 33cl", "Categoria": "Bebidas", "Preço (Kz)": 800.0, "Stock": 200}
    ])

if 'rh' not in st.session_state:
    st.session_state.rh = pd.DataFrame([
        {"Código": "EMP001", "Nome": "António Silva", "Cargo": "Chefe de Cozinha", "Contacto": "923000111"},
        {"Código": "EMP002", "Nome": "Maria João", "Cargo": "Empregada de Mesa", "Contacto": "912333444"}
    ])

# Capturar parâmetros da URL (ex: ?mesa=5 ou ?perfil=cozinha)
query_params = st.query_params
mesa_detectada = None
if "mesa" in query_params:
    try:
        mesa_detectada = int(query_params["mesa"])
    except:
        pass

perfil_url = query_params.get("perfil", None)


# ==========================================
# ÁREA: CLIENTE (Cardápio & Pedidos por Mesa)
# ==========================================
def area_cliente():
    if not mesa_detectada or not (1 <= mesa_detectada <= 30):
        st.error("⚠️ Mesa inválida ou não especificada no link QR Code.")
        return

    st.title(f"🍽️ Restaurante Nobre Sabor — Mesa {mesa_detectada}")
    
    mesas_data = carregar_mesas_disco()
    str_mesa = str(mesa_detectada)
    mesa_info = mesas_data[str_mesa]

    # Registo inicial do cliente na mesa se ainda não estiver aberta
    if mesa_info["status"] == "Fechada" or not mesa_info.get("cliente"):
        with st.form("form_registo_cliente"):
            st.subheader("Bem-vindo! Por favor, identifique-se:")
            nome_cli = st.text_input("O seu Nome:")
            tel_cli = st.text_input("O seu Telefone / WhatsApp:")
            btn_entrar = st.form_submit_button("Abrir Mesa e Ver Ementa")
            
            if btn_entrar:
                if nome_cli.strip():
                    mesa_info["status"] = "Aberta"
                    mesa_info["cliente"] = {"nome": nome_cli, "telefone": tel_cli}
                    salvar_mesas_disco(mesas_data)
                    st.success("Mesa aberta com sucesso! A carregar ementa...")
                    st.rerun()
                else:
                    st.warning("Por favor, introduza o seu nome para continuar.")
        return

    # Visualização de Fatura / Estado da Mesa Aberta
    st.info(f"👤 Cliente: **{mesa_info['cliente']['nome']}** | Estado da Mesa: **Aberta**")
    
    # Abas do Cliente
    aba_menu, aba_pedidos, aba_conta = st.tabs(["📖 Ementa & Pedidos", "📋 Os Meus Pedidos", "💳 Pedir Conta & Fatura"])
    
    with aba_menu:
        st.subheader("Escolha os seus pratos e bebidas")
        
        categorias = st.session_state.menu_itens["Categoria"].unique()
        cat_escolhida = st.selectbox("Filtrar por Categoria:", categorias)
        
        itens_filtrados = st.session_state.menu_itens[st.session_state.menu_itens["Categoria"] == cat_escolhida]
        
        for index, row in itens_filtrados.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"**{row['Item']}**")
                st.caption(f"Preço: {row['Preço (Kz)']:,.2f} Kz")
            with col2:
                qtd = st.number_input("Qtd", min_value=1, max_value=20, value=1, key=f"qtd_{index}")
            with col3:
                if st.button("➕ Adicionar", key=f"add_{index}", use_container_width=True):
                    novo_pedido = {
                        "item": row['Item'],
                        "quantidade": qtd,
                        "preco": row['Preço (Kz)'],
                        "status": "Pendente",
                        "cozinha_status": "NaFila",
                        "hora": datetime.now().strftime("%H:%M:%S")
                    }
                    mesa_info["pedidos"].append(novo_pedido)
                    
                    # Recalcular total
                    total_atual = sum(p['quantidade'] * p['preco'] for p in mesa_info["pedidos"] if p['status'] != "Anulado")
                    mesa_info["total"] = total_atual
                    
                    salvar_mesas_disco(mesas_data)
                    st.success(f"{qtd}x {row['Item']} adicionado ao pedido!")
                    st.rerun()

    with aba_pedidos:
        st.subheader("Estado dos seus Pedidos na Cozinha")
        pedidos_mesa = mesa_info["pedidos"]
        if pedidos_mesa:
            df_p = pd.DataFrame(pedidos_mesa)
            st.dataframe(df_p[['hora', 'item', 'quantidade', 'preco', 'cozinha_status']], use_container_width=True)
        else:
            st.info("Ainda não efetuou nenhum pedido.")

    with aba_conta:
        st.subheader("Resumo da Conta")
        pedidos_ativos = [p for p in mesa_info["pedidos"] if p['status'] != "Anulado"]
        if pedidos_ativos:
            total_conta = sum(p['quantidade'] * p['preco'] for p in pedidos_ativos)
            for p in pedidos_ativos:
                st.write(f"- {p['quantidade']}x {p['item']} — {p['quantidade'] * p['preco']:,.2f} Kz")
            st.markdown(f"### Total a Pagar: **{total_conta:,.2f} Kz**")
            
            if st.button("🛎️ Chamar Empregar / Pedir a Conta", use_container_width=True):
                st.success("Obrigado! Um colaborador foi notificado para fechar a sua mesa.")
        else:
            st.info("A sua conta está vazia.")


# ==========================================
# ÁREA: COZINHA (Painel de Pedidos em Tempo Real)
# ==========================================
def area_cozinha():
    st.title("👨‍🍳 Painel de Cozinha — Gestão de Pedidos")
    
    mesas_data = carregar_mesas_disco()
    
    if st.button("🔄 Atualizar Pedidos da Cozinha", use_container_width=True):
        st.rerun()
        
    st.markdown("---")
    
    # Recολher todos os pedidos pendentes ou em preparação de todas as mesas
    tem_pedidos = False
    for num_mesa, dados_m in mesas_data.items():
        if dados_m["status"] == "Aberta" and dados_m["pedidos"]:
            for idx, p in enumerate(dados_m["pedidos"]):
                if p.get("cozinha_status") in ["NaFila", "Preparando"]:
                    tem_pedidos = True
                    with st.container():
                        c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
                        with c1:
                            st.markdown(f"### 🪑 Mesa {num_mesa}")
                        with c2:
                            st.write(f"**{p['quantidade']}x {p['item']}**")
                            st.caption(f"Hora: {p.get('hora', 'N/A')} | Estado Atual: {p.get('cozinha_status')}")
                        with c3:
                            novo_st = st.selectbox("Mudar Estado", ["NaFila", "Preparando", "Feito"], index=["NaFila", "Preparando", "Feito"].index(p.get("cozinha_status", "NaFila")), key=f"cz_{num_mesa}_{idx}")
                            if novo_st != p.get("cozinha_status"):
                                p["cozinha_status"] = novo_st
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        with c4:
                            if p.get("cozinha_status") == "Feito":
                                st.success("Pronto para servir!")
                        st.divider()
                        
    if not tem_pedidos:
        st.info("Nenhum pedido pendente na cozinha neste momento. Bom trabalho!")


# ==========================================
# ÁREA: ADMINISTRADOR (Painel Completo)
# ==========================================
def area_administrador():
    st.title("🛠️ Painel de Administração - Restaurante Nobre Sabor")
    
    # Segurança simples de Admin
    palavra_passe = st.sidebar.text_input("Palavra-passe Admin", type="password")
    if palavra_passe != "123123123":
        st.warning("🔒 Introduza a palavra-passe correta na barra lateral para aceder à administração.")
        return

    menu_admin = st.sidebar.selectbox("Secção Administrativa", [
        "📊 Dashboard & Resumo", 
        "🧮 Gestão de Caixa", 
        "🪑 QR Codes & Mesas", 
        "📖 Gestão da Ementa", 
        "📦 Stock", 
        "👥 Recursos Humanos"
    ])

    if menu_admin == "📊 Dashboard & Resumo":
        st.subheader("📊 Indicadores de Desempenho")
        historico = carregar_historico_vendas()
        
        c1, c2, c3 = st.columns(3)
        total_vendas_geral = sum(v.get("Valor Dinheiro", 0) + v.get("Valor TPA", 0) for v in historico)
        with c1:
            st.metric("Total Faturado", f"{total_vendas_geral:,.2f} Kz")
        with c2:
            st.metric("Total de Vendas Registadas", len(historico))
        with c3:
            st.metric("Estado do Caixa", "Aberto" if st.session_state.caixa_aberto else "Fechado")
            
        st.markdown("---")
        st.subheader("📋 Histórico de Vendas Recentes")
        if historico:
            df_hist = pd.DataFrame(historico)
            st.dataframe(df_hist[['Data', 'Mesa', 'Cliente', 'Forma']], use_container_width=True)
        else:
            st.info("Ainda sem vendas registadas no histórico.")

    elif menu_admin == "🧮 Gestão de Caixa":
        st.subheader("🧮 Abertura e Fecho de Caixa")
        
        estado_atual = ler_estado_caixa_disco()
        st.write(h:="O caixa encontra-se atualmente: **" + ("ABERTO" if estado_atual else "FECHADO") + "**")
        
        c_abrir, c_fechar = st.columns(2)
        with c_abrir:
            if st.button("🟢 Abrir Caixa", use_container_width=True):
                salvar_estado_caixa_disco(True)
                st.session_state.caixa_aberto = True
                st.success("Caixa aberto com sucesso!")
                st.rerun()
        with c_fechar:
            if st.button("🔴 Fechar Caixa", use_container_width=True):
                salvar_estado_caixa_disco(False)
                st.session_state.caixa_aberto = False
                st.success("Caixa fechado com sucesso!")
                st.rerun()

    elif menu_admin == "🪑 QR Codes & Mesas":
        st.subheader("🪑 Gerador de QR Codes para as Mesas (1 a 30)")
        st.write("Imprima estes QR Codes para colocar em cada mesa do restaurante. Os clientes poderão ler para aceder diretamente à ementa e efetuar pedidos.")
        
        # URL base da aplicação (ajuste conforme o seu domínio Streamlit Cloud ou localhost)
        base_url_app = st.text_input("URL Base da Aplicação (ex: https://nombresabor.streamlit.app):", value="http://localhost:8501")
        
        num_mesa_qr = st.selectbox("Selecione a Mesa para Gerar QR Code:", list(range(1, 31)))
        
        url_mesa = f"{base_url_app}/?mesa={num_mesa_qr}"
        st.write(h:=f"Link gerado para a Mesa {num_mesa_qr}: `{url_mesa}`")
        
        # Gerar imagem QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_mesa)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        st.image(buffered.getvalue(), caption=f"QR Code - Mesa {num_mesa_qr}", width=300)

    elif menu_admin == "📖 Gestão da Ementa":
        st.subheader("📖 Adicionar ou Remover Pratos/Bebidas")
        st.dataframe(st.session_state.menu_itens, use_container_width=True)
        
        with st.form("form_novo_item"):
            st.markdown("### Adicionar Novo Item")
            ni_nome = st.text_input("Nome do Item:")
            ni_cat = st.selectbox("Categoria:", ["Pratos Principais", "Pratos Tradicionais", "Bebidas", "Sobremesas", "Entradas"])
            ni_preco = st.number_input("Preço (Kz):", min_value=0.0, step=100.0)
            ni_stock = st.number_input("Stock Inicial:", min_value=0, value=50)
            
            btn_add_menu = st.form_submit_button("Adicionar à Ementa")
            if btn_add_menu:
                if ni_nome.strip():
                    novo_df = pd.DataFrame([{"Item": ni_nome, "Categoria": ni_cat, "Preço (Kz)": ni_preco, "Stock": ni_stock}])
                    st.session_state.menu_itens = pd.concat([st.session_state.menu_itens, novo_df], ignore_index=True)
                    st.success("Item adicionado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Introduza o nome do item.")

    elif menu_admin == "📦 Stock":
        st.subheader("📦 Controlo de Stock Atual")
        st.dataframe(st.session_state.menu_itens[['Item', 'Categoria', 'Stock']], use_container_width=True)

    elif menu_admin == "👥 Recursos Humanos":
        st.subheader("👥 Gestão de Colaboradores")
        st.dataframe(st.session_state.rh, use_container_width=True)
        
        with st.form("form_novo_rh"):
            st.markdown("### Registar Novo Colaborador")
            nc = st.text_input("Nome Completo:")
            ccod = st.text_input("Código (ex: EMP003):")
            ccargo = st.selectbox("Cargo:", ["Chefe de Cozinha", "Empregada de Mesa", "Caixa", "Gerente"])
            ctel = st.text_input("Contacto Telefónico:")
            
            btn_reg_rh = st.form_submit_button("Registar Colaborador")
            if btn_reg_rh:
                if nc.strip():
                    novo_colab = pd.DataFrame([{"Código": ccod, "Nome": nc, "Cargo": ccargo, "Contacto": ctel}])
                    st.session_state.rh = pd.concat([st.session_state.rh, novo_colab], ignore_index=True)
                    st.success(f"Colaborador {nc.strip()} registado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Por favor, insira o nome completo.")


# ==========================================
# ÁREA: CAIXA (Gestão de Mesas & Faturação)
# ==========================================
def area_caixa():
    st.title("🧮 Painel de Caixa - Gestão de Mesas & Pagamentos")
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** Abra o caixa no painel de administração para poder gerir pagamentos.")
        return

    st.markdown("### 🪑 Estado Geral das Mesas (1 a 30)")
    
    cols_por_linha = 6
    for linha in range(0, 30, cols_por_linha):
        cols = st.columns(cols_por_linha)
        for j in range(cols_por_linha):
            num_m = linha + j + 1
            if num_m > 30:
                break
            
            str_m = str(num_m)
            dados_m = mesas_data[str_m]
            status_m = dados_m.get("status", "Fechada")
            
            with cols[j]:
                tem_pronto = any(p.get("cozinha_status") == "Feito" for p in dados_m["pedidos"])
                
                if tem_pronto:
                    st.markdown(f"""
                        <div class="mesa-pronta-alerta">
                            <b>Mesa {num_m}</b><br>🔔 Prato Pronto!
                        </div>
                    """, unsafe_allow_html=True)
                elif status_m == "Aberta":
                    st.markdown(f"""
                        <div class="mesa-aberta">
                            <b>Mesa {num_m}</b><br>🟢 Aberta ({dados_m.get('total', 0):,.2f} Kz)
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="mesa-fechada">
                            <b>Mesa {num_m}</b><br>🔒 Fechada
                        </div>
                    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("⚙️ Gestão Detalhada por Mesa")
    
    mesa_selecionada = st.selectbox("Selecione a Mesa para Fecho ou Consulta:", list(range(1, 31)), format_func=lambda x: f"Mesa {x}")
    str_ms = str(mesa_selecionada)
    m_info = mesas_data[str_ms]
    
    st.write(f"**Estado da Mesa {mesa_selecionada}:** {m_info['status']}")
    if m_info.get("cliente"):
        st.write(f"**Cliente:** {m_info['cliente']['nome']} | **Telefone:** {m_info['cliente']['telefone']}")
    
    pedidos_m = m_info["pedidos"]
    if pedidos_m:
        st.markdown("#### Pedidos Registados:")
        subtotal_mesa = 0
        for idx, item in enumerate(pedidos_m):
            t_item = item['quantidade'] * item['preco']
            if item['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                subtotal_mesa += t_item
            st.write(f"- {item['quantidade']}x {item['item']} ({t_item:,.2f} Kz) — Estado: **{item['status']}** / Cozinha: **{item.get('cozinha_status', 'N/A')}**")
        
        st.markdown(f"### Total Atual: **{subtotal_mesa:,.2f} Kz**")
        
        with st.form(f"form_pagamento_mesa_{mesa_selecionada}"):
            st.markdown("#### 💳 Efetuar Pagamento & Emitir Fatura")
            nome_fat = st.text_input("Nome para Fatura:", value=m_info['cliente']['nome'] if m_info.get('cliente') else "")
            tel_fat = st.text_input("Telefone / NIF:", value=m_info['cliente']['telefone'] if m_info.get('cliente') else "")
            forma_pag = st.selectbox("Forma de Pagamento:", ["Dinheiro", "TPA (Multicaixa)", "Transferência Bancária"])
            
            btn_pagar = st.form_submit_button("💰 Confirmar Pagamento & Fechar Mesa", use_container_width=True)
            
            if btn_pagar:
                if subtotal_mesa > 0:
                    hist = carregar_historico_vendas()
                    reg_venda = {
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Mesa": mesa_selecionada,
                        "Cliente": nome_fat,
                        "Valor Dinheiro": subtotal_mesa if forma_pag == "Dinheiro" else 0.0,
                        "Valor TPA": subtotal_mesa if forma_pag in ["TPA (Multicaixa)", "Transferência Bancária"] else 0.0,
                        "Forma": forma_pag,
                        "Itens": pedidos_m
                    }
                    hist.append(reg_venda)
                    salvar_historico_vendas(hist)
                    
                    m_info["fatura_emitida"] = {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": nome_fat,
                        "telefone": tel_fat,
                        "itens": pedidos_m,
                        "total": subtotal_mesa,
                        "pagamento_detalhe": forma_pag
                    }
                    m_info["status"] = "Fechada"
                    m_info["pedidos"] = []
                    m_info["total"] = 0.0
                    m_info["cliente"] = None
                    
                    salvar_mesas_disco(mesas_data)
                    st.success(f"Pagamento de {subtotal_mesa:,.2f} Kz processado com sucesso! Mesa {mesa_selecionada} fechada.")
                    st.rerun()
                else:
                    st.warning("Esta mesa não tem valor a pagar.")
    else:
        st.info("Nenhum pedido efetuado nesta mesa.")


# ==========================================
# ROTEADOR PRINCIPAL DO SISTEMA
# ==========================================
def main():
    if perfil_url == "cozinha":
        area_cozinha()
    elif perfil_url == "caixa":
        area_caixa()
    elif perfil_url == "admin":
        area_administrador()
    else:
        if mesa_detectada and 1 <= mesa_detectada <= 30:
            area_cliente()
        else:
            # Painel principal por omissão (Administração)
            area_administrador()

if __name__ == "__main__":
    main()
