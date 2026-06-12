from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Utente(Base):
    __tablename__ = "utenti"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=True)
    creato_il = Column(DateTime, default=datetime.utcnow)


class Progetto(Base):
    __tablename__ = "progetti"

    id = Column(Integer, primary_key=True, index=True)
    titolo = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    categoria = Column(String(100))          # es. "Residenziale", "Contract"
    location = Column(String(100))           # es. "Milano"
    anno = Column(Integer)
    descrizione_breve = Column(String(300))
    descrizione = Column(Text)
    immagine_cover = Column(String(300))     # path file
    in_evidenza = Column(Boolean, default=False)
    ordine = Column(Integer, default=0)      # per ordinare nel portfolio
    pubblicato = Column(Boolean, default=True)
    creato_il = Column(DateTime, default=datetime.utcnow)
    aggiornato_il = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    immagini = relationship("ImmagineProgetto", back_populates="progetto",
                            cascade="all, delete-orphan")


class ImmagineProgetto(Base):
    __tablename__ = "immagini_progetto"

    id = Column(Integer, primary_key=True, index=True)
    progetto_id = Column(Integer, ForeignKey("progetti.id"), nullable=False)
    path = Column(String(300), nullable=False)
    didascalia = Column(String(200))
    ordine = Column(Integer, default=0)

    progetto = relationship("Progetto", back_populates="immagini")


class Articolo(Base):
    __tablename__ = "articoli"

    id = Column(Integer, primary_key=True, index=True)
    titolo = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, index=True, nullable=False)
    tag = Column(String(100))                # es. "Tendenze", "Progetto"
    anteprima = Column(String(300))          # testo breve per la card
    contenuto = Column(Text)                 # corpo completo articolo
    immagine_cover = Column(String(300))
    pubblicato = Column(Boolean, default=False)
    creato_il = Column(DateTime, default=datetime.utcnow)
    aggiornato_il = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Servizio(Base):
    __tablename__ = "servizi"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(4))               # es. "01", "02"
    titolo = Column(String(150), nullable=False)
    descrizione = Column(Text)
    ordine = Column(Integer, default=0)
    attivo = Column(Boolean, default=True)


class Messaggio(Base):
    __tablename__ = "messaggi"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cognome = Column(String(100))
    email = Column(String(150), nullable=False)
    tipo_progetto = Column(String(100))
    testo = Column(Text, nullable=False)
    letto = Column(Boolean, default=False)
    ricevuto_il = Column(DateTime, default=datetime.utcnow)

class Impostazione(Base):
    __tablename__ = "impostazioni"

    id = Column(Integer, primary_key=True, index=True)
    chiave = Column(String(100), unique=True, index=True, nullable=False)
    valore = Column(Text)