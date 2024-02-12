from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)

dash = Blueprint("dash", __name__)
import sqlite3


@dash.route("/checkpoint")
def radio():
    return render_template("network.html")


@dash.route("/home")
def home():
    db = sqlite3.connect("helpers/schemas/users.db")
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    db.close()

    return render_template("home.html", totalusers=total_users)


@dash.route("/radio/<int:id>")
def radio_id(id: int): ...
