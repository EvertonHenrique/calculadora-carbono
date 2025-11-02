from flask import Flask, render_template
from quiz_interface import quiz_interface
site = Flask(__name__)

@site.route("/")
def index():
    return render_template("index.html")
@site.route("/creditos")
def creditos():
    return render_template("creditos.html")

@site.route("/metodologias")
def metodologias():
    return render_template("metodologias.html")

@site.route("/mercados")
def mercados():
    return render_template("mercados.html")


if __name__ == '__main__':
    site.run(debug=True)