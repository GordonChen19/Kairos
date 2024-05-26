from mongoengine import connect
from saved_route import saved_route

from dotenv import load_dotenv
import os

load_dotenv()

Mongo_DB_API = os.getenv('Mongo_DB_API')

connect(db='hacksg', host = Mongo_DB_API)


def POST(tele_handle, data):
    saved = saved_route(tele_handle=tele_handle)
    saved.data = data
    # saved.end = end
    # saved.transit_routing_preference = transit_routing_preference

    saved.save()

def UPDATE(tele_handle, data_old, data_new):
    saved = saved_route.objects(tele_handle=tele_handle, data=data_old)
    saved.update(data=data_new)

def GET(tele_handle):
    return saved_route.objects(tele_handle = tele_handle).as_pymongo()

def DELETE(_id):
    saved_route.objects(id=_id).delete()

def GET_PARTICULAR(_id):
    return saved_route.objects(id=_id).as_pymongo()
