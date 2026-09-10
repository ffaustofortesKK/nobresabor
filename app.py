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

# Estilos CSS Profissionais, Moldura Realista de Telemóvel e Animação de Sucesso
st.markdown("""
    <style>
    .stApp, body, html {
        background-color: #0c0c16 !important;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 90% !important;
        margin: 0 auto !important;
        background-color: #0c0c16 !important;
    }

    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        color: #e2e8f0 !important;
        font-weight: 400 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    input, select, option {
        color: #000000 !important;
    }

    div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] *, div[role="listbox"] * {
        color: #000000 !important;
        font-weight: 400 !important;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    /* Moldura de Telemóvel com Entalhe (Notch) e Altifalante Estilo Real */
    .smartphone-frame {
        max-width: 380px;
        margin: 15px auto;
        background-color: #0c0c16;
        border: 12px solid #1a1a24;
        border-radius: 40px;
        padding: 30px 16px 20px 16px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.95);
        position: relative;
    }

    /* Entalhe Superior do Telemóvel (Notch e Altifalante) */
    .smartphone-frame::before {
        content: "";
        position: absolute;
        top: 8px;
        left: 50%;
        transform: translateX(-50%);
        width: 110px;
        height: 16px;
        background-color: #1a1a24;
        border-radius: 10px;
    }

    /* Animação de Alerta de Pedido Enviado com Sucesso */
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(-10px); }
        20% { opacity: 1; transform: translateY(0); }
        80% { opacity: 1; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-10px); }
    }

    .pedido-enviado-toast {
        background: linear-gradient(135deg, #2ea44f, #218838);
        color: white;
        padding: 10px 14px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
        box-shadow: 0 4px 15px rgba(46, 164, 79, 0.4);
        margin-bottom: 12px;
        animation: fadeInOut 3s ease-in-out;
    }

    .mesa-circle {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        margin: 0 auto 1px auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        overflow: hidden;
        padding: 1px;
    }

    .mesa-aberta {
        border: 2px solid #2ea44f;
        background-color: #0f2316;
        color: #4ac26b !important;
    }

    .mesa-fechada {
        border: 2px solid #21262d;
        background-color: #161b22;
        color: #8b949e !important;
    }

    @keyframes oscilarVermelho {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        50% { transform: scale(1.02); box-shadow: 0 0 8px 3px rgba(239, 68, 68, 0.9); background-color: #ef4444 !important; color: #fff !important; }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    
    @keyframes oscilarVerde {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 194, 107, 0.7); }
        50% { transform: scale(1.02); box-shadow: 0 0 8px 3px rgba(74, 194, 107, 0.9); background-color: #4ac26b !important; color: #000 !important; }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 194, 107, 0); }
    }

    .mesa-conta-solicitada {
        animation: oscilarVermelho 1.2s infinite ease-in-out;
        border: 2px solid #fff !important;
    }
    .mesa-pronta-alerta {
        animation: oscilarVerde 1.2s infinite ease-in-out;
        border: 2px solid #fff !important;
    }

    .piscar-alerta {
        animation: piscar-aviso 1s infinite;
        color: #ff4b4b !important;
    }

    @keyframes piscar-aviso {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .stButton>button {
        border-radius: 6px;
        font-weight: 500 !important;
        padding: 4px 8px !important;
        font-size: 0.8rem !important;
        color: #000000 !important;
    }
    
    .stButton>button p, .stButton>button span {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    .element-container {
        margin-bottom: 0.2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Caminhos dos Ficheiros de Base de Dados Local
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
ARQUIVO_BLOQUEIOS_OPERADORES = "bloqueios_operadores.json"

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
    return {"logado": False, "operador": "Nenhum", "periodo": "N/A", "turno_aberto": False, "saldo_inicial": 0.0, "hora_abertura": "", "trancado": False, "tentativas_falhadas": 0}

def salvar_sessao_operador(sessao_dict):
    try:
        with open(ARQUIVO_SESSAO_CAIXA_OPERADOR, "w", encoding="utf-8") as f:
            json.dump(sessao_dict, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_bloqueios():
    if os.path.exists(ARQUIVO_BLOQUEIOS_OPERADORES):
        try:
            with open(ARQUIVO_BLOQUEIOS_OPERADORES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_bloqueios(bloq_list):
    try:
        with open(ARQUIVO_BLOQUEIOS_OPERADORES, "w", encoding="utf-8") as f:
            json.dump(bloq_list, f, ensure_ascii=False, indent=4)
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
                dados = json.load(f)
                if isinstance(dados, list):
                    return dados
        except:
            pass
    return []

def salvar_fechos_caixa(fechos_list):
    try:
        with open(ARQUIVO_FECHOS_CAIXA, "w", encoding="utf-8") as f:
            json.dump(fechos_list, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar fecho de caixa: {e}")

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

def carregar_vendas_excluidas():
    if os.path.exists(ARQUIVO_VENDAS_EXCLUIDAS):
        try:
            with open(ARQUIVO_VENDAS_EXCLUIDAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_vendas_excluidas(exc_list):
    try:
        with open(ARQUIVO_VENDAS_EXCLUIDAS, "w", encoding="utf-8") as f:
            json.dump(exc_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_atendimentos_garcon():
    if os.path.exists(ARQUIVO_ATENDIMENTOS_GARCON):
        try:
            with open(ARQUIVO_ATENDIMENTOS_GARCON, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def salvar_atendimentos_garcon(atend_list):
    try:
        with open(ARQUIVO_ATENDIMENTOS_GARCON, "w", encoding="utf-8") as f:
            json.dump(atend_list, f, ensure_ascii=False, indent=4)
    except:
        pass

def carregar_rh_disco():
    if os.path.exists(ARQUIVO_RH_COLABORADORES):
        try:
            df_loaded = pd.read_json(ARQUIVO_RH_COLABORADORES, orient="split")
            if not df_loaded.empty:
                if "Salário" not in df_loaded.columns:
                    df_loaded["Salário"] = 0.0
                return df_loaded
        except:
            pass
    return pd.DataFrame([
        ["NS0001", "Carlos Manuel", "Garçon", "923000111", "001234567LA042", 75000.0],
        ["NS0002", "Ana Paula", "Operador de Caixa", "912333444", "009876543LA031", 85000.0]
    ], columns=["Código", "Nome", "Categoria", "Telefone", "BI", "Salário"])

def salvar_rh_disco(df):
    try:
        df.to_json(ARQUIVO_RH_COLABORADORES, orient="split", index=False)
    except:
        pass

def carregar_stock_disco():
    if os.path.exists(ARQUIVO_STOCK):
        try:
            df_loaded = pd.read_json(ARQUIVO_STOCK, orient="split")
            if not df_loaded.empty:
                return df_loaded
        except:
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
        try:
            df.to_json(ARQUIVO_STOCK)
        except:
            pass

def gerar_imagem_qrcode_pil(url_texto):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url_texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

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

if "rh" not in st.session_state:
    st.session_state.rh = carregar_rh_disco()

# ==========================================
# ÁREA: CLIENTE (DENTRO DA TELA DO TELEFONE)
# ==========================================
@st.fragment(run_every=6)
def area_cliente():
    if not (mesa_detectada and 1 <= mesa_detectada <= 30):
        st.error("⚠️ Mesa inválida! Escaneie o QR correto.")
        return

    num_mesa = mesa_detectada
    mesas_data = carregar_mesas_disco()
    dados_m = mesas_data[str(num_mesa)]

    # Abre a moldura do smartphone com entalhe superior integrado
    st.markdown('<div class="smartphone-frame">', unsafe_allow_html=True)

    # 1. VERIFICAÇÃO PRINCIPAL: Se a fatura foi emitida (pelo caixa ou fechamento), exibe a fatura completa e o agradecimento
    if dados_m.get("fatura_emitida"):
        fat = dados_m["fatura_emitida"]
        st.markdown("<h4 style='text-align:center; font-size:0.95rem; color:#ffffff;'>🧾 Fatura Digital</h4>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:0.75rem; color:#ffb703;'><b>Restaurante Nobre Sabor</b></p>", unsafe_allow_html=True)
        
        for item in fat['itens']:
            st.markdown(f"<span style='font-size:0.7rem; color:#cccccc;'>- {item['quantidade']}x {item['item']} | {(item['quantidade']*item['preco']):,.0f}Kz</span>", unsafe_allow_html=True)
            
        st.markdown(f"<span style='font-size:0.8rem; color:#ffffff;'><b>Total Pago: {fat['total']:,.2f}Kz</b></span>", unsafe_allow_html=True)
        
        # Mensagem de agradecimento logo abaixo da fatura pedida
        st.markdown("""
            <div style='background-color: #1a1a24; padding: 10px; border-radius: 6px; border: 1px solid #ffb703; text-align: center; margin: 10px 0;'>
                <p style='color: #4ac26b; font-size: 0.8rem; margin-bottom: 2px;'>🙏 Muito Obrigado!</p>
                <p style='color: #aaaaaa; font-size: 0.7rem; line-height: 1.1;'>Agradecemos a sua preferência pelo <b>Restaurante Nobre Sabor</b>.</p>
            </div>
        """, unsafe_allow_html=True)

        try:
            pdf_path = gerar_pdf_fatura(fat, num_mesa)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Descarregar PDF", data=f, file_name=f"Fatura_NobreSabor_Mesa_{num_mesa}.pdf", use_container_width=True)
        except Exception:
            pass
            
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 2. SE O CLIENTE PEDIU A CONTA ("solicitou_fecho"), mas o caixa ainda não gerou a fatura oficial
    if dados_m.get("solicitou_fecho"):
        st.markdown(f"<div style='font-size:0.75rem; color:#ffb703; margin-bottom:6px; margin-top:10px; text-align:center; background:#1a1a24; padding:6px; border-radius:6px;'>Mesa {num_mesa}</div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background-color: #1a1a24; padding: 15px; border-radius: 8px; border: 1px solid #ffb703; text-align: center; margin-top: 20px;'>
                <h4 style='color: #ffffff; font-size: 0.9rem; margin-bottom: 8px;'>⏳ Conta Solicitada</h4>
                <p style='color: #aaaaaa; font-size: 0.75rem; line-height: 1.2;'>O seu pedido de fecho foi enviado ao caixa. Por favor, aguarde um momento enquanto processamos a sua fatura.</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 3. FLUXO NORMAL DE REGISTO DO CLIENTE (caso ainda não tenha inserido o nome)
    if not dados_m.get("cliente"):
        st.markdown(f"""
            <div style='text-align: center; background: #1a1a24; padding: 12px; border-radius: 8px; border: 1px solid #ffb703; margin-bottom: 12px; margin-top: 10px;'>
                <h4 style='font-size:0.95rem; color:#ffffff; margin-bottom: 4px;'>✨ Bem-vindo(a) ao Nobre Sabor!</h4>
                <p style='font-size:0.75rem; color:#aaaaaa; margin: 0;'>Insira os seus dados para iniciar na <b>Mesa {num_mesa}</b>.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form(f"fc_{num_mesa}"):
            nome = st.text_input("Seu Nome:", placeholder="Ex: João Silva")
            tel = st.text_input("Telemóvel:", placeholder="Ex: 923456789")
            nif = st.text_input("NIF (Opcional):", placeholder="NIF para fatura")
            whatsapp = st.checkbox("Entrar no Grupo WhatsApp?")
            
            if st.form_submit_button("Entrar e Começar", use_container_width=True) and nome and tel:
                dados_m["cliente"] = {"nome": nome, "telefone": tel, "nif": nif, "whatsapp": whatsapp}
                dados_m["status"] = "Aberta"
                salvar_mesas_disco(mesas_data)
                st.rerun()
    else:
        # 4. FLUXO NORMAL DE PEDIDOS (Cardápio, Conta Parcial, Eventos)
        cli = dados_m["cliente"]
        st.markdown(f"<div style='font-size:0.75rem; color:#ffb703; margin-bottom:6px; margin-top:10px; text-align:center; background:#1a1a24; padding:6px; border-radius:6px;'>Mesa {num_mesa} | <b>{cli['nome']}</b></div>", unsafe_allow_html=True)
        
        # Indicador visual dinâmico caso haja um pedido recém-enviado nesta sessão
        if st.session_state.get(f"pedido_recente_mesa_{num_mesa}", False):
            st.markdown("""
                <div class="pedido-enviado-toast">
                    ✅ Pedido enviado com sucesso! A preparar...
                </div>
            """, unsafe_allow_html=True)
            st.session_state[f"pedido_recente_mesa_{num_mesa}"] = False
        
        t_menu, t_cons, t_ev = st.tabs(["📋 Pedido", "📊 Conta", "🎉 Eventos"])
        
        with t_menu:
            categorias_fixas = ["Bebidas", "Refeições", "Sobremesas", "Outros"]
            
            stock_df_atual = carregar_stock_disco()
            if not stock_df_atual.empty:
                utilitarios_extras = [
                    {"Categoria": "Outros", "Produto": "Copo", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Guardanapos", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Talheres", "Preço Unitário": 0.0}
                ]
                stock_df_atual = pd.concat([stock_df_atual, pd.DataFrame(utilitarios_extras)], ignore_index=True)
            else:
                stock_df_atual = pd.DataFrame([
                    {"Categoria": "Outros", "Produto": "Copo", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Guardanapos", "Preço Unitário": 0.0},
                    {"Categoria": "Outros", "Produto": "Talheres", "Preço Unitário": 0.0}
                ])

            cats_disponiveis = [c for c in categorias_fixas if c in stock_df_atual['Categoria'].unique().tolist()]
            if not cats_disponiveis:
                cats_disponiveis = stock_df_atual['Categoria'].unique().tolist()

            cat = st.selectbox("Categoria:", cats_disponiveis, key="c_cat")
            itens = stock_df_atual[stock_df_atual['Categoria'] == cat]
            
            if not itens.empty:
                with st.form(f"fp_{num_mesa}", clear_on_submit=True):
                    lista_itens_formatada = {f"{row['Produto']} — {row['Preço Unitário']:,.2f} Kz": row['Produto'] for _, row in itens.iterrows()}
                    item_label_selecionado = st.selectbox("Item:", list(lista_itens_formatada.keys()))
                    prod = lista_itens_formatada[item_label_selecionado]
                    
                    qtd = st.number_input("Quantidade:", 1, 99, 1)
                    obs_cliente = st.text_input("Observação (opcional):", placeholder="Ex: Sem gelo...")
                    
                    if st.form_submit_button("🚀 Enviar Pedido", use_container_width=True):
                        p_row = itens[itens['Produto'] == prod].iloc[0]
                        preco_unit = float(p_row['Preço Unitário']) if 'Preço Unitário' in p_row else 0.0
                        is_ref = cat.lower() in ["refeições", "refeicoes", "pratos", "comida"]
                        
                        dados_m["pedidos"].append({
                            "item": prod, 
                            "tipo": cat, 
                            "quantidade": int(qtd),
                            "preco": preco_unit, 
                            "origem": f"Cliente ({cli['nome']})",
                            "observacao": obs_cliente, 
                            "status": "Confirmado" if not is_ref else "Pendente",
                            "cozinha_status": "N/A" if not is_ref else "Pendente", 
                            "hora": datetime.now().strftime("%H:%M")
                        })
                        
                        dados_m["total"] = float(sum(p['quantidade']*p['preco'] for p in dados_m["pedidos"] if p['status'] not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado"))
                        salvar_mesas_disco(mesas_data)
                        
                        st.session_state[f"pedido_recente_mesa_{num_mesa}"] = True
                        st.balloons()
                        st.rerun()

        with t_cons:
            total_parcial = 0
            for p in dados_m["pedidos"]:
                if p.get('status') in ["Anulado", "Recusado pela Cozinha"] or p.get('cozinha_status') == "Recusado":
                    continue
                
                t_item = p['quantidade'] * p['preco']
                total_parcial += t_item
                st.markdown(f"<span style='font-size:0.7rem; color:#cccccc;'>• {p['quantidade']}x {p['item']} ({t_item:,.0f}Kz) — {p['status']}</span>", unsafe_allow_html=True)
            
            dados_m["total"] = float(total_parcial)
            salvar_mesas_disco(mesas_data)

            st.markdown(f"<span style='font-size:0.8rem; color:#ffffff;'><b>Total Parcial: {total_parcial:,.2f}Kz</b></span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 6px 0; border-color: #222;'>", unsafe_allow_html=True)
            
            if dados_m.get("solicitou_fecho"):
                st.info("⏳ Pedido de fecho enviado ao caixa.")
                if st.button("Cancelar Pedido", key=f"cf_{num_mesa}", use_container_width=True):
                    dados_m["solicitou_fecho"] = False
                    salvar_mesas_disco(mesas_data)
                    st.rerun()
            else:
                if st.button("🔔 Pedir Conta", type="primary", use_container_width=True):
                    dados_m["solicitou_fecho"] = True
                    salvar_mesas_disco(mesas_data)
                    st.success("Conta solicitada!")
                    st.rerun()

        with t_ev:
            st.markdown("<span style='font-size:0.7rem; color:#aaaaaa;'><b>Agenda:</b><br>• Sexta: Música ao Vivo<br>• Sábado: Karaoke (Grupo FF)</span>", unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
    
# ==========================================
# ÁREA: COZINHA
# ==========================================
@st.fragment(run_every=8)
def area_cozinha():
    st.title("🍳 Área da Cozinha")
    st.session_state.caixa_aberto = ler_estado_caixa_disco()
    mesas_data = carregar_mesas_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO pela Administração.**")
        return

    tab_pendentes, tab_historico_cozinha = st.tabs(["🔥 Pedidos Pendentes", "📋 Histórico de Pratos"])

    with tab_pendentes:
        st.subheader("Pedidos de Refeições")
        tem_pedidos = False
        tem_novos_pendentes = False
        
        for i in range(1, 31):
            str_i = str(i)
            dados_m = mesas_data.get(str_i, {})
            pedidos_mesa = dados_m.get("pedidos", [])
            for idx_p, ped in enumerate(pedidos_mesa):
                cat_p = str(ped.get("tipo", "")).lower()
                c_status = ped.get("cozinha_status", "Pendente")
                
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and ped.get("status") != "Anulado" and c_status != "Entregue" and c_status != "Recusado":
                    tem_pedidos = True
                    if c_status == "Pendente":
                        tem_novos_pendentes = True
                    
                    col_c1, col_c2, col_c3 = st.columns([3, 2, 3])
                    with col_c1:
                        st.write(f"### 🍽️ Mesa {i}")
                        st.write(f"**Refeição:** {ped.get('item', 'Item')} | **Qtd:** {ped.get('quantidade', 1)}")
                        st.write(f"Obs: _{ped.get('obs', ped.get('observacao', 'Nenhuma'))}_ | Hora: `{ped.get('hora', 'N/A')}`")
                    with col_c2:
                        cor_estado = "#ffb703" if c_status == "Pendente" else ("#2a9d8f" if c_status == "Aprovado" else "#457b9d")
                        st.markdown(f"Estado: <span style='color:{cor_estado};'>{c_status}</span>", unsafe_allow_html=True)
                    with col_c3:
                        if c_status == "Pendente":
                            if st.button("✅ Aprovar", key=f"aprov_cz_{i}_{idx_p}und"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Aprovado"
                                mesas_data[str_i]["pedidos"][idx_p]["status"] = "Confirmado"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                            if st.button("❌ Recusar", key=f"rec_cz_{i}_{idx_p}und"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Recusado"
                                mesas_data[str_i]["pedidos"][idx_p]["status"] = "Recusado pela Cozinha"
                                # Atualizar o total da mesa removendo o item recusado
                                novo_t = sum(float(p.get('quantidade', 1))*float(p.get('preco', 0)) for p in mesas_data[str_i]["pedidos"] if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado")
                                mesas_data[str_i]["total"] = float(novo_t)
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif c_status == "Aprovado":
                            if st.button("🍲 Marcar Feito", key=f"feito_cz_{i}_{idx_p}und"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Feito"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                        elif c_status == "Feito":
                            st.info("A aguardar entrega")
                            if st.button("🚚 Entregue", key=f"entregue_cz_{i}_{idx_p}und"):
                                mesas_data[str_i]["pedidos"][idx_p]["cozinha_status"] = "Entregue"
                                salvar_mesas_disco(mesas_data)
                                st.rerun()
                    st.divider()
                    
        if not tem_pedidos:
            st.success("🎉 Sem refeições ativas de momento!")

        if tem_novos_pendentes:
            st.markdown("""
                <audio autoplay loop>
                  <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                  Seu navegador não suporta elemento de áudio.
                </audio>
                <div style='background-color: #780000; padding: 8px; border-radius: 6px; text-align: center; margin-bottom: 8px;'>
                    <span style='color: white; font-size: 0.9rem;'>🚨 ALARME: Novo Pedido de Refeição Pendente!</span>
                </div>
            """, unsafe_allow_html=True)

    with tab_historico_cozinha:
        st.subheader("📋 Registo de Pratos Preparados")
        lista_pratos_feitos = []
        for i in range(1, 31):
            str_i = str(i)
            dados_m = mesas_data.get(str_i, {})
            for ped in dados_m.get("pedidos", []):
                cat_p = str(ped.get("tipo", "")).lower()
                c_status = ped.get("cozinha_status", "")
                if ("refei" in cat_p or "prato" in cat_p or "comida" in cat_p) and c_status in ["Feito", "Entregue"]:
                    lista_pratos_feitos.append({
                        "Mesa": i,
                        "Prato": ped.get('item', ''),
                        "Quantidade": ped.get('quantidade', 1),
                        "Observações": ped.get('obs', ped.get('observacao', '')),
                        "Hora": ped.get('hora', ''),
                        "Estado": c_status
                    })
        
        if not lista_pratos_feitos:
            st.info("Ainda nenhum prato finalizado hoje.")
        else:
            df_feitos = pd.DataFrame(lista_pratos_feitos)
            st.dataframe(df_feitos, use_container_width=True)

import streamlit.components.v1 as components

# ==========================================
# ÁREA: CAIXA / GESTÃO DE MESAS
# ==========================================
@st.fragment(run_every=6)
def area_caixa_mesas():
    mesas_data = carregar_mesas_disco()

    # 1. Verificação de Alarme Ativo
    tem_mesas_prontas_com_alerta = False
    for str_m, dados_m in mesas_data.items():
        tem_pronto = any(p.get("cozinha_status") == "Feito" for p in dados_m.get("pedidos", []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado")
        silenciado_pelo_operador = st.session_state.get(f"silenciar_alarme_mesa_{str_m}", False)
        if tem_pronto and not silenciado_pelo_operador:
            tem_mesas_prontas_com_alerta = True
            break

    # 2. Gestão de Estado de Áudio Ativado (Evita bloqueio de autoplay do browser)
    if "som_ativado_caixa" not in st.session_state:
        st.session_state.som_ativado_caixa = False

    if not st.session_state.som_ativado_caixa:
        st.warning("⚠️ O sistema de som automático requer ativação inicial.")
        if st.button("🔊 Clique aqui para habilitar o alarme sonoro do caixa", type="primary", use_container_width=True):
            st.session_state.som_ativado_caixa = True
            st.rerun()

    # Se ativado e houver mesas prontas, disparamos o som via componente dedicado para evitar cortes do fragmento
    if st.session_state.som_ativado_caixa and tem_mesas_prontas_com_alerta:
        # Usamos um componente HTML com script persistente de loop de áudio
        audio_html = """
            <audio id="alarme_audio" autoplay loop>
              <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
            </audio>
            <script>
                var audio = document.getElementById("alarme_audio");
                audio.volume = 1.0;
                var playPromise = audio.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        console.log("Autoplay prevenido pelo browser, a tentar novamente...");
                        document.addEventListener('click', function() {
                            audio.play();
                        }, {once: true});
                    });
                }
            </script>
        """
        components.html(audio_html, height=0, width=0)

    # Inserir estilo CSS para a animação de piscar em verde
    st.markdown("""
        <style>
        @keyframes piscar-verde {
            0% { border-color: #4ac26b; box-shadow: 0 0 5px #4ac26b; background-color: rgba(74, 194, 107, 0.2); }
            50% { border-color: #ffffff; box-shadow: 0 0 20px #4ac26b; background-color: rgba(74, 194, 107, 0.6); }
            100% { border-color: #4ac26b; box-shadow: 0 0 5px #4ac26b; background-color: rgba(74, 194, 107, 0.2); }
        }
        .mesa-solicita-fecho-piscar {
            animation: piscar-verde 1s infinite;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='margin-bottom:6px;'>💻 Controlo do Caixa - Operador</h3>", unsafe_allow_html=True)
    st.session_state.caixa_aberto = ler_estado_caixa_disco()

    if not st.session_state.caixa_aberto:
        st.error("⚠️ **O Caixa encontra-se atualmente FECHADO pela Administração.**")
        return

    sessao_op = carregar_sessao_operador()
    bloqueios_lista = carregar_bloqueios()
    operador_atual_str = sessao_op.get("operador", "")
    esta_bloqueado = any(b.get("Operador") == operador_atual_str and not b.get("Resolvido", False) for b in bloqueios_lista)

    if esta_bloqueado:
        st.error(f"🚨 **CONTA BLOQUEADA POR SEGURANÇA!** O operador **{operador_atual_str}** excedeu as tentativas de senha.")
        if st.button("🚪 Terminar Sessão e Voltar", use_container_width=True):
            sessao_op["logado"] = False
            sessao_op["operador"] = "Nenhum"
            sessao_op["turno_aberto"] = False
            sessao_op["trancado"] = False
            salvar_sessao_operador(sessao_op)
            st.rerun()
        return

    if sessao_op.get("trancado", False) and sessao_op["logado"]:
        st.markdown(f"""
            <div style="background-color: #141420; padding: 15px; border-radius: 6px; border: 1px solid #ff4b4b; text-align: center; margin-bottom: 15px;">
                <h3 style="color: #ff4b4b; font-size: 1.1rem;">🔒 CAIXA TRANCADO</h3>
                <p>Operador: <b>{sessao_op['operador']}</b></p>
                <p style="font-size: 0.8rem; color: #aaa;">Insira a sua senha para voltar ao trabalho.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_destrancar_caixa"):
            senha_destrancar = st.text_input("Introduza a sua Senha:", type="password")
            btn_sub_destrancar = st.form_submit_button("🔓 Destrancar Caixa", use_container_width=True)
            
            if btn_sub_destrancar:
                senha_correta_sistema = "123123" 
                if senha_destrancar == senha_correta_sistema:
                    sessao_op["trancado"] = False
                    sessao_op["tentativas_falhadas"] = 0
                    salvar_sessao_operador(sessao_op)
                    st.success("Caixa destrancado com sucesso!")
                    st.rerun()
                else:
                    sessao_op["tentativas_falhadas"] = sessao_op.get("tentativas_falhadas", 0) + 1
                    tentativas_restantes = 5 - sessao_op["tentativas_falhadas"]
                    salvar_sessao_operador(sessao_op)
                    
                    if sessao_op["tentativas_falhadas"] >= 5:
                        bloqueios_lista.append({
                            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Operador": sessao_op['operador'],
                            "Senha Antiga (Correta)": senha_correta_sistema,
                            "Senha Errada Inserida": senha_destrancar,
                            "Resolvido": False
                        })
                        salvar_bloqueios(bloqueios_lista)
                        st.error("🚨 Limite de 5 tentativas excedido! Conta bloqueada.")
                        st.rerun()
                    else:
                        st.error(f"❌ Senha incorreta! Restam {tentativas_restantes} tentativas.")
        return

    if not sessao_op["logado"]:
        df_rh_login = carregar_rh_disco()
        lista_nomes_colab = df_rh_login['Nome'].tolist() if not df_rh_login.empty else ["Carlos Manuel", "Ana Paula"]

        with st.form("form_login_caixa_operador"):
            st.markdown("### 🔐 Autenticação do Funcionário de Caixa")
            utilizador_input = st.selectbox("Utilizador:", lista_nomes_colab)
            periodo_input = st.selectbox("Período:", ["Dia", "Noite"])
            senha_input = st.text_input("Senha:", type="password")
            
            btn_login_cx = st.form_submit_button("Entrar no Caixa", use_container_width=True)
            if btn_login_cx:
                if utilizador_input and senha_input:
                    sessao_op["logado"] = True
                    sessao_op["operador"] = utilizador_input
                    sessao_op["periodo"] = periodo_input
                    sessao_op["turno_aberto"] = False
                    sessao_op["saldo_inicial"] = 0.0
                    sessao_op["trancado"] = False
                    sessao_op["tentativas_falhadas"] = 0
                    sessao_op["hora_abertura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    salvar_sessao_operador(sessao_op)
                    st.success(f"Bem-vindo(a), {utilizador_input}!")
                    st.rerun()
                else:
                    st.warning("Preencha o utilizador e a senha.")
        return

    if not sessao_op["turno_aberto"]:
        st.markdown(f"""
            <div style="background-color: #141420; padding: 10px; border-radius: 6px; border: 1px solid #ffb703; margin-bottom: 10px;">
                <p>👤 <b>Utilizador:</b> {sessao_op['operador']} | ⏰ <b>Período:</b> {sessao_op['periodo']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        saidas_todas = carregar_saidas_caixa()
        saidas_destinadas = [s for s in saidas_todas if s.get("Destino Utilizador") == sessao_op['operador'] and s.get("Período") == sessao_op['periodo']]
        saldo_inicial_recebido = sum(float(s['Valor']) for s in saidas_destinadas)
        
        if saidas_destinadas:
            st.success(f"💵 Fundo de maneio detetado: **{saldo_inicial_recebido:,.2f} Kz**")
        else:
            st.info("💵 Sem fundo de maneio atribuído.")

        col_op1, col_op2 = st.columns(2)
        with col_op1:
            if st.button("🟢 Abertura do Período", type="primary", use_container_width=True):
                sessao_op["turno_aberto"] = True
                sessao_op["saldo_inicial"] = saldo_inicial_recebido
                sessao_op["hora_abertura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                salvar_sessao_operador(sessao_op)
                st.success("Caixa aberto!")
                st.rerun()
        with col_op2:
            if st.button("🚪 Sair", use_container_width=True):
                sessao_op["logado"] = False
                sessao_op["operador"] = "Nenhum"
                sessao_op["turno_aberto"] = False
                sessao_op["saldo_inicial"] = 0.0
                salvar_sessao_operador(sessao_op)
                st.rerun()
        return   

    hist_vendas = carregar_historico_vendas()
    stock_df_cx_card = carregar_stock_disco()

    hora_abertura_turno = sessao_op.get("hora_abertura", "2000-01-01 00:00:00")
    vendas_turno = [
        v for v in hist_vendas 
        if v.get("Data", "") >= hora_abertura_turno and v.get("Operador", sessao_op['operador']) == sessao_op['operador']
    ]

    total_dinheiro_vendas = sum(float(v.get('Valor Dinheiro', 0)) for v in vendas_turno)
    total_tpa_vendas = sum(float(v.get('Valor TPA', 0)) for v in vendas_turno)
    
    saldo_inicial_turno = float(sessao_op.get("saldo_inicial", 0.0))
    saldo_em_caixa_fisico = saldo_inicial_turno + total_dinheiro_vendas

    col_cab1, col_cab2 = st.columns([2.5, 1.5])
    with col_cab1:
        st.markdown(f"""
            <div style="background-color: #141420; padding: 8px 12px; border-radius: 6px; border: 1px solid #21262d;">
                <span style="font-size: 0.8rem; color: #ffb703;">Saldo em Caixa:</span> 
                Dinheiro: <b style="color: #4ac26b;">{saldo_em_caixa_fisico:,.2f} Kz</b> | TPA: <b style="color: #ffb703;">{total_tpa_vendas:,.2f} Kz</b>
            </div>
        """, unsafe_allow_html=True)
    with col_cab2:
        col_op_txt, col_op_btn = st.columns([1.3, 1])
        with col_op_txt:
            st.markdown(f"<div style='text-align: right; font-size: 0.8rem; padding-top: 4px;'><b>{sessao_op['operador']}</b> ({sessao_op['periodo']})</div>", unsafe_allow_html=True)
        with col_op_btn:
            if st.button("🔒 Trancar", use_container_width=True, type="secondary"):
                sessao_op["trancado"] = True
                sessao_op["tentativas_falhadas"] = 0
                salvar_sessao_operador(sessao_op)
                st.rerun()

    aba_operador_1, aba_operador_2, aba_operador_3 = st.tabs([
        "🗺️ Mesas & Operações", 
        "📚 Histórico de Vendas", 
        "🔒 Fecho de Caixa"
    ])

    with aba_operador_3:
        st.markdown("### 🔒 Auditoria e Fecho de Caixa do Período")
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1: st.metric("Saldo Inicial", f"{saldo_inicial_turno:,.2f} Kz")
        with col_res2: st.metric("Dinheiro", f"{total_dinheiro_vendas:,.2f} Kz")
        with col_res3: st.metric("TPA", f"{total_tpa_vendas:,.2f} Kz")
            
        st.markdown("---")
        if vendas_turno:
            itens_consolidados = {}
            for v in vendas_turno:
                for p in v.get("pedidos", []):
                    if p.get('status') in ["Anulado", "Recusado pela Cozinha"] or p.get('cozinha_status') == "Recusado":
                        continue
                    nome_prod = p.get('item', 'Desconhecido')
                    qtd_prod = int(p.get('quantidade', 1))
                    preco_prod = float(p.get('preco', 0.0))
                    
                    if nome_prod not in itens_consolidados:
                        itens_consolidados[nome_prod] = {"quantidade": 0, "total": 0.0, "preco": preco_prod}
                    itens_consolidados[nome_prod]["quantidade"] += qtd_prod
                    itens_consolidados[nome_prod]["total"] += (qtd_prod * preco_prod)
            
            for prod, dados in itens_consolidados.items():
                st.write(f"- **{dados['quantidade']}x** {prod} — {dados['total']:,.2f} Kz")
            
            total_geral_turno = sum(d["total"] for d in itens_consolidados.values())
            st.markdown(f"### Faturação Total: **{total_geral_turno:,.2f} Kz**")
            
            if st.button("🔒 Fechar Período de Caixa", type="primary", use_container_width=True):
                fechos = carregar_fechos_caixa()
                fechos.append({
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Operador": sessao_op['operador'],
                    "Período": sessao_op['periodo'],
                    "Total Fecho": total_geral_turno,
                    "Dinheiro": total_dinheiro_vendas,
                    "TPA": total_tpa_vendas
                })
                salvar_fechos_caixa(fechos)
                
                sessao_op["logado"] = False
                sessao_op["operador"] = "Nenhum"
                sessao_op["turno_aberto"] = False
                sessao_op["saldo_inicial"] = 0.0
                salvar_sessao_operador(sessao_op)
                st.success("Período de caixa encerrado!")
                st.rerun()
        else:
            st.info("Sem vendas registadas neste turno.")

    with aba_operador_2:
        st.markdown("### 🔍 Histórico de Vendas")
        if hist_vendas:
            pesquisa_cli = st.text_input("Filtrar Cliente/Telefone:", placeholder="Pesquisar...", key="filtro_hist_cli_caixa")
            vendas_filtradas = [v for v in hist_vendas if pesquisa_cli.lower() in str(v.get("Cliente", "")).lower() or pesquisa_cli in str(v.get("Telefone", ""))] if pesquisa_cli else hist_vendas
            
            for v_item in reversed(vendas_filtradas):
                with st.expander(f"Mesa {v_item.get('Mesa', '?')} — {v_item.get('Cliente', 'Desconhecido')} | {v_item.get('Total', 0.0):,.2f} Kz"):
                    st.write(f"Operador: {v_item.get('Operador', '')} | Data: {v_item.get('Data', '')}")
                    for p in v_item.get("pedidos", []):
                        if p.get('status') in ["Anulado", "Recusado pela Cozinha"] or p.get('cozinha_status') == "Recusado":
                            continue
                        st.markdown(f"- {p.get('quantidade', 1)}x {p.get('item')} ({p.get('preco', 0):,.2f} Kz)")
        else:
            st.info("Sem histórico.")

    with aba_operador_1:
        col_esq, col_dir = st.columns([1.1, 0.9])

        with col_dir:
            st.markdown("<h4 style='text-align: right; margin-bottom: 4px; font-size: 0.9rem;'>MESAS (1-30)</h4>", unsafe_allow_html=True)
            cols_grelha = 4
            rows = 8
            mesa_idx = 1
            
            # Variável de controlo para emitir o som de caixa registadora se houver pelo menos uma mesa a solicitar fecho
            tem_solicitacao_fecho_geral = False
            
            for r in range(rows):
                cols = st.columns(cols_grelha)
                for c in range(cols_grelha):
                    if mesa_idx > 30:
                        break
                    str_m = str(mesa_idx)
                    dados_m = mesas_data[str_m]
                    
                    status_m = dados_m.get("status", "Fechada")
                    cli_m = dados_m.get("cliente")
                    solicitou_fecho = dados_m.get("solicitou_fecho", False)
                    total_m = float(sum(float(p.get('quantidade', 1)) * float(p.get('preco', 0.0)) for p in dados_m.get("pedidos", []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado"))
                    dados_m["total"] = total_m

                    if solicitou_fecho:
                        tem_solicitacao_fecho_geral = True
                        # 💸 SÍMBOLO AUMENTADO EM MAIS 100% (font-size passado para 2.6rem)
                        simbolo_topo = '<span style="font-size: 2.6rem; line-height: 1rem;">💸</span>'
                        classe_css = "mesa-solicita-fecho-piscar"
                    else:
                        tem_refeicao = any(("refei" in str(p.get("tipo", "")).lower() or "prato" in str(p.get("tipo", "")).lower() or "comida" in str(p.get("tipo", "")).lower()) for p in dados_m["pedidos"] if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado")
                        tem_bebida = any(("bebida" in str(p.get("tipo", "")).lower() or any(w in str(p.get("item", "")).lower() for w in ["sumo", "cerveja", "refrigerante", "vinho", "agua"])) for p in dados_m["pedidos"] if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado")
                        tem_sobremesa = any(("sobremesa" in str(p.get("tipo", "")).lower()) for p in dados_m["pedidos"] if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado")
                        
                        simbolos_topo_lista = []
                        if tem_refeicao: simbolos_topo_lista.append("🍲")
                        if tem_bebida: simbolos_topo_lista.append("🍹")
                        if tem_sobremesa: simbolos_topo_lista.append("🍰")
                        simbolo_topo = " ".join(simbolos_topo_lista)

                        if any(p.get("cozinha_status") == "Feito" for p in dados_m["pedidos"] if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado"):
                            classe_css = "mesa-pronta-alerta"
                        elif status_m == "Aberta" or cli_m:
                            classe_css = "mesa-aberta"
                        else:
                            classe_css = "mesa-fechada"

                    with cols[c]:
                        nome_cliente_curto = cli_m['nome'].split()[0] if cli_m and isinstance(cli_m, dict) and cli_m.get('nome') else "Livre"
                        
                        conteudo_circulo = f"""
                            <div style="text-align: center; height: 35px; line-height: 35px; margin-bottom: 2px;">{simbolo_topo}</div>
                            <div class="mesa-circle {classe_css}">
                                <span style="font-size: 0.65rem; font-weight: 500; line-height: 1.1;">M{mesa_idx}</span>
                                <span style="font-size: 0.42rem; color: #aaa; line-height: 1.1;">{nome_cliente_curto}</span>
                                <span style="font-size: 0.42rem; color: #ffb703; line-height: 1.1;">{total_m:,.0f}K</span>
                            </div>
                        """
                        st.markdown(conteudo_circulo, unsafe_allow_html=True)
                        
                        if st.button(f"M{mesa_idx}", key=f"btn_gerir_mesa_cx_{mesa_idx}", use_container_width=True):
                            st.session_state.mesa_selecionada_caixa = mesa_idx
                            st.session_state[f"silenciar_alarme_mesa_{str_m}"] = True
                            st.session_state[f"adicionando_pedido_cx_{mesa_idx}"] = False
                            st.rerun()
                        
                    mesa_idx += 1

            # Disparar efeito sonoro de caixa registadora quando o símbolo 💸 aparece ativo
            if tem_solicitacao_fecho_geral and st.session_state.get("som_ativado_caixa", False):
                audio_fecho_html = """
                    <audio id="audio_fecho_conta" autoplay>
                      <source src="https://assets.mixkit.co/active_storage/sfx/2872/2872-preview.mp3" type="audio/mpeg">
                    </audio>
                """
                components.html(audio_fecho_html, height=0, width=0)

        with col_esq:
            with st.container():
                m_sel = st.session_state.get("mesa_selecionada_caixa", 1)
                dados_m_sel = mesas_data[str(m_sel)]
                
                cli_atual = dados_m_sel.get("cliente")
                nome_cliente_titulo = cli_atual.get('nome') if cli_atual and isinstance(cli_atual, dict) and cli_atual.get('nome') else "Livre"
                
                st.markdown(f"#### ⚙️ Mesa {m_sel} — {nome_cliente_titulo}", unsafe_allow_html=True)
                
                if st.button("➕ Adicionar Item", key=f"btn_toggle_add_pedido_{m_sel}", type="secondary", use_container_width=True):
                    st.session_state[f"adicionando_pedido_cx_{m_sel}"] = not st.session_state.get(f"adicionando_pedido_cx_{m_sel}", False)
                    st.rerun()
                
                if st.session_state.get(f"adicionando_pedido_cx_{m_sel}", False):
                    with st.container():
                        st.markdown(f"<div style='background: #141420; padding: 8px; border-radius: 6px; border: 1px solid #ffb703; margin-bottom: 8px;'>", unsafe_allow_html=True)
                        
                        if not stock_df_cx_card.empty:
                            categorias_disponiveis = ["Refeições", "Bebidas", "Sobremesas", "Outros"]
                            categorias_validas = [cat for cat in categorias_disponiveis if cat in stock_df_cx_card['Categoria'].values]
                            if not categorias_validas:
                                categorias_validas = stock_df_cx_card['Categoria'].unique().tolist()

                            cat_escolhida = st.selectbox("Categoria:", categorias_validas, key=f"cx_cat_{m_sel}")
                            itens_da_cat = stock_df_cx_card[stock_df_cx_card['Categoria'] == cat_escolhida]
                            
                            if not itens_da_cat.empty:
                                lista_itens_formatada = {f"{row['Produto']} — {row['Preço Unitário']:,.2f} Kz": row['Produto'] for _, row in itens_da_cat.iterrows()}
                                item_selecionado_label = st.selectbox("Item:", list(lista_itens_formatada.keys()), key=f"cx_item_label_{m_sel}")
                                
                                nome_item_escolhido = lista_itens_formatada[item_selecionado_label]
                                p_row = itens_da_cat[itens_da_cat['Produto'] == nome_item_escolhido].iloc[0]
                                preco_unitario = float(p_row['Preço Unitário'])
                                
                                qtd_adicionar = st.number_input("Qtd:", min_value=1, value=1, step=1, key=f"cx_qtd_{m_sel}")
                                obs_item = st.text_input("Obs:", key=f"cx_obs_{m_sel}")
                                
                                if st.button("📥 Confirmar", type="primary", key=f"cx_salvar_novo_ped_{m_sel}", use_container_width=True):
                                    is_ref_cx = cat_escolhida.lower() in ["refeições", "refeicoes", "pratos", "comida"]
                                    novo_item_reg = {
                                        "item": nome_item_escolhido,
                                        "quantidade": int(qtd_adicionar),
                                        "preco": preco_unitario,
                                        "tipo": cat_escolhida,
                                        "observacao": obs_item,
                                        "status": "Confirmado" if not is_ref_cx else "Pendente",
                                        "cozinha_status": "N/A" if not is_ref_cx else "Pendente",
                                        "origem": f"Caixa ({sessao_op['operador']})",
                                        "hora": datetime.now().strftime("%H:%M")
                                    }
                                    
                                    if not dados_m_sel.get("cliente"):
                                        dados_m_sel["cliente"] = {"nome": "Cliente Balcão", "telefone": "N/A"}
                                        dados_m_sel["status"] = "Aberta"
                                    
                                    dados_m_sel["pedidos"].append(novo_item_reg)
                                    novo_total = sum(float(i.get('quantidade', 1)) * float(i.get('preco', 0.0)) for i in dados_m_sel["pedidos"] if i.get('status') not in ["Anulado", "Recusado pela Cozinha"] and i.get('cozinha_status') != "Recusado")
                                    dados_m_sel["total"] = novo_total
                                    
                                    mesas_data[str(m_sel)] = dados_m_sel
                                    salvar_mesas_disco(mesas_data)
                                    
                                    st.session_state[f"adicionando_pedido_cx_{m_sel}"] = False
                                    st.success(f"Adicionado!")
                                    st.rerun()
                            else:
                                st.warning("Sem itens nesta categoria.")
                        else:
                            st.warning("Stock vazio.")
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<span style='font-size: 0.85rem;'><b>Consumos da Mesa</b></span>", unsafe_allow_html=True)
                pedidos_mesa = dados_m_sel.get("pedidos", [])
                
                pedidos_ativos = [p for p in pedidos_mesa if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado"]
                
                if pedidos_ativos:
                    for idx_p, p in enumerate(pedidos_mesa):
                        if p.get('status') in ["Anulado", "Recusado pela Cozinha"] or p.get('cozinha_status') == "Recusado":
                            continue
                        q = p.get('quantidade', 1)
                        preco_u = p.get('preco', 0.0)
                        subtotal_item = q * preco_u
                        
                        col_it1, col_it2 = st.columns([2.5, 1])
                        with col_it1:
                            st.markdown(f"<span style='font-size: 0.75rem;'>- {q}x {p.get('item')} ({subtotal_item:,.0f}Kz) — [{p.get('cozinha_status', 'OK')}]</span>", unsafe_allow_html=True)
                        with col_it2:
                            if st.button(f"🗑️", key=f"btn_anular_item_cx_{m_sel}_{idx_p}", use_container_width=True):
                                st.session_state[f"abrindo_anulacao_{m_sel}_{idx_p}"] = True
                        
                        if st.session_state.get(f"abrindo_anulacao_{m_sel}_{idx_p}", False):
                            with st.container():
                                motivo_anulacao = st.text_input(f"Motivo anulação ({p.get('item')}):", key=f"motivo_anulacao_txt_{m_sel}_{idx_p}")
                                col_j1, col_j2 = st.columns(2)
                                with col_j1:
                                    if st.button("Confirmar", type="primary", key=f"conf_anular_{m_sel}_{idx_p}", use_container_width=True):
                                        if motivo_anulacao.strip():
                                            p['status'] = "Anulado"
                                            p['motivo_anulacao'] = motivo_anulacao
                                            
                                            novo_total = sum(float(item.get('quantidade', 1)) * float(item.get('preco', 0.0)) for item in dados_m_sel["pedidos"] if item.get('status') not in ["Anulado", "Recusado pela Cozinha"] and item.get('cozinha_status') != "Recusado")
                                            dados_m_sel["total"] = novo_total if novo_total > 0 else 0.0
                                            mesas_data[str(m_sel)] = dados_m_sel
                                            salvar_mesas_disco(mesas_data)
                                            
                                            vendas_excluidas = carregar_vendas_excluidas()
                                            vendas_excluidas.append({
                                                "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                "Caixa": sessao_op['operador'],
                                                "Mesa": m_sel,
                                                "Item": p.get('item'),
                                                "Quantidade": q,
                                                "Valor": subtotal_item,
                                                "Motivo": motivo_anulacao,
                                                "Período": sessao_op['periodo']
                                            })
                                            salvar_vendas_excluidas(vendas_excluidas)
                                            
                                            st.session_state[f"abrindo_anulacao_{m_sel}_{idx_p}"] = False
                                            st.success("Anulado!")
                                            st.rerun()
                                        else:
                                            st.warning("Insira o motivo.")
                                with col_j2:
                                    if st.button("Cancelar", key=f"fechar_anular_{m_sel}_{idx_p}", use_container_width=True):
                                        st.session_state[f"abrindo_anulacao_{m_sel}_{idx_p}"] = False
                                        st.rerun()
                else:
                    st.info("Sem consumos ativos.")

                total_a_pagar = float(sum(float(i.get('quantidade', 1)) * float(i.get('preco', 0.0)) for i in dados_m_sel.get("pedidos", []) if i.get('status') not in ["Anulado", "Recusado pela Cozinha"] and i.get('cozinha_status') != "Recusado"))
                dados_m_sel["total"] = total_a_pagar
                
                st.markdown(f"**Total a Pagar: {total_a_pagar:,.2f} Kz**")
                
                if total_a_pagar > 0 or cli_atual:
                    st.markdown("---")
                    tipo_pagamento = st.selectbox("Forma:", ["Dinheiro", "TPA", "Misto"], key=f"pag_tipo_mesa_{m_sel}")
                    
                    v_dinheiro, v_tpa = 0.0, 0.0
                    if tipo_pagamento == "Dinheiro":
                        v_dinheiro = total_a_pagar
                    elif tipo_pagamento == "TPA":
                        v_tpa = total_a_pagar
                    else:
                        v_dinheiro = st.number_input("Dinheiro:", value=0.0, key=f"din_mesa_{m_sel}")
                        v_tpa = st.number_input("TPA:", value=max(0.0, total_a_pagar - v_dinheiro), key=f"tpa_mesa_{m_sel}")

                    if st.button("✅ Fechar Conta e Emitir Recibo", type="primary", use_container_width=True, key=f"btn_fechar_conta_mesa_{m_sel}"):
                        nome_c = cli_atual.get("nome", "Cliente Balcão") if isinstance(cli_atual, dict) else "Cliente Balcão"
                        tel_c = cli_atual.get("telefone", "N/A") if isinstance(cli_atual, dict) else "N/A"
                        
                        registo_venda = {
                            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Mesa": m_sel,
                            "Cliente": nome_c,
                            "Telefone": tel_c,
                            "Operador": sessao_op['operador'],
                            "Período": sessao_op['periodo'],
                            "Valor Dinheiro": v_dinheiro,
                            "Valor TPA": v_tpa,
                            "Valor Total": total_a_pagar,
                            "pedidos": [p for p in dados_m_sel.get("pedidos", []) if p.get('status') not in ["Anulado", "Recusado pela Cozinha"] and p.get('cozinha_status') != "Recusado"]
                        }
                        hist_vendas.append(registo_venda)
                        salvar_historico_vendas(hist_vendas)
                        
                        st.session_state[f"silenciar_alarme_mesa_{str(m_sel)}"] = False
                        
                        mesas_data[str(m_sel)] = {
                            "status": "Fechada"
                        }
                        
# ==========================================
# ÁREA: ADMINISTRADOR
# ==========================================
@st.fragment(run_every=6)
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
        st.markdown("<div style='text-align: right; color: #ffb703; font-size: 0.9rem; margin-bottom: 2px;'>🔗 Acessos Rápidos:</div>", unsafe_allow_html=True)
        col_lnk1, col_lnk2 = st.columns(2)
        with col_lnk1:
            st.link_button("💻 Abrir Painel do Caixa", "?perfil=caixa", use_container_width=True)
        with col_lnk2:
            st.link_button("🍳 Abrir Painel da Cozinha", "?perfil=cozinha", use_container_width=True)
            
    st.success("Painel de Administração desbloqueado.")
    st.markdown("---")

    vendas_exc_check = carregar_vendas_excluidas()
    tem_novas_exclusoes = len(vendas_exc_check) > 0
    nome_aba_excluidas = "🚨 Vendas Excluídas (NOVO!)" if tem_novas_exclusoes else "🚨 Vendas Excluídas"

    bloqueios_check = carregar_bloqueios()
    tem_bloqueios_ativos = any(not b.get("Resolvido", False) for b in bloqueios_check)
    nome_aba_desbloqueio = "🔓 Desbloquear Acessos (⚠️ ATENÇÃO!)" if tem_bloqueios_ativos else "🔓 Desbloquear Acessos"

    tab_fin, tab_fechos_cx, tab_saidas, tab_stk, tab_dch, tab_exc, tab_qr, tab_bloq = st.tabs([
        "💰 Finanças", 
        "📋 Fechos de Período", 
        "💸 Saídas de Caixa", 
        "📦 Stock & Menu", 
        "👥 DCH (Colaboradores)",
        nome_aba_excluidas,
        "🖨️ QR Codes",
        nome_aba_desbloqueio
    ])
    
    with tab_fin:
        st.subheader("⚙️ Controlo Geral de Abertura e Fecho do Dia")
        
        if "financa_aba_autenticada" not in st.session_state:
            st.session_state.financa_aba_autenticada = False

        if not st.session_state.financa_aba_autenticada:
            with st.form("form_senha_aba_financa"):
                st.markdown("#### 🔒 Acesso Restrito às Finanças")
                senha_fin = st.text_input("Senha de acesso às Finanças:", type="password")
                if st.form_submit_button("Desbloquear Finanças"):
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
                    if st.button("🔒 Fechar Dia", type="primary"):
                        gravar_estado_caixa_disco(False)
                        st.session_state.caixa_aberto = False
                        st.success("Dia fechado!")
                        st.rerun()
                else:
                    if st.button("🟢 Abrir Dia", type="primary"):
                        gravar_estado_caixa_disco(True)
                        st.session_state.caixa_aberto = True
                        st.success("Dia aberto!")
                        st.rerun()
            with col_adm_c2:
                if st.session_state.caixa_aberto:
                    st.info("🟢 Sistema **ABERTO**.")
                else:
                    st.warning("🔴 Sistema **FECHADO**.")

            sessao_op_adm = carregar_sessao_operador()
            hist_vendas_adm = carregar_historico_vendas()
            
            hora_abertura_adm = sessao_op_adm.get("hora_abertura", "2000-01-01 00:00:00")
            vendas_turno_adm = [
                v for v in hist_vendas_adm 
                if v.get("Data", "") >= hora_abertura_adm and v.get("Operador", sessao_op_adm.get('operador')) == sessao_op_adm.get('operador')
            ]
            
            vendas_dinheiro_adm = sum(float(v.get('Valor Dinheiro', 0)) for v in vendas_turno_adm)
            fundo_inicial_adm = float(sessao_op_adm.get("saldo_inicial", 0.0))
            saldo_fisico_atual = fundo_inicial_adm + vendas_dinheiro_adm
            
            operador_atual_nome = sessao_op_adm.get("operador", "Nenhum") if sessao_op_adm.get("logado") else "Nenhum"
            periodo_atual_nome = sessao_op_adm.get("periodo", "N/A")

            st.markdown(f"""
                <div style="background-color: #141420; padding: 10px; border-radius: 6px; border: 1px solid #ffb703; margin-top: 8px; margin-bottom: 12px;">
                    💵 <b>Saldo em Caixa:</b> <span style="color: #4ac26b;">{saldo_fisico_atual:,.2f} Kz</span><br>
                    👤 <b>Operador:</b> {operador_atual_nome} ({periodo_atual_nome}) | Fundo: {fundo_inicial_adm:,.2f} Kz
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("📊 Histórico Geral de Vendas")
            hist_vendas = carregar_historico_vendas()
            
            if not hist_vendas:
                st.info("Sem vendas registadas.")
            else:
                df_vendas = pd.DataFrame(hist_vendas)
                st.dataframe(df_vendas, use_container_width=True)
                total_geral_faturado = df_vendas['Valor Total'].sum() if 'Valor Total' in df_vendas.columns else 0
                st.markdown(f"### Faturação Total: **{total_geral_faturado:,.2f} Kz**")

    with tab_fechos_cx:
        st.subheader("📋 Relatórios de Fecho de Período")
        fechos_registados = carregar_fechos_caixa()
        
        if not fechos_registados:
            st.info("Nenhum fecho registado.")
        else:
            df_fechos = pd.DataFrame(fechos_registados)
            st.dataframe(df_fechos, use_container_width=True)
            total_fechos_acumulado = df_fechos['Total Fecho'].sum() if 'Total Fecho' in df_fechos.columns else 0
            st.markdown(f"### Total em Fechos: **{total_fechos_acumulado:,.2f} Kz**")

    with tab_saidas:
        st.subheader("💸 Saídas de Caixa")
        with st.form("form_registar_saida"):
            col_sc1, col_sc2 = st.columns(2)
            with col_sc1:
                motivo_saida = st.text_input("Motivo:")
                df_rh_saida = carregar_rh_disco()
                lista_utilizadores_padrao = df_rh_saida['Nome'].tolist() if not df_rh_saida.empty else ["Carlos", "Ana"]
                destino_utilizador = st.selectbox("Destinatário:", lista_utilizadores_padrao)
            with col_sc2:
                valor_saida = st.number_input("Valor (Kz):", min_value=0.0, value=20000.0, step=1000.0)
                periodo_destino = st.selectbox("Período:", ["Dia", "Noite"])
            
            responsavel_saida = st.text_input("Autorizado por:", value="Administração")
            
            if st.form_submit_button("🚀 Registar Saída", use_container_width=True) and motivo_saida and valor_saida > 0:
                saidas_list = carregar_saidas_caixa()
                saidas_list.append({
                    "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Motivo": motivo_saida,
                    "Destino Utilizador": destino_utilizador,
                    "Período": periodo_destino,
                    "Valor": float(valor_saida),
                    "Responsável": responsavel_saida
                })
                salvar_saidas_caixa(saidas_list)
                st.success("Saída registada!")
                st.rerun()

        st.divider()
        saidas_registadas = carregar_saidas_caixa()
        if not saidas_registadas:
            st.info("Nenhuma saída registada.")
        else:
            df_saidas = pd.DataFrame(saidas_registadas)
            st.dataframe(df_saidas, use_container_width=True)

    with tab_stk:
        st.subheader("📦 Stock & Menu")
        stock_df = carregar_stock_disco()
        
        with st.form("form_add_produto"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                novo_produto = st.text_input("Nome do Produto:")
                nova_categoria = st.selectbox("Categoria:", ["Bebidas", "Refeições", "Sobremesas", "Entradas", "Outros"])
            with col_s2:
                nova_qtd = st.number_input("Quantidade:", min_value=0, value=10)
                novo_preco = st.number_input("Preço Unitário (Kz):", min_value=0.0, value=500.0, step=100.0)
                
            if st.form_submit_button("💾 Salvar Produto", use_container_width=True) and novo_produto:
                if not stock_df.empty and novo_produto in stock_df['Produto'].values:
                    stock_df.loc[stock_df['Produto'] == novo_produto, ['Categoria', 'Quantidade', 'Preço Unitário']] = [nova_categoria, nova_qtd, novo_preco]
                else:
                    novo_df_linha = pd.DataFrame([[novo_produto, nova_categoria, nova_qtd, novo_preco]], columns=["Produto", "Categoria", "Quantidade", "Preço Unitário"])
                    stock_df = pd.concat([stock_df, novo_df_linha], ignore_index=True)
                
                salvar_stock_disco(stock_df)
                st.success("Produto guardado com sucesso no disco!")
                st.rerun()

        st.divider()
        st.dataframe(stock_df, use_container_width=True)
        
        if not stock_df.empty:
            with st.form("form_del_produto"):
                produto_a_remover = st.selectbox("Remover produto:", stock_df['Produto'].tolist())
                if st.form_submit_button("🗑️ Remover", use_container_width=True):
                    stock_df = stock_df[stock_df['Produto'] != produto_a_remover].reset_index(drop=True)
                    salvar_stock_disco(stock_df)
                    st.success("Removido!")
                    st.rerun()

    with tab_dch:
        st.subheader("👥 DCH — Colaboradores")
        df_rh_atual = carregar_rh_disco()
        
        if df_rh_atual.empty or "Código" not in df_rh_atual.columns:
            proximo_codigo = "NS0001"
        else:
            numeros = []
            for cod in df_rh_atual["Código"].astype(str):
                if cod.startswith("NS"):
                    try:
                        numeros.append(int(cod.replace("NS", "")))
                    except:
                        pass
            proximo_num = (max(numeros) + 1) if numeros else (len(df_rh_atual) + 1)
            proximo_codigo = f"NS{proximo_num:04d}"

        with st.expander("➕ Cadastrar Colaborador"):
            with st.form("form_cadastrar_colaborador"):
                st.markdown(f"**Código:** `{proximo_codigo}`")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    nome_func = st.text_input("Nome:")
                    cat_func = st.selectbox("Cargo:", ["Garçon", "Operador de Caixa", "Operador de Limpeza", "Chefe de Cozinha", "Ajudante de Cozinha"])
                    salario_func = st.number_input("Salário:", min_value=0.0, value=75000.0, step=5000.0)
                with col_r2:
                    tel_func = st.text_input("Telefone:")
                    bi_func = st.text_input("Nº BI:")
                
                if st.form_submit_button("💾 Salvar", use_container_width=True) and nome_func:
                    nova_linha_rh = pd.DataFrame([[proximo_codigo, nome_func, cat_func, tel_func, bi_func, salario_func]], columns=["Código", "Nome", "Categoria", "Telefone", "BI", "Salário"])
                    df_rh_atual = pd.concat([df_rh_atual, nova_linha_rh], ignore_index=True)
                    salvar_rh_disco(df_rh_atual)
                    st.success("Cadastrado!")
                    st.rerun()

        st.markdown("---")
        st.dataframe(df_rh_atual, use_container_width=True)

    with tab_exc:
        if tem_novas_exclusoes:
            st.markdown("<h3 class='piscar-alerta'>🚨 ALERTA: Itens Anulados!</h3>", unsafe_allow_html=True)
        else:
            st.subheader("🚨 Vendas Excluídas / Anuladas")

        vendas_excluidas_list = carregar_vendas_excluidas()
        if not vendas_excluidas_list:
            st.info("Nenhum item anulado.")
        else:
            df_exc = pd.DataFrame(vendas_excluidas_list)
            st.dataframe(df_exc, use_container_width=True)
            
            if st.button("🧹 Limpar Registo"):
                salvar_vendas_excluidas([])
                st.success("Limpo!")
                st.rerun()

    with tab_qr:
        st.subheader("🖨️ QR Codes das Mesas (1 a 30)")
        url_site = st.text_input("URL base:", value="https://nobresabor.streamlit.app")
        
        st.markdown("---")
        for linha in range(10):
            cols = st.columns(3)
            for c in range(3):
                num_mesa_qr = linha * 3 + c + 1
                if num_mesa_qr > 30:
                    break
                link_mesa = f"{url_site}/?mesa={num_mesa_qr}"
                with cols[c]:
                    st.markdown(f"**Mesa {num_mesa_qr}**")
                    st.text_input(f"Link M{num_mesa_qr}:", value=link_mesa, key=f"link_txt_mesa_{num_mesa_qr}")
                    gerada_bytes = gerar_imagem_qrcode_pil(link_mesa)
                    st.image(gerada_bytes, width=130)
                    st.download_button(f"📥 Baixar M{num_mesa_qr}", data=gerada_bytes, file_name=f"qrcode_mesa_{num_mesa_qr}.png", mime="image/png", key=f"dl_qr_{num_mesa_qr}")

    with tab_bloq:
        if tem_bloqueios_ativos:
            st.markdown("<h3 class='piscar-alerta'>⚠️ ATENÇÃO: Operadores Bloqueados!</h3>", unsafe_allow_html=True)
        else:
            st.subheader("🔓 Desbloqueio de Acessos")

        bloqueios_data = carregar_bloqueios()
        bloqueios_ativos = [b for b in bloqueios_data if not b.get("Resolvido", False)]

        if not bloqueios_ativos:
            st.info("Nenhum operador bloqueado.")
        else:
            for idx_b, b_item in enumerate(bloqueios_ativos):
                st.markdown(f"""
                    <div style="background-color: #141420; border: 1px solid #ff4b4b; padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                        🚨 Operador: <b>{b_item.get('Operador')}</b><br>
                        🔑 Senha Correta: <code style="color: #4ac26b;">{b_item.get('Senha Antiga (Correta)')}</code> | Senha Errada: <code style="color: #ff4b4b;">{b_item.get('Senha Errada Inserida')}</code>
                    </div>
                """, unsafe_allow_html=True)

                if st.button(f"✅ Desbloquear {b_item.get('Operador')}", key=f"btn_desbl_{idx_b}", use_container_width=True):
                    for item_b in bloqueios_data:
                        if item_b.get("Operador") == b_item.get("Operador") and item_b.get("Data") == b_item.get("Data"):
                            item_b["Resolvido"] = True
                    salvar_bloqueios(bloqueios_data)
                    
                    sessao_atual_op = carregar_sessao_operador()
                    if sessao_atual_op.get("operador") == b_item.get("Operador"):
                        sessao_atual_op["trancado"] = False
                        sessao_atual_op["tentativas_falhadas"] = 0
                        salvar_sessao_operador(sessao_atual_op)

                    st.success("Desbloqueado com sucesso!")
                    st.rerun()

# ==========================================
# ROTEADOR PRINCIPAL DA APLICAÇÃO
# ==========================================
def main():
    if mesa_detectada is not None:
        area_cliente()
    elif perfil_url == "caixa":
        area_caixa_mesas()
    elif perfil_url == "cozinha":
        area_cozinha()
    else:
        area_administrador()

if __name__ == "__main__":
    main()
