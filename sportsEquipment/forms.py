from django import forms
from .models import *
from login.models import UserProfileInfo

def call_choices_eqp():
	return [(x.eqpId, x.eqpName) for x in Equipments.objects.all().order_by('eqpName')]

def call_choices_ground():
	return [(x.gId, x.gname) for x in Ground.objects.all().order_by('gname')]

class EqpmntRequestForm(forms.Form):
	#lstEqpmnt = Equipments.objects.all().order_by('eqpName')
	#print(lstEqpmnt)
	EqpName = forms.ChoiceField(choices=call_choices_eqp)
	EqpQuantity = forms.IntegerField(min_value=1, max_value=2)
	# class Meta:
	#     model = Equipments
	#     fields = {'eqpName','eqpQuantity'}

class addEqpForm(forms.ModelForm):
	class Meta:
		model = Equipments
		fields = [
				'eqpName'   ,
				'eqpQuantity'
		]
	#EqpName = forms.CharField(label='eqp name', max_length=100)
	#EqpQuantity = forms.IntegerField(min_value=1)



class editForm(forms.ModelForm):
	class Meta:
		model = Equipments
		fields = [
			'eqpName',
			'eqpQuantity'
		]

class addGroundForm(forms.ModelForm):
	class Meta:
		model = Ground
		fields = [
				'gname',
		]

class ground_form(forms.Form):
	#lstGround = Ground.objects.all().order_by('gname')
	groundtype = forms.ChoiceField(choices = call_choices_ground)
	start_hour   = forms.IntegerField(min_value=0, max_value=23)
	start_min   = forms.IntegerField(min_value=0, max_value=59)
	end_hour   = forms.IntegerField(min_value=0, max_value=23)
	end_min   = forms.IntegerField(min_value=0, max_value=59)
