from pymongo import MongoClient

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://chiaocheng22:jTF7Q90sqSJuaFbS@cluster0.ulqgakk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.IS455Final  # Reference to the 'IS455Final' database

# Export db for use in app.py
def get_db():
    return db
