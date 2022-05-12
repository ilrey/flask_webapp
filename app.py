from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = "key"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/confronta', methods=["POST", "GET"])
def confronta():
    consumof1 = round(float(request.form['consumo_f1']) * (1 + float(request.form['perdite_rete'])/100), 1)
    consumof2 = round(float(request.form['consumo_f2']) * (1 + float(request.form['perdite_rete'])/100), 1)
    consumof3 = round(float(request.form['consumo_f3']) * (1 + float(request.form['perdite_rete'])/100), 1)
    costo_totale_attuale_f1 = round(float(request.form['costo_attuale_f1'])*consumof1, 1)
    costo_totale_attuale_f2 = round(float(request.form['costo_attuale_f2'])*consumof2, 1)
    costo_totale_attuale_f3 = round(float(request.form['costo_attuale_f3'])*consumof3, 1)
    costo_totale_fareconsulenza_f1 = round(float(request.form['costo_fareconsulenza_f1'])*consumof1, 1)
    costo_totale_fareconsulenza_f2 = round(float(request.form['costo_fareconsulenza_f2'])*consumof2, 1)
    costo_totale_fareconsulenza_f3 = round(float(request.form['costo_fareconsulenza_f3'])*consumof3, 1)
    costo_totale_attuale = round(costo_totale_attuale_f1+costo_totale_attuale_f2+costo_totale_attuale_f3, 1)
    costo_totale_fareconsulenza = round(costo_totale_fareconsulenza_f1+costo_totale_fareconsulenza_f2+costo_totale_fareconsulenza_f3, 1)
    risparmio_euro_f1 = round(costo_totale_attuale_f1-costo_totale_fareconsulenza_f1, 1)
    risparmio_euro_f2 = round(costo_totale_attuale_f2-costo_totale_fareconsulenza_f2, 1)
    risparmio_euro_f3 = round(costo_totale_attuale_f3-costo_totale_fareconsulenza_f3, 1)
    risparmio_euro_totale = round(risparmio_euro_f3+risparmio_euro_f2+risparmio_euro_f1, 1)
    risparmio_percentuale_f1 = round(100-(costo_totale_fareconsulenza_f1 * 100 / costo_totale_attuale_f1), 1)
    risparmio_percentuale_f2 = round(100-(costo_totale_fareconsulenza_f2 * 100 / costo_totale_attuale_f2), 1)
    risparmio_percentuale_f3 = round(100-(costo_totale_fareconsulenza_f3 * 100 / costo_totale_attuale_f3), 1)
    risparmio_percentuale_totale = round(100-(costo_totale_fareconsulenza * 100 / costo_totale_attuale), 1)


    return render_template("confronto.html",
                           risparmio_euro_f1=risparmio_euro_f1,
                           risparmio_euro_f2=risparmio_euro_f2,
                           risparmio_euro_f3=risparmio_euro_f3,
                           risparmio_euro_totale=risparmio_euro_totale,
                           risparmio_percentuale_f1=risparmio_percentuale_f1,
                           risparmio_percentuale_f2=risparmio_percentuale_f2,
                           risparmio_percentuale_f3=risparmio_percentuale_f3,
                           risparmio_percentuale_totale=risparmio_percentuale_totale)

if __name__ == '__main__':
    app.run()