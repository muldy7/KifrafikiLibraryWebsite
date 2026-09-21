from pymongo import MongoClient

def get_database():
    CONNECTION_STRING = "mongodb+srv://abe_db_user:<BYgiV2Ysm8oK9y5u>@kirafikicluster.k0x7uss.mongodb.net/"

    client = MongoClient(CONNECTION_STRING)

    return client['user_shopping_list']

if __name__ == "__main__":

    dbname = get_database