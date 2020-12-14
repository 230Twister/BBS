import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from .database import getDatabase
from .api import readImg, getData
partsbp = Blueprint('parts', __name__, url_prefix='/parts')

@partsbp.route('/<int:type>/<int:page>')
def parts(type, page):
    database = getDatabase()
    cursor = database.cursor()
    
    cursor.execute(
       'SELECT id,title,userid,updatetime,reply FROM post WHERE type=%s ORDER BY updatetime DESC;',(type,)
       )
    partdata = cursor.fetchall()
    partdata, pages = getPosts(cursor, partdata, page)
    
    return render_template('post/parts.html', 
                           partdata = partdata,           #板块内的帖子(最新)
                           pages = pages                  #当前页数和总页数
                           )

#生成某一页的帖子
def getPosts(cursor, partdata, page):
    length = len(partdata)
    partdata = [partdata[x:x + 25] for x in range(0, length, 25)]   #每页25个帖子
    pagecnt = len(partdata)                 #总共页数
    if pagecnt > 0:
        partdata = partdata[page - 1]
    partinfo = []

    for value in partdata:
        user = getData(cursor, 'user', 'uuid', value[2])
        partinfo.append([value[0], value[1], user[1], value[3], len(value[4].split(' '))])    #标题 用户 更新时间 回复数
    
    return partinfo, [page, pagecnt]
    

