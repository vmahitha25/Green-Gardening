from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.db import models
from django.db.models.fields import CharField
from .models import Appointments,UserAddressBook,ProductReview

class SignupForm(UserCreationForm):
    class Meta:
            model=User
            fields=('first_name','last_name','username','email','password1','password2')

    
class AddressBookForm(forms.ModelForm):
	class Meta:
		model=UserAddressBook
		fields=('address','mobile','status')

class ReviewAdd (forms.ModelForm):
	class Meta:
		model=ProductReview
		fields=('review_text','review_rating')


class ProfileForm(UserChangeForm):
	class Meta:
		model=User
		fields=('first_name','last_name','email','username')

class AppointmentForm(forms.ModelForm):
	class Meta:
		model=Appointments
		fields=('first_name','last_name','mobile','email')