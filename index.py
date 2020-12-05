import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)
from .database import getDatabase
from .auth import loginRequired
from PIL import Image
import time, datetime, re
from .api import readImg

indexbp = Blueprint('index', __name__, url_prefix='/index')

@indexbp.route('/', methods=('GET', 'POST'))
def index():
    # 主页
    # 主要包括各板块最新和最热的帖子标题、用户头像、id、昵称、积分、积分排行榜
    database = getDatabase()
    cursor = database.cursor()
    post = {findLatestPosts(cursor, 1), findHottestPosts(cursor, 1), findLatestPosts(cursor, 2), findHottestPosts(cursor, 2),
            findLatestPosts(cursor, 3), findHottestPosts(cursor, 3), findLatestPosts(cursor, 4), findHottestPosts(cursor, 4)}
    highestusers = findHighestPoints(cursor)
   
    # 搜索
    if request.methods == 'POST':
        search = request.form['search']                                 #搜索的内容，会搜索出与此字符串相关度较高的帖子
        searchposts = findSearchPost(cursor, search)                    #搜索结果

        return render_template('index.html', indexdata = [post, highestusers, searchposts])

    return render_template('index.html', indexdata = [post, highestusers])


def findUser(cursor, id):
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

def findLatestPosts(cursor, type):
    # 从post中按发布时间排序，取最新的3条
    cursor.execute(
        'SELECT * FROM post WHERE type=%s ORDER BY posttime DESC;', (type, )
    )
    post = cursor.fetchmany(3)
    return post

def findHottestPosts(cursor, type):
    # 从post中按热度排序，取最热的3条
    cursor.execute(
        'SELECT * FROM post WHERE type=%s ORDER BY visit DESC;', (type, )
    )
    post = cursor.fetchmany(3)
    return post

def findHighestPoints(cursor):
    # 从userinfo中按积分排序，取积分最高的15个用户
    cursor.execute(
<<<<<<< HEAD
        'SELECT * FROM userinfo ORDER BY visit DESC;',
    )
    users = cursor.fetchmany(15)
    return users
=======
        'SELECT * FROM userinfo ORDER BY point DESC;'
    )
    users = cursor.fetchmany(15)
    return users

def findSearchPost(cursor, search):
    # 根据search内容找到相关的帖子
    cursor.execute(
        'SELECT * FROM post WHERE title LIKE %s ORDER BY visit DESC', ('%' + search + '%', )
    )
    searchposts = cursor.fetchall()
    return searchposts
>>>>>>> e3b2c443b14f4f7dbf72061ddca0f777e030a8cf
