import csv
import os
from modelos import Cliente, Material, Pattern, Pedido

class DatabaseCSV:
    def __init__(self):
        self.arquivo_clientes = 'clientes.csv'
        self.arquivo_materiais = 'materiais.csv'
        self.arquivo_pedidos = 'pedidos.csv'
        self.arquivo_patterns = 'patterns.csv'
    
    def salvar_clientes(self, lista_clientes):
        with open(self.arquivo_clientes, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID_Cliente', 'Nome', 'Contato', 'Endereco', 'Cidade', 'Estado', 'CEP'])
            for cliente in lista_clientes:
                writer.writerow([
                    cliente.id_cliente, cliente.nome, cliente.contato, 
                    cliente.endereco, cliente.cidade, cliente.estado, cliente.cep
                ])
                
    def carregar_clientes(self):
        clientes = []
        if not os.path.exists(self.arquivo_clientes):
            return clientes
        with open(self.arquivo_clientes, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                clientes.append(Cliente(
                    nome=row.get('Nome', ''), 
                    contato=row.get('Contato', ''), 
                    endereco=row.get('Endereco', ''),
                    cidade=row.get('Cidade', ''),
                    estado=row.get('Estado', ''),
                    cep=row.get('CEP', ''),
                    id_cliente=row.get('ID_Cliente')
                ))
        return clientes

    def salvar_materiais(self, dicionario_materiais):
        with open(self.arquivo_materiais, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['SKU', 'Tipo', 'Nome', 'Cor', 'Num_Cor', 'Quantidade', 'Peso_Gramas', 'Preco_Custo', 'Rendimento_Base'])
            for m in dicionario_materiais.values():
                writer.writerow([m.sku, m.tipo, m.nome, m.cor, m.num_cor, m.quantidade, m.peso_gramas, m.preco_custo, m.rendimento_base])

    def carregar_materiais(self):
        materiais = {}
        if not os.path.exists(self.arquivo_materiais):
            return materiais
        with open(self.arquivo_materiais, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                m = Material(
                    sku=row['SKU'], tipo=row['Tipo'], nome=row['Nome'], cor=row['Cor'],
                    num_cor=row['Num_Cor'], quantidade=row['Quantidade'],
                    peso_gramas=row['Peso_Gramas'] if row['Peso_Gramas'] != 'None' and row['Peso_Gramas'] else None,
                    preco_custo=row['Preco_Custo'], rendimento_base=row['Rendimento_Base']
                )
                materiais[m.sku] = m
        return materiais

    # --- PATTERNS ---
    def salvar_patterns(self, lista_patterns):
        with open(self.arquivo_patterns, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nome', 'Materiais', 'Observacoes'])
            for p in lista_patterns:
                # Formata o dicionário de materiais para salvar no CSV como SKU1:Qtd|SKU2:Qtd
                mat_str = "|".join([f"{sku}:{qtd}" for sku, qtd in p.quantidades_estimadas.items()])
                writer.writerow([p.nome, mat_str, p.observacoes])

    def carregar_patterns(self):
        patterns = []
        if not os.path.exists(self.arquivo_patterns):
            return patterns
        with open(self.arquivo_patterns, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mat_str = row.get('Materiais', '')
                quantidades = {}
                skus = []
                if mat_str:
                    for item in mat_str.split('|'):
                        if ':' in item:
                            sku, qtd = item.split(':')
                            quantidades[sku] = float(qtd)
                            skus.append(sku)
                patterns.append(Pattern(row['Nome'], skus, quantidades, row.get('Observacoes', '')))
        return patterns

    # --- PEDIDOS ---
    def salvar_pedidos(self, lista_pedidos):
        with open(self.arquivo_pedidos, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['ID_Pedido', 'ID_Cliente', 'Nome_Cliente', 'Nome_Pattern', 'Status', 'Codigo_Rastreio', 'Peso_Inicial', 'Peso_Final', 'Data_Criacao'])
            for p in lista_pedidos:
                writer.writerow([
                    p.id_pedido, p.cliente.id_cliente, p.cliente.nome, p.pattern.nome,
                    p.status, p.codigo_rastreio, p.peso_fio_inicial, p.peso_fio_final, p.data_criacao
                ])

    def carregar_pedidos(self, lista_clientes, lista_patterns):
        pedidos = []
        if not os.path.exists(self.arquivo_pedidos):
            return pedidos
        
        mapa_clientes = {c.id_cliente: c for c in lista_clientes}
        mapa_patterns = {p.nome: p for p in lista_patterns}
        
        with open(self.arquivo_pedidos, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cliente = mapa_clientes.get(row['ID_Cliente'], Cliente(row['Nome_Cliente'], ""))
                # Agora o pedido se liga ao pattern real com os SKUs cadastrados!
                pattern = mapa_patterns.get(row['Nome_Pattern'], Pattern(row['Nome_Pattern'], []))
                
                p = Pedido(cliente, pattern, row['ID_Pedido'])
                p.status = row['Status']
                p.codigo_rastreio = row['Codigo_Rastreio'] if row['Codigo_Rastreio'] != 'None' and row['Codigo_Rastreio'] else None
                p.peso_fio_inicial = float(row['Peso_Inicial'])
                p.peso_fio_final = float(row['Peso_Final'])
                p.data_criacao = row['Data_Criacao']
                pedidos.append(p)
        return pedidos