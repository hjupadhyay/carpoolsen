# Create your views here.
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
from mainapp.checker import check
jinja_environ = jinja2.Environment(loader=jinja2.FileSystemLoader(['ui']));

#Dummy request object
class Dum:
    REQUEST = {}
#Perform basic checks on user

#send email function
def send_email(msg, entry):
    gmailLogin = 'carpoolsen'
    gmailPas = 'qwertqwert!'
    fro = gmailLogin + "@gmail.com"
    
    to = entry.email
    
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
    
    x = send_email(msg, entry)
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
    return HttpResponse(jinja_environ.get_template('signup.html').render({"rider":None}))
def login_page(request):
    return HttpResponse(jinja_environ.get_template('login.html').render({"rider":None}))
def contactus(request):
    rider = None
    if request.user.is_authenticated():
        rider = request.user.rider
    return HttpResponse(jinja_environ.get_template('ContactUs.html').render({"rider":rider}))
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
    return HttpResponse(jinja_environ.get_template('profileedit.html').render({"rider":request.user.rider}))

def profile(request):
    retval = check(request)
    if retval <> None:
        return retval

    try:
        riderid = request.REQUEST['id']
        if riderid == request.user.rider.pk:
            return HttpResponse(jinja_environ.get_template('profile.html').render({"rider":request.user.rider, "check":"1"}))
        else:
            return HttpResponse(jinja_environ.get_template('profile.html').render({"rider":Rider.objects.get(pk=riderid), "check":"0"}))
    except:
        return HttpResponse(jinja_environ.get_template('profile.html').render({"rider":request.user.rider, "check":"1"}))
    #return HttpResponse(request.user.first_name + " " + request.user.last_name + "'s Profile Page")
    

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
    #results1 = Message.objects.filter(sender = rider)
    messages = Message.objects.filter(receiver = request.user.rider)
    
    #generate list reserved objects for posts made by user.
    posts = Post.objects.filter(owner=request.user.rider)
    post_list = []
    for x in posts:
        for reserved in x.reserved_set.filter(status = 1):
            post_list.append(reserved)
    #create jinja template values
    
    template_values = {'rider' : request.user.rider,
                    'messages' : messages,
                    'post_list' : post_list,
                    'reserved_list' : Reserved.objects.filter(reserver=request.user.rider),
                    }
    return HttpResponse(jinja_environ.get_template('dashboard.html').render(template_values))
    #return HttpResponse(str(template_values))
    


def post_form(request):
    retval = check(request)
    if retval <> None:
        return retval
    return HttpResponse(jinja_environ.get_template('post.html').render({"rider":request.user.rider, 'owner':request.user.rider}))

def post_page(request):
    retval = check(request)
    if retval <> None:
        return retval
        
    postobj=Post.objects.get(pk=request.REQUEST['key'])
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
	              }
	              
    else: 
      template_values={'post':postobj, 
		       'minus':postobj.total_seats,
		       'time':time,
		       'date':date,
		       'rider':request.user.rider,
		       'reserved_obj': reserved_obj,
		       'reserved_list': postobj.reserved_set.all(),
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
    
    #image = request.FILES['image']
    #image.save('/home/rishav/Desktop/x.jpg',image.readlines(),True)
    #return HttpResponse('0')
    
    
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
                                                                          "text":'Post successful. Please go back or click <a href="/">here</a> to go to the homepage'}))
    

@csrf_exempt
def signup_do(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')

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
        return HttpResponse(jinja_environ.get_template('loginverify.html').render({"rider":None,
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


#Called when a user clicks logout button.
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
    http://localhost:8000/change_pass?reset_pass=%s\n\n\
    If you have not requested for a reset of password, please ignore.' % (subject, user.rider.reset_pass)
    
    x = send_email(msg, user)
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
        if entry.owner.user.pk == user.pk:
            #Delete all reserved entries for that post too
            for y in entry.reserved_set.all():
                #SMS notification
                y.delete()
            entry.delete()
        else:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'<p>Not enough permissions.</p>\
                                                                                      <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
    except Exception as e:
        return HttpResponse(e + "<a href="/"> Click here to go to Home Page </a>")
    
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Post successful. Please go back or click <a href="/">here</a> to go to the homepage'}))

@csrf_exempt
def post_new(request):
    
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
    
    #Date and time format: yyyy-mm-dd-hh-mm
    date=request.REQUEST['date']
    date=date.split('/')
    time=request.REQUEST['time']
    time=time.split(':')
    #date_time = datetime.datetime(year=int(request.REQUEST['year']),
                                  #month=int(request.REQUEST['month']), 
                                  #day=int(request.REQUEST['day']), 
                                  #hour=int(request.REQUEST['hour']),
                                  #minute=int(request.REQUEST['min']), 
                                  #second=0, 
                                  #microsecond=0,)
    date_time = datetime.datetime(year=date[0],
                                  month=date[1], 
                                  day=date[2], 
                                  hour=time[0],
                                  minute=time[1], 
                                  second=0, 
                                  microsecond=0,)
    
    
    ac = int(request.REQUEST['ac'])
    men_women = 0
    try:
        men_women += int(request.REQUEST['men'])
    except:
        pass
    try:
        men_women += int(request.REQUEST['women'])
    except:
        pass
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
                                                                          "text":'Accepted request. Please go back or click <a href="/">here</a> to go to the homepage'}))

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
        if resobj.status == 1:
            resobj.status = 0
            resobj.save()
        else:
            return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                                  "text":'Request already revoked/pending. Please go back or click <a href="/">here</a> to go to the homepage'}))
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>Cancelled reservation successfully.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))

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
        #entry = Reserved(post = postobj, reserver = reserver)
        
    except Exception as e:
        return HttpResponse(e)
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'<p>Reservation cancelled successfully.</p>\
                                                                              <p>Please go back or click <a href="/">here</a> to go to the homepage</p>'}))
    
@csrf_exempt
def search_do(request):
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
    
    fro = request.REQUEST['fro']
    to = request.REQUEST['to']
    #dtstart = request.REQUEST['dtstart'].split("-")
    #dtend = request.REQUEST['dtend'].split("-")
    date = request.REQUEST['date'].split("/")
    time_start = request.REQUEST['time_start'].split(":")
    time_end = request.REQUEST['time_end'].split(":")
    men_women = request.REQUEST['men_women']
    dtstart = datetime.datetime(year=int(date[2]), month=int(date[1]), day=int(date[0]), hour=int(time_start[0]),
                                minute=int(time_start[1]), second=0, microsecond=0)
    dtend = datetime.datetime(year=int(date[2]), month=int(date[1]), day=int(date[0]), hour=int(time_end[0]),
                                minute=int(time_end[1]), second=0, microsecond=0)
    results = Post.objects.filter(fro=fro, to=to, date_time__lte=dtend, date_time__gte=dtstart, men_women=int(men_women))
    template_values = {
        "rider":rider,
        'result_list':results,
        'searched':Post(to=to, fro=fro)
        }
    
    return HttpResponse(jinja_environ.get_template('searchresult.html').render(template_values))
    #return HttpResponse(len(results))
    

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
        postobj = Post.objects.get(pk=postid)
    except Exception as e:
        return HttpResponse(e)
    
    #Get new details.
    
    if postobj.owner.user.username <> owner.user.username:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'Invalid User. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    #owner = request.user.rider
    car_number = request.REQUEST['car_number']
    total_seats = int(request.REQUEST['total_seats'])
    phone = request.REQUEST['phone']
    fro = request.REQUEST['fro']
    to = request.REQUEST['to']
    autoaccept = request.REQUEST['autoaccept']
    
    #Date and time format: yyyy-mm-dd-hh-mm
    date_time = request.REQUEST['date_time'].split("-")
    date_time = datetime.datetime(year=int(date_time[0]),
                                  month=int(date_time[1]),
                                  day=int(date_time[2]),
                                  hour=int(date_time[3]), 
                                  minute=int(date_time[4]),
                                  second=0, 
                                  microsecond=0,)
    ac = int(request.REQUEST['ac'])
    men_women = int(request.REQUEST['men_women'])
    available_to = int(request.REQUEST['available_to'])
    
    #entry = Post(owner=owner, 
                 #car_number=car_number, 
                 #total_seats=total_seats, 
                 #phone=phone, 
                 #fro=fro, 
                 #to=to,
                 #date_time=date_time, 
                 #ac=ac,
                 #men_women=men_women,
                 #available_to=available_to)
    if total_seats < postobj.reserved_set.aggregate(Sum('status'))['status__sum']:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'You already have more reserved users than seats. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    postobj.car_number = car_number
    postobj.total_seats = total_seats
    postobj.phone = phone
    postobj.fro = fro
    postobj.to = to
    postobj.date_time = date_time
    postobj.ac = ac
    postobj.men_women = men_women
    postobj.available_to = available_to
    postobj.autoaccept = autoaccept
    
    postobj.save()
    return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                          "text":'Post edited successfully. Please go back or click <a href="/">here</a> to go to the homepage'}))


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
        
        entry = Message(sender = sender, receiver = receiver, message = message)
        entry.save()
    except Exception as e:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":None,
                                                                              "text":"""<p>505 Internal Error</p>
                                                                                  <p>""" + e + """</p>
                                                                                  <p>Please go back or click <a href="/">here</a> to go to the homepage"""}))
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
        
def delete_message(request):
    #if request.method == 'GET':
        #return HttpResponse('invalid request')
        
    #check for user login
    retval = check(request)
    if retval <> None:
        return retval
    
    rider = request.user.rider
    mid = request.REQUEST['mid']
    message = None
    try:
        message = Message.objects.get(pk=mid)
    except:
        return HttpResponse(jinja_environ.get_template('notice.html').render({"rider":request.user.rider,
                                                                              "text":'No such message exists!. Please go back or click <a href="/">here</a> to go to the homepage'}))
    
    if message.sender.pk == rider.pk:
        message.smailbox = 0
    if message.receiver.pk == rider.pk:
        message.rmailbox = 0
    if message.rmailbox + message.smailbox == 0:
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
def search_username(request):
    if request.method == 'POST':
        username = request.POST['username']
        length = 1
        try:
            User.objects.get(username=username)
        except Exception as e:
            return HttpResponse("0")
        return HttpResponse("1")

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


#Testing functions:
def tempage(request):
    retval = check(request)
    if retval <> None:
        return retval
    #if "lol" in request.REQUEST.keys():
        #return HttpResponse("LOL")
    #else:
        #return HttpResponse("No Lol")
    return HttpResponse(jinja_environ.get_template('tempage.html').render({'rider':request.user.rider}))
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
