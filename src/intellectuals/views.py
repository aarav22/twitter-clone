import requests
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
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
        print("REQ: ",request.user)
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
            user = authenticate(username=payload["customFieldInputValues"]["username"])
            # form = UserForm(
            #     {"username": payload["customFieldInputValues"]["username"], "email": payload["identifier"]})
            # print(form)
            # if form.is_valid():
            print("User Created", user)
            # form.save()
            # username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {payload["customFieldInputValues"]["username"]}.')
            # else:
            #     # print errors
            #     print(form.error_messages)
            #     print("User Exists")
            return redirect('home')
