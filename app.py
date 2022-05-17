# LIBRARIES AND FLASK FRAMEWORK
from flask import Flask, render_template, request, send_file, redirect, session, g
import pymysql
import module
import multiprocessing

app = Flask(__name__)
app.secret_key = "key"


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

        proccesso1 = multiprocessing.Process(target=module.grafico_a_barre, args=(session.get('costo_totale_attuale_f1', None),
                                                                                   session.get('costo_totale_attuale_f2', None),
                                                                                   session.get('costo_totale_attuale_f3', None),
                                                                                   session.get('costo_totale_fareconsulenza_f1', None),
                                                                                   session.get('costo_totale_fareconsulenza_f2', None),
                                                                                   session.get('costo_totale_fareconsulenza_f3', None),
                                                                                   g.utente))
        proccesso2 = multiprocessing.Process(target=module.grafico_a_torta, args=(session.get('costo_totale_attuale', None),
                                                                                   session.get('costo_totale_fareconsulenza', None),
                                                                                   g.utente))
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
        module.creare_pdf(
            nome_cliente, mail_cliente, nome_consulente, cellulare_consulente, mail_consulente,
            session.get('costo_totale_attuale', None), session.get('costo_totale_fareconsulenza', None), tipologia_contratto, tipologia_cliente, g.utente)
        return send_file(r'static/'+g.utente+'confronto.pdf', as_attachment=True)
    else:
        return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
