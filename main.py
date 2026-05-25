# main.py
from modelos import Cliente, Material
from database import DatabaseCSV

def executar_testes():
    print("--- Iniciando Sistema Namigurumi ---")
    
    # 1. Instanciando o banco de dados
    db = DatabaseCSV()
    
    # 2. Carregando clientes existentes (se houver)
    clientes_salvos = db.carregar_clientes()
    print(f"Clientes carregados do CSV: {len(clientes_salvos)}")
    
    # 3. Criando um cliente novo para teste
    novo_cliente = Cliente(nome="João Silva", contato="(11) 99999-9999")
    clientes_salvos.append(novo_cliente)
    
    # 4. Salvando no CSV
    db.salvar_clientes(clientes_salvos)
    print(f"Cliente {novo_cliente.nome} salvo com sucesso com ID: {novo_cliente.id_cliente}!")

if __name__ == "__main__":
    executar_testes()