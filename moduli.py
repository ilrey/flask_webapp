import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

plt.switch_backend('agg')


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
               costo_totale_att, costo_totale_fare, tipologia, nominativo, username):
    pdf = FPDF()
    pdf.add_page()
    WIDTH = 210
    HEIGHT = 297
    pdf.image("static/img/top.jpg", 0, 0, WIDTH)
    pdf.image("static/img/bottom.jpg", 0, 270, WIDTH)
    pdf.image("static/img/"+username+"_graficobarre.png", 5, 70, WIDTH/2-5)
    pdf.image("static/img/"+username+"_graficotorta.png", HEIGHT/2-45, 70, WIDTH / 2 - 5)
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

    pdf.output(r'static/'+username+'confronto.pdf')
    os.remove("static/img/"+username+"_graficobarre.png")
    os.remove("static/img/"+username+"_graficotorta.png")
    # if mailcliente !='e-mail' and mailcliente != '':
    #    inviamail(mailcliente, nomecliente, nominativo)
