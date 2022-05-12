#LIBRARIES AND FLASK FRAMEWORK
from flask import Flask, render_template, request, redirect, send_file
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF, HTMLMixin

app = Flask(__name__)
app.secret_key = "key"
costo_totale_attuale = None
costo_totale_fareconsulenza = None

#FUNCTIONS
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
    plt.savefig('static/img/graficobarre.png')

def grafico_a_torta(ctot_attuale, ctot_fare):
    fig, ax = plt.subplots(figsize=(8, 3), subplot_kw=dict(aspect="equal"))
    recipe = [(str(ctot_attuale)+"€ Costo attuale fornitore"),
              (str(ctot_fare)+"€ Costo Fareconsulenza"),
              (str(round((ctot_attuale-ctot_fare), 1))+"€ RISPARMIO")]
    data = [ctot_attuale, ctot_fare, (ctot_attuale-ctot_fare)]
    colors = ['red', 'orange', 'green']
    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40, colors=colors)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(recipe[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                    horizontalalignment=horizontalalignment, **kw)
    plt.savefig('static/img/graficotorta.png')

def creare_pdf(nomecliente, mailcliente, nomeconsulente, numconsulente, mailconsulente, costo_totale_attuale, costo_totale_fare, tipologia, nominativo):
    pdf= FPDF()
    pdf.add_page()
    WIDTH=210
    HEIGHT=297
    pdf.image("static/img/top.jpg", 0, 0, WIDTH)
    pdf.image("static/img/bottom.jpg", 0, 270, WIDTH)
    pdf.image("static/img/graficobarre.png", 5, 70, WIDTH/2-5)
    pdf.image("static/img/graficotorta.png", HEIGHT/2-45, 70, WIDTH /2 - 5)
    pdf.add_font('Arial', '', 'c:/windows/fonts/arial.ttf', uni=True)  # added line
    pdf.set_font('Arial', '', 12)

    moltiplicatore = 6
    if tipologia == 'mensile':
        moltiplicatore = 12

    pdf.multi_cell(0, 5, '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n'
                   + 'Gentile '+nominativo+' '
                   + str(nomecliente) + '\n' + '\n'
                   + 'In alto trova il dettaglio dei costi sostenuti per la Sua utenza che, in merito alla fattura analizzata le ha portato un costo della componente di €'
                   + str(costo_totale_attuale)+'.' + '\n' + '\n'
                   + 'Come potrà notare dal grafico, in caso avesse avuto il gestore da noi prospettato, a parità di consumi, avrebbe sostenuto un costo di €'
                   + str(costo_totale_fare)+' con conseguente beneficio di €'
                   + str(round((costo_totale_attuale-costo_totale_fare), 1))+'.' + '\n' + '\n' + 'Tale costo Le avrebbe consentito di risparmiare €'
                   + str(round(round(moltiplicatore*(costo_totale_attuale-costo_totale_fare)), 1))
                   + ' nell’ultimo anno! A questo si aggiunge una decrescita dei costi di iva che sono direttamente proporzionali all’imponibile dei costi generali.'
                   + '\n' + '\n' + 'Il Consulente a cui sono affidate le Sue utenze, è a Sua disposizione in NEL TEMPO per seguire i costi e tenerli SEMPRE aggiornati alle migliori condizioni di mercato.'
                   + '\n' + '\n' + '\n' + str(nomeconsulente) + '\n' + str(numconsulente) + '\n' + str(mailconsulente))

    pdf.output(r'static/confronto.pdf')
    #if mailcliente !='e-mail' and mailcliente != '':
    #    inviamail(mailcliente, nomecliente, nominativo)

#FLASK APP
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/confronta', methods=["POST", "GET"])
def confronta():
    global costo_totale_attuale, costo_totale_fareconsulenza
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

    grafico_a_torta(costo_totale_attuale, costo_totale_fareconsulenza)

    return render_template("confronto.html",
                           risparmio_euro_f1=risparmio_euro_f1,
                           risparmio_euro_f2=risparmio_euro_f2,
                           risparmio_euro_f3=risparmio_euro_f3,
                           risparmio_euro_totale=risparmio_euro_totale,
                           risparmio_percentuale_f1=risparmio_percentuale_f1,
                           risparmio_percentuale_f2=risparmio_percentuale_f2,
                           risparmio_percentuale_f3=risparmio_percentuale_f3,
                           risparmio_percentuale_totale=risparmio_percentuale_totale)

@app.route('/confronto/dati', methods=["POST", "GET"])
def dati():
    return render_template("dati.html")

@app.route('/confronto/dati/scarica', methods=["POST", "GET"])
def scarica():
    nome_consulente = str(request.form['nome_cognome_consulente'])
    mail_consulente = str(request.form['mail_consulente'])
    cellulare_consulente = str(request.form['numero_consulente'])
    tipologia_cliente = str(request.form['nomenclatura'])
    nome_cliente = str(request.form['nome_cognome_cliente'])
    mail_cliente = str(request.form['mail_cliente'])
    cellulare_cliente = str(request.form['numero_cliente'])
    tipologia_contratto = str(request.form['tipologia'])
    creare_pdf(nome_cliente, mail_cliente, nome_consulente, cellulare_consulente, mail_consulente,
               costo_totale_attuale, costo_totale_fareconsulenza, tipologia_contratto, tipologia_cliente)
    return send_file(r'static/confronto.pdf', as_attachment = True)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')



