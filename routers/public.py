from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    progetti_evidenza = db.query(models.Progetto)\
        .filter(models.Progetto.pubblicato == True)\
        .filter(models.Progetto.in_evidenza == True)\
        .order_by(models.Progetto.ordine)\
        .limit(5).all()
    articoli_recenti = db.query(models.Articolo)\
        .filter(models.Articolo.pubblicato == True)\
        .order_by(models.Articolo.creato_il.desc())\
        .limit(3).all()
    servizi_home = db.query(models.Servizio)\
        .filter(models.Servizio.attivo == True)\
        .order_by(models.Servizio.ordine)\
        .limit(6).all()
    hero_img = db.query(models.Impostazione)\
        .filter(models.Impostazione.chiave == "hero_image")\
        .first()

    return templates.TemplateResponse(
        request=request,
        name="public/home.html",
        context={
            "progetti": progetti_evidenza,
            "articoli": articoli_recenti,
            "servizi_home": servizi_home,
            "hero_image": hero_img.valore if hero_img else None
        }
    )


@router.get("/portfolio", response_class=HTMLResponse)
def portfolio(request: Request, db: Session = Depends(get_db)):
    progetti = db.query(models.Progetto)\
        .filter(models.Progetto.pubblicato == True)\
        .order_by(models.Progetto.ordine)\
        .all()
    categorie = db.query(models.Progetto.categoria)\
        .filter(models.Progetto.pubblicato == True)\
        .distinct().all()
    categorie = [c[0] for c in categorie if c[0]]
    return templates.TemplateResponse(
        request=request,
        name="public/portfolio.html",
        context={"progetti": progetti, "categorie": categorie}
    )


@router.get("/portfolio/{slug}", response_class=HTMLResponse)
def progetto_dettaglio(slug: str, request: Request, db: Session = Depends(get_db)):
    progetto = db.query(models.Progetto)\
        .filter(models.Progetto.slug == slug)\
        .filter(models.Progetto.pubblicato == True)\
        .first()
    if not progetto:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    altri = db.query(models.Progetto)\
        .filter(models.Progetto.pubblicato == True)\
        .filter(models.Progetto.id != progetto.id)\
        .limit(3).all()
    return templates.TemplateResponse(
        request=request,
        name="public/progetto.html",
        context={"progetto": progetto, "altri": altri}
    )


@router.get("/servizi", response_class=HTMLResponse)
def servizi(request: Request, db: Session = Depends(get_db)):
    servizi = db.query(models.Servizio)\
        .filter(models.Servizio.attivo == True)\
        .order_by(models.Servizio.ordine)\
        .all()
    return templates.TemplateResponse(
        request=request,
        name="public/servizi.html",
        context={"servizi": servizi}
    )


@router.get("/news", response_class=HTMLResponse)
def news(request: Request, db: Session = Depends(get_db)):
    articoli = db.query(models.Articolo)\
        .filter(models.Articolo.pubblicato == True)\
        .order_by(models.Articolo.creato_il.desc())\
        .all()
    return templates.TemplateResponse(
        request=request,
        name="public/news.html",
        context={"articoli": articoli}
    )


@router.get("/news/{slug}", response_class=HTMLResponse)
def articolo_dettaglio(slug: str, request: Request, db: Session = Depends(get_db)):
    articolo = db.query(models.Articolo)\
        .filter(models.Articolo.slug == slug)\
        .filter(models.Articolo.pubblicato == True)\
        .first()
    if not articolo:
        raise HTTPException(status_code=404, detail="Articolo non trovato")
    return templates.TemplateResponse(
        request=request,
        name="public/articolo.html",
        context={"articolo": articolo}
    )


@router.get("/contatti", response_class=HTMLResponse)
def contatti(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="public/contatti.html",
        context={}
    )


@router.post("/contatti", response_class=HTMLResponse)
def invia_messaggio(
    request: Request,
    nome: str = Form(...),
    cognome: str = Form(default=""),
    email: str = Form(...),
    tipo_progetto: str = Form(default=""),
    testo: str = Form(...),
    db: Session = Depends(get_db)
):
    if not nome or not email or not testo:
        return templates.TemplateResponse(
            request=request,
            name="public/contatti.html",
            context={"errore": "Compila tutti i campi obbligatori."}
        )

    messaggio = models.Messaggio(
        nome=nome,
        cognome=cognome,
        email=email,
        tipo_progetto=tipo_progetto,
        testo=testo
    )
    db.add(messaggio)
    db.commit()

    return templates.TemplateResponse(
        request=request,
        name="public/contatti.html",
        context={"successo": True}
    )