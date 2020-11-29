import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from .database import getDatabase

postsbp = Blueprint('posts', __name__, url_prefix='/posts')

@posts.route('/<int::postid>')
def getPostData(postid):
    if g.user is None:
        return redirect(url_for('auth.login'))
    database=getDatabase()
    cursor=database.cursor
    postdata=cursor.execute('SELECT * FROM post WHERE id=%s',(postid)).fetchone()
    if postdata is None:
        return render_template('404.html'),404
    return render_template('posts.html', postdata=postdata)



