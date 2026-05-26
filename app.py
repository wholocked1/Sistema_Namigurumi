import streamlit as st
from database import DatabaseCSV
from modelos import Cliente, Material, Pattern, Pedido

# Configuração da página para ocupar a tela toda
st.set_page_config(page_title="Namigurumi System", page_icon="🧶", layout="wide")

# Instancia o banco de dados
@st.cache_resource
def carregar_db():
    return DatabaseCSV()

db = carregar_db()

# O Streamlit recarrega o código de cima a baixo, então lemos os CSVs sempre para ter os dados frescos
clientes = db.carregar_clientes()
estoque = db.carregar_materiais()
patterns = db.carregar_patterns()
pedidos = db.carregar_pedidos(clientes, patterns)

st.title("🧶 Sistema de Gestão Namigurumi")

# Criando as 4 abas principais do sistema
aba_clientes, aba_estoque, aba_patterns, aba_pedidos = st.tabs([
    "👥 Clientes", "🧶 Estoque de Materiais", "📝 Patterns (Receitas)", "📦 Pedidos"
])

# ==========================================
# ABA 1: CLIENTES
# ==========================================
with aba_clientes:
    col1, col2 = st.columns([1, 2]) # Divide a tela em duas colunas (uma mais estreita para o form, outra larga pra tabela)
    
    with col1:
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
                    st.rerun() # Atualiza a tela para mostrar o novo dado
                    
    with col2:
        st.subheader("Clientes Cadastrados")
        if not clientes:
            st.info("Nenhum cliente cadastrado.")
        else:
            dados = [{"ID": c.id_cliente, "Nome": c.nome, "Contato": c.contato, "Local": f"{c.cidade}/{c.estado}"} for c in clientes]
            st.dataframe(dados, use_container_width=True)

# ==========================================
# ABA 2: ESTOQUE DE MATERIAIS
# ==========================================
with aba_estoque:
    # --- SISTEMA DE ALERTA DE ESTOQUE COMPACTO ---
    materiais_em_falta = [m for m in estoque.values() if m.quantidade <= 0]
    materiais_acabando = [m for m in estoque.values() if m.quantidade == 1]
    
    if materiais_em_falta or materiais_acabando:
        resumo_alerta = f"⚠️ **Lista de Compras:** {len(materiais_em_falta)} materiais esgotados e {len(materiais_acabando)} acabando. Clique aqui para expandir e ver a lista!"
        
        # Cria uma gaveta retrátil (que começa fechada por padrão)
        with st.expander(resumo_alerta, expanded=False):
            # Agrupa os dados em uma lista para virar uma tabela compacta
            dados_compras = []
            for m in materiais_em_falta:
                dados_compras.append({"Status": "🔴 Esgotado", "SKU": m.sku, "Material": m.nome, "Cor": f"{m.cor} #{m.num_cor}"})
            for m in materiais_acabando:
                dados_compras.append({"Status": "🟡 Acabando", "SKU": m.sku, "Material": m.nome, "Cor": f"{m.cor} #{m.num_cor}"})
                
            # Exibe os dados em uma tabela com barra de rolagem
            st.dataframe(dados_compras, use_container_width=True)
    else:
        st.success("✅ Seu estoque está saudável! Nenhum material esgotado ou acabando.")
        
    st.divider() # Cria uma linha visual para separar
    
    # --- CADASTRO E BUSCA ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
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
                else:
                    novo_m = Material(sku, tipo, nome_mat, cor, num_cor, quantidade, peso if peso>0 else None, preco, rendimento)
                    estoque[sku] = novo_m
                    db.salvar_materiais(estoque)
                    st.success("Material adicionado ao estoque!")
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
# ABA 3: PATTERNS (RECEITAS)
# ==========================================
with aba_patterns:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Criando sub-abas para separar o cadastro da edição
        tab_novo, tab_editar = st.tabs(["➕ Novo Pattern", "✏️ Editar Pattern"])
        
        with tab_novo:
            st.subheader("Cadastrar Pattern")
            nome_pat = st.text_input("Nome do Amigurumi* (Ex: Chopper)")
            obs = st.text_area("Observações (Ex: na carreira 4 não são 21 pontos, são 19)")
            
            st.markdown("📝 **Materiais Necessários**")
            quantidades = {}
            skus_list = []
            
            if not estoque:
                st.warning("Cadastre materiais no Estoque primeiro para selecioná-los.")
            else:
                opcoes_estoque = [f"{m.sku} - {m.nome} (Cor: {m.cor} #{m.num_cor})" for m in estoque.values()]
                materiais_selecionados = st.multiselect("Selecione os materiais no estoque:", opcoes_estoque)
                
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
                # Seleciona qual pattern vamos editar
                nomes_patterns = [p.nome for p in patterns]
                pattern_escolhido_nome = st.selectbox("Escolha a receita que deseja alterar:", nomes_patterns)
                
                # Busca o objeto do pattern selecionado
                pat_alvo = next(p for p in patterns if p.nome == pattern_escolhido_nome)
                
                # A SOLUÇÃO: Adicionamos o nome do pattern no final do 'key' para forçar a atualização!
                edit_nome = st.text_input("Nome", value=pat_alvo.nome, key=f"edit_nome_{pat_alvo.nome}")
                edit_obs = st.text_area("Observações", value=pat_alvo.observacoes, key=f"edit_obs_{pat_alvo.nome}")
                
                edit_quantidades = {}
                edit_skus_list = []
                
                if estoque:
                    opcoes_estoque = [f"{m.sku} - {m.nome} (Cor: {m.cor} #{m.num_cor})" for m in estoque.values()]
                    
                    # Descobre quais materiais já estavam marcados neste pattern
                    defaults_mat = []
                    for sku in pat_alvo.skus_necessarios:
                        match = next((op for op in opcoes_estoque if op.startswith(f"{sku} - ")), None)
                        if match:
                            defaults_mat.append(match)
                            
                    edit_selecionados = st.multiselect(
                        "Materiais no estoque:", 
                        opcoes_estoque, 
                        default=defaults_mat, 
                        key=f"edit_multi_{pat_alvo.nome}" # Chave dinâmica aqui também
                    )
                    
                    if edit_selecionados:
                        st.markdown("**Quantidades:**")
                        for item in edit_selecionados:
                            sku = item.split(" - ")[0]
                            qtd_atual = pat_alvo.quantidades_estimadas.get(sku, 1.0)
                            
                            # Chave dinâmica para as quantidades
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
                        st.success("Pattern atualizado com sucesso!")
                        st.rerun()

    with col2:
        st.subheader("Patterns Cadastrados")
        if not patterns:
            st.info("Nenhum pattern cadastrado.")
        else:
            for p in patterns:
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
# ABA 4: PEDIDOS
# ==========================================
with aba_pedidos:
    st.subheader("Gestão de Pedidos")
    
    # Linha superior: Criação de pedido
    with st.expander("➕ CRIAR NOVO PEDIDO", expanded=False):
        if not clientes or not patterns:
            st.warning("Cadastre ao menos 1 Cliente e 1 Pattern para criar pedidos.")
        else:
            with st.form("form_pedido", clear_on_submit=True):
                # O Streamlit permite formatar o que aparece na caixa de seleção
                cliente_sel = st.selectbox("Selecione o Cliente", clientes, format_func=lambda c: f"{c.nome} (ID: {c.id_cliente})")
                pattern_sel = st.selectbox("Selecione o Pattern", patterns, format_func=lambda p: p.nome)
                
                submit_ped = st.form_submit_button("Gerar Pedido em Espera")
                if submit_ped:
                    novo_p = Pedido(cliente_sel, pattern_sel)
                    pedidos.append(novo_p)
                    db.salvar_pedidos(pedidos)
                    st.success(f"Pedido criado com sucesso! ID: {novo_p.id_pedido}")
                    st.rerun()

    # Linha inferior: Listagem e ações de pedidos
    if not pedidos:
        st.info("Nenhum pedido registrado.")
    else:
        pedidos_espera = [p for p in pedidos if p.status == "Em espera"]
        pedidos_fin = [p for p in pedidos if p.status != "Em espera"]
        
        col_ped1, col_ped2 = st.columns(2)
        
        with col_ped1:
            st.markdown("### ⏳ Em Espera")
            for p in pedidos_espera:
                with st.container(border=True):
                    st.markdown(f"**ID:** {p.id_pedido} | **{p.pattern.nome}**")
                    st.write(f"👤 Cliente: {p.cliente.nome}")
                    st.write(f"📅 Data: {p.data_criacao}")
                    
                    # Formulário rápido para finalizar o pedido
                    with st.form(f"form_fin_{p.id_pedido}"):
                        st.write("Finalizar Pedido (Calcular Fio)")
                        peso_i = st.number_input("Peso Inicial do Fio (g)", min_value=0.0, step=5.0, key=f"pi_{p.id_pedido}")
                        peso_f = st.number_input("Peso Final do Fio (g)", min_value=0.0, step=5.0, key=f"pf_{p.id_pedido}")
                        sku_principal = st.text_input("SKU do Fio Principal usado", key=f"sku_{p.id_pedido}").strip().upper()
                        
                        if st.form_submit_button("Registrar e Finalizar"):
                            p.registrar_pesos(peso_i, peso_f)
                            custo = p.calcular_custo_total_materiais(estoque, sku_principal)
                            db.salvar_pedidos(pedidos)
                            st.success(f"Finalizado! Custo material: R$ {custo:.2f}")
                            st.rerun()

        with col_ped2:
            st.markdown("### ✅ Finalizados")
            for p in pedidos_fin:
                with st.container(border=True):
                    st.markdown(f"**ID:** {p.id_pedido} | **{p.pattern.nome}**")
                    st.write(f"👤 Cliente: {p.cliente.nome}")
                    st.write(f"🧶 Consumo de Fio: {p.calcular_uso_fio()}g")
                    
                    # Atualização rápida de rastreio
                    rastreio_atual = p.codigo_rastreio if p.codigo_rastreio else "Sem rastreio"
                    st.write(f"🚚 Rastreio: **{rastreio_atual}**")
                    
                    with st.popover("Adicionar/Editar Rastreio"):
                        novo_rastreio = st.text_input("Código", value=p.codigo_rastreio if p.codigo_rastreio else "", key=f"rast_{p.id_pedido}")
                        if st.button("Salvar Rastreio", key=f"btn_rast_{p.id_pedido}"):
                            p.atualizar_rastreio(novo_rastreio)
                            db.salvar_pedidos(pedidos)
                            st.rerun()