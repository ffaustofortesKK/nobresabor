import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from fpdf import FPDF
import qrcode
from io import BytesIO

# Configuração da Página
st.set_page_config(
    page_title="NobreSabor - Sistema de Gestão",
    page_icon="🍽️",
    layout="wide"
)

# Estilos CSS (Fundo Preto / Tema Escuro)
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
        max-width: 85% !important;
        margin: 0 auto !important;
        background-color: #0c0c16 !important;
    }

    html, body, [class*="css"], .stMarkdown, p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    input, select, option {
        color: #000000 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *, div[role="listbox"] * {
        color: #000000 !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .mesa-circle {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        margin: 0 auto 2px auto;
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

    .fatura-box {
        background-color: #141428;
        border: 2px dashed #ffb703;
        padding: 20px;
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

ARQUIVO_ESTADO_CAIXA = "caixa_status.txt"
ARQUIVO_DADOS_MESAS = "mesas_dados.json"
ARQUIVO_HISTORICO_VENDAS = "historico_vendas.json"
ARQUIVO_SAIDAS_CAIXA = "saidas_caixa.json"
ARQUIVO_STOCK = "stock_dados.json"
ARQUIVO_FECHOS_CAIXA = "fechos_caixa_historico.json"
ARQUIVO_ATENDIMENTOS_GARCON = "atendimentos_garcon.json"
ARQUIVO_RH_COLABORADORES = "rh_colaboradores.json"
ARQUIVO_VENDAS_EXCLUIDAS = "vendas_excluidas.json"
ARQUIVO_SESSAO_CAIXA_OPERADOR = "sessao_caixa_operador.json"

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

def carregar_sessao_operador():
    if os.path.exists(ARQUIVO_SESSAO_CAIXA_OPERADOR):
        try:
            with open(ARQUIVO_SESSAO_CAIXA_OPERADOR, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"logado": False, "operador": "Nenhum", "periodo": "N/A", "turno_aberto": False, "saldo_inicial": 0.0, "hora_abertura": ""}

def salvar_sessao_operador(sessao_dict):
    try:
        with open(ARQUIVO_SESSAO_CAIXA_OPERADOR, "w", encoding="utf-8") as f:
            json.dump(sessao_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_mesas_disco():
    if os.path.exists(ARQUIVO_DADOS_MESAS):
        try:
            with open(ARQUIVO_DADOS_MESAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {str(i): {"status": "Fechada", "pedidos": [], "total": 0.0, "cliente": None, "garcon": "Não atribuído", "fatura_emitida": None} for i in range(1, 31)}

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
    return []

def salvar_historico_vendas(hist_list):
    try:
        with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
            json.dump(hist_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_fechos_caixa():
    if os.path.exists(ARQUIVO_FECHOS_CAIXA):
        try:
            with open(ARQUIVO_FECHOS_CAIXA, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_fechos_caixa(fechos_list):
    try:
        with open(ARQUIVO_FECHOS_CAIXA, "w", encoding="utf-8") as f:
            json.dump(fechos_list, f, ensure_ascii=False, indent=4)
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

def gerar_pdf_fatura(fat_data, num_mesa):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Restaurante Nobre Sabor", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Fatura / Recibo — Mesa {num_mesa}", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Data: {fat_data['data']}", ln=True)
    pdf.cell(0, 7, f"Cliente: {fat_data['cliente']}", ln=True)
    pdf.cell(0, 7, f"Telefone: {fat_data['telefone']}", ln=True)
    if fat_data.get('nif'):
        pdf.cell(0, 7, f"NIF: {fat_data['nif']}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, "Descrição do Item", 1)
    pdf.cell(20, 8, "Qtd", 1, align="C")
    pdf.cell(40, 8, "Preço Unit.", 1, align="R")
    pdf.cell(40, 8, "Total", 1, align="R", ln=True)
    
    pdf.set_font("Arial", "", 10)
    for item in fat_data['itens']:
        sub_item = item['quantidade'] * item['preco']
        pdf.cell(90, 8, str(item['item']), 1)
        pdf.cell(20, 8, str(item['quantidade']), 1, align="C")
        pdf.cell(40, 8, f"{item['preco']:,.2f} Kz", 1, align="R")
        pdf.cell(40, 8, f"{sub_item:,.2f} Kz", 1, align="R", ln=True)
        
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Forma de Pagamento: {fat_data['pagamento_detalhe']}", ln=True)
    
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, f"Total Pago: {fat_data['total']:,.2f} Kz", ln=True, align="R")
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Muito obrigado pela sua preferência! Volte sempre ao Restaurante Nobre Sabor.", ln=True, align="C")
    
    nome_arquivo = f"fatura_mesa_{num_mesa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# Parâmetros URL
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

# Seletor de Perfil / Módulo Principal
if perfil_url == "cliente" or mesa_detectada:
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
            if fat.get('nif'):
                st.markdown(f"<p style='text-align: center;'><b>NIF:</b> {fat['nif']}</p>", unsafe_allow_html=True)
            st.divider()
            
            for item in fat['itens']:
                st.write(f"- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.2f} Kz")
            
            st.markdown(f"### Total Pago: **{fat['total']:,.2f} Kz**")
            st.markdown(f"<p><b>Forma de Pagamento:</b> {fat['pagamento_detalhe']}</p>", unsafe_allow_html=True)
            st.divider()
            
            try:
                pdf_path = gerar_pdf_fatura(fat, num_mesa)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Descarregar Fatura em PDF",
                            data=pdf_file,
                            file_name=f"Fatura_Mesa_{num_mesa}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            except Exception:
                st.warning("Não foi possível gerar o PDF de download automático.")

            st.markdown("<h3 style='text-align: center;'>🙏 Muito obrigado pela sua presença! Volte sempre!</h3>", unsafe_allow_html=True)
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
                    nif_cli = st.text_input("NIF (Opcional):", placeholder="Ex: 5000000000")
                    whatsapp_opt = st.checkbox("Deseja entrar no Grupo de WhatsApp?")
                    
                    btn_reg = st.form_submit_button("Entrar e Ver Menu", use_container_width=True)
                    if btn_reg and nome_cli and tel_cli:
                        dados_m["cliente"] = {
                            "nome": nome_cli,
                            "telefone": tel_cli,
                            "nif": nif_cli if nif_cli else "",
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
                            st.success(f"✅ Pedido de {qtd}x {item_escolhido} enviado!")
                            st.rerun()
                            
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
                st.markdown("- Sexta: Música ao Vivo\n- Sábado: Karaoke")

    area_cliente()
else:
    # Painel de Gestão Interno (Caixa, Cozinha, Admin)
    st.title("🍽️ NobreSabor - Painel de Gestão Interno")
    
    tab_cozinha, tab_caixa, tab_admin = st.tabs(["🍳 Cozinha", "💻 Caixa & Mesas", "⚙️ Administração"])
    
    with tab_cozinha:
        st.subheader("Painel de Controlo da Cozinha")
        mesas_data = carregar_mesas_disco()
        tem_pedidos = False
        for i in range(1, 31):
            str_i = str(i)
            dados_m = mesas_data[str_i]
            for idx_p, ped in enumerate(dados_m["pedidos"]):
                cat_p = str(ped.get("tipo", "")).lower()
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped["status"] != "Anulado" and ped.get("cozinha_status") != "Feito":
                    tem_pedidos = True
                    st.write(f"**Mesa {i}** — {ped['quantidade']}x {ped['item']} (Obs: {ped.get('obs', 'Nenhuma')}) — Estado: `{ped.get('cozinha_status', 'Pendente')}`")
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("Aprovar / Preparar", key=f"apr_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
                    with col_b2:
                        if st.button("Marcar como Feito", key=f"feito_{i}_{idx_p}"):
                            mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                            salvar_mesas_disco(mesas_data)
                            st.rerun()
        if not tem_pedidos:
            st.success("Nenhuma refeição pendente na cozinha.")

    with tab_caixa:
        st.subheader("Módulo de Caixa")
        caixa_status_atual = ler_estado_caixa_disco()
        st.write(f"Estado atual do Caixa no sistema: **{'ABERTO' if caixa_status_atual else 'FECHADO'}**")
        if st.button("Alternar Estado do Caixa"):
            gravar_estado_caixa_disco(not caixa_status_atual)
            st.rerun()

    with tab_admin:
        st.subheader("Painel Administrativo")
        st.write("Aqui pode gerir o stock, colaboradores e definições globais.")
        stock_df = st.session_state.stock
        st.dataframe(stock_df, use_container_width=True)
