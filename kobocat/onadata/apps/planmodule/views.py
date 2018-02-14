from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Count, Q
from django.http import (
    HttpResponseRedirect, HttpResponse)
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
# from django.utils import simplejson
import json
import logging
import sys
import operator
import pandas
from django.shortcuts import render
import numpy
import time
import datetime
from django.core.files.storage import FileSystemStorage

from django.core.urlresolvers import reverse


from django.db import (IntegrityError, transaction)
from django.db.models import ProtectedError
from django.shortcuts import redirect
from onadata.apps.main.models.user_profile import UserProfile
from onadata.apps.usermodule.forms import UserForm, UserProfileForm, ChangePasswordForm, UserEditForm, OrganizationForm, \
    OrganizationDataAccessForm, ResetPasswordForm
from onadata.apps.usermodule.models import UserModuleProfile, UserPasswordHistory, UserFailedLogin, Organizations, \
    OrganizationDataAccess

from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
# Menu imports
from onadata.apps.usermodule.forms import MenuForm
from onadata.apps.usermodule.models import MenuItem
# Unicef Imports
from onadata.apps.logger.models import Instance, XForm
# Organization Roles Import
from onadata.apps.usermodule.models import OrganizationRole, MenuRoleMap, UserRoleMap
from onadata.apps.usermodule.forms import OrganizationRoleForm, RoleMenuMapForm, UserRoleMapForm, UserRoleMapfForm
from django.forms.models import inlineformset_factory, modelformset_factory
from django.forms.formsets import formset_factory

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from collections import OrderedDict
import decimal
import os


def __db_fetch_values(query):
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = cursor.fetchall()
    cursor.close()
    return fetchVal


def __db_fetch_single_value(query):
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = cursor.fetchone()
    cursor.close()
    return fetchVal[0]


def __db_fetch_values_dict(query):
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = dictfetchall(cursor)
    cursor.close()
    return fetchVal


def __db_commit_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()


def dictfetchall(cursor):
    desc = cursor.description
    return [
        OrderedDict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()]


def decimal_date_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj
    raise TypeError


def index(request):
    return render(request, 'planmodule/index.html')



def facility_list(request):
    query = "select id,DATE(registration_date) registration_date, (select field_name from geo_data where id = district) district,(select field_name from geo_data where id = upazilla) upazilla,(select field_name from geo_data where id = xunion) xunion, facilty_name, facilty_id,facility_type from plan_facilities"
    facility_list = json.dumps(__db_fetch_values_dict(query),default= decimal_date_default)

    return render(request, 'planmodule/facility_list.html',{
        'facility_list': facility_list
    })


def add_facility_form(request):
    query = "select id,field_name from geo_data where field_type_id = 86"
    df = pandas.DataFrame()
    df = pandas.read_sql(query, connection)
    dist_id = df.id.tolist()
    dist_name = df.field_name.tolist()
    district = zip(dist_id, dist_name)

    print(district)
    return render(request,'planmodule/add_facility_form.html',{'district':district})


def insert_facility_form(request):
    if request.POST:
        registration_date = request.POST.get('registration_date')
        district = request.POST.get('district')
        upazilla = request.POST.get('upazila')
        union = request.POST.get('union')
        facilty_name = request.POST.get('facility_name')
        facilty_id = request.POST.get('facility_id')
        facility_type = request.POST.get('facility_type')
        user = request.user
        user_query = "select id from auth_user where username='"+str(user)+"'"
        df = pandas.DataFrame()
        df = pandas.read_sql(user_query, connection)
        user_id = df.id.tolist()[0]
        insert_query = "INSERT INTO public.plan_facilities (registration_date, district, upazilla, xunion, facilty_name, facilty_id,facility_type,created_by) VALUES('"+str(registration_date)+"', "+str(district)+", "+str(upazilla)+", "+str(union)+", '"+str(facilty_name)+"', '"+str(facilty_id)+"','"+str(facility_type)+"',"+str(user_id)+")"
        __db_commit_query(insert_query)
    return HttpResponseRedirect("/planmodule/facility_list/")


def edit_facility_form(request,form_id):
    query = "select DATE(registration_date) registration_date,(select field_name from geo_data where id = district) district_name,(select field_name from geo_data where id = upazilla) upazilla_name,(select field_name from geo_data where id = xunion) union_name,  district, upazilla, xunion, facilty_name, facilty_id,facility_type from plan_facilities where id="+str(form_id)+""
    df = pandas.DataFrame()
    df = pandas.read_sql(query,connection)
    data = {}
    data['form_id'] = form_id
    data['registration_date'] = df.registration_date.tolist()[0]
    data['facilty_name'] = df.facilty_name.tolist()[0]
    data['facilty_id'] = df.facilty_id.tolist()[0]
    data['facility_type'] = df.facility_type.tolist()[0]
    district_id = df.district.tolist()[0]
    district_name = df.district_name.tolist()[0]
    upazila_id = df.upazilla.tolist()[0]
    upazilla_name = df.upazilla_name.tolist()[0]
    xunion_id = df.xunion.tolist()[0]
    xunion_name = df.union_name.tolist()[0]


    query = "select id,field_name from geo_data where field_type_id = 88 and field_parent_id = "+str(district_id)
    df = pandas.DataFrame()
    df = pandas.read_sql(query, connection)
    upz_id = df.id.tolist()
    upz_name = df.field_name.tolist()
    upazila = zip(upz_id, upz_name)

    query = "select id,field_name from geo_data where field_type_id = 89 "
    df = pandas.DataFrame()
    df = pandas.read_sql(query, connection)
    union_id = df.id.tolist()
    union_name = df.field_name.tolist()
    union = zip(union_id, union_name)

    return render(request,'planmodule/edit_facility_form.html',{'data':json.dumps(data,default=decimal_date_default),'district_id':district_id,'district_name':district_name,'upazila_id':upazila_id,'upazilla_name':upazilla_name,'xunion_id':xunion_id,'xunion_name':xunion_name,'upazila':upazila,'union':union})


def update_facility_form(request):
    if request.POST:
        form_id = request.POST.get('form_id')
        registration_date = request.POST.get('registration_date')
        district = request.POST.get('district')
        upazilla = request.POST.get('upazila')
        union = request.POST.get('union')
        facilty_name = request.POST.get('facility_name')
        facilty_id = request.POST.get('facility_id')
        facility_type = request.POST.get('facility_type')
        user = request.user
        user_query = "select id from auth_user where username='" + str(user) + "'"
        df = pandas.DataFrame()
        df = pandas.read_sql(user_query, connection)
        user_id = df.id.tolist()[0]
        update_query = "UPDATE public.plan_facilities SET registration_date='"+str(registration_date)+"', district="+str(district)+", upazilla="+str(upazilla)+", xunion="+str(union)+", facilty_name='"+str(facilty_name)+"', facilty_id='"+str(facilty_id)+"', created_at=now(), created_by="+str(user_id)+" WHERE id="+str(form_id)
        __db_commit_query(update_query)
    return HttpResponseRedirect("/planmodule/facility_list/")


def delete_facility_form(request,facility_id):
    delete_query = "delete from plan_facilities where id = " + str(facility_id) + ""
    __db_commit_query(delete_query)
    return HttpResponseRedirect("/planmodule/facility_list/")





def getUpazilas(request):
    district = request.POST.get('dist')
    upazila_query = "select id,field_name from geo_data where field_type_id = 88 and field_parent_id = " + str(district)
    upazila_data = json.dumps(__db_fetch_values_dict(upazila_query))
    return HttpResponse(upazila_data)

def getUnions(request):
    upazila = request.POST.get('upz')
    union_query = "select id,field_name from geo_data where field_type_id = 89 and field_parent_id = " + str(upazila)
    union_data = json.dumps(__db_fetch_values_dict(union_query))
    return HttpResponse(union_data)