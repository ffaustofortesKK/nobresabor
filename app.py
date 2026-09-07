import streamlit as st
import pandas as pd
from datetime import datetime
import qrcode
from io import BytesIO
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
    return {str(i): {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "faturado": False, "fatura_dados": None} for i in range(1, 31)}

def salvar_mesas_disco(mesas_dict):
    try:
        with open(ARQUIVO_DADOS_MESAS, "w", encoding="utf-8") as f:
            json.dump(mesas_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_historico_disco():
    if os.path.exists(ARQUIVO_HISTORICO_VENDAS):
        try:
            with open(ARQUIVO_HISTORICO_VENDAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_historico_disco(hist_list):
    try:
        with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
            json.dump(hist_list, f, ensure_ascii=False, indent=4)
    except:
        pass

# Estilos CSS
st.markdown("""
    <style>
    @keyframes piscar-mesa {
        0% { background-color: #ff4b4b; color: white; transform: scale(1); }
        50% { background-color: #ffe6e6; color: black; transform: scale(1.03); }
        100% { background-color: #ff4b4b; color: white; transform: scale(1); }
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
    .bloco-seccao {
        padding: 25px;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        margin-bottom: 30px;
    }
    .fatura-box {
        padding: 30px;
        border-radius: 12px;
        background-color: #f9f9f9;
        border: 1px solid #ccc;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# Captura rigorosa de Parâmetros da URL
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

# Sincroniza estados globais do disco
st.session_state.caixa_aberto = ler_estado_caixa_disco()
st.session_state.mesas_disco = carregar_mesas_disco()
st.session_state.historico_vendas_definitivo = carregar_historico_disco()

if "stock" not in st.session_state:
    st.session_state.stock = pd.DataFrame([
        ["Água 0.5L", "Bebidas", 50, 300.0],
        ["Refrigerante Cola", "Bebidas", 40, 450.0],
        ["Cerveja Cuca", "Bebidas", 60, 500.0],
        ["Vinho Tinto", "Bebidas", 15, 4500.0],
        ["Frango à Grega", "Refeições", 20, 3500.0],
        ["Bife a Cavalo", "Refeições", 15, 4000.0],
        ["Pudim de Leite", "Sobremesas", 25, 1500.0],
        ["Salada de Frutas", "Sobremesas", 30, 1200.0]
    ], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])

if "rh" not in st.session_state:
    st.session_state.rh = pd.DataFrame([
        ["G001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042"],
        ["G002", "Ana Paula", "Garçon", "912333444", "009876543LA031"]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])

URL_OFICIAL = "https://nobresabor.streamlit.app"

def gerar_qrcode_bytes(url_texto):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

# Sidebar dinâmica
st.sidebar.image("https://img.icons8.com/color/96/restaurant-.png", width=80)
st.sidebar.title("NobreSabor - Gestão")
st.sidebar.divider()
if st.session_state.caixa_aberto:
    st.sidebar.success("🟢 Caixa Aberto")
else:
    st.sidebar.error("🔴 Caixa Fechado")

# ==========================================
# ÁREA: CLIENTE
# ==========================================
def area_cliente():
    if mesa_detectada and 1 <= mesa_detectada <= 30:
        num_mesa = mesa_detectada
    else:
        st.error("⚠️ Nenhum número de mesa detetado no link! Por favor, escaneie o QR Code correto da sua mesa.")
        return

    mesas_data = carregar_mesas_disco()
    str_mesa = str(num_mesa)
    dados_m = mesas_data[str_mesa]

    # Se a conta foi faturada pelo caixa, exibe a fatura final e agradecimento
    if dados_m.get("faturado") and dados_m.get("fatura_dados"):
        fat = dados_m["fatura_dados"]
        st.markdown("<div class='fatura-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>🍽️ Restaurante Nobre Sabor</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Fatura / Recibo de Consumo</h4>", unsafe_allow_html=True)
        st.divider()
        st.write(f"**Mesa:** {num_mesa} | **Cliente:** {fat['nome']} | **Data:** {fat['data']}")
        st.write(f"**Método de Pagamento:** {fat['pagamento']}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.subheader("Itens Consumidos:")
        for item in fat['itens']:
            st.write(f"- {item['quantidade']}x {item['item']} — {(item['quantidade'] * item['preco']):,.2f} Kz")
            
        st.markdown(f"### Total Pago: {fat['total']:,.2f} Kz")
        st.divider()
        st.success("🎉 **Muito obrigado pela sua presença no Restaurante Nobre Sabor! Esperamos vê-lo(a) novamente em breve.**")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if not dados_m.get("cliente"):
        st.markdown(f"<h1 style='text-align: center;'>🍽️ Bem-vindo ao Restaurante Nobre Sabor</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: gray;'>Registo de Entrada - Mesa {num_mesa}</h3>", unsafe_allow_html=True)
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form(f"form_cli_{num_mesa}"):
                nome_cli = st.text_input("Nome:")
                tel_cli = st.text_input("Telefone:")
                whatsapp_opt = st.checkbox("Deseja entrar no Grupo de WhatsApp do Restaurante?")
                
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
        st.title(f"📱 NobreSabor | Mesa {num_mesa}")
        st.success(f"Bem-vindo, **{cli['nome']}**!")
        
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo & Fatura", "🎉 Programas"])
        
        with tab_menu:
            cat_escolhida = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas"])
            stock_df = st.session_state.stock
            itens_cat = stock_df[stock_df['Categoria'] == cat_escolhida]
            
            if not itens_cat.empty:
                item_escolhido = st.selectbox("Item:", itens_cat['Produto'].tolist())
                row_prod = itens_cat[itens_cat['Produto'] == item_escolhido].iloc[0]
                qtd = st.number_input("Quantidade:", min_value=1, value=1)
                obs = st.text_input("Observações:")
                
                if st.button("🚀 Enviar Pedido"):
                    is_refeicao = (cat_escolhida == "Refeições")
                    novo_pedido = {
                        "item": item_escolhido,
                        "tipo": cat_escolhida,
                        "quantidade": qtd,
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
                    dados_m["total"] = total_calc
                    
                    salvar_mesas_disco(mesas_data)
                    st.success("Pedido enviado com sucesso e registado na sua mesa!")
                    st.rerun()
                
        with tab_consumo:
            st.subheader("O Meu Consumo")
            pedidos_mesa = dados_m["pedidos"]
            if not pedidos_mesa:
                st.info("Ainda não tem pedidos.")
            else:
                subtotal_geral = 0
                for p in pedidos_mesa:
                    total_item = p['quantidade'] * p['preco']
                    if p['status'] not in ["Anulado", "Recusado pela Cozinha"]:
                        subtotal_geral += total_item
                    st.write(f"- {p['quantidade']}x {p['item']} | {total_item:,.2f} Kz ({p['status']})")
                st.markdown(f"### Total: {subtotal_geral:,.2f} Kz")
                
        with tab_eventos:
            st.subheader("Eventos da Semana")
            st.markdown("- Sexta: Música ao Vivo\n- Sábado: Karaoke (Grupo FF Karaoke)")


# ==========================================
# ÁREA: COZINHA (Com Fragmento Auto-Executável)
# ==========================================
@st.fragment(run_every=6)
def area_cozinha():
    st.title("🍳 Área da Cozinha - Gestão de Refeições")
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** A cozinha foi encerrada automaticamente.")
        return

    st.caption("🔄 Esta secção atualiza-se sozinha em segundo plano (sem dar F5 na página).")
    
    tem_pedidos = False
    for i in range(1, 31):
        str_i = str(i)
        dados_m = mesas_data[str_i]
        for idx_p, ped in enumerate(dados_m["pedidos"]):
            if ped["tipo"] == "Refeições" and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
                tem_pedidos = True
                
                col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                with col_c1:
                    st.write(f"### 🍽️ Mesa {i}")
                    st.write(f"**Refeição:** {ped['item']} | **Qtd:** {ped['quantidade']}")
                    st.write(f"Origem: _{ped['origem']}_ | Obs: _{ped['obs']}_")
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
    st.markdown("<hr style='margin-top: 40px; margin-bottom: 40px;'>", unsafe_allow_html=True)
    st.title("👑 Painel do Administrador - NobreSabor")
    
    with st.expander("🔗 Links Oficiais do Sistema", expanded=True):
        st.text_input("Link Direto do Caixa:", f"{URL_OFICIAL}/?perfil=caixa")
        st.text_input("Link Direto da Cozinha:", f"{URL_OFICIAL}/?perfil=cozinha")
        
    tab_fin, tab_stk, tab_dch = st.tabs(["💰 Finanças", "📦 Stock", "👥 DCH"])
    
    with tab_fin:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("💰 Controlo de Caixa")
        
        col_cx_status, col_cx_btn = st.columns([3, 1])
        with col_cx_status:
            if st.session_state.caixa_aberto:
                st.success("🟢 O Caixa encontra-se ABERTO.")
            else:
                st.error("🔴 O Caixa encontra-se FECHADO.")
        with col_cx_btn:
            if st.session_state.caixa_aberto:
                if st.button("Fechar Caixa", type="secondary", key="btn_fechar_cx_adm"):
                    st.session_state.caixa_aberto = False
                    gravar_estado_caixa_disco(False)
                    st.success("Caixa fechado com sucesso!")
                    st.rerun()
            else:
                if st.button("Abrir Caixa", type="primary", key="btn_abrir_cx_adm"):
                    st.session_state.caixa_aberto = True
                    gravar_estado_caixa_disco(True)
                    st.success("Caixa aberto com sucesso!")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Histórico de Vendas (Administrador)")
        
        historico_atual = carregar_historico_disco()
        if historico_atual:
            st.dataframe(pd.DataFrame(historico_atual), use_container_width=True)
        else:
            st.info("Sem vendas registadas.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_stk:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("📦 Stock")
        with st.form("form_stock_adm"):
            np = st.text_input("Produto")
            cat = st.selectbox("Categoria", ["Bebidas", "Refeições", "Sobremesas"])
            qtd = st.number_input("Quantidade", min_value=0)
            prc = st.number_input("Preço (Kz)", min_value=0.0)
            if st.form_submit_button("Adicionar") and np:
                novo_df = pd.DataFrame([[np, cat, qtd, prc]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                st.session_state.stock = pd.concat([st.session_state.stock, novo_df], ignore_index=True)
                st.rerun()
        st.dataframe(st.session_state.stock, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab_dch:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("👥 Recursos Humanos")
        with st.form("form_rh_adm"):
            cc = st.text_input("Código")
            nc = st.text_input("Nome")
            cat_func = st.selectbox("Categoria", ["Garçon", "Cozinheiro", "Caixa"])
            tel = st.text_input("Telefone")
            bi = st.text_input("BI")
            if st.form_submit_button("Registar") and cc:
                novo_rh = pd.DataFrame([[cc, nc, cat_func, tel, bi]], columns=["Código", "Nome", "Categoria", "Telefone", "BI"])
                st.session_state.rh = pd.concat([st.session_state.rh, novo_rh], ignore_index=True)
                st.rerun()
        st.dataframe(st.session_state.rh, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS (Com Fragmento Auto-Executável)
# ==========================================
@st.fragment(run_every=6)
def area_caixa_mesas():
    st.title("💻 Controlo Geral de Mesas e Faturação (Caixa)")
    
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()
    historico_vendas = carregar_historico_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** O Administrador encerrou o caixa.")
        return

    # CÁLCULO DOS TOTAIS ACUMULADOS EM CAIXA (Monetário vs TPA)
    total_monetario = sum(v["Valor"] for v in historico_vendas if v.get("Pagamento") == "Dinheiro (Monetário)")
    total_tpa = sum(v["Valor"] for v in historico_vendas if v.get("Pagamento") == "TPA")
    total_geral_caixa = total_monetario + total_tpa

    # Bloco superior de contagem de valores acumulados no Caixa
    st.markdown(f"""
        <div style="background-color: #f1f3f5; padding: 20px; border-radius: 10px; border: 1px solid #ced4da; margin-bottom: 25px;">
            <h3 style="margin-top: 0; color: #333;">💵 Total em Caixa</h3>
            <hr style="margin: 5px 0 15px 0;">
            <p style="font-size: 1.1em; margin: 5px 0;"><b>Valor em Monetário:</b> <span style="color: #2b8a3e; font-weight: bold;">{total_monetario:,.2f} Kz</span></p>
            <p style="font-size: 1.1em; margin: 5px 0;"><b>Valor em TPA:</b> <span style="color: #1864ab; font-weight: bold;">{total_tpa:,.2f} Kz</span></p>
            <p style="font-size: 1.2em; margin: 10px 0 0 0;"><b>Total Geral Acumulado:</b> <span style="color: #d9480f; font-weight: bold;">{total_geral_caixa:,.2f} Kz</span></p>
        </div>
    """, unsafe_allow_html=True)

    st.success("🟢 Caixa Aberto. Atualização inteligente em segundo plano ativa.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        str_m_ativa = str(m_ativa)
        if st.button("⬅️ Voltar à Visão Geral"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Gestão da Mesa {m_ativa}")
        dados_mesa = mesas_data[str_m_ativa]
        
        total_calculado = sum(
            p['quantidade'] * p['preco'] 
            for p in dados_mesa['pedidos'] 
            if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
        )
        dados_mesa['total'] = total_calculado
        salvar_mesas_disco(mesas_data)

        with st.expander("📷 QR Code", expanded=False):
            link_mesa = f"{URL_OFICIAL}/?mesa={m_ativa}"
            st.code(link_mesa)
            st.image(gerar_qrcode_bytes(link_mesa), width=130)

        if dados_mesa.get("cliente"):
            cli = dados_mesa["cliente"]
            st.info(f"👤 **Cliente Registado na Mesa:** {cli['nome']} | 📞 Tel: {cli['telefone']}")

        st.subheader("📝 Pedidos Lançados na Mesa")
        if not dados_mesa['pedidos']:
            st.info("Nenhum pedido efetuado nesta mesa ainda.")
        else:
            for idx_p, p in enumerate(dados_mesa['pedidos']):
                col_p1, col_p2, col_p3 = st.columns([3, 2, 2])
                with col_p1:
                    st.write(f"- {p['quantidade']}x {p['item']} ({p['tipo']}) [{p['origem']}]")
                    if p['obs']:
                        st.caption(f"Obs: {p['obs']}")
                with col_p2:
                    st.write(f"**{(p['quantidade'] * p['preco']):,.2f} Kz**")
                with col_p3:
                    st.write(f"Estado: `{p['status']}`")

        st.markdown(f"### Total a Pagar: **{dados_mesa['total']:,.2f} Kz**")

        # Seleção do tipo de pagamento e botão de fechar conta
        forma_pagamento = st.radio("Selecione o Método de Pagamento:", ["Dinheiro (Monetário)", "TPA"], horizontal=True)

        if st.button("💳 Fechar Conta e Faturar", type="primary"):
            if dados_mesa['total'] > 0:
                nome_c_fatura = dados_mesa['cliente']['nome'] if dados_mesa.get('cliente') else 'Cliente Mesa'
                tel_c_fatura = dados_mesa['cliente']['telefone'] if dados_mesa.get('cliente') else 'N/A'
                data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Regista no histórico global compartilhado com o Administrador
                nova_venda = {
                    "Nome": nome_c_fatura, 
                    "Telefone": tel_c_fatura, 
                    "Mesa": m_ativa,
                    "Valor": dados_mesa["total"], 
                    "Dia": data_hora_atual, 
                    "Pagamento": forma_pagamento
                }
                historico_vendas.append(nova_venda)
                salvar_historico_disco(historico_vendas)

                # Prepara dados da fatura para o cliente visualizar no telemóvel
                dados_mesa["faturado"] = True
                dados_mesa["fatura_dados"] = {
                    "nome": nome_c_fatura,
                    "telefone": tel_c_fatura,
                    "data": data_hora_atual,
                    "pagamento": forma_pagamento,
                    "itens": list(dados_mesa["pedidos"]),
                    "total": dados_mesa["total"]
                }
                salvar_mesas_disco(mesas_data)

                st.success("Conta fechada e faturada com sucesso! O cliente já pode ver a fatura e a mensagem de agradecimento no telemóvel.")
                del st.session_state.mesa_ativa
                st.rerun()
            else:
                st.warning("A mesa não tem valor a faturar.")
    else:
        cols_por_linha = 6
        for linha in range(5):
            cols = st.columns(cols_por_linha)
            for c in range(cols_por_linha):
                num_mesa = linha * cols_por_linha + c + 1
                if num_mesa <= 30:
                    str_num = str(num_mesa)
                    dados_m = mesas_data[str_num]
                    status_m = dados_m["status"]
                    
                    total_m = sum(
                        p['quantidade'] * p['preco'] 
                        for p in dados_m['pedidos'] 
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )
                    dados_m['total'] = total_m
                    
                    classe_css = "mesa-aberta" if status_m == "Aberta" else "mesa-fechada"
                    
                    with cols[c]:
                        nome_cliente_txt = f"<br><span style='font-size: 0.75em;'>{dados_m['cliente']['nome']}</span>" if dados_m.get('cliente') else ""
                        st.markdown(f"""
                            <div class="{classe_css}">
                                Mesa {num_mesa}<br>{status_m}{nome_cliente_txt}<br>
                                <span style="font-size: 0.8em;">{dados_m['total']:,.2f} Kz</span>
                            </div>
                        """, unsafe_allow_html=True)
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
