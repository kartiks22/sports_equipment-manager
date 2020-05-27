from celery.schedules import crontab
from celery.task import periodic_task
from django.shortcuts import render, redirect
from login.forms import UserForm,UserProfileInfoForm
from login.models import UserProfileInfo
from datetime import *
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from pytz import timezone
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from .forms import *
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from .serializers import *
from django.core.mail import EmailMessage

#celery -A sportsroom worker -l info
#celery -A sportsroom beat -l info
def insertOrUpdate(model):
	model.save()

def utcToIst(lstRequest):
	for request in lstRequest:
		if request.dtOfRequest is not None:
			request.dtOfRequest = request.dtOfRequest.astimezone(timezone('Asia/Kolkata'))
		if request.dtOfExpRet is not None:
			request.dtOfExpRet = request.dtOfExpRet.astimezone(timezone('Asia/Kolkata'))
		if request.dtOfActualRet is not None:
			request.dtOfActualRet = request.dtOfActualRet.astimezone(timezone('Asia/Kolkata'))
		if request.dtAvailed is not None:
			request.dtAvailed = request.dtAvailed.astimezone(timezone('Asia/Kolkata'))

	return lstRequest

@periodic_task(run_every=(crontab(minute="*/1")), name="some_task", ignore_result=True)
def some_task():
	print("Updating Penalty")
	
	#processing penalty
	lstProcessedRequest = list(EquipmentRequest.objects.filter(reqStatus__in = [1]).order_by('-dtOfRequest'))
	lstProcessedRequest = utcToIst(lstProcessedRequest)
	for i in lstProcessedRequest:
		print(i.user)
		usr = i.user
		#print("fafafafasafsafs      ",usr)
		userProfile = UserProfileInfo.objects.get(user= usr)
		#sprint(userProfile.totalPenalty)
		dailyPenalty = settings.DAILY_PENALTY
		currentTime = datetime.today()
		delta = currentTime.date() - i.dtAvailed.date()
		#print("date of actual return")
		#print(currentTime)
		#print(delta.days)
		penaltyAmount = 0
		if (delta.days > 0):
			penaltyAmount = dailyPenalty * delta.days
		userProfile.totalPenalty += penaltyAmount
		print(usr.email)
		if(userProfile.totalPenalty>0):
			mail = EmailMessage('Sports Room Penalty', 'This is to notify that your penalty now is:'+
				str(userProfile.totalPenalty),to=[usr.email])
			mail.send()
		insertOrUpdate(userProfile)

	#deleting all ground records
	currentTime = datetime.today().astimezone(timezone('Asia/Kolkata'))
	if(currentTime.hour==5 and currentTime.minute>=0 and currentTime.minute<=10):
		all_grounds = list(Ground.objects.order_by('gId'))
		for i in all_grounds:
			i.booked = ";"
			i.who_booked = ";"
			insertOrUpdate(i)

