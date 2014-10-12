from django.db import models
from django.contrib.auth.models import User

#coding-utf-8
# Create your models here.

class activity_plan(models.Model):
    activity = models.ForeignKey(Activity)
    plan = models.ForeignKey(Plan)
    creation_date = models.DateField()

class Activity(models.Model):
    name = models.TextField()
    description = models.TextField()
    city = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    sector = models.TextField()
    picture = models.ImageField()

class Profile(models.Model):
    user = User
    picture = models.ImageField() #TODO imagefile location

class Plan(models.Model):
    name = models.TextField()
    owner = models.ForeignKey(Profile)


