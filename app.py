from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "key"

def grafico_a_barre(cattuale1, cattuale2, cattuale3, cfare1, cfare2, cfare3):
    labels = ['F1', 'F2', 'F3']
    Attuale = [cattuale1, cattuale2, cattuale3]
    Fareconsulenza = [cfare1, cfare2, cfare3]
    x = np.arange(len(labels))  # the label locations
    width = 0.25  # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, Attuale, width, label='Attuale Fornitore', color="red")
    rects2 = ax.bar(x + width / 2, Fareconsulenza, width, label='Fare Consulenza', color="orange")
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Costo €')
    ax.set_title('Confronto costo fattura')
    ax.set_xticks(x, labels)
    ax.legend(bbox_to_anchor=(1.05, 1))
    ax.bar_label(rects1, padding=0)
    ax.bar_label(rects2, padding=0)
    fig.tight_layout()
    plt.savefig('static/graficobarre.png')

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
    grafico_a_barre(costo_totale_attuale_f1, costo_totale_attuale_f2, costo_totale_attuale_f3, costo_totale_fareconsulenza_f1,
                    costo_totale_fareconsulenza_f2, costo_totale_fareconsulenza_f3)


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



