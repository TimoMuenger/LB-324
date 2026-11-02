import pytest

import helper
import main
from database import db


@pytest.fixture()
def client():
    main.app.config["TESTING"] = True
    with main.app.app_context():
        db.create_all()
        with main.app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


def test_startseite_zeigt_erfasste_eintraege(client):
    # Given: Ein erfasster Eintrag
    helper.add("Präsentation vorbereiten", "2026-11-05", "Modul")

    # When: Ich die Startseite aufrufe
    antwort = client.get("/")

    # Then: Der Eintrag ist auf der Seite sichtbar
    assert antwort.status_code == 200
    assert "Präsentation vorbereiten" in antwort.get_data(as_text=True)


def test_formular_legt_neuen_eintrag_an(client):
    # Given: Ein ausgefülltes Formular
    formular = {
        "titel": "Docker-Behälter bauen",
        "termin": "2026-11-28",
        "kategorie": "Projekt",
    }

    # When: Ich das Formular abschicke
    antwort = client.post("/add", data=formular)

    # Then: Die Seite leitet um und der Eintrag ist gespeichert
    assert antwort.status_code == 302
    assert helper.get_all()[-1].titel == "Docker-Behälter bauen"


def test_update_route_schaltet_status_um(client):
    # Given: Ein offener Eintrag
    eintrag = helper.add("Testfall grün bekommen", "2026-11-12")

    # When: Ich die update-Route aufrufe
    antwort = client.get("/update/{}".format(eintrag.id))

    # Then: Der Status ist umgeschaltet
    assert antwort.status_code == 302
    assert helper.get(eintrag.id).erledigt is True


def test_download_liefert_csv_datei(client):
    # Given: Ein erfasster Eintrag
    helper.add("Export prüfen", "2026-11-18")

    # When: Ich die Download-Route aufrufe
    antwort = client.get("/download")

    # Then: Die Antwort ist eine CSV-Datei zum Herunterladen
    assert antwort.status_code == 200
    assert antwort.mimetype == "text/csv"
    assert "attachment" in antwort.headers["Content-disposition"]
    assert "Export prüfen" in antwort.get_data(as_text=True)
