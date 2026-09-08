import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# Configuração da Página
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

ARQUIVO_ESTADO_CAIXA = "caixa_status.txt"
ARQUIVO_DADOS_MESAS = "mesas_dados.json"
ARQUIVO_HISTORICO_VENDAS = "historico_vendas.json"
ARQUIVO_SAIDAS_CAIXA = "saidas_caixa.json"
ARQUIVO_STOCK = "stock_dados.json"

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

def carregar_mesas_disco():
    if os.path.exists(ARQUIVO_DADOS_MESAS):
        try:
            with open(ARQUIVO_DADOS_MESAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {str(i): {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "fatura_emitida": None} for i in range(1, 31)}

def salvar_mesas_disco(mesas_dict):
    try:
        with open(ARQUIVO_DADOS_MESAS, "w", encoding="utf-8") as f:
            json.dump(mesas_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_historico_vendas():
    if os.path.exists(ARQUIVO_HISTORICO_VENDAS):
        try:
            with open(ARQUIVO_HISTORICO_VENDAS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if dados:
                    return dados
        except:
            pass
    
    ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    dados_exemplo = [
        {
            "Data": ontem,
            "Mesa": 3,
            "Cliente": "Carlos Silva",
            "Telefone": "923111222",
            "Valor Total": 12500.0,
            "Valor Dinheiro": 12500.0,
            "Valor TPA": 0.0,
            "Modo Pagamento": "Dinheiro"
        },
        {
            "Data": ontem,
            "Mesa": 7,
            "Cliente": "Maria Santos",
            "Telefone": "912333444",
            "Valor Total": 8400.0,
            "Valor Dinheiro": 0.0,
            "Valor TPA": 8400.0,
            "Modo Pagamento": "TPA"
        },
        {
            "Data": hoje,
            "Mesa": 1,
            "Cliente": "António Costa",
            "Telefone": "935666777",
            "Valor Total": 15000.0,
            "Valor Dinheiro": 5000.0,
            "Valor TPA": 10000.0,
            "Modo Pagamento": "Dinheiro: 5,000.00 Kz | TPA: 10,000.00 Kz"
        }
    ]
    salvar_historico_vendas(dados_exemplo)
    return dados_exemplo

def salvar_historico_vendas(hist_list):
    try:
        with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
            json.dump(hist_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_saidas_caixa():
    if os.path.exists(ARQUIVO_SAIDAS_CAIXA):
        try:
            with open(ARQUIVO_SAIDAS_CAIXA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_saidas_caixa(saidas_list):
    try:
        with open(ARQUIVO_SAIDAS_CAIXA, "w", encoding="utf-8") as f:
            json.dump(saidas_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_stock_disco():
    if os.path.exists(ARQUIVO_STOCK):
        try:
            df_loaded = pd.read_json(ARQUIVO_STOCK)
            if not df_loaded.empty:
                return df_loaded
        except:
            pass
    return pd.DataFrame([
        ["Água 0.5L", "Bebidas", 50, 300.0],
        ["Refrigerante Cola", "Bebidas", 40, 450.0],
        ["Cerveja Cuca", "Bebidas", 60, 500.0],
        ["Vinho Tinto", "Bebidas", 15, 4500.0],
        ["Frango à Grega", "Refeições", 20, 3500.0],
        ["Bife a Cavalo", "Refeições", 15, 4000.0],
        ["Pudim de Leite", "Sobremesas", 25, 1500.0],
        ["Salada de Frutas", "Sobremesas", 30, 1200.0]
    ], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

def salvar_stock_disco(df):
    try:
        df.to_json(ARQUIVO_STOCK, orient="split", index=False)
    except:
        pass

# Estilos CSS Corrigidos (Texto preto nos inputs e dropdowns abertos)
st.markdown("""
    <style>
    .stApp, body, html {
        background-color: #0c0c16 !important;
    }
    
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 62% !important;
        margin: 0 auto !important;
        background-color: #0c0c16 !important;
    }

    html, body, [class*="css"], .stMarkdown, p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Correção para forçar texto preto dentro dos inputs, selects e listas suspensas abertas */
    input, select, option, div[data-baseweb="select"] *, div[data-baseweb="popover"] *, [data-baseweb="menu"] * {
        color: #000000 !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .mesa-circle {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        margin: 0 auto 4px auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    .mesa-aberta {
        border: 3px solid #2ea44f;
        background-color: #0f2316;
        color: #4ac26b !important;
    }

    .mesa-fechada {
        border: 3px solid #30363d;
        background-color: #161b22;
        color: #ffffff !important;
    }

    .mesa-pronta-alerta {
        border: 3px solid #ff4b4b;
        background-color: #2b0d0d;
        color: #ff6b6b !important;
        animation: borda-vermelha-piscar 1s infinite;
    }

    @keyframes borda-vermelha-piscar {
        0% { border: 3px solid #ff4b4b; box-shadow: 0 0 10px #ff4b4b; }
        50% { border: 3px solid #ffa0a0; box-shadow: none; }
        100% { border: 3px solid #ff4b4b; box-shadow: 0 0 10px #ff4b4b; }
    }

    .fatura-box {
        background-color: #141428;
        border: 2px dashed #ffb703;
        padding: 15px;
        border-radius: 10px;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: bold !important;
        padding: 4px 8px !important;
        font-size: 0.85rem !important;
        color: #000000 !important;
    }
    
    .stButton>button p, .stButton>button span {
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Captura de Parâmetros da URL
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

st.session_state.caixa_aberto = ler_estado_caixa_disco()

if "stock" not in st.session_state:
    st.session_state.stock = carregar_stock_disco()

if "rh" not in st.session_state:
    st.session_state.rh = pd.DataFrame([
        ["G001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042"],
        ["G002", "Ana Paula", "Garçon", "912333444", "009876543LA031"]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])

# ==========================================
# ÁREA: CLIENTE
# ==========================================
@st.fragment(run_every=4)
def area_cliente():
    if mesa_detectada and 1 <= mesa_detectada <= 30:
        num_mesa = mesa_detectada
    else:
        st.error("⚠️ Nenhum número de mesa detetado no link! Por favor, escaneie o QR Code correto da sua mesa.")
        return

    mesas_data = carregar_mesas_disco()
    str_mesa = str(num_mesa)
    dados_m = mesas_data[str_mesa]

    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<div class='fatura-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🧾 Restaurante Nobre Sabor - Fatura / Recibo</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><b>Mesa:</b> {num_mesa} | <b>Data:</b> {fat['data']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><b>Cliente:</b> {fat['cliente']} | <b>Telefone:</b> {fat['telefone']}</p>", unsafe_allow_html=True)
        st.divider()
        
        for item in fat['itens']:
            st.write(f"- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.2f} Kz")
        
        st.markdown(f"### Total Pago: **{fat['total']:,.2f} Kz**")
        st.markdown(f"<p><b>Forma de Pagamento:</b> {fat['pagamento_detalhe']}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<h3 style='text-align: center;'>🙏 Muito obrigado pela sua presença no Restaurante Nobre Sabor! Volte sempre!</h3>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not dados_m.get("cliente"):
        st.markdown("<h2 style='text-align: center;'>🍽️ Bem-vindo ao Restaurante Nobre Sabor</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>Registo de Entrada - Mesa {num_mesa}</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form(f"form_cli_{num_mesa}"):
                nome_cli = st.text_input("Nome:")
                tel_cli = st.text_input("Telefone:")
                whatsapp_opt = st.checkbox("Deseja entrar no Grupo de WhatsApp?")
                
                btn_reg = st.form_submit_button("Entrar e Ver Menu", use_container_width=True)
                if btn_reg and nome_cli and tel_cli:
                    dados_m["cliente"] = {
                        "nome": nome_cli,
                        "telefone": tel_cli,
                        "whatsapp": whatsapp_opt
                    }
                    dados_m["status"] = "Aberta"
                    salvar_mesas_disco(mesas_data)
                    st.success("Registo efetuado com sucesso!")
                    st.rerun()
                elif btn_reg:
                    st.warning("Preencha o seu nome e telefone.")
    else:
        cli = dados_m["cliente"]
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background-color: #141428; padding: 10px 14px; border-radius: 8px; border: 1px solid #2a2a4a; margin-bottom: 10px;">
                <span style="font-size: 1.1rem; color: #ffb703;">🍽️ NobreSabor | Mesa {num_mesa}</span>
                <span style="font-size: 0.9rem;">👤 Bem-vindo(a), <b>{cli['nome']}</b></span>
            </div>
        """, unsafe_allow_html=True)
        
        categorias_disponiveis = st.session_state.stock['Categoria'].unique().tolist()
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo & Fatura", "🎉 Programas"])
        
        with tab_menu:
            cat_escolhida = st.selectbox("Categoria:", categorias_disponiveis, key="cat_cli_sel")
            stock_df = st.session_state.stock
            itens_cat = stock_df[stock_df['Categoria'] == cat_escolhida]
            
            if not itens_cat.empty:
                with st.form(key=f"form_pedido_{num_mesa}", clear_on_submit=True):
                    col_f1, col_f2 = st.columns([2, 1])
                    with col_f1:
                        item_escolhido = st.selectbox("Item:", itens_cat['Produto'].tolist())
                    with col_f2:
                        qtd = st.number_input("Qtd:", min_value=1, value=1)
                    
                    obs = st.text_input("Observações (Ex: Sem gelo, bem passado):")
                    
                    btn_enviar_pedido = st.form_submit_button("🚀 Enviar Pedido", use_container_width=True)
                    
                    if btn_enviar_pedido:
                        row_prod = itens_cat[itens_cat['Produto'] == item_escolhido].iloc[0]
                        is_refeicao = (cat_escolhida.lower() in ["refeições", "refeicoes", "pratos", "comida"])
                        novo_pedido = {
                            "item": item_escolhido,
                            "tipo": cat_escolhida,
                            "quantidade": int(qtd),
                            "preco": float(row_prod['Preço Unitário']),
                            "origem": f"Cliente ({cli['nome']})",
                            "obs": obs,
                            "status": "Confirmado" if not is_refeicao else "Pendente",
                            "cozinha_status": "N/A" if not is_refeicao else "Pendente",
                            "hora": datetime.now().strftime("%H:%M:%S")
                        }
                        
                        dados_m["pedidos"].append(novo_pedido)
                        dados_m["status"] = "Aberta"
                        
                        total_calc = sum(
                            p['quantidade'] * p['preco'] 
                            for p in dados_m["pedidos"] 
                            if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                        )
                        dados_m["total"] = float(total_calc)
                        
                        salvar_mesas_disco(mesas_data)
                        
                        st.session_state[f"aviso_pedido_enviado_{num_mesa}"] = f"✅ Pedido de {qtd}x {item_escolhido} enviado!"
                        st.rerun()

            chave_aviso = f"aviso_pedido_enviado_{num_mesa}"
            if chave_aviso in st.session_state:
                st.success(st.session_state[chave_aviso])
                del st.session_state[chave_aviso]
                
        with tab_consumo:
            st.subheader("O Meu Consumo & Estado dos Pedidos")
            pedidos_mesa = dados_m["pedidos"]
            if not pedidos_mesa:
                st.info("Ainda não tem pedidos.")
            else:
                subtotal_geral = 0
                for p in pedidos_mesa:
                    total_item = p['quantidade'] * p['preco']
                    if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                        subtotal_geral += total_item
                    
                    status_txt = p['status']
                    if p.get('cozinha_status') == "Feito":
                        status_txt = "🍽️ Refeição Pronta!"
                    elif p.get('cozinha_status') == "Aprovado":
                        status_txt = "Preparando 🍳"
                        
                    st.write(f"- {p['quantidade']}x {p['item']} | {total_item:,.2f} Kz — **{status_txt}**")
                    
                st.markdown(f"### Total: {subtotal_geral:,.2f} Kz")
                
        with tab_eventos:
            st.subheader("Eventos da Semana")
            st.markdown("- Sexta: Música ao Vivo\n- Sábado: Karaoke (Grupo FF Karaoke)")

# ==========================================
# ÁREA: COZINHA
# ==========================================
@st.fragment(run_every=6)
def area_cozinha():
    st.title("🍳 Área da Cozinha - Gestão de Refeições")
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.**")
        return

    tem_pedidos = False
    for i in range(1, 31):
        str_i = str(i)
        dados_m = mesas_data[str_i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            cat_p = str(ped.get("tipo", "")).lower()
            if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
                tem_pedidos = True
                
                col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                with col_c1:
                    st.write(f"### 🍽️ Mesa {i}")
                    st.write(f"**Refeição:** {ped['item']} | **Qtd:** {ped['quantidade']}")
                    st.write(f"Obs: _{ped['obs']}_")
                with col_c2:
                    st.write(f"Estado: **{ped.get('cozinha_status', 'Pendente')}**")
                with col_c3:
                    estado_atual = ped.get('cozinha_status', 'Pendente')
                    if estado_atual == "Pendente":
                        if st.button("✅ Aprovar", key=f"aprov_cz_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                            mesas_data[str_i]["pedidos"][idx_p]["status"] = "Confirmado"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
                        if st.button("❌ Recusar", key=f"rec_cz_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Recusado"
                            mesas_data[str_i]["pedidos"][idx_p]["status"] = "Recusado pela Cozinha"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
                    elif estado_atual == "Aprovado":
                        if st.button("🍲 Marcar Feito", key=f"feito_cz_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
                st.divider()
                
    if not tem_pedidos:
        st.success("🎉 Sem refeições pendentes de momento!")

# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
def area_administrador():
    st.markdown("<h1>👑 Painel do Administrador - NobreSabor</h1>", unsafe_allow_html=True)
    tab_fin, tab_saidas, tab_stk, tab_dch = st.tabs(["💰 Finanças & Histórico", "💸 Saídas de Caixa", "📦 Stock & Menu", "👥 DCH"])
    
    with tab_fin:
        if "financas_autenticado" not in st.session_state:
            st.session_state.financas_autenticado = False

        if not st.session_state.financas_autenticado:
            with st.form("form_senha_financas"):
                senha_digitada = st.text_input("Senha:", type="password")
                if st.form_submit_button("Desbloquear Finanças"):
                    if senha_digitada == "123123123":
                        st.session_state.financas_autenticado = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta!")
        else:
            if st.button("🔒 Bloquear Finanças"):
                st.session_state.financas_autenticado = False
                st.rerun()
            st.success("Finanças desbloqueadas com sucesso.")
            
            st.subheader("📊 Histórico de Faturação e Vendas Registadas")
            hist_vendas = carregar_historico_vendas()
            
            if not hist_vendas:
                st.info("Ainda não existem vendas faturadas registadas.")
            else:
                df_vendas = pd.DataFrame(hist_vendas)
                st.dataframe(df_vendas, use_container_width=True)
                
                total_geral_faturado = df_vendas['Valor Total'].sum() if 'Valor Total' in df_vendas.columns else 0
                st.markdown(f"### Faturação Total Acumulada: **{total_geral_faturado:,.2f} Kz**")

    with tab_saidas:
        st.subheader("💸 Gestão e Registo de Saídas de Caixa")
        
        with st.form("form_registar_saida"):
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                motivo_saida = st.text_input("Motivo da Saída (Ex: Compra de Gelo, Trocos, Pagamento Fornecedor):")
            with col_sc2:
                valor_saida = st.number_input("Valor da Saída (Kz):", min_value=0.0, value=1000.0, step=500.0)
            
            responsavel_saida = st.text_input("Responsável / Autorizado por:")
            
            btn_salvar_saida = st.form_submit_button("🚀 Registar Saída de Caixa", use_container_width=True)
            if btn_salvar_saida and motivo_saida and valor_saida > 0:
                saidas_list = carregar_saidas_caixa()
                nova_saida = {
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Motivo": motivo_saida,
                    "Valor": float(valor_saida),
                    "Responsável": responsavel_saida if responsavel_saida else "Administração"
                }
                saidas_list.append(nova_saida)
                salvar_saidas_caixa(saidas_list)
                st.success("Saída de caixa registada com sucesso!")
                st.rerun()

        st.divider()
        st.markdown("#### Histórico de Saídas de Caixa")
        saidas_registadas = carregar_saidas_caixa()
        if not saidas_registadas:
            st.info("Nenhuma saída de caixa registada.")
        else:
            df_saidas = pd.DataFrame(saidas_registadas)
            st.dataframe(df_saidas, use_container_width=True)
            total_saidas = df_saidas['Valor'].sum() if 'Valor' in df_saidas.columns else 0
            st.markdown(f"### Total Retirado em Saídas: **{total_saidas:,.2f} Kz**")

    with tab_stk:
        st.subheader("📦 Gestão de Stock e Produtos/Pratos")
        
        with st.form("form_add_produto"):
            st.markdown("#### Adicionar / Atualizar Item no Menu")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                novo_produto = st.text_input("Nome do Produto/Prato:")
                nova_categoria = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas", "Entradas", "Outros"])
            with col_s2:
                nova_qtd = st.number_input("Quantidade em Stock:", min_value=0, value=10)
                novo_preco = st.number_input("Preço Unitário (Kz):", min_value=0.0, value=500.0, step=100.0)
                
            btn_salvar_prod = st.form_submit_button("💾 Salvar / Atualizar Produto", use_container_width=True)
            if btn_salvar_prod and novo_produto:
                df_stk = st.session_state.stock
                if not df_stk.empty and novo_produto in df_stk['Produto'].values:
                    df_stk.loc[df_stk['Produto'] == novo_produto, ['Categoria', 'Quantidade', 'Preço Unitário']] = [nova_categoria, nova_qtd, novo_preco]
                    st.success(f"Produto '{novo_produto}' atualizado com sucesso!")
                else:
                    novo_df_linha = pd.DataFrame([[novo_produto, nova_categoria, nova_qtd, novo_preco]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                    st.session_state.stock = pd.concat([df_stk, novo_df_linha], ignore_index=True)
                    st.success(f"Produto '{novo_produto}' adicionado com sucesso!")
                
                salvar_stock_disco(st.session_state.stock)
                st.rerun()

        st.divider()
        st.markdown("#### Lista Atual de Produtos")
        st.dataframe(st.session_state.stock, use_container_width=True)
        
        if not st.session_state.stock.empty:
            with st.form("form_del_produto"):
                produto_a_remover = st.selectbox("Selecionar produto para remover:", st.session_state.stock['Produto'].tolist())
                btn_remover = st.form_submit_button("🗑️ Remover Produto Selecionado", use_container_width=True)
                if btn_remover:
                    st.session_state.stock = st.session_state.stock[st.session_state.stock['Produto'] != produto_a_remover].reset_index(drop=True)
                    salvar_stock_disco(st.session_state.stock)
                    st.success(f"Produto '{produto_a_remover}' removido!")
                    st.rerun()
        
    with tab_dch:
        st.dataframe(st.session_state.rh, use_container_width=True)

# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS
# ==========================================
@st.fragment(run_every=6)
def area_caixa_mesas():
    st.markdown("<h3 style='margin-bottom:8px;'>💻 Controlo Geral de Mesas e Faturação (Caixa)</h3>", unsafe_allow_html=True)
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()
    hist_vendas = carregar_historico_vendas()

    col_cx_btn1, col_cx_btn2 = st.columns([1, 4])
    with col_cx_btn1:
        if st.session_state.caixa_aberto:
            if st.button("🔒 Fechar Caixa", type="primary"):
                gravar_estado_caixa_disco(False)
                st.session_state.caixa_aberto = False
                st.rerun()
        else:
            if st.button("🟢 Abrir Caixa", type="primary"):
                gravar_estado_caixa_disco(True)
                st.session_state.caixa_aberto = True
                st.rerun()
    with col_cx_btn2:
        if not st.session_state.caixa_aberto:
            st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** Abra o caixa para iniciar operações.")
            return

    total_dinheiro_caixa = sum(float(v.get('Valor Dinheiro', 0)) for v in hist_vendas)
    total_tpa_caixa = sum(float(v.get('Valor TPA', 0)) for v in hist_vendas)
    total_geral_caixa = total_dinheiro_caixa + total_tpa_caixa

    st.markdown(f"""
        <div style="background-color: #141428; padding: 12px 18px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #2a2a4a; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2a2a4a; padding-bottom: 8px;">
                <span style="font-size: 1.15rem;">📊 Total: <b style="color: #4ac26b; font-size: 1.25rem;">{total_geral_caixa:,.2f} Kz</b></span>
                <span style="font-size: 0.85rem; background-color: #0f2316; color: #4ac26b; padding: 3px 10px; border-radius: 12px; border: 1px solid #2ea44f;">🟢 Aberto</span>
            </div>
            <div style="display: flex; justify-content: space-around; align-items: center; padding-top: 2px;">
                <span style="font-size: 0.95rem;">💵 Dinheiro: <b>{total_dinheiro_caixa:,.2f} Kz</b></span>
                <span style="font-size: 0.95rem;">💳 TPA: <b>{total_tpa_caixa:,.2f} Kz</b></span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1.1, 0.9], gap="medium")

    with col_esq:
        if "mesa_ativa" in st.session_state:
            m_ativa = st.session_state.mesa_ativa
            str_m_ativa = str(m_ativa)
                
            st.markdown(f"### 🎛️ Gestão da Mesa {m_ativa}")
            dados_mesa = mesas_data[str_m_ativa]
            
            if dados_mesa.get("fatura_emitida"):
                st.success("✅ Esta mesa já teve a conta fechada e a fatura emitida.")
                if st.button("🧹 Limpar e Liberar Mesa", type="primary", key=f"btn_limpar_{m_ativa}"):
                    mesas_data[str_m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "fatura_emitida": None}
                    salvar_mesas_disco(mesas_data)
                    del st.session_state.mesa_ativa
                    st.rerun()
                return

            total_calculado = sum(
                float(p['quantidade']) * float(p['preco']) 
                for p in dados_mesa['pedidos'] 
                if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
            )
            dados_mesa['total'] = float(total_calculado)
            salvar_mesas_disco(mesas_data)

            if dados_mesa.get("cliente"):
                cli = dados_mesa["cliente"]
                st.info(f"👤 **Cliente:** {cli['nome']} | 📞 {cli['telefone']}")

            st.markdown("#### 📝 Pedidos Lançados")
            if not dados_mesa['pedidos']:
                st.info("Nenhum pedido efetuado nesta mesa ainda.")
            else:
                for idx_p, p in enumerate(dados_mesa['pedidos']):
                    col_p1, col_p2, col_p3 = st.columns([3, 2, 2])
                    with col_p1:
                        st.write(f"- {p['quantidade']}x {p['item']}")
                    with col_p2:
                        st.write(f"**{(float(p['quantidade']) * float(p['preco'])):,.2f} Kz**")
                    with col_p3:
                        c_status = p.get('cozinha_status', 'N/A')
                        if c_status == "Feito":
                            st.markdown("🍽️ **Pronta**")
                            cat_p = str(p.get("tipo", "")).lower()
                            if "refei" in cat_p or "prato" in cat_p or "comida" in cat_p:
                                if st.button("✅ Adicionar Refeição", key=f"btn_baixa_ref_{m_ativa}_{idx_p}"):
                                    mesas_data[str_m_ativa]["pedidos"][idx_p]["cozinha_status"] = "Entregue"
                                    salvar_mesas_disco(mesas_data)
                                    st.rerun()
                        elif c_status == "Entregue":
                            st.markdown("✅ **Entregue**")
                        else:
                            st.write(f"Est: `{p['status']}`")

            st.markdown(f"#### Total a Pagar: **{float(dados_mesa['total']):,.2f} Kz**")

            if float(dados_mesa['total']) > 0:
                st.markdown("---")
                st.markdown("#### 💳 Pagamento")
                tipo_pagamento = st.selectbox("Modalidade:", ["Dinheiro", "TPA", "Ambos (Dinheiro + TPA)"], key=f"pag_tipo_{m_ativa}")
                
                val_dinheiro = 0.0
                val_tpa = 0.0
                
                if tipo_pagamento == "Dinheiro":
                    val_dinheiro = float(dados_mesa['total'])
                elif tipo_pagamento == "TPA":
                    val_tpa = float(dados_mesa['total'])
                else:
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        val_dinheiro = st.number_input("Dinheiro (Kz):", min_value=0.0, max_value=float(dados_mesa['total']), value=float(dados_mesa['total'])/2, key=f"din_{m_ativa}")
                    with col_m2:
                        val_tpa = float(dados_mesa['total']) - float(val_dinheiro)
                        st.info(f"TPA: **{val_tpa:,.2f} Kz**")

                if st.button("💳 Fechar Conta e Emitir Fatura", type="primary", key=f"btn_fechar_{m_ativa}"):
                    nome_c_fatura = dados_mesa['cliente']['nome'] if dados_mesa.get('cliente') and isinstance(dados_mesa['cliente'], dict) else 'Cliente Mesa'
                    tel_c_fatura = dados_mesa['cliente']['telefone'] if dados_mesa.get('cliente') and isinstance(dados_mesa['cliente'], dict) else 'N/A'
                    
                    detalhe_pag = f"Dinheiro: {val_dinheiro:,.2f} Kz | TPA: {val_tpa:,.2f} Kz" if tipo_pagamento == "Ambos (Dinheiro + TPA)" else tipo_pagamento

                    novo_registo_venda = {
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Mesa": int(m_ativa),
                        "Cliente": str(nome_c_fatura),
                        "Telefone": str(tel_c_fatura),
                        "Valor Total": float(dados_mesa["total"]),
                        "Valor Dinheiro": float(val_dinheiro),
                        "Valor TPA": float(val_tpa),
                        "Modo Pagamento": str(detalhe_pag)
                    }
                    hist_vendas.append(novo_registo_venda)
                    salvar_historico_vendas(hist_vendas)

                    dados_mesa["fatura_emitida"] = {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": str(nome_c_fatura),
                        "telefone": str(tel_c_fatura),
                        "itens": list(dados_mesa["pedidos"]),
                        "total": float(dados_mesa["total"]),
                        "pagamento_detalhe": str(detalhe_pag)
                    }
                    
                    dados_mesa["status"] = "Fechada"
                    salvar_mesas_disco(mesas_data)
                    st.success("Conta fechada com sucesso! Fatura emitida e gravada no histórico.")
                    del st.session_state.mesa_ativa
                    st.rerun()
        else:
            st.info("👈 Selecione uma mesa no lado direito para gerir.")

    with col_dir:
        st.markdown("#### 🪑 Mesas do Restaurante")
        cols_por_linha = 4
        for linha in range(8):
            cols = st.columns(cols_por_linha)
            for c in range(cols_por_linha):
                num_mesa = linha * cols_por_linha + c + 1
                if num_mesa <= 30:
                    str_num = str(num_mesa)
                    dados_m = mesas_data[str_num]
                    status_m = dados_m["status"]
                    
                    total_m = sum(
                        float(p['quantidade']) * float(p['preco']) 
                        for p in dados_m['pedidos'] 
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )
                    dados_m['total'] = float(total_m)
                    
                    tem_refeicao_pronta = any(
                        ("refei" in str(p.get("tipo", "")).lower() or "prato" in str(p.get("tipo", "")).lower()) and p.get("cozinha_status") == "Feito" 
                        for p in dados_m['pedidos']
                    )
                    
                    classe_css = "mesa-pronta-alerta" if tem_refeicao_pronta else ("mesa-aberta" if status_m == "Aberta" else "mesa-fechada")
                    
                    with cols[c]:
                        alerta_pronto_html = "🚨 " if tem_refeicao_pronta else ""
                        nome_cli_formatado = f"<div style='font-size: 0.58rem; max-width: 55px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{dados_m['cliente']['nome']}</div>" if dados_m.get('cliente') else f"<div style='font-size: 0.58rem;'>{status_m}</div>"
                        valor_formatado = f"<div style='font-size: 0.62rem; font-weight: bold;'>{dados_m['total']:,.0f}Kz</div>"

                        conteudo_html = f"""
                        <div class='mesa-circle {classe_css}'>
                            <div style='font-size: 0.7rem; line-height: 1.0;'>{alerta_pronto_html}M{num_mesa}</div>
                            {nome_cli_formatado}
                            {valor_formatado}
                        </div>
                        """
                        st.markdown(conteudo_html, unsafe_allow_html=True)
                        
                        if st.button(f"Gerir {num_mesa}", key=f"btn_m_{num_mesa}", use_container_width=True):
                            st.session_state.mesa_ativa = num_mesa
                            st.rerun()
    
    salvar_mesas_disco(mesas_data)

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
