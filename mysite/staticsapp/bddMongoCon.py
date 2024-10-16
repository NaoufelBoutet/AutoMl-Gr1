import os
from pymongo import MongoClient

def MongoConnexion():
    MONGODB_URI = 'mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5'  
    DB_NAME = 'Data_Storag'  


    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    coll = db['Datas']

    coll.create_index([('user_id', 1), ('dataset_name', 1)])
    return {"client":client,"db":db,'coll':coll}