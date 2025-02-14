import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import time

# Classe que representa uma "linha" (caixa de texto + checkbox + botão Excluir)
class MacroRow:
    def __init__(self, parent, index, remove_callback):
        """
        parent: Frame (ou outro widget) onde a linha será inserida
        index: posição/índice da linha na lista
        remove_callback: função a ser chamada ao clicar em "Excluir"
        """
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='x', pady=5)

        # Rótulo com "Mensagem X:"
        self.label = ttk.Label(self.frame, text=f"Mensagem {index + 1}:")
        self.label.pack(side=tk.LEFT)

        # Variável de texto para a caixa de entrada
        self.var_text = tk.StringVar()
        self.entry = ttk.Entry(self.frame, width=25, textvariable=self.var_text)
        self.entry.pack(side=tk.LEFT, padx=5)

        # Variável para o checkbox "Ativar"
        self.var_checkbox = tk.BooleanVar(value=True)
        self.checkbox = ttk.Checkbutton(self.frame, text="Ativar", variable=self.var_checkbox)
        self.checkbox.pack(side=tk.LEFT, padx=5)

        # Botão Excluir
        self.button_excluir = ttk.Button(self.frame, text="Excluir", command=remove_callback)
        # Por padrão, vamos ocultar o botão; só será mostrado na última linha.
        self.button_excluir.pack_forget()

    def set_label(self, text):
        """Atualiza o texto do rótulo (por exemplo, Mensagem 1, Mensagem 2, etc.)."""
        self.label.config(text=text)

    def show_exclude_button(self, show):
        """Mostra ou esconde o botão de excluir."""
        if show:
            self.button_excluir.pack(side=tk.LEFT, padx=5)
        else:
            self.button_excluir.pack_forget()

    def destroy(self):
        """Remove completamente o frame (e seus widgets) da tela."""
        self.frame.destroy()

class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro de Teclas")
        self.root.geometry("600x450")

        ttk.Label(root, text="Escolha um comando e digite a mensagem:", font=("Arial", 12)).pack(pady=10)

        # Lista de teclas pré-definidas
        self.atalhos_disponiveis = [
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "CTRL+A", "CTRL+C", "CTRL+V", "CTRL+Z", "CTRL+X",
            "ALT+TAB", "SHIFT+TAB", "ENTER", "ESC", "SPACE"
        ]

        # Variável para a tecla selecionada
        self.tecla_selecionada = tk.StringVar(value="Escolha a tecla")

        # Cria o combobox para escolher a tecla
        self.tecla_label = ttk.Label(root, text="Escolha a Tecla ou Comando:")
        self.tecla_label.pack()

        self.tecla_combobox = ttk.Combobox(
            root,
            values=self.atalhos_disponiveis + ["Digite a tecla..."],
            state="readonly",
            width=20,
            textvariable=self.tecla_selecionada
        )
        self.tecla_combobox.pack()
        self.tecla_combobox.bind("<<ComboboxSelected>>", self.on_tecla_selecionada)

        # Entrada para cadência
        self.cadencia_label = ttk.Label(root, text="Cadência entre mensagens (em segundos):")
        self.cadencia_label.pack(pady=5)

        self.cadencia_entry = ttk.Entry(root, width=10)
        self.cadencia_entry.insert(0, "0.5")  # valor padrão
        self.cadencia_entry.pack(pady=5)

        # Canvas + Scrollbar para rolar as linhas
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame que conterá as linhas (MacroRows)
        self.messages_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        # Ajusta a região de rolagem sempre que o frame for redimensionado
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Lista de linhas (MacroRow)
        self.rows = []

        # Cria inicialmente 5 linhas
        for _ in range(5):
            self.add_row()

        # Botão para adicionar mais caixas
        self.add_button = ttk.Button(root, text="Adicionar Caixa", command=self.add_row)
        self.add_button.pack(pady=10)

        # Botões de controle (Ativar e Parar Macro)
        self.start_button = ttk.Button(root, text="Ativar Macro", command=self.iniciar_macro)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Parar Macro", command=self.parar_macro, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.running = False

    def on_tecla_selecionada(self, event):
        """Se for 'Digite a tecla...', libera para digitar manualmente."""
        if self.tecla_selecionada.get() == "Digite a tecla...":
            self.tecla_combobox.config(state="normal")
        else:
            self.tecla_combobox.config(state="readonly")

    def add_row(self):
        """Adiciona uma nova linha (MacroRow), até o limite de 30."""
        if len(self.rows) >= 30:
            return

        index = len(self.rows)  # posição na lista
        new_row = MacroRow(
            parent=self.messages_frame,
            index=index,
            remove_callback=lambda idx=index: self.remove_row(idx)
        )
        self.rows.append(new_row)
        self.update_rows()

    def update_rows(self):
        """
        Atualiza:
          - Os textos de cada rótulo (Mensagem 1, Mensagem 2, etc.)
          - O botão Excluir para aparecer apenas na última linha (se houver mais de 1).
        """
        for i, row in enumerate(self.rows):
            row.set_label(f"Mensagem {i+1}:")

            # Esconder botão de excluir por padrão
            row.show_exclude_button(False)

        # Se há mais de 1 linha, mostra o botão de excluir apenas na última
        if len(self.rows) > 1:
            self.rows[-1].show_exclude_button(True)

    def remove_row(self, index):
        """
        Remove a linha de índice 'index' (se houver mais de uma).
        """
        if len(self.rows) <= 1:
            # Se só tem 1, não remove
            return

        # Destrói a linha (frame e widgets)
        self.rows[index].destroy()
        del self.rows[index]

        # Renumera e atualiza tudo
        self.update_rows()

    def iniciar_macro(self):
        """Configura e inicia a macro sem bloquear a interface."""
        if self.running:
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Obtém a tecla escolhida
        tecla = self.tecla_selecionada.get().strip()

        # Se for "Digite a tecla...", pegamos o que estiver no combobox
        if tecla.lower() == "digite a tecla...":
            tecla = self.tecla_combobox.get()

        # Monta a lista de mensagens ativas
        mensagens_ativas = []
        for row in self.rows:
            if row.var_checkbox.get():  # Se o checkbox "Ativar" estiver marcado
                mensagens_ativas.append(row.var_text.get())

        # Pega o tempo de cadência da entrada do usuário
        try:
            cadencia = float(self.cadencia_entry.get())
            if cadencia < 0.001:
                cadencia = 0.001
        except ValueError:
            cadencia = 0.001

        # Se há uma tecla definida, ativamos a macro
        if tecla:
            tecla = tecla.lower()
            self.ativar_macro(tecla, mensagens_ativas, cadencia)

    def ativar_macro(self, tecla, mensagens, cadencia):
        """Envia as mensagens quando a tecla for pressionada."""
        def acionar():
            for msg in mensagens:
                if msg:
                    # Se for uma única tecla digitável, apaga antes de enviar
                    if len(tecla) == 1:
                        pyautogui.press('backspace')
                    pyautogui.write(msg)
                    pyautogui.press('enter')
                    time.sleep(cadencia)

        keyboard.add_hotkey(tecla, acionar, suppress=True)

    def parar_macro(self):
        """Desativa a macro."""
        if not self.running:
            return

        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        keyboard.unhook_all()

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()
