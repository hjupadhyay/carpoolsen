from facebook import GraphAPI
import json
from django.http import HttpResponse
from django.utils import timezone
from mainapp.models import *
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.db.models import Count, Min, Sum, Avg
import uuid
import jinja2
import smtplib
jinja_environ = jinja2.Environment(loader=jinja2.FileSystemLoader(['ui']));

def check(request):
    
    #Check if user is logged in
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('fool.html').render({"rider":None}))

    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""
                                                                                  <p>No Rider associated!.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    
    #Check if user has been verified
    if request.user.rider.verified <> '1':
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":"""
                                                                                  <p>Your account has not been verified. Please check your email and click on the verification link.</p>
                                                                                  <p>To re-send verification email, click <a href="/send_verification_email/">here</a>.</p>
                                                                                  <p>If you have entered a wrong email, you can change it from <a href="/edit_profile_page/">here</a></p>
                                                                                  <p>Click <a href="/logout_do/">here</a> to go to the homepage and log-in again</p>"""}))
        #return HttpResponse(request.user.rider.verified)
    return None 
