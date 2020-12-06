import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from .database import getDatabase
from .api import readImg
partsbp = Blueprint('parts', __name__, url_prefix='/parts')

@partsbp.route('/<int:type>')
def parts(type):
    database=getDatabase()
    cursor=database.cursor()
    
    part_new=cursor.execute(
       'SELECT * FROM post WHERE type=%s ORDER BY updatetime DESC;',(type,)
       ).fetchall()
    part_hot=cursor.execute(
       'SELECT * FROM post WHERE type=%s ORDER BY visit DESC;',(type,)
       ).fetchall()

    parts={'new':part_new,
           'hot':part_hot
          }

    size=len(part_new)    #热帖和新帖排序后总帖数相同
    photos=[]
    for i in range(6):
        photos.append(readImg(part_hot[i][4]),'avatar.jpg')

    if g.user:
        avatar=readImg(g.user[0],'avatar.jpg')
        user=cursor.execute('SELECT * FROM user WHERE uuid=%s;', (g.user[0], ))
        userinfo=cursor.execute('SELECT * FROM userinfo WHERE uuid=%s;', (g.user[0], ))
        username=user[1]
        point=userinfo[4]
    else:
        avatar=None
        username=None
        point=None
    _user={'avatar':avatar,
           'name':username,
           'point':point
           }
    return render_template('parts.html', 
                           parts=parts,               #板块内的帖子(最新、最热)
                           size=size,                 #板块内帖子数目
                           photos=photos,             #最热帖的图片
                           user=_user                 #如果登陆的话会有用户信息
                           )
