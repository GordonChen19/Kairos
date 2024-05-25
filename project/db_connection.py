import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv('Mongo_DB_API')

client = pymongo.MongoClient(url)

db = client['hacksg']