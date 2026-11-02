import csv
import datetime
import io

from database import db

KATEGORIEN = ["Modul", "Projekt", "Prüfung", "Allgemein"]


class Eintrag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(120), nullable=False)
    kategorie = db.Column(db.String(60), nullable=False, default="Allgemein")
    termin = db.Column(db.Date, nullable=False)
    erledigt = db.Column(db.Boolean, nullable=False, default=False)


def in_einer_woche():
    return datetime.date.today() + datetime.timedelta(weeks=1)


def parse_termin(termin):
    if termin is None or termin == "":
        return in_einer_woche()
    if isinstance(termin, datetime.date):
        return termin
    return datetime.datetime.strptime(termin, "%Y-%m-%d").date()


def add(titel, termin=None, kategorie="Allgemein"):
    eintrag = Eintrag(
        titel=titel,
        kategorie=kategorie,
        termin=parse_termin(termin),
    )
    db.session.add(eintrag)
    db.session.commit()
    return eintrag


def get_all():
    return Eintrag.query.order_by(Eintrag.termin).all()


def get(eintrag_id):
    return db.session.get(Eintrag, eintrag_id)


def get_nach_kategorie(kategorie):
    return Eintrag.query.filter_by(kategorie=kategorie).order_by(Eintrag.termin).all()


def update(eintrag_id):
    eintrag = get(eintrag_id)
    eintrag.erledigt = not eintrag.erledigt
    db.session.commit()
    return eintrag


def loeschen(eintrag_id):
    eintrag = get(eintrag_id)
    db.session.delete(eintrag)
    db.session.commit()


def bearbeiten(eintrag_id, titel, termin):
    eintrag = get(eintrag_id)
    eintrag.titel = titel
    eintrag.termin = parse_termin(termin)
    db.session.commit()
    return eintrag


def get_csv():
    puffer = io.StringIO()
    schreiber = csv.writer(puffer)
    schreiber.writerow(["id", "titel", "kategorie", "termin", "erledigt"])
    for eintrag in get_all():
        schreiber.writerow(
            [
                eintrag.id,
                eintrag.titel,
                eintrag.kategorie,
                eintrag.termin.isoformat(),
                eintrag.erledigt,
            ]
        )
    return puffer.getvalue()
