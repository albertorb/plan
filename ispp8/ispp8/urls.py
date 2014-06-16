# encoding: utf-8
from django.conf.urls import patterns, url, include
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'ispp.views.home', name='home'),
                       # url(r'^ispp/', include('ispp.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^plan$', 'plan.views.automatic_plan'),
                       url(r'^activity/(?P<activity_id>\w+)/$', 'plan.views.activity', name='activity_info'),
                       url(r'^plan/(?P<activity_id>\w+)/(?P<activity_id2>\w+)/(?P<activity_id3>\w+)/$',
                           'plan.views.getPlan', name='plan_info'),
                       url(r'^home$', 'plan.views.home'),
                       url(r'^filter$', 'plan.views.filter_activities'),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, }),
                       url(r'^logout$', 'plan.views.logout'),
                       url(r'^timeline$', 'plan.views.timeline'),
                       url(r'^todo$', 'plan.views.todo'),
                       url(r'^error$', 'plan.views.error'),
                       url(r'^user_plans$', 'plan.views.pocketplans'),
                       url(r'^friends$', 'plan.views.friends'),
                       url(r'^signin/(?P<from_path>.*)/$', 'plan.views.signin'),
                       url(r'^mod_plan/(?P<plan_id>\d+)/$', 'plan.views.modify_plan'),
                       url(r'^addto_plan/(?P<plan_id>\d+)/$', 'plan.views.add_activities_to_given_plan'),
                       url(r'^preferences$', 'plan.views.preferences'),
                       url(r'^register$', 'plan.views.register'),
                       url(r'^planinfo/(?P<plan_id>\w+)/$', 'plan.views.planinfo'),
                       url(r'^search', 'plan.views.search'),
                       url(r'^addfriend$', 'plan.views.addfriend'),
                       url(r'^repeatedplan$', 'plan.views.repeatedplan'),
                       url(r'^terms$', 'plan.views.term'),
                       url(r'^contacto$', 'plan.views.contact'),
                       url(r'^profile/(?P<user_id>\d+)/$', 'plan.views.profile'),
                       url(r'^getplan', 'plan.views.planfromlocation'),
                       url(r'^i18n/', include('django.conf.urls.i18n')),
                       url(r'^accounts/', include('allauth.urls')),
                       # Uncomment the next line to enable the admin:
                       url(r'^admin', include(admin.site.urls)),
                       url(r'^$', 'plan.views.welcome'),
)
