from django.db import models
from django.contrib.auth.models import User

#coding-utf-8
# Create your models here.


class Activity(models.Model):
    MOMENTS = (("m", "morning"), ("e", "evening"), ("n", "night"),)
    PRICE = (("f", "free"), ("n", "nonfree"),)
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=40)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    photo = models.URLField()
    sector = models.CharField(max_length=200)
    moment = models.CharField(max_length=3, choices=MOMENTS)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    valoration = models.FloatField()
    isFree = models.CharField(max_length=3, choices=PRICE, default='f')
    isPromoted = models.BooleanField()
    objects = models.Manager()
    description = models.CharField(max_length=200)
    url = models.URLField()

    def __unicode__(self):
        return self.name


#Changed name of user from our model to difference it from django implementation
class OurUser(models.Model):
    djangoUser = models.OneToOneField(User)
    birthday = models.DateField()
    SEX = (("m", "Male"), ("f", "Female"),)
    image = models.ImageField(upload_to='images/profile/', blank=True)
    gender = models.CharField(max_length=1, choices=SEX)
    friends = models.ManyToManyField("self", blank=True, null=False)

    def __unicode__(self):
        return self.djangoUser.get_username()


class Plan(models.Model):
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    voted = models.BooleanField()
    activities = models.ManyToManyField(Activity)
    user = models.ForeignKey(OurUser, related_name='OurUser_content_type')
    sharedTo = models.ManyToManyField(OurUser, blank=True, null=False)
    done = models.BooleanField()

    def __unicode__(self):
        return "plan" + str(self.pk)


class Company(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField('password', max_length=128)
    birthday = models.DateTimeField()
    contactName = models.CharField(max_length=20)
    contactNumber = models.CharField(max_length=20)
    companyName = models.CharField(max_length=20)
    cif = models.CharField(max_length=20)

    def __unicode__(self):
        return self.companyName


class Payment(models.Model):
    RENEW = (("y", "Renewable"), ("n", "Non renewable"),)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    selfRenewing = models.BooleanField(max_length=1, choices=RENEW)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    activity = models.ForeignKey(Activity)
    company = models.ForeignKey(Company)

    def __unicode__(self):
        return self.amount


class Taste(models.Model):
    attribute_name = models.CharField(max_length=20)
    attribute_value = models.CharField(max_length=200)
    degree = models.FloatField()
    user = models.ForeignKey(OurUser)