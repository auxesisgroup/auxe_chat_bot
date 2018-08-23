from pymongo import MongoClient


def mongo_connection():
    try:
        client = MongoClient(host='127.0.0.1', port=27017)
        print("MongoDB Connected", client)
        return client

    except Exception as e:
        print "Error in mongo connection: ", e

