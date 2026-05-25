from modelos import Cliente, Material, Pattern, Pedido
from database import DatabaseCSV

def exibir_menu():
    print("\n" + "="*35)
    print("      SISTEMA GESTÃO NAMIGURUMI     ")
    print("="*35)
    print("1. Cadastrar Cliente")
    print("2. Cadastrar Material no Estoque")
    print("3. Criar Novo Pedido (Em Espera)")
    print("4. Registrar Pesagem e Finalizar Pedido")
    print("5. Adicionar Código de Rastreio")
    print("6. Visualizar Relatórios (Estoque / Pedidos)")
    print("7. Listar Clientes Cadastrados")
    print("8. Atualizar Dados de Cliente")
    print("9. Cadastrar Pattern (Receita de Crochê)")
    print("10. Atualizar Pattern Cadastrado")
    print("11. Atualizar Material Cadastrado")
    print("0. Sair")
    print("="*35)

def main():
    db = DatabaseCSV()
    
    clientes = db.carregar_clientes()
    estoque = db.carregar_materiais()
    patterns = db.carregar_patterns()
    pedidos = db.carregar_pedidos(clientes, patterns)
    
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n--- CADASTRO DE CLIENTE ---")
            nome = input("Nome do Cliente: ")
            contato = input("Contato (Telefone/Insta): ")
            endereco = input("Endereço (Rua, Número, Complemento): ")
            cidade = input("Cidade: ")
            estado = input("Estado (Ex: SP): ")
            cep = input("CEP: ")
            
            novo_c = Cliente(nome, contato, endereco, cidade, estado, cep)
            clientes.append(novo_c)
            db.salvar_clientes(clientes)
            print(f"Cliente cadastrado com sucesso! ID: {novo_c.id_cliente}")
            
        elif opcao == "2":
            print("\n--- CADASTRO DE MATERIAL ---")
            sku = input("SKU (Ex: FIO-AMI-VD01): ").strip().upper()
            tipo = input("Tipo (Fio, Olhos, Focinho, Terço): ")
            nome = input("Nome do Material (Ex: Fio Amigurumi): ")
            cor = input("Cor: ")
            num_cor = input("Número da Cor: ")
            quantidade = input("Quantidade em Estoque: ")
            peso = input("Peso em gramas (Se for fio, ex 125. Pressione Enter para pular): ")
            preco = input("Preço de Custo pago (Ex: 19.90. Enter para 0.0): ")
            rendimento = input("Rendimento Base (Gramas do novelo ou Qtd do lote de olhos. Enter para 1): ")
            
            peso_g = float(peso) if peso else None
            preco_c = float(preco) if preco else 0.0
            rend_b = float(rendimento) if rendimento else 1.0
            
            novo_m = Material(sku, tipo, nome, cor, num_cor, quantidade, peso_g, preco_c, rend_b)
            estoque[sku] = novo_m
            db.salvar_materiais(estoque)
            print(f"Material {sku} adicionado ao estoque!")
            
        elif opcao == "3":
            print("\n--- CRIAR NOVO PEDIDO ---")
            if not clientes:
                print("Nenhum cliente cadastrado ainda!")
                continue
            if not patterns:
                print("Nenhum Pattern cadastrado! Cadastre um Pattern (Opção 9) antes de criar pedidos.")
                continue
                
            print("\nClientes Disponíveis:")
            for idx, c in enumerate(clientes):
                print(f"[{idx}] {c.nome} (ID: {c.id_cliente})")
            
            try:
                c_idx = int(input("Escolha o número do cliente: "))
                cliente_escolhido = clientes[c_idx]
            except (ValueError, IndexError):
                print("Opção inválida.")
                continue
                
            print("\nPatterns Disponíveis:")
            for idx, pat in enumerate(patterns):
                print(f"[{idx}] {pat.nome}")
                
            try:
                pat_idx = int(input("Escolha o número do pattern: "))
                pattern_escolhido = patterns[pat_idx]
            except (ValueError, IndexError):
                print("Opção inválida.")
                continue
            
            novo_p = Pedido(cliente_escolhido, pattern_escolhido)
            pedidos.append(novo_p)
            db.salvar_pedidos(pedidos)
            print(f"Pedido {novo_p.id_pedido} criado com status 'Em espera'!")
            
        elif opcao == "4":
            print("\n--- FINALIZAR PEDIDO COM PESAGEM ---")
            pedidos_espera = [p for p in pedidos if p.status == "Em espera"]
            if not pedidos_espera:
                print("Não há pedidos pendentes 'Em espera'.")
                continue
                
            for idx, p in enumerate(pedidos_espera):
                print(f"[{idx}] {p.id_pedido} - {p.pattern.nome} (Cliente: {p.cliente.nome})")
                
            try:
                p_idx = int(input("Escolha o número do pedido para finalizar: "))
                pedido_escolhido = pedidos_espera[p_idx]
            except (ValueError, IndexError):
                print("Opção inválida. Retornando ao menu.")
                continue
            
            peso_inicial = float(input("Peso do fio ANTES de começar (em gramas): "))
            peso_final = float(input("Peso do fio DEPOIS de terminar (em gramas): "))
            
            pedido_escolhido.registrar_pesos(peso_inicial, peso_final)
            
            sku_fio = input("Digite o SKU do fio principal usado (para cálculo de custo): ").strip().upper()
            custo = pedido_escolhido.calcular_custo_total_materiais(estoque, sku_fio)
            
            db.salvar_pedidos(pedidos)
            print(f"\nPedido {pedido_escolhido.id_pedido} Finalizado!")
            print(f"Consumo total: {pedido_escolhido.calcular_uso_fio()}g")
            print(f"Custo estimado dos materiais (Fio + Itens do Pattern): R$ {custo}")
            
        elif opcao == "5":
            print("\n--- ADICIONAR CÓDIGO DE RASTREIO ---")
            if not pedidos:
                print("Nenhum pedido cadastrado.")
                continue
                
            for idx, p in enumerate(pedidos):
                print(f"[{idx}] {p.id_pedido} - {p.pattern.nome} [Rastreio Atual: {p.codigo_rastreio}]")
                
            try:
                p_idx = int(input("Escolha o número do pedido: "))
                cod_rastreio = input("Digite o código de rastreio postal: ").strip().upper()
            except (ValueError, IndexError):
                print("Opção inválida.")
                continue
            
            pedidos[p_idx].atualizar_rastreio(cod_rastreio)
            db.salvar_pedidos(pedidos)
            print("Código de rastreio atualizado com sucesso!")
            
        elif opcao == "6":
            print("\n--- RELATÓRIOS ---")
            print(f"\n>> ESTOQUE ATUAL ({len(estoque)} itens):")
            for m in estoque.values():
                print(f"SKU: {m.sku} | {m.nome} ({m.cor} #{m.num_cor}) | Qtd: {m.quantidade} | Custo Unitário Base: R$ {m.obter_custo_unitario():.4f}")
                
            print(f"\n>> HISTÓRICO DE PEDIDOS ({len(pedidos)} pedidos):")
            for p in pedidos:
                rastreio_str = p.codigo_rastreio if p.codigo_rastreio else "Não enviado"
                print(f"ID: {p.id_pedido} | Projeto: {p.pattern.nome} | Cliente: {p.cliente.nome} | Status: {p.status} | Rastreio: {rastreio_str}")
                
        elif opcao == "7":
            print("\n--- CLIENTES CADASTRADOS ---")
            if not clientes:
                print("Nenhum cliente cadastrado no momento.")
            else:
                print(f"Total de clientes: {len(clientes)}\n")
                for c in clientes:
                    print(f"ID: {c.id_cliente} | Nome: {c.nome} | Contato: {c.contato} | Local: {c.cidade}/{c.estado}")
                    
        elif opcao == "8":
            print("\n--- ATUALIZAR DADOS DE CLIENTE ---")
            if not clientes:
                print("Nenhum cliente cadastrado no momento.")
                continue
                
            for idx, c in enumerate(clientes):
                print(f"[{idx}] {c.nome} (ID: {c.id_cliente})")
                
            try:
                c_idx = int(input("Escolha o número do cliente que deseja atualizar: "))
                cliente_alvo = clientes[c_idx]
            except (ValueError, IndexError):
                print("Opção inválida.")
                continue

            print(f"\nAtualizando dados de: {cliente_alvo.nome}")
            print("DICA: Deixe em branco e pressione Enter para manter a informação atual.\n")
            
            novo_nome = input(f"Nome [{cliente_alvo.nome}]: ").strip()
            if novo_nome: cliente_alvo.nome = novo_nome
            
            novo_contato = input(f"Contato [{cliente_alvo.contato}]: ").strip()
            if novo_contato: cliente_alvo.contato = novo_contato
            
            novo_endereco = input(f"Endereço [{cliente_alvo.endereco}]: ").strip()
            if novo_endereco: cliente_alvo.endereco = novo_endereco
            
            nova_cidade = input(f"Cidade [{cliente_alvo.cidade}]: ").strip()
            if nova_cidade: cliente_alvo.cidade = nova_cidade
            
            novo_estado = input(f"Estado [{cliente_alvo.estado}]: ").strip()
            if novo_estado: cliente_alvo.estado = novo_estado
            
            novo_cep = input(f"CEP [{cliente_alvo.cep}]: ").strip()
            if novo_cep: cliente_alvo.cep = novo_cep
            
            db.salvar_clientes(clientes)
            db.salvar_pedidos(pedidos)
            print(f"\nCadastro de {cliente_alvo.nome} atualizado com sucesso!")

        elif opcao == "9":
            print("\n--- CADASTRO DE PATTERN (RECEITA) ---")
            nome_pattern = input("Nome do Pattern (Ex: Snoopy, Chopper, Maple the Fox): ").strip()
            obs = input("Observações da receita: ").strip()
            
            quantidades = {}
            skus_list = []
            
            print("\nAdicione os SKUs dos materiais necessários (Ex: FIO-VD01, OLHO-P02).")
            while True:
                sku_mat = input("SKU do Material (ou pressione Enter para finalizar a lista): ").strip().upper()
                if not sku_mat:
                    break
                
                qtd_str = input(f"Quantidade/Unidades necessárias de {sku_mat} (Ex: 2): ").strip()
                try:
                    qtd = float(qtd_str) if qtd_str else 1.0
                except ValueError:
                    qtd = 1.0
                    
                quantidades[sku_mat] = qtd
                skus_list.append(sku_mat)
                print(f"--> {qtd}x {sku_mat} adicionado ao pattern!")
                
            novo_pattern = Pattern(nome_pattern, skus_list, quantidades, obs)
            patterns.append(novo_pattern)
            db.salvar_patterns(patterns)
            print(f"\nPattern '{nome_pattern}' salvo com sucesso!")

        elif opcao == "10":
            print("\n--- ATUALIZAR PATTERN CADASTRADO ---")
            if not patterns:
                print("Nenhum Pattern cadastrado no momento.")
                continue
                
            for idx, p in enumerate(patterns):
                print(f"[{idx}] {p.nome}")
                
            try:
                p_idx = int(input("Escolha o número do Pattern que deseja atualizar: "))
                pattern_alvo = patterns[p_idx]
            except (ValueError, IndexError):
                print("Opção inválida.")
                continue

            print(f"\nAtualizando dados de: {pattern_alvo.nome}")
            print("DICA: Deixe em branco e pressione Enter para manter a informação atual.\n")
            
            novo_nome = input(f"Nome [{pattern_alvo.nome}]: ").strip()
            if novo_nome: pattern_alvo.nome = novo_nome
            
            nova_obs = input(f"Observações [{pattern_alvo.observacoes}]: ").strip()
            if nova_obs: pattern_alvo.observacoes = nova_obs
            
            refazer_mat = input("Deseja alterar a lista de materiais/SKUs deste pattern? (s/n): ").strip().lower()
            if refazer_mat == 's':
                pattern_alvo.quantidades_estimadas.clear()
                pattern_alvo.skus_necessarios.clear()
                
                print("\nAdicione os novos SKUs dos materiais necessários.")
                while True:
                    sku_mat = input("SKU do Material (ou pressione Enter para finalizar a lista): ").strip().upper()
                    if not sku_mat:
                        break
                    
                    qtd_str = input(f"Quantidade/Unidades necessárias de {sku_mat} (Ex: 2): ").strip()
                    try:
                        qtd = float(qtd_str) if qtd_str else 1.0
                    except ValueError:
                        qtd = 1.0
                        
                    pattern_alvo.quantidades_estimadas[sku_mat] = qtd
                    pattern_alvo.skus_necessarios.append(sku_mat)
                    print(f"--> {qtd}x {sku_mat} atualizado no pattern!")
            
            db.salvar_patterns(patterns)
            db.salvar_pedidos(pedidos)
            print(f"\nPattern '{pattern_alvo.nome}' atualizado com sucesso!")
            
        elif opcao == "11":
            print("\n--- ATUALIZAR MATERIAL CADASTRADO ---")
            if not estoque:
                print("Nenhum material cadastrado no momento.")
                continue
                
            for m in estoque.values():
                print(f"SKU: {m.sku} | {m.nome} (Cor: {m.cor} #{m.num_cor}) | Qtd Atual: {m.quantidade}")
                
            sku_alvo = input("\nDigite o SKU do material que deseja atualizar: ").strip().upper()
            if sku_alvo not in estoque:
                print("SKU não encontrado. Retornando ao menu.")
                continue
                
            mat_alvo = estoque[sku_alvo]
            
            print(f"\nAtualizando dados de: {mat_alvo.nome} (SKU: {mat_alvo.sku})")
            print("DICA: Deixe em branco e pressione Enter para manter a informação atual.\n")
            
            novo_tipo = input(f"Tipo [{mat_alvo.tipo}]: ").strip()
            if novo_tipo: mat_alvo.tipo = novo_tipo
            
            novo_nome = input(f"Nome [{mat_alvo.nome}]: ").strip()
            if novo_nome: mat_alvo.nome = novo_nome
            
            nova_cor = input(f"Cor [{mat_alvo.cor}]: ").strip()
            if nova_cor: mat_alvo.cor = nova_cor
            
            novo_num_cor = input(f"Número da Cor [{mat_alvo.num_cor}]: ").strip()
            if novo_num_cor: mat_alvo.num_cor = novo_num_cor
            
            nova_qtd = input(f"Quantidade em Estoque [{mat_alvo.quantidade}]: ").strip()
            if nova_qtd:
                try:
                    mat_alvo.quantidade = int(nova_qtd)
                except ValueError:
                    print("--> Valor inválido, mantendo quantidade anterior.")
                    
            novo_peso = input(f"Peso em gramas [{mat_alvo.peso_gramas}]: ").strip()
            if novo_peso:
                try:
                    mat_alvo.peso_gramas = float(novo_peso)
                except ValueError:
                    print("--> Valor inválido, mantendo peso anterior.")
                    
            novo_preco = input(f"Preço de Custo [{mat_alvo.preco_custo}]: ").strip()
            if novo_preco:
                try:
                    mat_alvo.preco_custo = float(novo_preco)
                except ValueError:
                    print("--> Valor inválido, mantendo preço anterior.")
                    
            novo_rendimento = input(f"Rendimento Base [{mat_alvo.rendimento_base}]: ").strip()
            if novo_rendimento:
                try:
                    mat_alvo.rendimento_base = float(novo_rendimento)
                except ValueError:
                    print("--> Valor inválido, mantendo rendimento anterior.")
                    
            db.salvar_materiais(estoque)
            print(f"\nMaterial '{mat_alvo.sku}' atualizado com sucesso!")

        elif opcao == "0":
            print("Encerrando o sistema Namigurumi. Até mais!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()