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
        username = request['username']              #用户名
        emailvcode = request['emailcode']           #邮箱验证码
        password = request['password']              #密码
        repassword = request['repassword']          #确认密码

        database = getDatabase()
        curse = database.cursor()
        user = curse.execute(
            'SELECT * FROM user WHERE name=?', (username,)
        ).fetchone()                            #从数据库查找用户记录
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

@authbp.route('/sendcode')
def sendEmail(dest):
    database = getDatabase()
    cursor = database.cursor()
    mail = cursor.execute(
        'SELECT * FROM mail WHERE destination=?', (dest,)
    ).fetchone()

    if len(dest) > 7 and re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", dest) != None:
        #间隔两分钟才能发送邮件
        if time.time() - mail['posttime'] > 120:
            app = current_app._get_current_object()
            vcode = generateCode()
            thr = Thread(target = sendMail, args = [app, '', vcode])
            thr.start()

            cursor.execute(
                'UPDATE mail SET posttime=? WHERE destination=?', (time.time(), dest,)
            )
            session['emailvcode'] = vcode
        else:
            flash('发送邮件过于频繁')
    else:
        flash('邮箱格式不正确')

@authbp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request['username']              #用户名
        password = request['password']              #密码
        vcode = request['verifycode'].lower()       #验证码
        database = getDatabase()
        curse = database.cursor()
        user = curse.execute(
            'SELECT * FROM user WHERE name=?', (username,)
            ).fetchone()                            #从数据库查找用户记录
        error = None

        if user is None:
            error = '用户名不存在！'
        elif not check_password_hash(user['password'], password):
            error = '密码错误！'
        elif vcode !=  session['imageCode']:
            error = '验证码错误！'
        
        if error is None:
            session.clear()
            session['userID'] = user['uuid']
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html')

@authbp.route('/imageCode')
def imageCode():
    return ImageCode().getImageCode()

@authbp.before_app_request
def loadLoginedUser():
    userID = session['userID']
    if userID is None:
        g.user = None
    else:
        g.user = getDatabase().execute(
        'SELECT * FROM user WHERE uuid=?', (userID,)
        ).fetchone()

def loginRequired(view):
    @functools.wraps(view)
    def wrappedView(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    
    return wrappedView