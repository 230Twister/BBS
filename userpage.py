import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)

from werkzeug.security import check_password_hash, generate_password_hash
from .database import getDatabase
from .auth import loginRequired
from PIL import Image
import os, datetime
from .api import readImg, uploadImg

userpagebp = Blueprint('userpage', __name__, url_prefix='/userpage')

@userpagebp.route('/<int:id>', methods=('GET', 'POST'))
def showUserpage(id):
    # 显示用户的个人主页
    # 主要包括个人信息，如昵称、头像、邮箱、关注、收藏、积分等
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    userinfo = findUserinfo(cursor, id)
    #error = None
    if user is None:
        return render_template('404.html'),404

    #头像也要显示

    # table: user
    uuid = user[0]
    name = user[1]
    ip = user[2]
    email = user[4]
    registertime = user[5]
    lastlogin = user[6]
        
    # table: userinfo
    warn = userinfo[1]
    permission = userinfo[2]
    collect = userinfo[3]
    point = userinfo[4]

    #如果是本人主页，可以修改设置
    if request.method == 'POST':
        return redirect(url_for('userpage.settings', id=id))

    return render_template('userpage.html', userpagedata = {user, userinfo})    #直接用user和userinfo就行...

# 展示图片（头像）
@userpagebp.route('/<int:id>/image/<name>')
@loginRequired
def showImg(id, name):
    return readImg(id, name)

@userpagebp.route('/<int:id>/post')
def showPosts(id):
    # 显示该用户曾发过的帖子
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    userinfo = findUserinfo(cursor, id)
    #error = None
    if user is None:
        return render_template('404.html'),404

    # 显示用户所有帖子
    posts = database.execute(
        'SELECT * FROM post WHERE name=%s'
        'ORDER BY created DESC'
    ).fetchall()
    return render_template('userposts.html', posts = posts)


@userpagebp.route('/<int:id>/settings', methods=('GET', 'POST'))
@loginRequired
def settings(id):
    # 用户设置，允许用户自行更改昵称、头像、密码、邮箱等
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    error = None
    if user is None or g.user[0] != user[0]:
        # 用户不存在 或 无权访问他人设置页面
        return render_template('404.html'),404

    # 允许用户开始设置
    # 设置分两种：修改密码/修改头像
    #if request.method == 'POST':
    #    if 'changeCode' in request.form:
    #        return redirect(url_for('userpage.changeCode', id=id))
    #    elif 'changeAvatar' in request.form:
    #        return redirect(url_for('userpage.changeAvatar', id=id))
    return render_template('userpage/settings.html', userdata={})


@userpagebp.route('/<int:id>/changecode', methods=('GET', 'POST'))
@loginRequired
def changeCode(id):
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    error = None
    if user is None or g.user[0] != user[0]:
        # 用户不存在 或 无权访问他人设置页面
        return render_template('404.html'),404
        
    if request.method == 'POST':
        oldPassword = request.form['oldPassword']               #验证原密码
        newPassword = request.form['newPassword']               #新密码
        newRepassword = request.form['newRepassword']           #新确认密码

        if 'settings' in request.form:                          #确认修改
            if not check_password_hash(user[3], oldPassword):
                error = '原密码输入有误'
            elif newPassword != newRepassword:
                error = '两次密码不一致'
                
            if error is None:
                cursor.execute(
                    'UPDATE user SET password'
                    '= %s WHERE id = %s;'
                    , (generate_password_hash(newPassword), user[0])
                )
                return redirect(url_for('userpage.settings', id=id))
            flash(error)
            return render_template('userpage/changeCode.html', userdata={  "oldPassword":oldPassword,
                                                                "newPassword":newPassword,
                                                                "newRepassword":newRepassword})

    return render_template('userpage/changeCode.html', userdata={})


@userpagebp.route('/<int:id>/changeavatar', methods=('GET', 'POST'))
@loginRequired
def changeAvatar(id):
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    error = None
    if user is None or g.user[0] != user[0]:
        # 用户不存在 或 无权访问他人设置页面
        return render_template('404.html'),404

    if request.method == 'POST':
        if 'settings' in request.form:                          #上传新头像
            file = request.files.get('editormd-image-file')     #获取上传的图片
            uploadImg(id, 'avatar.jpg', file)

    return render_template('userpage/changeAvatar.html')

def checkUser(cursor, id):
    # 从user中查找用户记录
    cursor.execute(
        'SELECT * FROM user WHERE uuid=%s;', (id, )
    )
    user = cursor.fetchone()
    return user

def findUserinfo(cursor, id):
    # 从userinfo获取用户记录
    cursor.execute(
        'SELECT * FROM userinfo WHERE uuid=%s;', (id, )
    )
    userinfo = cursor.fetchone()
    return userinfo
