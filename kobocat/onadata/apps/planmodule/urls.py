from django.conf.urls import patterns, include, url
from django.contrib import admin
from onadata.apps.planmodule import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^facility_list/$', views.facility_list, name='facility_list'),
    url(r'^add_facility_form/$', views.add_facility_form, name='add_facility_form'),
    url(r'^insert_facility_form/$', views.insert_facility_form, name='insert_facility_form'),
    url(r'^edit_facility_form/(?P<form_id>\d+)/$', views.edit_facility_form, name='edit_facility_form'),
    url(r'^update_facility_form/$', views.update_facility_form, name='update_facility_form'),
    url(r'^delete_facility_form/(?P<facility_id>\d+)/$', views.delete_facility_form, name='delete_facility_form'),
    url(r'^getUpazilas/$', views.getUpazilas, name='getUpazilas'),
    url(r'^getUnions/$', views.getUnions, name='getUnions'),
url(r'^getType/$', views.getType, name='getType'),

    url(r'^scorecard_list/$', views.scorecard_list, name='scorecard_list'),
url(r'^add_scorecard_form/$', views.add_scorecard_form, name='add_scorecard_form'),
url(r'^insert_scorecard_form/$', views.insert_scorecard_form, name='insert_scorecard_form'),
url(r'^edit_scorecard_form/(?P<scorecard_id>\d+)/$', views.edit_scorecard_form, name='edit_scorecard_form'),
url(r'^delete_scorecard_form/(?P<scorecard_id>\d+)/$', views.delete_scorecard_form, name='delete_scorecard_form'),
url(r'^update_scorecard_form/$', views.update_scorecard_form, name='update_scorecard_form'),
    )
