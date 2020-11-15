import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from threading import Thread
import time, re

from BBS.database import getDatabase
from BBS.api import ImageCode, generateCode, sendMail

authbp = Blueprint('auth', __name__, url_prefix='/auth')

@authbp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']              #用户名
        emailvcode = request.form['emailcode']           #邮箱验证码
        password = request.form['password']              #密码
        repassword = request.form['repassword']          #确认密码

        database = getDatabase()
        cursor = database.cursor()
        curse.execute(
            'SELECT * FROM user WHERE name=%s;', (username,)
        )
        user = cursor.fetchone()                        #从数据库查找用户记录
        error = None
        if user is not None:
            error = '该用户已存在'
        elif password != repassword:
            error = '两次密码不一致'
        elif emailvcode != session['emailvcode']:
            error = '验证码错误'

        if error is None:
            session.clear()
            session['userID'] = user['uuid']
            return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@authbp.route('/sendcode', methods=('GET', 'POST'))
def sendEmail():
    if request.method == 'POST':
        dest = request.form['email']
        database = getDatabase()
        cursor = database.cursor()
        cursor.execute(
            'SELECT * FROM mail WHERE destination=%s;', (dest,)
        )
        mail = cursor.fetchone()

        if len(dest) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", dest) != None:
            #间隔两分钟才能发送邮件
            if time.time() - mail['posttime'] > 120:
                app = current_app._get_current_object()
                vcode = generateCode()          #生成验证码
                thr = Thread(target = sendMail, args = [app, dest, vcode])
                thr.start()                     #异步发送邮件

                session['emailvcode'] = vcode
                cursor.execute(
                    'UPDATE mail SET posttime=%s WHERE destination=%s', (time.time(), dest,)
                )
            else:
                flash('发送邮件过于频繁')
        else:
            flash('邮箱格式不正确')

@authbp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']              #用户名
        password = request.form['password']              #密码
        vcode = request.form['verifycode']               #验证码
        database = getDatabase()
        curse = database.cursor()
        curse.execute(
            'SELECT * FROM user WHERE name=%s;', (username,)
            )                            #从数据库查找用户记录
        user = curse.fetchone()
        error = None

        if user is None:
            error = '用户名不存在！'
        elif not check_password_hash(user[3], password):
            error = '密码错误！'
        elif vcode !=  session['imageCode']:
            error = '验证码错误！'
        
        if error is None:
            session.clear()
            session['userID'] = user
            return redirect(url_for('hello'))
        flash(error)
    return render_template('auth/login.html')

@authbp.route('/imageCode')
def imageCode():
    return ImageCode().getImageCode()

@authbp.route('/forget', methods=('GET', 'POST'))
def forgetPassword():
    if request.method == 'POST':
        pass
    return render_template('auth/forget.html')

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

def loginRequired(view):
    @functools.wraps(view)
    def wrappedView(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    return wrappedView