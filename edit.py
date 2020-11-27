from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
import os, datetime
from PIL import Image

from auth import loginRequired
from database import getDatabase

editbp = Blueprint('edit', __name__, url_prefix='/edit')

@editbp.route('/', methods=('GET', 'POST'))
@loginRequired
def edit():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        _type = request.form['type']

        database = getDatabase()
        cursor = database.cursor()
        dtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
                    'INSERT INTO post(id, title, type, content, userid, posttime, updatetime, reply, visit, collect)'
                    'VALUES(null, %s, %s, %s, %s, %s, %s);'
                    , (title, _type, content, g.user[0], dtime, dtime, '', 1, 0)
                )
        return redirect(url_for('index.index'))
            
    return render_template('edit.html')

@editbp.route('/upload', methods=('GET', 'POST'))
@loginRequired
def upload():
    if request.method == 'POST':
        file = request.files.get('editormd-image-file')     #获取上传的图片
        image = Image.open(file)
        image.save(file)
        if not file:
            result = {
                'success':0,
                'message':'上传失败'
            }
        else:
            ext = os.path.splitext(file.filename)[1]
            filename = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ext
            current_path = os.path.abspath(os.path.dirname(__file__))       #获取当前文件夹绝对路径
            filedir = os.path.join(current_path, 'static\\asset\\img')      #获取保存图片的路径
            filepath = os.path.join(filedir, g.user[1])                     #获取当前用户保存图片的路径
            if os.path.exists(filepath):
                os.mkdir(filepath)
            file.save(os.path.join(filepath, filename))
            result = {
                'success':1
                'message':'上传成功'
                'url':url_for('edit.image', name=filename)
            }
        return result

@editbp.route('/image/<name>')
@loginRequired
def image(name):
    current_path = os.path.abspath(os.path.dirname(__file__))
    filedir = os.path.join(current_path, 'static\\asset\\img')
    filepath = os.path.join(filedir, g.user[1])         #获取图片文件路径

    with open(os.path.join(filepath, name), 'rb') as f:
        res = Response(f.read(), mimetype="image/jpeg")
    return res          #返回图片

