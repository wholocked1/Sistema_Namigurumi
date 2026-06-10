import streamlit as st
from database import DatabaseCSV
from modelos import Cliente, Pedido

# Configuração da página com uma cara mais "loja"
st.set_page_config(page_title="Namigurumi - Encomendas", page_icon="🧶", layout="centered")

@st.cache_resource
def carregar_db():
    return DatabaseCSV()

db = carregar_db()

# Carrega os dados necessários para a vitrine
clientes_db = db.carregar_clientes()
patterns_db = db.carregar_patterns()
pedidos_db = db.carregar_pedidos(clientes_db, patterns_db)

# Esconde o menu lateral do Streamlit para o cliente não se perder
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Cabeçalho da Loja
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🧶 Bem-vindo(a) à Namigurumi!</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Faça sua encomenda personalizada preenchendo o formulário abaixo.</p>", unsafe_allow_html=True)
st.divider()

if not patterns_db:
    st.info("Nosso catálogo está sendo atualizado. Volte em breve!")
else:
    st.subheader("1. O que você deseja encomendar?")
    
    # Exibe o catálogo como cartões (cards)
    opcoes_catalogo = []
    for p in patterns_db:
        opcoes_catalogo.append(p.nome)
        
    pattern_escolhido = st.selectbox("Selecione o Amigurumi do nosso catálogo:", opcoes_catalogo)
    
    st.divider()
    
    st.subheader("2. Seus Dados")
    with st.form("form_encomenda_cliente", clear_on_submit=True):
        nome_cliente = st.text_input("Seu Nome Completo*")
        contato_cliente = st.text_input("WhatsApp ou Instagram (Para combinarmos os detalhes)*")
        
        st.markdown("*(O valor final e prazo de entrega serão combinados diretamente com você via mensagem após o envio deste formulário!)*")
        
        submit = st.form_submit_button("Enviar Pedido de Encomenda", type="primary", use_container_width=True)
        
        if submit:
            if not nome_cliente or not contato_cliente:
                st.error("Por favor, preencha seu nome e contato para que possamos falar com você!")
            else:
                # 1. Verifica se o cliente já existe, se não, cadastra
                cliente_existente = next((c for c in clientes_db if c.nome.lower() == nome_cliente.lower()), None)
                
                if not cliente_existente:
                    # Cria um novo cliente básico (os outros dados ficam em branco por enquanto)
                    cliente_existente = Cliente(nome=nome_cliente, contato=contato_cliente, endereco="", cidade="", estado="", cep="")
                    clientes_db.append(cliente_existente)
                    db.salvar_clientes(clientes_db)
                
                # 2. Localiza o pattern escolhido
                pattern_obj = next(p for p in patterns_db if p.nome == pattern_escolhido)
                
                # 3. Cria o pedido (preço começa zerado até você aprovar no painel admin)
                novo_pedido = Pedido(cliente=cliente_existente, pattern=pattern_obj, preco_venda=0.0)
                pedidos_db.append(novo_pedido)
                db.salvar_pedidos(pedidos_db)
                
                st.success(f"🎉 Oba! Recebemos o seu pedido para o {pattern_escolhido}. Entraremos em contato em breve pelo {contato_cliente}!")
                st.balloons()