import pymongo

# Singleton pattern is being used
_client = None
_db = None

def get_db(db_name="PSX_datacentre", host="localhost", port=27017):
    global _client, _db
    if _db is None:
        _client = pymongo.MongoClient(host, port)
        _db = _client[db_name]
    return _db

