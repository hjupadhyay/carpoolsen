# Create your views here.
import math
from paths import cpspath
from facebook import GraphAPI
import json
from django.http import HttpResponse
from django.utils import timezone
from mainapp.models import *
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.db.models import Count, Min, Sum, Avg, Max
import uuid
import jinja2
import smtplib
from mainapp.checker import check
import thread
from django.http import Http404
from jinja2.ext import loopcontrols
import os
jinja_environ = jinja2.Environment(loader=jinja2.FileSystemLoader([cpspath + '/carpoolsen/ui']), extensions=[loopcontrols]);
#Dummy request object
#class Dum:
    #REQUEST = {}
#Perform basic checks on user

def errview(request):
	return HttpResponse(render('404.html'))

#Function to remove old posts of user
def remove_old_posts(user):
    for x in Post.objects.filter(owner=user.rider):
        if (timezone.now() - x.date_time).total_seconds() > 3600:
            for y in x.reserved_set.all():
                if y.changed == 0:
                    if y.reserved_set.all().aggregate(Sum('edited'))['edited__sum'] == 0:
                        if user.rider.neg_flags > 0:
                            user.rider.neg_flags -= 1
                y.delete()
            x.delete()
#send email function

month=["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def send_email(msg, email):
    gmailLogin = 'carpoolsen'
    gmailPas = 'qwertqwert!'
    fro = gmailLogin + "@gmail.com"
    
    to = email
    
    try:
        server = smtplib.SMTP_SSL('smtp.googlemail.com',465)
        a = server.login( gmailLogin, gmailPas)
        server.sendmail(fro, to,msg)
        return (1,1)
    except:
         return (0,HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>Could not send verification email. Please try again later.</p>\
                                                                                   <p>click <a href="/">here</a> to go to the homepage</p>'})))
#Function to send verification
def send_verification_email(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))
    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'No Rider associated!. Please go back or click <a href="/">here</a> to go to the homepage'}))
    entry = request.user
    subject = 'CarPool Verification Email'
    msg = 'Subject: %s \n\nYour email has been registered on carpoolsen.com.\nPlease\
    click on the following link to verify (or copy paste it in your browser if needed)\n\n\
    http://localhost:8000/verify?code=%s\n\nIf you have not registered on our website, please ignore.' % (subject, entry.rider.verified)
    
    x = send_email(msg, entry.email)
    if x[0]==0:
        return x[1]
    
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":"""<p>Verification Email sent! Please Check your email inbox.</p>
                                                                              <p>To re-send verification email, click <a href="/send_verification_email/">here</a>.</p>
                                                                              <p>Click <a href="/logout_do/">here</a> to go to the homepage and log-in again</p>"""}))


#pages and forms

def index(request):
    return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))
def signup_page(request):
	if request.user.is_authenticated():
		logout(request)
		redirect_url = "/"
		if 'redirect_url' in request.REQUEST.keys():
			redirect_url = request.REQUEST['redirect_url']
		return HttpResponse(jinja_environ.get_template('redirect.html').render({"rider":None,"redirect_url":redirect_url}))

	else:
		return HttpResponse(jinja_environ.get_template('signup.html').render({"rider":None}))

def login_page(request):
    return HttpResponse(jinja_environ.get_template('login.html').render({"rider":None}))
def contactus(request):
    rider = None
    if request.user.is_authenticated():
        rider = request.user.rider
    return HttpResponse(jinja_environ.get_template('ContactUs.html').render({"rider":rider}))

    return HttpResponse(jinja_environ.get_template('pref.html').render({"rider":request.user.rider}))
def faq(request):
    rider = None
    if request.user.is_authenticated():
        rider = request.user.rider
    return HttpResponse(jinja_environ.get_template('FAQs.html').render({'rider':rider}))
def aboutus(request):
    rider = None
    if request.user.is_authenticated():
        rider = request.user.rider
    return HttpResponse(jinja_environ.get_template('AboutUs.html').render({"rider":rider}))

def edit_profile_page(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))
    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'No Rider associated!.\
                                                                                  Please go back or click <a href="/">here</a> to go to the homepage'}))
    return HttpResponse(jinja_environ.get_template('pref.html').render({"rider":request.user.rider}))
    
def edit_post_page(request):
	retval = check(request)
	if retval <> None:
		return retval

	try:
		rider=request.user.rider
		key=request.REQUEST['key']
		postobj=Post.objects.get(id=key)
		return HttpResponse(jinja_environ.get_template('postedit.html').render({"rider":request.user.rider, 'post':postobj, 'reserved_list':postobj.reserved_set.all()}))
	except Exception as e:
		return HttpResponse(e)
		
def profile(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))

    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""
                                                                                  <p>No Rider associated!.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))

    try:
        riderid = request.REQUEST['id']
        if riderid == request.user.rider.pk:
            return HttpResponse(jinja_environ.get_template('profile.html').render({"rider":request.user.rider, "profiler":request.user.rider}))
        else:
            return HttpResponse(jinja_environ.get_template('profile.html').render({"rider":request.user.rider, "profiler":Rider.objects.get(pk=riderid)}))
    except:
        return HttpResponse(jinja_environ.get_template('profile.html').render({"rider":request.user.rider, "profiler":request.user.rider}))
    #return HttpResponse(request.user.first_name + " " + request.user.last_name + "'s Profile Page")

@csrf_exempt
def invite_page(request):
    retval = check(request)
    if retval <> None:
        return retval
    
    message = "Hey! Check out this amazing site, we can travel together now!"

    try :
      request.user.rider
      return HttpResponse(jinja_environ.get_template('invite.html').render({"rider": request.user.rider,
									    "message": message}))
    except Exception as e:
      return HttpResponse(e)
    
def inbox_page(request):   

    retval = check(request)
    if retval <> None:
        return retval
    
    try:
        results = Message.objects.filter(receiver=request.user.rider).extra(order_by = ['-date_time'])
        max_mid = 0
        for x in results:
            if x.id > max_mid:
                max_mid = x.id
        return HttpResponse(jinja_environ.get_template('inbox.html').render({"rider":request.user.rider,
                                                                             "messages":results,
                                                                             "max_mid": max_mid,}))
    except:
        return HttpResponse(jinja_environ.get_template('inbox.html').render({"rider":request.user.rider,
                                                                             "messages":None,
                                                                             "max_mid": 0,}))

def receipt(request):
    retval = check(request)
    if retval <> None:
        return retval
    
    try:
        return HttpResponse(jinja_environ.get_template('receipt.html').render({"rider":request.user.rider,
                                                                               "post":Post.objects.get(pk=request.REQUEST['key'])}))
        
    except:
        return HttpResponse(jinja_environ.get_template('receipt.html').render({"post":None}))

def dashboard(request):
    
    retval = check(request)
    if retval <> None:
        return retval
    
    #Delete old threads
    remove_old_posts(request.user)
    
    #results1 = Message.objects.filter(sender = rider)
    messages = Message.objects.filter(receiver = request.user.rider)
    
    #generate list reserved objects for posts made by user.
    posts = Post.objects.filter(owner=request.user.rider, status__lte=1)
    post_list = []
    for x in posts:
        #for reserved in x.reserved_set.all():
            #post_list.append(reserved)
        post_list.append([x,len(x.reserved_set.all()), len(x.reserved_set.filter(status=1))])
    #create jinja template values
    
    retval = check(request)
    if retval <> None:
        return retval
    #if "lol" in request.REQUEST.keys():
        #return HttpResponse("LOL")
    #else:
        #return HttpResponse("No Lol")
    #get latest post of rider
    date_time1 = None
    date_time2 = None
    l_p_obj = Post.objects.filter(owner=request.user.rider, date_time__gte = timezone.now(), status__lte=1)
    l_r_obj = Reserved.objects.filter(reserver=request.user.rider, status__lte=1)
    resobj = None
    pobj = None
    if len(l_p_obj) <> 0:
        l_p_obj = l_p_obj.aggregate(Min('date_time'))
        date_time1 = l_p_obj['date_time__min']
        pobj = Post.objects.get(owner=request.user.rider, date_time=date_time1)
    if len(l_r_obj) <> 0:
        mindt = None
        for x in l_r_obj:
            if x.post.date_time < timezone.now():
                continue
            if mindt == None:
                resobj = x
                mindt = x.post.date_time
            if mindt > x.post.date_time:
                resobj = x
                mindt = x.post.date_time
        date_time2 = mindt
    if date_time1 <> None:
        if (date_time1-timezone.now()).total_seconds() > 1800:
            date_time1=None
    if date_time2 <> None:
        if (date_time2-timezone.now()).total_seconds() > 1800:
            date_time2=None
    template_values = {'rider' : request.user.rider,
                    'messages' : messages[::-1],
                    'post_list' : post_list[::-1],
                    'reserved_list' : Reserved.objects.filter(reserver=request.user.rider)[::-1],
                    "date_time1":date_time1,
                    "date_time2":date_time2,
                    "reserved_obj":resobj,
                    "post_obj": pobj,
                    "nowtime": timezone.now(),
                    }
    return HttpResponse(jinja_environ.get_template('dashboard2.html').render(template_values))
    #return HttpResponse(str(template_values))
    

def settings_page(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))

    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""
                                                                                  <p>No Rider associated!.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    return HttpResponse(jinja_environ.get_template('pref.html').render({"rider":request.user.rider, 'owner':request.user.rider}))
def post_form(request):
    retval = check(request)
    if retval <> None:
        return retval
    return HttpResponse(jinja_environ.get_template('post.html').render({"rider":request.user.rider, 'owner':request.user.rider}))

def post_page(request):
    retval = check(request)
    if retval <> None:
        return retval
        
    postobj=Post.objects.get(pk=request.REQUEST['key'], status__lte=1)
    reserved=postobj.reserved_set.aggregate(Sum('status'))['status__sum']
    
    x=postobj.date_time
    
    date=x.date()
    time=x.time()
    
    reserved_obj = None
    for x in postobj.reserved_set.all():
        if x.reserver.user.username == request.user.username:
            reserved_obj = x
            break
    
    if(reserved>0):
      template_values={'post':postobj, 
		       'minus':postobj.total_seats-reserved,
		       'date':date,
		       'time':time,
		       'rider':request.user.rider,
		       'reserved_obj': reserved_obj,
		       'reserved_list': postobj.reserved_set.all(),
		       "nowtime":timezone.now(),
	              }
	              
    else: 
      template_values={'post':postobj, 
		       'minus':postobj.total_seats,
		       'time':time,
		       'date':date,
		       'rider':request.user.rider,
		       'reserved_obj': reserved_obj,
		       'reserved_list': postobj.reserved_set.all(),
		       "nowtime":timezone.now(),
	              }
              
    return HttpResponse(jinja_environ.get_template('postpage.html').render(template_values))

    
def reserve_page(request):
    retval = check(request)
    if retval <> None:
        return retval
    return HttpResponse(jinja_environ.get_template('reservepage.html').render({"rider":request.user.rider, 'post':Post.objects.get(pk=3)}))

#Forgot Password
def forgot_pass_page(request):
    if request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'<p>Please log out before requesting reset in password.</p>\
                                                                                  <p>click <a href="/">here</a> to go to the homepage</p>'}))
    return HttpResponse(jinja_environ.get_template('forgot_password.html').render({"rider":None}))

#Reset Password
@csrf_exempt
def reset_pass_page(request):
    if request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'<p>Please log out before requesting reset in password.</p>\
                                                                                  <p>click <a href="/">here</a> to go to the homepage</p>'}))
    if "reset_pass" not in request.REQUEST.keys() or 'email' not in request.REQUEST.keys():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'<p>Invalid Request</p>\
                                                                                  <p>click <a href="/">here</a> to go to the homepage</p>'}))
    reset_pass = request.REQUEST['reset_pass']
    if reset_pass == "":
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'<p>Invalid Request</p>\
                                                                                  <p>click <a href="/">here</a> to go to the homepage</p>'}))
    user = Rider.objects.filter(reset_pass=reset_pass)
    if len(user)==0:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                "text":'Invalid Request. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    user = user[0].user
    
    if user.email <> request.REQUEST['email']:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                "text":'Invalid Email. Please go back or click <a href="/">here</a> to go to the homepage'}))
    return HttpResponse(jinja_environ.get_template('reset_password.html').render({'rider':None, 'reset_pass':reset_pass}))

def change_pass_page(request):
    retval = check(request)
    if retval <> None:
        return retval
    return HttpResponse(jinja_environ.get_template('ChangePass.html').render({"rider":request.user.rider}))
        
##############################################################################
##############################################################################
##############################################################################


#Actions
@csrf_exempt
def edit_profile(request):
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))

    #Check if user has an associated rider
    #(This will be false if the admin logs in)
    
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""
                                                                                  <p>No Rider associated!.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    
    if 'image' in request.FILES.keys():
        #delete old file
        if str(request.user.rider.imageobj) <> '':
            path = cpspath + 'media/propics/' + request.user.username + request.user.rider.imageobj.url[request.user.rider.imageobj.url.rfind('.'):]
            if os.path.isfile(path):
                os.remove(path)
        request.user.rider.imageobj = request.FILES['image']
        request.user.rider.image = '/fonts/' + request.user.username + request.user.rider.imageobj.url[request.user.rider.imageobj.url.rfind('.'):]
        #request.user.rider.image = "{0}{1}".format(MEDIA_URL, request.rider.imageobj.url)
    
    
    request.user.first_name = request.REQUEST['first_name']
    request.user.last_name = request.REQUEST['last_name']
    request.user.email = request.REQUEST['email']
    
    request.user.save()
    
    request.user.rider.gender = request.REQUEST['gender']
    
    request.user.rider.phone = request.REQUEST['phone']
    request.user.rider.car_number = request.REQUEST['car_number']
    request.user.rider.auth_type = request.REQUEST['auth_type']
    request.user.rider.auth_token = request.REQUEST['auth_token']
    request.user.rider.save()
    
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Profile edit successful. Please go back or click <a href="/">here</a> to go to the homepage'}))
    

@csrf_exempt
def signup_do(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')

    if request.user.is_authenticated():
		logout(request)
		redirect_url = "/"
		if 'redirect_url' in request.REQUEST.keys():
			redirect_url = request.REQUEST['redirect_url']
		return HttpResponse(jinja_environ.get_template('redirect.html').render({"rider":None,"redirect_url":redirect_url}))
    
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    confirmpassword = request.REQUEST['confirmpassword']
        
    if password <> confirmpassword:
      return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                            "text":"""<p>Passwords don\'t match. Please Enter again.</p>
                                                                                <p>Click <a href="/signup_page/">here</a> to go back to signup page.</p>"""}))
    
    first_name = request.REQUEST['first_name']
    last_name = request.REQUEST['last_name']
    phone = request.REQUEST['phone']
    email = request.REQUEST['email']
    gender = request.REQUEST['gender']

    try:
        if len(User.objects.get(email=email))<>0:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                  "text":"""
                                                                                    <p>Someone has already registered using this email.</p>
                                                                                    <p>If you have forgotten your password, click <a href="/forgot_pass/</p>
                                                                                    <p>Click <a href="/signup_page/">here</a> to go back to signup page.</p>"""}))
    except:
        pass
    #gender = 'a'
    
    if '@' not in email or '.' not in email:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""<p>Invalid email, please Enter again.</p>
                                                                                  <p>Click <a href="/signup_page/">here</a> to go back to signup page.</p>"""}))
    
    car_number = request.REQUEST['car_number']
    
    if first_name == "":
        first_name = username
    
    try:
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        entry = Rider(user=user, phone=phone, gender=gender, car_number=car_number, verified = uuid.uuid4().hex[:5])
        
        entry.save()
        #send email to user
        login_do(request)
        return send_verification_email(request)
    except Exception as e:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""<p>Username already exists. Please enter some other username.</p>
                                                                                  <p>Click <a href="/signup_page/">here</a> to go back to signup page.</p>"""}))
    

#Called when a user enters verification code and clicks on submit
def verify(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    if not request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('loginverify.html').render({"rider":1,
                                                                                   "code":request.REQUEST['code']}))
    try:
        request.user.rider
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                             "text":"""<p>No Rider associated.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    
    code = request.REQUEST['code']
    rider = request.user.rider
    if rider.verified == '1':
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":"""<p>Already Verified.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    elif code == rider.verified:
        rider.verified = '1'
        rider.save()
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":"""<p>Verification successful.</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":"""<p>Verification Failed.</p>
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))


#Called when a user clicks button.
def logout_do(request):
    logout(request)
    redirect_url = "/"
    if 'redirect_url' in request.REQUEST.keys():
        redirect_url = request.REQUEST['redirect_url']
    #try:
        #if request.REQUEST['direct_home']=='1':
            #return HttpResponse(jinja_environ.get_template('index.html').render({"rider":None}))
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"text":"""<p>Log out successful.</p>
                                                                                  #<p>Please go back or click <a href="/">here</a> to go to the homepage"""}))
    return HttpResponse(jinja_environ.get_template('redirect.html').render({"rider":None,"redirect_url":redirect_url}))
    
#Called when a user clicks login button. 
@csrf_exempt
def login_do(request):
    
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
    
    username = request.REQUEST['username']
    password = request.REQUEST['password']
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if user.is_active:
            login(request, user)
            # Logged in now. Redirect to a success page.
            #return HttpResponse("<html><head></head><body>Login Done. <a href=\"/\">Click here to go to your Dashboard</a></body></html>")
            try:
                if request.REQUEST['code'] == user.rider.verified:
                    user.rider.verified=1
                    user.save()
                    user.rider.save()
                    if "js" in request.REQUEST.keys():
                        return HttpResponse("done")
                    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":user.rider,
                                                                                          "text":"""<p>Successfully Logged in.</p>
                                                                                              <p>Click <a href="/">here</a> to go to the homepage</p>"""}))
            except:
                pass
            return dashboard(request)
        else:
            # Return a 'disabled account' error message
            if "js" in request.REQUEST.keys():
                return HttpResponse("disabled")
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                "text":"""<p>Disabled Account.</p>
                                                                                    <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
        
    else:
        # Return an 'invalid login' error message.
        if "js" in request.REQUEST.keys():
            if len(User.objects.filter(username=request.REQUEST['username'])) == 0:
                return HttpResponse("inv_user")
            return HttpResponse("inv_pass")
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'Invalid Login. Please go back or click <a href="/">here</a> to go to the homepage'}))
    

#Forgot Password
@csrf_exempt
def forgot_pass(request):
    if request.user.is_authenticated():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'<p>Please log out in order to request for a password reset.</p>\
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
    if 'username' not in request.REQUEST.keys() or 'email' not in request.REQUEST.keys():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'Invalid Request. Please go back or click <a href="/">here</a> to go to the homepage'}))
    user = User.objects.filter(username=request.REQUEST['username'])
    if len(user) == 0:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'User Does not exist. Please go back or click <a href="/">here</a> to go to the homepage'}))
    user = user[0]
    if user.email <> request.REQUEST['email']:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'Invalid email. Please go back or click <a href="/">here</a> to go to the homepage'}))
    user.rider.reset_pass = uuid.uuid4().hex
    user.rider.save()
    
    subject = "Password Reset Request"
    msg = 'Subject: %s \n\nYou have requested for a password reset on CarPoolSen.com\n\
    Please click on the following link (or copy paste in your browser) to reset your password.\n\n\
    http://localhost:8000/reset_pass_page/?reset_pass=%s&email=%s\n\n\
    If you have not requested for a reset of password, please ignore.' % (subject, user.rider.reset_pass, user.email)
    
    x = send_email(msg, user.email)
    if x[0] == 0:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'Could not process request, please try again later by going back or clicking <a href="/">here</a> to go to the homepage'}))
    else:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":'<p>An email has been sent to your regestered email address.</p>\
                                                                                  <p>Check your email and click on the link to reset your password.</p>\
                                                                                  <p>Click <a href="/">here</a> to go to the homepage</p>'}))
    
#Change Password
@csrf_exempt
def change_pass(request):
    if "reset_pass" in request.REQUEST.keys():
        reset_pass = request.REQUEST['reset_pass']
        if reset_pass == "":
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                  "text":'<p>Invalid Request</p>\
                                                                                      <p>click <a href="/">here</a> to go to the homepage</p>'}))
        user = Rider.objects.filter(reset_pass=reset_pass)
        if len(user)==0 or 'pass' not in request.REQUEST.keys():
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                  "text":'Invalid Request. Please go back or click <a href="/">here</a> to go to the homepage'}))
        user = user[0].user
        user.set_password(request.REQUEST['pass'])
        user.save()
        user.rider.reset_pass = ""
        user.rider.save()
        logout(request)
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":1,
                                                                              "text":'Password Changed. Please click <a href="/logout_do">here</a> to go to the homepage or log in again.'}))
    else:
        retval = check(request)
        if retval <> None:
            return retval
        if "pass" not in request.REQUEST.keys() or "oldpass" not in request.REQUEST.keys():
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'Invalid Request. Please go back or click <a href="/">here</a> to go to the homepage'}))
        if not request.user.check_password(request.REQUEST['oldpass']):
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'Invalid Old Password. Please go back or click <a href="/">here</a> to go to the homepage'}))
        request.user.set_password(request.REQUEST['pass'])
        request.user.save()
        logout(request)
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":1,
                                                                              "text":'Password Changed. Please click <a href="/logout_do">here</a> to go to the homepage and log in again.'}))
        
#Called when a user cancels his post
@csrf_exempt
def cancel_post(request):
	retval = check(request)
	if retval <> None:
		return retval
	#using get for now.
	user = request.user

	#Not allowed to delete if user is not logged in. Not called, but to take edge cases into consideration.

	postid = request.REQUEST['postid']
	#return HttpResponse(postid)

	try:
		entry = Post.objects.get(pk=int(postid))
		#if entry.date_time < timezone.now():
			#return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
																					#"text":'<p>Trip has already started, cannot cancel now.</p>\
																						#<p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
		if entry.owner.user.pk == user.pk:
			if entry.reserved_set.aggregate(Sum('status'))['status__sum'] > 0:
				owner=entry.owner
				if owner.neg_flags<5:
					owner.neg_flags += 1
					owner.save()
			entry.status = 2
			entry.changed = 1
			entry.save()
			
			#Delete all reserved entries for that post too
			#for y in entry.reserved_set.all():
				#SMS notification
				#y.delete()
			#entry.delete()

		else:
			return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
																				"text":'<p>Not enough permissions.</p>\
																					<p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
	except Exception as e:
		return HttpResponse(e)
    #+ "<a href="/"> Click here to go to Home Page </a>")
    
	return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Post Cancelled successfully. Please go back or click <a href="/">here</a> to go to the homepage'}))

@csrf_exempt
def post_new(request):
    global month
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    #New Post
    owner = request.user.rider
    car_number = request.REQUEST['car_number']
    total_seats = int(request.REQUEST['total_seats'])
    phone = request.REQUEST['phone']
    fro = request.REQUEST['fro']
    to = request.REQUEST['to']
    
    #Date and time format: dd mm yyyy - hh:mm
    date_time=request.REQUEST['date_time']
    date_time=date_time.split(' ')
    date=date_time[0:3]
    time=date_time[4]
    time=time.split(':')
    
    date_time = datetime.datetime(day=int(date[0]),
                                  month=month.index(date[1]), 
                                  year=int(date[2]), 
                                  hour=int(time[0]),
                                  minute=int(time[1]), 
                                  second=0, 
                                  microsecond=0,)
        
    ac = int(request.REQUEST['ac'])
    men_women = 0
    men_women = int(request.REQUEST['men_women'])
    
    available_to = int(request.REQUEST['available_to'])
    
    autoaccept = 0
    try:
        autoaccept += int(request.REQUEST['autoaccept'])
    except:
        pass
    
    cost = int(request.REQUEST['cost'])
    
    sms_noti = 0
    try:
        sms_noti += int(request.REQUEST['sms_noti'])
    except:
        pass
    
    #Check for duplicate phone number here
    
    #Check for empty car number
    if car_number.strip() == '':
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'Invalid Car number. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    tempres = Post.objects.filter(owner=owner)
    for x in tempres:
        if math.fabs((x.date_time.replace(tzinfo=None)-date_time.replace(tzinfo=None)).total_seconds()) < 1800:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":"""
                                                                                      <p>You already have a post within 30 minutes of this post.</p>
                                                                                      <p>The only way you can take care of both posts is by driving too fast</p>
                                                                                      <p>And we do not promote that.</p>
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"""}))
    
    entry = Post(owner=owner, 
                 car_number=car_number, 
                 total_seats=total_seats,
                 phone=phone, 
                 fro=fro, 
                 to=to, 
                 date_time=date_time, 
                 ac=ac,
                 men_women=men_women,
                 available_to=available_to,
                 autoaccept=autoaccept,
                 cost=cost,
                 sms_noti=sms_noti,
                 )
    entry.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Post successful. Please go back or click <a href="/">here</a> to go to the homepage'}))

def reserve(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
        
    try:
        reserver = request.user.rider
        postid = request.REQUEST['postid']
        postobj = Post.objects.get(pk=postid)
        
        if reserver == postobj.owner:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                           "text":'<p>You can\'t reserve your own post.</p>\
                                                                               <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        
        if postobj.date_time < timezone.now():
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                           "text":'<p>Trip already started, cannot reserve now.</p>\
                                                                               <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        
        if (reserver.gender=='m' and postobj.men_women==1) or (reserver.gender=='f' and postobj.men_women==2):
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>You are not allowed to reserve this post due to gender preferences of the owner.</p>\
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        
        tempres = Reserved.objects.filter(owner=owner)
        for x in tempres:
            if math.fabs((x.post.date_time.replace(tzinfo=None)-postobj.date_time.replace(tzinfo=None)).total_seconds()) < 1800:
                return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>You already have a reservation within 15 minutes of this request.</p>\
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        entry = Reserved(post = postobj, reserver = reserver)
        
        
        #Check if automatic accept it on
        if postobj.autoaccept==1:
            #Check if there are seats available
            if postobj.total_seats > postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
                entry.status = 1
        entry.save()
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>Reservation request successfully sent.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))

    
def accept(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    
    try:
        owner = request.user.rider
        resid = request.REQUEST['resid']
        try:
            Reserved.objects.get(pk=resid)
        except Exception as e:
            return HttpResponse(e)
        resobj = Reserved.objects.get(pk=resid)
        
        postobj = resobj.post
        if postobj.total_seats > postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
            resobj.status = 1
            resobj.save()
        else:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'Seats full. Please go back or click <a href="/">here</a> to go to the homepage'}))
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Accepted request. Click <a href="/">here</a> to go back to the post.'}))

def revoke(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    
    try:
        owner = request.user.rider
        resid = request.REQUEST['resid']
        try:
            Reserved.objects.get(pk=resid)
        except Exception as e:
            return HttpResponse(e)
        resobj = Reserved.objects.get(pk=resid)
        
        #postobj = resobj.post
        #if postobj.total_seats > postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
            #resobj.status = 1
            #resobj.save()
        #if resobj.status == 1:
            #resobj.status = 0
            #resobj.save
        if resobj.post.date_time < timezone.now():
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                           "text":'<p>Trip already started, cannot reserve now.</p>\
                                                                               <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        resobj.delete()
        #else:
            #return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  #"text":'Request already revoked/pending. Please go back or click <a href="/">here</a> to go to the homepage'}))
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>Cancelled reservation successfully.</p>\
                                                                              <p>Click <a href="/">here</a> to go back to the post</p>'}))

def cancel_res(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    
    retval = check(request)
    if retval <> None:
        return retval

    try:
        reserver = request.user.rider
        resid = request.REQUEST['resid']
        resobj = Reserved.objects.get(pk=resid)
        
        if resobj.reserver.pk == reserver.pk:
            resobj.delete()
        else:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                                  "text":'Invalid User. Please go back or click <a href="/">here</a> to go to the homepage'}))
        if resobj.post.date_time < timezone.now():
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                           "text":'<p>Trip already started, cannot reserve now.</p>\
                                                                               <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        #entry = Reserved(post = postobj, reserver = reserver)
        
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>Reservation cancelled successfully.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        
@csrf_exempt
def search_do(request):
    global month
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
    #check for user login
    rider = None
    if request.user.is_authenticated():
        rider = request.user.rider
    
    #try:
        #request.user.rider
    #except:
        #return HttpResponse(jinja_environ.get_template('notice.html').render({"text":'No Rider associated. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    #Get batch number
    batch = 0
    if 'batch' in request.REQUEST.keys():
        batch = int(request.REQUEST['batch'])
    
    #batch length
    batchlen=100
    if 'batchlen' in request.REQUEST.keys():
        batchlen = int(request.REQUEST['batchlen'])
    
    fro = request.REQUEST['fro']
    to = request.REQUEST['to']
    #date = request.REQUEST['date_time'].split(" ")

    #Date and time format: dd mm yyyy - hh:mm
    start_date_time=Post.objects.filter(status__lte=1).aggregate(Min('date_time'))['date_time__min']
    if request.REQUEST['start_date_time']<>'':
        start_date_time=request.REQUEST['start_date_time']
        start_date_time=start_date_time.split(' ')
        startdate=start_date_time[0:3]
        starttime=start_date_time[4]
        starttime=starttime.split(':')
        start_date_time = datetime.datetime(day=int(startdate[0]),
                                            month=month.index(startdate[1]), 
                                            year=int(startdate[2]), 
                                            hour=int(starttime[0]),
                                            minute=int(starttime[1]), 
                                            second=0, 
                                            microsecond=0,)

    #Date and time format: dd mm yyyy - hh:mm
    end_date_time=Post.objects.filter(status__lte=1).aggregate(Max('date_time'))['date_time__max']
    if request.REQUEST['end_date_time']<>'':
        end_date_time=request.REQUEST['end_date_time']
        end_date_time=end_date_time.split(' ')
        enddate=end_date_time[0:3]
        endtime=end_date_time[4]
        endtime=endtime.split(':')
        end_date_time = datetime.datetime(day=int(enddate[0]),
                                          month=month.index(enddate[1]), 
                                          year=int(enddate[2]), 
                                          hour=int(endtime[0]),
                                          minute=int(endtime[1]), 
                                          second=0, 
                                          microsecond=0,)
    
    #[batch*batchlen:(batch+1)*batchlen]
    men_women=request.REQUEST['men_women']
    results = []
    
    def iterate(fro,to,men_women,start_date_time,end_date_time,pobject):
		if men_women <> "0":
			if end_date_time==None and start_date_time==None:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, men_women=int(men_women), status__lte=1)
			elif end_date_time==None and not start_date_time==None:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__gte=start_date_time, men_women=int(men_women), status__lte=1)
			elif (not end_date_time==None) and start_date_time==None:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, men_women=int(men_women), status__lte=1)
			else:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, date_time__gte=start_date_time, men_women=int(men_women), status__lte=1)
		else:
			if end_date_time==None and start_date_time==None:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, status__lte=1)
			elif end_date_time==None and not start_date_time==None:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__gte=start_date_time, status__lte=1)
			elif (not end_date_time==None) and start_date_time==None:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, status__lte=1)
			else:
				results = pobject.filter(fro__icontains=fro, to__icontains=to, date_time__lte=end_date_time, date_time__gte=start_date_time, status__lte=1)
		return results

    resultlist=[]
    resultlist+=iterate(fro,to,men_women,start_date_time,end_date_time,Post.objects)
    fro1=fro.split(', ')
    to1=to.split(', ')
    if len(fro1) <3 or len(to1) <3 :
		return HttpResponse(jinja_environ.get_template('notice.html').render({'rider':request.user.rider, 'text':"Please be more specific in your search. Click <a href=\"/\">here</a> to go back to homepage"}))

    fro2=fro1[-3] +", "+ fro1[-2] +", "+ fro1[-1]
    to2=to1[-3] +", "+ to1[-2] +", "+ to1[-1]
    #return HttpResponse(fro2 + to2)
    pobject=iterate(fro2,to2,men_women,start_date_time,end_date_time,Post.objects)
    #return HttpResponse(len(pobject))
    #temp2=[]
    
    if len(fro1)>3 and len(to1)>3:
		print "x"
		resultlist+=iterate(fro1[0],to1[0],men_women,start_date_time,end_date_time,pobject)
    elif len(fro1)>3 and len(to1)<3:
		resultlist+=iterate(fro1[0],to1[0],men_women,start_date_time,end_date_time,pobject)
    elif len(fro1)<3 and len(to1)>3:
		resultlist+=iterate(fro1[0],to1[0],men_women,start_date_time,end_date_time,pobject)
		
    if len(fro1)>4 and len(to1)>4:
		print "y"
		resultlist+=iterate(fro1[1],to1[1],men_women,start_date_time,end_date_time,pobject)
    elif len(fro1)>4 and len(to1)<4:
		resultlist+=iterate(fro1[1],to1[1],men_women,start_date_time,end_date_time,pobject)
    elif len(fro1)<4 and len(to1)>4:
		resultlist+=iterate(fro1[1],to1[1],men_women,start_date_time,end_date_time,pobject)
		
    if len(fro1)>5 and len(to1)>5:
		print "z"
		resultlist+=iterate(fro1[2],to1[2],men_women,start_date_time,end_date_time,pobject)
    elif len(fro1)>5 and len(to1)<5:
		resultlist+=iterate(fro1[2],to1[2],men_women,start_date_time,end_date_time,pobject)
    elif len(fro1)<5 and len(to1)>5:
		resultlist+=iterate(fro1[2],to1[2],men_women,start_date_time,end_date_time,pobject)
    
    resultlist+=pobject
    resultlist=list(set(resultlist))
    template_values = {
    "rider":rider,
    'result_list':resultlist[batch*batchlen:(batch+1)*batchlen],
    'searched':Post(to=to, fro=fro),
    'batch':batch,
    'batchlen':batchlen,
    }
    
    return HttpResponse(jinja_environ.get_template('searchresult.html').render(template_values))
    #return HttpResponse(len(results))
     
@csrf_exempt
def edit_post(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
    
    retval = check(request)
    if retval <> None:
        return retval
    
    
    #Get Post
    owner = request.user.rider
    postid = request.REQUEST['postid']
    postobj = None
    try:
        postobj = Post.objects.get(pk=postid, status__lte=1, date_time__gte=timezone.now())
    except Exception as e:
        return HttpResponse(e)
    
    #Get new details.
    
    if postobj.owner.user.username <> owner.user.username:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider, 
                                                                              "text":'Invalid User. Please go back or click <a href="/">here</a> to go to the homepage'}))
    if postobj.date_time < timezone.now():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'The trip has started, cannot edit post anymore. Please go back or click <a href="/">here</a> to go to the homepage'}))
    #owner = request.user.rider
    car_number = request.REQUEST['car_number']
    if car_number.strip() == '':
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'Invalid Car number. Please go back or click <a href="/">here</a> to go to the homepage'}))
    total_seats = int(request.REQUEST['total_seats'])
    phone = request.REQUEST['phone']
    #fro = request.REQUEST['fro']
    #to = request.REQUEST['to']
    autoaccept = 0
    try:
        autoaccept += int(request.REQUEST['autoaccept'])
    except:
        pass
    
    date_time=request.REQUEST['date_time']
    date_time=date_time.split(' ')
    date=date_time[0:3]
    time=date_time[4]
    time=time.split(':')
    
    date_time = datetime.datetime(day=int(date[0]),
                                  month=month.index(date[1]), 
                                  year=int(date[2]), 
                                  hour=int(time[0]),
                                  minute=int(time[1]), 
                                  second=0, 
                                  microsecond=0,)
    
    ac = int(request.REQUEST['ac'])
    men_women = int(request.REQUEST['men_women'])
    available_to = int(request.REQUEST['available_to'])
    
    if total_seats < postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'You already have more reserved users than seats. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    postobj.car_number = car_number
    postobj.total_seats = total_seats
    postobj.phone = phone
    #postobj.fro = fro
    #postobj.to = to
    postobj.date_time = date_time
    postobj.ac = ac
    postobj.men_women = men_women
    postobj.available_to = available_to
    postobj.autoaccept = autoaccept
    
    postobj.save()
    neg = 0
    for x in postobj.reserved_set.all():
        if x.edited == 0:
            if x.status == 1:
                neg = 1
        x.edited = 1
        x.save()
    postobj.owner.neg_flags += neg
    postobj.owner.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Post edited successfully. Click <a href="/">here</a> to the post details page'}))
@csrf_exempt
def reset_edited(request):
    retval = check(request)
    if retval <> None:
        return retval
    resobj = Reserved.objects.filter(pk=request.REQUEST['resid'])
    if len(resobj) == 0:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'Invalid Request. Click <a href="/">here</a> to the post details page'}))
    resobj[0].edited = 0
    resobj[0].save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Done. Click <a href="/">here</a> to the post details page'}))
@csrf_exempt
def send_message(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    
    sender = request.user.rider
    try:
		receiver = User.objects.get(username=request.REQUEST['to']).rider
		message = request.REQUEST['message']
        
		if sender==receiver:
			return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider, "text": 'Sending messages to self is a sign of narcissism. Click <a href="/">here</a> to go back to homepage.'}))

		else:
			entry = Message(sender = sender, receiver = receiver, message = message)
			entry.save()
			
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Message Sent. Please go back or click <a href="/">here</a> to go to the homepage'}))

def view_messages(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    
    rider = request.user.rider
    results1 = Message.objects.filter(sender = rider)
    results2 = Message.objects.filter(receiver = rider)
    
    return HttpResponse((len(results1) + len(results2)))

@csrf_exempt
def read_message(request):
  
    print "LOL"
    retval = check(request)
    if retval <> None:
        return retval
    
    key = request.REQUEST["mid"]
    
    try:
	result = Message.objects.filter(pk=mid)
	result.rmailbox=2
	result.save();
	return HttpResponse("1")
    except Exception as e:
        return HttpResponse("0"+str(e))
@csrf_exempt
def delete_message(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    
    rider = request.user.rider
    mids = request.REQUEST['mids']
    mids = mids.split(',')
    print mids
    for mid in mids:
		message = None
		
		try:
			message = Message.objects.get(pk=int(mid))
 		except:
			return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
											"text":'No such message exists!. Please go back or click <a href="/">here</a> to go to the homepage'}))
		# if message.sender.pk == rider.pk:
			# message.smailbox = 0
		if message.receiver.pk == rider.pk:
			message.rmailbox = 0
		# if message.rmailbox + message.smailbox == 0:
			#This means the message has been deleted from both the sender and the receiver's side.
			#The message will be deleted after one month
			#if message.date_time.month - timezone.now().month >= 1:
			#message.delete()
			
			#For now, message will be deleted. In the future, we may implement restoring of messages, in which case
			#We will keep the delete after one month feature.
			message.delete()
		else:
			message.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
											"text":'<p>Messege deleted successfully.</p>\
											<p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
		
  #reply to a message
  
@csrf_exempt
def reply(request):
    retval = check(request)
    if retval <> None:
        return retval
    
    mid = request.POST['mid']
    message = request.POST['message']
    receiver = None
    try:
        receiver = Message.objects.get(pk=int(mid)).sender
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":"<p>Message not found.</p>\
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>"}))
    entry = Message(sender = request.user.rider, receiver = receiver, message = message)
    entry.save()
    
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>Message sent successfully.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))

#Search for username
@csrf_exempt
def search(request):
    #if request.method == 'POST':
        #username = request.POST['username']
        #length = 1
        #try:
            #User.objects.get(username=username)
        #except Exception as e:
            #return HttpResponse("0")
        #return HttpResponse("1")
    #if request.method == "POST":
    if True:
        if request.REQUEST['search'] == 'phone':
            return HttpResponse("0")
        elif request.REQUEST['search'] == 'username':
            if len(User.objects.filter(username=request.REQUEST['username'])) <> 0:
                return HttpResponse("1")
            return HttpResponse("0")
        elif request.REQUEST['search'] == 'email':
            if len(User.objects.filter(email=request.REQUEST['email'])) <> 0:
                return HttpResponse("1")
            else:
                return HttpResponse("0")

#save facebook token
@csrf_exempt
def facebook(request):
    retval = check(request)
    if retval <> None:
        return retval
    if request.method == "POST":
        if "access_token" in request.REQUEST.keys():
            fbobj = GraphAPI(str(request.REQUEST['access_token']))
            return HttpResponse(json.dumps(fbobj.get_connections("me","friends"), indent=1))
    return HttpResponse(jinja_environ.get_template('facebook.html').render({"rider":request.user.rider, "text": request.get_full_path()}))


def delete_account(request):
    retval = check(request)
    if retval <> None:
        return retval
    #checking
    if request.REQUEST['username'] <> request.user.username or request.REQUEST['email'] <> request.user.email <> request.REQUEST['car_number'] <> request.user.rider.car_number:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'<p>Message sent successfully.</p>\
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
    for x in Message.objects.filter(sender=request.user.rider):
        x.delete()
    for x in Message.objects.filter(receiver=request.user.rider):
        x.delete()
    for x in Reserved.objects.filter(reserver=request.user.rider):
        x.delete()
    for x in Post.objects.filter(owner=request.user.rider):
        x.delete()
    request.user.rider.delete()
    request.user.delete()
    logout(request)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                          "text":'<p>Account Deleted Successfully.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
@csrf_exempt
def invite(request):

    retval = check(request)
    if retval <> None:
        return retval
      
    try:
        email=request.REQUEST['email_id']
        email=email.split(',')
        email = list(set(email))
        for i in range(0,len(email)):
            email[i]=email[i].strip();
            
        rider=request.user.rider
        message=request.REQUEST['message']
        #subject = 'CarPool.com Invitation Email'
        message="Subject:CarPool.com Invitation\n" + rider.user.first_name + " " + rider.user.last_name + " has invited you to join CarPoolSen!\n\n" + rider.user.first_name + " says:\n" + message + "\n\nClick http://localhost:8000 to visit the website."
      
        for i in range(0,len(email)):
            x = send_email(message, email[i])
        try:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>Emails Sent Successfully.</p>\
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
        except:
            pass
    except Exception as e:
        try:
            return HttpResponse(e)
        except:
            pass

#@csrf_exempt
def report_user(request):
    retval = check(request)
    if retval <> None:
        return retval
        
    if 'user' not in request.REQUEST.keys():
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>Invalid user.</p>\
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
    user = User.objects.filter(username=request.REQUEST['user'])
    if len(user)==0:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>Invalid user.</p>\
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))    
    
    user = user[0]
    flag=Rating.objects.filter(rated=user.rider, rater=request.user.rider)
    
    if len(flag) == 0 and len(flag) <5:
        user.rider.user_rating += 1
        user.rider.save()
        rateobj=Rating(rated=user.rider, rater=request.user.rider)
        rateobj.save()
    
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>User reported successfully.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
    else:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>You have already reported this user and can\'t report again. </p>\
                                                                          <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))

#Testing functions:
def tempage(request):
    retval = check(request)
    if retval <> None:
        return retval
    #if "lol" in request.REQUEST.keys():
        #return HttpResponse("LOL")
    #else:
        #return HttpResponse("No Lol")
    #get latest post of rider
    date_time1 = None
    date_time2 = None
    l_p_obj = Post.objects.filter(owner=request.user.rider)
    l_r_obj = Reserved.objects.filter(reserver=request.user.rider)
    resobj = None
    pobj = None
    if len(l_p_obj) <> 0:
        l_p_obj = l_p_obj.aggregate(Min('date_time'))
        date_time1 = l_p_obj['date_time__min']
        pobj = Post.objects.get(owner=request.user.rider, date_time=date_time1)
    if len(l_r_obj) <> 0:
        mindt = None
        for x in l_r_obj:
            if mindt == None:
                resobj = x
                mindt = x.post.date_time
            if mindt > x.post.date_time:
                resobj = x
                mindt = x.post.date_time
        date_time2 = mindt
    if (date_time1-timezone.now()).total_seconds() > 1800:
        date_time1=None
    if (date_time2-timezone.now()).total_seconds() > 1800:
        date_time2=None
    return HttpResponse(jinja_environ.get_template('timer.html').render({'rider':request.user.rider, "date_time1":date_time1, "date_time2":date_time2, "reserved_obj":resobj, "post_obj": pobj}))
#temp form checksdef upload_file(request):
@csrf_exempt
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            response = "Form is valid"
        else:
            response = "Failed to upload"
    return HttpResponse(response)

