from pymongo import MongoClient
from django.conf import settings
import os

class BddUser:
    def __init__(self):
        self.db_name = os.getenv("MONGO_DB_NAME")  # Chargé depuis une variable d'environnement
        self.host = os.getenv("MONGO_HOST")
        self.port = int(os.getenv("MONGO_PORT"))
        self.username = os.getenv("MONGO_USER",None)
        self.password = os.getenv("MONGO_PASS",None)

    def get_db(self):
        """Connexion sécurisée à MongoDB"""
        client = MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        db = client[self.db_name]
        return db, client
