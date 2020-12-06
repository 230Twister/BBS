import pymysql
import click

from flask import current_app, g
from flask.cli import with_appcontext

#获取数据库对象
def getDatabase():
    if 'db' not in g:
        g.db = pymysql.connect( host=current_app.config['HOST'],            #数据库ip
                                port=current_app.config['PORT'],            #端口
                                user=current_app.config['USER'],            #用户
                                password=current_app.config['PASSWORD'],    #密码
                                database=current_app.config['DATABASE'],    #数据库名
                                autocommit=True)
    return g.db

#关闭数据库
def closeDatabase(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#注册
def init_app(app):
    app.teardown_appcontext(closeDatabase)
    app.cli.add_command(initCommand)

#初始化数据库
def initDatabase():
    db = getDatabase()
    cursor = db.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS post('           #主题表单
        'id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'  #主题id
        'title TEXT NOT NULL,'                                  #标题
        'type TINYINT NOT NULL,'                                #主题分类 1 2 3 4    
        'content LONGTEXT NOT NULL,'                            #内容
        'userid INT UNSIGNED NOT NULL,'                         #发主题的用户id
        'posttime DATETIME NOT NULL,'                           #发表时间
        'updatetime DATETIME NOT NULL,'                         #更新时间
        'reply MEDIUMTEXT NOT NULL,'                            #主题回复
        'visit BIGINT UNSIGNED NOT NULL,'                       #阅读量
        'collect INT UNSIGNED NOT NULL'                         #收藏量
        ');')
    cursor.execute('CREATE TABLE IF NOT EXISTS reply('
        'id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'  #主题回复id
        'userid INT UNSIGNED NOT NULL,'                         #用户id
        'content LONGTEXT NOT NULL,'                            #内容
        'posttime DATETIME NOT NULL,'                           #发表时间
        'updatetime DATETIME NOT NULL,'                         #更新时间
        'reply INT UNSIGNED NOT NULL'                           #回复对象
        ');')
    cursor.execute('CREATE TABLE IF NOT EXISTS user ('
        'uuid INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'#用户id
        'name varchar(128) BINARY NOT NULL, '                   #昵称
        'ip varchar(32) NOT NULL,'                              #ip
        'password varchar(256) NOT NULL,'                       #密码
        'email varchar(32) NOT NULL,'                           #邮箱
        'registertime DATETIME NOT NULL,'                       #注册时间
        'lastlogin DATETIME NOT NULL'                           #最后登录时间
        ');')
    cursor.execute('CREATE TABLE IF NOT EXISTS userinfo ('
        'uuid INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,'#用户id
        'warn TEXT NOT NULL,'                                   #提醒
        'permission varchar(32) NOT NULL,'                      #权限列表 管理员 版主1/2/3/4 普通会员 禁言
        'collect TEXT NOT NULL,'                                #收藏的主题
        'point MEDIUMINT UNSIGNED NOT NULL)'                    #积分
    )
    cursor.execute('CREATE TABLE IF NOT EXISTS mail ('
        'destination varchar(32) NOT NULL,'                     #发送邮箱
        'posttime INT UNSIGNED NOT NULL);'                      #发送时间
    )

@click.command('init_db')
@with_appcontext
def initCommand():
    initDatabase()
    click.echo("数据库初始化完成！")
