from paths import cpspath
from django import forms
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os
from uuid import uuid4
## Create your models here.
#class Poll(models.Model):
    #question = models.CharField(max_length=200)
    #pub_date = models.DateTimeField('date published')
    #def __unicode__(self):  # Python 3: def __str__(self):
        #return self.question
    #def was_published_recently(self):
        #return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

#class Choice(models.Model):
    #poll = models.ForeignKey(Poll)
    #choice_text = models.CharField(max_length=200)
    #votes = models.IntegerField(default=0)
    #def __unicode__(self):  # Python 3: def __str__(self):
        #return self.choice_text
        


def update_filename(instance, filename):
    path = cpspath + 'media/propics/'
    format = instance.user.username + filename[filename.rfind('.'):]
    return os.path.join(path, format)

class Rider(models.Model):
    
    #current_post = models.ForeignKey(Post)

    #dummy = models.IntegerField(default=0)
    #username = models.CharField(max_length=200, unique=True)
    user = models.OneToOneField(User)
    #name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    #email = models.CharField(max_length=200)
    gender = models.CharField(max_length=1)
    car_number = models.CharField(max_length=20)
    
    #path to image
    image = models.CharField(max_length=300, default="https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQoAjhBuCjGc3JJb0HLIKePs15GE09p8_wfy7BW2LtoeuTSo-eQKg")
    
    #image
    imageobj = models.ImageField(upload_to=update_filename)
    #pass function here
    
    #1 - unverified
    #any other number = verification code
    verified = models.CharField(max_length=5)
    
    #0 - PAN
    #1 - Driving License
    #2 - Voter Card
    auth_type = models.CharField(max_length="20", default="None")
    auth_token = models.CharField(max_length=200, default = "0")
    
    
    user_rating = models.IntegerField(default=0)
    neg_flags = models.IntegerField(default=0)
    
    #for reset_password
    reset_pass = models.CharField(default="",max_length=32)
    
    #Facebook ID
    facebook_id = models.CharField(default="",max_length=200)
    
    def __unicode__(self):
        return self.user.username

class Rating(models.Model):
    
    #Change primary key to combination of everything to prevent duplicates.
    
    rated = models.ForeignKey(Rider, related_name = 'rated')
    rater = models.ForeignKey(Rider, related_name = 'rater')
    
    def __unicode__(self):
		return self.rater.user.username + '->' + self.rated.user.username

    
class Post(models.Model):
    
    owner = models.ForeignKey(Rider, null=False, related_name='owner')
    
    car_number = models.CharField(max_length=20)
    total_seats = models.IntegerField(default=1)
    phone = models.IntegerField(max_length=10)
    fro = models.CharField(max_length=200)
    to = models.CharField(max_length=200)
    date_time = models.DateTimeField('date_time',default=timezone.now())
    
    #status of post
    #0 - scheduled
    #1 - ongoing -> yet to be implemented
    #2 - cancelled
    status = models.IntegerField(default=0)
    changed = models.IntegerField(default=0)
    #0 - No
    #1 - Yes
    ac = models.IntegerField(default=0)
    autoaccept = models.IntegerField(default=0)
    
    #pass1 = models.ForeignKey(Rider, related_name='pass1', default=Rider.objects.get(pk=1))
    #pass2 = models.ForeignKey(Rider, related_name='pass2', default=Rider.objects.get(pk=1))
    #pass3 = models.ForeignKey(Rider, related_name='pass3', default=Rider.objects.get(pk=1))
    #pass4 = models.ForeignKey(Rider, related_name='pass4', default=Rider.objects.get(pk=1))
    #pass5 = models.ForeignKey(Rider, related_name='pass5', default=Rider.objects.get(pk=1))
    #pass6 = models.ForeignKey(Rider, related_name='pass6', default=Rider.objects.get(pk=1))
    
    
    #0 - Both
    #1 - Women only
    #2 - Men only
    men_women = models.IntegerField(default=0)
    
    
    #0 - available to all
    #1 - available to only friends
    available_to = models.IntegerField(default=0)
    
    cost = models.IntegerField(default=0)
    
    #0 - Doesn't want notifications
    #1 - Wants Notifications
    sms_noti = models.IntegerField(default=1)
    
    def __unicode__(self):
        return self.owner.user.username
    

class Reserved(models.Model):
    
    #Change primary key to combination of everything to prevent duplicates.
    
    post = models.ForeignKey(Post)
    reserver = models.ForeignKey(Rider)
    #0 - pending
    #1 - accepted
    status = models.IntegerField(default=0)
    
    
    #If post has been edited after reservation
    #0 - reserver is fine with edit
    #1 - reserver has not acknowledged edit
    edited = models.IntegerField(default=0)
    
class Message(models.Model):
    
    #Change primary key to combination of everything to prevent duplicates.
    
    sender = models.ForeignKey(Rider, related_name = 'sender')
    receiver = models.ForeignKey(Rider, related_name = 'receiver')
    message = models.CharField(max_length=200)
    date_time = models.DateTimeField('date_time',default = timezone.now())
    
    
    #The next two variables denote whether the message is present in the sender's and receiver's mailboxes or not.
    #2 -> read: Not implemented yet
    #1 -> present
    #0 -> The user has deleted.
    #As soon as both become 0, the message will be deleted from the database.
    smailbox = models.IntegerField(default=1)
    rmailbox = models.IntegerField(default=1)
    
    
#Here there also exists another table called 'User', provided by Django. It has username, email and password attributes.

#Temp check form
class UploadFileForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    #image = forms.FileField()