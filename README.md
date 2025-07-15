# Norcal Arcadian Fantasy Leaderboard

A Flask-based fantasy leaderboard application for the Norcal Ultimate Arcadian tournament, built with Firebase Firestore for real-time data storage and authentication.

## Features

- **User Authentication**: Register and login with email/password
- **Team Management**: Create and manage fantasy teams
- **Real-time Leaderboard**: Live updating leaderboard with points
- **Firebase Integration**: Secure cloud database with Firestore

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Firebase Configuration

1. Make sure your `key.json` file is in the project root (Firebase service account key)
2. Update the Firebase project ID in `FirebaseConfig.js` if needed

### 3. Test Firebase Connection

```bash
python test_firebase.py
```

This will verify that your Firebase setup is working correctly.

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Database Structure

### Collections

1. **users** - User account information
   ```json
   {
     "user_id": {
       "email": "user@example.com",
       "username": "player123",
       "created_at": "timestamp"
     }
   }
   ```

2. **teams** - Fantasy teams created by users
   ```json
   {
     "team_id": {
       "user_id": "user123",
       "team_name": "Team Awesome",
       "players": ["player1", "player2", "player3"],
       "created_at": "timestamp"
     }
   }
   ```

3. **leaderboard** - Current standings
   ```json
   {
     "entry_id": {
       "user_id": "user123",
       "team_id": "team456",
       "team_name": "Team Awesome",
       "points": 150,
       "created_at": "timestamp",
       "updated_at": "timestamp"
     }
   }
   ```

## API Endpoints

- `GET /` - Home page with leaderboard
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /register` - Registration page
- `POST /register` - Create new user account
- `GET /create` - Team creation page
- `POST /create` - Create new team
- `GET /logout` - Logout user
- `POST /api/update_score` - Update team score
- `GET /api/leaderboard` - Get leaderboard data (JSON)

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Create Team**: Select players and create your fantasy team
3. **View Leaderboard**: See current standings and team details
4. **Update Scores**: Use the API to update team points during the tournament

## Security Notes

- Change the `app.secret_key` in `app.py` to a secure random string
- Ensure your Firebase service account key (`key.json`) is kept secure
- Consider implementing proper password verification for production use

## Next Steps

- Implement proper password authentication
- Add team editing functionality
- Create admin panel for score management
- Add real-time updates using Firebase listeners
- Implement player selection validation 