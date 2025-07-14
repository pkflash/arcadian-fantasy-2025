from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os
import requests
import random
import time
import pandas as pd
from datetime import datetime
import math

app = Flask(__name__)

# Initialize Firebase Admin SDK and db instance
cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/create', methods=["POST"])
def add_team():
    pass
