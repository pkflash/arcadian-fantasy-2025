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
from app import *

STARTGG_API_URL = 'https://api.start.gg/gql/alpha'
STARTGG_API_TOKEN = os.getenv('STARTGG_API_TOKEN')

# # Print entrant placings
# print(f'ENTRANT PLACINGS: {fetch_entrant_placings()}')

# # Print bonuses
# print(f'G5 COUNT: {fetch_top8_game5_count()}\n')
# print(f'GAMES LOST BY WINNER: {fetch_winner_games_lost()}')
# print(f'UNIQUE CHARACTERS: {fetch_top8_unique_characters_count()}')
# print(f'THREE STOCKS: {fetch_top8_three_stock_count()}')


# Test for start gg placement scores
placings = fetch_entrant_placings()
game5_count = fetch_top8_game5_count()
winner_games_lost = fetch_winner_games_lost()
unique_char_count = fetch_top8_unique_characters_count()
three_stock_count = fetch_top8_three_stock_count()

print(f"Fetched placings: {placings}")
print(f"Game 5 count: {game5_count}")
print(f"Winner games lost: {winner_games_lost}")
print(f"Unique character count: {unique_char_count}")
print(f"Three stock count: {three_stock_count}")

teams_ref = db.collection('teams').stream()
for team_doc in teams_ref:
    team = team_doc.to_dict()
    players = team.get('players', [])
    total_points = 0
    print(f"\nProcessing team: {team.get('name', 'Unknown')}")
    
    for player in players:
        eid = player['id'] if isinstance(player, dict) else player
        print(f"  Player EID: {eid}")
        
        # FIXED: Use safe dictionary access like in app.py
        player_placing_data = placings.get(eid, {})
        placing = player_placing_data.get('placing')
        gamer_tag = player_placing_data.get('gamerTag', 'Unknown')
        
        print(f"    Player data: {player_placing_data}")
        print(f"    Placing: {placing}")
        
        points = get_points_for_placing(placing) if placing is not None else 0
        print(f"    Points earned: {points}")
        total_points += points
    
    print(f"  Total points for team: {total_points}")