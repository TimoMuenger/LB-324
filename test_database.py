import database


def test_verbindung_nutzt_postgresql_wenn_zugangsdaten_gesetzt(monkeypatch):
    # Given: Zugangsdaten für PostgreSQL in der Umgebung
    monkeypatch.setenv("DBUSER", "postgres")
    monkeypatch.setenv("DBPASS", "geheim")
    monkeypatch.setenv("DBHOST", "localhost:5432")
    monkeypatch.setenv("DBNAME", "modulplaner")

    # When/Then: Die Verbindung zeigt auf PostgreSQL
    assert database.verbindungszeichenkette().startswith("postgresql+psycopg2://")
    assert database.datenbank_art() == "PostgreSQL"


def test_verbindung_faellt_ohne_zugangsdaten_auf_sqlite_zurueck(monkeypatch):
    # Given: Keine Zugangsdaten für PostgreSQL
    monkeypatch.setenv("DBUSER", "")

    # When/Then: Die Verbindung zeigt auf SQLite
    assert database.verbindungszeichenkette().startswith("sqlite:///")
    assert database.datenbank_art() == "SQLite"
