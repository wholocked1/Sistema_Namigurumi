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
            for c in lista_clientes:
                writer.writerow([c.id_cliente, c.nome, c.contato, c.endereco, c.cidade, c.estado, c.cep])
                
    def carregar_clientes(self):
        clientes = []
        if not os.path.exists(self.arquivo_clientes): return clientes
        with open(self.arquivo_clientes, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                clientes.append(Cliente(row.get('Nome', ''), row.get('Contato', ''), row.get('Endereco', ''),
                                        row.get('Cidade', ''), row.get('Estado', ''), row.get('CEP', ''), row.get('ID_Cliente')))
        return clientes

    def salvar_materiais(self, dicionario_materiais):
        with open(self.arquivo_materiais, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['SKU', 'Tipo', 'Nome', 'Cor', 'Num_Cor', 'Quantidade', 'Peso_Gramas', 'Preco_Custo', 'Rendimento_Base'])
            for m in dicionario_materiais.values():
                writer.writerow([m.sku, m.tipo, m.nome, m.cor, m.num_cor, m.quantidade, m.peso_gramas, m.preco_custo, m.rendimento_base])

    def carregar_materiais(self):
        materiais = {}
        if not os.path.exists(self.arquivo_materiais): return materiais
        with open(self.arquivo_materiais, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                m = Material(row['SKU'], row['Tipo'], row['Nome'], row['Cor'], row['Num_Cor'], row['Quantidade'],
                             row['Peso_Gramas'] if row['Peso_Gramas'] != 'None' and row['Peso_Gramas'] else None,
                             row['Preco_Custo'], row['Rendimento_Base'])
                materiais[m.sku] = m
        return materiais

    def salvar_patterns(self, lista_patterns):
        with open(self.arquivo_patterns, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Nome', 'Materiais', 'Observacoes'])
            for p in lista_patterns:
                mat_str = "|".join([f"{sku}:{qtd}" for sku, qtd in p.quantidades_estimadas.items()])
                writer.writerow([p.nome, mat_str, p.observacoes])

    def carregar_patterns(self):
        patterns = []
        if not os.path.exists(self.arquivo_patterns): return patterns
        with open(self.arquivo_patterns, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                mat_str = row.get('Materiais', '')
                quantidades, skus = {}, []
                if mat_str:
                    for item in mat_str.split('|'):
                        if ':' in item:
                            sku, qtd = item.split(':')
                            quantidades[sku] = float(qtd)
                            skus.append(sku)
                patterns.append(Pattern(row['Nome'], skus, quantidades, row.get('Observacoes', '')))
        return patterns

    def salvar_pedidos(self, lista_pedidos):
        with open(self.arquivo_pedidos, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Adicionado a coluna Preco_Venda
            writer.writerow(['ID_Pedido', 'ID_Cliente', 'Nome_Cliente', 'Nome_Pattern', 'Preco_Venda', 'Status', 'Codigo_Rastreio', 'Pesos_Iniciais', 'Pesos_Finais', 'Data_Criacao'])
            for p in lista_pedidos:
                str_iniciais = "|".join([f"{k}:{v}" for k,v in p.pesos_iniciais.items()])
                str_finais = "|".join([f"{k}:{v}" for k,v in p.pesos_finais.items()])
                writer.writerow([
                    p.id_pedido, p.cliente.id_cliente, p.cliente.nome, p.pattern.nome, p.preco_venda,
                    p.status, p.codigo_rastreio, str_iniciais, str_finais, p.data_criacao
                ])

    def carregar_pedidos(self, lista_clientes, lista_patterns):
        pedidos = []
        if not os.path.exists(self.arquivo_pedidos): return pedidos
        
        mapa_clientes = {c.id_cliente: c for c in lista_clientes}
        mapa_patterns = {p.nome: p for p in lista_patterns}
        
        with open(self.arquivo_pedidos, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cliente = mapa_clientes.get(row['ID_Cliente'], Cliente(row['Nome_Cliente'], ""))
                pattern = mapa_patterns.get(row['Nome_Pattern'], Pattern(row['Nome_Pattern'], []))
                
                # Passa o preco_venda na recriação do pedido
                preco_venda_salvo = float(row.get('Preco_Venda', 0.0))
                p = Pedido(cliente, pattern, preco_venda_salvo, row['ID_Pedido'])
                
                p.status = row['Status']
                p.codigo_rastreio = row['Codigo_Rastreio'] if row['Codigo_Rastreio'] != 'None' and row['Codigo_Rastreio'] else None
                
                str_ini = row.get('Pesos_Iniciais', '')
                if str_ini:
                    for item in str_ini.split('|'):
                        if ':' in item:
                            k, v = item.split(':')
                            p.pesos_iniciais[k] = float(v)
                        
                str_fin = row.get('Pesos_Finais', '')
                if str_fin:
                    for item in str_fin.split('|'):
                        if ':' in item:
                            k, v = item.split(':')
                            p.pesos_finais[k] = float(v)
                        
                p.data_criacao = row.get('Data_Criacao', '')
                pedidos.append(p)
        return pedidos