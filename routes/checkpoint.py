from flask import Blueprint, jsonify, render_template, request

checkpoint = Blueprint("checkpoint", __name__)


@checkpoint.route("/radio")
def radio():
    return render_template("network.html")
