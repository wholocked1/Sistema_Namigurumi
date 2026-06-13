import streamlit as st
import pandas as pd
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage
from database import DatabaseCSV
from modelos import Cliente, Material, Pattern, Pedido

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E BANCO DE DADOS
# ==========================================
st.set_page_config(
    page_title="Namigurumi", 
    page_icon="🧶", 
    layout="wide"
)

# Carrega as senhas do arquivo .env
load_dotenv()

@st.cache_resource
def carregar_db():
    return DatabaseCSV()

db = carregar_db()
clientes = db.carregar_clientes()
estoque = db.carregar_materiais()
patterns = db.carregar_patterns()
pedidos = db.carregar_pedidos(clientes, patterns)

# ==========================================
# FUNÇÃO: ENVIAR RELATÓRIO DE ESTOQUE
# ==========================================
def enviar_relatorio_estoque():
    EMAIL_ORIGEM = os.getenv("EMAIL_BOT")
    SENHA_APP = os.getenv("SENHA_BOT")
    EMAIL_DESTINO = os.getenv("EMAIL_BOT") 
    
    if not EMAIL_ORIGEM or not SENHA_APP:
        return False, "Credenciais não configuradas no arquivo .env!"
        
    materiais_em_falta = [m for m in estoque.values() if m.quantidade <= 0]
    materiais_acabando = [m for m in estoque.values() if m.quantidade == 1]
    
    if not materiais_em_falta and not materiais_acabando:
        return False, "Seu estoque está 100% abastecido, não há nada para comprar!"
        
    corpo = "⚠️ RELATÓRIO DE COMPRAS - NAMIGURUMI ⚠️\n\n"
    if materiais_em_falta:
        corpo += "🔴 ESGOTADOS:\n"
        for m in materiais_em_falta:
            corpo += f"- {m.sku}: {m.nome} ({m.cor})\n"
            
    if materiais_acabando:
        corpo += "\n🟡 ACABANDO (Apenas 1 unidade):\n"
        for m in materiais_acabando:
            corpo += f"- {m.sku}: {m.nome} ({m.cor})\n"
            
    msg = EmailMessage()
    msg.set_content(corpo)
    msg['Subject'] = "📦 Namigurumi: Sua Lista de Compras do Estoque"
    msg['From'] = EMAIL_ORIGEM
    msg['To'] = EMAIL_DESTINO
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ORIGEM, SENHA_APP)
        server.send_message(msg)
        server.quit()
        return True, "E-mail enviado com sucesso!"
    except Exception as e:
        return False, f"Erro ao enviar: {e}"

# ==========================================
# FUNÇÃO: ENVIAR E-MAIL (NOTIFICAÇÃO)
# ==========================================
def avisar_ana_por_email(nome_cliente, resumo_pedido, contato_cliente):
    EMAIL_ORIGEM = os.getenv("EMAIL_BOT")
    SENHA_APP = os.getenv("SENHA_BOT")
    EMAIL_DESTINO = os.getenv("EMAIL_BOT") 
    
    if not EMAIL_ORIGEM or not SENHA_APP:
        print("Erro: Credenciais de e-mail não encontradas no arquivo .env!")
        return False
    
    msg = EmailMessage()
    
    # Colocamos o resumo gigante dentro do corpo do texto, onde as quebras de linha são permitidas
    corpo_email = f"""🧶 Novo Pedido Recebido na Plataforma!

👤 Cliente: {nome_cliente}
📞 Contato: {contato_cliente}

📦 RESUMO DA ENCOMENDA:
{resumo_pedido}

Entre em contato pelo WhatsApp/Insta para negociar o valor e o prazo!"""

    msg.set_content(corpo_email)
    
    # O assunto fica limpo e em uma linha só
    msg['Subject'] = f"NOVO PEDIDO de {nome_cliente}!"
    msg['From'] = EMAIL_ORIGEM
    msg['To'] = EMAIL_DESTINO
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ORIGEM, SENHA_APP)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

# ==========================================
# FUNÇÃO: NOTIFICAR CLIENTE (PRODUTO PRONTO)
# ==========================================
def notificar_cliente_finalizado(email_cliente, nome_cliente, pattern_nome, codigo_rastreio=None):
    EMAIL_ORIGEM = os.getenv("EMAIL_BOT")
    SENHA_APP = os.getenv("SENHA_BOT")
    
    # Se o cliente não tiver e-mail cadastrado (clientes antigos ou em branco), ignora silenciosamente
    if not email_cliente:
        return False
        
    if not EMAIL_ORIGEM or not SENHA_APP:
        print("Erro: Credenciais de e-mail não encontradas no arquivo .env!")
        return False
        
    msg = EmailMessage()
    
    # Monta uma mensagem super carinhosa para o seu cliente
    corpo_email = f"""Olá, {nome_cliente}! ✨

Temos ótimas notícias! O seu amigurumi feito sob encomenda, **{pattern_nome}**, foi finalizado com muito carinho e já está prontinho! 🌸
"""

    if codigo_rastreio:
        corpo_email += f"\n🚚 Seu código de rastreio para acompanhar a entrega é: {codigo_rastreio}\n"
    else:
        corpo_email += "\nEm breve entraremos em contato para combinar os detalhes do envio ou da retirada! 📦\n"

    corpo_email += "\nMuito obrigado por apoiar o Namigurumi! 💕"

    msg.set_content(corpo_email)
    msg['Subject'] = f"🧶 Seu Namigurumi está pronto! ({pattern_nome})"
    msg['From'] = EMAIL_ORIGEM
    msg['To'] = email_cliente
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_ORIGEM, SENHA_APP)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao notificar cliente por email: {e}")
        return False

# ==========================================
# FUNÇÃO: DETALHE DO PRODUTO (TELA DE PRODUTO)
# ==========================================
def renderizar_tela_produto():
    p = st.session_state.produto_selecionado
    
    if st.button("⬅️ Voltar para o Catálogo"):
        st.session_state.produto_selecionado = None
        st.rerun()
        
    st.divider()
    
    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        # 👇 USO DO GETATTR PARA EVITAR O ERRO
        img_val = getattr(p, 'imagem', '')
        link_imagem = img_val if img_val else "https://placehold.co/600x600?text=Sem+Foto"
        
        try:
            st.image(link_imagem, use_container_width=True)
        except Exception:
            st.image("https://placehold.co/600x600?text=Erro+ao+Carregar+Imagem", use_container_width=True)
            
    with col_info:
        st.markdown(f"# 🧶 {p.nome}")
        st.markdown("### ✨ Detalhes do Produto")
        st.write(getattr(p, 'observacoes', "Peça artesanal produzida manualmente com fios de alta qualidade e acabamento impecável."))
        
        st.divider()
        st.markdown("##### 📦 Condições de Encomenda:")
        st.caption("• O valor final e o prazo de entrega serão combinados diretamente via WhatsApp.")
        st.caption("• Produção totalmente personalizada conforme sua preferência de cores.")
        st.divider()
        
        if st.session_state.perfil != 'cliente':
            st.button("Faça login para fazer sua encomenda", disabled=True, use_container_width=True)
        else:
            qtd = st.number_input("Quantidade desejada:", min_value=1, step=1, value=1, key=f"qtd_detalhe_{p.nome}")
            
            if st.button("🛍️ Adicionar ao Carrinho", type="primary", use_container_width=True):
                st.session_state.carrinho_cliente.append({
                    'pattern': p,
                    'quantidade': qtd
                })
                st.success(f"🎉 {qtd}x {p.nome} adicionado(s) ao carrinho!")
                st.session_state.produto_selecionado = None
                st.rerun()


# ==========================================
# FUNÇÃO: CATÁLOGO GERAL DE PRODUTOS
# ==========================================
def renderizar_catalogo():
    if "carrinho_cliente" not in st.session_state:
        st.session_state.carrinho_cliente = []
    if "produto_selecionado" not in st.session_state:
        st.session_state.produto_selecionado = None

    if st.session_state.produto_selecionado is not None:
        renderizar_tela_produto()
        return

    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🧶 Bem-vindo(a) à Namigurumi!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Explore nosso catálogo e encomende peças exclusivas.</p>", unsafe_allow_html=True)
    st.divider()

    if "compra_finalizada" in st.session_state and st.session_state.compra_finalizada:
        cliente_logado = st.session_state.usuario_logado
        st.success(f"🎉 Pedido recebido! Em breve a Ana entrará em contato pelo WhatsApp {cliente_logado.contato}.")
        st.balloons()
        st.session_state.compra_finalizada = False

    if st.session_state.perfil == 'cliente' and st.session_state.carrinho_cliente:
        with st.expander("🛒 SEU CARRINHO DE ENCOMENDAS", expanded=True):
            st.subheader("Itens Selecionados")
            for i, item in enumerate(st.session_state.carrinho_cliente):
                col_it1, col_it2, col_it3 = st.columns([3, 1, 1])
                col_it1.markdown(f"🧶 **{item['pattern'].nome}**")
                col_it2.write(f"Qtd: **{item['quantidade']}**")
                if col_it3.button("Remover", key=f"rem_cli_{i}"):
                    st.session_state.carrinho_cliente.pop(i)
                    st.rerun()
            
            st.divider()
            if st.button("✅ Enviar Encomenda Completa", type="primary", use_container_width=True):
                cliente_logado = st.session_state.usuario_logado
                itens_resumo = []
                
                for item in st.session_state.carrinho_cliente:
                    qtd = item['quantidade']
                    for _ in range(qtd):
                        novo_pedido = Pedido(cliente=cliente_logado, pattern=item['pattern'], preco_venda=0.0)
                        pedidos.append(novo_pedido)
                    
                    detalhe = getattr(item['pattern'], 'descricao_completa', '')
                    if detalhe:
                        itens_resumo.append(f"{qtd}x {item['pattern'].nome}\n   -> Detalhes: {detalhe}")
                    else:
                        itens_resumo.append(f"{qtd}x {item['pattern'].nome}")
                    
                db.salvar_pedidos(pedidos)
                resumo_str = "\n\n".join(itens_resumo)
                avisar_ana_por_email(cliente_logado.nome, resumo_str, cliente_logado.contato)
                
                st.session_state.carrinho_cliente = []
                st.session_state.compra_finalizada = True
                st.rerun()

    st.subheader("Catálogo Disponível")
    if not patterns:
        st.info("Nosso catálogo está sendo atualizado. Volte em breve!")
        return

    cols = st.columns(3)
    for i, p in enumerate(patterns):
        with cols[i % 3]:
            with st.container(border=True):
                # 👇 USO DO GETATTR PARA EVITAR O ERRO
                img_val = getattr(p, 'imagem', '')
                link_mini = img_val if img_val else "https://placehold.co/400x300?text=Sem+Foto"
                
                try:
                    st.image(link_mini, use_container_width=True)
                except Exception:
                    st.image("https://placehold.co/400x300?text=Erro+Imagem", use_container_width=True)
                
                st.markdown(f"### {p.nome}")
                
                obs_val = getattr(p, 'observacoes', '')
                resumo_obs = obs_val if len(obs_val) <= 60 else obs_val[:60] + "..."
                st.write(resumo_obs if resumo_obs else "Amigurumi feito sob encomenda.")
                
                if st.button("🔍 Ver Detalhes", key=f"btn_detalhe_{i}", use_container_width=True, type="secondary"):
                    st.session_state.produto_selecionado = p
                    st.rerun()

    if st.session_state.perfil == 'cliente':
        st.divider()
        st.markdown("### ✨ Não encontrou o que procurava?")
        with st.container(border=True):
            st.write("**Quer uma peça que não foi listada no catálogo?**")
            st.write("Descreva o que você quer para que seja analisada a viabilidade de realizar a sua peça exclusiva.")
            desc_personalizada = st.text_area("Descreva detalhes como personagem, tamanho, cores, referências, etc.")
            
            if st.button("➕ Adicionar Pedido Personalizado ao Carrinho"):
                if not desc_personalizada.strip():
                    st.error("Por favor, descreva a peça que deseja antes de adicionar!")
                else:
                    resumo = desc_personalizada[:30] + "..." if len(desc_personalizada) > 30 else desc_personalizada
                    # Passando a imagem genérica para a peça personalizada
                    pat_temp = Pattern(nome=f"✨ Personalizado: {resumo}", skus_necessarios=[], imagem="https://placehold.co/600x600?text=%E2%9C%A8+Personalizado")
                    pat_temp.descricao_completa = desc_personalizada 
                    
                    st.session_state.carrinho_cliente.append({
                        'pattern': pat_temp,
                        'quantidade': 1
                    })
                    st.success("Peça personalizada adicionada ao seu carrinho! Suba a página para finalizar.")
                    st.rerun()

# ==========================================
# FUNÇÃO: CATÁLOGO GERAL DE PRODUTOS
# ==========================================
def renderizar_catalogo():
    if "carrinho_cliente" not in st.session_state:
        st.session_state.carrinho_cliente = []
    if "produto_selecionado" not in st.session_state:
        st.session_state.produto_selecionado = None

    if st.session_state.produto_selecionado is not None:
        renderizar_tela_produto()
        return

    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🧶 Bem-vindo(a) à Namigurumi!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Explore nosso catálogo e encomende peças exclusivas.</p>", unsafe_allow_html=True)
    st.divider()

    if "compra_finalizada" in st.session_state and st.session_state.compra_finalizada:
        cliente_logado = st.session_state.usuario_logado
        st.success(f"🎉 Pedido recebido! Em breve a Ana entrará em contato pelo WhatsApp {cliente_logado.contato}.")
        st.balloons()
        st.session_state.compra_finalizada = False

    if st.session_state.perfil == 'cliente' and st.session_state.carrinho_cliente:
        with st.expander("🛒 SEU CARRINHO DE ENCOMENDAS", expanded=True):
            st.subheader("Itens Selecionados")
            for i, item in enumerate(st.session_state.carrinho_cliente):
                col_it1, col_it2, col_it3 = st.columns([3, 1, 1])
                col_it1.markdown(f"🧶 **{item['pattern'].nome}**")
                col_it2.write(f"Qtd: **{item['quantidade']}**")
                if col_it3.button("Remover", key=f"rem_cli_{i}"):
                    st.session_state.carrinho_cliente.pop(i)
                    st.rerun()
            
            st.divider()
            if st.button("✅ Enviar Encomenda Completa", type="primary", use_container_width=True):
                cliente_logado = st.session_state.usuario_logado
                itens_resumo = []
                
                for item in st.session_state.carrinho_cliente:
                    qtd = item['quantidade']
                    for _ in range(qtd):
                        novo_pedido = Pedido(cliente=cliente_logado, pattern=item['pattern'], preco_venda=0.0)
                        pedidos.append(novo_pedido)
                    
                    detalhe = getattr(item['pattern'], 'descricao_completa', '')
                    if detalhe:
                        itens_resumo.append(f"{qtd}x {item['pattern'].nome}\n   -> Detalhes: {detalhe}")
                    else:
                        itens_resumo.append(f"{qtd}x {item['pattern'].nome}")
                    
                db.salvar_pedidos(pedidos)
                resumo_str = "\n\n".join(itens_resumo)
                avisar_ana_por_email(cliente_logado.nome, resumo_str, cliente_logado.contato)
                
                st.session_state.carrinho_cliente = []
                st.session_state.compra_finalizada = True
                st.rerun()

    st.subheader("Catálogo Disponível")
    if not patterns:
        st.info("Nosso catálogo está sendo atualizado. Volte em breve!")
        return

    cols = st.columns(3)
    for i, p in enumerate(patterns):
        with cols[i % 3]:
            with st.container(border=True):
                # 👇 AQUI ESTÁ A CORREÇÃO BLINDADA COM GETATTR
                img_val = getattr(p, 'imagem', '')
                link_mini = img_val if img_val else "https://placehold.co/400x300?text=Sem+Foto"
                
                try:
                    st.image(link_mini, use_container_width=True)
                except Exception:
                    st.image("https://placehold.co/400x300?text=Erro+Imagem", use_container_width=True)
                
                st.markdown(f"### {p.nome}")
                
                obs_val = getattr(p, 'observacoes', '')
                resumo_obs = obs_val if len(obs_val) <= 60 else obs_val[:60] + "..."
                st.write(resumo_obs if resumo_obs else "Amigurumi feito sob encomenda.")
                
                if st.button("🔍 Ver Detalhes", key=f"btn_detalhe_{i}", use_container_width=True, type="secondary"):
                    st.session_state.produto_selecionado = p
                    st.rerun()

    if st.session_state.perfil == 'cliente':
        st.divider()
        st.markdown("### ✨ Não encontrou o que procurava?")
        with st.container(border=True):
            st.write("**Quer uma peça que não foi listada no catálogo?**")
            st.write("Descreva o que você quer para que seja analisada a viabilidade de realizar a sua peça exclusiva.")
            desc_personalizada = st.text_area("Descreva detalhes como personagem, tamanho, cores, referências, etc.")
            
            if st.button("➕ Adicionar Pedido Personalizado ao Carrinho"):
                if not desc_personalizada.strip():
                    st.error("Por favor, descreva a peça que deseja antes de adicionar!")
                else:
                    resumo = desc_personalizada[:30] + "..." if len(desc_personalizada) > 30 else desc_personalizada
                    pat_temp = Pattern(nome=f"✨ Personalizado: {resumo}", skus_necessarios=[], imagem="https://placehold.co/600x600?text=%E2%9C%A8+Personalizado")
                    pat_temp.descricao_completa = desc_personalizada 
                    
                    st.session_state.carrinho_cliente.append({
                        'pattern': pat_temp,
                        'quantidade': 1
                    })
                    st.success("Peça personalizada adicionada ao seu carrinho! Suba a página para finalizar.")
                    st.rerun()
                    
# ==========================================
# FUNÇÃO: MEUS PEDIDOS (CLIENTE)
# ==========================================
def renderizar_meus_pedidos():
    st.title("📦 Meus Pedidos")
    cliente_atual = st.session_state.usuario_logado
    
    meus_pedidos = [p for p in pedidos if getattr(p.cliente, 'email', None) == getattr(cliente_atual, 'email', None)]
    
    if not meus_pedidos:
        st.info("Você ainda não tem nenhuma encomenda com a gente. Que tal dar uma olhada no catálogo?")
    else:
        for p in meus_pedidos:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{p.pattern.nome}**")
                    if p.preco_venda == 0.0:
                        st.write("💵 Preço: *Em negociação com o ateliê*")
                    else:
                        st.write(f"💵 Preço Combinado: **R$ {p.preco_venda:.2f}**")
                    
                    rastreio = getattr(p, 'codigo_rastreio', None)
                    if rastreio:
                        st.write(f"🚚 Rastreio: **{rastreio}**")
                        
                with col2:
                    if p.status == "Em espera":
                        st.warning("⏳ Em Produção")
                        # Botão de cancelar para o cliente
                        with st.popover("❌ Cancelar Pedido"):
                            st.write("Deseja realmente desistir desta encomenda?")
                            if st.button("Sim, cancelar", key=f"canc_cli_{p.id_pedido}"):
                                pedidos.remove(p)
                                db.salvar_pedidos(pedidos)
                                st.success("Pedido cancelado com sucesso.")
                                st.rerun()
                    else:
                        st.success("✅ Finalizado")


# ==========================================
# TELAS DA ADMINISTRADORA (BACK-OFFICE)
# ==========================================
def renderizar_aba_bi():
    st.title("📊 Business Intelligence & Analytics")
    st.markdown("Acompanhe a saúde financeira e o desempenho operacional.")

    if not pedidos:
        st.info("Ainda não há pedidos finalizados para gerar análises estatísticas.")
        return

    pedidos_fin = [p for p in pedidos if p.status == "Finalizado"]
    
    if not pedidos_fin:
        st.warning("Nenhum pedido foi finalizado ainda. Finalize um pedido para ver as métricas de lucro.")
        return

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

    st.subheader("💰 Panorama Financeiro (Pedidos Finalizados)")
    faturamento_total = df_pedidos["valor_venda"].sum()
    lucro_total = df_pedidos["lucro_liquido"].sum()
    margem_media = (lucro_total / faturamento_total) * 100 if faturamento_total > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Faturamento Total", value=f"R$ {faturamento_total:,.2f}")
    col2.metric(label="Lucro Líquido Total", value=f"R$ {lucro_total:,.2f}")
    col3.metric(label="Margem de Lucro Média", value=f"{margem_media:.1f}%")

    st.markdown("---")

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
                email = st.text_input("E-mail (Para Login)")
                senha = st.text_input("Senha (Para Login)", type="password")
                
                submit_cliente = st.form_submit_button("Salvar Cliente")
                
                if submit_cliente:
                    if not nome:
                        st.error("O campo Nome é obrigatório!")
                    else:
                        novo_c = Cliente(nome, contato, endereco, cidade, estado, cep, email=email, senha=senha)
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
                    edit_email = st.text_input("E-mail", value=getattr(c_alvo, 'email', ''), key=f"edit_email_cli_{c_alvo.id_cliente}")
                    edit_senha = st.text_input("Senha", value=getattr(c_alvo, 'senha', ''), type="password", key=f"edit_senha_cli_{c_alvo.id_cliente}")
                    
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
                            c_alvo.email = edit_email
                            c_alvo.senha = edit_senha
                            
                            db.salvar_clientes(clientes)
                            st.success(f"Cliente '{c_alvo.nome}' atualizado com sucesso!")
                            st.rerun()

    with col2:
        st.subheader("Clientes Cadastrados")
        if not clientes:
            st.info("Nenhum cliente cadastrado.")
        else:
            dados = [{"ID": c.id_cliente, "Nome": c.nome, "Contato": c.contato, "E-mail": getattr(c, 'email', '')} for c in clientes]
            st.dataframe(dados, use_container_width=True)


# ==========================================
# FUNÇÃO: ABA DE ESTOQUE (COM BOTÃO DE E-MAIL)
# ==========================================
def renderizar_estoque():
    st.title("🧶 Estoque de Materiais")
    materiais_em_falta = [m for m in estoque.values() if m.quantidade <= 0 or (m.peso_gramas is not None and m.peso_gramas <= 0)]
    materiais_acabando = [m for m in estoque.values() if m.quantidade == 1 or (m.peso_gramas is not None and 0 < m.peso_gramas <= 15)]
    
    if materiais_em_falta or materiais_acabando:
        resumo_alerta = f"⚠️ **Lista de Compras:** {len(materiais_em_falta)} materiais esgotados e {len(materiais_acabando)} acabando. Clique aqui para expandir!"
        with st.expander(resumo_alerta, expanded=False):
            dados_compras = []
            for m in materiais_em_falta:
                dados_compras.append({"Status": "🔴 Esgotado", "SKU": m.sku, "Material": m.nome, "Cor": f"{m.cor} #{m.num_cor}"})
            for m in materiais_acabando:
                dados_compras.append({"Status": "🟡 Acabando", "SKU": m.sku, "Material": m.nome, "Cor": f"{m.cor} #{m.num_cor}"})
            st.dataframe(dados_compras, use_container_width=True)
            
            # 👇 NOVO BOTÃO: Envia o relatório gerado diretamente para o seu e-mail do .env
            if st.button("📧 Enviar Lista de Compras para o meu E-mail", type="primary", use_container_width=True):
                sucesso, mensagem = enviar_relatorio_estoque()
                if sucesso:
                    st.success(mensagem)
                else:
                    st.error(mensagem)
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
                
                if st.form_submit_button("Salvar Material"):
                    if not sku:
                        st.error("O SKU é obrigatório!")
                    elif sku in estoque:
                        st.error("Esse SKU já existe! Use a aba 'Editar Material' para atualizá-lo.")
                    else:
                        novo_m = Material(sku, tipo, nome_mat, cor, num_cor, quantidade, peso if peso > 0 else None, preco, rendimento)
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
                # Exibe a tabela atualizada mostrando as quantidades e os pesos atuais em tempo real
                dados_est = [
                    {
                        "SKU": m.sku, 
                        "Tipo": m.tipo, 
                        "Nome": m.nome, 
                        "Cor": f"{m.cor} #{m.num_cor}", 
                        "Qtd (Unid)": m.quantidade,
                        "Peso Atual (g)": f"{m.peso_gramas:.1f}g" if m.peso_gramas is not None else "-",
                        "Custo Unit": f"R$ {m.obter_custo_unitario():.2f}"
                    } for m in materiais_filtrados
                ]
                st.dataframe(dados_est, use_container_width=True)


# ==========================================
# FUNÇÃO: GERENCIAR PATTERNS (ADMIN)
# ==========================================
def renderizar_patterns():
    st.title("📝 Patterns (Receitas)")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        tab_novo, tab_editar = st.tabs(["➕ Novo Pattern", "✏️ Editar Pattern"])
        
        with tab_novo:
            st.subheader("Cadastrar Pattern")
            nome_pat = st.text_input("Nome do Amigurumi* (Ex: Chopper)")
            obs = st.text_area("Observações", placeholder="Ex: Atenção - na carreira 4 não são 21 pontos, são 19.")
            
            st.markdown("📸 **Imagem do Produto**")
            imagem_upload = st.file_uploader("Upload da Imagem (Do seu computador)", type=["png", "jpg", "jpeg"], key="upload_novo")
            imagem_link = st.text_input("OU Link da Imagem (URL da internet)", placeholder="https://exemplo.com/foto.jpg")
            
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
                    # Lógica para salvar a imagem
                    caminho_final = ""
                    if imagem_upload is not None:
                        # Cria a pasta 'imagens' se ela não existir
                        if not os.path.exists("imagens"):
                            os.makedirs("imagens")
                        
                        # Salva o arquivo fisicamente na pasta
                        caminho_final = f"imagens/{imagem_upload.name}"
                        with open(caminho_final, "wb") as f:
                            f.write(imagem_upload.getbuffer())
                    elif imagem_link:
                        caminho_final = imagem_link

                    novo_pattern = Pattern(nome_pat, skus_list, quantidades, obs, imagem=caminho_final)
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
                edit_obs = st.text_area("Observações", value=getattr(pat_alvo, 'observacoes', ''), key=f"edit_obs_{pat_alvo.nome}")
                
                st.markdown("📸 **Imagem do Produto**")
                imagem_atual = getattr(pat_alvo, 'imagem', '')
                if imagem_atual:
                    st.caption(f"Imagem atual salva: {imagem_atual}")
                
                edit_upload = st.file_uploader("Substituir Imagem (Upload)", type=["png", "jpg", "jpeg"], key=f"edit_up_{pat_alvo.nome}")
                edit_link = st.text_input("OU Substituir por Link", value=imagem_atual if "http" in imagem_atual else "", key=f"edit_link_{pat_alvo.nome}")
                
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
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Salvar Alterações", type="primary", key=f"btn_salvar_{pat_alvo.nome}"):
                        if not edit_nome:
                            st.error("O nome não pode ficar em branco!")
                        else:
                            # Lógica para atualizar a imagem
                            caminho_editado = imagem_atual
                            if edit_upload is not None:
                                if not os.path.exists("imagens"):
                                    os.makedirs("imagens")
                                caminho_editado = f"imagens/{edit_upload.name}"
                                with open(caminho_editado, "wb") as f:
                                    f.write(edit_upload.getbuffer())
                            elif edit_link:
                                caminho_editado = edit_link

                            pat_alvo.nome = edit_nome
                            pat_alvo.observacoes = edit_obs
                            pat_alvo.imagem = caminho_editado
                            pat_alvo.skus_necessarios = edit_skus_list
                            pat_alvo.quantidades_estimadas = edit_quantidades
                            
                            db.salvar_patterns(patterns)
                            db.salvar_pedidos(pedidos)
                            st.success("Pattern atualizado!")
                            st.rerun()
                            
                with col_btn2:
                    with st.popover("🗑️ Eliminar Pattern"):
                        st.error("Aviso: Esta ação não pode ser desfeita!")
                        st.write(f"Deseja mesmo eliminar permanentemente a receita '{pat_alvo.nome}'?")
                        if st.button("Sim, confirmar exclusão", key=f"btn_del_{pat_alvo.nome}"):
                            patterns.remove(pat_alvo)
                            db.salvar_patterns(patterns)
                            st.success("Pattern removido com sucesso!")
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
                        st.write(f"**Observações:** {getattr(p, 'observacoes', '')}")
                        img_link = getattr(p, 'imagem', '')
                        if img_link:
                            # Mostra a miniatura da imagem no próprio painel da Admin
                            try:
                                st.image(img_link, width=150)
                            except Exception:
                                st.write("Imagem salva (Não foi possível exibir a prévia)")
                            
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
# FUNÇÃO: GESTÃO DE PEDIDOS (ADMIN)
# ==========================================
def renderizar_pedidos_admin():
    st.title("📦 Gestão de Pedidos")
    
    if "carrinho_atual" not in st.session_state:
        st.session_state.carrinho_atual = []

    with st.expander("➕ CRIAR NOVA ENCOMENDA MÚLTIPLA", expanded=False):
        if not clientes or not patterns:
            st.warning("Cadastre ao menos 1 Cliente e 1 Pattern para criar pedidos.")
        else:
            cliente_sel = st.selectbox("👤 Cliente Responsável", clientes, format_func=lambda c: f"{c.nome} (ID: {c.id_cliente})")
            
            st.markdown("### 🛒 Carrinho de Itens")
            
            if st.session_state.carrinho_atual:
                for i, item in enumerate(st.session_state.carrinho_atual):
                    col_it1, col_it2, col_it3 = st.columns([3, 1, 1])
                    col_it1.write(f"🧶 **{item['pattern'].nome}**")
                    col_it2.write(f"R$ {item['preco']:.2f}")
                    if col_it3.button("Remover", key=f"rem_{i}"):
                        st.session_state.carrinho_atual.pop(i)
                        st.rerun()
                
                total = sum(item['preco'] for item in st.session_state.carrinho_atual)
                st.markdown(f"#### 💰 Total da Encomenda: R$ {total:.2f}")
                st.divider()
                
            st.write("**Adicionar novo item à encomenda:**")
            col_add1, col_add2, col_add3 = st.columns([2, 1, 1])
            with col_add1:
                pattern_sel = st.selectbox("Selecione o Pattern", patterns, format_func=lambda p: p.nome, key="add_pat")
            with col_add2:
                preco_venda = st.number_input("Preço (R$)", min_value=0.0, step=5.0, key="add_preco")
            with col_add3:
                st.write("") 
                if st.button("➕ Adicionar", use_container_width=True):
                    st.session_state.carrinho_atual.append({
                        "pattern": pattern_sel,
                        "preco": preco_venda
                    })
                    st.rerun()

            st.markdown("---")
            if st.session_state.carrinho_atual:
                if st.button("✅ Finalizar Encomenda Completa", type="primary", use_container_width=True):
                    for item in st.session_state.carrinho_atual:
                        novo_p = Pedido(cliente_sel, item['pattern'], item['preco'])
                        pedidos.append(novo_p)
                        
                    db.salvar_pedidos(pedidos)
                    st.session_state.carrinho_atual = [] 
                    st.success("Encomenda múltipla criada com sucesso!")
                    st.rerun()

    if not pedidos:
        st.info("Nenhum pedido registrado.")
    else:
        st.markdown("### 🔍 Filtros de Busca")
        col_filtro1, col_filtro2 = st.columns([2, 1])
        
        with col_filtro1:
            termo_busca_ped = st.text_input("Buscar por nome do Cliente ou Pattern:", "").strip().lower()
        with col_filtro2:
            filtro_status = st.selectbox("Filtrar por Status:", ["Todos", "Em espera", "Finalizado"])
            
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
                        
                        if p.preco_venda == 0.0:
                            st.warning("⚠️ Este pedido veio da Vitrine do Cliente. Defina o preço final:")
                            novo_preco = st.number_input("Preço Combinado (R$)", min_value=0.0, step=5.0, key=f"preco_vitrine_{p.id_pedido}")
                            if st.button("Salvar Preço", key=f"btn_salvar_preco_{p.id_pedido}"):
                                p.preco_venda = novo_preco
                                db.salvar_pedidos(pedidos)
                                st.rerun()
                        else:
                            st.write(f"💵 Preço Combinado: **R$ {p.preco_venda:.2f}**")
                        
                        fios_do_pattern = [sku for sku in p.pattern.skus_necessarios if sku in estoque and estoque[sku].tipo.lower() == "fio"]
                        
                        if not fios_do_pattern:
                            st.warning("Nenhum 'Fio' foi encontrado na receita para pesagem.")
                            
                            c_btn1, c_btn2 = st.columns(2)
                            with c_btn1:
                                if st.button("Finalizar Pedido", key=f"btn_fin_{p.id_pedido}"):
                                    p.status = "Finalizado"
                                    db.salvar_pedidos(pedidos)
                                    
                                    # NOTIFICAÇÃO: Pedido sem fios finalizado
                                    email_cli = getattr(p.cliente, 'email', '')
                                    notificar_cliente_finalizado(email_cli, p.cliente.nome, p.pattern.nome, p.codigo_rastreio)
                                    
                                    st.rerun()
                            with c_btn2:
                                with st.popover("❌ Cancelar"):
                                    st.write("Excluir este pedido permanentemente?")
                                    if st.button("Sim, apagar", key=f"canc_adm1_{p.id_pedido}"):
                                        pedidos.remove(p)
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
                                        ini = pesos_temp_ini[sku]
                                        fin = pesos_temp_fin[sku]
                                        
                                        # 1. Registra os pesos no pedido
                                        p.registrar_peso_fio(sku, ini, fin)
                                        
                                        # 2. Dá baixa no Estoque automaticamente!
                                        peso_gasto = max(0.0, ini - fin)
                                        if sku in estoque and estoque[sku].peso_gramas is not None:
                                            estoque[sku].peso_gramas -= peso_gasto
                                            if estoque[sku].peso_gramas < 0:
                                                estoque[sku].peso_gramas = 0.0
                                    
                                    # Salva ambos os bancos de dados
                                    db.salvar_materiais(estoque)
                                    db.salvar_pedidos(pedidos)
                                    
                                    # NOTIFICAÇÃO: Pedido com pesagem finalizado
                                    email_cli = getattr(p.cliente, 'email', '')
                                    notificar_cliente_finalizado(email_cli, p.cliente.nome, p.pattern.nome, p.codigo_rastreio)
                                    
                                    st.success("Pedido finalizado e estoque atualizado com sucesso!")
                                    st.rerun()
                            
                            with st.popover("❌ Cancelar Pedido"):
                                st.write("Deseja cancelar e excluir este pedido permanentemente?")
                                if st.button("Sim, apagar", key=f"canc_adm2_{p.id_pedido}"):
                                    pedidos.remove(p)
                                    db.salvar_pedidos(pedidos)
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
                        
                        rastreio_atual = getattr(p, 'codigo_rastreio', 'Sem rastreio')
                        st.write(f"🚚 Rastreio: **{rastreio_atual}**")
                        
                        col_fin1, col_fin2 = st.columns(2)
                        with col_fin1:
                            with st.popover("📦 Rastreio"):
                                novo_rastreio = st.text_input("Código", value=rastreio_atual if rastreio_atual != 'Sem rastreio' else "", key=f"rast_{p.id_pedido}")
                                if st.button("Salvar", key=f"btn_rast_{p.id_pedido}"):
                                    p.atualizar_rastreio(novo_rastreio)
                                    db.salvar_pedidos(pedidos)
                                    
                                    # NOTIFICAÇÃO: Se atualizar o rastreio, reenvia o email
                                    email_cli = getattr(p.cliente, 'email', '')
                                    notificar_cliente_finalizado(email_cli, p.cliente.nome, p.pattern.nome, novo_rastreio)
                                    
                                    st.rerun()
                        with col_fin2:
                            with st.popover("🗑️ Apagar"):
                                st.write("Apagar o registro desta venda?")
                                if st.button("Confirmar", key=f"del_fin_{p.id_pedido}"):
                                    pedidos.remove(p)
                                    db.salvar_pedidos(pedidos)
                                    st.rerun()

# ==========================================
# ESTRUTURA PRINCIPAL E CONTROLE DE SESSÃO
# ==========================================
def main():
    if "perfil" not in st.session_state:
        st.session_state.perfil = None 
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = None

    st.markdown("""
        <style>
        [data-testid="stSidebar"] { padding-top: 1rem; }
        [data-testid="collapsedControl"] {display: none;}
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        try:
            st.image("logo.png", use_container_width=True)
        except Exception:
            st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🧶 Namigurumi</h2>", unsafe_allow_html=True)
        
        st.divider()

        # ----------------------------------------
        # SE NÃO ESTIVER LOGADO (VISITANTE)
        # ----------------------------------------
        if st.session_state.perfil is None:
            aba_login, aba_cadastro = st.tabs(["🔑 Login", "📝 Criar Conta"])
            
            with aba_login:
                login_email = st.text_input("E-mail")
                login_senha = st.text_input("Senha", type="password")
                
                if st.button("Entrar", use_container_width=True):
                    if login_email == "admin" and login_senha == "ana2026":
                        st.session_state.perfil = "admin"
                        st.rerun()
                    else:
                        cliente_encontrado = next((c for c in clientes if getattr(c, 'email', '') == login_email and getattr(c, 'senha', '') == login_senha), None)
                        
                        if cliente_encontrado:
                            st.session_state.perfil = "cliente"
                            st.session_state.usuario_logado = cliente_encontrado
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos!")
            
            with aba_cadastro:
                st.write("Novo por aqui? Cadastre-se:")
                with st.form("form_novo_cadastro"):
                    cad_nome = st.text_input("Nome Completo*")
                    cad_contato = st.text_input("WhatsApp (com DDD)*")
                    cad_email = st.text_input("E-mail*")
                    cad_senha = st.text_input("Crie uma Senha*", type="password")
                    
                    if st.form_submit_button("Criar Minha Conta", use_container_width=True):
                        if not cad_nome or not cad_email or not cad_senha:
                            st.error("Preencha todos os campos obrigatórios!")
                        else:
                            novo_c = Cliente(nome=cad_nome, contato=cad_contato, endereco="", cidade="", estado="", cep="", email=cad_email, senha=cad_senha)
                            clientes.append(novo_c)
                            db.salvar_clientes(clientes)
                            st.success("Conta criada! Agora faça o login.")

        # ----------------------------------------
        # SE FOR UM CLIENTE LOGADO
        # ----------------------------------------
        elif st.session_state.perfil == "cliente":
            st.markdown(f"### Olá, {st.session_state.usuario_logado.nome.split()[0]}! 👋")
            menu = st.radio("Seu Painel", ["🛍️ Catálogo", "📦 Meus Pedidos"])
            
            st.divider()
            if st.button("🚪 Sair da Conta", use_container_width=True):
                st.session_state.perfil = None
                st.session_state.usuario_logado = None
                st.rerun()

        # ----------------------------------------
        # SE FOR A ADMINISTRADORA (ANA)
        # ----------------------------------------
        elif st.session_state.perfil == "admin":
            st.markdown("### 👑 Painel Gerencial")
            menu = st.radio(
                "Navegação", 
                ["📦 Gestão de Pedidos", "👥 Clientes", "🧶 Estoque", "📝 Patterns", "📊 Analytics / BI"]
            )
            
            st.divider()
            
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
                
            st.divider()
            
            if st.button("🚪 Sair do Sistema", use_container_width=True):
                st.session_state.perfil = None
                st.rerun()

    # ==========================================
    # ROTEAMENTO DAS TELAS PRINCIPAIS
    # ==========================================
    if st.session_state.perfil is None:
        renderizar_catalogo()
        
    elif st.session_state.perfil == "cliente":
        if menu == "🛍️ Catálogo":
            renderizar_catalogo()
        elif menu == "📦 Meus Pedidos":
            renderizar_meus_pedidos()
            
    elif st.session_state.perfil == "admin":
        if menu == "📦 Gestão de Pedidos":
            renderizar_pedidos_admin()
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