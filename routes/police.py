from flask import Blueprint, jsonify, render_template, request

police = Blueprint("police", __name__)


@police.route("/radio")
def radio():
    return render_template("radio.html")
