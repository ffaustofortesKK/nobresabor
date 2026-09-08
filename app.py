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
                return json.load(f)
        except:
            pass
    return []

def salvar_historico_vendas(hist_list):
    try:
        with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
            json.dump(hist_list, f, ensure_ascii=False, indent=4)
    except:
        pass

# Estilos CSS atualizados com formato de mesa realista (arredondado/oval)
st.markdown("""
    <style>
    @keyframes borda-vermelha-piscar {
        0% { border: 3px solid #ff4b4b; box-shadow: 0 0 10px #ff4b4b; background-color: #fff5f5; }
        50% { border: 3px solid #ffa0a0; box-shadow: none; background-color: #ffffff; }
        100% { border: 3px solid #ff4b4b; box-shadow: 0 0 10px #ff4b4b; background-color: #fff5f5; }
    }
    .mesa-pronta-alerta {
        padding: 15px;
        border-radius: 60px / 30px;
        text-align: center;
        font-weight: bold;
        animation: borda-vermelha-piscar 1s infinite;
        color: #d32f2f;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .mesa-aberta {
        padding: 15px;
        border-radius: 60px / 30px;
        text-align: center;
        font-weight: bold;
        border: 2px solid #28a745;
        background-color: #f4fff6;
        color: #155724;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .mesa-fechada {
        padding: 15px;
        border-radius: 60px / 30px;
        text-align: center;
        font-weight: bold;
        border: 2px solid #d6d8db;
        background-color: #f8f9fa;
        color: #6c757d;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .bloco-seccao {
        padding: 25px;
        border-radius: 12px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        margin-bottom: 30px;
    }
    .fatura-box {
        background-color: #f9f9f9;
        border: 2px dashed #4CAF50;
        padding: 25px;
        border-radius: 10px;
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

    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<div class='fatura-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #2e7d32;'>🧾 Restaurante Nobre Sabor - Fatura / Recibo</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><b>Mesa:</b> {num_mesa} | <b>Data:</b> {fat['data']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'><b>Cliente:</b> {fat['cliente']} | <b>Telefone:</b> {fat['telefone']}</p>", unsafe_allow_html=True)
        st.divider()
        
        for item in fat['itens']:
            st.write(f"- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.2f} Kz")
        
        st.markdown(f"### Total Pago: **{fat['total']:,.2f} Kz**")
        st.markdown(f"<p><b>Forma de Pagamento:</b> {fat['pagamento_detalhe']}</p>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<h3 style='text-align: center; color: #1565c0;'>🙏 Muito obrigado pela sua presença no Restaurante Nobre Sabor! Esperamos vê-lo(a) novamente em breve.</h3>", unsafe_allow_html=True)
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
        
        categorias_disponiveis = st.session_state.stock['Categoria'].unique().tolist()
        tab_menu, tab_consumo, tab_eventos = st.tabs(["📋 Fazer Pedidos", "📊 O Meu Consumo & Fatura", "🎉 Programas"])
        
        with tab_menu:
            cat_escolhida = st.selectbox("Categoria:", categorias_disponiveis, key="cat_cli_sel")
            stock_df = st.session_state.stock
            itens_cat = stock_df[stock_df['Categoria'] == cat_escolhida]
            
            if not itens_cat.empty:
                with st.form(key=f"form_pedido_{num_mesa}", clear_on_submit=True):
                    item_escolhido = st.selectbox("Item:", itens_cat['Produto'].tolist())
                    qtd = st.number_input("Quantidade:", min_value=1, value=1)
                    obs = st.text_input("Observações:")
                    
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
                        
                        st.session_state[f"aviso_pedido_enviado_{num_mesa}"] = f"✅ Pedido de {qtd}x {item_escolhido} enviado com sucesso! Já pode solicitar outro item."
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
                        status_txt = "Preparando na Cozinha 🍳"
                        
                    st.write(f"- {p['quantidade']}x {p['item']} | {total_item:,.2f} Kz — Estado: **{status_txt}**")
                    
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
            cat_p = str(ped.get("tipo", "")).lower()
            if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
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
        st.subheader("📊 Histórico de Vendas Definitivo")
        hist_vendas = carregar_historico_vendas()
        if hist_vendas:
            df_vendas = pd.DataFrame(hist_vendas)
            st.dataframe(df_vendas, use_container_width=True)
            
            t_dinheiro = df_vendas['Valor Dinheiro'].sum() if 'Valor Dinheiro' in df_vendas else 0
            t_tpa = df_vendas['Valor TPA'].sum() if 'Valor TPA' in df_vendas else 0
            t_geral = df_vendas['Valor Total'].sum() if 'Valor Total' in df_vendas else 0
            
            st.markdown(f"**Total Acumulado Geral:** {t_geral:,.2f} Kz | 💵 **Dinheiro:** {t_dinheiro:,.2f} Kz | 💳 **TPA:** {t_tpa:,.2f} Kz")
        else:
            st.info("Sem vendas registadas.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_stk:
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("➕ Registo de Produtos com Categoria")
        
        with st.form("form_registo_produto_novo"):
            st.write("Insira os dados do novo item/produto para o menu e stock:")
            col_rp1, col_rp2 = st.columns(2)
            with col_rp1:
                nome_novo_prod = st.text_input("Nome do Produto (ex: Cuca, Frango, Sumu...):")
                categoria_nova = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas", "Entradas", "Diversos"])
            with col_rp2:
                qtd_nova = st.number_input("Quantidade em Stock:", min_value=0, value=10)
                preco_novo = st.number_input("Preço Unitário (Kz):", min_value=0.0, value=1000.0)
                
            if st.form_submit_button("💾 Registar Produto", use_container_width=True):
                if nome_novo_prod.strip():
                    if not st.session_state.stock[st.session_state.stock['Produto'].str.lower() == nome_novo_prod.strip().lower()].empty:
                        st.error("Já existe um produto com este nome no stock!")
                    else:
                        novo_reg = pd.DataFrame([[nome_novo_prod.strip(), categoria_nova, int(qtd_nova), float(preco_novo)]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                        st.session_state.stock = pd.concat([st.session_state.stock, novo_reg], ignore_index=True)
                        st.success(f"Produto '{nome_novo_prod.strip()}' registado com sucesso na categoria '{categoria_nova}'!")
                        st.rerun()
                else:
                    st.warning("Por favor, insira o nome do produto.")

        st.markdown("</div>", unsafe_allow_html=True)

        # Secção: Stock de Bebidas
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("🍾 Stock de Bebidas")
        df_bebidas = st.session_state.stock[st.session_state.stock['Categoria'].str.lower() == "bebidas"]
        if df_bebidas.empty:
            st.info("Nenhuma bebida registada no stock.")
        else:
            st.dataframe(df_bebidas, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Secção: Stock de Produtos (Geral / Outras Categorias)
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("📦 Stock de Produtos (Geral / Refeições / Sobremesas / Outros)")
        df_produtos = st.session_state.stock[st.session_state.stock['Categoria'].str.lower() != "bebidas"]
        if df_produtos.empty:
            st.info("Nenhum produto geral registado.")
        else:
            st.dataframe(df_produtos, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Gestão e Edição Completa de Qualquer Item
        st.markdown("<div class='bloco-seccao'>", unsafe_allow_html=True)
        st.subheader("🛠️ Editar ou Remover Qualquer Item do Stock")
        
        if st.session_state.stock.empty:
            st.info("O stock está totalmente vazio.")
        else:
            lista_todos_produtos = st.session_state.stock['Produto'].tolist()
            prod_selecionado_gestao = st.selectbox("Selecione o produto para editar ou remover:", lista_todos_produtos, key="sel_gestao_produto_geral")
            
            if prod_selecionado_gestao:
                idx_encontrado = st.session_state.stock[st.session_state.stock['Produto'] == prod_selecionado_gestao].index[0]
                dado_item = st.session_state.stock.loc[idx_encontrado]
                
                with st.form(f"form_edicao_item_{idx_encontrado}"):
                    edit_nome = st.text_input("Nome do Produto:", value=str(dado_item['Produto']))
                    
                    cats_possiveis = ["Bebidas", "Refeições", "Sobremesas", "Entradas", "Diversos"]
                    cat_atual_val = dado_item['Categoria']
                    if cat_atual_val not in cats_possiveis:
                        cats_possiveis.append(cat_atual_val)
                        
                    edit_cat = st.selectbox("Categoria:", cats_possiveis, index=cats_possiveis.index(cat_atual_val))
                    edit_qtd = st.number_input("Quantidade:", min_value=0, value=int(dado_item['Quantidade']))
                    edit_prc = st.number_input("Preço Unitário (Kz):", min_value=0.0, value=float(dado_item['Preço Unitário']))
                    
                    col_b_ed1, col_b_ed2 = st.columns(2)
                    with col_b_ed1:
                        btn_salvar_edicao = st.form_submit_button("🔄 Atualizar Produto", use_container_width=True)
                    with col_b_ed2:
                        btn_apagar_prod = st.form_submit_button("🗑️ Remover Produto", use_container_width=True)
                        
                    if btn_salvar_edicao:
                        st.session_state.stock.at[idx_encontrado, 'Produto'] = edit_nome.strip()
                        st.session_state.stock.at[idx_encontrado, 'Categoria'] = edit_cat
                        st.session_state.stock.at[idx_encontrado, 'Quantidade'] = int(edit_qtd)
                        st.session_state.stock.at[idx_encontrado, 'Preço Unitário'] = float(edit_prc)
                        st.success("Produto atualizado com sucesso!")
                        st.rerun()
                        
                    if btn_apagar_prod:
                        st.session_state.stock = st.session_state.stock.drop(idx_encontrado).reset_index(drop=True)
                        st.success("Produto removido do stock com sucesso!")
                        st.rerun()

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
    hist_vendas = carregar_historico_vendas()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO.** O Administrador encerrou o caixa.")
        return

    # --- PAINEL SUPERIOR: CONTROLO DE CAIXA ACUMULADO ---
    total_dinheiro_caixa = sum(float(v.get('Valor Dinheiro', 0)) for v in hist_vendas)
    total_tpa_caixa = sum(float(v.get('Valor TPA', 0)) for v in hist_vendas)
    total_geral_caixa = total_dinheiro_caixa + total_tpa_caixa

    st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #d1d5db;">
            <h3 style="margin-top: 0; color: #1f2937;">📊 Resumo Total em Caixa</h3>
    """, unsafe_allow_html=True)
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("Total Acumulado", f"{total_geral_caixa:,.2f} Kz")
    with col_kpi2:
        st.metric("Valor em Dinheiro 💵", f"{total_dinheiro_caixa:,.2f} Kz")
    with col_kpi3:
        st.metric("Valor em TPA 💳", f"{total_tpa_caixa:,.2f} Kz")
    st.markdown("</div>", unsafe_allow_html=True)

    st.success("🟢 Caixa Aberto. Atualização inteligente em segundo plano ativa.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "mesa_ativa" in st.session_state:
        m_ativa = st.session_state.mesa_ativa
        str_m_ativa = str(m_ativa)
        if st.button("⬅️ Voltar à Visão Geral", key="btn_voltar_geral"):
            del st.session_state.mesa_ativa
            st.rerun()
            
        st.header(f"🎛️ Gestão da Mesa {m_ativa}")
        dados_mesa = mesas_data[str_m_ativa]
        
        if dados_mesa.get("fatura_emitida"):
            st.success("✅ Esta mesa já teve a conta fechada e a fatura foi emitida para o cliente.")
            st.warning("O cliente ainda está a ver a fatura no telemóvel. Quando ele sair, clique no botão abaixo para liberar a mesa.")
            if st.button("🧹 Limpar e Liberar Mesa para Novo Cliente", type="primary", key=f"btn_limpar_{m_ativa}"):
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
                    st.write(f"**{(float(p['quantidade']) * float(p['preco'])):,.2f} Kz**")
                with col_p3:
                    c_status = p.get('cozinha_status', 'N/A')
                    if c_status == "Feito":
                        st.markdown("🍽️ **Refeição Pronta**")
                    else:
                        st.write(f"Estado: `{p['status']}`")

        st.markdown(f"### Total a Pagar: **{float(dados_mesa['total']):,.2f} Kz**")

        if float(dados_mesa['total']) > 0:
            st.markdown("---")
            st.subheader("💳 Opções de Pagamento")
            tipo_pagamento = st.selectbox("Selecione a modalidade de pagamento:", ["Dinheiro", "TPA", "Ambos (Dinheiro + TPA)"], key=f"pag_tipo_{m_ativa}")
            
            val_dinheiro = 0.0
            val_tpa = 0.0
            
            if tipo_pagamento == "Dinheiro":
                val_dinheiro = float(dados_mesa['total'])
            elif tipo_pagamento == "TPA":
                val_tpa = float(dados_mesa['total'])
            else:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    val_dinheiro = st.number_input("Valor em Dinheiro (Kz):", min_value=0.0, max_value=float(dados_mesa['total']), value=float(dados_mesa['total'])/2, key=f"din_{m_ativa}")
                with col_m2:
                    val_tpa = float(dados_mesa['total']) - float(val_dinheiro)
                    st.info(f"Valor restante calculado para TPA: **{val_tpa:,.2f} Kz**")

            if st.button("💳 Fechar Conta, Emitir Fatura e Agradecer", type="primary", key=f"btn_fechar_{m_ativa}"):
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
                st.success("Conta fechada, fatura emitida e enviada para o cliente com sucesso!")
                del st.session_state.mesa_ativa
                st.rerun()
        else:
            st.warning("A mesa não tem valor a faturar.")
            
            if dados_mesa.get("cliente"):
                if st.button("❌ Cancelar / Limpar Mesa (Sem Consumo)", key=f"btn_cancela_{m_ativa}"):
                    mesas_data[str_m_ativa] = {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "fatura_emitida": None}
                    salvar_mesas_disco(mesas_data)
                    del st.session_state.mesa_ativa
                    st.rerun()
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
                        float(p['quantidade']) * float(p['preco']) 
                        for p in dados_m['pedidos'] 
                        if p['status'] not in ["Anulado", "Recusado pela Cozinha"]
                    )
                    dados_m['total'] = float(total_m)
                    
                    tem_refeicao_pronta = any(
                        ("refei" in str(p.get("tipo", "")).lower() or "prato" in str(p.get("tipo", "")).lower()) and p.get("cozinha_status") == "Feito" 
                        for p in dados_m['pedidos']
                    )
                    
                    if tem_refeicao_pronta:
                        classe_css = "mesa-pronta-alerta"
                    else:
                        classe_css = "mesa-aberta" if status_m == "Aberta" else "mesa-fechada"
                    
                    with cols[c]:
                        alerta_pronto_html = "<div style='color: #d32f2f; font-size: 0.85em; font-weight: bold; margin-bottom: 2px;'>🚨 Refeição Pronta!</div>" if tem_refeicao_pronta else ""
                        
                        nome_cli_formatado = f"<br><span style='font-size: 0.8em;'>{dados_m['cliente']['nome']}</span>" if dados_m.get('cliente') else ""

                        valor_formatado = f"<span style='color: black; font-weight: bold;'>{dados_m['total']:,.2f} Kz</span>"

                        conteudo_html = f"<div class='{classe_css}'>{alerta_pronto_html}🪑 Mesa {num_mesa}<br>{status_m}{nome_cli_formatado}<br>{valor_formatado}</div>"
                        
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
