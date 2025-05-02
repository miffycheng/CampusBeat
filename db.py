from pymongo import MongoClient

# MongoDB Atlas connection string
client = MongoClient("USE YOUR OWN STRING")
db = client.IS455Final  # Reference to the 'IS455Final' database

# Export db for use in app.py
def get_db():
    return db
