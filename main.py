from app import App
from routes import *

Client = App()
Client.app.register_blueprint(police, url_prefix="/police")
Client.app.register_blueprint(checkpoint, url_prefix="/checkpoint")

Client.run()
