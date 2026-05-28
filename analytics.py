import streamlit as st
import pandas as pd
from database import DatabaseCSV

def renderizar_aba_bi():
    st.title("📊 Business Intelligence & Analytics")
    st.markdown("Acompanhe a saúde financeira e o desempenho operacional da Namigurumi.")

    db = DatabaseCSV()
    
    # 1. CARREGAMENTO E TRATAMENTO DOS DADOS
    # (Ajuste os métodos abaixo conforme os nomes reais do seu arquivo database.py)
    pedidos_dict = db.carregar_pedidos() 
    
    if not pedidos_dict:
        st.info("Ainda não há pedidos cadastrados para gerar análises estatísticas.")
        return

    # Convertendo o dicionário de objetos para uma lista de dicionários puros para o Pandas
    dados_pedidos = []
    for p in pedidos_dict.values():
        dados_pedidos.append({
            "id": p.id,
            "cliente": p.cliente_nome,      # Nome ou ID do cliente
            "pattern": p.pattern_nome,      # Nome da receita (Snoopy, Fox, etc.)
            "valor_venda": float(p.valor_venda),
            "lucro_liquido": float(p.lucro_liquido),
            "data": pd.to_datetime(p.data_pedido) # Certifique-se de ter um campo de data
        })

    # Criação do DataFrame principal
    df_pedidos = pd.DataFrame(dados_pedidos)

    # 2. BLOCO FINANCEIRO: FATURAMENTO E LUCRO TOTAL
    st.subheader("💰 Panorama Financeiro Geral")
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

    # 3. EVOLUÇÃO MENSAL (Faturamento e Lucro)
    st.subheader("📅 Desempenho Mensal")
    # Agrupa por Ano-Mês para criar a linha do tempo
    df_pedidos['Ano_Mes'] = df_pedidos['data'].dt.to_period('M').astype(str)
    df_mensal = df_pedidos.groupby('Ano_Mes')[['valor_venda', 'lucro_liquido']].sum()
    
    # Renomeia as colunas para o gráfico ficar com nomes amigáveis
    df_mensal.columns = ['Faturamento', 'Lucro Líquido']
    st.line_chart(df_mensal)

    st.markdown("---")

    # 4. RANKINGS: TOP CLIENTES E TOP PATTERNS (Lado a Lado)
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("👥 Top 5 Clientes (Por Valor Total)")
        # Agrupa por cliente, soma o valor gasto e pega os 5 maiores
        top_clientes = df_pedidos.groupby("cliente")["valor_venda"].sum().sort_values(ascending=True).tail(5)
        st.bar_chart(top_clientes, horizontal=True)

    with col_dir:
        st.subheader("🧶 Top 5 Patterns Mais Vendidos")
        # Conta a quantidade de vezes que cada receita aparece nos pedidos
        top_patterns = df_pedidos.groupby("pattern")["id"].count().sort_values(ascending=True).tail(5)
        top_patterns.name = "Quantidade"
        st.bar_chart(top_patterns, horizontal=True)

    st.markdown("---")

    # 5. MAPA DE CONSUMO DE ESTOQUE
    st.subheader("🎨 Mapa de Consumo de Fios (Estoque Atual)")
    materiais_dict = db.carregar_materiais()
    
    if materiais_dict:
        dados_materiais = []
        for m in materiais_dict.values():
            dados_materiais.append({
                "Nome": f"{m.nome} ({m.cor})",
                "Quantidade Disponível": m.quantidade
            })
        
        df_materiais = pd.DataFrame(dados_materiais).set_index("Nome")
        # Exibe um gráfico de barras verticais mostrando os níveis de estoque por cor
        st.bar_chart(df_materiais["Quantidade Disponível"])