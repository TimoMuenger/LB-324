# Modulplaner

Kleine Flask-Applikation, mit der schulische Aufgaben mit Kategorie und
Termin erfasst und als CSV exportiert werden können.

Leistungsbeurteilung Modul 324 (DevOps-Prozesse mit Tools unterstützen),
Klasse IM24a — Timo Münger und Joshua Merki.

## Entwicklungsumgebung einrichten (HZ2)

Voraussetzungen: Python 3.11 oder neuer, git, Visual Studio Code, optional
Docker Desktop und PostgreSQL mit pgAdmin.

```powershell
git clone https://github.com/TimoMuenger/LB-324.git
cd LB-324

# Virtuelle Umgebung: hält die Abhängigkeiten dieses Projekts getrennt
# von anderen Projekten auf demselben Rechner.
python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install pytest pytest-cov flake8 pre-commit

# Haken lokal aktivieren - ab jetzt prüfen sie jeden commit
pre-commit install
pre-commit install -t commit-msg

# Der Haken pytest-check laeuft im System-Python, nicht in der venv,
# weil git-Haken ohne aktivierte venv starten. Darum dort dasselbe
# nochmals installieren:
# python -m pip install pytest Flask Flask-SQLAlchemy python-dotenv

# Zugangsdaten vorbereiten (nur nötig für PostgreSQL)
copy .env.example .env
```

Starten mit `python main.py`, danach `http://localhost:5000` aufrufen.
Ohne `.env` verwendet die Applikation SQLite und braucht keinen
Datenbankserver.

## Datenbank

| Umgebung | Datenbank | Woher kommen die Zugangsdaten |
| :-- | :-- | :-- |
| Lokal ohne `.env` | SQLite (`instance/modulplaner.db`) | keine nötig |
| Lokal mit `.env` | PostgreSQL | `.env`, steht in der `.gitignore` |
| Azure | PostgreSQL Flexible Server | Application Settings im Azure-Portal |

`database.py` baut den connection string aus den vier Variablen `DBUSER`,
`DBPASS`, `DBHOST` und `DBNAME`. Sind sie nicht gesetzt, fällt die
Applikation auf SQLite zurück. Passwörter stehen nie im Code.

Welche Datenbank gerade aktiv ist, steht am Fuss der Startseite.

### PostgreSQL lokal einrichten

```powershell
winget install PostgreSQL.PostgreSQL.17
```

Die Installation läuft unbeaufsichtigt durch und fragt kein Passwort ab. Es
wird darum nachträglich gesetzt, in einer PowerShell als Administrator:

```powershell
$hba = "C:\Program Files\PostgreSQL\17\data\pg_hba.conf"
Copy-Item $hba "$hba.backup"
(Get-Content $hba) -replace 'scram-sha-256', 'trust' | Set-Content $hba
Restart-Service postgresql-x64-17

& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "ALTER USER postgres PASSWORD 'EUER-PASSWORT';"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE modulplaner;"

Copy-Item "$hba.backup" $hba -Force
Restart-Service postgresql-x64-17
```

Die vorletzten zwei Zeilen sind wichtig: `trust` erlaubt lokal die Anmeldung
ohne Passwort und darf nur für diese zwei Minuten gelten.

Danach `.env.example` als `.env` kopieren und die vier Werte eintragen.

### Warum die Testfälle nie PostgreSQL berühren

`conftest.py` setzt `DBUSER` auf leer, bevor pytest die Testmodule lädt.
Ohne das würden die Testfälle gegen die echte Datenbank laufen, und das
`drop_all()` in den fixtures würde bei jedem Testlauf alle Daten löschen.

## Testfälle

```powershell
pytest                          # alle Testfälle
pytest --cov=.                  # mit Testabdeckung
```

- `test_helper.py` — Komponententests der Logik in `helper.py`
- `test_main.py` — Integrationstests der Routen über den Flask-Testclient
- `conftest.py` — setzt den Datenbanknamen auf `test.db`, bevor pytest die
  Testmodule lädt, damit nie gegen die echte Datenbank getestet wird

Jeder Testfall ist nach dem Schema **Given / When / Then** aufgebaut und
gehört zu einer Anforderung (issue).

## Arbeitsablauf (GitHub Flow)

1. Anforderung als issue erfassen (Vorlage *User Story*), Etikette und
   Meilenstein setzen, zuständige Person eintragen
2. Vom issue aus einen Ast erstellen, lokal `git pull` und
   `git checkout Ast-Name`
3. Zuerst den Testfall schreiben, dann die Umsetzung
4. `git commit -m "Kategorien ergänzt, closes #12"` — die Haken lassen den
   commit nur durch, wenn die Tests grün sind und eine issue-Nummer in der
   Meldung steht
5. `git push`, Änderungsantrag (PR) auf `main` eröffnen
6. Der CI-Ablauf prüft Code und Testfälle, die zweite Person begutachtet
   und vereinigt den PR; das issue schliesst sich automatisch

Der `main`-Ast ist geschützt: Änderungen kommen nur über einen PR hinein.

## Automatisierte Abläufe

| Datei | Ausgelöst durch | Wirkung |
| :-- | :-- | :-- |
| `issue-in-progress.yml` | issue erhält Meilenstein | setzt `status: in progress` |
| `issue-assigned.yml` | issue erhält zuständige Person | entfernt `status: new issue` |
| `ci.yml` | Änderungsantrag auf `main` | flake8 und pytest |
| `release.yml` | neue Etikette | erstellt Veröffentlichung mit Quellcode |
| `docker.yml` | neue Etikette | baut Abbild, lädt es nach GitHub Packages |
| `azure-deploy.yml` | neue Etikette | testet und liefert auf Azure aus |

Neue Version veröffentlichen und ausliefern:

```powershell
git tag -a "1.0.0" -m "Erste vollständige Version"
git push --tags
```

## Docker

```powershell
docker build -t modulplaner .
docker run -d -p 8000:8000 modulplaner
```

Das Abbild enthält Betriebssystem, Python, alle Abhängigkeiten und den
Code. Es läuft darum auf jedem Rechner gleich — unabhängig davon, ob dort
Python installiert ist.

## Etiketten (labels)

| Etikette | Bedeutung |
| :-- | :-- |
| `status: new issue` | Noch nicht eingeordnet, niemand zuständig |
| `status: in progress` | Eingeordnet, jemand arbeitet daran |
| `status: backlog` | Zurückgestellt |
| `type: user story` | Neue Anforderung aus Benutzersicht |
| `type: bug` | Fehler in der bestehenden Applikation |
