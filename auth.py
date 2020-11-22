import functools

from werkzeug.local import LocalProxy
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from threading import Thread
import time, datetime, re

from .database import getDatabase
from .api import ImageCode, generateCode, sendMail

authbp = Blueprint('auth', __name__, url_prefix='/auth')

@authbp.route('/register', methods=('GET', 'POST'))
def register():
    if g.user:
        return redirect(url_for('index.index'))
    if request.method == 'POST':
        username = request.form['username']              #用户名
        email = request.form['email']                    #邮箱
        emailvcode = request.form['emailcode']           #邮箱验证码
        password = request.form['password']              #密码
        repassword = request.form['repassword']          #确认密码
        if 'register' in request.form:
            database = getDatabase()
            cursor = database.cursor()
            user = checkUser(cursor, username, email)   #从数据库查找用户记录
            error = None
            if user is not None:
                error = '该用户已存在'
            elif password != repassword:
                error = '两次密码不一致'
            elif emailvcode != session['emailvcode']:
                error = '验证码错误'

            if error is None:
                dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    'INSERT INTO user(uuid, name, ip, password, email, registertime, lastlogin)'
                    'VALUES(null, %s, %s, %s, %s, %s, %s);'
                    , (username, '0.0.0.0', generate_password_hash(password), email, dtime, dtime)
                )
                cursor.execute(
                    'SELECT * FROM user WHERE name=%s;', (username,)
                )
                user = cursor.fetchone()
                session.clear()
                session['userID'] = user
                return redirect(url_for('auth.login'))
            flash(error)
        else:
            database = getDatabase()
            cursor = database.cursor()
            if checkUser(cursor, username, email) is not None:
                flash("用户已存在")
            else:
                sendEmail(request)
        return render_template('auth/register.html',
                                    userdata={  "username":username,
                                                "password":password,
                                                "repassword":repassword,
                                                "email":email})

    return render_template('auth/register.html', userdata={})

def sendEmail(request):
    dest = request.form['email']
    database = getDatabase()
    cursor = database.cursor()
    cursor.execute(
        'SELECT * FROM mail WHERE destination=%s;', (dest,)
    )
    mail = cursor.fetchone()

    if len(dest) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", dest) != None:
        #间隔两分钟才能发送邮件
        if mail is None or time.time() - mail[1] > 120:
            app = current_app._get_current_object()
            vcode = generateCode()          #生成验证码
            thr = Thread(target = sendMail, args = [app, dest, vcode])
            thr.start()                     #异步发送邮件

            session['emailvcode'] = vcode
            if mail is None:
                cursor.execute(
                    'INSERT INTO mail(destination, posttime) '
                    'VALUES(%s, %s);', (dest, time.time(),)
                )
            else:
                cursor.execute(
                    'UPDATE mail SET posttime=%s WHERE destination=%s', (time.time(), dest,)
                )
        else:
            flash('发送邮件过于频繁')
    else:
        flash('邮箱格式不正确')

@authbp.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('index.index'))
    if request.method == 'POST':
        username = request.form['username']              #用户名
        password = request.form['password']              #密码
        vcode = request.form['verifycode']               #验证码
        database = getDatabase()
        curse = database.cursor()
        curse.execute(
            'SELECT * FROM user WHERE name=%s OR email=%s;', (username, username,)
            )                            #从数据库查找用户记录
        user = curse.fetchone()
        error = None

        if user is None or not check_password_hash(user[3], password):
            error = '用户名或密码错误！'
        elif vcode !=  session['imageCode']:
            error = '验证码错误！'

        if error is None:
            session.clear()
            session['userID'] = user
            return redirect(url_for('index.index'))
        flash(error)
        return render_template('auth/login.html', userdata={"username":username, "password":password})
    return render_template('auth/login.html', userdata={})

@authbp.route('/imageCode')
def imageCode():
    return ImageCode().getImageCode()

@authbp.route('/forget', methods=('GET', 'POST'))
def forgetPassword():
    if request.method == 'POST':
        pass
    return render_template('auth/forget.html')

#登出
@authbp.route('/logout')
def logout():
    if session['userID']:
        session.clear()
    return redirect('index.index')

@authbp.before_app_request
def loadLoginedUser():
    userID = session.get('userID')
    if userID is None:
        g.user = None
    else:
        cursor = getDatabase().cursor()
        cursor.execute(
        'SELECT * FROM user WHERE uuid=%s;', (userID[0],)
        )
        g.user = cursor.fetchone()

#需要登陆检测
def loginRequired(view):
    @functools.wraps(view)
    def wrappedView(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrappedView

#查询是否存在一个用户
def checkUser(cursor, name, email):
    cursor.execute(
                'SELECT * FROM user WHERE name=%s OR email=%s;', (name, email, )
            )
    user = cursor.fetchone()                        #从数据库查找用户记录
    return user