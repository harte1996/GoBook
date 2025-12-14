from flask import Flask
from modulos import bd, logger
from routes.auth import auth_bp
from routes.home import home_bp
from routes.cadastro import cadastro_bp
from routes.servicos import servicos_bp
from routes.agenda import agenda_bp
from routes.client import client_bp
import os
from threading import Timer
import webbrowser
import argparse

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Registrar blueprints
    app.register_blueprint(agenda_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(servicos_bp)
    return app

def open_browser(port):
    webbrowser.open_new(f"http://127.0.0.1:{port}/login")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Inventário Web App')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    app = create_app()
    Timer(2, open_browser, args=(args.port,)).start()
    app.run(host='0.0.0.0', port=args.port, debug=True)
