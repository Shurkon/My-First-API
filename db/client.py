# pip install pymongo
# mongod --dbpath "/path/a/la/base/de/datos/data"
# mongodb://localhost

from pymongo import MongoClient

db_client = MongoClient("mongodb://localhost")