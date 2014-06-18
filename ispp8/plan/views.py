from plan.models import *
from plan.forms import *
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404

import time
from datetime import datetime
from django.utils import formats
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.contrib.auth.hashers import make_password, pbkdf2
import random
from random import shuffle
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _
import algorithm
import operator


def search(request):
    # Es necesario ejecutar el siguiente codigo en la db para que esto funcione
    # CREATE FULLTEXT INDEX plan_activity_name ON plan_activity(name);
    search_query = request.POST['search']
    print(len(search_query))
    res = Activity.objects.filter(name__search=search_query)
    return render_to_response('search_result.html', {'res': res}, context_instance=RequestContext(request))


def getPlan(request, activity_id, activity_id2, activity_id3):
    plans = Plan.objects.all()
    act = get_object_or_404(Activity, id=activity_id)
    act2 = get_object_or_404(Activity, id=activity_id2)
    act3 = get_object_or_404(Activity, id=activity_id3)
    planform = PlanForm()
    plan = planform.save(commit=False)
    plan.voted = False
    plan.done = False
    plan.startDate = act.startDate
    plan.endDate = act3.endDate
    if request.user.is_authenticated():
        duser = request.user
        ouser = OurUser.objects.get(djangoUser=duser)
        for p in plans:
            if p.user_id == ouser.id:
                return HttpResponseRedirect('/repeatedplan')
            else:
                plan.user = request.user.ouruser
                plan.save()
                plan.activities = [act, act2, act3]
    elif not request.user.is_authenticated():
        return HttpResponseRedirect('/register')
    return render_to_response('plan.html', {'plan': plan}, context_instance=RequestContext(request))


def repeatedplan(request):
    return render_to_response('repetedplan.html', context_instance=RequestContext(request))


def welcome(request):
    loginw = False
    if request.method == 'POST' and "log" in request.POST:
        print("vamos alla")
        userName = request.POST['usernamelogin']
        hashPassword = request.POST['passwordlogin']
        print(hashPassword)
        UserAccount = authenticate(username=userName, password=hashPassword)
        if UserAccount is not None:
            if UserAccount.is_active:

                login(request, UserAccount)
                # Llevar a la vista principal
                return HttpResponseRedirect('/plan')
            else:
                # Cuenta no activada

                return HttpResponseRedirect("/error")
        else:
            # Login incorrecto
            loginw = True
            return render_to_response('signin.html',
                                      {'loginw': loginw},
                                      context_instance=RequestContext(request))

    return render_to_response('welcome.html', {}, context_instance=RequestContext(request))


def activity(request, activity_id):
    obj = get_object_or_404(Activity, id=activity_id)
    comments = Comment.objects.filter(activity=obj)
    if request.method == 'POST' and request.user.is_authenticated():
        texto = request.POST['comment']
        ourser = OurUser.objects.get(djangoUser=request.user)
        Comment.objects.create(text=texto, activity=obj, user=ourser)
        return HttpResponseRedirect("/activity/" + str(activity_id) + '/')
    else:
        # checking if some friend has done this activity
        res = []
        print(request.user.is_authenticated())
        if request.user.is_authenticated():
            ourser = OurUser.objects.get(djangoUser=request.user)
            friends = ourser.friends.all()

            for friend in friends:
                planesRealizados = Plan.objects.filter(user=friend)

                for plan in planesRealizados:
                    res.append(friend)
                    print(res)
            return render_to_response('actinfo.html',
                                      {'activity': obj, 'friendsDid': res, 'comments': comments, 'user': ourser},
                                      context_instance=RequestContext(request))
        return render_to_response('actinfo.html', {'activity': obj, 'friendsDid': res, 'comments': comments},
                                  context_instance=RequestContext(request))


def signin(request, from_path):
    # validation

    loginw = False

    if request.method == 'POST':
        userName = request.POST['usernamelogin']

        hashPassword = request.POST['passwordlogin']
        print(hashPassword)
        UserAccount = authenticate(username=userName, password=hashPassword)
        if UserAccount is not None:
            if UserAccount.is_active:

                login(request, UserAccount)
                # Llevar a la vista principal
                return HttpResponseRedirect(from_path)
            else:
                # Cuenta no activada

                return HttpResponseRedirect("/error")
        else:
            # Login incorrecto
            loginw = True
            return render_to_response('signin.html',
                                      {'loginw': loginw},
                                      context_instance=RequestContext(request))

    return render_to_response('signin.html',
                              {'loginw': loginw},
                              context_instance=RequestContext(request))


def register(request):
    djangoform = userDjangoForm()
    userform = OurUserRegistrationForm()
    if request.method == 'POST' and "submit" in request.POST:
        print("entra al formulario")
        userform = OurUserRegistrationForm(request.POST)
        djangoform = userDjangoForm(request.POST)
        if userform.is_valid() and djangoform.is_valid():
            print("formularios validos")
            # saving to database
            userp = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
            profile = userform.save(commit=False)
            profile.djangoUser = userp
            if 'picture' in request.FILES:
                profile.image = request.FILES['picture']

                # Now we save the UserProfile model instance.
                profile.save()
                print("registro ok")
                # request.session.flush()
                username = request.POST['username']
                hashpassword = request.POST['password']
                UserAccount = authenticate(username=username, password=hashpassword)
                login(request, UserAccount)
                return HttpResponseRedirect('/plan')
        else:
            print(djangoform.errors)
            print(userform.errors)
            djangoform = userDjangoForm()
    return render_to_response('register.html', context_instance=RequestContext(request))


def planfromlocation(request):
    save = request.POST.get('save', False)
    if request.method == 'POST' and save:
        plans = []
        print(request.POST)
        for i in range(len(request.POST)):
            to_save = request.POST.get('plan'+str(i), False)
            if to_save:
                act = []
                for j in range(len(request.POST)):
                    index = request.POST.get(to_save + str(j), False)
                    if index:
                        act.append(request.POST[to_save + str(j)])
                plans.append(act)
        for elem in plans:
            startDate = '2000-09-01T13:20:30+03:00'
            endDate = '3000-09-01T13:20:30+03:00'
            print('guardando plan')
            loc = Activity.objects.get(pk=elem[0]).location
            plan = Plan.objects.create(location=loc, startDate=startDate, endDate=endDate, voted=False, user=request.user.ouruser, done=False)
            i = 0
            for a in elem:
                act = Activity.objects.get(pk=a)
                print(act)
                saveToPlan(act, plan, i)
                i += 1
        return HttpResponseRedirect('/user_plans')
    else:
        if request.user.is_authenticated():
            list_of_plans = algorithm.algorithm(request.user.ouruser, request.POST['location'], 4, 10)
        else:
            list_of_plans = algorithm.algorithm(None, request.POST['location'], 4, 10)
        if len(list_of_plans) < int(request.POST['days']):
            list_of_plans = list_of_plans + algorithm.algorithm(request.ouruser, request.POST['location'], 4, 10)
            print('faltan planes')
        proposed_plan = list_of_plans[:int(request.POST['days'])]
        return render_to_response('planx.html', {'plan': proposed_plan}, context_instance=RequestContext(request))


# @login_required(login_url="/login/")
def automatic_plan(request):
    ranking = Activity.objects.all().order_by('valoration')[:5]

    # featured
    featured = Activity.objects.filter(isPromoted=True)

    # validation
    uservform = User.objects.all()

    #locations
    locations = []
    for a in Activity.objects.all():
        if a.location not in locations:
            locations.append(a.location)

    # sign up
    djangoform = userDjangoForm()
    userform = OurUserRegistrationForm()
    loginw = False
    if request.method == 'POST' and request.POST['inORup'] == 'up':
        print("aqui si entra")
        userform = OurUserRegistrationForm(request.POST)
        djangoform = userDjangoForm(request.POST)

        if userform.is_valid() and djangoform.is_valid():
            print("vamos")
            # saving to database
            userp = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])


            # Now sort out the userform instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = userform.save(commit=False)
            profile.djangoUser = userp

            if 'picture' in request.FILES:
                profile.image = request.FILES['picture']

                # Now we save the UserProfile model instance.
                profile.save()
                print("registro ok")
                # request.session.flush()
                username = request.POST['username']
                hashpassword = request.POST['password']
                UserAccount = authenticate(username=username, password=hashpassword)
                login(request, UserAccount)
                return HttpResponseRedirect('/home')
        else:
            print(djangoform.errors)
            print(userform.errors)
            djangoform = userDjangoForm()
            formulario = OurUserRegistrationForm()
            # ####

    if request.method == 'POST' and request.POST['inORup'] == 'in':
        userName = request.POST['usernamelogin']

        hashPassword = request.POST['passwordlogin']
        print(hashPassword)
        UserAccount = authenticate(username=userName, password=hashPassword)
        if UserAccount is not None:
            if UserAccount.is_active:
                print('jeje')
                login(request, UserAccount)
                # Llevar a la vista principal
                return HttpResponseRedirect("/home")
            else:
                # Cuenta no activada
                print('habia entrado')
                return HttpResponseRedirect("/error")
        else:
            # Login incorrecto
            loginw = True

            return render_to_response('automatic_plan.html',
                                      {'loginw': loginw,
                                       'userform': userform,
                                       'djangoform': djangoform, 'uservform': uservform, 'featured': featured[:3], 'locations': locations},
                                      context_instance=RequestContext(request))

    return render_to_response('automatic_plan.html',
                              {'loginw': loginw,
                               'userform': userform,
                               'djangoform': djangoform, 'uservform': uservform, 'featured': featured[:3],
                               'activities': ranking, 'locations': locations},
                              context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/plan")


def error(request):
    return render_to_response('404.html')


@login_required(login_url='/plan')
def home(request):
    # automatic plan
    # activities = Activity.objects.all()
    activities = Activity.objects.all()

    activities2 = []
    ac1 = activities[0]
    activities2.append(ac1)
    ac2 = activities[1]
    activities2.append(ac2)
    ac3 = activities[2]
    activities2.append(ac3)

    # user

    our = get_object_or_404(OurUser, djangoUser=request.user.id)


    # recently done
    recentplans = Plan.objects.filter(user=our, done=True).all()
    return render_to_response('home.html',
                              {'recentplans': recentplans, 'user': our, 'activities': activities, 'ac1': ac1,
                               'ac2': ac2,
                               'ac3': ac3}, context_instance=RequestContext(request))


def filter_activities(request):
    if request.user.is_authenticated():
        duser = request.user
        ouser = OurUser.objects.get(djangoUser=duser)
        print('iniciando filtrado')
        if request.method == 'POST' and 'filter' in request.POST:
            print('realizando filtrado')
            location = request.POST.get('location', False)
            sector = request.POST.get('sector', False)
            moment = request.POST.get('moment', False)
            sDate = request.POST.get('sDate', False)
            eDate = request.POST.get('eDate', False)
            val = request.POST.get('valoration', False)
            isFree = request.POST.get('isFree', False)
            isPromoted = request.POST.get('isPromoted', False)
            results = filtered_activities(location, sector, moment, sDate, eDate, val, isFree, isPromoted)
            print('results filtered')
            return render_to_response('customplan.html', {'user': ouser, 'results': results},
                                      context_instance=RequestContext(request))
        if request.method == 'POST' and 'custom' in request.POST:
            print('empezando el guardado')
            activities = []
            print(request.POST)
            for key, value in request.POST.items():
                if request.POST[key].isdigit():
                    print('sacando actividad')
                    activities.append(Activity.objects.get(pk=int(value)))
            startDate = '2000-09-01T13:20:30+03:00'
            endDate = '3000-09-01T13:20:30+03:00'
            loc = activities[0].location
            print('guardando plan')
            plan = Plan.objects.create(location=loc, startDate=startDate, endDate=endDate, voted=False, user=ouser, done=False)
            i = 0
            for a in activities:
                saveToPlan(a, plan, i)
                i += 1
            return HttpResponseRedirect("/todo")
        else:
            print('seleccionando parametros')
            return render_to_response('filter.html', {'user': ouser}, context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            print('realizando filtrado')
            location = request.POST.get('location', False)
            sector = request.POST.get('sector', False)
            moment = request.POST.get('moment', False)
            sDate = request.POST.get('sDate', False)
            eDate = request.POST.get('eDate', False)
            val = request.POST.get('valoration', False)
            isFree = request.POST.get('isFree', False)
            isPromoted = request.POST.get('isPromoted', False)
            results = filtered_activities(location, sector, moment, sDate, eDate, val, isFree, isPromoted)
            return render_to_response('customplan.html', {'results': results}, context_instance=RequestContext(request))
        else:
            print('seleccionando parametros')
            return render_to_response('filter.html', context_instance=RequestContext(request))


@login_required(login_url='/plan')
def timeline(request):
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    friends = ouser.friends.all()
    data = []
    for friend in friends:
        planesRealizados = []
        planes = Plan.objects.filter(user=friend)
        for p in planes:
            actividades = getActivitiesFrom(p)
            planesRealizados.append({'plan': p, 'activities': actividades})
        data.append({'friend': friend, 'donePlans': planesRealizados})
    return render_to_response('timeline.html', {'user': ouser, 'data': data}, context_instance=RequestContext(request))


@login_required(login_url='/plan')
def pocketplans(request):
    loguser = request.user
    ourser = OurUser.objects.get(djangoUser=loguser)
    userplans = []
    plans = Plan.objects.filter(user_id=ourser)
    for plan in plans:
        activities = getActivitiesFrom(plan)
        userplans.append({'plan': plan, 'activities': activities})
    friends = ourser.friends.all()
    if request.method == 'POST' and 'share' in request.POST:
        ident = request.POST.get("plan")
        plan = Plan.objects.filter(pk=ident).get()
        shareTo = []
        for toadd in request.POST['user']:
            shareTo.append(OurUser.objects.get(pk=int(toadd)))
        for p in shareTo:
            if p not in plan.sharedTo.all():
                plan.sharedTo.add(p)
        return HttpResponseRedirect("/user_plans")

    return render_to_response('user_plans.html', {'user': ourser, 'userplans': userplans, 'friends': friends},
                              context_instance=RequestContext(request))


def planinfo(request, plan_id):
    loguser = request.user
    ouser = OurUser.objects.get(djangoUser=loguser)
    plan = Plan.objects.get(id=plan_id)
    activities = getActivitiesFrom(plan)
    return render_to_response('planinfo.html', {'user': ouser, 'plan': plan, 'activities': activities},
                              context_instance=RequestContext(request))


def shareplan(request, plan_id):
    loguser = request.user
    ouser = OurUser.objects.get(djangoUser=loguser)
    plan = Plan.objects.filter(id=plan_id)
    activities = getActivitiesFrom(plan)
    return render_to_response('shareplan.html', {'user': ouser, 'plan': plan, 'activities': activities},
                              context_instance=RequestContext(request))


@login_required(login_url='/plan')
def todo(request):
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    if request.method == 'POST':
        ident = request.POST.get("id")
        Plan.objects.filter(pk=ident).update(done=True)
        return HttpResponseRedirect("/todo")
    else:
        planes = Plan.objects.filter(user=ouser, done=False)
        plans = []
        for plan in planes:
            activities = getActivitiesFrom(plan)
            plans.append({'plan': plan, 'activities': activities})
        paginator = Paginator(plans, 2)

        page = request.GET.get('page')
        try:
            objs = paginator.page(page)
        except PageNotAnInteger:
            objs = paginator.page(1)
        except EmptyPage:
            objs = paginator.page(paginator.num_pages)
        return render_to_response('todo.html', {'user': ouser, 'plans': objs},
                                  context_instance=RequestContext(request))


@login_required(login_url='/plan/')
def friends(request):
    duser = request.user
    print(duser)
    ouser = OurUser.objects.get(djangoUser=duser)
    friends = ouser.friends.all()
    all = OurUser.objects.all()
    print(friends)
    print(all)
    print(request.method)
    if request.method == 'POST':
        if 'borrar' in request.POST:
            idfriend = request.POST.get('friend')
            userfriend = OurUser.objects.get(id=idfriend)
            if userfriend in friends:
                ouser.friends.remove(userfriend)
                return HttpResponseRedirect("../friends")
        if 'añadir' in request.POST:
            idfriend = request.POST.get('friend')
            userfriend = OurUser.objects.get(id=idfriend)
            if userfriend not in friends:
                ouser.friends.add(userfriend)
                return HttpResponseRedirect("../friends")
    return render_to_response('friends.html', {'user': ouser, 'friends': friends, 'all': all},
                              context_instance=RequestContext(request))


def addfriend(request):
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    allusers = OurUser.objects.all()
    friends = ouser.friends.all()
    notfriends = []
    for a in allusers:
        if a not in friends:
            notfriends.append(a)
    if 'añadir' in request.POST:
        idfriend = request.POST.get('friend')
        userfriend = OurUser.objects.get(id=idfriend)
        if userfriend not in friends:
            ouser.friends.add(userfriend)
            return HttpResponseRedirect("../friends")
    print(notfriends)
    return render_to_response('addfriend.html',
                              {'user': ouser, 'notfriends': friends, 'allusers': allusers, 'friends': friends},
                              context_instance=RequestContext(request))


@login_required(login_url='/plan')
def modify_plan(request, plan_id):
    plan = Plan.objects.get(pk=plan_id)
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    activities = getActivitiesFrom(plan)
    if request.method == 'POST' and 'remove' in request.POST:
        for key, value in request.POST.items():
            if request.POST[key].isdigit():
                act = Activity.objects.get(pk=int(value))
                removeFromPlan(act, plan)
        return HttpResponseRedirect("/mod_plan/" + str(plan_id) + '/')
    if request.method == 'POST' and 'delete' in request.POST:
        for a in activities:
            removeFromPlan(a, plan)
        plan.delete()
        return HttpResponseRedirect("/user_plans")
    else:
        return render_to_response('mod_plan.html', {'user': ouser, 'plan': plan, 'activities': activities},
                                  context_instance=RequestContext(request))


@login_required(login_url='/plan')
def add_activities_to_given_plan(request, plan_id):
    plan = Plan.objects.get(pk=plan_id)
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    if request.method == 'POST' and 'filter' in request.POST:
        location = request.POST.get('location', False)
        sector = request.POST.get('sector', False)
        moment = request.POST.get('moment', False)
        sDate = request.POST.get('sDate', False)
        eDate = request.POST.get('eDate', False)
        val = request.POST.get('valoration', False)
        isFree = request.POST.get('isFree', False)
        isPromoted = request.POST.get('isPromoted', False)
        results = filtered_activities(location, sector, moment, sDate, eDate, val, isFree, isPromoted)
        return render_to_response('add_activities.html', {'user': ouser, 'plan': plan, 'results': results},
                                  context_instance=RequestContext(request))
    if request.method == 'POST' and 'add' in request.POST:
        for key, value in request.POST.items():
            if request.POST[key].isdigit():
                act = Activity.objects.get(pk=int(value))
                actividades = getActivitiesFrom(plan)
                last_index = Appearance.objects.get(plan=plan, activity=actividades[len(actividades) - 1]).order
                saveToPlan(act, plan, last_index + 1)
        return HttpResponseRedirect("/user_plans")
    else:
        return render_to_response('filter_to_modify.html', {'user': ouser, 'plan': plan},
                                  context_instance=RequestContext(request))


@login_required(login_url='/plan')
def profile(request, user_id):
    ouser = OurUser.objects.get(pk=user_id)
    return render_to_response('profile.html', {'user': ouser}, context_instance=RequestContext(request))


@login_required(login_url='/plan')
def preferences(request):
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    if request.method == 'POST' and 'psector' in request.POST:
        attribute_name = 'sector'
        attribute_value = Sector.objects.get(pk=request.POST['sector']).name
        degree = request.POST['degree']
        taste = Taste.objects.create(attribute_name=attribute_name, attribute_value=attribute_value, degree=degree)
        ouser.tastes.add(taste)
        return HttpResponseRedirect("/profile/"+str(request.user.ouruser.id)+'/')
    elif request.method == 'POST' and 'valoration' in request.POST:
        attribute_name = 'valoration'
        attribute_value = request.POST['minvaloration']
        degree = 0
        taste = Taste.objects.create(attribute_name=attribute_name, attribute_value=attribute_value, degree=degree)
        ouser.tastes.add(taste)
        return HttpResponseRedirect("/profile/"+str(request.user.ouruser.id)+'/')
    else:
        tastes = ouser.tastes.all()
        setmin = True
        for t in tastes:
            if t.attribute_name == 'valoration':
                setmin = False
        sectors = Sector.objects.all()
        return render_to_response('preferences.html', {'setmin': setmin, 'sectors': sectors},
                                  context_instance=RequestContext(request))


def term(request):
    return render_to_response('terms.html', context_instance=RequestContext(request))


def contact(request):
    return render_to_response('contact.html', context_instance=RequestContext(request))


# FUNCIONES AUXILIARES - MANTENER LAS VISTAS POR ENCIMA DE ESTO
def filtered_activities(location, sector, moment, sDate, eDate, val, isFree, isPromoted):
    results = []
    for a in Activity.objects.all():
        if location and a.location == location:
            results.append(a)
        if sector and a.sector.name == sector:
            results.append(a)
        moments = []
        for m in a.moment.all():
            moments.append(m.name)
        if moment and moment in moments:
            results.append(a)
        if sDate and eDate and sDate <= a.startDate and eDate >= a.endDate:
            results.append(a)
        if val and a.valoration >= int(val):
            results.append(a)
        if isFree and a.isFree == isFree:
            results.append(a)
        if isPromoted and a.isPromoted == isPromoted:
            results.append(a)
        if not location and not sector and not moment and not sDate and not eDate and not val and not isFree and not isPromoted:
            results.append(a)
    return results


def getActivitiesFrom(plan):
    plan_activities = Activity.objects.filter(plan__pk=plan.pk)
    aux = {}
    for ac in plan_activities:
        order_activity = Appearance.objects.get(plan=plan, activity=ac).order
        aux[order_activity] = ac
    sol = []
    for i in range(len(aux)):
        sol.append(aux[i])
    return sol


def saveToPlan(act, plan, order):
    app = Appearance(activity=act, plan=plan, order=order)
    app.save()


def removeFromPlan(act, plan):
    # sacamos las actividades del plan
    activities = getActivitiesFrom(plan)
    # limpiamos la relacion
    plan.activities.clear()
    # sacamos de la lista la actividad que no queremos guardar
    activities.remove(act)
    # guardamos las actividades con los indices de aparicion actualizados
    i = 0
    for elem in activities:
        saveToPlan(elem, plan, i)
        i += 1
