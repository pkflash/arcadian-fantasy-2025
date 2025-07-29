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

# Print entrant placings
print(f'ENTRANT PLACINGS: {fetch_entrant_placings()}')

# Print bonuses
print(f'G5 COUNT: {fetch_top8_game5_count()}\n')
print(f'GAMES LOST BY WINNER: {fetch_winner_games_lost()}')
print(f'UNIQUE CHARACTERS: {fetch_top8_unique_characters_count()}')
print(f'THREE STOCKS: {fetch_top8_three_stock_count()}')
