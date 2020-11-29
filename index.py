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

@indexbp.route('/')
def index():
    # 主页
    # 主要包括各板块最新和最热的帖子标题、用户头像、id、昵称、积分、积分排行榜
    database = getDatabase()
    cursor = database.cursor()
    post = {findLatestPosts(cursor, 1), findHottestPosts(cursor, 1), findLatestPosts(cursor, 2), findHottestPosts(cursor, 2),
            findLatestPosts(cursor, 3), findHottestPosts(cursor, 3), findLatestPosts(cursor, 4), findHottestPosts(cursor, 4)}
   
    return render_template('index.html', postdata = post)


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
    cursor.execute(
        'SELECT * FROM post WHERE type=%s ORDER BY posttime DESC;', (type, )
    )
    post = cursor.fetchmany(3)
    return post

def findHottestPosts(cursor, type):
    cursor.execute(
        'SELECT * FROM post WHERE type=%s ORDER BY visit DESC;', (type, )
    )
    post = cursor.fetchmany(3)
    return post