import os

from flask import Flask
from flask_mail import Mail

mail = None         #邮件发送对象

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(  #默认配置
        SECRET_KEY="dev",

        HOST="127.0.0.1",
        PORT=3306,
        USER="root",
        PASSWORD="root",
        DATABASE="bbs",

        MAIL_SERVER='smtp.qq.com',
        MAIL_USERNAME="null",
        MAIL_PASSWORD="null",
        MAIL_DEFAULT_SENDER="null",
        MAIL_USE_TLS=True,
        MAIL_PORT=587
    )
    app.config.from_pyfile('config.py', silent=True)  #载入配置文件
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    global mail
    mail = Mail(app)

    from . import database
    database.init_app(app)       #注册数据库初始化命令

    from . import auth
    app.register_blueprint(auth.authbp)

    from . import userpage
    app.register_blueprint(userpage.userpagebp)
    from . import index
    app.register_blueprint(index.indexbp)
    from . import edit
    app.register_blueprint(edit.editbp)

    @app.route('/test')
    def hello():
        return "这是一个测试网站"
    
    return app