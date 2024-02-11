import sqlite3
import uuid
from datetime import datetime

from flask import Blueprint, redirect, render_template, url_for

invoice = Blueprint("invoice", __name__)


@invoice.route("/<invoice_id>")
def index(invoice_id: str) -> str:
    db = sqlite3.connect("helpers/schemas/invoice.db")
    data = db.cursor()
    data.execute(
        """
        CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY,
        invoice_id TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP NOT NULL,
        payment_type TEXT NOT NULL
        );
        """
    )
    data.execute(
        """
        SELECT * FROM invoices WHERE invoice_id = ?
        """,
        (invoice_id,),
    )
    check = data.fetchone()
    code = ""
    if check:
        payment_type = check[3]
        if payment_type == "ltc":
            code = "/static/qrcodes/ltc.png"
        elif payment_type == "btc":
            code = "/static/qrcodes/btc.png"
        elif payment_type == "eth":
            code = "/static/qrcodes/eth.png"
    else:
        return render_template(
            "error.html",
            error="That invoice was not found! Please create a new one if the time period has not expired.",
        )

    return render_template(
        "invoice.html", invoice=invoice_id, code=code, payment_type=payment_type
    )


@invoice.route("/create/<payment_type>")
def create_invoice(payment_type: str) -> str:
    if payment_type not in ["ltc", "btc", "eth"]:
        return render_template(
            "error.html",
            error=f"The payment type '{payment_type}' is not supported currently. Please contact the administrator.",
        )
    db = sqlite3.connect("helpers/schemas/invoice.db")
    data = db.cursor()
    invoice_id = str(uuid.uuid4())
    created_at = datetime.now()
    data.execute(
        """
        INSERT INTO invoices (invoice_id, created_at, payment_type) VALUES (?, ?, ?)
        """,
        (invoice_id, created_at, payment_type),
    )
    db.commit()
    return redirect(
        url_for(
            "invoice.index",
            invoice_id=invoice_id,
        )
    )
