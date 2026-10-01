from pymongo import MongoClient

def get_database():
    CONNECTION_STRING = MONGO_API_KEY

    client = MongoClient(CONNECTION_STRING)

    return client['user_shopping_list']

if __name__ == "__main__":

    dbname = get_database