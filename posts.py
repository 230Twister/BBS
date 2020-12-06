import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for, current_app)
import datetime
from .auth import loginRequired
from .database import getDatabase
from .api import getData, getGroupName
postsbp = Blueprint('posts', __name__, url_prefix='/posts')


@postsbp.route('/<int:postid>/posts/<int:page>')  #标注编号
def posts(postid, page):
    database = getDatabase()
    cursor = database.cursor()
    cursor.execute('SELECT * FROM post WHERE id=%s;', (postid, ))
    postdata = cursor.fetchone()

    if postdata is None:
        return render_template('404.html'), 404
    
    hostinfo = getUserDisplay(getData(cursor, 'user', 'uuid', postdata[4]), getData(cursor, 'userinfo', 'uuid', postdata[4]), True, g.user[0] if g.user else 0)
    cursor.execute(
        'UPDATE post SET visit = %s WHERE id = %s;'  #更新阅读量
        ,(int(postdata[8]) + 1, postdata[0]))
    replyinfo, replysize, pages = getReplyInfo(cursor, postdata, page)
    return render_template( 'post/detail.html',
                            postdata = postdata,            #帖子信息
                            replysize = replysize,          #回复条数
                            replyinfo = replyinfo,          #帖子回复信息
                            pages = pages,                  #当前页数与总页数
                            loops = range(1, pages[1] + 1),
                            hostinfo = hostinfo)            #楼主信息

@postsbp.route('/<int:postid>/collect')
@loginRequired
def collect(postid):
    database = getDatabase()
    cursor = database.cursor()

    if not checkUserCollect(cursor, g.user[0]):
        cursor.execute('SELECT * FROM post WHERE id=%s;',(postid, ))
        postdata = cursor.fetchone()
        cursor.execute(
            'UPDATE post SET collect = %s WHERE id = %s;'                       #更新本帖收藏量
            ,(int(postdata[9]) + 1, postid,))
        appendData(cursor, 'userinfo', 'uuid', g.user[0], 'collect', 3, postid)     #用户的收藏增加
    return redirect(url_for('posts.posts', postid = postid, page = 1))

@postsbp.route('/<int:postid>/uncollect')
@loginRequired
def uncollect(postid):
    database = getDatabase()
    cursor = database.cursor()
    if checkUserCollect(cursor, g.user[0], True):
        pass

    return redirect(url_for('posts.posts', postid = postid, page = 1))

@postsbp.route('/<int:postid>/reply', methods=('GET', 'POST'))
@loginRequired
def reply(postid):
    if request.method == 'POST':
        database = getDatabase()
        cursor = database.cursor()
        cursor.execute('SELECT * FROM post WHERE id=%s', (postid))
        postdata = cursor.fetchone()
        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = request.form['content']

        cursor.execute(
            'INSERT INTO reply(id, userid , content, posttime)'
            'VALUES(null, %s, %s, %s);',
            (g.user[0], text, dtime))                               #增加新回复
        cursor.execute('SELECT LAST_INSERT_ID();')                  #新回复的id
        replyid = cursor.fetchone()

        updatedreply = postdata[7] + ' ' + str(replyid[0])
        cursor.execute(
            'UPDATE post SET reply = %s WHERE id = %s;'                                 #更新本帖回复id
            ,(updatedreply, postdata[0]))
        appendData(cursor, 'userinfo', 'uuid', postdata[4], 'warn', 1, postdata[0])     #楼主的提醒加一

    return redirect(url_for('posts.posts', postid = postid, page = 1))

#生成回复
def getReplyInfo(cursor, postdata, page):
    replyidlist = postdata[7].split(' ')
    replyidlist.remove('')
    length = len(replyidlist)
    replyidlist = [replyidlist[x:x + 15] for x in range(0, length, 15)]        #分割，每一页15楼
    pagecnt = len(replyidlist)
    if pagecnt > 0:
        replyidlist = replyidlist[page - 1]
    replyinfo = []

    for value in replyidlist:
        reply = getData(cursor, 'reply', 'id', value)
        user = getUserDisplay(getData(cursor, 'user', 'uuid', reply[1]), getData(cursor, 'userinfo', 'uuid', reply[1]))
        replyinfo.append([reply, user])
    return replyinfo, length, [page, pagecnt]

#获取用户展示使用的信息
def getUserDisplay(user, info, flag = False, postid = 0):
    display = [user[0], user[1], info[4]]
    display.append(int(int(info[4]) / 100))
    display.append(getGroupName(info[2]))
    display.append(int(info[4]) % 100)
    display.append(0)

    if flag:
        collected = info[3].split(' ')
        display[6] = (str(postid) in collected)
    return display

#扩展数据
def appendData(cursor, table, key, value, indexkey, index, add):
    cursor.execute(
        'SELECT * FROM ' + table + ' WHERE ' + key + ' =%s;', (value,)
    )
    origin = cursor.fetchone()
    res = str(origin[index]) + ' ' + str(add)
    cursor.execute(
        'UPDATE '+ table + ' SET ' + indexkey + ' =' + res + ' WHERE ' + key + ' =%s;', (value,)
    )

#检查用户是否有某个帖子收藏
def checkUserCollect(cursor, id, flag = False):
    info = getData(cursor, 'userinfo', 'uuid', g.user[0])
    collected = info[3].split(' ')

    if str(id) in collected:
        if flag:
            collected.remove(str(id))
            result = ''
            for col in collected:
                result = result + col + ' '
            cursor.execute(
                'UPDATE userinfo SET collect=%s WHERE uuid=%s;', (result, g.user[0],)
            )
        return True
    else:
        return False

