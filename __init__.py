import os

from flask import Flask

def create_app():
    app = Flask(__name__)

    from MyWeb import database
    database.init_app(app)

    @app.route('/test')
    def hello():
        return "这是一个测试网站"
    
    return app