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
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext as _


def getPlan(request, activity_id, activity_id2, activity_id3):
    act = get_object_or_404(Activity, id=activity_id)
    act2 = get_object_or_404(Activity, id=activity_id2)
    act3 = get_object_or_404(Activity, id=activity_id3)
    planform = PlanForm()
    plan = planform.save(commit=False)
    plan.voted = False
    plan.done = False
    plan.startDate = act.startDate
    plan.endDate = act3.endDate
    plan.user = request.user.ouruser
    plan.save()
    plan.activities = [act, act2, act3]

    return render_to_response('plan.html', {'plan': plan}, context_instance=RequestContext(request))


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

    return render_to_response('welcome.html',{}, context_instance=RequestContext(request))


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
            return render_to_response('activity.html',
                                      {'activity': obj, 'friendsDid': res, 'comments': comments, 'user': ourser},
                                      context_instance=RequestContext(request))
        return render_to_response('activity.html', {'activity': obj, 'friendsDid': res, 'comments': comments},
                                  context_instance=RequestContext(request))


def signin(request, from_path):
    #validation

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
                return HttpResponseRedirect('/'+from_path)
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
            #saving to database
            userp = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
            profile = userform.save(commit=False)
            profile.djangoUser = userp
            if 'picture' in request.FILES:
                profile.image = request.FILES['picture']

                # Now we save the UserProfile model instance.
                profile.save()
                print("registro ok")
                #request.session.flush()
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


#@login_required(login_url="/login/")
def automatic_plan(request):
    # automatic plan
    #activities = Activity.objects.all()
    activities = Activity.objects.all()

    activities2 = []
    ac1 = activities[0]
    activities2.append(ac1)
    ac2 = activities[1]
    activities2.append(ac2)
    ac3 = activities[2]
    activities2.append(ac3)

    # featured
    featured = Activity.objects.filter(isPromoted=True)

    #validation
    uservform = User.objects.all()

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
            #saving to database
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
                #request.session.flush()
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
            #####

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
                                      {'loginw': loginw, 'activities': activities, 'ac1': ac1, 'ac2': ac2, 'ac3': ac3,
                                       'userform': userform,
                                       'djangoform': djangoform, 'uservform': uservform, 'featured': featured[:3]},
                                      context_instance=RequestContext(request))


    #######


    return render_to_response('automatic_plan.html',
                              {'loginw': loginw, 'activities': activities, 'ac1': ac1, 'ac2': ac2, 'ac3': ac3,
                               'userform': userform,
                               'djangoform': djangoform, 'uservform': uservform, 'featured': featured[:3]},
                              context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/plan")


def error(request):
    return render_to_response('404.html')


@login_required(login_url='/plan')
def home(request):
    # automatic plan
    #activities = Activity.objects.all()
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
            print(results)
            return render_to_response('customplan.html', {'user': ouser, 'results': results}, context_instance=RequestContext(request))
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
            print('guardando plan')
            plan = Plan.objects.create(startDate=startDate, endDate=endDate, voted=False, user=ouser, done=False)
            for a in activities:
                plan.activities.add(a)
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
    print('getting django user')
    print(duser)
    ouser = OurUser.objects.get(djangoUser=duser)
    print('getting our user')
    print(ouser)
    friends = ouser.friends.all()
    print('checking number of friends')
    print(len(friends))
    data = []
    for friend in friends:
        planesRealizados = Plan.objects.filter(user=friend)
        print('checking number of done planes: ' + str(len(planesRealizados)))
        planesVotados = Plan.objects.filter(user=friend, voted=True)
        print('checking number of voted plans: ' + str(len(planesVotados)))
        planesCompartidos = Plan.objects.exclude(sharedTo__isnull=True)
        print('checking number of shared plans: ' + str(len(planesCompartidos)))
        data.append({'friend': friend, 'donePlans': planesRealizados, 'votedPlans': planesVotados,
                     'sharedPlans': planesCompartidos})
    return render_to_response('timeline.html', {'user': ouser, 'data': data}, context_instance=RequestContext(request))


@login_required(login_url='/plan')
def user_plans(request):
    loguser = request.user
    ouser = OurUser.objects.get(djangoUser=loguser)
    if request.method == 'POST':
        ident = request.POST.get("plan")
        plan = Plan.objects.filter(pk=ident).get()
        shareTo = []
        for toadd in request.POST['user']:
            shareTo.append(OurUser.objects.get(pk=int(toadd)))
        for p in shareTo:
            plan.sharedTo.add(p)
        return HttpResponseRedirect("../user_plans")
    else:
        plans = Plan.objects.filter(user=ouser).all()
        friends = ouser.friends.all()
        data = []
        for plan in plans:
            sharedTo = plan.sharedTo.all()
            toShare = []
            share = True
            for friend in friends:
                for s in sharedTo:
                    if s == friend:
                        share = False
                if share:
                    toShare.append(friend)
            data.append({'plan': plan, 'sharedTo': sharedTo, 'toShare': toShare})
        return render_to_response('user_plans.html', {'user': ouser, 'data': data},
                                  context_instance=RequestContext(request))


@login_required(login_url='/plan')
def todo(request):
    duser = request.user
    print('getting django user')
    print(duser)
    ouser = OurUser.objects.get(djangoUser=duser)
    print('getting our user')
    if request.method == 'POST':
        ident = request.POST.get("id")
        Plan.objects.filter(pk=ident).update(done=True)
        return HttpResponseRedirect("../todo")
    else:
        plans = Plan.objects.filter(user=ouser, done=False).all()
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


@login_required(login_url='/plan')
def modify_plan(request, plan_id):
    plan = Plan.objects.get(pk=plan_id)
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    if request.method == 'POST' and 'remove' in request.POST:
        for key, value in request.POST.items():
            if request.POST[key].isdigit():
                act = Activity.objects.get(pk=int(value))
                plan.activities.remove(act)
        return HttpResponseRedirect("/mod_plan/" + str(plan_id) + '/')
    if request.method == 'POST' and 'delete' in request.POST:
        plan.delete()
        return HttpResponseRedirect("/user_plans")
    else:
        return render_to_response('mod_plan.html', {'user': ouser, 'plan': plan},
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
                plan.activities.add(act)
        return HttpResponseRedirect("/user_plans")
    else:
        return render_to_response('filter_to_modify.html', {'user': ouser, 'plan': plan},
                                  context_instance=RequestContext(request))


@login_required(login_url='/plan')
def profile(request):
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)
    return render_to_response('profile.html', {'user': ouser}, context_instance=RequestContext(request))


def set_tastes(request):
    #duser = request.user
    #ouser = OurUser.objects.get(djangoUser=duser)
    if request.method == 'POST':
        print(request.POST)
    else:
        sectors = Sector.objects.all()
        return render_to_response('set_tastes.html', {'sectors': sectors}, context_instance=RequestContext(request))


#funcion extra para no repetir codigo
def filtered_activities(location, sector, moment, sDate, eDate, val, isFree, isPromoted):
    results = []
    for a in Activity.objects.all():
        if location and a.location == location:
            results.append(a)
        if sector and a.sector.name == sector:
            results.append(a)
        if moment and a.moment == moment:
            results.append(a)
        if sDate and eDate and sDate <= a.startDate and eDate >= a.endDate:
            results.append(a)
        if val and a.valoration >= val:
            results.append(a)
        if isFree and a.isFree == isFree:
            results.append(a)
        if isPromoted and a.isPromoted == isPromoted:
            results.append(a)
        if not location and not sector and not moment and not sDate and not eDate and not val and not isFree and not isPromoted:
            results.append(a)
    return results