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
git clone [https://github.com/SEU_USUARIO/Sistema_Namigurumi.git](https://github.com/SEU_USUARIO/Sistema_Namigurumi.git)
cd Sistema_Namigurumi