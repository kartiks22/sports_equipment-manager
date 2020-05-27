from django.test import TestCase
from login.forms import UserForm

class TestForms(TestCase):

	def test_UserForm(self):
		form = UserForm(data={
			'username': 'xyz',
			'email': 'xyz@iiitb.org',
			'password':'xyz'
			})

		self.assertTrue(form.is_valid())

	# def test_UserForm(self):
	# 	form = UserForm(data={
	# 		'username': 'xyz',
	# 		'email': '',
	# 		'password':'xyz'
	# 		})

	# 	self.assertFalse(form.is_valid())
	# 	self.assertEquals(len(form.errors),2)