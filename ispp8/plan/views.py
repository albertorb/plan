from plan.models import *
from plan.forms import *
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404


from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.contrib.auth.hashers import make_password, pbkdf2
import random
from django.views.decorators.http import require_http_methods






#@login_required(login_url="/login/")
def automatic_plan(request):
    # sign up
    djangoform = userDjangoForm()
    userform = OurUserRegistrationForm()
    if request.method == 'POST' and request.POST['inORup'] == 'up':
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
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()
            print("registro ok")

            return HttpResponseRedirect('/home')
        else:

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
                # Llevar a la vista de error
                print('habia entrado')
                return HttpResponseRedirect("/panic.html")
        else:
            # Llevar a la vista de error

            return HttpResponseRedirect("/shit")


    #######

    # automatic plan
    #activities = Activity.objects.all()
    activities=Activity.objects.all()



    activities2=[]
    ac1 = activities[0]
    activities2.append(ac1)
    ac2 = activities[1]
    activities2.append(ac2)
    ac3 = activities[2]
    activities2.append(ac3)
    return render_to_response('automatic_plan_nonlogged.html',
                              { 'activities': activities, 'ac1': ac1, 'ac2': ac2, 'ac3': ac3, 'userform': userform,
                               'djangoform': djangoform},
                              context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    #return HttpResponseRedirect("/pagina1/pagina2")


def home(request):

    # automatic plan
    #activities = Activity.objects.all()
    activities=Activity.objects.all()

    activities2=[]
    ac1 = activities[0]
    activities2.append(ac1)
    ac2 = activities[1]
    activities2.append(ac2)
    ac3 = activities[2]
    activities2.append(ac3)

    # user

    our = get_object_or_404(OurUser,djangoUser=request.user.id)

    return render_to_response('home.html', {'request': our,'activities': activities, 'ac1': ac1, 'ac2': ac2, 'ac3': ac3}, context_instance=RequestContext(request))


def filter_plan(request):
    return render_to_response('filterplan.html', context_instance=RequestContext(request))

def list_plan(request):
    actividades= Activity.objects.filter(location=request.GET['l'])
    return render_to_response('filter_plan.html', {'activitiesfilt': actividades}, context_instance=RequestContext(request))


#@login_required(login_url="/login/")
def timeline(request):
    #Esto quiere decir, que debe mostrar que plan realizó recientemente, que plan votó, si compartió algún plan contigo (y que puntuación le dio)
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
        data.append({'friend': friend, 'donePlans': planesRealizados, 'votedPlans': planesVotados, 'sharedPlans': planesCompartidos})
    return render_to_response('timeline.html', {'data': data}, context_instance=RequestContext(request))
