import sqlite3
import uuid
from datetime import datetime
from json import load

from flask import Blueprint, redirect, render_template, url_for
from requests import get

invoice = Blueprint("invoice", __name__)
config = load(open("helpers/config/config.json"))


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
        payment_type TEXT NOT NULL,
        payment_amount REAL
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
    address: str = ""
    payment_type = ""
    payment_amount = ""
    created_at = check[2]
    if check:
        payment_type = check[3]
        payment_amount = check[4] if len(check) > 4 else None
        if payment_type == "ltc":
            code = "/static/qrcodes/ltc.png"
            address = config["crypto"]["ltc"]
        elif payment_type == "btc":
            code = "/static/qrcodes/btc.png"
            address = config["crypto"]["btc"]
        elif payment_type == "eth":
            code = "/static/qrcodes/eth.png"
            address = config["crypto"]["eth"]
    else:
        return render_template(
            "error.html",
            error="That invoice was not found! Please create a new one if the time period has not expired.",
        )

    response = get(f"https://blockchain.info/tobtc?currency=USD&value={payment_amount}")
    if not response:
        cryptoamount = 0
    cryptoamount = response.text

    return render_template(
        "invoice.html",
        invoice=invoice_id,
        code=code,
        payment_type=payment_type,
        payment_amount=f"{payment_amount:,}",
        created_at=created_at,
        cryptoamount=cryptoamount,
        address=address,
    )


@invoice.route("/create/<payment_type>/<int:payment_amount>")
def create_invoice(payment_type: str, payment_amount: float) -> str:
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
        INSERT INTO invoices (invoice_id, created_at, payment_type, payment_amount) VALUES (?, ?, ?, ?)
        """,
        (invoice_id, created_at, payment_type, payment_amount),
    )
    db.commit()
    return redirect(
        url_for(
            "invoice.index",
            invoice_id=invoice_id,
            created_at=created_at,
            payment_type=payment_type,
        )
    )
