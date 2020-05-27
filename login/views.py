from django.shortcuts import render, redirect
from login.forms import UserForm,UserProfileInfoForm
from login.models import UserProfileInfo
from django import forms
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
import random
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    if(request.user.is_authenticated):
        return redirect('/sportsEquipment/')
    return render(request,'Login/index.html')

@login_required
def special(request):
    return HttpResponse("You are logged in")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def validate(email):
    return email.split('@')[1] == "iiitb.org"


def otp(request):
    if request.method =='POST':
        otp_entered = request.POST.get('otp')
        otp_no = request.POST.get('otp_no')
        email = request.POST.get('email')
        user_profile = UserProfileInfo.objects.get(user=User.objects.get(email=email))
        print(type(otp_entered))
        print(type(otp_no))
        if(otp_no==otp_entered):
            user_profile.is_verified = 1
            user_profile.save()
            return render(request,'Login/login.html')
        else:
            error = "OTP doesn't match"
            #return HttpResponse(error)
            return render(request,'Login/login.html',{'error':error,})




def register(request):
    error = ""
    registered = False
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            if  validate(user_form.cleaned_data.get("email")):

                otp_no = random.randint(1000000, 9999999)
                mail = EmailMessage('Sports Room Authentication', 'Authentication key: '+str(otp_no),
                    to=[user_form.cleaned_data.get("email")])
                mail.send()

                user = user_form.save()
                user.username = user.username.upper()
                user.set_password(user.password)
                user.save()

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.otp_no = otp_no
                if 'profile_pic' in request.FILES:
                    profile.profile_pic = request.FILES['profile_pic']

                profile.save()

                registered = True
                return render(request,'Login/otp.html',{'otp_no':otp_no,
                    'email':user_form.cleaned_data.get("email")})
            else:
                error = "IIITB email required"
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request,'Login/register.html',{
            'user_form':user_form,
            'profile_form':profile_form,
            'registered':registered,
            'error' : error
    })


def user_login(request):
    if request.method =='POST':

        username = request.POST.get('username').upper()
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                # return HttpResponseRedirect(reverse('home'))
                userprofile = UserProfileInfo.objects.get(user=user)
                if(userprofile.is_verified==0):
                    return render(request,'Login/otp.html',{'otp_no':userprofile.otp_no,
                            'email':user.email})
                return redirect('/sportsEquipment/home')
            else:
                #return HttpResponse("ACCOUNT NOT ACTIVE")
                return render(request,'Login/login.html',{'error':"ACCOUNT NOT ACTIVE"})
        else:
            print("login Failed due to inactive account")
            return render(request,'Login/login.html',{'error':"Invalid login Details"})
        # print (userprofile.profile_pic)


    else:
        return render(request,'Login/login.html')
