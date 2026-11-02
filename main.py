from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for

import helper
from database import db, verbindungszeichenkette

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = verbindungszeichenkette()
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template(
        "index.html",
        eintraege=helper.get_all(),
        kategorien=helper.KATEGORIEN,
    )


@app.route("/add", methods=["POST"])
def add():
    helper.add(
        request.form.get("titel"),
        request.form.get("termin"),
        request.form.get("kategorie", "Allgemein"),
    )
    return redirect(url_for("index"))


@app.route("/update/<int:eintrag_id>")
def update(eintrag_id):
    helper.update(eintrag_id)
    return redirect(url_for("index"))


@app.route("/delete/<int:eintrag_id>")
def delete(eintrag_id):
    helper.loeschen(eintrag_id)
    return redirect(url_for("index"))


@app.route("/edit/<int:eintrag_id>", methods=["POST"])
def edit(eintrag_id):
    helper.bearbeiten(
        eintrag_id,
        request.form.get("titel"),
        request.form.get("termin"),
    )
    return redirect(url_for("index"))


@app.route("/download")
def download():
    return Response(
        helper.get_csv(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=modulplaner.csv"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
