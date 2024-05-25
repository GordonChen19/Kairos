import pymongo

url = "mongodb+srv://testhack:L4g3Ptj8g7D0cXIH@kairos.79p8xqm.mongodb.net/"

client = pymongo.MongoClient(url)

db = client['hacksg']