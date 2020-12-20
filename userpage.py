import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)

from werkzeug.security import check_password_hash, generate_password_hash
from .database import getDatabase
from .auth import loginRequired
from PIL import Image
import os, datetime
from .api import readImg, uploadImg, getData, getGroupName, getUserName, getPartData

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

    level = int(userinfo[4] / 100)      #等级
    percentage = userinfo[4] % 100      #经验条比例
    needpoint = 100 - percentage        #升级所需经验
    group = getGroupName(userinfo[2])   #用户组

    return render_template('userpage/info.html', userpagedata = [user, userinfo, group, level, percentage, needpoint, id])

@userpagebp.route('/<int:id>/collect')
@loginRequired
def collect(id):
    database = getDatabase()
    cursor = database.cursor()
    user = getUserName(cursor, id)
    userinfo = getPartData(cursor, 'userinfo', 'uuid', id, 'collect')
    if user is None or g.user[0] != id:               #不允许访问不存在用户和其他用户的收藏
        return render_template('404.html'),404

    _collect = str(userinfo[0]).split(" ")      #主题id列表
    if '' in _collect:
        _collect.remove('')
    _posts = []                                 #主题列表
    length = len(_collect)

    for i in range(0, length):
        collectpost = getPartData(cursor, 'post', 'id', _collect[i], 'id', 'title', 'userid', 'reply')
        if collectpost is not None:
            _posts.append (collectpost)
        else:
            del _collect[i]                 #收藏中的帖子不存在，应该删除

    cursor.execute(
        'UPDATE userinfo SET collect=%s WHERE uuid=%s;'     #更新收藏列表，去除不存在的收藏
        , (' '.join(_collect), id,)
    )
    post = []
    for p in _posts:
        post.append([p[0], p[1], getUserName(cursor, p[2]), len(p[3].split(' ')) - 1])

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
    if getUserName(cursor, id) is None:
        return render_template('404.html'),404

    # 获取用户所有帖子
    cursor.execute(
        'SELECT id,title,userid,reply FROM post WHERE userid=%s;', (id, )
    )
    _posts = cursor.fetchall()

    post = [] 
    for p in _posts:
        post.append([p[0], p[1], getUserName(cursor, p[2]), len(p[3].split(' ')) - 1])

    return render_template('userpage/mypost.html', info = [post, id])

@userpagebp.route('/<int:id>/notice')
@loginRequired
def showNotice(id):
    database = getDatabase()
    cursor = database.cursor()
    user = getUserName(cursor, id)
    userinfo = getPartData(cursor, 'userinfo', 'uuid', id, 'warn')
    if user is None or g.user[0] != id:
        return render_template('404.html'),404

    # 以下为消息提醒
    _warn = str(userinfo[0]).split(" ")
    if '' in _warn:
        _warn.remove('')

    _posts = []
    _replyuser = []
    length = len(_warn)
    for i in range(0,length):
        tmp = _warn[i].split(":")
        _posts.append(
            getPartData(cursor, 'post', 'id', tmp[0], 'id', 'title', 'userid', 'reply')
            )    #获取被回复帖子信息
        rep = getPartData(cursor, 'reply', 'id', tmp[1], 'userid')
        _replyuser.append(getUserName(cursor, rep[0]))          #获取回复人名字

    post = []
    for index, p in enumerate(_posts):
        post.append([p[0], p[1], getUserName(cursor, p[2]), len(p[3].split(' ')) - 1, _replyuser[index]])

    return render_template('userpage/notify.html', info = [post, id])

@userpagebp.route('/<int:id>/unwarn/<int:postid>')
@loginRequired
def unwarn(id, postid):
    database = getDatabase()
    cursor = database.cursor()
    userinfo = getPartData(cursor, 'userinfo', 'uuid', id, 'warn')
    if userinfo is None or g.user[0] != id:
        return render_template('404.html'),404
    
    warn = ''
    warnlist = userinfo[0].split(' ')
    if '' in warnlist:
        warnlist.remove('')
    for w in warnlist:              #消除已经打开的提醒
        if(not w.startswith(str(postid))):
            warn = warn + ' ' + w
    cursor.execute(
        'UPDATE userinfo SET warn=%s WHERE uuid=%s;', (warn, id,)
    )
    return redirect(url_for('posts.posts', postid = postid, page = 1))

@userpagebp.route('/<int:id>/setting', methods=('GET', 'POST'))
@loginRequired
def setting(id):
    # 用户设置，允许用户自行更改昵称、头像、密码、邮箱等
    database = getDatabase()
    cursor = database.cursor()
    user = getPartData(cursor, 'user', 'uuid', id, 'uuid', 'password')
    error = None
    if user is None or g.user[0] != user[0]:
        # 用户不存在 或 无权访问他人设置页面
        return render_template('404.html'),404
    
    if request.method == 'POST':
        if 'codeSetting' in request.form:                           #修改密码
            oldPassword = request.form['oldPassword']               #验证原密码
            newPassword = request.form['newPassword']               #新密码
            newRepassword = request.form['newRepassword']           #新确认密码
            if not check_password_hash(user[1], oldPassword):
                error = '原密码输入有误'
            elif newPassword != newRepassword:
                error = '两次密码不一致'
                
            if error is None:
                flash("密码修改成功！")
                cursor.execute(
                    'UPDATE user SET password = %s WHERE uuid = %s;'
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

@userpagebp.route('/<int:id>/setgroup/<group>')
@loginRequired
def setGroup(id, group):        #设置禁言和解除禁言
    database = getDatabase()
    cursor = database.cursor()
    username = getUserName(cursor, id)
    oldgroup = getPartData(cursor, 'userinfo', 'uuid', id, 'permission')    #被操作人的原来用户组
    error = None       #错误信息
    if  username is None       or\
        g.userinfo[2] == 'ban' or g.userinfo[2] == 'normal' or\
        (group != 'ban'        and group != 'unban'        )or\
        oldgroup[0] == 'admin' or\
        (oldgroup[0].startswith('part') and g.userinfo[2].startswith('part')):
        return render_template('404.html'),404

    group = 'normal' if group == 'unban' else group
    cursor.execute(
        'UPDATE userinfo SET permission=%s WHERE uuid=%s;', (group, id,)
    )
    return redirect(url_for('userpage.showUserpage', id=id))


