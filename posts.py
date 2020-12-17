import functools
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for, current_app)
import datetime
from .auth import loginRequired
from .database import getDatabase
from .api import getData, getPartData, getGroupName
postsbp = Blueprint('posts', __name__, url_prefix='/posts')

@postsbp.route('/<int:postid>/posts/<int:page>')  #标注编号
def posts(postid, page):
    database = getDatabase()
    cursor = database.cursor()
    cursor.execute('SELECT * FROM post WHERE id=%s;', (postid, ))
    postdata = cursor.fetchone()

    if postdata is None:
        return render_template('404.html'), 404
    
    #楼主信息
    hostinfo = getUserDisplay(  getPartData(cursor, 'user', 'uuid', postdata[4], 'uuid', 'name'), 
                                getPartData(cursor, 'userinfo', 'uuid', postdata[4], 'permission', 'point'))
    
    if postid not in session['posts']:
        cursor.execute(
            'UPDATE post SET visit=visit+1 WHERE id = %s;'     #更新阅读量
            , (postdata[0]),)
        temp = session['posts']
        temp.append(postid)
        session['posts'] = temp
    
    replyinfo, replysize, pages = getReplyInfo(cursor, postdata, page)
    isCollect = checkUserCollect(cursor, postid)        #是否有收藏
    return render_template( 'post/detail.html',
                            postdata = postdata,            #帖子信息
                            replysize = replysize,          #回复条数
                            replyinfo = replyinfo,          #帖子回复信息
                            pages = pages,                  #当前页数与总页数
                            loops = range(1, pages[1] + 1),
                            iscollect = isCollect,          #当前帖子是否被观看者收藏
                            hostinfo = hostinfo)            #楼主信息

@postsbp.route('/<int:postid>/collect')
@loginRequired
def collect(postid):
    database = getDatabase()
    cursor = database.cursor()

    if not checkUserCollect(cursor, postid):
        cursor.execute(
            'UPDATE post SET collect = collect+1 WHERE id = %s;'                    #更新本帖收藏量
            ,(postid,))
        appendData(cursor, 'userinfo', 'uuid', g.user[0], 'collect', 3, postid)     #用户的收藏增加
    return redirect(url_for('posts.posts', postid = postid, page = 1))

@postsbp.route('/<int:postid>/uncollect')
@loginRequired
def uncollect(postid):
    database = getDatabase()
    cursor = database.cursor()

    if checkUserCollect(cursor, postid, True):
        cursor.execute(
            'UPDATE post SET collect = collect-1 WHERE id = %s;'                    #更新本帖收藏量
            ,(postid,))
    return redirect(url_for('posts.posts', postid = postid, page = 1))

@postsbp.route('/<int:postid>/reply', methods=('GET', 'POST'))
@loginRequired
def reply(postid):
    if request.method == 'POST' and g.userinfo[2] != 'ban':
        database = getDatabase()
        cursor = database.cursor()
        postdata = getPartData(cursor, 'post', 'id', postid, 'id', 'userid')        #当前帖子id与楼主uuid
        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")   #当前时间
        text = request.form['content']                                  #回复内容

        cursor.execute(
            'INSERT INTO reply(id, userid , content, posttime)'
            'VALUES(null, %s, %s, %s);',
            (g.user[0], text, dtime))                               #增加新回复
        cursor.execute('SELECT LAST_INSERT_ID();')                  #新回复的id
        replyid = cursor.fetchone()

        updatedreply = ' ' + str(replyid[0])
        cursor.execute(
            'UPDATE post SET reply = CONCAT(reply,%s), updatetime = %s WHERE id = %s;'  #更新本帖回复id和更新时间
            ,(updatedreply, dtime, postid))
        cursor.execute(
            'UPDATE userinfo SET point=point+1 WHERE uuid=%s;', (g.user[0],)            #回复获得积分
        )

        if(postdata[1] != g.user[0]):                               #楼主的提醒加一
            appendData(cursor, 'userinfo', 'uuid', postdata[1], 'warn', 1, str(postdata[0])+':'+str(replyid[0]))     

    return redirect(url_for('posts.posts', postid = postid, page = 1))

#生成回复
def getReplyInfo(cursor, postdata, page):
    replyidlist = postdata[7].split(' ')
    if '' in replyidlist:
        replyidlist.remove('')
    length = len(replyidlist)           #回复数量
    replyidlist = [replyidlist[x:x + 15] for x in range(0, length, 15)]        #分割，每一页15楼
    pagecnt = len(replyidlist)          #总页数
    if pagecnt > 0:
        replyidlist = replyidlist[page - 1 if page - 1 < pagecnt else 0]
    replyinfo = []

    for value in replyidlist:
        reply = getData(cursor, 'reply', 'id', value)
        user = getUserDisplay(  getPartData(cursor, 'user', 'uuid', reply[1], 'uuid', 'name'), 
                                getPartData(cursor, 'userinfo', 'uuid', reply[1], 'permission', 'point'))
        replyinfo.append([reply, user])         #回复内容与回复人
    return replyinfo, length, [page if page <= pagecnt else 1, pagecnt]

#获取用户展示使用的信息
def getUserDisplay(user, info):
    display = [user[0], user[1], info[1]]
    display.append(int(int(info[1]) / 100))
    display.append(getGroupName(info[0]))
    display.append(int(info[1]) % 100)
    return display

#扩展数据
def appendData(cursor, table, key, value, indexkey, index, add):
    res = ' ' + str(add)
    cursor.execute(
        'UPDATE '+ table + ' SET ' + indexkey + ' =CONCAT('+indexkey+',%s) WHERE ' + key + ' =%s;', (res, value,)
    )

#检查用户是否有某个帖子收藏
def checkUserCollect(cursor, id, flag = False):
    if g.user is None:
        return False

    info = getData(cursor, 'userinfo', 'uuid', g.user[0])
    collected = info[3].split(' ')
    if '' in collected:
        collected.remove('')

    if str(id) in collected:
        if flag:                        #若存在且flag为true则删除
            collected.remove(str(id))
            result = ' '.join(collected)
            cursor.execute(
                'UPDATE userinfo SET collect=%s WHERE uuid=%s;', (result, g.user[0],)
            )
        return True
    else:
        return False

