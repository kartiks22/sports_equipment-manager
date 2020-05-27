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
import time

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

@periodic_task(run_every=(crontab(minute="*/15")), name="some_task", ignore_result=True)
def some_task():
	#print("Updating Penalty")

	#processing penalty
	lstProcessedRequest = list(EquipmentRequest.objects.filter(reqStatus__in = [1]).order_by('-dtOfRequest'))
	lstProcessedRequest = utcToIst(lstProcessedRequest)
	cnt=0
	for i in lstProcessedRequest:
		print(cnt)
		cnt+=1
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
		#print(usr.email)
		if(userProfile.totalPenalty>0):
			mail = EmailMessage('Sports Room Penalty', 'This is to notify that your penalty now has reached:'+
				str(userProfile.totalPenalty),to=[usr.email])
			mail.send()
		insertOrUpdate(userProfile)
	print("saaas")
	# time.sleep(30)
	print("gggggg")
	#clearing ground
	currentTime = datetime.today().astimezone(timezone('Asia/Kolkata'))
	#print(currentTime)
	if(currentTime.hour==5 and currentTime.minute>=0 and currentTime.minute<=10):
		all_grounds = list(Ground.objects.order_by('gId'))
		for i in all_grounds:
			i.booked = ";"
			i.who_booked = ";"
			insertOrUpdate(i)

	#clearing not verified users
	#print("dafsdaf")
	unverified = list(UserProfileInfo.objects.filter(is_verified = 0))
	for i in unverified:
		print(i.user.username)
		i.user.delete()
	UserProfileInfo.objects.filter(is_verified = 0).delete()
	# UserProfile = UserProfileInfo.objects.get(user=request.user)
	# Equipments.objects.filter(eqpId=pk).delete()
	# items = Equipments.objects.all()
	# bin/logstash -f logstash-simple.conf


	#sending email to admin every month notifying penalty of all users
	context = list(UserProfileInfo.objects.order_by('totalPenalty'))
	lst = ""
	for i in context:
		t = i.user.username + "	  " + str(i.totalPenalty) + "\n"
		lst+= t
	mail2 = EmailMessage('User Penalty List', lst ,to=["kartik.gupta@iiitb.org"])
	mail2.send()

	# time.sleep(60)
	print("jjjjjj")
	#sending email to admin every month notifying current sports inventory
	context = list(Equipments.objects.order_by('-eqpId'))
	lst = ""
	for i in context:
		t = i.eqpName + "	  " + str(i.eqpQuantity) + "\n"
		lst+= t
	mail3 = EmailMessage('Current Sports Inventory', lst ,to=["kartik.gupta@iiitb.org"])
	mail3.send()
