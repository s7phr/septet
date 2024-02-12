from app import App
from routes import *

Client = App()

Client.app.register_blueprint(dash, url_prefix="/dash")
Client.app.register_blueprint(checkpoint, url_prefix="/checkpoint")
Client.app.register_blueprint(invoice, url_prefix="/invoice")

Client.run()
