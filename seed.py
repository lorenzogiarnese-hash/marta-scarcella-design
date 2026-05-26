from database import SessionLocal, engine
from models import Base, Utente, Servizio, Progetto, Articolo
from auth import hash_password
from config import settings

Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()

    # Admin
    esistente = db.query(Utente).filter(Utente.email == settings.ADMIN_EMAIL).first()
    if not esistente:
        admin = Utente(
            email=settings.ADMIN_EMAIL,
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_admin=True
        )
        db.add(admin)
        print(f"✓ Admin creato: {settings.ADMIN_EMAIL}")
    else:
        print(f"✓ Admin già esistente")

    # Servizi
    if db.query(Servizio).count() == 0:
        servizi = [
            Servizio(numero="01", titolo="Progettazione d'interni", ordine=1,
                descrizione="Dalla concept al progetto esecutivo, curiamo ogni dettaglio della composizione spaziale e dell'identità visiva degli ambienti."),
            Servizio(numero="02", titolo="Consulenza e styling", ordine=2,
                descrizione="Sessioni di consulenza personalizzate per definire palette cromatiche, materiali e arredi in armonia con il tuo stile di vita."),
            Servizio(numero="03", titolo="Ristrutturazione", ordine=3,
                descrizione="Direzione lavori e coordinamento di artigiani e fornitori selezionati per garantire qualità e rispetto dei tempi."),
            Servizio(numero="04", titolo="Contract & hospitality", ordine=4,
                descrizione="Progettazione su scala contract per hotel, ristoranti, showroom e spazi commerciali con approccio sartoriale."),
            Servizio(numero="05", titolo="Render 3D e visualizzazioni", ordine=5,
                descrizione="Visualizzazioni fotorealistiche per esplorare il progetto prima della realizzazione, con massima accuratezza materica."),
            Servizio(numero="06", titolo="Home staging", ordine=6,
                descrizione="Valorizzazione degli spazi per la vendita o la locazione, con allestimenti che esaltano le potenzialità di ogni immobile."),
        ]
        db.add_all(servizi)
        print("✓ Servizi creati")

    # Progetti demo
    if db.query(Progetto).count() == 0:
        progetti = [
            Progetto(
                titolo="Villa Contemporanea",
                slug="villa-contemporanea",
                categoria="Residenziale",
                location="Milano",
                anno=2024,
                descrizione_breve="Una villa su tre livelli che fonde materiali naturali e linee contemporanee.",
                descrizione="Un progetto residenziale di ampio respiro sviluppato su tre livelli. La sfida principale era integrare il paesaggio esterno con gli spazi interni attraverso grandi vetrate e l'uso sapiente di materiali naturali come il travertino e il legno di rovere. Il risultato è un'abitazione che dialoga costantemente con il verde circostante, mantenendo al contempo una forte identità contemporanea.",
                in_evidenza=True,
                ordine=1,
                pubblicato=True
            ),
            Progetto(
                titolo="Loft Industriale Navigli",
                slug="loft-industriale-navigli",
                categoria="Residenziale",
                location="Milano",
                anno=2023,
                descrizione_breve="Un ex spazio produttivo trasformato in loft abitativo di 180 mq.",
                descrizione="La ristrutturazione di questo loft ai Navigli ha richiesto un approccio attento alla conservazione degli elementi originali — travi in ferro, pavimenti in cemento levigato, mattoni a vista — integrandoli con arredi contemporanei selezionati. Il risultato è uno spazio che racconta la sua storia industriale attraverso il filtro di un'estetica raffinata.",
                in_evidenza=True,
                ordine=2,
                pubblicato=True
            ),
            Progetto(
                titolo="Studio Legale Centrale",
                slug="studio-legale-centrale",
                categoria="Contract",
                location="Roma",
                anno=2023,
                descrizione_breve="Progettazione di uno studio professionale su 400 mq nel centro di Roma.",
                descrizione="Un ambiente professionale che doveva comunicare autorevolezza e accoglienza allo stesso tempo. Abbiamo scelto una palette cromatica neutra e sofisticata — grigio caldo, panna e ottone — declinata su boiserie in legno laccato, pavimenti in marmo Calacatta e arredi su misura. Gli spazi di rappresentanza sono stati distinti da quelli operativi mantenendo una coerenza visiva totale.",
                in_evidenza=True,
                ordine=3,
                pubblicato=True
            ),
            Progetto(
                titolo="Boutique Hotel Oltrarno",
                slug="boutique-hotel-oltrarno",
                categoria="Hospitality",
                location="Firenze",
                anno=2022,
                descrizione_breve="12 camere e spazi comuni per un boutique hotel nel cuore di Firenze.",
                descrizione="Un progetto hospitality che interpreta il DNA della Firenze artigiana attraverso un linguaggio contemporaneo. Ogni camera è concepita come un'installazione autonoma, con tessuti prodotti da botteghe locali, ceramiche di artisti emergenti e un sistema di illuminazione scenografico. Gli spazi comuni giocano su soffitti a volta originali del XV secolo in dialogo con opere d'arte contemporanea.",
                in_evidenza=True,
                ordine=4,
                pubblicato=True
            ),
            Progetto(
                titolo="Penthouse Vista Lago",
                slug="penthouse-vista-lago",
                categoria="Residenziale",
                location="Como",
                anno=2024,
                descrizione_breve="Attico con terrazza panoramica sul lago di Como, 220 mq.",
                descrizione="Un progetto che aveva come unico punto di partenza la vista: il lago di Como in tutta la sua estensione. Ogni scelta progettuale — dalla disposizione degli ambienti alla selezione dei materiali, dai colori alle altezze dei mobili — è stata subordinata alla relazione visiva con il paesaggio. Il risultato è uno spazio che scompare davanti alla natura, lasciando che sia il lago il vero protagonista.",
                in_evidenza=True,
                ordine=5,
                pubblicato=True
            ),
        ]
        db.add_all(progetti)
        print("✓ Progetti demo creati")

    # Articoli demo
    if db.query(Articolo).count() == 0:
        articoli = [
            Articolo(
                titolo="Il ritorno del Wabi-Sabi nel design contemporaneo",
                slug="wabi-sabi-design-contemporaneo",
                tag="Tendenze",
                anteprima="Come la filosofia giapponese della bellezza imperfetta sta influenzando il design d'interni europeo.",
                contenuto="""<p>Il Wabi-Sabi, la filosofia estetica giapponese che trova bellezza nell'imperfezione e nella transitorietà, sta vivendo una nuova stagione di interesse nel design d'interni contemporaneo europeo.</p>

<p>Non si tratta di una moda passeggera, ma di una risposta culturale profonda alla stanchezza verso l'estetica della perfezione digitale che ha dominato l'ultimo decennio. Superfici che mostrano il tempo trascorso, materiali che invecchiano con grazia, oggetti che portano i segni dell'uso: questi sono i nuovi lussi.</p>

<p>Nei progetti che seguiamo, questo si traduce in scelte concrete: intonaci a calce con finiture irregolari, ceramiche con imperfezioni deliberate, legni non trattati che cambieranno nel tempo, tessuti naturali che si deformano e si ammorbidiscono con l'uso.</p>

<p>La sfida per il designer è trovare l'equilibrio tra l'estetica dell'imperfezione e la funzionalità degli spazi. Un pavimento in cemento levigato che mostra le bolle è poesia visiva, ma deve anche essere pratico da pulire e confortevole da calpestare.</p>""",
                pubblicato=True
            ),
            Articolo(
                titolo="Case study: la ristrutturazione del loft ai Navigli",
                slug="case-study-loft-navigli",
                tag="Progetto",
                anteprima="Un percorso di sei mesi per trasformare uno spazio industriale in un'abitazione contemporanea.",
                contenuto="""<p>Quando i nostri clienti ci hanno mostrato per la prima volta questo spazio ai Navigli, abbiamo visto subito il potenziale nascosto sotto anni di utilizzo industriale: travi in ferro originali, pavimenti in cemento, soffitti a quattro metri e mezzo.</p>

<p>La sfida era duplice: preservare l'anima industriale dello spazio, che era esattamente ciò che i clienti amavano, e trasformarlo in un'abitazione confortevole per una famiglia con due bambini.</p>

<p>La soluzione è arrivata attraverso il concetto di "stratificazione temporale": ogni intervento nuovo è chiaramente distinguibile dall'esistente, senza tentare di imitarlo. Le partizioni in vetro e ferro nero creano nuovi ambienti senza nascondere la struttura originale. I pavimenti in rovere naturale dialogano con il cemento conservato nelle zone di passaggio.</p>

<p>Il risultato, dopo sei mesi di lavoro con artigiani locali selezionati, è uno spazio che racconta due storie contemporaneamente: quella industriale di Milano e quella contemporanea di una famiglia che ha scelto di abitare la città in modo non convenzionale.</p>""",
                pubblicato=True
            ),
            Articolo(
                titolo="Travertino e calcestruzzo: un dialogo inaspettato",
                slug="travertino-calcestruzzo-dialogo",
                tag="Materiali",
                anteprima="Esplorare la combinazione tra materiali naturali e industriali per superfici di carattere.",
                contenuto="""<p>Tra i materiali che più ci affascinano in questo momento c'è il confronto tra il travertino — con la sua storia millenaria, le sue venature, le sue cavità naturali — e il calcestruzzo a vista, figlio del Novecento industriale.</p>

<p>Apparentemente opposti, questi due materiali condividono una caratteristica fondamentale: l'onestà. Entrambi mostrano apertamente ciò che sono, senza pretese di essere qualcos'altro. Il travertino mostra i fossili, le bolle, le imperfezioni di milioni di anni. Il calcestruzzo mostra le casseforme, le bolle d'aria, i giunti.</p>

<p>In un recente progetto a Milano, abbiamo accostato un pavimento in travertino Navona non levigato a pareti in calcestruzzo pigmentato color terra. Il risultato è stato sorprendente: i due materiali sembravano fatti per stare insieme, come se avessero sempre saputo che un giorno si sarebbero incontrati.</p>

<p>Il segreto dell'accostamento è la palette cromatica: entrambi i materiali vivono nel range dei beige, ocra e grigi caldi. Non si combattono mai, si completano.</p>""",
                pubblicato=True
            ),
        ]
        db.add_all(articoli)
        print("✓ Articoli demo creati")

    db.commit()
    db.close()
    print("✓ Seed completato")

if __name__ == "__main__":
    seed()