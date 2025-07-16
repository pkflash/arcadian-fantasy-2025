from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import requests
import random
import time
import pandas as pd
from datetime import datetime
import math
from functools import wraps
import hashlib
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

# Load environment variables
load_dotenv()
STARTGG_CLIENT_ID = os.getenv('STARTGG_CLIENT_ID')
STARTGG_CLIENT_SECRET = os.getenv('STARTGG_CLIENT_SECRET')
STARTGG_REDIRECT_URI = os.getenv('STARTGG_REDIRECT_URI')
STARTGG_AUTH_BASE = 'https://start.gg/oauth/authorize'
STARTGG_TOKEN_URL = 'https://start.gg/oauth/token'
STARTGG_API_URL = 'https://api.start.gg/gql/alpha'

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize Firebase Admin SDK and db instance
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    # Get current user's teams
    user_teams = db.collection('teams').where('user_id', '==', session['user_id']).stream()
    teams = [team.to_dict() for team in user_teams]
    
    # Get leaderboard data
    leaderboard_ref = db.collection('leaderboard').order_by('points', direction=firestore.Query.DESCENDING).stream()
    leaderboard = []
    for i, entry in enumerate(leaderboard_ref, 1):
        entry_data = entry.to_dict()
        entry_data['rank'] = i
        leaderboard.append(entry_data)
    
    return render_template('index.html', teams=teams, leaderboard=leaderboard)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_query = db.collection('users').where('username', '==', username).stream()
        user_doc = next(user_query, None)
        if user_doc:
            user = user_doc.to_dict()
            if user['password_hash'] == hash_password(password):
                session['user_id'] = user_doc.id
                session['username'] = user['username']
                return redirect(url_for('home'))
            else:
                flash('Incorrect password.')
        else:
            flash('Username not found.')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username exists
        user_query = db.collection('users').where('username', '==', username).stream()
        if next(user_query, None):
            flash('Username already exists.')
            return render_template('register.html')
        # Store user with hashed password
        user_ref = db.collection('users').add({
            'username': username,
            'password_hash': hash_password(password),
            'created_at': datetime.now()
        })
        session['user_id'] = user_ref[1].id
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/create')
@login_required
def create():
    return render_template('create.html')

@app.route('/create', methods=["POST"])
@login_required
def add_team():
    team_name = request.form['team_name']
    players = request.form.getlist('players[]')  # Get all selected players
    
    # Create team document
    team_ref = db.collection('teams').add({
        'user_id': session['user_id'],
        'team_name': team_name,
        'players': players,
        'created_at': datetime.now()
    })
    
    # Create leaderboard entry
    db.collection('leaderboard').add({
        'user_id': session['user_id'],
        'team_id': team_ref[1].id,
        'team_name': team_name,
        'points': 0,
        'created_at': datetime.now()
    })
    
    flash('Team created successfully!')
    return redirect(url_for('home'))

@app.route('/api/update_score', methods=['POST'])
@login_required
def update_score():
    data = request.get_json()
    team_id = data.get('team_id')
    points = data.get('points')
    
    # Update leaderboard entry
    leaderboard_ref = db.collection('leaderboard').where('team_id', '==', team_id).stream()
    for entry in leaderboard_ref:
        entry.reference.update({
            'points': points,
            'updated_at': datetime.now()
        })
        break
    
    return jsonify({'success': True})

@app.route('/api/leaderboard')
def get_leaderboard():
    leaderboard_ref = db.collection('leaderboard').order_by('points', direction=firestore.Query.DESCENDING).stream()
    leaderboard = []
    for i, entry in enumerate(leaderboard_ref, 1):
        entry_data = entry.to_dict()
        entry_data['rank'] = i
        leaderboard.append(entry_data)
    
    return jsonify(leaderboard)

@app.route('/startgg/login')
def startgg_login():
    oauth = OAuth2Session(STARTGG_CLIENT_ID, redirect_uri=STARTGG_REDIRECT_URI)
    authorization_url, state = oauth.authorization_url(STARTGG_AUTH_BASE)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/startgg/callback')
def startgg_callback():
    oauth = OAuth2Session(STARTGG_CLIENT_ID, redirect_uri=STARTGG_REDIRECT_URI, state=session.get('oauth_state'))
    token = oauth.fetch_token(
        STARTGG_TOKEN_URL,
        client_secret=STARTGG_CLIENT_SECRET,
        authorization_response=request.url
    )
    # Fetch user info from start.gg
    user_info = get_startgg_user_info(token['access_token'])
    if not user_info:
        flash('Failed to fetch start.gg user info.')
        return redirect(url_for('login'))
    startgg_id = user_info['id']
    username = user_info['slug']
    # Check if user exists in Firestore
    user_query = db.collection('users').where('startgg_id', '==', startgg_id).stream()
    user_doc = next(user_query, None)
    if user_doc:
        user_id = user_doc.id
    else:
        # Create new user
        user_ref = db.collection('users').add({
            'username': username,
            'startgg_id': startgg_id,
            'created_at': datetime.now()
        })
        user_id = user_ref[1].id
    session['user_id'] = user_id
    session['username'] = username
    session['startgg_id'] = startgg_id
    flash('Logged in with start.gg!')
    return redirect(url_for('home'))

def get_startgg_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    # GraphQL query to get user info
    query = '{ "query": "query Me { me { id slug } }" }'
    resp = requests.post(STARTGG_API_URL, headers=headers, data=query)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('data') and data['data'].get('me'):
            return data['data']['me']
    return None

if __name__ == '__main__':
    app.run(debug=True)
