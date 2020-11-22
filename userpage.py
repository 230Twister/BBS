import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from werkzeug.security import check_password_hash, generate_password_hash
from .database import getDatabase
from .auth import loginRequired

userpagebp = Blueprint('userpage', __name__, url_prefix='/userpage')

@userpagebp.route('/<int:id>')
def showUserpage(id):
    # 显示用户的个人主页
    # 主要包括个人信息，如昵称、（头像）、邮箱、关注、收藏、积分等
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    userinfo = findUserinfo(cursor, id)
    #error = None
    if user is None:
        return render_template('404.html'),404
    
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

    return render_template('userpage.html', userpagedata = {user, userinfo})


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
    # 用户设置，允许用户自行更改昵称、（头像）、密码、邮箱等
    database = getDatabase()
    cursor = database.cursor()
    user = checkUser(cursor, id)
    error = None
    if user is None or g.user[0] != user[0]:
        # 用户不存在 或 无权访问他人设置页面
        return render_template('404.html'),404

    # 允许用户开始设置
    if request.method == 'POST':
        #newUsername = request.form['newUsername']       #新用户名
        #newMail = request.form['newMail']               #新邮箱
        oldPassword = request.form['oldPassword']       #验证原密码
        newPassword = request.form['newPassword']       #新密码
        newRepassword = request.form['newRepassword']   #新确认密码

        if 'settings' in request.form:
            #settingusername = reCheckUsername(cursor, newUsername)
            #settingmail = reCheckMail(cursor, newMail)
            #if settingusername is not None:
                #error = '此用户名已被占用'
            #elif settingmail is not None:
                #error = '此邮箱已被占用'
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
                return redirect(url_for('userpage.showUserpage'))
            flash(error)
            return render_template('userpage.html', userdata={  "oldPassword":oldPassword,
                                                                "newPassword":newPassword,
                                                                "newRepassword":newRepassword})
        
    return render_template('userpage.html', userdata={})


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

'''
def reCheckUsername(cursor, username):
    # 检查用户重新设置的用户名是否被占用
    cursor.execute(
        'SELECT * FROM user WHERE name=%s', (name, )
    )
    settingusername = cursor.fetchone()                        #从数据库查找用户记录
    return settingusername

def reCheckMail(cursor, email):
    # 检查用户重新设置的用户名是否被占用
    cursor.execute(
        'SELECT * FROM user WHERE email=%s', (email, )
    )
    settingmail = cursor.fetchone()                        #从数据库查找用户记录
    return settingmail
'''