__author__ = 'Mike'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ispp8.settings")
from plan.models import *


def show():
    print('Numero de actividades:')
    print(len(Activity.objects.all()))
    print('Numero de usuarios:')
    print(len(OurUser.objects.all()))
    print('Numero de planes:')
    print(len(Plan.objects.all()))
    print('Numero de Gustos:')
    print(len(Taste.objects.all()))

