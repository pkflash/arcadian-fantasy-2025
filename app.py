from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import requests
import random
import time
import pandas as pd
from datetime import datetime, timezone
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

POINTS_BY_PLACING = {
    1: 550,
    2: 520,
    3: 490,
    4: 460,
    5: 430,
    7: 390,
    9: 350,
    13: 310,
    17: 270,
    25: 220,
    33: 170,
    49: 120,
    73: 60,
    97: 0,
    129: 0,
    193: 0,
    257: 0,
}

def get_points_for_placing(placing):
    return POINTS_BY_PLACING.get(placing, 0)

def fetch_entrant_placings():
    # Fetch all entrants and their placings from start.gg
    tournament_slug = 'norcal-ultimate-arcadian-the-great-pirate-era'
    event_slug = 'tournament/norcal-ultimate-arcadian-the-great-pirate-era/event/fishman-island-singles'
    url = STARTGG_API_URL
    headers = {
        'Authorization': f'Bearer {STARTGG_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    query = '''
    query EventPlacings($tourneySlug: String!) {
      tournament(slug: $tourneySlug) {
        events {
          slug
          standings(query: {perPage: 300}) {
            nodes {
              placement
              entrant {
                id
                name
              }
            }
          }
        }
      }
    }
    '''
    variables = {'tourneySlug': tournament_slug}
    response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
    data = response.json()
    if 'errors' in data or 'data' not in data:
        print("Data error")
        return {}
    events = data['data']['tournament']['events']
    event = next((e for e in events if e['slug'] == event_slug), None)
    if not event:
        print("Event not found")
        return {}
    entrants = event['standings']['nodes']

    # Map entrant id to (finalPlacement, gamerTag)
    placings = {}
    for entrant in entrants:
        eid = entrant['entrant']['id']
        placement = entrant['placement']
        # gamerTag = entrant['participants'][0]['gamerTag'] if entrant['participants'] and 'gamerTag' in entrant['participants'][0] else entrant['name']
        gamerTag = entrant['entrant']['name']
        placings[eid] = {'placing': placement, 'gamerTag': gamerTag}
    return placings

def update_all_team_points():
    placings = fetch_entrant_placings()
    game5_count = fetch_top8_game5_count()
    winner_games_lost = fetch_winner_games_lost()
    unique_char_count = fetch_top8_unique_characters_count()
    three_stock_count = fetch_top8_three_stock_count()
    teams_ref = db.collection('teams').stream()
    for team_doc in teams_ref:
        team = team_doc.to_dict()
        players = team.get('players', [])
        total_points = 0
        for player in players:
            eid = player['id'] if isinstance(player, dict) else player
            placing = placings.get(eid, {}).get('placing')
            points = get_points_for_placing(placing) if placing is not None else 0
            total_points += points
        # Bonus 1: Award 25 points if user's selected range or 21+ matches three_stock_count
        bonus1 = team.get('bonus1')
        try:
            if three_stock_count is not None and bonus1 is not None:
                if '+' in bonus1:
                    min_val = int(bonus1.replace('+', '').replace(' ', ''))
                    if three_stock_count >= min_val:
                        total_points += 25
                elif '-' in bonus1:
                    min_val, max_val = [int(x) for x in bonus1.split('-')]
                    if min_val <= three_stock_count <= max_val:
                        total_points += 25
                else:
                    # Exact match (if dropdown ever uses exact numbers)
                    if int(bonus1) == three_stock_count:
                        total_points += 25
        except Exception as e:
            print(f"Error checking bonus1 for team {team_doc.id}: {e}")
        # Bonus 2: Award 25 points if user's answer matches actual game5_count
        bonus2 = team.get('bonus2')
        try:
            if bonus2 is not None and int(bonus2) == game5_count:
                total_points += 25
        except Exception as e:
            print(f"Error checking bonus2 for team {team_doc.id}: {e}")
        # Bonus 3: Award 25 points if user's selected range or 12+ matches unique_char_count
        bonus3 = team.get('bonus3')
        try:
            if unique_char_count is not None and bonus3 is not None:
                if '+' in bonus3:
                    min_val = int(bonus3.replace('+', '').replace(' ', ''))
                    if unique_char_count >= min_val:
                        total_points += 25
                elif '-' in bonus3:
                    min_val, max_val = [int(x) for x in bonus3.split('-')]
                    if min_val <= unique_char_count <= max_val:
                        total_points += 25
                else:
                    # Exact match (if dropdown ever uses exact numbers)
                    if int(bonus3) == unique_char_count:
                        total_points += 25
        except Exception as e:
            print(f"Error checking bonus3 for team {team_doc.id}: {e}")
        # Bonus 4: Award 25 points if user's selected range contains actual games lost
        bonus4 = team.get('bonus4')
        try:
            if bonus4 is not None:
                if '+' in bonus4:
                    min_val = int(bonus4.replace('+', '').replace(' ', ''))
                    if winner_games_lost >= min_val:
                        total_points += 25
                elif '-' in bonus4:
                    min_val, max_val = [int(x) for x in bonus4.split('-')]
                    if min_val <= winner_games_lost <= max_val:
                        total_points += 25
        except Exception as e:
            print(f"Error checking bonus4 for team {team_doc.id}: {e}")
        # Update leaderboard entry for this team
        leaderboard_query = db.collection('leaderboard').where('team_id', '==', team_doc.id).stream()
        for entry in leaderboard_query:
            entry.reference.update({'points': total_points})

def fetch_top8_game5_count():
    """
    Fetch all sets in top 8 for the event and count how many were game 5s (3-2 score).
    Returns the count as an integer.
    """
    tournament_slug = 'norcal-ultimate-arcadian-the-great-pirate-era'
    event_slug = 'tournament/norcal-ultimate-arcadian-the-great-pirate-era/event/fishman-island-singles'
    url = STARTGG_API_URL
    headers = {
        'Authorization': f'Bearer {STARTGG_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    # First, get the phaseGroups for the event (to find top 8 phase group)
    query_phasegroups = '''
    query EventPhaseGroups($tourneySlug: String!) {
      tournament(slug: $tourneySlug) {
        events {
          slug
          phaseGroups {
            id
            displayIdentifier
            phase {
              name
            }
          }
        }
      }
    }
    '''
    variables = {'tourneySlug': tournament_slug}
    response = requests.post(url, headers=headers, json={"query": query_phasegroups, "variables": variables})
    data = response.json()
    if 'errors' in data or 'data' not in data:
        print('Error fetching phase groups:', data)
        return 0
    events = data['data']['tournament']['events']
    event = next((e for e in events if e['slug'] == event_slug), None)
    if not event:
        print('Event not found')
        return 0
    # Try to find the phase group for top 8 (look for 'Top 8' in phase name or displayIdentifier)
    top8_pg = next((pg for pg in event['phaseGroups'] if pg['phase']['name'] == 'Singles Top 8'), None)
    if not top8_pg:
        print('Top 8 phase group not found')
        return 0
    phasegroup_id = top8_pg['id']
    # Now fetch setIDs for this phase group
    query_sets = '''
    query PhaseGroupSets($phaseGroupId: ID!) {
      phaseGroup(id: $phaseGroupId) {
        sets(perPage: 50) {
          nodes {
            id
          }
        }
      }
    }
    '''
    variables = {'phaseGroupId': phasegroup_id}
    response = requests.post(url, headers=headers, json={"query": query_sets, "variables": variables})
    data = response.json()
    if 'errors' in data or 'data' not in data:
        print('Error fetching ID\'s:', data)
        return 0
    
    sets = data['data']['phaseGroup']['sets']['nodes']
    # Finally, gather set score data from all the set ID's and count g5 sets

    query_score = '''
    query set($setId: ID!) {
        set(id: $setId) {
            id
            slots {
                id
                standing {
                    stats {
                        score {
                            label
                            value
                        }
                    }
                }
            }
        }
    }
    '''
    game5_count = 0
    for s in sets:
        set_id = s['id']

        # Fetch match data for the given set id
        set_response = requests.post(url, headers=headers, json={"query": query_score, "variables": {'setId': set_id}})
        set_data = set_response.json()

        # Increment game 5 count if both a 3 and a 2 are found in score data
        three_found = False
        two_found = False
        for item in set_data['data']['set']['slots']:
            score = item['standing']['stats']['score']['value']

            if score != 3 and score != 2:
                continue
            elif score == 3:
                three_found = True
            else:
                two_found = True
        if three_found and two_found:
            game5_count += 1

    return game5_count

def fetch_winner_games_lost():
    """
    Find the winner of singles, fetch all their sets, and count the total number of games they lost throughout the event.
    Returns the total games lost as an integer.
    """
    tournament_slug = 'norcal-ultimate-arcadian-the-great-pirate-era'
    event_slug = 'tournament/norcal-ultimate-arcadian-the-great-pirate-era/event/fishman-island-singles'
    url = STARTGG_API_URL
    headers = {
        'Authorization': f'Bearer {STARTGG_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    # Step 1: Find winner's user ID
    query_entrants = '''
    query EventPlacings($tourneySlug: String!) {
      tournament(slug: $tourneySlug) {
        events {
          slug
          standings(query: {perPage: 300}) {
            nodes {
              placement
              entrant {
                id
                name
              }
            }
          }
        }
      }
    }
    '''
    variables = {'tourneySlug': tournament_slug}
    response = requests.post(url, headers=headers, json={"query": query_entrants, "variables": variables})
    data = response.json()
    if 'errors' in data or 'data' not in data:
        print('Error fetching entrants:', data)
        return 0
    events = data['data']['tournament']['events']
    event = next((e for e in events if e['slug'] == event_slug), None)
    if not event:
        print('Event not found')
        return 0
    entrants = event['standings']['nodes']
    winner = next((e for e in entrants if e.get('placement') == 1), None)
    if not winner:
        print('Winner not found')
        return 0
    winner_id = winner['entrant']['id']

    # Step 2: Fetch all set id's of this player's matches
    query_sets = '''
    query EventSets($eventSlug: String!, $id: ID!) {
      event(slug: $eventSlug) {
          sets(perPage: 100, filters: {entrantIds: [$id]}) {
            nodes {
              id
            }
          }
      }
    }
    '''
    set_variables = {'eventSlug': event_slug, 'id': winner_id}
    response = requests.post(url, headers=headers, json={"query": query_sets, "variables": set_variables})
    data = response.json()
    if 'errors' in data or 'data' not in data:
        print('Error fetching sets:', data)
        return 0
    sets = data['data']['event']['sets']['nodes']
    # Step 3: For each set the winner played, count games lost
    query_score = '''
    query set($setId: ID!) {
        set(id: $setId) {
            id
            slots {
                id
                entrant {
                    id
                }
                standing {
                    stats {
                        score {
                            label
                            value
                        }
                    }
                }
            }
        }
    }
    '''

    games_lost = 0
    for s in sets:
        set_id = s['id']

        # Fetch match data for the given set id
        set_response = requests.post(url, headers=headers, json={"query": query_score, "variables": {'setId': set_id}})
        set_data = set_response.json()
        
        # Add number of games taken by opponent to games_lost
        for item in set_data['data']['set']['slots']:
            if item['entrant']['id'] == winner_id:
                continue
            else:
                score = item['standing']['stats']['score']['value']
                games_lost += score

    return games_lost

def fetch_top8_unique_characters_count():
    return 8

def fetch_top8_three_stock_count():
    return 1

@app.route('/')
@login_required
def home():
    # update_all_team_points()  # Disabled for performance; now updated by scheduler
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
    # Restrict access after 2:00 pm on 7/19/25 (UTC assumed)
    deadline = datetime(2025, 7, 19, 14, 0, 0, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if now > deadline:
        return '<h2 style="text-align:center; color:#ff3333;">too late bud</h2>'
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
    # Extract bonus answers from form
    bonus1 = request.form.get('bonus1')
    bonus2 = request.form.get('bonus2')
    bonus3 = request.form.get('bonus3')
    bonus4 = request.form.get('bonus4')
    # Create team document
    team_data = {
        'user_id': session['user_id'],
        'username': session['username'],
        'team_name': team_name,
        'players': players,
        'created_at': datetime.now(),
        'bonus1': bonus1,
        'bonus2': bonus2,
        'bonus3': bonus3,
        'bonus4': bonus4
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

@app.route('/api/update_leaderboard', methods=['POST', 'GET'])
def update_leaderboard():
    # Optionally, add a secret key check for security
    # secret = request.headers.get('X-Update-Secret')
    # if secret != os.getenv('SCHEDULER_SECRET', 'changeme'):
    #     return 'Unauthorized', 401
    update_all_team_points()
    return 'Leaderboard updated', 200

# Remove /startgg/login and /startgg/callback routes and get_startgg_user_info

if __name__ == '__main__':
    app.run(debug=True)
