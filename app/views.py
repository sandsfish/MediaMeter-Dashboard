import datetime
import json

import flask
import flask_login
import mediacloud
import mediacloud.api as mcapi
import mediacloud.media as mcmedia
import pymongo

from app import app, login_manager, mc
from user import User, authenticate_user
from forms import *

@app.route('/')
def index():
    content = flask.render_template('progress.html')
    return flask.render_template('main.html', content=content)

@app.route('/api/login', methods=['POST'])
def login():
    if flask_login.current_user.is_authenticated():
        # User is already logged in, confirm by sending user object
        response = {
            'username': flask_login.current_user.name
            , 'authenticated': True
            , 'anonymous': False
        }
        return json.dumps(response)
    # User is attempting new login, authenticate
    username = ''
    password = ''
    try:
        username = flask.request.form['username']
        password = flask.request.form['password']
    except KeyError:
        pass
    user = authenticate_user(username, password)
    if not user.is_authenticated():
        flask.abort(401)
    flask_login.login_user(user)
    response = {
        'username': username
        , 'authenticated': True
        , 'anonymous': False
    }
    return json.dumps(response)

@app.route('/api/user', methods=['POST'])
def user():
    if flask_login.current_user.is_authenticated():
        # User is already logged in, confirm by sending user object
        response = {
            'username': flask_login.current_user.name
            , 'authenticated': True
            , 'anonymous': False
        }
        return json.dumps(response)
    flask.abort(401)

@app.route('/api/logout', methods=['POST'])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    response = {
        'username': ''
        , 'authenticated': False
    }
    return json.dumps(response)

@app.route('/api/media')
@flask_login.login_required
def media():
    return json.dumps({
        'sources': list(mcmedia.all_sources())
        , 'sets': list(mcmedia.all_sets())
    });

@app.route('/api/media/sources')
@flask_login.login_required
def media_sources():
    return json.dumps(list(mcmedia.all_sources()))

@app.route('/api/media/sets')
@flask_login.login_required
def media_sets():
    return json.dumps(list(mcmedia.all_sets()))
    
@app.route('/api/sentences/<keywords>/<query>')
@flask_login.login_required
def sentences(keywords, query):
    res = mc.sentencesMatching(keywords , query)
    return json.dumps(res)
    
@app.route('/api/sentences/docs/<keywords>/<query>')
@flask_login.login_required
def sentence_docs(keywords, query):
    res = mc.sentencesMatching(keywords , query)
    return json.dumps(res['response']['docs'])
    
@app.route('/api/sentences/numfound/<keywords>/<media>/<start>/<end>')
@flask_login.login_required
def sentence_numfound(keywords, media, start, end):
    startdate = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    enddate = datetime.datetime.strptime(end, '%Y-%m-%d').date()
    num_days = (enddate - startdate).days + 1
    dates = [startdate + datetime.timedelta(x) for x in range(num_days)]
    dates = [date.strftime('%Y-%m-%d') for date in dates]
    results = []
    for date in dates:
        query = "+publish_date:[%sT00:00:00Z TO %sT23:59:59Z] AND %s" % (date, date, media)
        res = mc.sentencesMatching(keywords, query)
        results.append({
            'date': date
            , 'numFound': res['response']['numFound']
        })
    return json.dumps(results)
    
@app.route('/api/wordcount/<keywords>/<query>')
@flask_login.login_required
def wordcount(keywords, query):
    res = mc.wordCount(keywords , query)
    return json.dumps(res)
    
# Callback for flask-login
@login_manager.user_loader
def load_user(userid):
    return User(userid, userid)
