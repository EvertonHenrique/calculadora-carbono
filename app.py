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



