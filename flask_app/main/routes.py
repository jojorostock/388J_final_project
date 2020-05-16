# 3rd-party packages
from flask import render_template, request, redirect, url_for, flash, Response, send_file, Blueprint
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from PIL import Image
import pyotp, qrcode
from qrcode.image import svg
# stdlib
from datetime import datetime
import io
import base64

# local
from flask_app import bcrypt, client, mongo_lock, session, messaging, client2
from flask_app.forms import (SearchForm, GameCommentForm, RegistrationForm, LoginForm,
                             UpdateUsernameForm, UpdateProfilePicForm)
from flask_app.models import User, Comment, load_user
from flask_app.utils import current_time

# API
# IDs for leagues
NFL_ID = 4391
MLB_ID = 4424
NBA_ID = 4387
MLS_ID = 4340
NHL_ID = 4380



main = Blueprint("main", __name__)

@main.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('main.query_results', query=form.search_query.data))

    return render_template('home.html', form=form)

@main.route('/leagues')
def leagues():
    # ls = api.Search().Leagues(country="England",sport="Soccer")
    ls = client2.getLeagues("United States")
    return render_template('leagues.html', leaguesList = ls)

@main.route('/events')
def events():

    nfl_events = client2.getLeagueLastFifteen(league_id = NFL_ID)
    mlb_events = client2.getLeagueLastFifteen(league_id = MLB_ID)
    nba_events = client2.getLeagueLastFifteen(league_id = NBA_ID)
    mls_events = client2.getLeagueLastFifteen(league_id = MLS_ID)
    nhl_events = client2.getLeagueLastFifteen(league_id = NHL_ID)
    return render_template('events.html', NFL_events = nfl_events, MLB_events = mlb_events, NBA_events = nba_events,MLS_events = mls_events,NHL_events = nhl_events)

@main.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    results = client2.searchTeams(query)

    if type(results) == dict:
        return render_template('query.html', error_msg=results['Error'])
    
    return render_template('query.html', results=results)

@main.route('/leagues/<league_id>', methods=['GET', 'POST'])
def league_detail(league_id):
    result = client2.getLeagueByID(league_id)
    teams = client2.getTeamsInALeague(league_id)

    return render_template('league_detail.html', league=result, teams=teams)


@main.route('/games/<game_id>', methods=['GET', 'POST'])
def game_detail(game_id):
    result = client2.getEventByID(game_id)

    # if type(result) == dict:
    #     return render_template('game_detail.html', error_msg=result['Error'])

    form = GameCommentForm()
    if form.validate_on_submit():
        comment = Comment(
            commenter=load_user(current_user.username), 
            content=form.text.data, 
            date=current_time(),
            game_id=game_id,
        )

        mongo_lock.acquire()
        comment.save()
        mongo_lock.release()

        return redirect(request.path)

    mongo_lock.acquire()
    comments_m = Comment.objects(imdb_id=game_id)
    mongo_lock.release()

    comments = []
    for r in comments_m:
        comments.append({
            'date': r.date,
            'username': r.commenter.username,
            'content': r.content,
        })


    return render_template('game_detail.html', form=form, game=result, comments=comments)

@main.route('/teams/<team_id>', methods=['GET', 'POST'])
def team_detail(team_id):
    result = client2.getTeamByID(team_id)
    lastFive = client2.getTeamLastFive(team_id)
    nextFive = client2.getTeamLastFive(team_id, nextFive=True)

    # if type(result) == dict:
    #     return render_template('game_detail.html', error_msg=result['Error'])

    return render_template('team_detail.html', team=result, teamLastFive=lastFive, teamNextFive=nextFive)

@main.route('/project')
def project():
    return render_template('project.html')
