import json
from datetime import datetime, timedelta

# Nome do ficheiro de histórico que o sistema lê
ARQUIVO_HISTORICO_VENDAS = "historico_vendas.json"

# Dados simulados para garantir que tens informação imediata
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

# Grava os dados diretamente no disco
with open(ARQUIVO_HISTORICO_VENDAS, "w", encoding="utf-8") as f:
    json.dump(dados_exemplo, f, ensure_ascii=False, indent=4)

print("✅ Dados de faturação de ontem e hoje criados com sucesso no ficheiro 'historico_vendas.json'!")
