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
        leaderboard.append(entry_data)
    
    return render_template('index.html', teams=teams, leaderboard=leaderboard)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            # Verify user with Firebase Auth
            user = auth.get_user_by_email(email)
            # Note: Firebase Admin SDK doesn't verify passwords directly
            # You'll need to implement proper authentication
            session['user_id'] = user.uid
            session['email'] = user.email
            return redirect(url_for('home'))
        except Exception as e:
            flash('Login failed. Please check your credentials.')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            # Create user document in Firestore
            db.collection('users').document(user.uid).set({
                'email': email,
                'username': username,
                'created_at': datetime.now()
            })
            
            session['user_id'] = user.uid
            session['email'] = user.email
            return redirect(url_for('home'))
        except Exception as e:
            flash('Registration failed. Please try again.')
            return render_template('register.html')
    
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

if __name__ == '__main__':
    app.run(debug=True)
