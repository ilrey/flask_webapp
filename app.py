# LIBRARIES AND FLASK FRAMEWORK
from flask import Flask, render_template, request, redirect, session, g
import pymysql
import module
import multiprocessing

app = Flask(__name__)
app.secret_key = "key"


# FLASK APP
@app.route('/')
def login():
    session["consumof1"] = None
    if g.utente:
        return render_template("home.html")
    else:
        return render_template("login.html")


@app.before_request
def before_request():
    if "utente" in session:
        g.utente = session["utente"]
    else:
        g.utente = None


@app.route('/home', methods=["POST", "GET"])
def home():
    if g.utente:
        return render_template("home.html")
    else:
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
                return render_template("home.html")
        except Exception as e:
            print(e)
            return redirect("/")


@app.route('/pod', methods=["POST", "GET"])
def pod():
    if g.utente:
        return render_template("pod.html")
    else:
        return redirect("/")


@app.route('/calcolo', methods=["POST", "GET"])
def index():
    if g.utente:
        try:
            session["pod"] = int(request.form['numero_pod'])
            session["num_pod"] = 1
            print(session.get('pod', None))
            return render_template("calcolo.html", numero_fattura=session.get('pod', None) - session.get('pod', None) + 1)
        except Exception as e:
            print(e)
            return redirect("/pod")
    else:
        return redirect("/")


@app.route('/confronto', methods=["POST", "GET"])
def confronto():
    if g.utente:
        try:
            if session["consumof1"] is None:
                session["consumof1"] = round(float(request.form['consumo_f1']) * (1 + float(request.form['perdite_rete'])/100), 2)
                session["consumof2"] = round(float(request.form['consumo_f2']) * (1 + float(request.form['perdite_rete'])/100), 2)
                session["consumof3"] = round(float(request.form['consumo_f3']) * (1 + float(request.form['perdite_rete'])/100), 2)
                session["costo_totale_attuale_f1"] = round(float(request.form['costo_attuale_f1'])*session.get('consumof1', None), 2)
                session["costo_totale_attuale_f2"] = round(float(request.form['costo_attuale_f2'])*session.get('consumof2', None), 2)
                session["costo_totale_attuale_f3"] = round(float(request.form['costo_attuale_f3'])*session.get('consumof3', None), 2)
                session["costo_totale_fareconsulenza_f1"] = round(float(request.form['costo_fareconsulenza_f1'])*session.get('consumof1', None), 2)
                session["costo_totale_fareconsulenza_f2"] = round(float(request.form['costo_fareconsulenza_f2'])*session.get('consumof2', None), 2)
                session["costo_totale_fareconsulenza_f3"] = round(float(request.form['costo_fareconsulenza_f3'])*session.get('consumof3', None), 2)
                session["costo_totale_attuale"] = round(session.get('costo_totale_attuale_f1', None)+session.get('costo_totale_attuale_f2', None)+session.get('costo_totale_attuale_f3', None), 2)
                session["costo_totale_fareconsulenza"] = round(session.get('costo_totale_fareconsulenza_f1', None)+session.get('costo_totale_fareconsulenza_f2', None)+session.get('costo_totale_fareconsulenza_f3', None), 2)
                session["risparmio_euro_f1"] = round(session.get('costo_totale_attuale_f1', None)-session.get('costo_totale_fareconsulenza_f1', None), 2)
                session["risparmio_euro_f2"] = round(session.get('costo_totale_attuale_f2', None)-session.get('costo_totale_fareconsulenza_f2', None), 2)
                session["risparmio_euro_f3"] = round(session.get('costo_totale_attuale_f3', None)-session.get('costo_totale_fareconsulenza_f3', None), 2)
                session["risparmio_euro_totale"] = round(session.get('risparmio_euro_f1', None)+session.get('risparmio_euro_f2', None)+session.get('risparmio_euro_f3', None), 2)
                session["risparmio_percentuale_f1"] = round(100-(session.get('costo_totale_fareconsulenza_f1', None) * 100 / session.get('costo_totale_attuale_f1', None)), 1)
                session["risparmio_percentuale_f2"] = round(100-(session.get('costo_totale_fareconsulenza_f2', None) * 100 / session.get('costo_totale_attuale_f2', None)), 1)
                session["risparmio_percentuale_f3"] = round(100-(session.get('costo_totale_fareconsulenza_f3', None) * 100 / session.get('costo_totale_attuale_f3', None)), 1)
                session["risparmio_percentuale_totale"] = round(100-(session.get('costo_totale_fareconsulenza', None) * 100 / session.get('costo_totale_attuale', None)), 1)
            else:
                session["consumof1"] = round(float(request.form['consumo_f1']) * (1 + float(request.form['perdite_rete'])/100), 2)
                session["consumof2"] = round(float(request.form['consumo_f2']) * (1 + float(request.form['perdite_rete'])/100), 2)
                session["consumof3"] = round(float(request.form['consumo_f3']) * (1 + float(request.form['perdite_rete'])/100), 2)
                session["costo_totale_attuale_f1"] = session["costo_totale_attuale_f1"]+round(float(request.form['costo_attuale_f1'])*session.get('consumof1', None), 2)
                session["costo_totale_attuale_f2"] = session["costo_totale_attuale_f2"]+round(float(request.form['costo_attuale_f2'])*session.get('consumof2', None), 2)
                session["costo_totale_attuale_f3"] = session["costo_totale_attuale_f3"]+round(float(request.form['costo_attuale_f3'])*session.get('consumof3', None), 2)
                session["costo_totale_fareconsulenza_f1"] = session["costo_totale_fareconsulenza_f1"]+round(float(request.form['costo_fareconsulenza_f1'])*session.get('consumof1', None), 2)
                session["costo_totale_fareconsulenza_f2"] = session["costo_totale_fareconsulenza_f2"]+round(float(request.form['costo_fareconsulenza_f2'])*session.get('consumof2', None), 2)
                session["costo_totale_fareconsulenza_f3"] = session["costo_totale_fareconsulenza_f3"]+round(float(request.form['costo_fareconsulenza_f3'])*session.get('consumof3', None), 2)
                session["costo_totale_attuale"] = round(session.get('costo_totale_attuale_f1', None)+session.get('costo_totale_attuale_f2', None)+session.get('costo_totale_attuale_f3', None), 2)
                session["costo_totale_fareconsulenza"] = round(session.get('costo_totale_fareconsulenza_f1', None)+session.get('costo_totale_fareconsulenza_f2', None)+session.get('costo_totale_fareconsulenza_f3', None), 2)
                session["risparmio_euro_f1"] = round(session.get('costo_totale_attuale_f1', None)-session.get('costo_totale_fareconsulenza_f1', None), 2)
                session["risparmio_euro_f2"] = round(session.get('costo_totale_attuale_f2', None)-session.get('costo_totale_fareconsulenza_f2', None), 2)
                session["risparmio_euro_f3"] = round(session.get('costo_totale_attuale_f3', None)-session.get('costo_totale_fareconsulenza_f3', None), 2)
                session["risparmio_euro_totale"] = round(session.get('risparmio_euro_f1', None)+session.get('risparmio_euro_f2', None)+session.get('risparmio_euro_f3', None), 2)
                session["risparmio_percentuale_f1"] = round(100-(session.get('costo_totale_fareconsulenza_f1', None) * 100 / session.get('costo_totale_attuale_f1', None)), 1)
                session["risparmio_percentuale_f2"] = round(100-(session.get('costo_totale_fareconsulenza_f2', None) * 100 / session.get('costo_totale_attuale_f2', None)), 1)
                session["risparmio_percentuale_f3"] = round(100-(session.get('costo_totale_fareconsulenza_f3', None) * 100 / session.get('costo_totale_attuale_f3', None)), 1)
                session["risparmio_percentuale_totale"] = round(100-(session.get('costo_totale_fareconsulenza', None) * 100 / session.get('costo_totale_attuale', None)), 1)
            session["num_pod"] = session["num_pod"]+1
            session["pod"] = session["pod"]-1

            if session["pod"] != 0:
                return render_template("calcolo.html", numero_fattura=session.get('num_pod', None))
            else:
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
                proccesso1.daemon = True
                proccesso2.daemon = True
                proccesso1.start()
                proccesso2.start()
                session.pop('pod', None)
                session.pop('num_pod', None)
                return render_template("confronto.html",
                                       risparmio_euro_f1=session.get('risparmio_euro_f1', None),
                                       risparmio_euro_f2=session.get('risparmio_euro_f2', None),
                                       risparmio_euro_f3=session.get('risparmio_euro_f3', None),
                                       risparmio_euro_totale=session.get('risparmio_euro_totale', None),
                                       risparmio_percentuale_f1=session.get('risparmio_percentuale_f1', None),
                                       risparmio_percentuale_f2=session.get('risparmio_percentuale_f2', None),
                                       risparmio_percentuale_f3=session.get('risparmio_percentuale_f3', None),
                                       risparmio_percentuale_totale=session.get('risparmio_percentuale_totale', None))
        except Exception as e:
            print(e)
            return redirect("/calcolo")
    else:
        return redirect("/")


@app.route('/dati', methods=["POST", "GET"])
def dati():
    if g.utente:
        try:
            if session["risparmio_euro_f1"]:
                session.pop('risparmio_euro_f1', None)
                session.pop('risparmio_euro_f2', None)
                session.pop('risparmio_euro_f3', None)
                session.pop('risparmio_euro_totale', None)
                session.pop('risparmio_percentuale_f1', None)
                session.pop('risparmio_percentuale_f2', None)
                session.pop('risparmio_percentuale_f3', None)
                session.pop('risparmio_percentuale_totale', None)
                return render_template("dati.html")
            else:
                return redirect("/confronto")
        except Exception as e:
            print(e)
            return redirect("/confronto")
    else:
        return redirect("/")


@app.route('/scarica', methods=["POST", "GET"])
def scarica():
    if g.utente:
        try:
            mail_cliente = str(request.form['mail_cliente'])
            cellulare_cliente = str(request.form['numero_cliente'])
            module.creare_pdf(
                str(request.form['nome_cognome_cliente']), str(request.form['nome_cognome_consulente']), str(request.form['numero_consulente']), str(request.form['mail_consulente']),
                session.get('costo_totale_attuale', None), session.get('costo_totale_fareconsulenza', None), str(request.form['tipologia']), str(request.form['nomenclatura']), g.utente)
            session.pop('costo_totale_attuale', None)
            session.pop('costo_totale_fareconsulenza', None)
            if mail_cliente:
                module.send_mail(mail_cliente, str(request.form['nome_cognome_cliente']), str(request.form['nomenclatura']), g.utente)
            return render_template('download.html', file='../static/'+g.utente+'confronto.pdf')
        except Exception as e:
            print(e)
            return redirect("/dati")
    else:
        return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
