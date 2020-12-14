import os

from flask import Flask, redirect, url_for
from flask_mail import Mail

mail = None         #邮件发送对象

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(  #默认配置
        SECRET_KEY="dev",
        MAX_CONTENT_LENGTH=1 * 1024 * 1024, #限制上传文件大小1M

        HOST="127.0.0.1",                   #Mysql数据库设置
        PORT=3306,
        USER="root",
        PASSWORD="root",
        DATABASE="bbs",

        MAIL_SERVER='smtp.example.com',     #stmp服务器设置
        MAIL_USERNAME="root",
        MAIL_PASSWORD="root",
        MAIL_DEFAULT_SENDER="root",
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
    database.init_app(app)                      #注册数据库初始化命令

    from . import auth
    app.register_blueprint(auth.authbp)         #登陆注册
    from . import userpage
    app.register_blueprint(userpage.userpagebp) #用户主页
    from . import index
    app.register_blueprint(index.indexbp)       #主页
    from . import edit
    app.register_blueprint(edit.editbp)         #帖子编辑
    from . import posts
    app.register_blueprint(posts.postsbp)       #主题页面

    @app.route('/')
    def hello():
        return redirect(url_for('index.index'))
    
    return app