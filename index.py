import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, Response
)
from .database import getDatabase
from .auth import loginRequired
from PIL import Image
import time, datetime, re
from .api import readImg, getData, getGroupName

indexbp = Blueprint('index', __name__, url_prefix='/index')

@indexbp.route('/')
def index():
    # 主页
    # 主要包括各板块最新和最热的帖子标题、用户头像、id、昵称、积分、积分排行榜
    database = getDatabase()
    cursor = database.cursor()
    post = [findLatestPosts(cursor, 1), findLatestPosts(cursor, 2),
            findLatestPosts(cursor, 3), findLatestPosts(cursor, 4)]
    highestusers = findHighestPoints(cursor)

    return render_template('index.html', indexdata = [post, highestusers])


@indexbp.route('/search', methods=('GET', 'POST'))
def search():
    # 搜索
    database = getDatabase()
    cursor = database.cursor()
    if request.method == 'POST':
        search = request.form['search']                                 #搜索的内容，会搜索出与此字符串相关度较高的帖子
        searchposts = findSearchPost(cursor, search)                    #搜索结果

        return render_template('search.html', searchposts=[searchposts, search])

    return render_template('search.html')


def findUser(cursor, id):
    # 从user中查找用户记录
    return getData(cursor, 'user', 'uuid', id)


def findUserinfo(cursor, id):
    # 从userinfo获取用户记录
    return getData(cursor, 'userinfo', 'uuid', id)


def findLatestPosts(cursor, type):
    # 从post中按发布时间排序，取最新的4条
    cursor.execute(
        'SELECT * FROM post WHERE type=%s ORDER BY posttime DESC;', (type, )
    )
    _post = cursor.fetchmany(4)
    post = []
    for p in _post:
        post.append([p[1], findUser(cursor, p[4])[1], 10])
    return post


def findHighestPoints(cursor):
    # 从userinfo中按积分排序，取积分最高的15个用户
    cursor.execute(
        'SELECT * FROM userinfo ORDER BY point DESC;'
    )
    users = cursor.fetchmany(15)
    user = []
    for u in users:
        user.append([u[0], findUser(cursor, u[0])[1], u[4]])
    return user

def findSearchPost(cursor, search):
    # 根据search内容找到相关的帖子
    cursor.execute(
        'SELECT * FROM post WHERE title LIKE %s ORDER BY visit DESC', ('%' + search + '%', )
    )
    _searchposts = cursor.fetchall()
    searchposts = []
    for p in _searchposts:
        searchposts.append([p[1], findUser(cursor, p[4])[1], 10])
    return searchposts
