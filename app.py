import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import random
from datetime import date

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

db = mysql.connector.connect(
    host="zephyr.proxy.rlwy.net",
    user="root",
    password="ZDdOtytktloTNZMkBkzethgbZycfQAZr",
    database="railway",
    port=43437
)

cursor = db.cursor(dictionary=True)

def schimbare_baterie(data):
    if data["cicluri_incarcare"] > 1500 or data["sanatate_baterie"] < 70:
        return "Da"
    return "Nu"

def adauga_date_live(vehicul):
    vehicul["tensiune"] = round(random.uniform(200, 700), 1)
    vehicul["temperatura_baterie"] = round(random.uniform(30, 65), 1)
    return vehicul

@app.route("/vehicule")
def get_vehicule():
    cursor.execute("SELECT * FROM vehicule")
    vehicule = cursor.fetchall()
    return jsonify([adauga_date_live(v) for v in vehicule]), 200

@app.route("/vehicule/<int:id>")
def get_vehicul(id):
    cursor.execute("SELECT * FROM vehicule WHERE id = %s", (id,))
    vehicul = cursor.fetchone()
    if not vehicul:
        return jsonify({"eroare": "Vehicul inexistent"}), 404
    return jsonify(adauga_date_live(vehicul)), 200

@app.route("/vehicule", methods=["POST"])
def adauga_vehicul():
    data = request.get_json()
    campuri = [
        "vin", "model_masina", "an_fabricatie", "kilometraj",
        "nivel_baterie", "autonomie_estimata_km",
        "cicluri_incarcare", "sanatate_baterie"
    ]
    for c in campuri:
        if c not in data:
            return jsonify({"eroare": f"Lipseste {c}"}), 400

    sql = """
    INSERT INTO vehicule (
        vin, model_masina, an_fabricatie, kilometraj,
        nivel_baterie, autonomie_estimata_km,
        cicluri_incarcare, sanatate_baterie,
        schimbare_baterie, data_ultima_verificare
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    val = (
        data["vin"], data["model_masina"], data["an_fabricatie"], data["kilometraj"],
        data["nivel_baterie"], data["autonomie_estimata_km"], data["cicluri_incarcare"],
        data["sanatate_baterie"], schimbare_baterie(data), date.today().strftime("%d.%m.%Y")
    )
    cursor.execute(sql, val)
    db.commit()
    return jsonify({"mesaj": "Vehicul adaugat"}), 201

@app.route("/vehicule/<int:id>", methods=["PUT"])
def update_vehicul(id):
    data = request.get_json()
    sql = """
    UPDATE vehicule SET
        vin=%s, model_masina=%s, an_fabricatie=%s, kilometraj=%s,
        nivel_baterie=%s, autonomie_estimata_km=%s, cicluri_incarcare=%s,
        sanatate_baterie=%s, schimbare_baterie=%s, data_ultima_verificare=%s
    WHERE id=%s
    """
    val = (
        data["vin"], data["model_masina"], data["an_fabricatie"], data["kilometraj"],
        data["nivel_baterie"], data["autonomie_estimata_km"], data["cicluri_incarcare"],
        data["sanatate_baterie"], schimbare_baterie(data), date.today().strftime("%d.%m.%Y"), id
    )
    cursor.execute(sql, val)
    db.commit()
    return jsonify({"mesaj": "Vehicul actualizat"}), 200

@app.route("/vehicule", methods=["PUT"])
def update_all_same_values():
    data = request.get_json()
    sql = """
    UPDATE vehicule SET
        vin=%s, model_masina=%s, an_fabricatie=%s, kilometraj=%s,
        nivel_baterie=%s, autonomie_estimata_km=%s, cicluri_incarcare=%s,
        sanatate_baterie=%s, schimbare_baterie=%s, data_ultima_verificare=%s
    """
    val = (
        data["vin"], data["model_masina"], data["an_fabricatie"], data["kilometraj"],
        data["nivel_baterie"], data["autonomie_estimata_km"], data["cicluri_incarcare"],
        data["sanatate_baterie"], schimbare_baterie(data), date.today().strftime("%d.%m.%Y")
    )
    cursor.execute(sql, val)
    db.commit()
    return jsonify({"mesaj": "Toate vehiculele au fost suprascrise"}), 200

@app.route("/vehicule/<int:id>", methods=["DELETE"])
def delete_vehicul(id):
    cursor.execute("DELETE FROM vehicule WHERE id=%s", (id,))
    db.commit()
    return jsonify({"mesaj": "Vehicul sters"}), 200

@app.route("/vehicule", methods=["DELETE"])
def delete_all():
    cursor.execute("DELETE FROM vehicule")
    db.commit()
    return jsonify({"mesaj": "Toate vehiculele au fost sterse"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
