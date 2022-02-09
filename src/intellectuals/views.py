import requests
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as login_main
from sawo import createTemplate, getContext, verifyToken
from dotenv import load_dotenv
import json
import os
# from decouple import config

# Create your views here.

load = ''
loaded = 0

load_dotenv()


def setPayload(payload):
    global load
    load = payload


def setLoaded(reset=False):
    global loaded
    if reset:
        loaded = 0
    else:
        loaded += 1


createTemplate("templates/partials")


def index(request):
    return render(request, "index.html")


def login(request):
    if request.user.is_authenticated:
        print("here")
        return redirect('home')
    else:
        print("REQ: ", request.user)
        setLoaded()
        setPayload(load if loaded < 2 else '')

        configuration = {
            "auth_key": os.getenv("api_key"),
            "identifier": "email",
            "to": "receive"
        }
        context = {"sawo": configuration, "load": load,
                   "title": "Home"}
        return render(request, "login.html", context)


def receive(request):
    if request.method == 'POST':
        payload = json.loads(request.body)["payload"]
        setLoaded(True)
        setPayload(payload)
        print("PAYLOAD: ", payload)
        res = requests.post('https://api.sawolabs.com/api/v1/userverify/', data={
                            "user_id": payload["user_id"], "verification_token": payload["verification_token"]})
        if res.status_code == 200:
            print("SUCCESS")
            if User.objects.filter(username=payload["customFieldInputValues"]["username"]).exists():
                user = authenticate(request,
                    username=payload["customFieldInputValues"]["username"])
                login_main(request, user)
            else:
                form = UserForm(
                    {"username": payload["customFieldInputValues"]["username"], "email": payload["identifier"], "password1": "radpass@123", "password2": "radpass@123"})
                print(form)
                if form.is_valid():
                    user = form.save()
                    print("User Created", user)
                    username = form.cleaned_data.get('username')
                    user.set_unusable_password()
                    messages.success(
                        request, f'Account created for {username}.')
                else:
                    # print errors
                    # authenticate(username=payload["customFieldInputValues"]["username"])
                    print(form.error_messages)
                    print("User Exists")
        return redirect('home')
