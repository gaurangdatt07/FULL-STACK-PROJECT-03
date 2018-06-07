from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import Base, Club, Player, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response, flash
import requests
import httplib2
app = Flask(__name__)
engine = create_engine(
    'sqlite:///clubinfo.db',
    connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ClubApp"


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response
        (json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

"""
    Created a new user by fetching its email_id.
"""


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
        # execute http get req to revoke current token.
    access_token = login_session['access_token']
    print ("token -> ", access_token)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        # disconnecting the users.
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        # Response to indicate users has successfully logout from application.
        print "Successfully disconnected"
        clubs = session.query(Club).all()
        # Back to lmain page as user should see items even though he has not sign in.   # noqa
        return render_template('clubs.html', clubs=clubs)
    else:
        # For whatever reason, the given token was invalid and something went wrong in disconnect process.   # noqa
        print (login_session['access_token'])
        print "Failed to revoke token for given user."
        return redirect(url_for('showClubs'))


@app.route('/club/<int:club_id>/player/JSON')
def clubPlayerJSON(club_id):
    club = session.query(Club).filter_by(id=club_id).one()
    players = session.query(Player).filter_by(
        club_id=club_id).all()
    return jsonify(Players=[i.serialize for i in players])


@app.route('/club/<int:club_id>/player/<int:player_id>/JSON')
def PlayerJSON(club_id, player_id):
    player = session.query(Player).filter_by(id=player_id).one()
    return jsonify(player=player.serialize)


@app.route('/club/JSON')
def clubsJSON():
    clubs = session.query(Club).all()
    return jsonify(clubs=[r.serialize for r in clubs])


# Show all clubs
@app.route('/')
def mainpage():
    showLogin()
    # menu=session.query(MenuItem).all()
    if login_session.has_key('email') and login_session['email']:
        print "hello"
        flag = 1
        return render_template('clubs.html', STATE=login_session['state'], name=login_session['username'], image=login_session['picture'])  # noqa
    flag = 0
    if login_session.has_key('email') and login_session['email']:
        flag = 1
        return render_template('clubs.html', STATE=login_session['state'], name=login_session['username'], image=login_session['picture'])   # noqa
    return render_template('clubs.html', STATE=login_session['state'], flag=flag, name='', image='')   # noqa


@app.route('/club')
def showClubs():

    clubs = session.query(Club).all()
    if 'username' not in login_session or login_session['username'] is None:
        login = 0
    else:
        login = 1
    return render_template(
        'clubs.html', clubs=clubs, login_session=login_session, login=login)

# Create a new Club


@app.route('/club/new/', methods=['GET', 'POST'])
def newClub():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newClub = Club(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newClub)
        flash('New club %s Successfully Created' % newClub.name)
        session.commit()
        return redirect(url_for('showClubs'))
    else:
        return render_template('newClub.html')
# Edit a club


@app.route('/club/<int:club_id>/edit/', methods=['GET', 'POST'])
def editClub(club_id):
    editedClub = session.query(Club).filter_by(id=club_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedClub.user_id != login_session['user_id']:
            flash('You are not authorized to edit this Club')
            return redirect(url_for('showClubs'))
    if request.method == 'POST':
        if request.form['name']:
            editedClub.name = request.form['name']
            return redirect(url_for('showClubs', club_id=club_id))
    else:
        return render_template(
            'editClub.html', club=editedClub)
# Delete a club


@app.route('/club/<int:club_id>/delete/', methods=['GET', 'POST'])
def deleteClub(club_id):
    clubToDelete = session.query(Club).filter_by(id=club_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if (
        clubToDelete and clubToDelete.user_id) != (
            login_session['user_id']):
        flash('You are not authorized to delete this club')
        return redirect(url_for('showClubs'))
    if request.method == 'POST':
        session.delete(clubToDelete)
        flash('{name} Successfully Deleted'.format(name=clubToDelete.name))   # noqa
        session.commit()
        return redirect(
            url_for('showClubs', club_id=club_id))
    else:
        return render_template(
            'deleteClub.html', club=clubToDelete)
# Show a club player


@app.route('/club/<int:club_id>/')
@app.route('/club/<int:club_id>/player/')
def showPlayer(club_id):
    club = session.query(Club).filter_by(id=club_id).one()
    players = session.query(Player).filter_by(
        club_id=club_id).all()
    if 'username' not in login_session:
        return render_template(
            'clubs.html',
            players=players,
            club=club)
    else:
        return render_template(
            'player.html',
            players=players,
            club=club,
            login_session=login_session)

# Sign a new Club Player


@app.route(
    '/club/<int:club_id>/player/new/', methods=['GET', 'POST'])
def newPlayer(club_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newPlayer = Player(name=request.form['name'], description=request.form[
                           'description'], jersey=request.form['jersey'],
                           position=request.form['position'], club_id=club_id,
                           user_id=login_session['user_id'])
        session.add(newPlayer)
        flash('Player Successfully Signed')
        session.commit()

        return redirect(url_for('showPlayer', club_id=club_id))
    else:
        return render_template('newplayer.html', club_id=club_id)

# Edit a Club Player


@app.route('/club/<int:club_id>/player/<int:player_id>/edit',
           methods=['GET', 'POST'])
def editPlayer(club_id, player_id):
    editedPlayer = session.query(Player).filter_by(id=player_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedPlayer.user_id != login_session['user_id']:
        flash('You are not authorized to edit Player')
        return redirect(url_for('showClubs', club_id=club_id))

    if request.method == 'POST':
        if request.form['name']:
            editedPlayer.name = request.form['name']
        if request.form['description']:
            editedPlayer.description = request.form['description']
        if request.form['jersey']:
            editedPlayer.jersey = request.form['jersey']
        if request.form['position']:
            editedPlayer.position = request.form['position']
        session.add(editedPlayer)
        flash('Player Successfully Edited')
        session.commit()
        return redirect(url_for('showPlayer', club_id=club_id))
    else:

        return render_template(
            'editplayer.html', club_id=club_id,
            player_id=player_id, player=editedPlayer)
# Delete a Club Player


@app.route('/club/<int:club_id>/player/<int:player_id>/delete',
           methods=['GET', 'POST'])
def deletePlayer(club_id, player_id):
    playerToDelete = session.query(Player).filter_by(id=player_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if playerToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete this player')
        return redirect(url_for('showClubs'))

    if request.method == 'POST':
        session.delete(playerToDelete)
        flash('Player Successfully deleted')
        session.commit()
        return redirect(url_for('showPlayer', club_id=club_id))
    else:
        return render_template(
            'deleteplayer.html', player=playerToDelete, club_id=club_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
