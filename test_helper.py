import datetime

import pytest
from flask import Flask

import helper
from database import db


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_add_speichert_den_termin(app):
    # Given: Ich möchte einen Eintrag mit Termin erfassen
    titel = "Modul 324 abschliessen"
    termin = "2026-12-19"

    # When: Ich den Eintrag hinzufüge
    helper.add(titel, termin)

    # Then: Der Eintrag hat ein Datum vom Typ date
    eintrag = helper.get_all()[-1]
    assert isinstance(eintrag.termin, datetime.date)
    assert eintrag.termin == datetime.date(2026, 12, 19)


def test_add_ohne_termin_setzt_termin_in_einer_woche(app):
    # Given: Ein Eintrag ohne Termin
    # When: Ich ihn hinzufüge
    helper.add("Ohne Termin")

    # Then: Der Termin liegt eine Woche in der Zukunft
    eintrag = helper.get_all()[-1]
    assert eintrag.termin == datetime.date.today() + datetime.timedelta(weeks=1)


def test_eintraege_werden_nach_termin_sortiert(app):
    # Given: Mehrere Einträge in unsortierter Reihenfolge
    helper.add("Spät", "2026-12-24")
    helper.add("Früh", "2026-11-03")
    helper.add("Mitte", "2026-12-01")

    # When: Ich alle Einträge abfrage
    eintraege = helper.get_all()

    # Then: Sie sind nach Termin aufsteigend sortiert
    for i in range(len(eintraege) - 1):
        assert eintraege[i].termin <= eintraege[i + 1].termin


def test_update_schaltet_den_status_um(app):
    # Given: Ein offener Eintrag
    eintrag = helper.add("Testfall schreiben", "2026-11-10")
    assert eintrag.erledigt is False

    # When: Ich den Status umschalte
    helper.update(eintrag.id)

    # Then: Der Eintrag ist erledigt
    assert helper.get(eintrag.id).erledigt is True


def test_get_nach_kategorie_filtert(app):
    # Given: Einträge in zwei Kategorien
    helper.add("Modulprüfung", "2026-11-20", "Prüfung")
    helper.add("LB 324", "2026-11-21", "Modul")

    # When: Ich nach einer Kategorie filtere
    treffer = helper.get_nach_kategorie("Prüfung")

    # Then: Nur die Einträge dieser Kategorie kommen zurück
    assert len(treffer) == 1
    assert treffer[0].titel == "Modulprüfung"


def test_get_csv_enthaelt_kopfzeile_und_eintrag(app):
    # Given: Ein erfasster Eintrag
    helper.add("CSV-Export bauen", "2026-11-15", "Projekt")

    # When: Ich den CSV-Export abrufe
    csv_text = helper.get_csv()

    # Then: Kopfzeile und Eintrag stehen darin
    zeilen = csv_text.strip().splitlines()
    assert zeilen[0] == "id,titel,kategorie,termin,erledigt"
    assert "CSV-Export bauen" in zeilen[1]
    assert "2026-11-15" in zeilen[1]


def test_get_csv_maskiert_komma_im_titel(app):
    # Given: Ein Titel, der selbst ein Komma enthält
    helper.add("Testen, dann einbuchen", "2026-11-16")

    # When: Ich den CSV-Export abrufe
    csv_text = helper.get_csv()

    # Then: Der Titel steht maskiert in Anführungszeichen
    assert '"Testen, dann einbuchen"' in csv_text


def test_loeschen_entfernt_eintrag(app):
    # Given: Zwei erfasste Aufgaben
    helper.add("Bleibt stehen", "2026-11-20")
    weg = helper.add("Soll weg", "2026-11-21")

    # When: Ich eine davon lösche
    helper.loeschen(weg.id)

    # Then: Nur die andere ist noch da
    titel = [eintrag.titel for eintrag in helper.get_all()]
    assert titel == ["Bleibt stehen"]


def test_bearbeiten_aendert_titel_und_termin(app):
    # Given: Eine erfasste Aufgabe
    eintrag = helper.add("Alter Titel", "2026-11-10")

    # When: Ich Titel und Termin ändere
    helper.bearbeiten(eintrag.id, "Neuer Titel", "2026-12-01")

    # Then: Der Eintrag trägt die neuen Werte
    geaendert = helper.get(eintrag.id)
    assert geaendert.titel == "Neuer Titel"
    assert geaendert.termin == datetime.date(2026, 12, 1)


def test_get_offene_liefert_nur_unerledigte(app):
    # Given: Eine offene und eine erledigte Aufgabe
    helper.add("Noch offen", "2026-11-10")
    erledigt = helper.add("Schon fertig", "2026-11-11")
    helper.update(erledigt.id)

    # When: Ich nur die offenen abfrage
    treffer = helper.get_offene()

    # Then: Nur die offene kommt zurück
    titel = [eintrag.titel for eintrag in treffer]
    assert titel == ["Noch offen"]
