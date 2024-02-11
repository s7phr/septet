from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)

police = Blueprint("police", __name__)


@police.route("/radio")
def radio():
    return render_template("network.html")


@police.route("/radio/home")
def home():
    return render_template("home.html")


@police.route("/radio/<int:id>")
def radio_id(id: int): ...
