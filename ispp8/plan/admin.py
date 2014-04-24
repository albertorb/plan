#encoding:utf-8
__author__ = 'albrinbor'
from django.contrib import admin
from plan.models import *

admin.site.register(Activity)
admin.site.register(Company)
admin.site.register(OurUser)
admin.site.register(Payment)
admin.site.register(Plan)
#admin.site.register(SharedPlan)