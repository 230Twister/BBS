import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)

from werkzeug.security import check_password_hash, generate_password_hash
from .database import getDatabase
from .auth import loginRequired
from PIL import Image
import os, datetime
from .api import readImg, uploadImg, getData, getGroupName

userpagebp = Blueprint('userpage', __name__, url_prefix='/userpage')

@userpagebp.route('/<int:id>', methods=('GET', 'POST'))
def showUserpage(id):
    # 显示用户的个人主页
    database = getDatabase()
    cursor = database.cursor()
    user = getData(cursor, 'user', 'uuid', id)
    userinfo = getData(cursor, 'userinfo', 'uuid', id)
    if user is None:
        return render_template('404.html'),404

    level = int(userinfo[4] / 100)
    percentage = userinfo[4] % 100
    needpoint = 100 - percentage
    group = getGroupName(userinfo[2])

    return render_template('userpage/info.html', userpagedata = [user, userinfo, group, level, percentage, needpoint, id])


@userpagebp.route('/<int:id>/collect')
@loginRequired
def collect(id):
    database = getDatabase()
    cursor = database.cursor()
    user = getData(cursor, 'user', 'uuid', id)
    userinfo = getData(cursor, 'userinfo', 'uuid', id)
    if user is None or g.user[0] != user[0]:            #不允许访问不存在用户和其他用户的收藏
        return render_template('404.html'),404

    _collect = str(userinfo[3]).split(" ")
    _collect.remove('')
    _post_id = []               #主题id列表
    _posts = []                 #主题列表
    length = len(_collect)
    for i in range(0,length):
        _post_id.append(_collect[i])

    for i in range(0, length):
        cursor.execute(
            'SELECT * FROM post WHERE id=%s;', (_post_id[i], )
        )
        _posts.append (cursor.fetchone())
    post = []
    for p in _posts:
        post.append([p[0], p[1], getData(cursor, 'user', 'uuid', p[4])[1], len(p[7].split(' ')) - 1])

    return render_template('userpage/mycollection.html', info = [post, id])

# 展示图片（头像）
@userpagebp.route('/<int:id>/image')
def showImg(id):
    return readImg(id, 'avatar.jpg')

@userpagebp.route('/<int:id>/mypost')
def showPosts(id):
    # 显示该用户曾发过的帖子
    database = getDatabase()
    cursor = database.cursor()
    user = getData(cursor, 'user', 'uuid', id)
    if user is None:
        return render_template('404.html'),404

    # 显示用户所有帖子
    cursor.execute(
        'SELECT * FROM post WHERE userid=%s;', (id, )
    )
    _posts = cursor.fetchall()

    post = [] 
    for p in _posts:
        post.append([p[0], p[1], getData(cursor, 'user', 'uuid', p[4])[1], len(p[7].split(' ')) - 1])

    return render_template('userpage/mypost.html', info = [post, id])

@userpagebp.route('/<int:id>/notice')
@loginRequired
def showNotice(id):
    database = getDatabase()
    cursor = database.cursor()
    user = getData(cursor, 'user', 'uuid', id)
    userinfo = getData(cursor, 'userinfo', 'uuid', id)
    if user is None or g.user[0] != user[0]:
        return render_template('404.html'),404

    # 以下为消息提醒
    _warn = str(userinfo[1]).split(" ")
    _warn.remove('')
    _postreply = []
    _post_id = []
    _reply_id = []
    length = len(_warn)
    for i in range(0,length):
        _postreply.append(_warn[i].split(":"))
        _post_id.append( _postreply[i][0])          #回帖主题id
        _reply_id.append( _postreply[i][1])         #回复id

    _posts = []
    _replyuser = []
    for i in range(0, length):      #获取回复人的名字
        rep = getData(cursor, 'reply', 'id', _reply_id[i])
        _replyuser.append(getData(cursor, 'user', 'uuid', rep[1])[1])
    for i in range(0, length):      #获取被回复的帖子信息
        _posts.append(getData(cursor, 'post', 'id', _post_id[i]))

    post = []
    for index, p in enumerate(_posts):
        post.append([p[0], p[1], getData(cursor, 'user', 'uuid', p[4])[1], len(p[7].split(' ')) - 1, _replyuser[index]])

    return render_template('userpage/notify.html', info = [post, id])

@userpagebp.route('/<int:id>/unwarn/<int:postid>')
@loginRequired
def unwarn(id, postid):
    database = getDatabase()
    cursor = database.cursor()
    userinfo = getData(cursor, 'userinfo', 'uuid', id)
    if userinfo is None or g.user[0] != userinfo[0]:
        return render_template('404.html'),404
    
    warn = ''
    warnlist = userinfo[1].split(' ')
    warnlist.remove('')
    for w in warnlist:
        if(not w.startswith(str(postid))):
            warn = warn + ' ' + w
    cursor.execute(
        'UPDATE userinfo SET warn=%s WHERE uuid=%s;', (warn, id,)
    )
    return redirect(url_for('posts.posts', postid=postid, page=1))

@userpagebp.route('/<int:id>/setting', methods=('GET', 'POST'))
@loginRequired
def setting(id):
    # 用户设置，允许用户自行更改昵称、头像、密码、邮箱等
    database = getDatabase()
    cursor = database.cursor()
    user = getData(cursor, 'user', 'uuid', id)
    error = None
    if user is None or g.user[0] != user[0]:
        # 用户不存在 或 无权访问他人设置页面
        return render_template('404.html'),404
    
    if request.method == 'POST':
        if 'codeSetting' in request.form:                           #修改密码
            oldPassword = request.form['oldPassword']               #验证原密码
            newPassword = request.form['newPassword']               #新密码
            newRepassword = request.form['newRepassword']           #新确认密码
            if not check_password_hash(user[3], oldPassword):
                error = '原密码输入有误'
            elif newPassword != newRepassword:
                error = '两次密码不一致'
                
            if error is None:
                flash("密码修改成功！")
                cursor.execute(
                    'UPDATE user SET password'
                    '= %s WHERE uuid = %s;'
                    , (generate_password_hash(newPassword), user[0])
                )
                return redirect(url_for('userpage.setting', id=id))
            flash(error)
            return render_template('userpage/setting.html', userdata={  "oldPassword":oldPassword,
                                                                "newPassword":newPassword,
                                                                "newRepassword":newRepassword,
                                                                "id":id})
        else:                                                   #修改头像
            file = request.files['editormd-image-file']
            if(os.path.splitext(file.filename)[1] == '.jpg' and not len(file.read())/1048576 > 1):
                uploadImg(id, 'avatar', file)
            else:
                flash("上传图片格式错误或大小超限！")

    return render_template('userpage/setting.html', userdata={ "id":id })