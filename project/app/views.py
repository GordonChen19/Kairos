from django.shortcuts import render
from .models import users
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def add_telegram_user(request):
    records = {
        "user_id":"test"
    }
    users.insert_one(records)
    return HttpResponse("<p>Db working</p>")

def get_telegram_user(request):
    user = users.find()
    return HttpResponse(user)