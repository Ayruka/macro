import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pyautogui
import keyboard
import time
import threading

# Classe que representa uma "linha" (caixa de texto + checkbox + botão Excluir)
class MacroRow:
    def __init__(self, parent, index, remove_callback):
        """
        parent: Frame onde a linha será inserida.
        index: Posição/índice da linha na lista.
        remove_callback: Função a ser chamada ao clicar em "Excluir".
        """
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='x', pady=5)

        # Rótulo com "Mensagem X:"
        self.label = ttk.Label(self.frame, text=f"Mensagem {index + 1}:", font=("Arial", 10, "bold"))
        self.label.pack(side=tk.LEFT)

        # Caixa de entrada para a mensagem (largura aumentada)
        self.var_text = tk.StringVar()
        self.entry = ttk.Entry(self.frame, width=55, textvariable=self.var_text)
        self.entry.pack(side=tk.LEFT, padx=5)

        # Checkbox "Ativar"
        self.var_checkbox = tk.BooleanVar(value=True)
        self.checkbox = ttk.Checkbutton(self.frame, text="Ativar", variable=self.var_checkbox)
        self.checkbox.pack(side=tk.LEFT, padx=5)

        # Botão Excluir (inicialmente oculto; aparece somente na última linha)
        self.button_excluir = ttk.Button(self.frame, text="Excluir", command=remove_callback)
        self.button_excluir.pack_forget()

    def set_label(self, text):
        """Atualiza o rótulo (ex.: 'Mensagem 1:')."""
        self.label.config(text=text)

    def show_exclude_button(self, show):
        """Mostra ou esconde o botão de excluir."""
        if show:
            self.button_excluir.pack(side=tk.LEFT, padx=5)
        else:
            self.button_excluir.pack_forget()

    def destroy(self):
        """Remove o frame e todos os widgets da linha."""
        self.frame.destroy()

class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MACRO DIVULGADORES RÁDIO HABBLET")
        self.root.geometry("750x500")
        self.root.configure(bg="white")

        # Carregar a imagem de fundo
        self.background_image = Image.open("background.png")
        self.background_image = self.background_image.resize((750, 500), Image.Resampling.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Criar um Canvas para o fundo
        self.background_canvas = tk.Canvas(root, width=750, height=500)
        self.background_canvas.pack(fill="both", expand=True)
        self.background_canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        # Adicionar os widgets por cima do Canvas de fundo
        self.create_widgets()

    def create_widgets(self):
        """Cria e posiciona os widgets por cima do fundo."""
        # Textos maiores e em negrito
        ttk.Label(self.root, text="Escolha um comando e digite a mensagem:", font=("Arial", 12, "bold")).place(x=40, y=20)

        # Lista de teclas pré-definidas
        self.atalhos_disponiveis = [
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "CTRL+A", "CTRL+C", "CTRL+V", "CTRL+Z", "CTRL+X",
            "ALT+TAB", "SHIFT+TAB", "ENTER", "ESC", "SPACE"
        ]

        # Combobox para selecionar a tecla de envio
        self.tecla_selecionada = tk.StringVar(value="Escolha a tecla")
        self.tecla_label = ttk.Label(self.root, text="Comando para enviar as mensagens:", font=("Arial", 10, "bold"))
        self.tecla_label.place(x=40, y=50)
        self.tecla_combobox = ttk.Combobox(
            self.root,
            values=self.atalhos_disponiveis + ["Digite a tecla..."],
            state="readonly",
            width=20,
            textvariable=self.tecla_selecionada
        )
        self.tecla_combobox.place(x=40, y=75)
        self.tecla_combobox.bind("<<ComboboxSelected>>", self.on_tecla_selecionada)

        # Entrada para a cadência entre mensagens (velocidade do flood)
        self.cadencia_label = ttk.Label(self.root, text="Cadência entre mensagens (em segundos):", font=("Arial", 10, "bold"))
        self.cadencia_label.place(x=250, y=50)
        self.cadencia_entry = ttk.Entry(self.root, width=10)
        self.cadencia_entry.insert(0, "0.5")  # Valor padrão para flood speed
        self.cadencia_entry.place(x=250, y=75)

        # Checkbox para ativar o loop de envio
        self.loop_var = tk.BooleanVar(value=False)
        self.loop_checkbox = ttk.Checkbutton(self.root, text="Ativar Loop de Envio", variable=self.loop_var)
        self.loop_checkbox.place(x=40, y=105)

        # Entrada para o intervalo entre execuções da macro (loop interval)
        self.loop_interval_label = ttk.Label(self.root, text="Intervalo entre execuções da macro (em segundos):", font=("Arial", 10, "bold"))
        self.loop_interval_label.place(x=400, y=50)
        self.loop_interval_entry = ttk.Entry(self.root, width=10)
        self.loop_interval_entry.insert(0, "20")  # Valor padrão para loop interval
        self.loop_interval_entry.place(x=400, y=75)

        # Nova opção: Combobox para hotkey de PARADA da macro
        self.stop_hotkey_label = ttk.Label(self.root, text="Hotkey para Parar Macro:", font=("Arial", 10, "bold"))
        self.stop_hotkey_label.place(x=40, y=140)
        self.stop_hotkey_var = tk.StringVar(value="ESC")
        self.stop_hotkey_combobox = ttk.Combobox(
            self.root,
            values=["ESC", "F9", "F10", "CTRL+ESC", "CTRL+SHIFT+X"],
            state="readonly",
            width=20,
            textvariable=self.stop_hotkey_var
        )
        self.stop_hotkey_combobox.place(x=40, y=165)

        # Nova opção: Combobox para hotkey de ATIVAÇÃO da macro
        self.start_hotkey_label = ttk.Label(self.root, text="Hotkey para Ativar Macro:", font=("Arial", 10, "bold"))
        self.start_hotkey_label.place(x=250, y=140)
        self.start_hotkey_var = tk.StringVar(value="F12")  # Valor padrão
        self.start_hotkey_combobox = ttk.Combobox(
            self.root,
            values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
            state="readonly",
            width=20,
            textvariable=self.start_hotkey_var
        )
        self.start_hotkey_combobox.place(x=250, y=165)
        self.start_hotkey_combobox.bind("<<ComboboxSelected>>", self.registrar_hotkey_automatico)

        # Canvas + Scrollbar para rolar as linhas (MacroRows)
        self.canvas = tk.Canvas(self.root, bd=0, highlightthickness=0)  # Remove bordas e destaque
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Posicionamento do Canvas e Scrollbar
        self.canvas.place(x=40, y=200, width=670, height=200)  # Tamanho do Canvas aumentado
        self.scrollbar.place(x=710, y=200, height=200)  # Scrollbar ao lado do Canvas (ajuste o x para alinhar)

        # Frame interno para as mensagens
        self.messages_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")

        # Ajusta o tamanho do Frame interno para ser maior que o Canvas
        self.messages_frame.configure(width=670, height=300)  # Aumente a altura para mais espaço

        # Ajusta a área de rolagem quando o frame interno muda de tamanho
        self.messages_frame.bind("<Configure>", lambda e: self.canvas.config(scrollregion=self.canvas.bbox("all")))

        # Função para vincular o scroll do mouse ao canvas
        def on_mouse_wheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # Bind do evento de scroll do mouse para o Canvas
        self.canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        # Lista de linhas (MacroRow)
        self.rows = []
        for _ in range(5):
            self.add_row()

        # Botão para adicionar mais caixas
        self.add_button = ttk.Button(self.root, text="Adicionar Caixa", command=self.add_row)
        self.add_button.place(x=40, y=460)

        # Botões de controle: Ativar Macro e Parar Macro
        self.start_button = ttk.Button(self.root, text="Ativar Macro", command=self.iniciar_macro)
        self.start_button.place(x=250, y=460)
        self.stop_button = ttk.Button(self.root, text="Parar Macro", command=self.parar_macro, state=tk.DISABLED)
        self.stop_button.place(x=400, y=460)

        self.running = False
        self.loop_started = False  # Flag para indicar se o loop já foi iniciado
        self.hotkey_registered = None  # Armazena a hotkey de ativação registrada

        # Registra a hotkey de ativação automaticamente ao iniciar o programa
        self.registrar_hotkey_automatico()

    def on_tecla_selecionada(self, event):
        """Libera edição se 'Digite a tecla...' for selecionado."""
        if self.tecla_selecionada.get() == "Digite a tecla...":
            self.tecla_combobox.config(state="normal")
        else:
            self.tecla_combobox.config(state="readonly")

    def add_row(self):
        """Adiciona uma nova linha (até 30)."""
        if len(self.rows) >= 30:
            return
        index = len(self.rows)
        new_row = MacroRow(
            parent=self.messages_frame,
            index=index,
            remove_callback=lambda idx=index: self.remove_row(idx)
        )
        self.rows.append(new_row)
        self.update_rows()

    def update_rows(self):
        """Atualiza os rótulos e exibe o botão 'Excluir' somente na última linha (se houver > 1)."""
        for i, row in enumerate(self.rows):
            row.set_label(f"Mensagem {i+1}:")
            row.show_exclude_button(False)
        if len(self.rows) > 1:
            self.rows[-1].show_exclude_button(True)

    def remove_row(self, index):
        """Remove a linha de índice 'index' (mantendo pelo menos 1)."""
        if len(self.rows) <= 1:
            return
        self.rows[index].destroy()
        del self.rows[index]
        self.update_rows()

    def registrar_hotkey_automatico(self, event=None):
        """Registra automaticamente a hotkey de ativação quando o usuário seleciona uma opção."""
        hotkey = self.start_hotkey_var.get().strip()
        if hotkey:
            if self.hotkey_registered:
                try:
                    keyboard.remove_hotkey(self.hotkey_registered)  # Remove a hotkey anterior
                except ValueError:
                    pass  # Ignora se a hotkey já foi removida
            try:
                self.hotkey_registered = keyboard.add_hotkey(hotkey, self.iniciar_macro, suppress=True)
                print(f"Hotkey '{hotkey}' registrada com sucesso!")
            except ValueError as e:
                print(f"Erro ao registrar hotkey: {e}")

    def iniciar_macro(self):
        """
        Inicia a macro e registra a hotkey de envio.
        O loop de envio (se ativado) só começará quando o usuário pressionar a tecla definida pela primeira vez.
        Além disso, registra a hotkey de parada definida.
        """
        if self.running:
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.loop_started = False  # Reseta para que o loop inicie na primeira pressão

        # Obtém a tecla para envio
        tecla = self.tecla_selecionada.get().strip()
        if tecla.lower() == "digite a tecla...":
            tecla = self.tecla_combobox.get()

        # Monta a lista de mensagens ativas
        mensagens_ativas = []
        for row in self.rows:
            if row.var_checkbox.get():
                mensagens_ativas.append(row.var_text.get())

        # Flood speed: cadência entre mensagens (velocidade do flood)
        try:
            flood_speed = float(self.cadencia_entry.get())
            if flood_speed < 0.00001:
                flood_speed = 0.001
        except ValueError:
            flood_speed = 0.001

        # Registra a hotkey para enviar as mensagens (envio único ou início do loop)
        if tecla:
            tecla = tecla.lower()
            self.ativar_macro(tecla, mensagens_ativas, flood_speed)

        # Registra a hotkey para parar a macro
        stop_key = self.stop_hotkey_var.get().strip()
        keyboard.add_hotkey(stop_key, self.parar_macro, suppress=True)

    def ativar_macro(self, tecla, mensagens, flood_speed):
        """
        Registra a hotkey para envio das mensagens.
        Se o loop estiver ativado, na primeira pressão da tecla o loop é iniciado;
        caso contrário, envia as mensagens uma única vez.
        """
        def acionar():
            if self.loop_var.get() and not self.loop_started:
                try:
                    loop_interval = float(self.loop_interval_entry.get())
                    if loop_interval < 0:
                        loop_interval = 0
                except ValueError:
                    loop_interval = 20
                threading.Thread(target=self.loop_mensagens, args=(mensagens, flood_speed, loop_interval), daemon=True).start()
                self.loop_started = True
            elif not self.loop_var.get():
                for msg in mensagens:
                    if msg:
                        if len(tecla) == 1:
                            pyautogui.press('backspace')
                        pyautogui.write(msg)
                        pyautogui.press('enter')
                        time.sleep(flood_speed)
        keyboard.add_hotkey(tecla, acionar, suppress=True)

    def loop_mensagens(self, mensagens, flood_speed, loop_interval):
        """
        Loop: envia as mensagens com a cadência (flood_speed) e espera loop_interval para repetir.
        Esse loop só começa quando o usuário pressiona a tecla pela primeira vez.
        """
        while self.running and self.loop_var.get():
            for msg in mensagens:
                if msg:
                    pyautogui.write(msg)
                    pyautogui.press('enter')
                    time.sleep(flood_speed)
            time.sleep(loop_interval)

    def parar_macro(self):
        """Para a macro, desabilita os hotkeys e reseta as flags."""
        if not self.running:
            return
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        keyboard.unhook_all()  # Remove todas as hotkeys, exceto a de ativação
        self.loop_started = False

        # Re-registra a hotkey de ativação após parar a macro
        self.registrar_hotkey_automatico()

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()