import uuid
from datetime import datetime

class Material:
    def __init__(self, sku, tipo, nome, cor, num_cor, quantidade, peso_gramas=None, preco_custo=0.0, rendimento_base=1):
        self.sku = sku
        self.tipo = tipo
        self.nome = nome
        self.cor = cor
        self.num_cor = num_cor
        self.quantidade = int(quantidade)
        self.peso_gramas = float(peso_gramas) if peso_gramas else None
        self.preco_custo = float(preco_custo)
        self.rendimento_base = float(rendimento_base)

    def obter_custo_unitario(self):
        if self.preco_custo == 0.0 or self.rendimento_base == 0:
            return 0.0
        return self.preco_custo / self.rendimento_base

class Cliente:
    def __init__(self, nome, contato, endereco="", cidade="", estado="", cep="", id_cliente=None):
        self.id_cliente = id_cliente if id_cliente else f"CLI-{str(uuid.uuid4())[:6].upper()}"
        self.nome = nome
        self.contato = contato
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.cep = cep
        self.historico_pedidos = []

class Pattern:
    def __init__(self, nome, skus_necessarios, quantidades_estimadas=None, observacoes=""):
        self.nome = nome
        self.skus_necessarios = skus_necessarios
        self.quantidades_estimadas = quantidades_estimadas if quantidades_estimadas else {}
        self.observacoes = observacoes

class Pedido:
    def __init__(self, cliente, pattern, id_pedido=None):
        self.id_pedido = id_pedido if id_pedido else f"PED-{str(uuid.uuid4())[:6].upper()}"
        self.cliente = cliente
        self.pattern = pattern
        self.status = "Em espera"
        self.codigo_rastreio = None
        self.peso_fio_inicial = 0.0
        self.peso_fio_final = 0.0
        self.data_criacao = datetime.now().strftime("%Y-%m-%d")

    def atualizar_rastreio(self, codigo):
        self.codigo_rastreio = codigo

    def registrar_pesos(self, peso_inicial, peso_final):
        self.peso_fio_inicial = float(peso_inicial)
        self.peso_fio_final = float(peso_final)
        self.status = "Finalizado"

    def calcular_uso_fio(self):
        return max(0.0, self.peso_fio_inicial - self.peso_fio_final)

    def calcular_custo_total_materiais(self, dicionario_materiais, sku_fio_principal):
        custo_total = 0.0
        if sku_fio_principal in dicionario_materiais:
            fio = dicionario_materiais[sku_fio_principal]
            gramas_gastadas = self.calcular_uso_fio()
            custo_total += gramas_gastadas * fio.obter_custo_unitario()
        
        for sku, qtd_usada in self.pattern.quantidades_estimadas.items():
            if sku in dicionario_materiais:
                material = dicionario_materiais[sku]
                custo_total += qtd_usada * material.obter_custo_unitario()
                
        return round(custo_total, 2)