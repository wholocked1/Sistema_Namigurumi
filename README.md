# 🧶 Sistema de Gestão Namigurumi

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-success?style=flat-square)

Um sistema web completo desenvolvido em Python para o gerenciamento da loja de amigurumis **Namigurumi**. A aplicação integra o controle de estoque de materiais, catálogo de receitas (patterns), precificação dinâmica baseada no consumo real de fios e um assistente virtual automatizado via e-mail.

## ✨ Funcionalidades

* **👥 Gestão de Clientes:** Cadastro e acompanhamento de dados dos clientes e histórico de encomendas.
* **📦 Controle de Estoque Inteligente:** Monitoramento de materiais (fios, olhos, enchimentos). O sistema emite alertas automáticos na interface para itens esgotados ou acabando.
* **📝 Catálogo de Patterns (Receitas):** Armazenamento de receitas com sistema de busca por nome ou SKU, incluindo as quantidades base de cada material necessário.
* **💰 Precificação e Lucro Líquido:** Sistema de pesagem dupla (fio inicial e fio final) que calcula o gasto exato em gramas de cada cor. Cruza o custo de material com o preço de venda para exibir o **lucro líquido real** de cada peça.
* **🤖 Assistente Vigia de E-mail:** Um script autônomo que monitora a caixa de entrada. Ao receber um "Ping", analisa o banco de dados e responde automaticamente com a lista de compras atualizada (materiais em falta/acabando).
* **🔒 Segurança (Boas Práticas):** Credenciais de e-mail e senhas isoladas utilizando variáveis de ambiente (`.env`).

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Interface Web:** Streamlit
* **Banco de Dados:** Arquivos CSV estruturados (leitura/escrita customizada)
* **Automação:** Bibliotecas nativas `imaplib` e `smtplib`
* **Segurança:** `python-dotenv`

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/Sistema_Namigurumi.git
cd Sistema_Namigurumi 
```

### 2. Instalar as dependências
Certifique-se de instalar as bibliotecas necessárias para rodar a interface e ler as variáveis de ambiente:
```bash
pip install streamlit python-dotenv
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto e adicione as suas credenciais do Gmail (lembre-se de usar uma "Senha de App" gerada no Google):

```env
EMAIL_BOT=seu_email@gmail.com
SENHA_BOT=sua_senha_de_app
```

### 4. Rodar a Interface Web (Streamlit)
No terminal, execute o comando abaixo para iniciar o painel de gestão:

```bash
python -m streamlit run app.py
```

### 5. Rodar o Robô Vigia (Opcional)
Para habilitar a automação de lista de compras via e-mail, abra um **segundo terminal** na mesma pasta e rode:

```bash
python vigia_email.py
```

Envie um e-mail para si mesma com o assunto Ping Compras para receber o status do estoque no seu celular em até 60 segundos!

### 6. Colocar o logo do negócio (Opcional)
Para ter seu logo na parte superior da página, coloque a imagem na mesma pasta que o projeto e coloque o nome dele de "logo.PNG". Quando recarregar a página, seu logo estará na parte superior esquerdo.

## 📂 Estrutura de Arquivos

* `app.py`: Interface web e rotas do Streamlit.
* `modelos.py`: Definição das classes de objetos (`Cliente`, `Material`, `Pattern`, `Pedido`).
* `database.py`: Lógica de persistência de dados (CRUD) em arquivos `.csv`.
* `vigia_email.py`: Script do bot de monitoramento de e-mails via IMAP/SMTP.
* `*.csv`: Arquivos atuando como banco de dados local da aplicação.

---
Desenvolvido por **Ana Carolina Cogo Nami** 💻

