__author__ = 'Mike'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ispp8.settings")
from plan.models import *
import random
import math


def show():
    print('Numero de actividades:')
    print(len(Activity.objects.all()))
    print('Numero de usuarios:')
    print(len(OurUser.objects.all()))
    print('Numero de planes:')
    print(len(Plan.objects.all()))
    print('Numero de Gustos:')
    print(len(Taste.objects.all()))
    print('Sectores:')
    for sector in Sector.objects.all():
        print(sector.name)


def repeated(plan):
    rep = False
    for i in range(len(plan)-1):
        for j in range(i+1, len(plan)):
            if plan[i] == plan[j]:
                rep = True
                break
    return rep

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
    #chequear el orden por momentos
    check_momentos = True
    morning = Moment.objects.get(name__icontains='morning')
    evening = Moment.objects.get(name__icontains='evening')
    for i in range(1, len(plan)-1):
        moment_actual = plan[i].moment.all()
        moment_anteror = plan[i-1].moment.all()
        if morning in moment_actual and morning not in moment_anteror:
            check_momentos = False
        if evening in moment_actual and evening not in moment_anteror and morning not in moment_anteror:
            check_momentos = False
    #chequear que no sean todas actividades del mismo sector
    check_same_sectors = False
    sector = plan[0].sector
    for i in range(1, len(plan)-1):
        nsector = plan[i].sector
        if sector != nsector:
            check_same_sectors = True
            break

    #chequear que las actividades del sector hosteleria son de momentos diferentes
    check_eat = True
    eat_time = []
    for act in plan:
        if act.sector.name == 'Restaurante' or act.sector.name == 'Cafeteria':
            if act.moment not in eat_time:
                eat_time.append(act.moment)
            else:
                check_eat = False
                break
    #chequear que no hay actividades de comer pegadas
    check_pegadas = True
    for i in range(len(plan)-1):
        if plan[i].sector.name == 'Restaurante' or plan[i].sector.name == 'Cafeteria':
            if plan[i+1].sector.name == 'Restaurante' or plan[i+1].sector.name == 'Cafeteria':
                check_pegadas = False

    #que no sea comer y hacer deporte
    check_sport = True
    for i in range(0, len(plan)-2):
        if (plan[i].sector.name == 'Restaurante' or plan[i].sector.name == 'Cafeteria') and plan[i+1].sector.name == 'Deporte':
            check_sport = False
    return (check_momentos*5 + check_sport + check_eat + check_pegadas + check_same_sectors*2)/10


def get_perfect_plans(population):
    sol = []
    for elem in population:
        if elem['posibility'] == 10:
            sol.append(elem['plan'])
    return sol


def selection(population):
    working_population = list(population)
    result = []
    while len(result) < 50:
        elem = working_population[random.randint(0, len(working_population)-1)]
        if random.random() >= elem['posibility']:
            result.append(elem['plan'])
            working_population.remove(elem)
    return result


def recombination(to_recombine):
    res = []
    for plan_index in range(0, len(to_recombine)-1, 2):
        #sacamos dos planes contiguos
        plan_uno = to_recombine[plan_index]
        plan_dos = to_recombine[plan_index + 1]
        #repetimos el intercambio el numero medio entero por abajo
        for activity_index in range(math.floor(len(plan_uno))):
            #sacamos las actividades aleatoriamente de cada plan y la sustituimos en cada otro
            index_uno = random.randint(0, len(plan_uno)-1)
            index_dos = random.randint(0, len(plan_dos)-1)
            act_uno = plan_uno[index_uno]
            act_dos = plan_dos[index_dos]
            #intercambiamos
            plan_uno[index_uno] = act_dos
            plan_dos[index_dos] = act_uno
        #damos formato correcto a los planes para juntarlos con el resto de la ploblacion
        if repeated(plan_uno) or repeated(plan_dos):
            ev = evaluate_plan(to_recombine[plan_index])
            res.append({'posibility': ev, 'plan': to_recombine[plan_index]})
            ev = evaluate_plan(to_recombine[plan_index])
            res.append({'posibility': ev, 'plan': to_recombine[plan_index]})
        else:
            ev = evaluate_plan(plan_uno)
            res.append({'posibility': ev, 'plan': plan_uno})
            ev = evaluate_plan(plan_dos)
            res.append({'posibility': ev, 'plan': plan_dos})
    return res


def mutate(elem, activities_list):
    plan = elem['plan']
    #sustituimos una actividad aleatoria del plan con una aleatoria de la lista de actividades
    while True:
        new_activity = activities_list[random.randint(0, len(activities_list)-1)]['activity']
        if new_activity not in plan:
            plan[random.randint(0, len(plan)-1)] = new_activity
            ev = evaluate_plan(plan)
            elem['posibility'] = ev
            break


def best_selection(to_work, population):
    new_population = []
    for elem in to_work:
        if elem['posibility'] >= 0.5:
            new_population.append(elem)
    for elem in population:
        if elem['posibility'] >= 0.5:
            new_population.append(elem)
    return new_population


def acsNotRep(plan_list, plan):
    check = True
    for ac in plan:
        for elem in plan_list:
            if ac in elem:
                check = False
                break
    return check


def algorithm(user, location, planSize, iterations):
    #Inicialization
    print('Starting algorithm')
    wl = create_working_list(user, location)
    population = []
    final = []
    while len(population) < 100:
        plan = create_plan(wl, planSize)
        #evaluacion
        ev = evaluate_plan(plan)
        population.append({'posibility': ev, 'plan': plan})
    print('Calculating')
    generation = 0
    while generation < iterations:
        #seleccion de los elementos de la poblacion a recombinar
        to_work = selection(population)
        #recombinacion de los elementos seleccionados
        to_work = recombination(to_work)
        #posible mutacion de cada elemento
        for elem in to_work:
            if random.random() <= 0.1:
                mutate(elem, wl)
        #reemplazo
        population = best_selection(to_work, population)
        generation += 1
    #fin del algoritmo genetico, como solo nos interesan los mejores resultados filtramos
    print('Filtering data')
    for elem in population:
        if elem['posibility'] == 1:
            if not repeated(elem['plan']):
                if acsNotRep(final, elem['plan']):
                    final.append(elem['plan'])
    return final