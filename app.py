import streamlit as st
import pandas as pd
from database import DatabaseCSV
from modelos import Cliente, Material, Pattern, Pedido

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Namigurumi System", 
    page_icon="🧶", 
    layout="wide"
)

# Inicialização do Banco de Dados
@st.cache_resource
def carregar_db():
    return DatabaseCSV()

db = carregar_db()
clientes = db.carregar_clientes()
estoque = db.carregar_materiais()
patterns = db.carregar_patterns()
pedidos = db.carregar_pedidos(clientes, patterns)


# ==========================================
# FUNÇÃO: ABA DE BI / ANALYTICS
# ==========================================
def renderizar_aba_bi():
    st.title("📊 Business Intelligence & Analytics")
    st.markdown("Acompanhe a saúde financeira e o desempenho operacional.")

    if not pedidos:
        st.info("Ainda não há pedidos finalizados para gerar análises estatísticas.")
        return

    # Filtra apenas os pedidos finalizados para calcular lucro real
    pedidos_fin = [p for p in pedidos if p.status == "Finalizado"]
    
    if not pedidos_fin:
        st.warning("Nenhum pedido foi finalizado ainda. Finalize um pedido para ver as métricas de lucro.")
        return

    # Tratamento dos dados para o Pandas
    dados_pedidos = []
    for p in pedidos_fin:
        custo_final = p.calcular_custo_total_materiais(estoque)
        lucro_liquido = p.preco_venda - custo_final
        
        dados_pedidos.append({
            "id": p.id_pedido,
            "cliente": p.cliente.nome,
            "pattern": p.pattern.nome,
            "valor_venda": p.preco_venda,
            "custo": custo_final,
            "lucro_liquido": lucro_liquido
        })

    df_pedidos = pd.DataFrame(dados_pedidos)

    # Panorama Financeiro Geral
    st.subheader("💰 Panorama Financeiro (Pedidos Finalizados)")
    faturamento_total = df_pedidos["valor_venda"].sum()
    lucro_total = df_pedidos["lucro_liquido"].sum()
    margem_media = (lucro_total / faturamento_total) * 100 if faturamento_total > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Faturamento Total", value=f"R$ {faturamento_total:,.2f}")
    with col2:
        st.metric(label="Lucro Líquido Total", value=f"R$ {lucro_total:,.2f}")
    with col3:
        st.metric(label="Margem de Lucro Média", value=f"{margem_media:.1f}%")

    st.markdown("---")

    # Rankings (Lado a Lado)
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.subheader("👥 Top Clientes (Faturamento)")
        top_clientes = df_pedidos.groupby("cliente")["valor_venda"].sum().sort_values(ascending=True).tail(5)
        st.bar_chart(top_clientes, horizontal=True)

    with col_dir:
        st.subheader("🧶 Top Patterns Mais Vendidos")
        top_patterns = df_pedidos.groupby("pattern")["id"].count().sort_values(ascending=True).tail(5)
        top_patterns.name = "Quantidade"
        st.bar_chart(top_patterns, horizontal=True)

    st.markdown("---")

    # Mapa de Consumo
    st.subheader("🎨 Mapa do Estoque (Fios Atuais)")
    if estoque:
        dados_materiais = [{"Nome": f"{m.nome} ({m.cor})", "Quantidade Disponível": m.quantidade} for m in estoque.values() if m.tipo.lower() == "fio"]
        if dados_materiais:
            df_materiais = pd.DataFrame(dados_materiais).set_index("Nome")
            st.bar_chart(df_materiais["Quantidade Disponível"])
        else:
            st.info("Não há materiais do tipo 'Fio' cadastrados no estoque.")
    else:
        st.info("Não há materiais cadastrados no estoque.")


# ==========================================
# FUNÇÃO: ABA DE CLIENTES
# ==========================================
def renderizar_clientes():
    st.title("👥 Cadastro de Clientes")
    col1, col2 = st.columns([1, 2]) 
    
    with col1:
        tab_novo_cli, tab_editar_cli = st.tabs(["➕ Novo Cliente", "✏️ Editar Cliente"])
        
        with tab_novo_cli:
            st.subheader("Novo Cliente")
            with st.form("form_cliente", clear_on_submit=True):
                nome = st.text_input("Nome do Cliente*")
                contato = st.text_input("Contato (Insta/WhatsApp)")
                endereco = st.text_input("Endereço")
                cidade = st.text_input("Cidade")
                estado = st.text_input("Estado (Ex: SP)")
                cep = st.text_input("CEP")
                submit_cliente = st.form_submit_button("Salvar Cliente")
                
                if submit_cliente:
                    if not nome:
                        st.error("O campo Nome é obrigatório!")
                    else:
                        novo_c = Cliente(nome, contato, endereco, cidade, estado, cep)
                        clientes.append(novo_c)
                        db.salvar_clientes(clientes)
                        st.success("Cliente salvo com sucesso!")
                        st.rerun() 
                        
        with tab_editar_cli:
            st.subheader("Atualizar Cliente")
            if not clientes:
                st.info("Nenhum cliente cadastrado para editar.")
            else:
                opcoes_clientes = [f"{c.id_cliente} - {c.nome}" for c in clientes]
                cliente_selecionado_str = st.selectbox("Selecione o Cliente para alterar:", opcoes_clientes)
                
                if cliente_selecionado_str:
                    id_alvo = cliente_selecionado_str.split(" - ")[0]
                    c_alvo = next(c for c in clientes if str(c.id_cliente) == id_alvo)
                    
                    edit_nome = st.text_input("Nome*", value=c_alvo.nome, key=f"edit_nome_cli_{c_alvo.id_cliente}")
                    edit_contato = st.text_input("Contato", value=c_alvo.contato, key=f"edit_contato_cli_{c_alvo.id_cliente}")
                    edit_endereco = st.text_input("Endereço", value=getattr(c_alvo, 'endereco', ''), key=f"edit_end_cli_{c_alvo.id_cliente}")
                    edit_cidade = st.text_input("Cidade", value=getattr(c_alvo, 'cidade', ''), key=f"edit_cid_cli_{c_alvo.id_cliente}")
                    edit_estado = st.text_input("Estado", value=getattr(c_alvo, 'estado', ''), key=f"edit_est_cli_{c_alvo.id_cliente}")
                    edit_cep = st.text_input("CEP", value=getattr(c_alvo, 'cep', ''), key=f"edit_cep_cli_{c_alvo.id_cliente}")
                    
                    if st.button("Salvar Alterações", type="primary", key=f"btn_salvar_cli_{c_alvo.id_cliente}"):
                        if not edit_nome:
                            st.error("O nome não pode ficar em branco!")
                        else:
                            c_alvo.nome = edit_nome
                            c_alvo.contato = edit_contato
                            c_alvo.endereco = edit_endereco
                            c_alvo.cidade = edit_cidade
                            c_alvo.estado = edit_estado
                            c_alvo.cep = edit_cep
                            
                            db.salvar_clientes(clientes)
                            st.success(f"Cliente '{c_alvo.nome}' atualizado com sucesso!")
                            st.rerun()

    with col2:
        st.subheader("Clientes Cadastrados")
        if not clientes:
            st.info("Nenhum cliente cadastrado.")
        else:
            dados = [{"ID": c.id_cliente, "Nome": c.nome, "Contato": c.contato, "Local": f"{getattr(c, 'cidade', '')}/{getattr(c, 'estado', '')}"} for c in clientes]
            st.dataframe(dados, use_container_width=True)


# ==========================================
# FUNÇÃO: ABA DE ESTOQUE
# ==========================================
def renderizar_estoque():
    st.title("🧶 Estoque de Materiais")
    materiais_em_falta = [m for m in estoque.values() if m.quantidade <= 0]
    materiais_acabando = [m for m in estoque.values() if m.quantidade == 1]
    
    if materiais_em_falta or materiais_acabando:
        resumo_alerta = f"⚠️ **Lista de Compras:** {len(materiais_em_falta)} materiais esgotados e {len(materiais_acabando)} acabando. Clique aqui para expandir!"
        with st.expander(resumo_alerta, expanded=False):
            dados_compras = []
            for m in materiais_em_falta:
                dados_compras.append({"Status": "🔴 Esgotado", "SKU": m.sku, "Material": m.nome, "Cor": f"{m.cor} #{m.num_cor}"})
            for m in materiais_acabando:
                dados_compras.append({"Status": "🟡 Acabando", "SKU": m.sku, "Material": m.nome, "Cor": f"{m.cor} #{m.num_cor}"})
            st.dataframe(dados_compras, use_container_width=True)
    else:
        st.success("✅ Seu estoque está saudável! Nenhum material esgotado ou acabando.")
        
    st.divider() 
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        tab_novo_mat, tab_editar_mat = st.tabs(["➕ Novo Material", "✏️ Editar Material"])
        
        with tab_novo_mat:
            st.subheader("Cadastrar Material")
            with st.form("form_material", clear_on_submit=True):
                sku = st.text_input("SKU (Ex: FIO-VD01)*").strip().upper()
                tipo = st.selectbox("Tipo", ["Fio", "Olhos", "Focinho", "Terço", "Enchimento", "Outro"])
                nome_mat = st.text_input("Nome (Ex: Amigurumi Verde)")
                cor = st.text_input("Cor")
                num_cor = st.text_input("Número da Cor")
                quantidade = st.number_input("Quantidade em Estoque", min_value=0, step=1)
                peso = st.number_input("Peso total (gramas)", min_value=0.0, step=10.0)
                preco = st.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1)
                rendimento = st.number_input("Rendimento Base (g ou unidades)", min_value=1.0, step=1.0)
                
                submit_mat = st.form_submit_button("Salvar Material")
                
                if submit_mat:
                    if not sku:
                        st.error("O SKU é obrigatório!")
                    elif sku in estoque:
                        st.error("Esse SKU já existe! Use a aba 'Editar Material' para atualizá-lo.")
                    else:
                        novo_m = Material(sku, tipo, nome_mat, cor, num_cor, quantidade, peso if peso>0 else None, preco, rendimento)
                        estoque[sku] = novo_m
                        db.salvar_materiais(estoque)
                        st.success("Material adicionado ao estoque!")
                        st.rerun()

        with tab_editar_mat:
            st.subheader("Atualizar Material")
            if not estoque:
                st.info("Nenhum material no estoque para editar.")
            else:
                opcoes_mat = [f"{m.sku} - {m.nome} (Cor: {m.cor} #{m.num_cor})" for m in estoque.values()]
                mat_selecionado_str = st.selectbox("Selecione o Material para alterar:", opcoes_mat)
                
                if mat_selecionado_str:
                    sku_alvo = mat_selecionado_str.split(" - ")[0]
                    mat_alvo = estoque[sku_alvo]
                    
                    tipos_disponiveis = ["Fio", "Olhos", "Focinho", "Terço", "Enchimento", "Outro"]
                    try:
                        index_tipo = tipos_disponiveis.index(mat_alvo.tipo)
                    except ValueError:
                        index_tipo = 5
                    
                    edit_tipo = st.selectbox("Tipo", tipos_disponiveis, index=index_tipo, key=f"edit_tipo_{sku_alvo}")
                    edit_nome_mat = st.text_input("Nome", value=mat_alvo.nome, key=f"edit_nome_mat_{sku_alvo}")
                    edit_cor = st.text_input("Cor", value=mat_alvo.cor, key=f"edit_cor_{sku_alvo}")
                    edit_num_cor = st.text_input("Número da Cor", value=mat_alvo.num_cor, key=f"edit_num_cor_{sku_alvo}")
                    edit_quantidade = st.number_input("Quantidade em Estoque", min_value=0, step=1, value=mat_alvo.quantidade, key=f"edit_qtd_{sku_alvo}")
                    edit_peso = st.number_input("Peso total (gramas)", min_value=0.0, step=10.0, value=float(mat_alvo.peso_gramas) if mat_alvo.peso_gramas else 0.0, key=f"edit_peso_{sku_alvo}")
                    edit_preco = st.number_input("Preço de Custo (R$)", min_value=0.0, step=0.1, value=float(mat_alvo.preco_custo), key=f"edit_preco_{sku_alvo}")
                    edit_rendimento = st.number_input("Rendimento Base (g ou unidades)", min_value=1.0, step=1.0, value=float(mat_alvo.rendimento_base), key=f"edit_rend_{sku_alvo}")
                    
                    if st.button("Salvar Alterações", type="primary", key=f"btn_salvar_mat_{sku_alvo}"):
                        mat_alvo.tipo = edit_tipo
                        mat_alvo.nome = edit_nome_mat
                        mat_alvo.cor = edit_cor
                        mat_alvo.num_cor = edit_num_cor
                        mat_alvo.quantidade = edit_quantidade
                        mat_alvo.peso_gramas = edit_peso if edit_peso > 0 else None
                        mat_alvo.preco_custo = edit_preco
                        mat_alvo.rendimento_base = edit_rendimento
                        
                        db.salvar_materiais(estoque)
                        st.success(f"Material {sku_alvo} atualizado com sucesso!")
                        st.rerun()

    with col2:
        st.subheader("Estoque Atual")
        termo_busca = st.text_input("🔍 Buscar material por Nome, Cor ou SKU:", "").strip().lower()
        
        if not estoque:
            st.info("Estoque vazio.")
        else:
            materiais_filtrados = []
            for m in estoque.values():
                if not termo_busca or termo_busca in m.nome.lower() or termo_busca in m.sku.lower() or termo_busca in m.cor.lower():
                    materiais_filtrados.append(m)
            
            if not materiais_filtrados:
                st.warning("Nenhum material encontrado com esse termo.")
            else:
                dados_est = [{"SKU": m.sku, "Tipo": m.tipo, "Nome": m.nome, "Cor": f"{m.cor} #{m.num_cor}", "Qtd": m.quantidade, "Custo Unit": f"R$ {m.obter_custo_unitario():.2f}"} for m in materiais_filtrados]
                st.dataframe(dados_est, use_container_width=True)


# ==========================================
# FUNÇÃO: ABA DE PATTERNS
# ==========================================
def renderizar_patterns():
    st.title("📝 Patterns (Receitas)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        tab_novo, tab_editar = st.tabs(["➕ Novo Pattern", "✏️ Editar Pattern"])
        
        with tab_novo:
            st.subheader("Cadastrar Pattern")
            nome_pat = st.text_input("Nome do Amigurumi* (Ex: Chopper)")
            obs = st.text_area("Observações (Ex: na carreira 4 não são 19 pontos)")
            
            st.markdown("📝 **Materiais Necessários**")
            quantidades = {}
            skus_list = []
            
            if not estoque:
                st.warning("Cadastre materiais no Estoque primeiro para selecioná-los.")
            else:
                opcoes_estoque = [f"{m.sku} - {m.nome} (Cor: {m.cor} #{m.num_cor})" for m in estoque.values()]
                materiais_selecionados = st.multiselect("Selecione os materiais no estoque:", opcoes_estoque, key="novo_pattern_multi")
                
                if materiais_selecionados:
                    st.markdown("**Defina a quantidade:**")
                    for item in materiais_selecionados:
                        sku = item.split(" - ")[0]
                        qtd = st.number_input(f"Qtd de {sku}", min_value=0.1, step=1.0, value=1.0, key=f"novo_qtd_{sku}")
                        skus_list.append(sku)
                        quantidades[sku] = qtd
                
            if st.button("Salvar Novo Pattern", type="primary"):
                if not nome_pat:
                    st.error("O nome do Pattern é obrigatório!")
                else:
                    novo_pattern = Pattern(nome_pat, skus_list, quantidades, obs)
                    patterns.append(novo_pattern)
                    db.salvar_patterns(patterns)
                    st.success(f"Pattern '{nome_pat}' salvo com sucesso!")
                    st.rerun()

        with tab_editar:
            st.subheader("Atualizar Pattern")
            if not patterns:
                st.info("Nenhum Pattern cadastrado para editar.")
            else:
                nomes_patterns = [p.nome for p in patterns]
                pattern_escolhido_nome = st.selectbox("Escolha a receita que deseja alterar:", nomes_patterns)
                
                pat_alvo = next(p for p in patterns if p.nome == pattern_escolhido_nome)
                
                edit_nome = st.text_input("Nome", value=pat_alvo.nome, key=f"edit_nome_{pat_alvo.nome}")
                edit_obs = st.text_area("Observações", value=pat_alvo.observacoes, key=f"edit_obs_{pat_alvo.nome}")
                
                edit_quantidades = {}
                edit_skus_list = []
                
                if estoque:
                    opcoes_estoque = [f"{m.sku} - {m.nome} (Cor: {m.cor} #{m.num_cor})" for m in estoque.values()]
                    defaults_mat = []
                    for sku in pat_alvo.skus_necessarios:
                        match = next((op for op in opcoes_estoque if op.startswith(f"{sku} - ")), None)
                        if match:
                            defaults_mat.append(match)
                            
                    edit_selecionados = st.multiselect(
                        "Materiais no estoque:", 
                        opcoes_estoque, 
                        default=defaults_mat, 
                        key=f"edit_multi_{pat_alvo.nome}"
                    )
                    
                    if edit_selecionados:
                        st.markdown("**Quantidades:**")
                        for item in edit_selecionados:
                            sku = item.split(" - ")[0]
                            qtd_atual = pat_alvo.quantidades_estimadas.get(sku, 1.0)
                            qtd = st.number_input(f"Qtd de {sku}", min_value=0.1, step=1.0, value=float(qtd_atual), key=f"edit_qtd_{sku}_{pat_alvo.nome}")
                            edit_skus_list.append(sku)
                            edit_quantidades[sku] = qtd
                
                if st.button("Salvar Alterações", type="primary", key=f"btn_salvar_{pat_alvo.nome}"):
                    if not edit_nome:
                        st.error("O nome não pode ficar em branco!")
                    else:
                        pat_alvo.nome = edit_nome
                        pat_alvo.observacoes = edit_obs
                        pat_alvo.skus_necessarios = edit_skus_list
                        pat_alvo.quantidades_estimadas = edit_quantidades
                        
                        db.salvar_patterns(patterns)
                        db.salvar_pedidos(pedidos)
                        st.success("Pattern atualizado!")
                        st.rerun()

    with col2:
        st.subheader("Patterns Cadastrados")
        termo_busca_pat = st.text_input("🔍 Buscar receita por Nome ou SKU:", "").strip().lower()
        
        if not patterns:
            st.info("Nenhum pattern cadastrado.")
        else:
            patterns_filtrados = []
            for p in patterns:
                match_nome = termo_busca_pat in p.nome.lower()
                match_sku = any(termo_busca_pat in sku.lower() for sku in p.skus_necessarios)
                if not termo_busca_pat or match_nome or match_sku:
                    patterns_filtrados.append(p)
            
            if not patterns_filtrados:
                st.warning("Nenhuma receita encontrada com esse termo.")
            else:
                for p in patterns_filtrados:
                    with st.expander(f"🧶 {p.nome}"):
                        st.write(f"**Observações:** {p.observacoes}")
                        if p.quantidades_estimadas:
                            st.write("**Materiais Base:**")
                            for s, q in p.quantidades_estimadas.items():
                                if s in estoque:
                                    mat = estoque[s]
                                    st.write(f"- {q}x {s} ({mat.nome} - {mat.cor})")
                                else:
                                    st.write(f"- {q}x {s} (SKU antigo, não está mais no estoque)")
                        else:
                            st.write("Nenhum material base listado.")


# ==========================================
# FUNÇÃO: ABA DE PEDIDOS (COM FILTROS)
# ==========================================
def renderizar_pedidos():
    st.title("📦 Gestão de Pedidos")
    
    with st.expander("➕ CRIAR NOVO PEDIDO", expanded=False):
        if not clientes or not patterns:
            st.warning("Cadastre ao menos 1 Cliente e 1 Pattern para criar pedidos.")
        else:
            with st.form("form_pedido", clear_on_submit=True):
                cliente_sel = st.selectbox("Selecione o Cliente", clientes, format_func=lambda c: f"{c.nome} (ID: {c.id_cliente})")
                pattern_sel = st.selectbox("Selecione o Pattern", patterns, format_func=lambda p: p.nome)
                preco_venda = st.number_input("Preço Cobrado do Cliente (R$)", min_value=0.0, step=5.0)
                
                submit_ped = st.form_submit_button("Gerar Pedido em Espera")
                if submit_ped:
                    novo_p = Pedido(cliente_sel, pattern_sel, preco_venda)
                    pedidos.append(novo_p)
                    db.salvar_pedidos(pedidos)
                    st.success(f"Pedido criado com sucesso! ID: {novo_p.id_pedido}")
                    st.rerun()

    if not pedidos:
        st.info("Nenhum pedido registrado.")
    else:
        # --- NOVO: SISTEMA DE BUSCA E FILTROS ---
        st.markdown("### 🔍 Filtros de Busca")
        col_filtro1, col_filtro2 = st.columns([2, 1])
        
        with col_filtro1:
            termo_busca_ped = st.text_input("Buscar por nome do Cliente ou Pattern:", "").strip().lower()
        with col_filtro2:
            filtro_status = st.selectbox("Filtrar por Status:", ["Todos", "Em espera", "Finalizado"])
            
        # Aplica a lógica de filtragem na lista
        pedidos_filtrados = []
        for p in pedidos:
            match_texto = not termo_busca_ped or (termo_busca_ped in p.cliente.nome.lower()) or (termo_busca_ped in p.pattern.nome.lower())
            match_status = (filtro_status == "Todos") or (p.status == filtro_status)
            
            if match_texto and match_status:
                pedidos_filtrados.append(p)

        st.divider()

        if not pedidos_filtrados:
            st.warning("Nenhum pedido encontrado com esses filtros.")
        else:
            pedidos_espera = [p for p in pedidos_filtrados if p.status == "Em espera"]
            pedidos_fin = [p for p in pedidos_filtrados if p.status != "Em espera"]
            
            st.markdown("### 📋 Visão Geral")
            dados_tabela = [{
                "ID": p.id_pedido, 
                "Cliente": p.cliente.nome, 
                "Pattern": p.pattern.nome,
                "Valor (R$)": f"{p.preco_venda:.2f}",
                "Lucro (R$)": f"{(p.preco_venda - p.calcular_custo_total_materiais(estoque)):.2f}" if p.status == "Finalizado" else "-",
                "Status": p.status
            } for p in pedidos_filtrados]
            st.dataframe(dados_tabela, use_container_width=True, hide_index=True)
            
            st.divider()
            
            col_ped1, col_ped2 = st.columns(2)
            
            with col_ped1:
                st.markdown("### ⏳ Em Espera")
                if not pedidos_espera:
                    st.info("Nenhum pedido em espera nesta seleção.")
                for p in pedidos_espera:
                    with st.container(border=True):
                        st.markdown(f"**ID:** {p.id_pedido} | **{p.pattern.nome}**")
                        st.write(f"👤 Cliente: {p.cliente.nome}")
                        st.write(f"💵 Preço Combinado: **R$ {p.preco_venda:.2f}**")
                        
                        fios_do_pattern = [sku for sku in p.pattern.skus_necessarios if sku in estoque and estoque[sku].tipo.lower() == "fio"]
                        
                        if not fios_do_pattern:
                            st.warning("Nenhum 'Fio' foi encontrado na receita para pesagem.")
                            if st.button("Finalizar Pedido Sem Fios", key=f"btn_fin_{p.id_pedido}"):
                                p.status = "Finalizado"
                                db.salvar_pedidos(pedidos)
                                st.rerun()
                        else:
                            with st.form(f"form_fin_{p.id_pedido}"):
                                st.write("Pesagem dos Fios (em gramas):")
                                pesos_temp_ini = {}
                                pesos_temp_fin = {}
                                
                                for sku in fios_do_pattern:
                                    fio = estoque[sku]
                                    st.markdown(f"🧶 **{fio.nome} ({fio.cor})**")
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        pesos_temp_ini[sku] = st.number_input("Início (g)", min_value=0.0, step=1.0, key=f"ini_{p.id_pedido}_{sku}")
                                    with c2:
                                        pesos_temp_fin[sku] = st.number_input("Fim (g)", min_value=0.0, step=1.0, key=f"fim_{p.id_pedido}_{sku}")
                                        
                                if st.form_submit_button("Registrar e Finalizar"):
                                    for sku in fios_do_pattern:
                                        p.registrar_peso_fio(sku, pesos_temp_ini[sku], pesos_temp_fin[sku])
                                    
                                    db.salvar_pedidos(pedidos)
                                    st.success("Pedido finalizado com sucesso!")
                                    st.rerun()

            with col_ped2:
                st.markdown("### ✅ Finalizados")
                if not pedidos_fin:
                    st.info("Nenhum pedido finalizado nesta seleção.")
                for p in pedidos_fin:
                    with st.container(border=True):
                        st.markdown(f"**ID:** {p.id_pedido} | **{p.pattern.nome}**")
                        st.write(f"👤 Cliente: {p.cliente.nome}")
                        
                        st.markdown("**Consumo por Fio:**")
                        for sku in p.pesos_iniciais.keys():
                            nome_fio = estoque[sku].nome if sku in estoque else sku
                            cor_fio = estoque[sku].cor if sku in estoque else ""
                            st.write(f"- {nome_fio} ({cor_fio}): **{p.calcular_uso_fio(sku)}g**")
                            
                        custo_final = p.calcular_custo_total_materiais(estoque)
                        lucro = p.preco_venda - custo_final
                        
                        st.write(f"💵 Preço de Venda: **R$ {p.preco_venda:.2f}**")
                        st.write(f"📉 Custo Material: **R$ {custo_final:.2f}**")
                        st.write(f"✨ **LUCRO LÍQUIDO:** **R$ {lucro:.2f}**")
                        
                        rastreio_atual = p.codigo_rastreio if p.codigo_rastreio else "Sem rastreio"
                        st.write(f"🚚 Rastreio: **{rastreio_atual}**")
                        
                        with st.popover("Editar Rastreio"):
                            novo_rastreio = st.text_input("Código", value=p.codigo_rastreio if p.codigo_rastreio else "", key=f"rast_{p.id_pedido}")
                            if st.button("Salvar Rastreio", key=f"btn_rast_{p.id_pedido}"):
                                p.atualizar_rastreio(novo_rastreio)
                                db.salvar_pedidos(pedidos)
                                st.rerun()


# ==========================================
# ESTRUTURA PRINCIPAL E NAVEGAÇÃO LATERAL
# ==========================================
def main():
    # CSS opcional para ajustar o espaçamento do topo da barra lateral
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { padding-top: 1rem; }
        </style>
        """, unsafe_allow_html=True
    )

    with st.sidebar:
        # 1. Logo e Boas-vindas centralizados e estilizados
        try:
            st.image("logo.PNG", use_container_width=True)
        except Exception:
            st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🧶 Namigurumi</h1>", unsafe_allow_html=True)
            
        st.markdown("<h3 style='text-align: center; margin-top: -10px;'>Olá, Ana Carolina! ✨</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>Gerenciador de Ateliê</p>", unsafe_allow_html=True)
        
        st.divider()
        
        # 2. Menu mais limpo (sem o título padrão)
        menu = st.radio(
            "Navegação", 
            ["📦 Pedidos", "👥 Clientes", "🧶 Estoque", "📝 Patterns", "📊 Analytics / BI"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 3. Mini-Painel de Status Rápido Dinâmico
        st.markdown("#### ⚡ Status Rápido")
        
        pedidos_espera = len([p for p in pedidos if p.status == "Em espera"])
        estoque_alerta = len([m for m in estoque.values() if m.quantidade <= 1])
        
        if pedidos_espera > 0:
            st.warning(f"⏳ {pedidos_espera} pedido(s) em espera")
        else:
            st.success("✅ Sem pedidos pendentes")
            
        if estoque_alerta > 0:
            st.error(f"⚠️ {estoque_alerta} material(is) no fim")
        else:
            st.success("📦 Estoque abastecido")
            
        # 4. Rodapé personalizado
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>Desenvolvido por <b>Ana Carolina</b> 💻</p>", unsafe_allow_html=True)

    # Roteamento das Telas
    if menu == "📦 Pedidos":
        renderizar_pedidos()
    elif menu == "👥 Clientes":
        renderizar_clientes()
    elif menu == "🧶 Estoque":
        renderizar_estoque()
    elif menu == "📝 Patterns":
        renderizar_patterns()
    elif menu == "📊 Analytics / BI":
        renderizar_aba_bi()

if __name__ == "__main__":
    main()