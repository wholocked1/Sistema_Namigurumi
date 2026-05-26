import tkinter as tk
from tkinter import messagebox, ttk
from modelos import Cliente, Material, Pattern, Pedido
from database import DatabaseCSV

class NamigurumiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Namigurumi - Sistema de Gestão")
        self.root.geometry("400x350")
        
        # Carrega o banco de dados exatamente como fazíamos no terminal
        self.db = DatabaseCSV()
        self.clientes = self.db.carregar_clientes()
        self.estoque = self.db.carregar_materiais()
        self.patterns = self.db.carregar_patterns()
        self.pedidos = self.db.carregar_pedidos(self.clientes, self.patterns)
        
        self.menu_principal()

    def menu_principal(self):
        # Limpa a tela inicial
        for widget in self.root.winfo_children():
            widget.destroy()
            
        tk.Label(self.root, text="🧶 Namigurumi", font=("Helvetica", 20, "bold")).pack(pady=20)
        
        # Botões do Menu
        tk.Button(self.root, text="Cadastrar Cliente", width=30, height=2, command=self.tela_cadastrar_cliente).pack(pady=5)
        tk.Button(self.root, text="Listar Clientes", width=30, height=2, command=self.tela_listar_clientes).pack(pady=5)
        
        tk.Label(self.root, text="As telas de Estoque, Patterns e Pedidos\nserão adicionadas a seguir!", fg="gray").pack(pady=20)
        
        tk.Button(self.root, text="Sair", width=15, command=self.root.quit).pack(pady=10)

    def tela_cadastrar_cliente(self):
        # Cria uma janela pop-up
        janela = tk.Toplevel(self.root)
        janela.title("Novo Cliente")
        janela.geometry("350x400")
        
        # Campos de texto (Entry)
        tk.Label(janela, text="Nome do Cliente:").pack(pady=2)
        entry_nome = tk.Entry(janela, width=40)
        entry_nome.pack(pady=2)
        
        tk.Label(janela, text="Contato (Insta/Tel):").pack(pady=2)
        entry_contato = tk.Entry(janela, width=40)
        entry_contato.pack(pady=2)
        
        tk.Label(janela, text="Endereço:").pack(pady=2)
        entry_endereco = tk.Entry(janela, width=40)
        entry_endereco.pack(pady=2)
        
        tk.Label(janela, text="Cidade:").pack(pady=2)
        entry_cidade = tk.Entry(janela, width=40)
        entry_cidade.pack(pady=2)
        
        tk.Label(janela, text="Estado:").pack(pady=2)
        entry_estado = tk.Entry(janela, width=40)
        entry_estado.pack(pady=2)

        def salvar():
            nome = entry_nome.get().strip()
            contato = entry_contato.get().strip()
            endereco = entry_endereco.get().strip()
            cidade = entry_cidade.get().strip()
            estado = entry_estado.get().strip()
            
            if not nome:
                messagebox.showwarning("Aviso", "O campo Nome é obrigatório!", parent=janela)
                return
                
            novo_c = Cliente(nome, contato, endereco, cidade, estado, "")
            self.clientes.append(novo_c)
            self.db.salvar_clientes(self.clientes)
            
            messagebox.showinfo("Sucesso", f"Cliente {nome} salvo com sucesso!", parent=janela)
            janela.destroy() # Fecha o pop-up após salvar

        tk.Button(janela, text="Salvar Cliente", width=20, bg="lightgreen", command=salvar).pack(pady=20)

    def tela_listar_clientes(self):
        janela = tk.Toplevel(self.root)
        janela.title("Clientes Cadastrados")
        janela.geometry("600x300")
        
        # Criando uma tabela interativa (Treeview)
        colunas = ("ID", "Nome", "Contato", "Local")
        tabela = ttk.Treeview(janela, columns=colunas, show="headings")
        
        tabela.heading("ID", text="ID")
        tabela.heading("Nome", text="Nome")
        tabela.heading("Contato", text="Contato")
        tabela.heading("Local", text="Local")
        
        tabela.column("ID", width=80)
        tabela.column("Nome", width=200)
        tabela.column("Contato", width=150)
        tabela.column("Local", width=150)
        
        tabela.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Preenchendo a tabela com os dados do CSV
        for c in self.clientes:
            tabela.insert("", "end", values=(c.id_cliente, c.nome, c.contato, f"{c.cidade}/{c.estado}"))

# Ponto de partida do programa visual
if __name__ == "__main__":
    root = tk.Tk()
    app = NamigurumiGUI(root)
    root.mainloop()