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
# Remove OAuth2 variables
# STARTGG_CLIENT_ID = os.getenv('STARTGG_CLIENT_ID')
# STARTGG_CLIENT_SECRET = os.getenv('STARTGG_CLIENT_SECRET')
# STARTGG_REDIRECT_URI = os.getenv('STARTGG_REDIRECT_URI')
# STARTGG_AUTH_BASE = 'https://start.gg/oauth/authorize'
# STARTGG_TOKEN_URL = 'https://start.gg/oauth/token'
STARTGG_API_URL = 'https://api.start.gg/gql/alpha'
STARTGG_API_TOKEN = os.getenv('STARTGG_API_TOKEN')

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize Firebase Admin SDK and db instance
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

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
        # Use username if available, else fallback to user_id
        entry_data['display_name'] = entry_data.get('username', entry_data.get('user_id', ''))
        leaderboard.append(entry_data)
    
    return render_template('index.html', teams=teams, leaderboard=leaderboard)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_query = db.collection('users').where('username', '==', username).limit(1).stream()
        user_doc = next(user_query, None)
        if user_doc:
            user = user_doc.to_dict()
            user_id = user_doc.id
            # Check password hash
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.get('password_hash') == password_hash:
                session['user_id'] = user_id
                session['username'] = username
                return redirect(url_for('home'))
        flash('Login failed. Please check your credentials.')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username already exists
        user_query = db.collection('users').where('username', '==', username).limit(1).stream()
        if next(user_query, None):
            flash('Username already taken. Please choose another.')
            return render_template('register.html')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user_ref = db.collection('users').add({
            'username': username,
            'password_hash': password_hash,
            'created_at': datetime.now()
        })
        user_id = user_ref[1].id
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def seed_to_cost(seed):
    if seed == 1:
        return 250
    elif seed == 2:
        return 240
    elif seed == 3:
        return 220
    elif seed == 4:
        return 210
    elif 5 <= seed <= 6:
        return 190
    elif 7 <= seed <= 9:
        return 170
    elif 10 <= seed <= 12:
        return 150
    elif 13 <= seed <= 16:
        return 140
    elif 17 <= seed <= 24:
        return 130
    elif 25 <= seed <= 32:
        return 120
    elif 33 <= seed <= 42:
        return 100
    elif 43 <= seed <= 62:
        return 90
    elif 63 <= seed <= 75:
        return 80
    elif 76 <= seed <= 113:
        return 70
    elif 114 <= seed <= 149:
        return 60
    elif 150 <= seed <= 167:
        return 50
    elif 168 <= seed <= 183:
        return 40
    elif 184 <= seed <= 191:
        return 30
    elif 192 <= seed <= 203:
        return 20
    else:
        return '?'

@app.route('/create')
@login_required
def create():
    # Check if user already has a team
    user_team_query = db.collection('teams').where('user_id', '==', session['user_id']).limit(1).stream()
    user_team_doc = next(user_team_query, None)
    user_team = user_team_doc.to_dict() if user_team_doc else None
    if user_team:
        # Pass team to template for delete button
        team_id = user_team_doc.id
    else:
        team_id = None
    # Fetch entrants from start.gg
    tournament_slug = 'norcal-ultimate-arcadian-the-great-pirate-era'
    event_slug = 'tournament/norcal-ultimate-arcadian-the-great-pirate-era/event/fishman-island-singles'
    url = STARTGG_API_URL
    headers = {
        'Authorization': f'Bearer {STARTGG_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    query = '''
    query EventEntrants($tourneySlug: String!) {
      tournament(slug: $tourneySlug) {
        events {
          name
          slug
          entrants(query: {perPage: 300}) {
            nodes {
              id
              name
              seeds {
                seedNum
              }
              participants {
                gamerTag
              }
            }
          }
        }
      }
    }
    '''
    variables = {
        'tourneySlug': tournament_slug
    }
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()
    if 'errors' in data or 'data' not in data:
        return "Error loading entrants", 500
    events = data['data']['tournament']['events']
    event = next((e for e in events if e['slug'] == event_slug), None)
    if not event:
        return f"Event with slug '{event_slug}' not found.", 500
    entrants = event['entrants']['nodes']
    for entrant in entrants:
        seed = entrant.get('seeds', [{}])[0].get('seedNum')
        entrant['cost'] = seed_to_cost(seed) if seed is not None else '?'
        entrant['seed'] = seed
    return render_template('create.html', entrants=entrants, user_team=user_team, team_id=team_id)

@app.route('/create', methods=["POST"])
@login_required
def add_team():
    # Prevent multiple teams per user
    user_team_query = db.collection('teams').where('user_id', '==', session['user_id']).limit(1).stream()
    if next(user_team_query, None):
        flash('You have already created a team.')
        return redirect(url_for('home'))
    team_name = request.form['team_name']
    import json
    players_json = request.form.get('players', '[]')
    print(f"DEBUG: Received players_json: {players_json}")  # Debug print
    try:
        players = json.loads(players_json)
        print(f"DEBUG: Parsed players: {players}")  # Debug print
    except Exception as e:
        print(f"DEBUG: Error parsing players: {e}")  # Debug print
        players = []
    # Create team document
    team_data = {
        'user_id': session['user_id'],
        'username': session['username'],
        'team_name': team_name,
        'players': players,
        'created_at': datetime.now()
    }
    print(f"DEBUG: Team data being stored: {team_data}")  # Debug print
    team_ref = db.collection('teams').add(team_data)
    # Create leaderboard entry
    db.collection('leaderboard').add({
        'user_id': session['user_id'],
        'username': session['username'],
        'team_id': team_ref[1].id,
        'team_name': team_name,
        'points': 0,
        'created_at': datetime.now()
    })
    flash('Team created')
    return redirect(url_for('home'))

@app.route('/delete_team', methods=['POST'])
@login_required
def delete_team():
    # Find and delete user's team
    user_team_query = db.collection('teams').where('user_id', '==', session['user_id']).limit(1).stream()
    user_team_doc = next(user_team_query, None)
    if user_team_doc:
        team_id = user_team_doc.id
        user_team_doc.reference.delete()
        # Delete leaderboard entry for this team
        leaderboard_query = db.collection('leaderboard').where('team_id', '==', team_id).stream()
        for entry in leaderboard_query:
            entry.reference.delete()
        flash('Team deleted')
    else:
        flash('No team to delete')
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

@app.route('/api/team/<team_id>')
def api_get_team(team_id):
    # Fetch team document
    team_doc = db.collection('teams').document(team_id).get()
    if not team_doc.exists:
        return jsonify({'error': 'Team not found'}), 404
    team = team_doc.to_dict()
    # Try to get player details if stored
    players = team.get('players', [])
    # If players are stored as dicts with gamerTag/seed/cost, return as is
    # If only IDs are stored, just return the IDs
    return jsonify({
        'team_name': team.get('team_name', ''),
        'players': players
    })

# Remove /startgg/login and /startgg/callback routes and get_startgg_user_info

if __name__ == '__main__':
    app.run(debug=True)
