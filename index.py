from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

indexbp = Blueprint('index', __name__, url_prefix='/index')

@indexbp.route('/')
def index():
    return render_template('index.html')