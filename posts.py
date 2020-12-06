import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from .auth import loginRequired
from .database import getDatabase
from .api import readImg
postsbp = Blueprint('posts', __name__, url_prefix='/posts')

@postsbp.route('/<int::postid>')                #标注编号
def posts(postid):
    database=getDatabase()
    cursor=database.cursor
    postdata=cursor.execute('SELECT * FROM post WHERE id=%s;',(postid,)).fetchone()
    hostinfo=(postdata[4],readImg(postdata[4],'avatar.jpg'))
    cursor.execute('UPDATE post SET visit = %d WHERE id = %d;'        #更新阅读量
                    , (postdata[8]+1,postdata[0])
                   )
    replyinfo,avatar=GetReplyInfo(cursor,postdata)
    replysize=len(replyinfo)
    if postdata is None:
        return render_template('404.html'),404
    return render_template('posts.html', 
                           postdata=postdata,      #帖子信息
                           replysize=replysize,    #回复条数
                           replyinfo=replyinfo,    #帖子回复信息
                           avatar=avatar,          #帖子回复人的头像
                           hostinfo=hostinfo)      #楼主信息


@loginRequired
def collect(cursor,id,userid):
    postdata=cursor.execute('SELECT * FROM post WHERE id=%s;',(id,)).fetchone()
    cursor.execute('UPDATE post SET collect = %d WHERE id = %d;'        #更新本帖收藏量
                    , (postdata[9]+1,postdata[0])
                   )
    _userinfo=cursor.execute('SELECT * FROM userinfo WHERE uuid=%d;').fetchone()
    _text=_userinfo[3]+' '+str(id)
    cursor.execute('UPDATE userinfo SET collect = %s WHERE uuid = %d;'  #更新用户个人收藏
                    ,(_text,userid)
                   )

@loginRequired
@postsbp.route('/<int::postid>/reply', methods=('GET', 'POST'))
def reply(id,postid):
    database=getDatabase()
    cursor=database.cursor
    postdata=cursor.execute('SELECT * FROM post WHERE id=%s',(postid)).fetchone()
    if request.methods=='POST':
        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = request.form['text']
        
        cursor.execute(
                    'INSERT INTO reply(id, userid , content, posttime, updatetime, reply)'
                    'VALUES(null, %d, %d, %s, %s, %d, %d);'
                    , ( g.user[0],text, dtime, dtime, '', id)
                )
        updatedreply=postdata[7]+' '+str(replyid)
        cursor.execute('UPDATE post SET reply = %s WHERE id = %d;'        #更新本帖回复id
                    , (updatedreply,postdata[0])
                   )
        return render_template('post.html')
    return render_template('reply.html')

def GetReplyInfo(cursor,postdata):
    replyidlist=postdata[7].split(' ')
    replyidlist.remove('')
    replyinfo=[]
    avatar=[]
    for value in replyidlist:
        reply=cursor.execute('SELECT * FROM reply WHERE id=%s;',(value,)).fetchone()
        replyinfo.append(reply)
        avatar.append(readImg(reply[1],'avatar.jpg'))
    return replyinfo,avatar


