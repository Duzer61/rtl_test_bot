from pymongo import MongoClient

from config_data.config import config

client: MongoClient = MongoClient('mongodb://localhost:27017')
db = client[config.database.base_name]
collection = db[config.database.collection_name]
