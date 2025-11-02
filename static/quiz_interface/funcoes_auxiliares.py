import tkinter as tk
from tkinter import PhotoImage, messagebox
import os

class CarbonoQuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Carbono 🌱")
        self.geometry("700x500")
        self.respostas = {}
        self.pergunta_atual = 0

        self.assets = os.path.join(os.path.dirname(__file__), "assets")
        self.perguntas = [
            ("💡", "Consumo de energia elétrica por mês (kWh)", "icon_energy.png", "energia"),
            ("🚗", "Quantos km você dirige por semana?", "icon_transport.png", "transporte"),
            ("🍖", "Quantos kg de carne você consome por semana?", "icon_food.png", "carne"),
            ("✈️", "Quantas horas de voo você fez neste ano?", "icon_flight.png", "voo"),
            ("🗑️", "Quantos kg de lixo você gera por semana?", "icon_waste.png", "lixo")
        ]

        bg_path = os.path.join(self.assets, "background.png")
        self.bg_image = PhotoImage(file=bg_path)
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        self.frame = None
        self.iniciar_quiz()

    def iniciar_quiz(self):
        self.frame = tk.Frame(self, bg="#e8f5e9")
        self.frame.place(relwidth=1, relheight=1)
        tk.Label(self.frame, text="🌿 Descubra sua Pegada de Carbono!", font=("Arial", 16, "bold"), bg="#e8f5e9", fg="#1b5e20").pack(pady=20)
        tk.Button(self.frame, text="Começar", bg="#388e3c", fg="white", font=("Arial", 12, "bold"), command=self.proxima_pergunta).pack(pady=20)

    def proxima_pergunta(self):
        if self.frame:
            self.frame.destroy()

        if self.pergunta_atual < len(self.perguntas):
            emoji, texto, icone, chave = self.perguntas[self.pergunta_atual]
            self.criar_pergunta(emoji, texto, icone, chave)
            self.pergunta_atual += 1
        else:
            self.mostrar_resultado()

    def criar_pergunta(self, emoji, texto, icone, chave):
        self.frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20)
        self.frame.place(relwidth=1, relheight=1)

        try:
            icon_path = os.path.join(self.assets, icone)
            icon = PhotoImage(file=icon_path)
            icon_label = tk.Label(self.frame, image=icon, bg="#ffffff")
            icon_label.image = icon
            icon_label.pack(pady=5)
        except:
            pass

        tk.Label(self.frame, text=f"{emoji} {texto}", font=("Arial", 14, "bold"), bg="#ffffff", fg="#1b5e20").pack(pady=5)
        entrada = tk.Entry(self.frame)
        entrada.pack(pady=5)
        entrada.insert(0, "0")

        def salvar():
            try:
                valor = float(entrada.get())
                self.respostas[chave] = valor
                self.proxima_pergunta()
            except ValueError:
                messagebox.showerror("Erro", "Digite um número válido.")

        tk.Button(self.frame, text="Próximo", bg="#4caf50", fg="white", command=salvar).pack(pady=10)

    def mostrar_resultado(self):
        self.frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20)
        self.frame.place(relwidth=1, relheight=1)

        total = (
            self.respostas.get("energia", 0) * 0.084 +
            self.respostas.get("transporte", 0) * 0.192 +
            self.respostas.get("carne", 0) * 27.0 +
            self.respostas.get("voo", 0) * 90.0 +
            self.respostas.get("lixo", 0) * 1.9 * 52
        )

        toneladas = total / 1000
        arvores = round(toneladas * 5.3)

        tk.Label(self.frame, text="🌍 Resultado Final", font=("Arial", 14, "bold"), bg="#ffffff", fg="#1b5e20").pack(pady=10)
        tk.Label(self.frame, text=f"Você emitiu aproximadamente {toneladas:.2f} toneladas de CO₂e por ano.", bg="#ffffff").pack()
        tk.Label(self.frame, text=f"Isso equivale a plantar {arvores} árvores 🌳", bg="#ffffff").pack(pady=5)

        tk.Button(self.frame, text="Refazer Quiz", bg="#388e3c", fg="white", command=self.reiniciar).pack(pady=10)

    def reiniciar(self):
        self.frame.destroy()
        self.respostas = {}
        self.pergunta_atual = 0
        self.iniciar_quiz()

if __name__ == "__main__":
    app = CarbonoQuizApp()
    app.mainloop()
