from django.http import HttpResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import logging

# Create your views here.
@login_required(redirect_field_name='/login')
def start(request):
	
	ret = {}
	ret['username'] = request.user.username
	return render_to_response('profile.html', ret)

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

def addServices(request):
	
	ret = {}
	ret['username'] = request.user.username
	return render_to_response('login.html', ret)

def verifyRegisterParams(emailAddress, username, password, confirmpassword):
	#passwords are the same

	#emailAdd looks like an email addy
	return True
