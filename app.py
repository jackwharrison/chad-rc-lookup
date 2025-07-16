from flask import Flask, render_template, request, send_file, redirect, session, url_for
import requests
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

import os

KOBO_TOKEN = os.environ.get("KOBO_TOKEN")
ASSET_ID = os.environ.get("ASSET_ID")

KOBO_API_URL = f"https://kobo.ifrc.org/api/v2/assets/{ASSET_ID}/data/"
PASSWORD = "password"

translations = {
    "en": {
        "title": "Beneficiary Information",
        "name": "Name",
        "dob": "Date of Birth",
        "photo": "Photo",
        "payment_approved": "Payment Approved",
        "payment_rejected": "Payment Rejected",
        "participant_withdraws": "Participant Withdraws",
        "language": "Language",
        "login": "Login",
        "enter_password": "Enter Password",
        "submit": "Submit",
        "payment_status": "Payment Status",
        "confirm_person": "Are you sure this is the correct person?",
        "rejection_reason": "Reason for Rejection"
    },
    "fr": {
        "title": "Informations du bénéficiaire",
        "name": "Nom",
        "dob": "Date de naissance",
        "photo": "Photo",
        "payment_approved": "Paiement Approuvé",
        "payment_rejected": "Paiement Rejeté",
        "participant_withdraws": "Participant Se Retire",
        "language": "Langue",
        "login": "Connexion",
        "enter_password": "Entrez le mot de passe",
        "submit": "Soumettre",
        "payment_status": "Statut du paiement",
        "confirm_person": "Êtes-vous sûr que c'est la bonne personne ?",
        "rejection_reason": "Raison du refus"
    },
    "ar": {
        "title": "معلومات المستفيد",
        "name": "الاسم",
        "dob": "تاريخ الميلاد",
        "photo": "الصورة",
        "payment_approved": "تمت الموافقة على الدفع",
        "payment_rejected": "تم رفض الدفع",
        "participant_withdraws": "انسحب المستفيد",
        "language": "اللغة",
        "login": "تسجيل الدخول",
        "enter_password": "أدخل كلمة المرور",
        "submit": "إرسال",
        "payment_status": "حالة الدفع",
        "confirm_person": "هل أنت متأكد أن هذا هو الشخص الصحيح؟",
        "rejection_reason": "سبب الرفض"
    }
}

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        ben_id = request.form.get("id")
        lang = request.form.get("lang", "en")
        if password == PASSWORD:
            session.clear()
            session.permanent = False
            session['logged_in'] = True
            return redirect(f"/beneficiary?id={ben_id}&lang={lang}")
        else:
            return render_template("login.html", error="Incorrect password", lang="en", id=ben_id, t=translations["en"])

    ben_id = request.args.get("id")
    lang = request.args.get("lang", "en")
    return render_template("login.html", error=None, lang=lang, id=ben_id, t=translations.get(lang, translations["en"]))

@app.route("/beneficiary")
def beneficiary():
    if not session.get("logged_in"):
        return redirect(f"/login?id={request.args.get('id')}&lang={request.args.get('lang', 'en')}")

    ben_id = request.args.get("id")
    lang = request.args.get("lang", "en")
    if not ben_id:
        return "Missing beneficiary ID", 400

    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    url = f"{KOBO_API_URL}{ben_id}/?format=json"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "Beneficiary not found.", 404

    data = response.json()
    photo_url = f"/photo/{ben_id}"

    return render_template(
        "beneficiary.html",
        data=data,
        photo_url=photo_url,
        lang=lang,
        t=translations.get(lang, translations["en"])
    )

@app.route("/photo/<int:ben_id>")
def photo(ben_id):
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    photo_url = f"https://kobo.ifrc.org/api/v2/assets/{ASSET_ID}/data/{ben_id}/attachments/?xpath=photo"

    response = requests.get(photo_url, headers=headers)
    if response.status_code == 200:
        return send_file(BytesIO(response.content), mimetype='image/jpeg')
    else:
        return "Photo not found", 404

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
