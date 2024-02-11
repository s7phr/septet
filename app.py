import random
import sqlite3
import string
from json import dumps, load
from typing import List, Optional, Tuple, Union
from uuid import uuid4

import bcrypt
import qrcode
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
)
from terminut import log

from routes import *


class App:
    def __init__(self):
        self.config = load(open("helpers/config/config.json"))
        self.robots = load(open("helpers/config/robots.json"))
        self.app = Flask(__name__)
        self.jwt = JWTManager(self.app)
        self.log = log()
        self.app.config["SECRET_KEY"] = "septetsociety123@123!234"
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        @property
        def app(self):
            return self.app

        @property
        def jwt(self):
            return self.jwt

        @self.app.route("/")
        def main():
            return render_template(
                "loader.html",
            )

        @self.app.route("/home")
        def home():
            return render_template("index.html")

        @self.app.route("/404")
        def not_found():
            return render_template("404.html")

        @self.app.route("/signin")
        def signin():
            return render_template("login.html")

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            username = request.json.get("username", None)
            password = request.json.get("password", None)

            conn = sqlite3.connect("helpers/schemas/users.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                "SELECT id, password FROM users WHERE username = ?", (username,)
            )
            user = cursor.fetchone()

            conn.close()

            if user:
                user_id, hashed_password = user
                if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
                    access_token = create_access_token(identity=username)
                    return jsonify(access_token=access_token), 200
                else:
                    return jsonify({"error": "Invalid password"}), 401
            else:
                return jsonify({"error": "User not found"}), 404

        @self.app.route("/newuser")
        def newuser():
            return render_template("signup.html")

        @self.app.route("/tos")
        def tos():
            return render_template("loader.html")

        @self.app.route("/pricing")
        def pricing():
            return render_template("prices.html")

        @self.app.route("/signup", methods=["POST"])
        def signup():
            username = request.json.get("username", None)
            password = request.json.get("password", None)

            conn = sqlite3.connect("helpers/schemas/users.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
                """
            )

            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                conn.close()
                return jsonify({"error": "Username already exists"}), 400

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            conn.commit()
            conn.close()

            return redirect("/signin")

        @self.app.route("/videos")
        def videos():
            return render_template("videos.html")

        @self.app.route("/robots", methods=["GET"])
        def robots():
            return jsonify(
                {
                    "robots": self.robots["Google_Search_Engine_Robot"],
                    "sitemap_url": self.robots["Sitemap"],
                    "DiscordBot": self.robots["Discordbot"],
                    "CrawlDelay": int(self.robots["Crawl_Delay"]),
                }
            )

        @self.app.route("/sitemap", methods=["GET"])
        def sitemap():
            return render_template("sitemap.xml")

        @self.app.route("/api/v1/radio/get_stations")
        def get_stations():
            conn = sqlite3.connect("helpers/schemas/radio.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    url TEXT NOT NULL UNIQUE,
                    logo TEXT NOT NULL UNIQUE,
                    country TEXT NOT NULL,
                    language TEXT NOT NULL,
                    category TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    description TEXT NOT NULL,
                    bitrate TEXT NOT NULL,
                    codec TEXT NOT NULL,
                    is_hd INTEGER NOT NULL,
                    is_new INTEGER NOT NULL,
                    is_active INTEGER NOT NULL
                )
                """
            )
            cursor.execute("SELECT * FROM stations")
            stations = cursor.fetchall()
            conn.close()
            return jsonify(stations)

    def run(self):
        return self.app.run(
            host="0.0.0.0",
            debug=True,
        )

    def create_code(self: "App", type: str = "btc") -> str:
        """
        Creates a qr code for the payments
        """
        mapping: dict = {
            "btc": {
                "data": self.config["crypto"]["btc"],
                "filename": "static/qrcodes/btc.png",
            },
            "eth": {
                "data": self.config["crypto"]["eth"],
                "filename": "static/qrcodes/eth.png",
            },
            "ltc": {
                "data": self.config["crypto"]["ltc"],
                "filename": "static/qrcodes/ltc.png",
            },
        }

        if type in mapping:
            info = mapping[type]
            self.qr.add_data(info["data"])
            self.qr.make(fit=True)
            img = self.qr.make_image()
            img.save(info["filename"])
            return self.log.success(f"QR code created -> {info['filename']}")
        else:
            raise ValueError("Invalid crypto type specified!")
