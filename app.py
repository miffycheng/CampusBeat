from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from db import get_db  
from flask import session

app = Flask(__name__)


db = get_db()

# Sign-Up (User Registration) Route
from werkzeug.security import generate_password_hash

@app.route('/signup', methods=['POST'])
def signup():
    user_data = request.get_json()

   
    if not user_data.get('Name') or not user_data.get('Email') or not user_data.get('Password'):
        return jsonify({"error": "Missing required fields"}), 400

    
    new_user = {
        "Name": user_data['Name'],
        "Email": user_data['Email'],
        "Password": user_data['Password'],  
        "PreferredGenres": user_data.get('PreferredGenres', [])
    }

    
    db.USER.insert_one(new_user)
    return jsonify({"message": "User registered successfully!"}), 201


# Login Route (User Authentication)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()  
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    
    user = db.USER.find_one({"Email": email})

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

   
    if user['Password'] != password:
        return jsonify({"error": "Invalid email or password"}), 401
    
    user_id_str = str(user['_id'])
    
    return jsonify({"message": "Login successful", "user_id": user_id_str}), 200



# Create a route to add a new user
# @app.route('/add_user', methods=['POST'])
# def add_user():
#     user_data = request.get_json()  # Get data from the POST request in JSON format
#     new_user = db.USER.insert_one(user_data)  # Insert data into the 'users' collection
#     return jsonify({"message": "User added", "user_id": str(new_user.inserted_id)}), 201

# Create a route to get all songs
@app.route('/songs', methods=['GET'])
def get_songs():
    try:
        songs = db.SONG.find() 
        song_list = []

        for song in songs:
            song_data = {
                "title": song.get("Title", "Unknown Title"),
                "artist": song.get("Detail", {}).get("Artist", "Unknown Artist"),  
                "genre": song.get("Detail", {}).get("Genre", "Unknown Genre"),  
                "play_count": song.get("PlayCount", 0),
                "last_played": song.get("LastPlayed", "Unknown Date"),
                "audio_file": song.get("AudioFile", "Unknown File"),
                "album": song.get("Detail", {}).get("Album", "Unknown Album"),  
                "duration": song.get("Detail", {}).get("Duration", "Unknown Duration")  
            }
            song_list.append(song_data)

        print("Songs retrieved:", song_list) 
        return jsonify(song_list)
    except Exception as e:
        print("Error fetching songs:", e)
        return jsonify({"error": "Failed to retrieve songs", "details": str(e)}), 500


# search bar
@app.route('/search_songs', methods=['GET'])
def search_songs():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Search query is required"}), 400

    try:
        
        search_results = db.SONG.find({
            "$or": [
                {"Title": {"$regex": query, "$options": "i"}},  
                {"Detail.Artist": {"$regex": query, "$options": "i"}}  
            ]
        })
        
        # Prepare the list of songs to return
        songs_list = []
        for song in search_results:
            song_data = {
                "title": song.get("Title", "Unknown Title"),
                "artist": song.get("Detail", {}).get("Artist", "Unknown Artist"),
                "album": song.get("Detail", {}).get("Album", "Unknown Album"),
                "duration": song.get("Detail", {}).get("Duration", "Unknown Duration")
            }
            songs_list.append(song_data)

        if songs_list:
            return jsonify(songs_list)
        else:
            return jsonify({"message": "No songs found matching the query"}), 404

    except Exception as e:
        print("Error during song search:", e)
        return jsonify({"error": "Failed to search songs", "details": str(e)}), 500

#match users with same taste
@app.route('/match_preferences', methods=['POST'])
def match_preferences():
    data = request.get_json()  
    user_id = data.get('user_id')  

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    logged_in_user = db.USER.find_one({"_id": ObjectId(user_id)})

    if not logged_in_user:
        return jsonify({"error": "User not found"}), 404
    
    preferred_genres = logged_in_user.get("PreferredGenres", [])

    if not preferred_genres:
        return jsonify({"error": "User has no preferred genres"}), 400


    if isinstance(preferred_genres, str):
        preferred_genres = [preferred_genres]  

    
    matched_users = db.USER.find({
        "PreferredGenres": {
            "$in": preferred_genres  
        },
        "_id": {"$ne": ObjectId(user_id)}  
    })

    
    matched_users_list = []
    for user in matched_users:
        matched_users_list.append({
            "name": user["Name"],
            "email": user.get("email", "Not provided"),
            "preferred_genres": user.get("PreferredGenres", [])
        })

    if not matched_users_list:
        return jsonify({"message": "No users with matching preferences found"}), 200
    
    return jsonify({"matched_users": matched_users_list}), 200

# not yet ready
@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    user_id = request.json.get('user_id')

    # Fetch the user's preferences based on ObjectId
    user = db.USER.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch the recommended songs based on UserID
    recommendations = db.RECOMMENDATION.find({"UserID": ObjectId(user_id)}).sort("RelevanceScore", -1)

    if not recommendations:
        return jsonify({"message": "No recommendations found for this user."}), 200

    # Prepare the result with detailed song info
    result = []
    for recommendation in recommendations:
        song_id = recommendation.get("SongID")
        song = db.songs.find_one({"_id": song_id})

        if song:
            result.append({
                "song_title": song.get("title"),
                "artist": song.get("artist"),
                "genre": song.get("details", {}).get("genre", "N/A"),
                "relevance_score": recommendation.get("RelevanceScore")
            })

    return jsonify(result), 200


@app.route('/top_songs', methods=['GET'])
def get_top_songs():

    top_songs = db.SONG.find().sort("PlayCount", -1).limit(3)
    
    result = []
    for song in top_songs:
        
        artist = song.get("Detail", {}).get("Artist", "Unknown Artist")
        

        result.append({
            "title": song.get("Title"),
            "artist": artist,
            "play_count": song.get("PlayCount")
        })
    
    return jsonify(result), 200



# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
