from mongoengine import Document, ListField, IntField

class saved_route(Document):
    tele_handle = IntField(require=True)
    data = ListField(require=True)