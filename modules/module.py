# LIBRARIES
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

plt.switch_backend('agg')


# PIE CHART FUNCTION
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


# BAR CHART FUNCTION
def grafico_a_torta(ctot_attuale, ctot_fare, username):
    fig, ax = plt.subplots(figsize=(8, 3), subplot_kw=dict(aspect="equal"))
    recipe = [(str(ctot_attuale)+"€ Costo attuale fornitore"),
              (str(ctot_fare)+"€ Costo Fareconsulenza"),
              (str(round((ctot_attuale-ctot_fare), 2))+"€ RISPARMIO")]
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


# PDF CREATION FUNCTION
def creare_pdf(nomecliente, nomeconsulente, numconsulente, mailconsulente,
               costo_totale_att, costo_totale_fare, costo_totale_attuale, nominativo, username):
    pdf = FPDF()
    pdf.add_page()
    WIDTH = 210
    HEIGHT = 297
    pdf.image("static/img/top.jpg", 0, 0, WIDTH)
    pdf.image("static/img/bottom.jpg", 0, 270, WIDTH)
    pdf.image("static/img/"+username+"_graficobarre.png", 5, 70, WIDTH/2-5)
    pdf.image("static/img/"+username+"_graficotorta.png", HEIGHT/2-45, 70, WIDTH / 2 - 5)
    pdf.add_font('Arial', '', r'./static/fonts/arial.ttf', uni=True)
    pdf.add_font('Arial Grassetto', '', r'./static/fonts/arialbd.ttf', uni=True)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 5, '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n' + '\n'
                   + 'Gentile '+nominativo+' ' + str(nomecliente) + '\n' + '\n'
                   + 'In alto trova il dettaglio dei costi sostenuti per la Sua utenza che, in merito alla fattura analizzata le ha portato un costo della componente di')
    pdf.set_xy(pdf.get_x()+77, pdf.get_y()-5)
    pdf.set_text_color(255, 0, 0)  # ROSSO
    pdf.multi_cell(0, 5, '€' + str(costo_totale_att) + '\n' + '\n', align='J')
    pdf.set_text_color(0, 0, 0)  # NERO
    pdf.multi_cell(0, 5, 'Come potrà notare dal grafico, in caso avesse avuto il gestore da noi prospettato, a parità di consumi, avrebbe sostenuto un costo di ')
    pdf.set_xy(pdf.get_x() + 77, pdf.get_y() - 5)
    pdf.set_text_color(255, 140, 0)  # ARANCIONE
    pdf.multi_cell(0, 5, '€' + str(costo_totale_fare))
    lunghezza = len(str(costo_totale_fare))
    if lunghezza == 1:
        setting = 84
    elif lunghezza == 2:
        setting = 86
    elif lunghezza == 3:
        setting = 88.5
    elif lunghezza == 4:
        setting = 90.5
    elif lunghezza == 5:
        setting = 93.5
    elif lunghezza == 6:
        setting = 95.5
    else:
        setting = 95.5 + lunghezza
    pdf.set_xy(pdf.get_x() + setting, pdf.get_y() - 5)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, 'con conseguente beneficio di')
    pdf.set_xy(pdf.get_x() + setting+57, pdf.get_y() - 5)
    pdf.set_text_color(34, 139, 34)  # VERDE
    pdf.multi_cell(0, 5, '€'+str(round((costo_totale_att-costo_totale_fare), 1))+ '\n' + '\n')
    pdf.set_text_color(0, 0, 0)  # NERO
    pdf.multi_cell(0, 5, 'Tale costo Le avrebbe consentito di risparmiare')
    pdf.set_xy(pdf.get_x() + 91, pdf.get_y() - 5)
    pdf.set_text_color(34, 139, 34)  # VERDE
    pdf.multi_cell(0, 5, '€'+costo_totale_attuale)
    lunghezza = len(costo_totale_attuale)
    if lunghezza == 1:
        setting = 97.5
    elif lunghezza == 2:
        setting = 99.5
    elif lunghezza == 3:
        setting = 102.5
    elif lunghezza == 4:
        setting = 104.5
    elif lunghezza == 5:
        setting = 106.5
    elif lunghezza == 6:
        setting = 108.5
    else:
        setting = 108.5 + lunghezza
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(pdf.get_x() + setting, pdf.get_y() - 5)
    pdf.multi_cell(0, 5, 'nell’ultimo anno!')
    pdf.multi_cell(0, 5, 'A questo si aggiunge una decrescita dei costi di iva che sono direttamente proporzionali all’imponibile dei costi generali.'
                   + '\n' + '\n' + 'Il Consulente a cui sono affidate le Sue utenze, è a Sua disposizione')
    pdf.set_font('Arial Grassetto', '', 12)
    pdf.set_xy(140.5, pdf.get_y() - 5)
    pdf.multi_cell(0, 5, 'NEL TEMPO')
    pdf.set_font('Arial', '', 12)
    pdf.set_xy(167, pdf.get_y() - 5)
    pdf.multi_cell(0, 5, 'per seguire i')
    pdf.multi_cell(0, 5, 'costi e tenerli')
    pdf.set_font('Arial Grassetto', '', 12)
    pdf.set_xy(36, pdf.get_y() - 5)
    pdf.multi_cell(0, 5, 'SEMPRE')
    pdf.set_font('Arial', '', 12)
    pdf.set_xy(55, pdf.get_y() - 5)
    pdf.multi_cell(0, 5, 'aggiornati alle migliori condizioni di mercato.' + '\n' + '\n' + '\n')
    pdf.multi_cell(0, 5, str(nomeconsulente) + '\n' + str(numconsulente) + '\n' + str(mailconsulente))

    pdf.output(r'static/'+username+'confronto.pdf')


# MAIL SENDER FUNCTION
def send_mail(mailcliente, nomecliente, nomenclatura, username):
    body = 'Gentile '+str(nomenclatura)+', '+str(nomecliente)+' come da lei richiesto alleghiamo il confronto delle sue utenze'
    message = MIMEMultipart()
    message['From'] = 'inviodocumenti.fareconsulenza@gmail.com'
    message['To'] = mailcliente
    message['Subject'] = 'Comparazioni costi fattura'
    message.attach(MIMEText(body, 'plain'))
    pdfname = r'static/'+username+'confronto.pdf'
    binary_pdf = open(pdfname, 'rb')
    payload = MIMEBase('application', 'octate-stream', Name='confronto.pdf')
    payload.set_payload(binary_pdf.read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=pdfname)
    message.attach(payload)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login('inviodocumenti.fareconsulenza@gmail.com', 'PASSWORD')
    session.sendmail('inviodocumenti.fareconsulenza@gmail.com', mailcliente, message.as_string())
    session.quit()
    print('Mail Sent')
