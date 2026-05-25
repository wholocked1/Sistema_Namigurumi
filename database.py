# database.py
import csv
import os
from modelos import Cliente

class DatabaseCSV:
    def __init__(self):
        # Define os nomes dos arquivos CSV que serão gerados na pasta do projeto
        self.arquivo_clientes = 'clientes.csv'
        self.arquivo_materiais = 'materiais.csv'
        self.arquivo_pedidos = 'pedidos.csv'
    
    def salvar_clientes(self, lista_clientes):
        with open(self.arquivo_clientes, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID_Cliente', 'Nome', 'Contato'])
            for cliente in lista_clientes:
                writer.writerow([cliente.id_cliente, cliente.nome, cliente.contato])
                
    def carregar_clientes(self):
        clientes = []
        if not os.path.exists(self.arquivo_clientes):
            return clientes # Retorna lista vazia se o arquivo não existir ainda
            
        with open(self.arquivo_clientes, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                clientes.append(Cliente(row['Nome'], row['Contato'], row['ID_Cliente']))
        return clientes