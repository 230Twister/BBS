import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)

from werkzeug.security import check_password_hash, generate_password_hash
from .database import getDatabase
from .auth import loginRequired
from PIL import Image
import os, datetime
from .api import readImg, uploadImg, getData

userpagebp = Blueprint('userpage', __name__, url_prefix='/userpage')

@userpagebp.route('/<int:id>', methods=('GET', 'POST'))
def showUserpage(id):
    # 显示用户的个人主页
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    userinfo = findUserinfo(cursor, id)
    #error = None
    if user is None:
        return render_template('404.html'),404

    point = userinfo[4]
    level = userinfo[4] / 100
    percentage = userinfo[4] % 100
    needpoint = 100 - percentage

    #如果是本人主页，可以修改设置
    if request.method == 'POST':
        return redirect(url_for('userpage.setting', id=id))

    return render_template('userpage/info.html', userpagedata = [user, userinfo, point, level, percentage, needpoint, id])


@userpagebp.route('/<int:id>/collect')
def collect(id):
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    userinfo = findUserinfo(cursor, id)
    if user is None:
        return render_template('404.html'),404

    _collect = str(userinfo[3]).split(" ")
    _collect.remove('')
    _post_id = []
    _posts = []
    length=len(_collect)
    for i in range(0,length):
        _post_id.append(_collect[i])

    for i in range(0,length):
        cursor.execute(
            'SELECT * FROM post WHERE id=%s'
            'ORDER BY posttime DESC;', (_post_id[i], )
        )
        _posts.append (cursor.fetchone())
    post = []
    for p in _posts:
        post.append([p[0], p[1], findUser(cursor, p[4])[1], len(p[7].split(' ')) - 1])

    return render_template('userpage/collect.html', info = [post, id])

# 展示图片（头像）
@userpagebp.route('/<int:id>/image')
def showImg(id):
    return readImg(id, 'avatar.jpg')

@userpagebp.route('/<int:id>/mypost')
def showPosts(id):
    # 显示该用户曾发过的帖子
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    #error = None
    if user is None:
        return render_template('404.html'),404

    # 显示用户所有帖子
    cursor.execute(
        'SELECT * FROM post WHERE userid=%s'
        'ORDER BY created DESC;', (id, )
    )
    _posts = cursor.fetchall()

    post = [] 
    for p in _posts:
        post.append([p[0], p[1], findUser(cursor, p[4])[1], len(p[7].split(' ')) - 1])

    return render_template('userpage/mypost.html', info = [post, id])

@userpagebp.route('/<int:id>/notice')
def showNotice(id):
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    userinfo = findUserinfo(cursor, id)
    #error = None
    if user is None:
        return render_template('404.html'),404

    # 以下为消息提醒
    _warn = str(userinfo[1]).split(" ")
    _postreply = []
    _post_id = []
    _reply_id = []
    length=len(_warn)
    for i in range(0,length):
        _postreply.append(_warn[i].split(":"))
        _post_id.append( _postreply[i][0])          #回帖主题id
        _reply_id.append( _postreply[i][1])         #回复id

    _posts = []
    _reply = []
    for i in range(0,length):
        cursor.execute(
            'SELECT * FROM post WHERE id=%s'
            'ORDER BY created DESC;', (_post_id[i], )
        )
        _posts.append( cursor.fetchone())

    post = []
    for p in _posts:
        post.append([p[0], p[1], findUser(cursor, p[4])[1], len(p[7].split(' ')) - 1])


    for i in range(0,length):
        cursor.execute(
            'SELECT * FROM reply WHERE id=%s'
            'ORDER BY created DESC;', (_reply_id[i], )
        )
        _reply.append(cursor.fetchone())

    reply = []
    for r in _reply:
        post.append([r[2]])

    return render_template('userpage/notify.html', info = [post, reply, id])


@userpagebp.route('/<int:id>/setting', methods=('GET', 'POST'))
@loginRequired
def setting(id):
    # 用户设置，允许用户自行更改昵称、头像、密码、邮箱等
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

        if 'codeSetting' in request.form:                          #修改密码
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
                return redirect(url_for('userpage.setting', id=id))
            flash(error)
            return render_template('setting.html', userdata={  "oldPassword":oldPassword,
                                                                "newPassword":newPassword,
                                                                "newRepassword":newRepassword,
                                                                "id":id})
        else:                                                       #修改头像
            file = request.files.get('editormd-image-file')     #获取上传的图片
            uploadImg(id, 'avatar.jpg', file)

    return render_template('userpage/setting.html', userdata={ "id":id })


#   以下为功能函数

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

def findUser(cursor, id):
    # 从user中查找用户记录
    return getData(cursor, 'user', 'uuid', id)