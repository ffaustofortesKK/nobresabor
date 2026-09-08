import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import io

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

# Estilos CSS Customizados
st.markdown("""
    <style>
        .main { background-color: #0e0e1a; color: #ffffff; }
        .stButton>button { border-radius: 8px; font-weight: bold; }
        .piscar-alerta {
            color: #ff4b4b;
            animation: piscar 1.5s infinite;
        }
        @keyframes piscar {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GESTÃO DE FICHEIROS E PERSISTÊNCIA (JSON)
# ==========================================
ARQUIVO_ESTADO_CAIXA = "estado_caixa.json"
ARQUIVO_HISTORICO_VENDAS = "historico_vendas.json"
ARQUIVO_FECHOS = "fechos_caixa.json"
ARQUIVO_SAIDAS = "saidas_caixa.json"
ARQUIVO_STOCK = "stock_menu.json"
ARQUIVO_RH = "recurso_humano.json"
ARQUIVO_ATENDIMENTOS = "atendimentos_garcon.json"
ARQUIVO_EXCLUIDAS = "vendas_excluidas.json"
ARQUIVO_MESAS = "estado_mesas.json"
ARQUIVO_SESSAO_OP = "sessao_operador.json"

def ler_json(arquivo, default):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def ler_estado_caixa_disco():
    return ler_json(ARQUIVO_ESTADO_CAIXA, False)

def gravar_estado_caixa_disco(estado):
    salvar_json(ARQUIVO_ESTADO_CAIXA, estado)

def carregar_historico_vendas():
    return ler_json(ARQUIVO_HISTORICO_VENDAS, [])

def salvar_historico_vendas(dados):
    salvar_json(ARQUIVO_HISTORICO_VENDAS, dados)

def carregar_fechos_caixa():
    return ler_json(ARQUIVO_FECHOS, [])

def salvar_fechos_caixa(dados):
    salvar_json(ARQUIVO_FECHOS, dados)

def carregar_saidas_caixa():
    return ler_json(ARQUIVO_SAIDAS, [])

def salvar_saidas_caixa(dados):
    salvar_json(ARQUIVO_SAIDAS, dados)

def carregar_stock_disco():
    dados = ler_json(ARQUIVO_STOCK, [])
    if not dados:
        df_init = pd.DataFrame([
            {"Produto": "Água Mineral", "Categoria": "Bebidas", "Quantidade": 100, "Preço Unitário": 300.0},
            {"Produto": "Refrigerante Cola", "Categoria": "Bebidas", "Quantidade": 80, "Preço Unitário": 500.0},
            {"Produto": "Cerveja Cuca", "Categoria": "Bebidas", "Quantidade": 120, "Preço Unitário": 600.0},
            {"Produto": "Funge com Carne Seca", "Categoria": "Refeição", "Quantidade": 40, "Preço Unitário": 3500.0},
            {"Produto": "Moamba de Galinha", "Categoria": "Refeição", "Quantidade": 35, "Preço Unitário": 4000.0},
            {"Produto": "Picanha Grelhada", "Categoria": "Refeição", "Quantidade": 25, "Preço Unitário": 6000.0},
            {"Produto": "Pudim de Leite", "Categoria": "Sobremesa", "Quantidade": 30, "Preço Unitário": 1500.0},
            {"Produto": "Salada de Frutas", "Categoria": "Sobremesa", "Quantidade": 25, "Preço Unitário": 1000.0},
        ])
        salvar_json(ARQUIVO_STOCK, df_init.to_dict(orient="records"))
        return df_init
    return pd.DataFrame(dados)

def salvar_stock_disco(df):
    salvar_json(ARQUIVO_STOCK, df.to_dict(orient="records"))

def carregar_rh_disco():
    dados = ler_json(ARQUIVO_RH, [])
    if not dados:
        df_init = pd.DataFrame([
            {"Código": "G001", "Nome": "Carlos Manuel", "Categoria": "Garçon", "Telefone": "923000001", "BI": "001234567LA042"},
            {"Código": "G002", "Nome": "Ana Paula", "Categoria": "Garçon", "Telefone": "923000002", "BI": "009876543LA041"}
        ])
        salvar_json(ARQUIVO_RH, df_init.to_dict(orient="records"))
        return df_init
    return pd.DataFrame(dados)

def salvar_rh_disco(df):
    salvar_json(ARQUIVO_RH, df.to_dict(orient="records"))

def carregar_atendimentos_garcon():
    return ler_json(ARQUIVO_ATENDIMENTOS, [])

def salvar_atendimentos_garcon(dados):
    salvar_json(ARQUIVO_ATENDIMENTOS, dados)

def carregar_vendas_excluidas():
    return ler_json(ARQUIVO_EXCLUIDAS, [])

def salvar_vendas_excluidas(dados):
    salvar_json(ARQUIVO_EXCLUIDAS, dados)

def carregar_sessao_operador():
    return ler_json(ARQUIVO_SESSAO_OP, {"logado": False, "operador": "", "periodo": "", "saldo_inicial": 0.0, "hora_abertura": ""})

def salvar_sessao_operador(dados):
    salvar_json(ARQUIVO_SESSAO_OP, dados)

def carregar_estado_mesas():
    # Inicializa todas as mesas zeradas / livres por padrão
    default_mesas = {f"Mesa {i}": {"itens": [], "estado": "Livre", "garcon": ""} for i in range(1, 13)}
    return ler_json(ARQUIVO_MESAS, default_mesas)

def salvar_estado_mesas(dados):
    salvar_json(ARQUIVO_MESAS, dados)

def converter_df_para_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatorio_NobreSabor')
    return output.getvalue()

# ==========================================
# INICIALIZAÇÃO DO SESSION STATE
# ==========================================
if "stock" not in st.session_state:
    st.session_state.stock = carregar_stock_disco()

if "caixa_aberto" not in st.session_state:
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

if "mesas" not in st.session_state:
    st.session_state.mesas = carregar_estado_mesas()

# ==========================================
# ROTEAMENTO DE URL (PARÂMETROS)
# ==========================================
query_params = st.query_params
mesa_detectada = query_params.get("mesa", None)
perfil_url = query_params.get("perfil", None)

# ==========================================
# ÁREA: CLIENTE (VIA QR CODE DA MESA)
# ==========================================
def area_cliente():
    st.markdown(f"<h1 style='text-align: center; color: #ffb703;'>🍽️ Restaurante NobreSabor - {mesa_detectada}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #d0d0e0;'>Faça o seu pedido diretamente da mesa com total comodidade.</p>", unsafe_allow_html=True)
    
    if not st.session_state.caixa_aberto:
        st.warning("🔴 O restaurante encontra-se atualmente encerrado ou com o sistema fechado pela Administração. Volte mais tarde!")
        return

    st.markdown("---")
    st.subheader("📋 Cardápio Disponível")
    
    df_stk = st.session_state.stock
    if df_stk.empty:
        st.info("O cardápio está temporariamente vazio.")
        return

    categorias = df_stk['Categoria'].unique().tolist()
    cat_selecionada = st.selectbox("Filtrar por Categoria:", ["Todas"] + categorias)
    
    if cat_selecionada != "Todas":
        df_filtrado = df_stk[df_stk['Categoria'] == cat_selecionada]
    else:
        df_filtrado = df_stk

    for index, row in df_filtrado.iterrows():
        col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
        with col_c1:
            st.markdown(f"**{row['Produto']}**")
            st.caption(f"Categoria: {row['Categoria']} | Stock: {row['Quantidade']}")
        with col_c2:
            st.markdown(f"<span style='color: #4ac26b; font-weight: bold;'>{row['Preço Unitário']:,.2f} Kz</span>", unsafe_allow_html=True)
        with col_c3:
            st.number_input(f"Qtd##{row['Produto']}", min_value=0, max_value=int(row['Quantidade']), value=0, step=1, key=f"cli_{mesa_detectada}_{row['Produto']}")
        st.divider()

    if mesa_detectada not in st.session_state.mesas:
        st.session_state.mesas[mesa_detectada] = {"itens": [], "estado": "Ocupada", "garcon": "Auto-Atendimento"}

    if st.button("🚀 Enviar Pedido para a Cozinha / Caixa", type="primary", use_container_width=True):
        novos_itens = []
        for index, row in df_stk.iterrows():
            q = st.session_state.get(f"cli_{mesa_detectada}_{row['Produto']}", 0)
            if q > 0:
                novos_itens.append({
                    "Produto": row['Produto'],
                    "Quantidade": int(q),
                    "Preço Unitário": float(row['Preço Unitário']),
                    "Subtotal": float(q * row['Preço Unitário']),
                    "Estado": "Pendente"
                })
        
        if not novos_itens:
            st.warning("Selecione pelo menos um produto antes de enviar o pedido.")
        else:
            st.session_state.mesas[mesa_detectada]["itens"].extend(novos_itens)
            st.session_state.mesas[mesa_detectada]["estado"] = "Ocupada"
            salvar_estado_mesas(st.session_state.mesas)
            st.success("✅ Pedido enviado com sucesso para a cozinha e caixa!")
            st.rerun()

    st.markdown("---")
    st.subheader(f"🧾 Estado Atual da {mesa_detectada}")
    mesa_info = st.session_state.mesas.get(mesa_detectada, {"itens": []})
    if not mesa_info["itens"]:
        st.info("Ainda não há pedidos registados nesta mesa.")
    else:
        df_mesa_atual = pd.DataFrame(mesa_info["itens"])
        st.dataframe(df_mesa_atual, use_container_width=True)
        total_mesa = df_mesa_atual['Subtotal'].sum() if 'Subtotal' in df_mesa_atual.columns else 0
        st.markdown(f"### Total Consumido: **{total_mesa:,.2f} Kz**")

# ==========================================
# ÁREA: CAIXA / OPERADOR
# ==========================================
def area_caixa_mesas():
    st.markdown("<h1>💻 Painel do Operador de Caixa & Gestão de Mesas</h1>", unsafe_allow_html=True)
    
    sessao_op = carregar_sessao_operador()
    
    if not sessao_op.get("logado"):
        st.markdown("### 🔐 Autenticação do Operador de Caixa")
        with st.form("form_login_operador"):
            op_nome = st.text_input("Nome do Operador de Caixa:")
            op_periodo = st.selectbox("Período de Trabalho:", ["Dia", "Noite"])
            senha_caixa = st.text_input("Senha de Caixa:", type="password")
            
            btn_login = st.form_submit_button("Entrar no Caixa", use_container_width=True)
            if btn_login:
                if senha_caixa == "123123123" and op_nome:
                    saidas_disp = carregar_saidas_caixa()
                    saldo_inicial_atribuido = 0.0
                    for s in reversed(saidas_disp):
                        if s.get("Destino Utilizador", "").lower() == op_nome.lower() or s.get("Período") == op_periodo:
                            saldo_inicial_atribuido = float(s.get("Valor", 0.0))
                            break
                    
                    sessao_op = {
                        "logado": True,
                        "operador": op_nome,
                        "periodo": op_periodo,
                        "saldo_inicial": saldo_inicial_atribuido,
                        "hora_abertura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    salvar_sessao_operador(sessao_op)
                    st.success(f"Sessão iniciada para {op_nome} ({op_periodo}). Fundo inicial carregado: {saldo_inicial_atribuido:,.2f} Kz")
                    st.rerun()
                else:
                    st.error("Preencha o nome e introduza a senha correta (123123123)!")
        return

    col_op1, col_op2, col_op3 = st.columns([3, 2, 1])
    with col_op1:
        st.info(f"👤 **Operador:** {sessao_op.get('operador')} | **Período:** {sessao_op.get('periodo')} | **Fundo Inicial:** {sessao_op.get('saldo_inicial', 0.0):,.2f} Kz")
    with col_op2:
        st.info(f"🟢 **Abertura:** {sessao_op.get('hora_abertura')}")
    with col_op3:
        if st.button("🚪 Terminar Sessão"):
            salvar_sessao_operador({"logado": False, "operador": "", "periodo": "", "saldo_inicial": 0.0, "hora_abertura": ""})
            st.rerun()

    st.markdown("---")
    
    tab_mesas, tab_pedidos_cx, tab_fecho_turno = st.tabs(["🪑 Gestão de Mesas & Lançamentos", "📊 Vendas e Faturação", "📋 Fecho de Período / Caixa"])
    
    with tab_mesas:
        st.subheader("🪑 Salas e Mesas do Restaurante")
        
        st.session_state.mesas = carregar_estado_mesas()
        
        lista_mesas = list(st.session_state.mesas.keys())
        mesa_selecionada = st.selectbox("Selecione a Mesa para Atendimento / Lançamento:", lista_mesas)
        
        info_mesa = st.session_state.mesas[mesa_selecionada]
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"#### Estado da Mesa: **{info_mesa['estado']}**")
            garcon_atribuido = st.selectbox("Garçon Responsável:", ["Selecione..."] + carregar_rh_disco()['Nome'].tolist(), index=0)
            if garcon_atribuido != "Selecione...":
                info_mesa['garcon'] = garcon_atribuido
        
        with col_m2:
            st.markdown("#### ⚡ Ações Rápidas de Mesa")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🧹 Limpar / Zerar Mesa", use_container_width=True):
                    st.session_state.mesas[mesa_selecionada] = {"itens": [], "estado": "Livre", "garcon": ""}
                    salvar_estado_mesas(st.session_state.mesas)
                    st.success(f"A {mesa_selecionada} foi totalmente limpa e zerada com sucesso!")
                    st.rerun()
            with col_b2:
                st.link_button("🔗 Ver QR Code da Mesa", f"/?mesa={mesa_selecionada.replace(' ', '_')}", use_container_width=True)

        st.divider()
        st.markdown("#### ➕ Adicionar Itens à Mesa (Filtros por Categoria)")
        
        # 3 BOTÕES DE CATEGORIA NO CAIXA SOLICITADOS
        col_f1, col_f2, col_f3 = st.columns(3)
        if "filtro_caixa_cat" not in st.session_state:
            st.session_state.filtro_caixa_cat = "Todas"
            
        with col_f1:
            if st.button("🥤 Bebidas", use_container_width=True):
                st.session_state.filtro_caixa_cat = "Bebidas"
        with col_f2:
            if st.button("🍲 Refeição", use_container_width=True):
                st.session_state.filtro_caixa_cat = "Refeição"
        with col_f3:
            if st.button("🍰 Sobremesa", use_container_width=True):
                st.session_state.filtro_caixa_cat = "Sobremesa"

        st.caption(f"Filtro ativo atual: **{st.session_state.filtro_caixa_cat}**")
        if st.button("🔄 Mostrar Todas as Categorias"):
            st.session_state.filtro_caixa_cat = "Todas"
            st.rerun()

        df_stk = st.session_state.stock
        if not df_stk.empty:
            if st.session_state.filtro_caixa_cat != "Todas":
                df_cat_filtrado = df_stk[df_stk['Categoria'] == st.session_state.filtro_caixa_cat]
            else:
                df_cat_filtrado = df_stk

            with st.form("form_lancar_item_caixa"):
                produto_escolhido = st.selectbox("Selecionar Produto:", df_cat_filtrado['Produto'].tolist() if not df_cat_filtrado.empty else [])
                qtd_lancar = st.number_input("Quantidade:", min_value=1, value=1)
                
                btn_lancar = st.form_submit_button("🛒 Lançar Item na Mesa", use_container_width=True)
                if btn_lancar and produto_escolhido:
                    preco_unit = float(df_stk.loc[df_stk['Produto'] == produto_escolhido, 'Preço Unitário'].values[0])
                    novo_item = {
                        "Produto": produto_escolhido,
                        "Quantidade": int(qtd_lancar),
                        "Preço Unitário": preco_unit,
                        "Subtotal": float(qtd_lancar * preco_unit),
                        "Estado": "Pronto para Cozinha"
                    }
                    st.session_state.mesas[mesa_selecionada]["itens"].append(novo_item)
                    st.session_state.mesas[mesa_selecionada]["estado"] = "Ocupada"
                    salvar_estado_mesas(st.session_state.mesas)
                    st.success(f"Item '{produto_escolhido}' adicionado à {mesa_selecionada}!")
                    st.rerun()

        st.markdown("---")
        st.markdown(f"#### 🧾 Consumo Atual da {mesa_selecionada}")
        itens_mesa = info_mesa.get("itens", [])
        if not itens_mesa:
            st.info("Nenhum item lançado nesta mesa.")
        else:
            df_itens = pd.DataFrame(itens_mesa)
            st.dataframe(df_itens, use_container_width=True)
            total_consumo = df_itens['Subtotal'].sum() if 'Subtotal' in df_itens.columns else 0
            st.markdown(f"### Total a Pagar: **{total_consumo:,.2f} Kz**")
            
            with st.form("form_pagamento_mesa"):
                st.markdown("#### 💳 Efetuar Pagamento / Fechar Conta")
                forma_pagamento = st.selectbox("Forma de Pagamento:", ["Dinheiro", "TPA / Multicaixa", "Misto"])
                
                val_dinheiro = 0.0
                val_tpa = 0.0
                if forma_pagamento == "Dinheiro":
                    val_dinheiro = total_consumo
                elif forma_pagamento == "TPA / Multicaixa":
                    val_tpa = total_consumo
                else:
                    val_dinheiro = st.number_input("Valor em Dinheiro (Kz):", min_value=0.0, value=total_consumo/2)
                    val_tpa = st.number_input("Valor em TPA (Kz):", min_value=0.0, value=total_consumo/2)

                btn_finalizar_pagamento = st.form_submit_button("💰 Confirmar Pagamento e Emitir Fatura", use_container_width=True)
                if btn_finalizar_pagamento:
                    hist_vendas = carregar_historico_vendas()
                    registo_venda = {
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Mesa": mesa_selecionada,
                        "Operador": sessao_op.get("operador"),
                        "Período": sessao_op.get("periodo"),
                        "Forma Pagamento": forma_pagamento,
                        "Valor Dinheiro": float(val_dinheiro),
                        "Valor TPA": float(val_tpa),
                        "Valor Total": float(total_consumo),
                        "Itens": itens_mesa
                    }
                    hist_vendas.append(registo_venda)
                    salvar_historico_vendas(hist_vendas)

                    if info_mesa.get("garcon"):
                        atendimentos = carregar_atendimentos_garcon()
                        atendimentos.append({
                            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Garçon": info_mesa.get("garcon"),
                            "Mesa": mesa_selecionada,
                            "Valor Venda": float(total_consumo)
                        })
                        salvar_atendimentos_garcon(atendimentos)

                    st.session_state.mesas[mesa_selecionada] = {"itens": [], "estado": "Livre", "garcon": ""}
                    salvar_estado_mesas(st.session_state.mesas)
                    st.success(f"Pagamento da {mesa_selecionada} processado com sucesso! Venda registada.")
                    st.rerun()

    with tab_pedidos_cx:
        st.subheader("📊 Histórico de Vendas do Turno")
        hist_vendas = carregar_historico_vendas()
        if not hist_vendas:
            st.info("Nenhuma venda registada ainda.")
        else:
            df_v = pd.DataFrame(hist_vendas)
            st.dataframe(df_v, use_container_width=True)

    with tab_fecho_turno:
        st.subheader("📋 Fecho de Período do Caixa")
        with st.form("form_fecho_caixa"):
            vendas_turno = [v for v in carregar_historico_vendas() if v.get("Operador") == sessao_op.get("operador")]
            total_dinheiro_turno = sum(float(v.get("Valor Dinheiro", 0)) for v in vendas_turno)
            total_tpa_turno = sum(float(v.get("Valor TPA", 0)) for v in vendas_turno)
            fundo_inicial = float(sessao_op.get("saldo_inicial", 0))
            
            total_geral_fecho = fundo_inicial + total_dinheiro_turno + total_tpa_turno
            
            st.markdown(f"""
                * **Fundo Inicial (Saída ADM):** {fundo_inicial:,.2f} Kz
                * **Total Vendas em Dinheiro:** {total_dinheiro_turno:,.2f} Kz
                * **Total Vendas em TPA:** {total_tpa_turno:,.2f} Kz
                ### **Total Geral do Fecho:** {total_geral_fecho:,.2f} Kz
            """)
            
            obs_fecho = st.text_area("Observações do Fecho:")
            btn_submeter_fecho = st.form_submit_button("📤 Submeter Fecho de Período ao Administrador", use_container_width=True)
            if btn_submeter_fecho:
                fechos = carregar_fechos_caixa()
                fechos.append({
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Operador": sessao_op.get("operador"),
                    "Período": sessao_op.get("periodo"),
                    "Fundo Inicial": fundo_inicial,
                    "Total Dinheiro": total_dinheiro_turno,
                    "Total TPA": total_tpa_turno,
                    "Total Fecho": total_geral_fecho,
                    "Observações": obs_fecho
                })
                salvar_fechos_caixa(fechos)
                st.success("Fecho de período submetido com sucesso à Administração!")
                st.rerun()

# ==========================================
# ÁREA: COZINHA
# ==========================================
def area_cozinha():
    st.markdown("<h1>🍳 Painel da Cozinha - NobreSabor</h1>", unsafe_allow_html=True)
    
    if not st.session_state.caixa_aberto:
        st.warning("🔴 O restaurante encontra-se encerrado. Cozinha inativa.")
        return

    st.subheader("📋 Pedidos Atuais nas Mesas para Preparação")
    st.session_state.mesas = carregar_estado_mesas()
    
    tem_pedidos = False
    for nome_mesa, info in st.session_state.mesas.items():
        if info.get("itens"):
            tem_pedidos = True
            with st.expander(f"📌 {nome_mesa} (Estado: {info['estado']} | Garçon: {info.get('garcon', 'N/A')})", expanded=True):
                df_itens_mesa = pd.DataFrame(info["itens"])
                st.dataframe(df_itens_mesa, use_container_width=True)
                
                if st.button(f"✅ Marcar todos os itens da {nome_mesa} como Prontos", key=f"coz_{nome_mesa}"):
                    for item in info["itens"]:
                        item["Estado"] = "Pronto"
                    salvar_estado_mesas(st.session_state.mesas)
                    st.success(f"Pedidos da {nome_mesa} atualizados para PRONTO!")
                    st.rerun()

    if not tem_pedidos:
        st.info("Nenhum pedido pendente na cozinha neste momento.")

# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
def area_administrador():
    st.markdown("<h1>👑 Painel do Administrador - NobreSabor</h1>", unsafe_allow_html=True)
    
    if "financas_autenticado" not in st.session_state:
        st.session_state.financas_autenticado = False

    if not st.session_state.financas_autenticado:
        with st.form("form_senha_financas"):
            st.markdown("### 🔒 Autenticação de Administrador")
            senha_digitada = st.text_input("Introduza a Senha de Administrador:", type="password")
            if st.form_submit_button("Desbloquear Painel"):
                if senha_digitada == "123123123":
                    st.session_state.financas_autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
        return

    col_btn_sair, col_links_rapidos = st.columns([1, 3])
    with col_btn_sair:
        if st.button("🔒 Bloquear Painel / Sair"):
            st.session_state.financas_autenticado = False
            st.rerun()
            
    with col_links_rapidos:
        st.markdown("<div style='text-align: right; color: #ffb703; font-size: 0.95rem; margin-bottom: 4px;'>🔗 Acessos Rápidos:</div>", unsafe_allow_html=True)
        col_lnk1, col_lnk2 = st.columns(2)
        with col_lnk1:
            st.link_button("💻 Abrir Painel do Caixa", "?perfil=caixa", use_container_width=True)
        with col_lnk2:
            st.link_button("🍳 Abrir Painel da Cozinha", "?perfil=cozinha", use_container_width=True)
            
    st.success("Painel de Administração desbloqueado com sucesso.")
    st.markdown("---")

    vendas_exc_check = carregar_vendas_excluidas()
    tem_novas_exclusoes = len(vendas_exc_check) > 0
    nome_aba_excluidas = "🚨 Vendas Excluídas (NOVO!)" if tem_novas_exclusoes else "🚨 Vendas Excluídas"

    tab_fin, tab_fechos_cx, tab_saidas, tab_stk, tab_dch, tab_exc = st.tabs([
        "💰 Finanças & Abertura do Dia", 
        "📋 Fechos de Período (Caixa)", 
        "💸 Saídas de Caixa", 
        "📦 Stock & Menu", 
        "👥 DCH (Colaboradores & Bónus)",
        nome_aba_excluidas
    ])
    
    with tab_fin:
        st.subheader("⚙️ Controlo Geral de Abertura e Fecho do Dia")
        
        if "financa_aba_autenticada" not in st.session_state:
            st.session_state.financa_aba_autenticada = False

        if not st.session_state.financa_aba_autenticada:
            with st.form("form_senha_aba_financa"):
                st.markdown("#### 🔒 Acesso Restrito às Finanças")
                senha_fin = st.text_input("Senha:", type="password")
                if st.form_submit_button("Desbloquear"):
                    if senha_fin == "123123123":
                        st.session_state.financa_aba_autenticada = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta!")
        else:
            if st.button("🔒 Bloquear Aba Finanças"):
                st.session_state.financa_aba_autenticada = False
                st.rerun()
                
            st.markdown("---")
            st.session_state.caixa_aberto = ler_estado_caixa_disco()
            
            col_adm_c1, col_adm_c2 = st.columns([1, 3])
            with col_adm_c1:
                if st.session_state.caixa_aberto:
                    if st.button("🔒 Fechar Dia do Restaurante", type="primary"):
                        gravar_estado_caixa_disco(False)
                        st.session_state.caixa_aberto = False
                        st.success("Dia fechado com sucesso!")
                        st.rerun()
                else:
                    if st.button("🟢 Abrir Dia do Restaurante", type="primary"):
                        # Ao abrir o dia/sistema, garantimos limpeza ou re-início controlado se desejado
                        gravar_estado_caixa_disco(True)
                        st.session_state.caixa_aberto = True
                        st.success("Dia aberto com sucesso!")
                        st.rerun()
            with col_adm_c2:
                if st.session_state.caixa_aberto:
                    st.info("🟢 O Sistema encontra-se atualmente **ABERTO**.")
                else:
                    st.warning("🔴 O Sistema encontra-se atualmente **FECHADO**.")

            st.markdown("---")
            st.subheader("📊 Histórico Geral de Vendas")
            hist_vendas = carregar_historico_vendas()
            if not hist_vendas:
                st.info("Ainda não existem vendas faturadas registadas.")
            else:
                df_vendas = pd.DataFrame(hist_vendas)
                st.dataframe(df_vendas, use_container_width=True)
                total_geral_faturado = df_vendas['Valor Total'].sum() if 'Valor Total' in df_vendas.columns else 0
                st.markdown(f"### Faturação Total Acumulada: **{total_geral_faturado:,.2f} Kz**")
                
                excel_data = converter_df_para_excel(df_vendas)
                st.download_button(
                    label="📥 Descarregar Relatório em Excel (.xlsx)",
                    data=excel_data,
                    file_name=f"Relatorio_Vendas_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    with tab_fechos_cx:
        st.subheader("📋 Relatórios de Fecho de Período")
        fechos_registados = carregar_fechos_caixa()
        if not fechos_registados:
            st.info("Nenhum fecho de período registado.")
        else:
            df_fechos = pd.DataFrame(fechos_registados)
            st.dataframe(df_fechos, use_container_width=True)

    with tab_saidas:
        st.subheader("💸 Gestão e Registo de Saídas de Caixa (Fundo Inicial)")
        with st.form("form_registar_saida"):
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                motivo_saida = st.text_input("Motivo:", value="Fundo de Maneio")
                destino_utilizador = st.selectbox("Destinatário (Operador):", ["Carlos", "Ana", "OperadorCaixa1", "OperadorCaixa2"])
            with col_sc2:
                valor_saida = st.number_input("Valor da Saída (Kz):", min_value=0.0, value=20000.0, step=1000.0)
                periodo_destino = st.selectbox("Período:", ["Dia", "Noite"])
            
            btn_salvar_saida = st.form_submit_button("🚀 Registar Saída e Enviar para o Caixa", use_container_width=True)
            if btn_salvar_saida and valor_saida > 0:
                saidas_list = carregar_saidas_caixa()
                saidas_list.append({
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Motivo": motivo_saida,
                    "Destino Utilizador": destino_utilizador,
                    "Período": periodo_destino,
                    "Valor": float(valor_saida),
                    "Responsável": "Administração"
                })
                salvar_saidas_caixa(saidas_list)
                st.success("Saída registada com sucesso!")
                st.rerun()

        st.divider()
        saidas_registadas = carregar_saidas_caixa()
        if saidas_registadas:
            st.dataframe(pd.DataFrame(saidas_registadas), use_container_width=True)

    with tab_stk:
        st.subheader("📦 Gestão de Stock e Menu")
        df_stock_atual = carregar_stock_disco()
        st.dataframe(df_stock_atual, use_container_width=True)

    with tab_dch:
        st.subheader("👥 Gestão de Recursos Humanos & Bónus de Atendimento")
        df_rh = carregar_rh_disco()
        st.dataframe(df_rh, use_container_width=True)

    with tab_exc:
        st.subheader("🚨 Registo de Vendas Excluídas")
        vendas_exc = carregar_vendas_excluidas()
        if not vendas_exc:
            st.info("Nenhuma venda excluída registada.")
        else:
            st.dataframe(pd.DataFrame(vendas_exc), use_container_width=True)

# ==========================================
# ROTEAMENTO PRINCIPAL DA APLICAÇÃO
# ==========================================
if mesa_detectada:
    area_cliente()
elif perfil_url == "caixa":
    area_caixa_mesas()
elif perfil_url == "cozinha":
    area_cozinha()
else:
    # Menu lateral de navegação geral caso não aceda via URL específica
    st.sidebar.title("🧭 Navegação Principal")
    opcao_menu = st.sidebar.radio("Escolha o Painel:", ["Painel Administrador", "Operador de Caixa", "Cozinha"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reiniciar / Limpar Estado do Sistema"):
        if os.path.exists(ARQUIVO_MESAS):
            os.remove(ARQUIVO_MESAS)
        st.session_state.mesas = carregar_estado_mesas()
        st.sidebar.success("Estado das mesas limpo/zerado com sucesso!")
        st.rerun()

    if opcao_menu == "Painel Administrador":
        area_administrador()
    elif opcao_menu == "Operador de Caixa":
        area_caixa_mesas()
    elif opcao_menu == "Cozinha":
        area_cozinha()
