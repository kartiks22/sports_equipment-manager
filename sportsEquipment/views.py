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
#from django.core.urlresolvers import reverse_lazy

# Create your views here.
#method to render home page after login
@login_required
def home(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	if request.user.is_staff:
		return redirect(reverse('sportsEquipment:pendingRequest'))
	else:
		return redirect(reverse('sportsEquipment:viewRequest'))

#method to perform an insert or update

def insertOrUpdate(model):
	model.save()
	# try:
	#     with transaction.atomic():
	#         model.save()
	# except IntegrityError:
	#     handle_exception()

#method to make requests for equipments by students

#method to make requests for equipments by students

@login_required
def checkAvailability(request):
	# print(request.POST)
	reqId = request.POST['reqId']
	# print(reqId)
	penReq = EquipmentRequest.objects.get(reqId=reqId)
	availability = penReq.eqp.eqpQuantity- penReq.eqp.eqpQuantityTaken
	# print('availability',availability)
	# data = {
	#     'availability' : availability,
	#     'id' : reqId
	# }
	return HttpResponse(availability)
	# equipments = Equipments.objects.get(eqpName=penReq.eqp)
	# print(equipments)

@login_required
def eqpRequest(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	if(request.method == "POST"):
		if(request.user.is_authenticated):
			form = EqpmntRequestForm(request.POST)
			# print(form)
			# print(request.POST)
			myDict = dict(request.POST.items())
			# print(myDict)
			if form.is_valid():
				user = request.user
				equipmentRequest = EquipmentRequest()
				currentDateTime = datetime.today()
				# print(currentDateTime)
				requestedQuantity = request.POST['EqpQuantity']


				equipmentRequest.quantity       = requestedQuantity
				equipmentRequest.eqp            = Equipments.objects.get(pk=int(request.POST['EqpName'],10))
				equipmentRequest.user           = user
				equipmentRequest.dtOfRequest    = currentDateTime
				# print("date of Req")
				# print(currentDateTime)
				# equipmentRequest.dtAvailed      = datetime.today()
				# equipmentRequest.dtOfExpRet     = currentDateTime + timedelta(days=1)
				insertOrUpdate(equipmentRequest)

				return redirect(reverse('sportsEquipment:viewRequest'))
			else:
				return HttpResponse("Equipment not available")



	else:
		# lstEqpmnt = Equipments.objects.all().order_by('eqpName')
		form = EqpmntRequestForm()
		# print(form.lstEqpmnt)
		# form.EqpName = choices = [(x.eqpId, x.eqpName) for x in lstEqpmnt]
		return render(request, 'EndUser/eqpRequest.html', {'form' : form,'userProfile': userProfile});
	# return home(request);

#method to add equiment by admin
@login_required
def addEquip(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	if(request.method=="POST"):
		form = addEqpForm(request.POST)
		if form.is_valid():
			form.save()
		return viewInventory(request)
	else:
		if(request.user.is_staff==False):
			return redirect('/sportsEquipment/')
		form = addEqpForm()
		context ={
			'form' : form,
			'userProfile': userProfile
		}
		return render(request, "AdminUser/addEquip.html",context)


#method to check penalty of users
@login_required
def penalty(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	context = list(UserProfileInfo.objects.order_by('totalPenalty'))
	# print(context)
	# print("No of requests: ", len(context))
	return render(request, 'AdminUser/viewPenalty.html', {'context': context,'userProfile': userProfile});
	#return render(request, "AdminUser/viewPenalty.html")
	# print("Check penalty is working!!")
	# return viewInventory(request)
	# if(request.method=="POST"):
	#     form = penaltyForm(request.POST)
	#     if form.is_valid():
	#         form.save()
	#         #viewPenalty(request)
	#         userProfile = UserProfileInfo.objects.get(user=request.user)
	#         totalPenalty = userProfile.totalPenalty
	        # print(totalPenalty)
	        # print("form is valid!!")
	#         return render(request, "AdminUser/viewPenalty.html")
	#     else:
	        # print("form invalid!")
	#         return render(request, "AdminUser/viewPenalty.html")
	# else:
	#     form = penaltyForm()
	#     context ={
	#         'form' : form
	#     }
	#     #SSviewPenalty(request)
	    # print("Method is not post!!!")
	#     return render(request, "AdminUser/checkPenalty.html",context)


#method to edit equipment list by Admin
@login_required
def editEquipList(request,pk):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	item = get_object_or_404(Equipments,eqpId = pk)

	if request.method == "POST":
		form = editForm(request.POST, instance=item)
		if form.is_valid():
			form.save()
			# return render(request,'AdminUser/editEquipList.html',{'form':form})
			return viewInventory(request)

	else:
		form = editForm(instance = item)
		return render(request,'AdminUser/editEquipList.html',{'form':form,'userProfile': userProfile})




#method to delete a equip
#@login_required
def deleteEqp(request,pk):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	Equipments.objects.filter(eqpId=pk).delete()
	items = Equipments.objects.all()
	# print (items)
	context = {
		'items' : items,
		'userProfile': userProfile
	}
	return render(request,'AdminUser/deleteEquip.html',context)

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

#method to view request status for equipments by students
@login_required
def viewRequest(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	user = request.user
	# print(user)
	lstRequest = list(EquipmentRequest.objects.filter(user=user).order_by('-dtOfRequest'))
	# print(lstRequest)
	lstRequest = utcToIst(lstRequest)

		# request.dtOfRequest = request.dtOfRequest.astimezone(timezone('Asia/Kolkata'))
	# print("No of requests: ", len(lstRequest))
	return render(request, 'EndUser/viewRequest.html', {'lstRequest': lstRequest,'userProfile': userProfile});



#method to view inventory
@login_required
def viewInventory(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	context = list(Equipments.objects.order_by('-eqpId'))
	for req in context:
		req.eqpQuantityTaken = req.eqpQuantity - req.eqpQuantityTaken
	# print(context)
	# print("No of requests: ", len(context))
	if request.user.is_staff:
		return render(request, 'AdminUser/viewEquipList.html', {'context': context,'userProfile': userProfile});
	else:
		return render(request, 'EndUser/viewEquipList.html', {'context': context,'userProfile': userProfile});


#method to view all pending requests to be processed by the sports room admin
@login_required
def pendingRequest(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	lstPendingRequest = list(EquipmentRequest.objects.filter(reqStatus = 0).order_by('user','-dtOfRequest'))
	lstPendingRequest = utcToIst(lstPendingRequest)
	# print("No of pending requests: ",len(lstPendingRequest))
	return render(request, 'AdminUser/pendingRequest.html', {'lstPendingRequest' : lstPendingRequest,'userProfile': userProfile});

#method to view all processed requests to be by the sports room admin
@login_required
def approvedRequest(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	lstProcessedRequest = list(EquipmentRequest.objects.filter(reqStatus__in = [1,2,3]).order_by('-dtOfRequest'))
	lstProcessedRequest = utcToIst(lstProcessedRequest)
	# print("No of processed requests: ", len(lstProcessedRequest))
	return render(request, 'AdminUser/processedRequest.html', {'lstProcessedRequest': lstProcessedRequest,'userProfile': userProfile});

#method to process a pending requests by the sports room admin
@login_required
def processRequest(request):
	isAcceptRequest = request.GET.get('isAcceptRequest')
	# print(isAcceptRequest)
	reqId = request.GET.get('reqId')
	# print(reqId)
	penReq = EquipmentRequest.objects.get(reqId=reqId)
	# print(penReq.eqp)
	currentTime = datetime.today()
	if(int(isAcceptRequest) == 1):
		eqp = penReq.eqp
		requestedQuantity = penReq.quantity
		# print(requestedQuantity)
		# print(eqp.eqpQuantity - eqp.eqpQuantityTaken)
		if(requestedQuantity <= (eqp.eqpQuantity - eqp.eqpQuantityTaken)) :
			penReq.reqStatus    = 1
			penReq.dtAvailed    = currentTime
			penReq.dtOfExpRet   = currentTime + timedelta(days=1)
			# print("date of process")
			# print(currentTime)
			# print("date of dtOfExpRet")
			# print(currentTime + timedelta(days=1))
			eqp.eqpQuantityTaken += requestedQuantity
			insertOrUpdate(eqp)
		else :
			return HttpResponse("Equipment not available")
	else:
		penReq.reqStatus    = 2
		penReq.dtAvailed    = currentTime
		penReq.dtOfExpRet   = currentTime
		penReq.dtOfActualRet= None

	insertOrUpdate(penReq)
	return pendingRequest(request)

#method to process return request by the sports room admin
@login_required
def processReturnRequest(request):
	reqId = request.GET.get('reqId')
	# print(reqId)
	returnRequest = EquipmentRequest.objects.get(reqId=reqId)
	# print(returnRequest)
	currentTime = datetime.today()
	eqp = returnRequest.eqp
	eqp.eqpQuantityTaken -= returnRequest.quantity
	returnRequest.reqStatus    = 3
	returnRequest.dtOfActualRet= currentTime
	returnRequest.penalty      = 0
	insertOrUpdate(returnRequest)
	insertOrUpdate(eqp)
	# insertOrUpdate(UserProfileInfo)
	return approvedRequest(request)

#method to add ground
@login_required
def addGround(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	if(request.method=="POST"):
		form = addGroundForm(request.POST)
		if form.is_valid():
			form.save()
		return redirect('/sportsEquipment/viewGrounds')
	else:
		if(request.user.is_staff==False):
			return redirect('/sportsEquipment/')
		form = addGroundForm()
		context ={
			'form' : form,
			'userProfile': userProfile
		}
		return render(request, "AdminUser/addGround.html",context)

def check_time(sh,sm,eh,em):
	if(eh<sh):
		eh+=24
	dh = eh-sh
	if(em<sm):
		dh-=1
		dm = 60-abs(em-sm)
	else:
		dm = em-sm
	dm += (dh*60)
	if(dm>120):
		return False
	return True

def check_ground_availability(s_tm,e_tm,booked):
	for i in booked:
		if(int(i[1])<=s_tm):
			continue
		elif(int(i[0])>=e_tm):
			continue
		else:
			return False
	return True



def groundRequests(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	if(request.method=="POST"):
		form = ground_form(request.POST)
		groundtype = request.POST["groundtype"]
		# print("dafafasasasfassafasasffsasf",groundtype)
		current_ground = Ground.objects.get(gId=groundtype)
		booked = [ x.split(',') for x in current_ground.booked.split(';') if x!='']

		sh = int(request.POST["start_hour"])
		sm = int(request.POST["start_min"])
		# print("daadffasafs",booked)
		#s_tm = 1700
		eh = int(request.POST["end_hour"])
		em = int(request.POST["end_min"])
		# print("end",end_tm)
		if(check_time(sh,sm,eh,em)==False):
			return render(request, 'EndUser/g_request.html', {'form': form,'userProfile': userProfile,'error':"Cannot book the ground or court for more than 2 hrs"})
			#return HttpResponse("Cannot book the ground or court for more than 2 hrs")

		if(check_ground_availability(sh*100 +sm,eh*100 +em,booked)):
			#booked.append((sh*100 + sm,eh*100 +em))
			current_ground.booked += str(sh*100 + sm) + "," + str(eh*100 + em) +";"
			current_ground.who_booked += str(request.user.username)+";"
			current_ground.save()
			return redirect('/sportsEquipment/viewGrounds')
		else:
			return render(request, 'EndUser/g_request.html', {'form': form,'userProfile': userProfile,'error':"Ground not available"})
			#return HttpResponse("Ground not available")

	else:
		form = ground_form()
		return render(request, 'EndUser/g_request.html', {'form': form,'userProfile': userProfile})


def viewGrounds(request):
	userProfile = UserProfileInfo.objects.get(user=request.user)
	if(request.user.is_authenticated==False):
		return redirect('/login/user_login/?next=/sportsEquipment/viewGrounds/')
	groundList_final = []

	curr_date_time = datetime.now(timezone('Asia/Kolkata'))
	for ground in Ground.objects.all():
		all_grounds_list = []
		a = ground.who_booked.split(';')
		b = ground.booked.split(';')
		curr_ground_owners = "None"
		for i in range(len(a)):
			temp_times = b[i].split(',')
			if(a[i]!=""):
				start_time_hour = int(temp_times[0])//100
				start_time_min = int(temp_times[0])%100
				end_time_hour = int(temp_times[1])//100
				end_time_min = int(temp_times[1])%100
				start_time_str = str(start_time_hour - 12)+":"+ str(start_time_min).zfill(2)+" PM" if start_time_hour>12 else str(start_time_hour)+":"+str(start_time_min).zfill(2)+" AM"
				end_time_str = str(end_time_hour - 12)+":"+ str(end_time_min).zfill(2)+" PM" if end_time_hour>12 else str(end_time_hour)+":"+ str(end_time_min).zfill(2)+" AM"
				all_grounds_list.append((a[i],(start_time_str,end_time_str)))
				if(int(temp_times[0])<= curr_date_time.hour*100+curr_date_time.minute <=int(temp_times[1]) ):
					curr_ground_owners=str(a[i])

		groundList_final.append((str(ground.gname),curr_ground_owners,all_grounds_list))
	#groundList_final = [ (all_ground_names[i],all_grounds_list[i]) for i in range(len(all_grounds_list))]

	return render(request,'EndUser/viewGrounds.html',{'groundList':groundList_final, 'userProfile': userProfile})
