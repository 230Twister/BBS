import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from .database import getDatabase

partsbp = Blueprint('parts', __name__, url_prefix='/parts')

@partsbp.route('/')
def getPartsData():
    if g.user is None:
        return redirect(url_for('auth.login'))
    database=getDatabase()
    cursor=database.cursor()
    study='study'
    techshare='techshare'
    entertain='entertain'
    studypart=cursor.execute(
        'SELECT * FROM post WHERE classification=%s'
        'ORDER BY updatetime DESC;',(study,)
        ).fetchall()
    techsharepart=cursor.execute(
        'SELECT * FROM post WHERE classification=%s'
        'ORDER BY updatetime DESC;',(techshare,)
        ).fetchall()
    entertainpart=cursor.execute(
        'SELECT * FROM post WHERE classification=%s'
        'ORDER BY updatetime DESC;',(entertain,)
        ).fetchall()
    return render_template('parts.html', parts={'study':studypart,
                                                'techshare':techsharepart,
                                                'entertain':entertainpart})

