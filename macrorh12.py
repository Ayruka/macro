import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import time

class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro de Teclas")
        self.root.geometry("500x450")

        ttk.Label(root, text="Escolha um comando e digite a mensagem:", font=("Arial", 12)).pack(pady=10)

        # Lista de teclas pré-definidas
        self.atalhos_disponiveis = [
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "CTRL+A", "CTRL+C", "CTRL+V", "CTRL+Z", "CTRL+X",
            "ALT+TAB", "SHIFT+TAB", "ENTER", "ESC", "SPACE"
        ]

        # Tecla e mensagens
        self.tecla_selecionada = tk.StringVar()
        self.tecla_selecionada.set("Escolha a tecla")
        self.mensagens = []
        self.checkboxes = []
        self.checkbox_vars = []

        # Caixa para escolher a tecla da macro
        self.tecla_label = ttk.Label(root, text="Escolha a Tecla ou Comando:")
        self.tecla_label.pack()

        self.tecla_combobox = ttk.Combobox(
            root,
            values=self.atalhos_disponiveis + ["Digite a tecla..."],
            state="readonly",
            width=20
        )
        self.tecla_combobox.pack()
        self.tecla_combobox.bind("<<ComboboxSelected>>", self.on_tecla_selecionada)

        # Caixa de entrada para o tempo de cadência entre as mensagens
        self.cadencia_label = ttk.Label(root, text="Cadência entre mensagens (em segundos):")
        self.cadencia_label.pack(pady=5)

        self.cadencia_entry = ttk.Entry(root, width=10)
        self.cadencia_entry.insert(0, "0.5")  # valor padrão de 0.5 segundos
        self.cadencia_entry.pack(pady=5)

        # Caixas de texto para a macro (5 mensagens)
        for i in range(5):
            frame = ttk.Frame(root)
            frame.pack(pady=5)

            ttk.Label(frame, text=f"Mensagem {i+1}:").pack(side=tk.LEFT)

            mensagem_entry = ttk.Entry(frame, width=25)
            mensagem_entry.pack(side=tk.LEFT, padx=5)

            # Checkbox para ativar/desativar a caixa de mensagem
            checkbox_var = tk.BooleanVar(value=True)  # Controla o estado do checkbox
            checkbox = tk.Checkbutton(frame, text="Ativar", variable=checkbox_var)
            checkbox.pack(side=tk.LEFT, padx=5)

            self.mensagens.append(mensagem_entry)
            self.checkboxes.append(checkbox)
            self.checkbox_vars.append(checkbox_var)

        self.start_button = ttk.Button(root, text="Ativar Macro", command=self.iniciar_macro)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(root, text="Parar Macro", command=self.parar_macro, state=tk.DISABLED)
        self.stop_button.pack()

        self.running = False

    def on_tecla_selecionada(self, event):
        """Se for 'Digite a tecla...', permitimos que o usuário digite diretamente no Combobox."""
        if self.tecla_combobox.get() == "Digite a tecla...":
            # Desbloqueia para o usuário digitar manualmente
            self.tecla_combobox.config(state="normal")
        else:
            # Continua readonly para selecionar apenas da lista
            self.tecla_combobox.config(state="readonly")

    def ativar_macro(self, tecla, mensagens, cadencia):
        """Envia os textos (um por vez, com intervalo de cadência entre eles) quando a tecla for pressionada."""
        def acionar():
            for msg in mensagens:
                if msg:  # Se não estiver vazio
                    # Se for uma tecla digitável (tamanho 1), apaga antes de enviar
                    if len(tecla) == 1:
                        pyautogui.press('backspace')
                    pyautogui.write(msg)
                    pyautogui.press('enter')
                    time.sleep(cadencia)  # Intervalo de cadência configurável

        # Registra o atalho
        keyboard.add_hotkey(tecla, acionar, suppress=True)

    def iniciar_macro(self):
        """Configura e inicia a macro sem bloquear a interface."""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Obtém a tecla escolhida
            tecla = self.tecla_combobox.get().strip()

            # Se for "Digite a tecla...", pegamos o que estiver no combobox como a tecla digitada
            if tecla.lower() == "digite a tecla...":
                tecla = self.tecla_combobox.get()

            # Monta a lista de mensagens ativas
            mensagens_ativas = []
            for i in range(5):
                if self.checkbox_vars[i].get():
                    mensagens_ativas.append(self.mensagens[i].get())

            # Pega o tempo de cadência da entrada do usuário
            try:
                cadencia = float(self.cadencia_entry.get())  # Obtém o valor inserido
                if cadencia < 0.001:
                    cadencia = 0.001  # Limite mínimo de 0.001
            except ValueError:
                cadencia = 0.001  # Se inválido, assume o limite mínimo

            # Se há uma tecla definida, ativamos a macro
            if tecla:
                # Converte para minúsculo para o keyboard reconhecer (ex: "ctrl+a", "f2", etc.)
                tecla = tecla.lower()
                self.ativar_macro(tecla, mensagens_ativas, cadencia)

    def parar_macro(self):
        """Desativa a macro e reabilita o botão de ativar."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        keyboard.unhook_all()  # Remove todos os atalhos

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()
