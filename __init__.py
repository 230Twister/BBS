import os

from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(  #默认配置
        HOST="127.0.0.1",
        PORT=3306,
        USER="root",
        PASSWORD="root",
        DATABASE="bbs"
    )
    app.config.from_pyfile('config.py', silent=True)  #载入配置文件
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from BBS import database
    database.init_app(app)       #注册数据库初始化命令

    @app.route('/test')
    def hello():
        return "这是一个测试网站"
    
    return app