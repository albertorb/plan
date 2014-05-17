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



def getPlan(request, activity_id,activity_id2,activity_id3):
    act = get_object_or_404(Activity, id=activity_id)
    act2 = get_object_or_404(Activity, id=activity_id2)
    act3 = get_object_or_404(Activity, id=activity_id3)
    planform = PlanForm()
    plan = planform.save(commit = False)
    plan.voted = False
    plan.done = False
    plan.startDate = act.startDate
    plan.endDate = act3.endDate
    plan.user = request.user.ouruser
    plan.save()
    plan.activities = [act,act2,act3]



    return render_to_response('plan.html', {'plan':plan},context_instance=RequestContext(request))


def welcome(request):
    return render_to_response('welcome.html',  context_instance=RequestContext(request))

def activity(request, activity_id):
    obj = get_object_or_404(Activity, id=activity_id)
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



    return render_to_response('activity.html', {'activity':obj, 'friendsDid':res}, context_instance=RequestContext(request))

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
            return render_to_response('automatic_plan_nonlogged.html',
                                      {'loginw': loginw, 'activities': activities, 'ac1': ac1, 'ac2': ac2, 'ac3': ac3,
                                       'userform': userform,
                                       'djangoform': djangoform, 'uservform': uservform,'featured':featured[:3]} ,
                                      context_instance=RequestContext(request))


    #######


    return render_to_response('automatic_plan_nonlogged.html',
                                      {'loginw': loginw, 'activities': activities, 'ac1': ac1, 'ac2': ac2, 'ac3': ac3,
                                       'userform': userform,
                                       'djangoform': djangoform, 'uservform': uservform,'featured':featured[:3]} ,
                                      context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/plan")


def error(request):
    return render_to_response('404.html')


@login_required(login_url='/plan/')
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
                              {'recentplans': recentplans, 'user': our, 'activities': activities, 'ac1': ac1, 'ac2': ac2,
                               'ac3': ac3}, context_instance=RequestContext(request))


def filter_activities(request):
    print('iniciando filtrado')
    if request.method == 'POST':
        print('realizando filtrado')
        results = []
        location = request.POST.get('location', False)
        sector = request.POST.get('sector', False)
        moment = request.POST.get('moment', False)
        sDate = request.POST.get('startDate', False)
        eDate = request.POST.get('endDate', False)
        val = request.POST.get('valoration', False)
        isFree = request.POST.get('isFree', False)
        isPromoted = request.POST.get('isPromoted', False)

        if location:
            activities = Activity.objects.filter(location__icontains=location)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if sector:
            activities = Activity.objects.filter(sector__icontains=sector)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if moment:
            activities = Activity.objects.filter(moment=moment)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if sDate and eDate:
            fsdate = time.strptime(sDate, '%b %d %Y %I:%M%p')
            fedate = time.strptime(eDate, '%b %d %Y %I:%M%p')
            activities = Activity.objects.filter(drop_off__gte=fsdate, pick_up__lte=fedate)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if val:
            activities = Activity.objects.filter(valoration__gt=val)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if isFree:
            activities = Activity.objects.filter(isFree=isFree)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if isPromoted:
            activities = Activity.objects.filter(isPromoted=isPromoted)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if not(location and sector and moment and sDate and eDate and val and isFree and isPromoted):
            results.append(Activity.objects.all())
        print(results)
        return render_to_response('customplan.html', {'results': results}, context_instance=RequestContext(request))
    else:
        print('seleccionando parametros')
        return render_to_response('filter.html', context_instance=RequestContext(request))


@login_required(login_url='/plan/')
def filter_activities_registered(request):
    duser = request.user
    ouser = OurUser.objects.get(djangoUser=duser)

    print('iniciando filtrado')
    if request.method == 'POST' and 'filter' in request.POST:
        print('realizando filtrado')
        results = []
        location = request.POST.get('location', False)
        sector = request.POST.get('sector', False)
        moment = request.POST.get('moment', False)
        sDate = request.POST.get('startDate', False)
        eDate = request.POST.get('endDate', False)
        val = request.POST.get('valoration', False)
        isFree = request.POST.get('isFree', False)
        isPromoted = request.POST.get('isPromoted', False)

        if location:
            activities = Activity.objects.filter(location__icontains=location)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if sector:
            activities = Activity.objects.filter(sector__icontains=sector)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if moment:
            activities = Activity.objects.filter(moment=moment)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if sDate and eDate:
            fsdate = time.strptime(sDate, '%b %d %Y %I:%M%p')
            fedate = time.strptime(eDate, '%b %d %Y %I:%M%p')
            activities = Activity.objects.filter(drop_off__gte=fsdate, pick_up__lte=fedate)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if val:
            activities = Activity.objects.filter(valoration__gt=val)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if isFree:
            activities = Activity.objects.filter(isFree=isFree)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if isPromoted:
            activities = Activity.objects.filter(isPromoted=isPromoted)
            if len(results) == 0:
                results.append(activities)
            else:
                results = list(set(results) & set(activities))
        if not(location and sector and moment and sDate and eDate and val and isFree and isPromoted):
            results.append(Activity.objects.all())
        print(results)
        return render_to_response('customplanloged.html', {'user': ouser, 'results': results}, context_instance=RequestContext(request))
    if request.method == 'POST' and 'custom' in request.POST:
        activities = []
        for key, value in request.POST.items():
            if request.POST[key].isdigit():
                activities.append(Activity.objects.get(pk=int(value)))
        startDate = time.ctime()
        endDate = time.strptime('Jun 1 2050  1:33PM', '%b %d %Y %I:%M%p')
        plan = Plan.objects.create(startDate=startDate, endDate=endDate, voted=False, user=ouser, done=False)
        for a in activities:
            plan.add(a)
        return HttpResponseRedirect("/todo")
    else:
        print('seleccionando parametros')
        return render_to_response('filterloged.html', {'user': ouser}, context_instance=RequestContext(request))


@login_required(login_url='/plan/')
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


@login_required(login_url='/plan/')
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
        return render_to_response('user_plans.html', {'user': ouser, 'data': data}, context_instance=RequestContext(request))


@login_required(login_url='/plan/')
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
        paginator = Paginator(plans,2)

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
    duser=request.user
    print(duser)
    ouser=OurUser.objects.get(djangoUser=duser)
    friends = ouser.friends.all()
    all=OurUser.objects.all()
    print(friends)
    print(all)
    for elem in friends:
        print(elem.djangoUser)
        print(elem.image)
    return render_to_response('friends.html',{'user':ouser,'friends':friends,'all':all},context_instance=RequestContext(request))


@login_required(login_url='/plan/')
def deletefriend(request,id_friend):
    userlogged=OurUser.objects.get(djangoUser=request.user)
    print(userlogged)
    friends=userlogged.friends.all()
    all=OurUser.objects.all()
    userfriend=OurUser.objects.get(id=id_friend)
    print(userfriend)
    for a in friends:
      if a == userfriend:
           userlogged.friends.remove(a)
    return render_to_response('friends.html',{"user":userlogged,'friends':friends,'all':all},context_instance=RequestContext(request))

@login_required(login_url='/plan/')
def addfriend(request,id_friend):
    userlogged=OurUser.objects.get(djangoUser=request.user)
    friends=userlogged.friends.all()
    all=OurUser.objects.all()
    userfriend=OurUser.objects.get(id=id_friend)
    if userfriend not in friends:
        userlogged.friends.add(userfriend)
    return render_to_response('friends.html',{"user":userlogged,'friends':friends,'all':all},context_instance=RequestContext(request))
