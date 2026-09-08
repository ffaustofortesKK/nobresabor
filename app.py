import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import io
import qrcode

# Configuração inicial da página
st.set_page_config(
    page_title="Gestão de Restaurante & Mesas",
    page_icon="🍽️",
    layout="wide"
)

# Definir URL base oficial da aplicação (ajuste se necessário para o seu domínio no Streamlit Cloud)
URL_OFICIAL = "https://seu-app.streamlit.app"

# ==========================================
# CAMINHOS E PERSISTÊNCIA DE DADOS EM DISCO
# ==========================================
ARQUIVO_CARDAPIO = "cardapio.json"
ARQUIVO_MESAS = "mesas.json"
ARQUIVO_CAIXA = "caixa_estado.json"
ARQUIVO_VENDAS = "historico_vendas.json"

def carregar_cardapio_disco():
    if os.path.exists(ARQUIVO_CARDAPIO):
        with open(ARQUIVO_CARDAPIO, "r", encoding="utf-8") as f:
            return json.load(f)
    # Cardápio padrão inicial
    return [
        {"id": 1, "nome": "Prato do Dia (Funge com Carne)", "categoria": "Pratos Principais", "preco": 3500.0, "disponivel": True},
        {"id": 2, "nome": "Caldeirada de Peixe", "categoria": "Pratos Principais", "preco": 5000.0, "disponivel": True},
        {"id": 3, "nome": "Sumo Natural de Maracujá", "categoria": "Bebidas", "preco": 1000.0, "disponivel": True},
        {"id": 4, "nome": "Cerveja Cuca Gelada", "categoria": "Bebidas", "preco": 800.0, "disponivel": True},
    ]

def salvar_cardapio_disco(cardapio):
    with open(ARQUIVO_CARDAPIO, "w", encoding="utf-8") as f:
        json.dump(cardapio, f, ensure_ascii=False, indent=4)

def carregar_mesas_disco():
    if os.path.exists(ARQUIVO_MESAS):
        with open(ARQUIVO_MESAS, "r", encoding="utf-8") as f:
            return json.load(f)
    # Inicializar as 30 mesas do restaurante
    mesas_iniciais = {}
    for i in range(1, 31):
        mesas_iniciais[str(i)] = {
            "status": "Fechada", # Fechada, Ocupada, Pedido Solicitado
            "pedidos": [],
            "total": 0.0,
            "cliente": None,
            "fatura_emitida": None
        }
    return mesas_iniciais

def salvar_mesas_disco(mesas):
    with open(ARQUIVO_MESAS, "w", encoding="utf-8") as f:
        json.dump(mesas, f, ensure_ascii=False, indent=4)

def ler_estado_caixa_disco():
    if os.path.exists(ARQUIVO_CAIXA):
        with open(ARQUIVO_CAIXA, "r", encoding="utf-8") as f:
            return json.load(f).get("aberto", False)
    return False

def gravar_estado_caixa_disco(estado):
    with open(ARQUIVO_CAIXA, "w", encoding="utf-8") as f:
        json.dump({"aberto": estado}, f, ensure_ascii=False, indent=4)

def carregar_historico_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        with open(ARQUIVO_VENDAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_historico_vendas(vendas):
    with open(ARQUIVO_VENDAS, "w", encoding="utf-8") as f:
        json.dump(vendas, f, ensure_ascii=False, indent=4)

def gerar_qrcode_bytes(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# ==========================================
# ANÁLISE DOS PARÂMETROS DA URL (ROTEAMENTO)
# ==========================================
query_params = st.query_params
perfil_url = query_params.get("perfil", None)
mesa_param = query_params.get("mesa", None)

mesa_detectada = None
if mesa_param:
    try:
        mesa_detectada = int(mesa_param)
    except ValueError:
        mesa_detectada = None

# ==========================================
# ÁREA: CLIENTE / MESA (QR CODE)
# ==========================================
def area_cliente():
    st.title(f"📱 Pedidos Digitais - Mesa {mesa_detectada}")
    
    mesas_data = carregar_mesas_disco()
    str_m = str(mesa_detectada)
    if str_m not in mesas_data:
        st.error("Mesa inválida ou não configurada no sistema.")
        return
        
    d_mesa = mesas_data[str_m]
    cardapio = carregar_cardapio_disco()

    # Identificação do cliente na mesa (se ainda não tiver)
    if not d_mesa.get("cliente"):
        st.info("Por favor, identifique-se para começar a fazer os seus pedidos.")
        with st.form("form_cliente_mesa"):
            nome_cli = st.text_input("Seu Nome:")
            tel_cli = st.text_input("Seu Telemóvel:")
            btn_entrar = st.form_submit_button("Entrar na Mesa", use_container_width=True)
            if btn_entrar:
                if nome_cli.strip():
                    d_mesa["cliente"] = {"nome": nome_cli, "telefone": tel_cli}
                    d_mesa["status"] = "Ocupada"
                    salvar_mesas_disco(mesas_data)
                    st.success("Bem-vindo! Já pode realizar os seus pedidos.")
                    st.rerun()
                else:
                    st.warning("Por favor, insira o seu nome.")
        return

    # Cliente já identificado
    cli = d_mesa["cliente"]
    st.write(f"Olá, **{cli['nome']}**! | Estado da Mesa: **{d_mesa['status']}**")
    
    tab_cardapio, tab_conta = st.tabs(["📋 Cardápio & Pedir", "🧾 Minha Conta Atual"])

    with tab_cardapio:
        st.subheader("Escolha os seus itens")
        
        # Agrupar por categorias
        cats = list(set([item["categoria"] for item in cardapio if item["disponivel"]]))
        cat_selecionada = st.selectbox("Filtrar Categoria:", ["Todas"] + cats)

        for item in cardapio:
            if not item["disponivel"]:
                continue
            if cat_selecionada != "Todas" and item["categoria"] != cat_selecionada:
                continue

            col_item1, col_item2, col_item3 = st.columns([3, 2, 2])
            with col_item1:
                st.write(f"**{item['nome']}**")
                st.caption(f"Categoria: {item['categoria']}")
            with col_item2:
                st.write(f"**{item['preco']:,.2f} Kz**")
            with col_item3:
                with st.form(f"form_item_{item['id']}"):
                    qtd = st.number_input("Qtd", min_value=1, max_value=10, value=1, key=f"q_{item['id']}")
                    obs = st.text_input("Observações (ex: sem gelo, mal passado)", key=f"obs_{item['id']}")
                    btn_pedir = st.form_submit_button("➕ Adicionar", use_container_width=True)
                    
                    if btn_pedir:
                        novo_pedido = {
                            "item": item["nome"],
                            "preco": item["preco"],
                            "quantidade": qtd,
                            "obs": obs,
                            "status": "Pendente",
                            "cozinha_status": "NaFila"
                        }
                        d_mesa["pedidos"].append(novo_pedido)
                        # Recalcular total
                        t_calc = sum(p['quantidade'] * p['preco'] for p in d_mesa["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"])
                        d_mesa["total"] = float(t_calc)
                        d_mesa["status"] = "Pedido Solicitado"
                        salvar_mesas_disco(mesas_data)
                        st.success(f"Adicionado: {qtd}x {item['nome']}!")
                        st.rerun()

    with tab_conta:
        st.subheader("Resumo de Consumo da Mesa")
        pedidos = d_mesa.get("pedidos", [])
        if not pedidos:
            st.info("Ainda não efetuou nenhum pedido.")
        else:
            total_parcial = 0.0
            for idx, p in enumerate(pedidos):
                sub = p["quantidade"] * p["preco"]
                if p["status"] not in ["Anulado", "Recusado pela Cozinha"]:
                    total_parcial += sub
                st.write(f"- **{p['quantidade']}x** {p['item']} — **{sub:,.2f} Kz** [{p['status']} | Cozinha: {p.get('cozinha_status', 'N/A')}]")
                if p.get('obs'):
                    st.caption(f"Obs: {p['obs']}")

            st.divider( )
            st.write(f"### Total a Pagar: {total_parcial:,.2f} Kz")
            
            if st.button("🛎️ Chamar Empregado / Fechar Conta", use_container_width=True):
                st.success("Obrigado! Um funcionário foi notificado para atender a sua mesa e fechar a conta.")


# ==========================================
# ÁREA: COZINHA
# ==========================================
def area_cozinha():
    st.title("🍳 Painel da Cozinha - Gestão de Pedidos")
    
    mesas_data = carregar_mesas_disco()
    
    if st.button("🔄 Atualizar Pedidos", use_container_width=True):
        st.rerun()

    st.divider()
    
    tem_pedidos = False
    for num_m, d_mesa in mesas_data.items():
        pedidos = d_mesa.get("pedidos", [])
        for idx_p, p in enumerate(pedidos):
            # Mostrar se não estiver cancelado
            if p["status"] != "Anulado":
                tem_pedidos = True
                c_status = p.get("cozinha_status", "NaFila")
                
                with st.container(border=True):
                    col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
                    with col_c1:
                        st.write(f"### Mesa {num_m}")
                        st.write(f"**Item:** {p['quantidade']}x {p['item']}")
                        if p.get('obs'):
                            st.warning(f"Obs: {p['obs']}")
                    with col_c2:
                        st.write(f"Estado Cozinha: **{c_status}**")
                        st.write(f"Cliente: {d_mesa['cliente']['nome'] if d_mesa.get('cliente') else 'Balcão'}")
                    with col_c3:
                        if c_status == "NaFila":
                            if st.button("👨‍🍳 Aceitar", key=f"aceitar_{num_m}_{idx_p}"):
                                mesas_data[num_m]["pedidos"][idx_p]["cozinha_status"] = "EmPreparacao"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif c_status == "EmPreparacao":
                            if st.button("✅ Pronto", key=f"pronto_{num_m}_{idx_p}"):
                                mesas_data[num_m]["pedidos"][idx_p]["cozinha_status"] = "Pronto"
                                mesas_data[num_m]["pedidos"][idx_p]["status"] = "Entregue"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif c_status == "Pronto":
                            st.success("Pronto para servir!")

    if not tem_pedidos:
        st.info("Nenhum pedido ativo no momento.")


# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS
# ==========================================
def area_caixa():
    st.title("💵 Área de Caixa - Gestão de Mesas & Faturação")

    caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    col_cx_info, col_cx_cmd = st.columns([3, 1])
    with col_cx_info:
        if caixa_aberto:
            st.success("🟢 Estado do Caixa: ABERTO")
        else:
            st.error("🔴 Estado do Caixa: FECHADO")
    with col_cx_cmd:
        if caixa_aberto:
            if st.button("🔴 Fechar Caixa", use_container_width=True):
                gravar_estado_caixa_disco(False)
                st.success("Caixa fechado com sucesso!")
                st.rerun()
        else:
            if st.button("🟢 Abrir Caixa", use_container_width=True):
                gravar_estado_caixa_disco(True)
                st.success("Caixa aberto com sucesso!")
                st.rerun()

    st.divider()

    tab_mesas, tab_qrcode = st.tabs(["🪑 Controlo de Mesas & Pedidos", "📷 QR Codes das Mesas"])

    with tab_mesas:
        st.subheader("Painel Geral das Mesas (1 a 30)")
        
        lista_mesas_num = list(range(1, 31))
        mesa_selecionada = st.selectbox("Selecione a Mesa para Gerir:", lista_mesas_num, format_func=lambda x: f"Mesa {x}")
        
        str_m = str(mesa_selecionada)
        d_mesa = mesas_data[str_m]
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.write(f"### Mesa {mesa_selecionada}")
            status_m = d_mesa.get("status", "Fechada")
            st.write(f"Estado: **{status_m}**")
            if d_mesa.get("cliente"):
                cli = d_mesa["cliente"]
                st.write(f"**Cliente:** {cli['nome']} | **Tel:** {cli['telefone']}")
            else:
                st.info("Nenhum cliente registado nesta mesa ainda.")
        with col_m2:
            st.write(f"**Total Consumido:** {d_mesa.get('total', 0.0):,.2f} Kz")
            if st.button("🧹 Limpar / Fechar Mesa", key=f"limpar_mesa_{mesa_selecionada}"):
                mesas_data[str_m] = {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "fatura_emitida": None}
                salvar_mesas_disco(mesas_data)
                st.success(f"Mesa {mesa_selecionada} limpa e fechada com sucesso!")
                st.rerun()

        st.markdown("#### Pedidos da Mesa")
        pedidos_m = d_mesa.get("pedidos", [])
        if not pedidos_m:
            st.info("Sem pedidos registados nesta mesa.")
        else:
            for idx_p, p in enumerate(pedidos_m):
                tot_p = p['quantidade'] * p['preco']
                col_p1, col_p2, col_p3 = st.columns([3, 2, 2])
                with col_p1:
                    st.write(f"- {p['quantidade']}x {p['item']} ({tot_p:,.2f} Kz) [{p['status']}]")
                    if p.get('obs'):
                        st.caption(f"Obs: {p['obs']}")
                with col_p2:
                    st.write(f"Cozinha: {p.get('cozinha_status', 'N/A')}")
                with col_p3:
                    if p['status'] != "Anulado":
                        if st.button("❌ Anular", key=f"anular_p_{mesa_selecionada}_{idx_p}"):
                            mesas_data[str_m]["pedidos"][idx_p]["status"] = "Anulado"
                            t_calc = sum(item['quantidade'] * item['preco'] for item in mesas_data[str_m]["pedidos"] if item['status'] not in ["Anulado", "Recusado pela Cozinha"])
                            mesas_data[str_m]["total"] = float(t_calc)
                            salvar_mesas_disco(mesas_data)
                            st.success("Pedido anulado!")
                            st.rerun()

        st.divider()
        st.subheader("💳 Emissão de Fatura / Pagamento")
        with st.form(f"form_pagamento_{mesa_selecionada}"):
            forma_pg = st.selectbox("Forma de Pagamento:", ["Dinheiro", "TPA (Multicaixa)", "Misto (Dinheiro + TPA)"])
            val_dinheiro_informado = st.number_input("Valor em Dinheiro (Kz):", min_value=0.0, value=float(d_mesa.get('total', 0.0)))
            val_tpa_informado = st.number_input("Valor em TPA (Kz):", min_value=0.0, value=0.0)
            
            btn_emitir = st.form_submit_button("🧾 Emitir Fatura e Fechar Mesa", use_container_width=True)
            if btn_emitir:
                if d_mesa.get('total', 0.0) <= 0:
                    st.warning("A mesa não possui valores a pagar.")
                else:
                    fat_dados = {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "cliente": d_mesa['cliente']['nome'] if d_mesa.get('cliente') else "Cliente Balcão",
                        "telefone": d_mesa['cliente']['telefone'] if d_mesa.get('cliente') else "N/D",
                        "itens": d_mesa['pedidos'],
                        "total": d_mesa['total'],
                        "pagamento_detalhe": f"{forma_pg} (Dinheiro: {val_dinheiro_informado:,.2f} Kz | TPA: {val_tpa_informado:,.2f} Kz)"
                    }
                    d_mesa["fatura_emitida"] = fat_dados
                    
                    hist_vendas = carregar_historico_vendas()
                    reg_venda_hist = {
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Mesa": mesa_selecionada,
                        "Cliente": fat_dados["cliente"],
                        "Total Bruto": d_mesa['total'],
                        "Valor Dinheiro": val_dinheiro_informado,
                        "Valor TPA": val_tpa_informado,
                        "Pagamento": forma_pg
                    }
                    hist_vendas.append(reg_venda_hist)
                    salvar_historico_vendas(hist_vendas)
                    
                    salvar_mesas_disco(mesas_data)
                    st.success("Fatura emitida com sucesso!")
                    st.rerun()

    with tab_qrcode:
        st.subheader("📷 QR Codes para as Mesas (1 a 30)")
        st.info("Imprima estes QR Codes para colocar nas mesas do restaurante.")
        
        cols_qr = st.columns(3)
        for i in range(1, 31):
            url_mesa = f"{URL_OFICIAL}/?mesa={i}"
            img_bytes = gerar_qrcode_bytes(url_mesa)
            
            with cols_qr[(i - 1) % 3]:
                st.markdown(f"<div style='border: 1px solid #2a2a4a; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;'>", unsafe_allow_html=True)
                st.write(f"### Mesa {i}")
                st.image(img_bytes, width=150)
                st.text(f"/?mesa={i}")
                st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
def area_administrador():
    st.title("⚙️ Painel de Administração - Gestão do Sistema")

    cardapio = carregar_cardapio_disco()
    hist_vendas = carregar_historico_vendas()

    tab_cardapio_adm, tab_vendas_adm, tab_links_adm = st.tabs(["📋 Gerir Cardápio", "📊 Relatório de Vendas", "🔗 Links de Acesso Rápido"])

    with tab_cardapio_adm:
        st.subheader("Adicionar Novo Item ao Cardápio")
        with st.form("form_novo_item"):
            nome_novo = st.text_input("Nome do Prato/Bebida:")
            cat_nova = st.selectbox("Categoria:", ["Pratos Principais", "Entradas", "Bebidas", "Sobremesas", "Outros"])
            preco_novo = st.number_input("Preço (Kz):", min_value=0.0, value=1000.0)
            btn_add_cardapio = st.form_submit_button("Adicionar ao Cardápio", use_container_width=True)
            
            if btn_add_cardapio:
                if nome_novo.strip():
                    novo_id = max([i["id"] for i in cardapio], default=0) + 1
                    cardapio.append({
                        "id": novo_id,
                        "nome": nome_novo,
                        "categoria": cat_nova,
                        "preco": preco_novo,
                        "disponivel": True
                    })
                    salvar_cardapio_disco(cardapio)
                    st.success("Item adicionado com sucesso!")
                    st.rerun()

        st.divider()
        st.subheader("Itens Existentes")
        for idx, item in enumerate(cardapio):
            col_a1, col_a2, col_a3 = st.columns([3, 2, 1])
            with col_a1:
                st.write(f"**{item['nome']}** ({item['categoria']}) - {item['preco']:,.2f} Kz")
            with col_a2:
                disp = st.checkbox("Disponível", value=item["disponivel"], key=f"disp_adm_{item['id']}")
                if disp != item["disponivel"]:
                    cardapio[idx]["disponivel"] = disp
                    salvar_cardapio_disco(cardapio)
                    st.rerun()
            with col_a3:
                if st.button("🗑️ Apagar", key=f"del_adm_{item['id']}"):
                    cardapio.pop(idx)
                    salvar_cardapio_disco(cardapio)
                    st.rerun()

    with tab_vendas_adm:
        st.subheader("Histórico de Vendas Faturadas")
        if not hist_vendas:
            st.info("Ainda não existem registos de vendas.")
        else:
            df_vendas = pd.DataFrame(hist_vendas)
            st.dataframe(df_vendas, use_container_width=True)
            total_geral_fat = df_vendas["Total Bruto"].sum()
            st.metric("Faturamento Total Acumulado", f"{total_geral_fat:,.2f} Kz")

    with tab_links_adm:
        st.subheader("Links Diretos para os Diferentes Perfis")
        st.write(f"- **Painel de Administração:** `{URL_OFICIAL}`")
        st.write(f"- **Painel da Cozinha:** `{URL_OFICIAL}/?perfil=cozinha`")
        st.write(f"- **Painel de Caixa:** `{URL_OFICIAL}/?perfil=caixa`")
        st.write(f"- **Exemplo de Mesa (Mesa 1):** `{URL_OFICIAL}/?mesa=1`")


# ==========================================
# ROTEADOR PRINCIPAL DA APLICAÇÃO
# ==========================================
if perfil_url == "cozinha":
    area_cozinha()
elif perfil_url == "caixa":
    area_caixa()
elif mesa_detectada and 1 <= mesa_detectada <= 30:
    area_cliente()
else:
    area_administrador()
