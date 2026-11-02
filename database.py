import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def verbindungszeichenkette():
    if os.environ.get("DBUSER"):
        return "postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}".format(
            dbuser=os.environ["DBUSER"],
            dbpass=os.environ["DBPASS"],
            dbhost=os.environ["DBHOST"],
            dbname=os.environ["DBNAME"],
        )
    return "sqlite:///" + os.environ.get("DBFILE", "modulplaner.db")


def datenbank_art():
    return "PostgreSQL" if os.environ.get("DBUSER") else "SQLite"
