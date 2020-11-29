import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from .database import getDatabase


postsbp = Blueprint('posts', __name__, url_prefix='/posts')

@postsbp.route('/<int::postid>')                #标注编号
def posts(postid):
    if g.user is None:
        return redirect(url_for('auth.login'))
    database=getDatabase()
    cursor=database.cursor
    postdata=cursor.execute('SELECT * FROM post WHERE id=%s;',(postid,)).fetchone()

    cursor.execute('UPDATE post SET visit = %d WHERE id = %d;'        #更新阅读量
                    , (postdata[8]+1,postdata[0])
                   )
    replyinfo=GetReplyInfo(cursor,postdata)
    
    if postdata is None:
        return render_template('404.html'),404
    return render_template('posts.html', postdata=postdata,replyinfo=replyinfo)#replyinfo为列表中套元组的结构


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


@postsbp.route('/<int::postid>/reply', methods=('GET', 'POST'))
def reply(id,postid):
    if g.user is None:
        return redirect(url_for('auth.login'))
    database=getDatabase()
    cursor=database.cursor
    postdata=cursor.execute('SELECT * FROM post WHERE id=%s',(postid)).fetchone()
    if request.methods=='POST':
        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = request.form['text']
        
        cursor.execute(
                    'INSERT INTO reply(id, userid , content, posttime, updatetime, reply)'
                    'VALUES(null, %d, %d, %s, %s, %d, %d);'
                    , (  g.user[0],text, dtime, dtime, '', id)
                )
        updatedreply=postdata[8]+' '+str(replyid)
        cursor.execute('UPDATE post SET reply = %s WHERE id = %d;'        #更新本帖回复id
                    , (updatedreply,postdata[0])
                   )
        return render_template('post.html')
    return render_template('reply.html')

def GetReplyInfo(cursor,postdata):
    replyidlist=postdata[7].split(' ')
    replyidlist.remove('')
    replyinfo=[]
    for value in replyidlist:
        replyinfo.append(cursor.execute('SELECT * FROM reply WHERE id=%s;',(value,)).fetchone())
    return replyinfo


