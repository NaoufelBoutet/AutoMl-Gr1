from pymongo import MongoClient
def get_db_mongo(db_name, host, port, username=None, password=None):

 client = MongoClient(host=host,
                      port=int(port),
                      username=username,
                      password=password
                     )
 db_mongo = client[db_name]
 return db_mongo, client