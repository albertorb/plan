__author__ = 'developer'
#encoding:utf-8
from django.forms import ModelForm
from django import forms
from plan.models import *
from django.contrib.auth.models import User


class CompanyRegistrationFrom(ModelForm):
    class Meta:
        model = Company


class userDjangoForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class OurUserRegistrationForm(ModelForm):
    class Meta:
        model = OurUser
        fields = ('birthday', 'gender', 'image')

class PlanForm(ModelForm):
    class Meta:
        model=Plan