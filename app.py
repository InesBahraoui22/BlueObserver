from flask import Flask, render_template

# Crée l'application Flask
app = Flask(__name__)

# Route pour la page d'accueil
@app.route("/")
def home():
    return render_template("index.html")

# Lancer le serveur
if __name__ == "__main__":
    app.run(debug=True)
