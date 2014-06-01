__author__ = 'Mike'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ispp8.settings")
from plan.models import *
import random


def show():
    print('Numero de actividades:')
    print(len(Activity.objects.all()))
    print('Numero de usuarios:')
    print(len(OurUser.objects.all()))
    print('Numero de planes:')
    print(len(Plan.objects.all()))
    print('Numero de Gustos:')
    print(len(Taste.objects.all()))


def Algorithm(user, location, planSize):
    #Inicialization
    wl = create_working_list(user, location)
    plan = create_plan(wl, planSize)
    #evaluacion
    #while(no terminamos)
        #seleccion
        #reconbinacion
        #cruzamiento
        #reemplazo
    for e in plan:
        print(e.name)


def create_working_list(user, location):
    #obtencion de las preferencias del usuario si existe
    activityList = []
    for activity in Activity.objects.filter(location__icontains=location):
        activityList.append(activity)
    if user:
        tastes = user.tastes
        sector_preferences = [{'valoration': 0, 'sectors': []}, {'valoration': 1, 'sectors': []}, {'valoration': 2, 'sectors': []}, {'valoration': 3, 'sectors': []}]
        min_valoration = 0
        for taste in tastes.all():
            if taste.attribute_name == 'sector':
                sector = Sector.objects.get(name=taste.attribute_value)
                valoration = taste.degree
                for item in sector_preferences:
                    if item['valoration'] == valoration:
                        item['sectors'].append(sector)
            if taste.attribute_name == 'valoration':
                min_valoration = int(taste.attribute_value)
    #Preparamos las actividades para que tengan una probabilidad de seleccion segun los gustos del usuario
    #La probabilidades de valoration*(1/4)
    working_list = []
    for act in activityList:
        sector = act.sector
        saved = False
        if user:
            for elem in sector_preferences:
                if sector in elem['sectors'] and act.valoration >= min_valoration:
                    working_list.append({'activity': act, 'probability': elem['valoration']*(1/4)})
                    saved = True
        if not saved:
            if user:
                if act.valoration >= min_valoration:
                    working_list.append({'activity': act, 'probability': 0.5})
            else:
                working_list.append({'activity': act, 'probability': 0.5})
    return working_list


def create_plan(activities_list, planSize):
    #Teniedo la lista de trabajo, pasamos a realizar el plan de forma aleatoria
    working_list = list(activities_list)
    result = []
    while len(result) < planSize:
        elem = working_list[random.randint(0, len(working_list)-1)]
        if random.random() >= elem['probability']:
            result.append(elem['activity'])
            working_list.remove(elem)
    return result


def evaluate_plan(plan):
    return True


#Ejecucion del algoritmo
user = OurUser.objects.get(pk=1)
#user = None
Algorithm(user, 'barcelona', 9)
show()