from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import qrcode
import os

app = Flask(__name__)
app.secret_key = "segredo"

DB_NAME = "database.db"
PIX_KEY = "jbm5688@hotmail.com"  # sua chave pix
PIX_VALOR = "1.00"

# ---------- Banco de Dados ----------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS depositos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT UNIQUE,
                email TEXT,
                status TEXT
            )
        """)
        conn.commit()

init_db()

# ---------- Página Inicial ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cpf = request.form["cpf"]
        email = request.form["email"]

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM depositos WHERE cpf = ?", (cpf,))
            existente = cursor.fetchone()

            if existente:
                flash("⚠️ Esse CPF já fez um depósito.")
                return redirect(url_for("index"))

            cursor.execute("INSERT INTO depositos (cpf, email, status) VALUES (?, ?, ?)",
                           (cpf, email, "pendente"))
            conn.commit()

        return redirect(url_for("sucesso", cpf=cpf))

    return render_template("index.html")

# ---------- Página Sucesso + QR Code ----------
@app.route("/sucesso/<cpf>")
def sucesso(cpf):
    # cria QR Code Pix simples (código copia e cola fake)
    payload = f"00020126580014BR.GOV.BCB.PIX0114{PIX_KEY}52040000530398654041.005802BR5925NOME EXEMPLO6009SAO PAULO62070503***6304ABCD"
    img = qrcode.make(payload)
    filename = f"static/qrcode_{cpf}.png"
    img.save(filename)

    return render_template("sucesso.html", cpf=cpf, qrcode=filename)

# ---------- Página Admin ----------
@app.route("/admin")
def admin():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cpf, email, status FROM depositos")
        registros = cursor.fetchall()

    total = len([r for r in registros if r[2] == "pendente" or r[2] == "pago"])
    return render_template("admin.html", registros=registros, total=total)

if __name__ == "__main__":
    app.run(debug=True)
