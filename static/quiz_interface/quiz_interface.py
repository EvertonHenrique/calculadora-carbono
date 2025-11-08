"""
quiz_interface_final.py

Versão aprimorada da Calculadora de Carbono:
- Usa `factors.json` como fonte de fatores e preços.
- Exibe background.png na tela inicial (usa Pillow se disponível; caso contrário tenta PhotoImage).
- Cada tela de pergunta usa a cor correspondente à categoria (as mesmas do gráfico/tabela).
- Gera um HTML com gráfico de barras verticais e tabela explicativa usando as mesmas cores.
- Valida entradas (não permite negativos) e tem botão "Recalcular".

Como usar:
- Coloque este script na mesma pasta do seu projeto.
- Crie uma subpasta `assets/` contendo:
    - background.png        (fundo principal)
    - icon_energy.png       (ícone decorativo para o HTML) — opcional
- Tenha o arquivo `factors.json` na mesma pasta do script.
- Pillow (PIL) é opcional — se estiver instalada, melhora o redimensionamento da imagem de fundo.
"""

import tkinter as tk
from tkinter import messagebox
import os
import json
import math
import tempfile
import webbrowser

# Tenta importar Pillow (opcional). Se não existir, o app continua com fallback.
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---------------------------
# Local paths (assume script directory)
# ---------------------------
BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FACTORS_PATH = os.path.join(BASE_DIR, "factors.json")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "background.png")
ICON_PATH = os.path.join(ASSETS_DIR, "icon_energy.png")  # decorativo para HTML (opcional)

# ---------------------------
# Carrega fatores e preços do JSON (fallback para constantes simples se arquivo faltar)
# ---------------------------
DEFAULT_FACTORS = {
    "energia": {"descricao": "Consumo de energia elétrica em kWh", "fator": 0.084},
    "transporte": {
        "carro": 0.192, "moto": 0.103, "onibus": 0.089, "metro": 0.041, "bike": 0.0, "caminhada": 0.0
    },
    "carne": {"descricao": "Consumo de carne bovina em kg", "fator": 27.0},
    "aviao": {"descricao": "Horas de voo por ano", "fator": 90.0},
    "lixo": {"descricao": "Quantidade de lixo gerado por semana (kg)", "fator": 1.9},
    "precos": {"Reflorestamento": 40, "Energia Renovável": 55, "Captura e Armazenamento": 120}
}

try:
    with open(FACTORS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normaliza a estrutura para uso consistente no código
    FACTORES = {
        "energia": data.get("energia", DEFAULT_FACTORS["energia"])["fator"] if isinstance(data.get("energia"), dict) else DEFAULT_FACTORS["energia"]["fator"],
        "transporte": data.get("transporte", DEFAULT_FACTORS["transporte"]),
        "carne": data.get("carne", DEFAULT_FACTORS["carne"])["fator"] if isinstance(data.get("carne"), dict) else DEFAULT_FACTORS["carne"]["fator"],
        "aviao": data.get("aviao", DEFAULT_FACTORS["aviao"])["fator"] if isinstance(data.get("aviao"), dict) else DEFAULT_FACTORS["aviao"]["fator"],
        "lixo": data.get("lixo", DEFAULT_FACTORS["lixo"])["fator"] if isinstance(data.get("lixo"), dict) else DEFAULT_FACTORS["lixo"]["fator"],
        "precos": data.get("precos", DEFAULT_FACTORS["precos"])
    }
except Exception:
    FACTORES = {
        "energia": DEFAULT_FACTORS["energia"]["fator"],
        "transporte": DEFAULT_FACTORS["transporte"],
        "carne": DEFAULT_FACTORS["carne"]["fator"],
        "aviao": DEFAULT_FACTORS["aviao"]["fator"],
        "lixo": DEFAULT_FACTORS["lixo"]["fator"],
        "precos": DEFAULT_FACTORS["precos"]
    }

# ---------------------------
# Paleta de cores — deve coincidir com o HTML/Gráfico
# ---------------------------
CATEGORY_COLORS = {
    "Energia": "#4e79a7",      # azul
    "Transporte": "#f28e2b",   # laranja
    "Alimentação": "#e15759",  # vermelho
    "Viagens": "#76b7b2",      # verde-água
    "Resíduos": "#59a14f"      # verde
}

# ---------------------------
# Utilitários de validação simples
# ---------------------------
def is_nonneg_number(s):
    """Tenta converter string para float e verifica se é >= 0 e finito."""
    try:
        v = float(s)
    except Exception:
        return False
    if math.isfinite(v) and v >= 0:
        return True
    return False

# ---------------------------
# Aplicação Tkinter principal
# ---------------------------
class CalculadoraCarbonoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Carbono 🌱")
        self.root.geometry("800x560")
        self.root.minsize(700, 480)

        # estado
        self.respostas = {}
        self.pergunta_atual = 0
        self.current_frame = None

        # prepara imagem de fundo (tenta Pillow, se disponível)
        self.bg_label = None
        self.bg_img_tk = None
        if os.path.exists(BACKGROUND_PATH):
            try:
                if PIL_AVAILABLE:
                    # carregamos imagem com Pillow e adaptamos ao tamanho da janela dinamicamente
                    self._load_bg_with_pillow(BACKGROUND_PATH)
                    # redimensiona quando janela muda
                    self.root.bind("<Configure>", self._on_root_configure)
                else:
                    # tentativa simples com PhotoImage (pode falhar em alguns PNGs)
                    try:
                        self.bg_img_tk = tk.PhotoImage(file=BACKGROUND_PATH)
                        self.bg_label = tk.Label(self.root, image=self.bg_img_tk)
                        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    except tk.TclError:
                        # incompatível -> fallback color
                        print("⚠️ background.png não compatível com tk.PhotoImage. Usando cor sólida.")
                        self.root.configure(bg="#e8f5e9")
            except Exception as e:
                print("⚠️ Erro ao carregar background:", e)
                self.root.configure(bg="#e8f5e9")
        else:
            # sem imagem -> cor sólida
            self.root.configure(bg="#e8f5e9")

        # configura perguntas: (label emoji, texto, chave)
        self.questions = [
            ("💡", "Consumo de energia elétrica por mês (kWh)", "energia", 12, "Energia"),
            ("🚗", "Quantos km você percorre por semana?", "transporte", 52, "Transporte"),
            ("🍖", "Quantos kg de carne você consome por semana?", "carne", 52, "Alimentação"),
            ("✈️", "Quantas horas de voo você fez neste ano?", "aviao", 1, "Viagens"),
            ("🗑️", "Quantos kg de lixo você gera por semana?", "lixo", 52, "Resíduos")
        ]

        # começa
        self.show_start_screen()

    # ---------------------------
    # Funções para bg com Pillow
    # ---------------------------
    def _load_bg_with_pillow(self, path):
        try:
            img = Image.open(path)
            # cria label vazio inicialmente
            self.bg_img_original = img.convert("RGBA") if img.mode != "RGBA" else img
            self._update_bg_image_to_current_size()
        except Exception as e:
            print("⚠️ Erro Pillow ao abrir background:", e)
            self.root.configure(bg="#e8f5e9")

    def _update_bg_image_to_current_size(self):
        # calcula tamanho da janela (client area)
        w = max(self.root.winfo_width(), 200)
        h = max(self.root.winfo_height(), 200)
        try:
            resized = self.bg_img_original.resize((w, h), Image.LANCZOS)
            # se a imagem tiver alfa, converta para RGB com fundo branco leve -> evita problemas de blending
            if resized.mode in ("RGBA", "LA"):
                bg = Image.new("RGB", resized.size, (230, 245, 233))  # verde suave de fundo
                bg.paste(resized, mask=resized.split()[3])  # 3 = alpha
                final = bg
            else:
                final = resized.convert("RGB")
            self.bg_img_tk = ImageTk.PhotoImage(final)
            if self.bg_label is None:
                self.bg_label = tk.Label(self.root, image=self.bg_img_tk)
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                self.bg_label.configure(image=self.bg_img_tk)
                self.bg_label.image = self.bg_img_tk
        except Exception as e:
            print("⚠️ Falha ao redimensionar background:", e)
            self.root.configure(bg="#e8f5e9")

    def _on_root_configure(self, event):
        # atualiza bg apenas quando necessário (para evitar uso excessivo)
        if PIL_AVAILABLE and hasattr(self, "bg_img_original"):
            self._update_bg_image_to_current_size()

    # ---------------------------
    # UI: telas
    # ---------------------------
    def clear_current_frame(self):
        if self.current_frame is not None:
            try:
                self.current_frame.destroy()
            except Exception:
                pass
            self.current_frame = None

    def show_start_screen(self):
        self.clear_current_frame()
        self.pergunta_atual = 0
        frame = tk.Frame(self.root, bg="#ffffff", padx=18, pady=18)
        # centraliza com place para ficar sobre o background
        frame.place(relx=0.5, rely=0.5, anchor="center")
        self.current_frame = frame

        tk.Label(frame, text="🌿 Calculadora de Pegada de Carbono", font=("Arial", 18, "bold"),
                 bg="#ffffff", fg="#1b5e20").pack(pady=(6, 12))

        tk.Label(frame, text="Responda perguntas simples para estimar suas emissões anuais de CO₂e.",
                 bg="#ffffff", wraplength=520).pack(pady=(0, 12))

        tk.Button(frame, text="Começar", bg="#388e3c", fg="white", font=("Arial", 12, "bold"),
                  command=self.next_question).pack(pady=10)

    def next_question(self):
        # mostra próxima pergunta
        if self.pergunta_atual < len(self.questions):
            q = self.questions[self.pergunta_atual]
            self.show_question_screen(*q)
            self.pergunta_atual += 1
        else:
            self.show_result_screen()

    def show_question_screen(self, emoji, text, key, anual_multiplier, category_name):
        self.clear_current_frame()
        # usa a cor do category como fundo dessa tela (mantendo boa legibilidade)
        color = CATEGORY_COLORS.get(category_name, "#ffffff")
        # cria frame que cobre boa parte da janela (colocado centralizado)
        frame = tk.Frame(self.root, bg=color, padx=18, pady=18)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.7)
        self.current_frame = frame

        # título + ajuda (em branco/escuro conforme cor)
        # escolhemos texto em branco se a cor for escura (simples heurística)
        text_fg = "#ffffff" if self._is_color_dark(color) else "#222222"

        tk.Label(frame, text=f"{emoji} {text}", font=("Arial", 16, "bold"), bg=color, fg=text_fg).pack(pady=(6, 10))

        entry_var = tk.StringVar(value="0")
        entry = tk.Entry(frame, textvariable=entry_var, font=("Arial", 12))
        entry.pack(pady=(6, 12))
        entry.focus_set()

        # instrução e botão
        tk.Label(frame, text="Digite um número (valores decimais com ponto).", bg=color, fg=text_fg).pack()

        def salvar():
            s = entry_var.get().strip()
            if s == "":
                s = "0"
            if not is_nonneg_number(s):
                messagebox.showerror("Entrada inválida", "Digite um número válido (não-negativo).")
                return
            v = float(s)
            # armazena valor já anualizado (multiplicador passado)
            self.respostas[key] = v * anual_multiplier
            self.next_question()

        btn_frame = tk.Frame(frame, bg=color)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Próximo", bg="#ffffff", fg="#000", command=salvar).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancelar (Voltar ao início)", bg="#f44336", fg="white",
                  command=self.reset_quiz).pack(side="left", padx=6)

    def show_result_screen(self):
        self.clear_current_frame()
        frame = tk.Frame(self.root, bg="#ffffff", padx=18, pady=18)
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        self.current_frame = frame

        # calcula por categoria (em kg CO2e)
        categorias = {}
        total_kg = 0.0

        # energia (consumo mensal anualizado já na resposta)
        energia_kwh_ano = self.respostas.get("energia", 0.0)
        energia_kg = energia_kwh_ano * FACTORES["energia"]
        categorias["Energia"] = energia_kg
        total_kg += energia_kg

        # transporte (resposta já foi km/ano)
        transporte_tuple = self.respostas.get("transporte", 0.0)
        if isinstance(transporte_tuple, tuple):
            km_ano, tipo = transporte_tuple
        else:
            km_ano = self.respostas.get("transporte", 0.0)
            tipo = "carro"
        # se transporte info estiver apenas como número, assumimos carro (fator carro)
        if isinstance(FACTORES["transporte"], dict):
            transporte_fator = FACTORES["transporte"].get(tipo, list(FACTORES["transporte"].values())[0])
        else:
            transporte_fator = FACTORES["transporte"]
        transporte_kg = km_ano * transporte_fator
        categorias["Transporte"] = transporte_kg
        total_kg += transporte_kg

        # carne
        carne_kg_ano = self.respostas.get("carne", 0.0)
        carne_kg = carne_kg_ano * FACTORES["carne"]
        categorias["Alimentação"] = carne_kg
        total_kg += carne_kg

        # aviao
        voo_horas = self.respostas.get("aviao", 0.0)
        voo_kg = voo_horas * FACTORES["aviao"]
        categorias["Viagens"] = voo_kg
        total_kg += voo_kg

        # lixo (resposta anualizada)
        lixo_kg_ano = self.respostas.get("lixo", 0.0)
        lixo_kg = lixo_kg_ano * FACTORES["lixo"]
        categorias["Resíduos"] = lixo_kg
        total_kg += lixo_kg

        # proteção: se total 0 -> informa usuário
        if total_kg <= 0 or not math.isfinite(total_kg):
            messagebox.showinfo("Resultado", "As emissões calculadas são zero ou inválidas. Tente novamente.")
            self.reset_quiz()
            return

        toneladas = total_kg / 1000.0
        arvores = math.ceil(toneladas * 5.3)

        tk.Label(frame, text="🌍 Resultado Final", font=("Arial", 16, "bold"), bg="#ffffff", fg="#1b5e20").pack(pady=(6, 8))
        tk.Label(frame, text=f"Você emitiu aproximadamente {toneladas:.3f} toneladas de CO₂e por ano.", bg="#ffffff").pack()
        tk.Label(frame, text=f"Isto equivale a plantar ~{arvores} árvores.", bg="#ffffff").pack(pady=(0, 8))

        # custos de compensação
        preco_text = "Custo estimado para compensação:\n"
        for nome, preco in FACTORES.get("precos", {}).items():
            custo = toneladas * preco
            preco_text += f"• {nome}: R$ {custo:.2f}\n"
        tk.Label(frame, text=preco_text, bg="#ffffff", justify="left").pack(pady=(6, 8))

        btns = tk.Frame(frame, bg="#ffffff")
        btns.pack(pady=8)
        tk.Button(btns, text="Gerar Gráfico e Tabela (HTML)", bg="#4caf50", fg="white",
                  command=lambda: self.generate_html_report(categorias)).pack(side="left", padx=8)
        tk.Button(btns, text="Recalcular", bg="#f57c00", fg="white", command=self.reset_quiz).pack(side="left", padx=8)

    def reset_quiz(self):
        # limpa e volta à tela inicial
        self.respostas = {}
        self.pergunta_atual = 0
        self.show_start_screen()

    # ---------------------------
    # HTML: gera gráfico de barras verticais + tabela
    # ---------------------------
    def generate_html_report(self, categorias):
        total = sum(v for v in categorias.values() if isinstance(v, (int, float)) and v >= 0 and math.isfinite(v))
        if total <= 0:
            messagebox.showerror("Erro", "Dados inválidos para gerar relatório.")
            return

        # garante lista ordenada para manter consistência
        entries = list(categorias.items())

        # determina caminhos para background e icon no HTML - usa absolute file URL
        bg_url = ""
        icon_url = ""
        if os.path.exists(BACKGROUND_PATH):
            bg_url = f"file:///{os.path.abspath(BACKGROUND_PATH).replace(os.sep, '/')}"
        if os.path.exists(ICON_PATH):
            icon_url = f"file:///{os.path.abspath(ICON_PATH).replace(os.sep, '/')}"

        # constrói HTML
        html = [
            "<!doctype html>",
            "<html><head><meta charset='utf-8'><title>Relatório de Emissões</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 0; padding: 0; }",
        ]

        # background CSS (se disponível)
        if bg_url:
            html.append(f"body {{ background-image: url('{bg_url}'); background-size: cover; background-attachment: fixed; }}")
        else:
            html.append("body { background-color: #f5f7f6; }")

        html.append("""
        .container { background-color: rgba(255,255,255,0.95); max-width: 1000px; margin: 40px auto; padding: 20px; border-radius: 10px; }
        .chart { display:flex; justify-content:center; align-items:flex-end; height:320px; margin:20px 0; background-repeat:no-repeat; }
        .bar { width: 80px; margin: 0 12px; text-align:center; }
        .bar-rect { border-radius:6px 6px 0 0; transition: height .5s; }
        table { width:100%; border-collapse: collapse; margin-top: 18px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align:left; }
        th { background: #f2f2f2; }
        .color-box { width:24px; height:18px; display:inline-block; border-radius:4px; }
        """)

        # if icon present, add a subtle side-decoration using it
        if icon_url:
            html.append(f".chart {{ background-image: url('{icon_url}'); background-repeat: repeat-y; background-position: left right; background-size: 80px; }}")

        html.append("</style></head><body>")
        html.append("<div class='container'>")
        html.append("<h2>Distribuição das suas emissões de CO₂e</h2>")

        # chart
        html.append("<div class='chart'>")
        max_h = 260.0
        for i, (cat, val) in enumerate(entries):
            color = CATEGORY_COLORS.get(cat, "#777777")
            height = int((val / total) * max_h)
            html.append(f"<div class='bar'><div class='bar-rect' style='background:{color}; height:{height}px;' title='{cat}: {val:.1f} kg CO₂e'></div><div style='margin-top:6px;'>{cat}</div></div>")
        html.append("</div>")  # end chart

        # table header
        html.append("<table><thead><tr><th>Cor</th><th>Categoria</th><th>Emissão (kg CO₂e)</th><th>Percentual</th></tr></thead><tbody>")
        for cat, val in entries:
            color = CATEGORY_COLORS.get(cat, "#777777")
            perc = (val / total) * 100.0
            html.append(f"<tr><td><span class='color-box' style='background:{color};'></span></td><td>{cat}</td><td>{val:.1f}</td><td>{perc:.1f}%</td></tr>")
        html.append("</tbody></table>")

        # totals & footer
        toneladas = total / 1000.0
        html.append(f"<p style='margin-top:16px;'><strong>Total:</strong> {total:.2f} kg CO₂e = {toneladas:.3f} tCO₂e</p>")
        precos = FACTORES.get("precos", {})
        if precos:
            html.append("<p><strong>Estimativa de custo de compensação:</strong><br>")
            for nome, preco in precos.items():
                custo = toneladas * preco
                html.append(f"{nome}: R$ {custo:.2f}<br>")
            html.append("</p>")

        html.append("</div></body></html>")
        html_content = "\n".join(html)

        # escreve arquivo temporário e abre no navegador
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as f:
            f.write(html_content)
            webbrowser.open(f.name)

    # ---------------------------
    # helpers
    # ---------------------------
    def _is_color_dark(self, hex_color):
        """Heurística simples: retorna True se cor for escura (para escolher texto branco)."""
        try:
            c = hex_color.lstrip("#")
            r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
            # luminance formula (perceptual)
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            return lum < 140
        except Exception:
            return False

# ---------------------------
# Execução
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraCarbonoApp(root)
    root.mainloop()
