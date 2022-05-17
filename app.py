# LIBRARIES AND FLASK FRAMEWORK
from flask import Flask, render_template, request, send_file, redirect, session, g
import os
import pymysql
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF


app = Flask(__name__)
app.secret_key = "key"
plt.switch_backend('agg')


# FUNCTIONS
def grafico_a_barre(cattuale1, cattuale2, cattuale3, cfare1, cfare2, cfare3, username):
    labels = ['F1', 'F2', 'F3']
    Attuale = [cattuale1, cattuale2, cattuale3]
    Fareconsulenza = [cfare1, cfare2, cfare3]
    x = np.arange(len(labels))  # Label locations
    width = 0.25  # Width of the bars
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
    plt.savefig('static/img/'+username+'_graficobarre.png')


def grafico_a_torta(ctot_attuale, ctot_fare, username):
    fig, ax = plt.subplots(figsize=(8, 3), subplot_kw=dict(aspect="equal"))
    recipe = [(str(ctot_attuale)+"€ Costo attuale fornitore"),
              (str(ctot_fare)+"€ Costo Fareconsulenza"),
              (str(round((ctot_attuale-ctot_fare), 1))+"€ RISPARMIO")]
    data = [ctot_attuale, ctot_fare, (ctot_attuale-ctot_fare)]
    colors = ['red', 'orange', 'green']
    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40, colors=colors)
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(recipe[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                    horizontalalignment=horizontalalignment, **kw)

    plt.savefig('static/img/'+username+'_graficotorta.png')


def creare_pdf(nomecliente, mailcliente, nomeconsulente, numconsulente, mailconsulente,
               costo_totale_att, costo_totale_fare, tipologia, nominativo):
    pdf = FPDF()
    pdf.add_page()
    WIDTH = 210
    HEIGHT = 297
    pdf.image("static/img/top.jpg", 0, 0, WIDTH)
    pdf.image("static/img/bottom.jpg", 0, 270, WIDTH)
    pdf.image("static/img/"+g.utente+"_graficobarre.png", 5, 70, WIDTH/2-5)
    pdf.image("static/img/"+g.utente+"_graficotorta.png", HEIGHT/2-45, 70, WIDTH / 2 - 5)
    pdf.add_font('Arial', '', 'c:/windows/fonts/arial.ttf', uni=True)  # added line
    pdf.set_font('Arial', '', 12)
    moltiplicatore = 6

    if tipologia == 'mensile':
        moltiplicatore = 12

    pdf.multi_cell(0, 5, '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n'
                   + 'Gentile '+nominativo+' '
                   + str(nomecliente) + '\n' + '\n'
                   + 'In alto trova il dettaglio dei costi sostenuti per la Sua utenza che, in merito alla fattura analizzata le ha portato un costo della componente di €'
                   + str(costo_totale_att)+'.' + '\n' + '\n'
                   + 'Come potrà notare dal grafico, in caso avesse avuto il gestore da noi prospettato, a parità di consumi, avrebbe sostenuto un costo di €'
                   + str(costo_totale_fare)+' con conseguente beneficio di €'
                   + str(round((costo_totale_att-costo_totale_fare), 1))+'.' + '\n' + '\n' + 'Tale costo Le avrebbe consentito di risparmiare €'
                   + str(round(round(moltiplicatore*(costo_totale_att-costo_totale_fare)), 1))
                   + ' nell’ultimo anno! A questo si aggiunge una decrescita dei costi di iva che sono direttamente proporzionali all’imponibile dei costi generali.'
                   + '\n' + '\n' + 'Il Consulente a cui sono affidate le Sue utenze, è a Sua disposizione in NEL TEMPO per seguire i costi e tenerli SEMPRE aggiornati alle migliori condizioni di mercato.'
                   + '\n' + '\n' + '\n' + str(nomeconsulente) + '\n' + str(numconsulente) + '\n' + str(mailconsulente))

    pdf.output(r'static/'+g.utente+'confronto.pdf')
    os.remove("static/img/"+g.utente+"_graficobarre.png")
    os.remove("static/img/" + g.utente + "_graficotorta.png")
    # if mailcliente !='e-mail' and mailcliente != '':
    #    inviamail(mailcliente, nomecliente, nominativo)


# FLASK APP
@app.route('/')
def login():
    return render_template("login.html")


@app.before_request
def before_request():
    if "utente" in session:
        g.utente = session["utente"]
    else:
        g.utente = None


@app.route('/calcolo', methods=["POST", "GET"])
def index():
    try:
        con = pymysql.connect(
            host="localhost",
            user=str(str(request.form['login'])),
            password=str(str(request.form['password'])),
            database="fareconsulenzadb")
        cur = con.cursor()
        cur.execute(
            "select indice from utenti where username='"
            + str(request.form['login']) + "' and password = '"
            + str(request.form['password']) + "'")
        row = cur.fetchone()
        if row is None:
            return redirect("/")
        else:
            session["utente"] = row[0]
            return render_template("calcolo.html")
    except Exception:
        return redirect("/")


@app.route('/confronto', methods=["POST", "GET"])
def confronto():
    if g.utente:
        global costo_totale_attuale, costo_totale_fareconsulenza
        session["consumof1"] = round(float(request.form['consumo_f1']) * (1 + float(request.form['perdite_rete'])/100), 1)
        session["consumof2"] = round(float(request.form['consumo_f2']) * (1 + float(request.form['perdite_rete'])/100), 1)
        session["consumof3"] = round(float(request.form['consumo_f3']) * (1 + float(request.form['perdite_rete'])/100), 1)
        session["costo_totale_attuale_f1"] = round(float(request.form['costo_attuale_f1'])*session.get('consumof1', None), 1)
        session["costo_totale_attuale_f2"] = round(float(request.form['costo_attuale_f2'])*session.get('consumof2', None), 1)
        session["costo_totale_attuale_f3"] = round(float(request.form['costo_attuale_f3'])*session.get('consumof3', None), 1)
        session["costo_totale_fareconsulenza_f1"] = round(float(request.form['costo_fareconsulenza_f1'])*session.get('consumof1', None), 1)
        session["costo_totale_fareconsulenza_f2"] = round(float(request.form['costo_fareconsulenza_f2'])*session.get('consumof2', None), 1)
        session["costo_totale_fareconsulenza_f3"] = round(float(request.form['costo_fareconsulenza_f3'])*session.get('consumof3', None), 1)
        session["costo_totale_attuale"] = round(session.get('costo_totale_attuale_f1', None)+session.get('costo_totale_attuale_f2', None)+session.get('costo_totale_attuale_f3', None), 1)
        session["costo_totale_fareconsulenza"] = round(session.get('costo_totale_fareconsulenza_f1', None)+session.get('costo_totale_fareconsulenza_f2', None)+session.get('costo_totale_fareconsulenza_f3', None), 1)
        session["risparmio_euro_f1"] = round(session.get('costo_totale_attuale_f1', None)-session.get('costo_totale_fareconsulenza_f1', None), 1)
        session["risparmio_euro_f2"] = round(session.get('costo_totale_attuale_f2', None)-session.get('costo_totale_fareconsulenza_f2', None), 1)
        session["risparmio_euro_f3"] = round(session.get('costo_totale_attuale_f3', None)-session.get('costo_totale_fareconsulenza_f3', None), 1)
        session["risparmio_euro_totale"] = round(session.get('risparmio_euro_f1', None)+session.get('risparmio_euro_f2', None)+session.get('risparmio_euro_f3', None), 1)
        session["risparmio_percentuale_f1"] = round(100-(session.get('costo_totale_fareconsulenza_f1', None) * 100 / session.get('costo_totale_attuale_f1', None)), 1)
        session["risparmio_percentuale_f2"] = round(100-(session.get('costo_totale_fareconsulenza_f2', None) * 100 / session.get('costo_totale_attuale_f2', None)), 1)
        session["risparmio_percentuale_f3"] = round(100-(session.get('costo_totale_fareconsulenza_f3', None) * 100 / session.get('costo_totale_attuale_f3', None)), 1)
        session["risparmio_percentuale_totale"] = round(100-(session.get('costo_totale_fareconsulenza', None) * 100 / session.get('costo_totale_attuale', None)), 1)

        proccesso1 = multiprocessing.Process(target=grafico_a_barre, args=(session.get('costo_totale_attuale_f1', None),
                                                                           session.get('costo_totale_attuale_f2', None),
                                                                           session.get('costo_totale_attuale_f3', None),
                                                                           session.get('costo_totale_fareconsulenza_f1', None),
                                                                           session.get('costo_totale_fareconsulenza_f2', None),
                                                                           session.get('costo_totale_fareconsulenza_f3', None), g.utente))
        proccesso2 = multiprocessing.Process(target=grafico_a_torta, args=(session.get('costo_totale_attuale', None),
                                                                           session.get('costo_totale_fareconsulenza', None), g.utente))
        proccesso1.start()
        proccesso1.terminate()
        proccesso2.start()
        proccesso2.terminate()

        return render_template("confronto.html",
                               risparmio_euro_f1=session.get('risparmio_euro_f1', None),
                               risparmio_euro_f2=session.get('risparmio_euro_f2', None),
                               risparmio_euro_f3=session.get('risparmio_euro_f3', None),
                               risparmio_euro_totale=session.get('risparmio_euro_totale', None),
                               risparmio_percentuale_f1=session.get('risparmio_percentuale_f1', None),
                               risparmio_percentuale_f2=session.get('risparmio_percentuale_f2', None),
                               risparmio_percentuale_f3=session.get('risparmio_percentuale_f3', None),
                               risparmio_percentuale_totale=session.get('risparmio_percentuale_totale', None))
    else:
        return redirect("/")


@app.route('/dati', methods=["POST", "GET"])
def dati():
    if g.utente:
        return render_template("dati.html")
    else:
        return redirect("/")


@app.route('/scarica', methods=["POST", "GET"])
def scarica():
    if g.utente:
        nome_consulente = str(request.form['nome_cognome_consulente'])
        mail_consulente = str(request.form['mail_consulente'])
        cellulare_consulente = str(request.form['numero_consulente'])
        tipologia_cliente = str(request.form['nomenclatura'])
        nome_cliente = str(request.form['nome_cognome_cliente'])
        mail_cliente = str(request.form['mail_cliente'])
        cellulare_cliente = str(request.form['numero_cliente'])
        tipologia_contratto = str(request.form['tipologia'])
        creare_pdf(
            nome_cliente, mail_cliente, nome_consulente, cellulare_consulente, mail_consulente,
            session.get('costo_totale_attuale', None), session.get('costo_totale_fareconsulenza', None), tipologia_contratto, tipologia_cliente)
        return send_file(r'static/'+g.utente+'confronto.pdf', as_attachment=True)
    else:
        return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
