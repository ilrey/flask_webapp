from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "key"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/confronta', methods=["POST", "GET"])
def confronta():
    consumo=request.form['consumo_f1']
    print(str(consumo))
    return render_template("confronto.html")

if __name__ == '__main__':
    app.run()