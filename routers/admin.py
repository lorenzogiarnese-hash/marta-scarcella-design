import os
import uuid
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import require_admin, verify_password, hash_password, create_access_token
from config import settings
import models
from PIL import Image
import re
from typing import Optional

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

MEDIA_DIR = "media"


# --- UTILITY ---

def make_slug(testo: str) -> str:
    testo = testo.lower().strip()
    testo = re.sub(r"[àáâãäå]", "a", testo)
    testo = re.sub(r"[èéêë]", "e", testo)
    testo = re.sub(r"[ìíîï]", "i", testo)
    testo = re.sub(r"[òóôõö]", "o", testo)
    testo = re.sub(r"[ùúûü]", "u", testo)
    testo = re.sub(r"[^a-z0-9\s-]", "", testo)
    testo = re.sub(r"\s+", "-", testo)
    return testo


def salva_immagine(file: UploadFile, sottocartella: str = "") -> str:
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        raise HTTPException(status_code=400, detail="Formato immagine non supportato")
    cartella = os.path.join(MEDIA_DIR, sottocartella)
    os.makedirs(cartella, exist_ok=True)
    nome_file = f"{uuid.uuid4().hex}.{ext}"
    percorso = os.path.join(cartella, nome_file)
    with open(percorso, "wb") as f:
        f.write(file.file.read())
    img = Image.open(percorso)
    img.thumbnail((1920, 1080))
    img.save(percorso, optimize=True, quality=85)
    return os.path.join(sottocartella, nome_file) if sottocartella else nome_file


# --- AUTH ---

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={}
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    utente = db.query(models.Utente).filter(models.Utente.email == email).first()
    if not utente or not verify_password(password, utente.hashed_password):
        return templates.TemplateResponse(
            request=request,
            name="admin/login.html",
            context={"errore": "Email o password non corretti"}
        )
    token = create_access_token({"sub": utente.email})
    response = RedirectResponse(url="/admin", status_code=302)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# --- DASHBOARD ---

@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "n_progetti": db.query(models.Progetto).count(),
            "n_articoli": db.query(models.Articolo).count(),
            "n_messaggi": db.query(models.Messaggio).count(),
            "n_non_letti": db.query(models.Messaggio).filter(models.Messaggio.letto == False).count(),
            "messaggi_recenti": db.query(models.Messaggio).order_by(models.Messaggio.ricevuto_il.desc()).limit(5).all(),
        }
    )


# --- PROGETTI ---

@router.get("/progetti", response_class=HTMLResponse)
def lista_progetti(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    progetti = db.query(models.Progetto).order_by(models.Progetto.ordine).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/progetti.html",
        context={"progetti": progetti}
    )


@router.get("/progetti/nuovo", response_class=HTMLResponse)
def nuovo_progetto(request: Request, admin=Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/progetto_form.html",
        context={"progetto": None}
    )


@router.post("/progetti/nuovo")
def crea_progetto(
    request: Request,
    titolo: str = Form(...),
    categoria: str = Form(default=""),
    location: str = Form(default=""),
    anno: Optional[int] = Form(default=None),
    descrizione_breve: str = Form(default=""),
    descrizione: str = Form(default=""),
    in_evidenza: Optional[str] = Form(default=None),
    ordine: int = Form(default=0),
    pubblicato: Optional[str] = Form(default=None),
    immagine_cover: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    slug = make_slug(titolo)
    base_slug = slug
    counter = 1
    while db.query(models.Progetto).filter(models.Progetto.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    cover_path = None
    if immagine_cover and immagine_cover.filename:
        cover_path = salva_immagine(immagine_cover, "progetti")

    progetto = models.Progetto(
        titolo=titolo, slug=slug, categoria=categoria,
        location=location, anno=anno,
        descrizione_breve=descrizione_breve, descrizione=descrizione,
        immagine_cover=cover_path,
        in_evidenza=in_evidenza == "on",
        ordine=ordine,
        pubblicato=pubblicato == "on"
    )
    db.add(progetto)
    db.commit()
    return RedirectResponse(url="/admin/progetti", status_code=302)


@router.get("/progetti/{id}/modifica", response_class=HTMLResponse)
def modifica_progetto(id: int, request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    progetto = db.query(models.Progetto).filter(models.Progetto.id == id).first()
    if not progetto:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="admin/progetto_form.html",
        context={"progetto": progetto}
    )


@router.post("/progetti/{id}/modifica")
def aggiorna_progetto(
    id: int,
    titolo: str = Form(...),
    categoria: str = Form(default=""),
    location: str = Form(default=""),
    anno: Optional[int] = Form(default=None),
    descrizione_breve: str = Form(default=""),
    descrizione: str = Form(default=""),
    in_evidenza: Optional[str] = Form(default=None),
    ordine: int = Form(default=0),
    pubblicato: Optional[str] = Form(default=None),
    immagine_cover: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    progetto = db.query(models.Progetto).filter(models.Progetto.id == id).first()
    if not progetto:
        raise HTTPException(status_code=404)

    progetto.titolo = titolo
    progetto.categoria = categoria
    progetto.location = location
    progetto.anno = anno
    progetto.descrizione_breve = descrizione_breve
    progetto.descrizione = descrizione
    progetto.in_evidenza = in_evidenza == "on"
    progetto.ordine = ordine
    progetto.pubblicato = pubblicato == "on"

    if immagine_cover and immagine_cover.filename:
        progetto.immagine_cover = salva_immagine(immagine_cover, "progetti")

    db.commit()
    return RedirectResponse(url="/admin/progetti", status_code=302)


@router.post("/progetti/{id}/elimina")
def elimina_progetto(id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    progetto = db.query(models.Progetto).filter(models.Progetto.id == id).first()
    if progetto:
        db.delete(progetto)
        db.commit()
    return RedirectResponse(url="/admin/progetti", status_code=302)


# --- ARTICOLI ---

@router.get("/articoli", response_class=HTMLResponse)
def lista_articoli(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    articoli = db.query(models.Articolo).order_by(models.Articolo.creato_il.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/articoli.html",
        context={"articoli": articoli}
    )


@router.get("/articoli/nuovo", response_class=HTMLResponse)
def nuovo_articolo(request: Request, admin=Depends(require_admin)):
    return templates.TemplateResponse(
        request=request,
        name="admin/articolo_form.html",
        context={"articolo": None}
    )


@router.post("/articoli/nuovo")
def crea_articolo(
    titolo: str = Form(...),
    tag: str = Form(default=""),
    anteprima: str = Form(default=""),
    contenuto: str = Form(default=""),
    pubblicato: Optional[str] = Form(default=None),
    immagine_cover: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    slug = make_slug(titolo)
    base_slug = slug
    counter = 1
    while db.query(models.Articolo).filter(models.Articolo.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    cover_path = None
    if immagine_cover and immagine_cover.filename:
        cover_path = salva_immagine(immagine_cover, "articoli")

    articolo = models.Articolo(
        titolo=titolo, slug=slug, tag=tag,
        anteprima=anteprima, contenuto=contenuto,
        immagine_cover=cover_path,
        pubblicato=pubblicato == "on"
    )
    db.add(articolo)
    db.commit()
    return RedirectResponse(url="/admin/articoli", status_code=302)


@router.get("/articoli/{id}/modifica", response_class=HTMLResponse)
def modifica_articolo(id: int, request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    articolo = db.query(models.Articolo).filter(models.Articolo.id == id).first()
    if not articolo:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="admin/articolo_form.html",
        context={"articolo": articolo}
    )


@router.post("/articoli/{id}/modifica")
def aggiorna_articolo(
    id: int,
    titolo: str = Form(...),
    tag: str = Form(default=""),
    anteprima: str = Form(default=""),
    contenuto: str = Form(default=""),
    pubblicato: Optional[str] = Form(default=None),
    immagine_cover: UploadFile = File(default=None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    articolo = db.query(models.Articolo).filter(models.Articolo.id == id).first()
    if not articolo:
        raise HTTPException(status_code=404)

    articolo.titolo = titolo
    articolo.tag = tag
    articolo.anteprima = anteprima
    articolo.contenuto = contenuto
    articolo.pubblicato = pubblicato == "on"

    if immagine_cover and immagine_cover.filename:
        articolo.immagine_cover = salva_immagine(immagine_cover, "articoli")

    db.commit()
    return RedirectResponse(url="/admin/articoli", status_code=302)



@router.post("/articoli/{id}/elimina")
def elimina_articolo(id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    articolo = db.query(models.Articolo).filter(models.Articolo.id == id).first()
    if articolo:
        db.delete(articolo)
        db.commit()
    return RedirectResponse(url="/admin/articoli", status_code=302)


# --- SERVIZI ---

@router.get("/servizi", response_class=HTMLResponse)
def lista_servizi(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    servizi = db.query(models.Servizio).order_by(models.Servizio.ordine).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/servizi.html",
        context={"servizi": servizi}
    )


@router.post("/servizi/{id}/modifica")
def aggiorna_servizio(
    id: int,
    titolo: str = Form(...),
    descrizione: str = Form(default=""),
    numero: str = Form(default=""),
    ordine: int = Form(default=0),
    attivo: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    servizio = db.query(models.Servizio).filter(models.Servizio.id == id).first()
    if not servizio:
        raise HTTPException(status_code=404)
    servizio.titolo = titolo
    servizio.descrizione = descrizione
    servizio.numero = numero
    servizio.ordine = ordine
    servizio.attivo = attivo == "on"
    db.commit()
    return RedirectResponse(url="/admin/servizi", status_code=302)


# --- MESSAGGI ---

@router.get("/messaggi", response_class=HTMLResponse)
def lista_messaggi(request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    messaggi = db.query(models.Messaggio).order_by(models.Messaggio.ricevuto_il.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/messaggi.html",
        context={"messaggi": messaggi}
    )


@router.get("/messaggi/{id}", response_class=HTMLResponse)
def leggi_messaggio(id: int, request: Request, db: Session = Depends(get_db), admin=Depends(require_admin)):
    messaggio = db.query(models.Messaggio).filter(models.Messaggio.id == id).first()
    if not messaggio:
        raise HTTPException(status_code=404)
    messaggio.letto = True
    db.commit()
    return templates.TemplateResponse(
        request=request,
        name="admin/messaggio_dettaglio.html",
        context={"messaggio": messaggio}
    )


@router.post("/messaggi/{id}/elimina")
def elimina_messaggio(id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    messaggio = db.query(models.Messaggio).filter(models.Messaggio.id == id).first()
    if messaggio:
        db.delete(messaggio)
        db.commit()
    return RedirectResponse(url="/admin/messaggi", status_code=302)