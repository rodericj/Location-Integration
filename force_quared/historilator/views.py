from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import random
import urllib
import time
import logging

# Create your views here.
@login_required(redirect_field_name='/login')
def start(request):
	
	ret = {}
	ret['username'] = request.user.username
	return render_to_response('profile.html', ret)

def authorizeSource(request):

	#username, password, type
	#foursquare auth info
	oauth_consumer_key = '0bf482ea6ad98dc8fa2e668575c0eaba04a5ce475'
	oauth_token = 'ff6729db73f8668c32e1419909e64c25'

	data = {}
	data['oauth_token'] = oauth_token
	data['oauth_consumer_key'] = oauth_consumer_key
	foursquare = 'http://api.playfoursquare.com/v1/authexchange'
	return HttpResponsePermanentRedirect(foursquare)
	
	

def weblogin(request):
	emailAddress = request.POST['emailaddress']
	password = request.POST['password']
	user = authenticate(username=emailAddress, password=password)
	dest = 'login'
	if user is not None:
		if user.is_active:
			ret['loginret'] =  "You provided a correct username and password!"
			ret['rc'] = 0
			dest = 'profile'			
		else:
			ret['loginret'] = "Your account has been disabled!"
	else:
		ret['loginret'] = "Your username and password were incorrect2."
		ret['rc'] = 0
	
	return HttpResponseRedirect(dest, ret)

def register(request):
	emailAddress = request.POST['emailaddress']
	username = request.POST['username']
	password = request.POST['password']
	confirmpassword = request.POST['confirmpassword']
	user = authenticate(username=username, password=password)
	ret = {}

	dest = '/login'
	if user is not None:
		ret['registerret'] =  "An account with that username already exists"
	else:
		#time to set up a new user
		verifyRegisterParams(emailAddress, username, password, confirmpassword)
		user = User.objects.create_user(username, emailAddress, password)
		user.isActive = True
		user.save()
		ret['registerret'] = "Success, you are known as " + username
		#now to authenticate
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				ret['registerret'] =  "You provided a correct username and password!"
				login(request, user)
			else:
				ret['registerret'] = "Your account has been disabled!"
		else:
			ret['registerret'] = "Your username and password were incorrect1."
		

		dest = '/'
	
	return HttpResponseRedirect(dest+'?ret='+ret['registerret'])

def authorize(request):
	None

def addServices(request):
	
	ret = {}
	username = request.user.username
	nonce = int(random.random()*100000000)
	timestamp = int(time.time())
	key = '52e6db5e1d8bd8c481e8e1e3f798652004a7fbfc8'
	secret = '57c1aac04b076d8743664e2d935da13b'

	ret['username'] = username
	ret['nonce'] = nonce
	ret['timestamp'] = timestamp
	ret['key'] = key
	ret['secret'] = secret
	link = "http://api.playfoursquare.com/oauth/request_token?oauth_consumer_key="+key+"&oauth_signature="+secret+"&oauth_nonce="+str(nonce)+"&oauth_timestamp="+str(timestamp)+"&oauth_version=1.0"

	ret['link'] = link
	return render_to_response('login.html', ret)

def verifyRegisterParams(emailAddress, username, password, confirmpassword):
	#passwords are the same

	#emailAdd looks like an email addy
	return True
