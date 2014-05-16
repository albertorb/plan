#encoding: utf-8
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
    url(r'^plan$','plan.views.automatic_plan'),
    url(r'^activity/(?P<activity_id>\w+)/$','plan.views.activity', name='activity_info'),
    url(r'^plan/(?P<activity_id>\w+)/(?P<activity_id2>\w+)/(?P<activity_id3>\w+)/$','plan.views.getPlan', name='plan_info'),
    url(r'^home$','plan.views.home'),
    url(r'^filter$', 'plan.views.filter_activities'),
    url(r'^filterloged$', 'plan.views.filter_activities_registered'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT,}),
    url(r'^logout$', 'plan.views.logout'),
    url(r'^timeline$', 'plan.views.timeline'),
    url(r'^todo$', 'plan.views.todo'),
    url(r'^error$', 'plan.views.error'),
    url(r'^user_plans$', 'plan.views.user_plans'),
    url(r'^friends$','plan.views.friends'),
    url(r'^deletefriend/(?P<id_friend>\w+)/$','plan.views.deletefriend', name='delete_friend'),

    # Uncomment the next line to enable the admin:
    url(r'^admin', include(admin.site.urls)),
    url(r'', 'plan.views.welcome'),
)
