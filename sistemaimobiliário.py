import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pickle
import os

class ImobiliariaApp:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Sistema Imobiliário")
        self.janela.geometry("800x600")
        self.janela.configure(bg="gray")  

        
        largura_janela = 800
        altura_janela = 600
        largura_tela = self.janela.winfo_screenwidth()
        altura_tela = self.janela.winfo_screenheight()
        posicao_x = (largura_tela - largura_janela) // 2
        posicao_y = (altura_tela - altura_janela) // 2
        self.janela.geometry(f"{largura_janela}x{altura_janela}+{posicao_x}+{posicao_y}")

        self.conexao = sqlite3.connect("imobiliaria.db")
        self.criar_tabela()

        self.propriedades = []

       
        style = ttk.Style()
        style.configure("TNotebook", background="lightgray")
        style.configure("TNotebook.Tab", background="gray", foreground="black", font=('Arial', 10, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", "darkgray")])

        
        self.notebook = ttk.Notebook(janela)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        
        self.aba_adicionar = ttk.Frame(self.notebook)
        self.aba_listar = ttk.Frame(self.notebook)

        
        self.notebook.add(self.aba_adicionar, text="Adicionar")
        self.notebook.add(self.aba_listar, text="Listar")

        
        self.label_nome = ttk.Label(self.aba_adicionar, text="Nome da Propriedade:", font=('Arial', 12))
        self.entry_nome = ttk.Entry(self.aba_adicionar, width=50, font=('Arial', 12))

        self.label_preco = ttk.Label(self.aba_adicionar, text="Preço:", font=('Arial', 12))
        self.entry_preco = ttk.Entry(self.aba_adicionar, width=20, font=('Arial', 12))

        self.btn_adicionar = ttk.Button(self.aba_adicionar, text="Adicionar Propriedade", command=self.adicionar_propriedade, width=30)

        
        self.label_nome.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_nome.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.label_preco.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_preco.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.btn_adicionar.grid(row=2, column=0, columnspan=2, pady=20)

        
        self.listbox_propriedades = tk.Listbox(self.aba_listar, width=60, height=15, font=('Arial', 10))
        self.scrollbar = ttk.Scrollbar(self.aba_listar, orient="vertical", command=self.listbox_propriedades.yview)
        self.listbox_propriedades.config(yscrollcommand=self.scrollbar.set)
        self.btn_listar = ttk.Button(self.aba_listar, text="Listar Propriedades", command=self.listar_propriedades, width=30)
        self.btn_excluir = ttk.Button(self.aba_listar, text="Excluir Propriedade", command=self.excluir_propriedade, width=30)

        
        self.listbox_propriedades.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.btn_listar.grid(row=1, column=0, padx=10, pady=10)
        self.btn_excluir.grid(row=2, column=0, padx=10, pady=10)

        
        self.aba_adicionar.columnconfigure(0, weight=1)
        self.aba_adicionar.columnconfigure(1, weight=1)
        self.aba_adicionar.rowconfigure(2, weight=1)
        self.aba_listar.columnconfigure(0, weight=1)
        self.aba_listar.rowconfigure(0, weight=1)

        self.executar_programa()

    def criar_tabela(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS propriedades (
                    id INTEGER PRIMARY KEY,
                    nome TEXT,
                    preco REAL
                )
            """)
            self.conexao.commit()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar a tabela: {str(e)}")

    def adicionar_propriedade(self):
        try:
            nome = self.entry_nome.get()
            preco = self.entry_preco.get()

            if nome and preco:
                preco = float(preco)
                cursor = self.conexao.cursor()
                cursor.execute("INSERT INTO propriedades (nome, preco) VALUES (?, ?)", (nome, preco))
                self.conexao.commit()
                tk.messagebox.showinfo("Sucesso", "Propriedade adicionada com sucesso!")
                self.limpar_campos()
            else:
                tk.messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        except ValueError:
            tk.messagebox.showerror("Erro", "Por favor, insira um valor numérico para o preço.")
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao adicionar propriedade: {str(e)}")

    def listar_propriedades(self):
        try:
            self.listbox_propriedades.delete(0, tk.END)
            cursor = self.conexao.cursor()
            cursor.execute("SELECT id, nome, preco FROM propriedades")
            propriedades = cursor.fetchall()
            for prop in propriedades:
                self.listbox_propriedades.insert(tk.END, f"{prop[0]}. {prop[1]}: R$ {prop[2]}")
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao listar propriedades: {str(e)}")

    def excluir_propriedade(self):
        try:
            selecionados = self.listbox_propriedades.curselection()
            if selecionados:
                indice = int(selecionados[0])
                cursor = self.conexao.cursor()
                cursor.execute("SELECT id, nome FROM propriedades")
                propriedades = cursor.fetchall()
                propriedade_excluida = propriedades[indice - 1]
                resposta = messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir '{propriedade_excluida[1]}'?")
                if resposta:
                    cursor.execute("DELETE FROM propriedades WHERE id=?", (propriedade_excluida[0],))
                    self.conexao.commit()
                    tk.messagebox.showinfo("Sucesso", f"Propriedade '{propriedade_excluida[1]}' excluída com sucesso!")
                    self.listar_propriedades()
            else:
                tk.messagebox.showwarning("Aviso", "Por favor, selecione uma propriedade para excluir.")
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao excluir propriedade: {str(e)}")

    def limpar_campos(self):
        self.entry_nome.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)

    def backup(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT * FROM propriedades")
            propriedades = cursor.fetchall()
            with open("backup_propriedades.pkl", "wb") as arquivo:
                pickle.dump(propriedades, arquivo)
            tk.messagebox.showinfo("Backup", "Backup realizado com sucesso!")
        except Exception as e:
            tk.messagebox.showerror("Erro", f"Erro ao realizar backup: {str(e)}")

    def executar_programa(self):
        while True:
            try:
                escolha = int(input("Escolha uma opção:\n1. Adicionar Propriedade\n2. Listar Propriedades\n3. Excluir Propriedade\n4. Backup\n5. Sair\n"))
                if escolha == 1:
                    self.adicionar_propriedade()
                elif escolha == 2:
                    self.listar_propriedades()
                elif escolha == 3:
                    self.excluir_propriedade()
                elif escolha == 4:
                    self.backup()
                elif escolha == 5:
                    self.janela.destroy()
                    break
                else:
                    print("Escolha inválida. Tente novamente.")
            except ValueError:
                print("Por favor, insira um número válido.")
            except Exception as e:
                print(f"Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    janela = tk.Tk()
    app = ImobiliariaApp(janela)
    janela.mainloop()
