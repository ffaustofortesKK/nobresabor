if dados_mesa['total'] > 0:
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
                    val_tpa = float(dados_mesa['total']) - val_dinheiro
                    st.info(f"Valor restante calculado para TPA: **{val_tpa:,.2f} Kz**")

            if st.button("💳 Fechar Conta, Emitir Fatura e Agradecer", type="primary", key=f"btn_fechar_{m_ativa}"):
                nome_c_fatura = dados_mesa['cliente']['nome'] if dados_mesa.get('cliente') and isinstance(dados_mesa['cliente'], dict) else 'Cliente Mesa'
                tel_c_fatura = dados_mesa['cliente']['telefone'] if dados_mesa.get('cliente') and isinstance(dados_mesa['cliente'], dict) else 'N/A'
                
                detalhe_pag = f"Dinheiro: {val_dinheiro:,.2f} Kz | TPA: {val_tpa:,.2f} Kz" if tipo_pagamento == "Ambos (Dinheiro + TPA)" else tipo_pagamento

                # Registo seguro no histórico de vendas central
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

                # Prepara a fatura para o cliente visualizar no telemóvel
                dados_mesa["fatura_emitida"] = {
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "cliente": nome_c_fatura,
                    "telefone": tel_c_fatura,
                    "itens": list(dados_mesa["pedidos"]),
                    "total": float(dados_mesa["total"]),
                    "pagamento_detalhe": detalhe_pag
                }
                
                # Opcional: se desejar limpar a mesa logo após fechar, descomente as linhas abaixo:
                # dados_mesa["pedidos"] = []
                # dados_mesa["status"] = "Fechada"
                # dados_mesa["cliente"] = None
                
                salvar_mesas_disco(mesas_data)
                st.success("Conta fechada, fatura emitida e enviada para o cliente com sucesso!")
                if "mesa_ativa" in st.session_state:
                    del st.session_state.mesa_ativa
                st.rerun()
        else:
            st.warning("A mesa não tem valor a faturar.")
