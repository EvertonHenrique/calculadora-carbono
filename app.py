
from flask import Flask, render_template, request, jsonify
import json, math
from flask import Flask, render_template, url_for

site = Flask(__name__)

@site.route('/')
def index():
    return render_template("index.html", nome='Inicio')
@site.route('/mercados')
def mercados():
    return render_template("mercados.html", nome='Mercados de Carbono')

@site.route('/metodologias')
def metodologias():
    return render_template("metodologias.html", nome='Metodologias de Cálculo de Emissões de CO2')

@site.route('/creditos')
def creditos():
    return render_template("creditos.html", nome='Créditos de Carbono')

# Executar os comandos
if __name__ == '__main__':
    site.run(debug=True)

# Carrega os fatores do arquivo JSON
with open("factors.json", "r", encoding="utf-8") as f:
    fatores = json.load(f)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/mercadoDeCarbono')
def mercadoDeCarbono():
    return render_template('mercadoDeCarbono.html')

@app.route('/principiosBasicosCB')
def principiosBasicosCB():
    return render_template('principiosBasicosCB.html')

@app.route('/emissoes')
def emissoes():
    return render_template('emissoes.html')


@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json

    # Recebe as respostas
    energia = float(data.get("energia", 0))
    km = float(data.get("km", 0))
    tipo = data.get("tipo", "carro")
    carne = float(data.get("carne", 0))
    voo = float(data.get("aviao", 0))
    lixo = float(data.get("lixo", 0))

    # Calcula total em kg de CO2e
    total = (
        energia * fatores["energia"]["fator"] +
        km * fatores["transporte"][tipo] +
        carne * fatores["carne"]["fator"] +
        voo * fatores["aviao"]["fator"] +
        lixo * fatores["lixo"]["fator"]
    )

    toneladas = total / 1000
    arvores = math.ceil(toneladas * 5.3)

    categorias = {
        "Energia": energia * fatores["energia"]["fator"],
        "Transporte": km * fatores["transporte"][tipo],
        "Alimentação": carne * fatores["carne"]["fator"],
        "Viagens": voo * fatores["aviao"]["fator"],
        "Resíduos": lixo * fatores["lixo"]["fator"]
    }

    precos = fatores["precos"]
    compensacoes = {nome: toneladas * preco for nome, preco in precos.items()}

    return jsonify({
        "total_toneladas": round(toneladas, 2),
        "arvores": arvores,
        "categorias": categorias,
        "compensacoes": compensacoes
    })


if __name__ == '__main__':
    app.run(debug=True)

