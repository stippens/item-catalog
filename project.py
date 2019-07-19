from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Media

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import re


#--retrieve client ID for google authentication--------------------------------
CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

#--Connect to Database and create database session-----------------------------
engine = create_engine('sqlite:///mediaCatalog.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


#******************************************************************************
#
# AUTHENTICATION ROUTES
#
#******************************************************************************


#=============================================================== showLogin() ==
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)



#================================================================ gconnect() ==
@app.route('/gconnect', methods=['POST'])
def gconnnect():
	#--validate state token-------------------------------------------------------
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#--obtain authorization code--------------------------------------------------
	code = request.data
	try:
		#--upgrade the authorization code into a credentials object------------------
		oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)

	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#--check that the access token is valid---------------------------------------
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])

	#--if there was an error in the access token info, abort----------------------
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	#--verify that the access token is used for the intended user-----------------
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#--verify that the access token is valid for this app-------------------------
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's"), 401)
		print "Tokens's client ID does not match app's"
		response.headers['Content-Type'] = 'application/json'
		return response

	#--check to see if user is already logged in----------------------------------
	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	#--store the access token in the session for later use------------------------
	login_session['provider'] = 'google'
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	#--get user info--------------------------------------------------------------
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt':'json'}
	answer = requests.get(userinfo_url, params=params)
	data = answer.json()

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] =  data["email"]

	#--if new user create new user entry in table---------------------------------
	userId = getUserId(login_session['email'])
	if not userId:
		userId = createUser(login_session)

	login_session['user_id'] = userId;

	#--create a response for successful login-------------------------------------
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style="width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
	print "done!"
	return output


#============================================================= gdisconnect() ==
@app.route("/gdisconnect")
def gdisconnect():
	#--only disconnect a connected user-------------------------------------------
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(json.dumps('Current user not connected'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#--execute HTTP GET request to revoke current token---------------------------
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		#--reset users session-------------------------------------------------------
		response = make_response(json.dumps('Successfully disconnected'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	else:
		#--handle invalid token------------------------------------------------------
		response = make_response(json.dumps('Failed to revoke token for given user'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response


#============================================================== disconnect() ==
@app.route('/disconnect')
def disconnect():
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			gdisconnect()
			del login_session['gplus_id']

		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['user_id']
		del login_session['provider']
		return redirect(url_for('showAll'))
	else:
		return redirect(url_for('showAll'))



#******************************************************************************
#
# JSON APIs
#
#******************************************************************************


#================================================================ itemJSON() ==
@app.route('/media/item/<string:urlname>/JSON')
def itemJSON(urlname):
	item = session.query(Media).filter(Media.urlname==urlname).one()
	return jsonify(item = item.serialize)


#============================================================ allItemsJSON() ==
@app.route('/media/catalog/JSON')
def allItemsJSON():
	media = session.query(Media).order_by(Media.name.asc())
	return jsonify(items=[i.serialize for i in media])



#******************************************************************************
#
# PUBLIC ACCESS ROUTES
#
#******************************************************************************


#=========================================================== notAuthorized() ==
@app.route('/not-authorized')
def notAuthorized():
	return render_template('not-authorized.html')


#================================================================= showAll() ==
@app.route('/')
@app.route('/media/viewAll')
def viewAll():
	media  = session.query(Media).order_by(Media.media_type.asc(), Media.name.asc())
	return render_template('view-all.html', media=media, title='All Media')


#================================================================= showAll() ==
@app.route('/')
@app.route('/media/all')
def showAll():
	books  = session.query(Media).filter(Media.media_type=='book').order_by(Media.name.asc())
	movies = session.query(Media).filter(Media.media_type=='movie').order_by(Media.name.asc())
	games  = session.query(Media).filter(Media.media_type=='video-game').order_by(Media.name.asc())
	return render_template('list-all.html', books=books, movies=movies, games=games, title='All Media')


#============================================================== showRecent() ==
@app.route('/media/recent')
def showRecent():
	media = session.query(Media).order_by(Media.id.desc()).limit(10)
	return render_template('media-list.html', title="Recently Added", media=media)


#=============================================================== showBooks() ==
@app.route('/media/books')
def showBooks():
	media = session.query(Media).filter(Media.media_type=='book').order_by(Media.name.asc()).all()
	return render_template('media-list.html', title="Books", media=media)


#================================================================ showMovies ==
@app.route('/media/movies')
def showMovies():
	media = session.query(Media).filter(Media.media_type=='movie').order_by(Media.name.asc()).all()
	return render_template('media-list.html', title="Movies", media=media)


#=============================================================== showGames() ==
@app.route('/media/games')
def showGames():
	media = session.query(Media).filter(Media.media_type=='video-game').order_by(Media.name.asc()).all()
	return render_template('media-list.html', title="Games", media=media)


#================================================================ showItem() ==
@app.route('/media/item/<string:urlname>')
def showItem(urlname):
	item = session.query(Media).filter(Media.urlname==urlname).one()
	return render_template('view-item.html', item=item)



#******************************************************************************
#
# AUTHORIZATION REQUIRED ROUTES
#
#******************************************************************************


#============================================================= showMyMedia() ==
@app.route('/media/mymedia')
def showMyMedia():
	if 'username' not in login_session:
		return redirect('/login')

	books  = session.query(Media).filter(Media.media_type=='book', Media.user_id==login_session['user_id']).order_by(Media.name.asc())
	movies = session.query(Media).filter(Media.media_type=='movie', Media.user_id==login_session['user_id']).order_by(Media.name.asc())
	games  = session.query(Media).filter(Media.media_type=='video-game', Media.user_id==login_session['user_id']).order_by(Media.name.asc())
	return render_template('list-all.html', books=books, movies=movies, games=games, title=login_session['username']+' Media')


#================================================================ editItem() ==
@app.route('/media/item/<string:urlname>/edit/', methods = ['GET', 'POST'])
def editItem(urlname):
	if 'username' not in login_session:
		return redirect('/login')

	item = session.query(Media).filter(Media.urlname==urlname).one()
	if item.user_id != login_session['user_id']:
		return render_template('not-authorized.html')

	if request.method == 'POST':
		if request.form['name']:
			item.name = request.form['name']
			item.urlname = getUrlName(request.form['name'])
		if request.form['description']:
			item.description = request.form['description']
		if request.form['media_type']:
			item.media_type = request.form['media_type']
		session.add(item)
		session.commit()
		return redirect(url_for('showItem', urlname=item.urlname))
	else:
		return render_template('edit-item.html', item=item)


#================================================================ newItem() ==
@app.route('/media/item/new/', methods = ['GET', 'POST'])
def newItem():
	if 'username' not in login_session:
		return redirect('/login')

	if request.method == 'POST':
		item = Media(
			name = request.form['name'],
			urlname = getUrlName(request.form['name']),
			description = request.form['description'],
			media_type = request.form['media_type'],
			user_id = login_session['user_id']
		)
		session.add(item)
		session.commit()
		return redirect(url_for('showRecent'))
	else:
		return render_template('new-item.html')


#============================================================== deleteItem() ==
@app.route('/media/item/<string:urlname>/delete/', methods = ['GET','POST'])
def deleteItem(urlname):
	if 'username' not in login_session:
		return redirect('/login')

	item = session.query(Media).filter(Media.urlname==urlname).one()
	if item.user_id != login_session['user_id']:
		return render_template('not-authorized.html')

	if request.method == 'POST':
		session.delete(item)
		session.commit()
		return redirect(url_for('showAll'))
	else:
		return render_template('delete-item.html', item=item)



#******************************************************************************
#
# HELPER FUNCTIONS
#
#******************************************************************************


#============================================================== getUrlName() ==
def getUrlName(theName):
	myName = theName.strip().lower().replace(" ","-")
	return re.sub(r'[^a-z0-9-]', '', myName)


#=============================================================== getUserId() ==
def getUserId(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None


#============================================================= getUserInfo() ==
def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user


#============================================================== createUser() ==
def createUser(login_session):
	newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id




if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
