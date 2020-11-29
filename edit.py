from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
import os, datetime
from PIL import Image

from .auth import loginRequired
from .database import getDatabase

editbp = Blueprint('edit', __name__, url_prefix='/edit')

@editbp.route('/<part>')
@loginRequired
def create(part):
    database = getDatabase()
    cursor = database.cursor()
    #创建新主题
    cursor.execute(
                'INSERT INTO post(id, title, type, content, userid, posttime, updatetime, reply, visit, collect)'
                'VALUES(null, '', %s, '', %s, %s, %s, '', %s, %s);'
                , (part, g.user[0], dtime, dtime, 1, 0)
            )
    cursor.execute(
        'SELECT LAST_INSERT_ID();'
    )
    return redirect(url_for(edit.edit), id=cursor.fetchone())

@editbp.route('/<int:id>', methods=('GET', 'POST'))
@loginRequired
def edit(id):
    database = getDatabase()
    cursor = database.cursor()
    cursor.execute(
        'SELECT * FROM post WHERE id=%s;' ,(id,)
    )
    post = cursor.fetchone()
    if post is None or post[4] != g.user[0]:        #若不存在这个主题或楼主不是当前访问用户
        return render_template('404.html')          #返回404

    if request.method == 'POST':
        title = request.form['title']       #标题
        content = request.form['content']   #内容
        _type = request.form['type']        #发往的版块

        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
                    'UPDATE post SET title=%s, type=%s, content=%s, updatetime=%s WHERE id=%s;'
                    , (title, _type, content, dtime, id,)
                )
        return redirect(url_for('index.index'))
            
    return render_template('post/edit.html', post=post)

@editbp.route('/delete/<int:id>')
@loginRequired
def delete(id):
    database = getDatabase()
    cursor = database.cursor()
    cursor.execute(
        'SELECT * FROM post WHERE id=%s;' ,(id,)
    )
    post = cursor.fetchone()
    if post is None or post[4] != g.user[0]:        #若不存在这个主题或楼主不是当前访问用户
        return render_template('404.html')          #返回404

    cursor.execute(
        'DELETE FROM post WHERE id=%s;', (id,)
    )

@editbp.route('/upload', methods=('GET', 'POST'))
@loginRequired
def upload():
    if request.method == 'POST':
        file = request.files.get('editormd-image-file')     #获取上传的图片
        if not file:
            result = {
                'success':0,
                'message':'上传失败'
            }
        else:
            ext = os.path.splitext(file.filename)[1]
            filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ext
            current_path = os.path.abspath(os.path.dirname(__file__))       #获取当前文件夹绝对路径
            filedir = os.path.join(current_path, 'data\\img')               #获取保存图片的路径
            filepath = os.path.join(filedir, g.user[1])                     #获取当前用户保存图片的路径
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            file.save(os.path.join(filepath, filename))
            result = {
                'success':1,
                'message':'上传成功',
                'url':url_for('edit.image', name=filename)
            }
        return result

@editbp.route('/image/<name>')
@loginRequired
def image(name):
    current_path = os.path.abspath(os.path.dirname(__file__))
    filedir = os.path.join(current_path, 'data\\img')
    filepath = os.path.join(filedir, g.user[1])         #获取图片文件路径

    with open(os.path.join(filepath, name), 'rb') as f:
        res = Response(f.read(), mimetype="image/jpeg")
    return res          #返回图片

