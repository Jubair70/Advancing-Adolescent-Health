#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import connection
from collections import OrderedDict
from django.http import HttpResponse
import dateutil.parser
from django.contrib.auth.models import User
from onadata.apps.usermodule.models import UserModuleProfile, Organizations
from django.views.decorators.csrf import csrf_exempt
import json
import csv


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


def __db_commit_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    fetchval = cursor.fetchone()
    cursor.close()
    return fetchval[0]


def __db_fetch_values_dict(query):
    cursor = connection.cursor()
    cursor.execute(query)
    fetchVal = dictfetchall(cursor)
    cursor.close()
    return fetchVal


def dictfetchall(cursor):
    desc = cursor.description
    return [
        OrderedDict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()]


# background process
def register_household_adolescent(request):
    unregistered_households = __db_fetch_values_dict(
        "select * from logger_instance where xform_id = 549 and deleted_at is NULL and json->>'hh_no' not in (select hh_no::text from plan_household_profile)")
    for unregistered_hh in unregistered_households:
        hh_id = register_household(unregistered_hh)
        if hh_id:
            register_hh_persons(unregistered_hh, hh_id)
            register_adolescents(unregistered_hh, hh_id)
    return HttpResponse("OK")


def register_household(unregistered_hh):
    district = unregistered_hh['json']['district']
    upazila = unregistered_hh['json']['upazila']
    union_name = unregistered_hh['json']['union_name']
    mouza = unregistered_hh['json']['mouza']
    village = unregistered_hh['json']['village']
    para = unregistered_hh['json']['para']
    hh_no = unregistered_hh['json']['hh_no']
    hh_head = unregistered_hh['json']['hh_head']
    respondent_name = unregistered_hh['json']['respondent_name']
    ethnicity = unregistered_hh['json']['ethnicity']
    hh_member = unregistered_hh['json']['hh_member']
    member_aged_8_19y = unregistered_hh['json']['member_aged_8_19y']
    if unregistered_hh['json'].has_key('_geolocation'):
        latitude = unregistered_hh['json']['_geolocation'][0]
        longitude = unregistered_hh['json']['_geolocation'][1]
    else:
        latitude = 'NULL'
        longitude = 'NULL'
    created_at = dateutil.parser.parse(unregistered_hh['json']['_submission_time'])
    created_user = User.objects.filter(username=unregistered_hh['json']['_submitted_by'])
    pngo_id = unregistered_hh['json']['pngo']

    hh_id = __db_commit_query(
        "INSERT INTO public.plan_household_profile (id, district, upazila, union_name, mouza, village, para, hh_no, hh_head, respondent_name, ethnicity, hh_member, member_aged_8_19y, latitude, longitude, pngo_id, created_at, created_by, updated_at, updated_by) VALUES(nextval('plan_household_profile_id_seq'::regclass), " + str(
            district) + ", " + str(upazila) + ", " + str(union_name) + ", " + str(mouza) + ", " + str(
            village) + ", " + str(para) + ", '" + str(hh_no) + "', '" + str(
            hh_head) + "', '" + respondent_name + "', " + str(ethnicity) + ", " + str(hh_member) + ", " + str(
            member_aged_8_19y) + ", '" + str(latitude) + "', '" + str(longitude) + "', '" + str(pngo_id) + "', '" + str(
            created_at) + "', " + str(created_user[0].id) + ", NULL, NULL) returning id")

    return hh_id


def register_hh_persons(unregistered_hh, hh_id):
    person_map = [[1, 'mem_name/father_name'], [2, 'mem_name/mother_name'], [3, 'mem_name/husband_wife_name'],
                  [4, 'mem_name/father_in_law'], [5, 'mem_name/mother_in_law']]
    for pm in person_map:
        if unregistered_hh['json'].has_key(pm[1]):
            __db_commit_query(
                "INSERT INTO public.plan_hh_living_person (id, hh_id, person_name, person_type) VALUES(nextval('plan_hh_living_person_id_seq'::regclass), " + str(
                    hh_id) + ", '" + str(unregistered_hh['json'][pm[1]]) + "', " + str(pm[0]) + ") returning id")
    return 0


def register_adolescents(unregistered_hh, hh_id):
    for ado_info in unregistered_hh['json']['ado_info']:
        if not str(ado_info['ado_info/id_adolescent']).endswith('0'):
            adolescent_name = ado_info['ado_info/adolescent_name']
            id_adolescent = ado_info['ado_info/id_adolescent']
            sex = ado_info['ado_info/sex']
            age = ado_info['ado_info/age']
            have_birth_reg = ado_info['ado_info/have_birth_reg']
            have_birth_reg = ado_info['ado_info/have_birth_reg']
            relation = ado_info['ado_info/relation']
            going_school = ado_info['ado_info/going_school']
            work_wage = ado_info['ado_info/work_wage']
            disable = ado_info['ado_info/disable']
            mobile = ado_info['ado_info/mobile']
            mobile_owner = ado_info['ado_info/mobile_owner']
            maritial_status = ado_info['ado_info/maritial_status']
            if ado_info.has_key('marriage_reg'):
                marriage_reg = ado_info['ado_info/marriage_reg']
            else:
                marriage_reg = 'NULL'
            if ado_info.has_key('maritial_duration'):
                maritial_duration = ado_info['ado_info/maritial_duration']
            else:
                maritial_duration = 'NULL'
            if ado_info.has_key('child_any'):
                child_any = ado_info['ado_info/child_any']
            else:
                child_any = 'NULL'
            if ado_info.has_key('child_num'):
                child_num = ado_info['ado_info/child_num']
            else:
                child_num = 'NULL'
            if ado_info.has_key('pregnant_currently'):
                pregnant_currently = ado_info['ado_info/pregnant_currently']
            else:
                pregnant_currently = 'NULL'

            __db_commit_query(
                "INSERT INTO public.plan_adolescents_profile (id, hh_id, adolescent_name, id_adolescent, sex, age, have_birth_reg, relation, going_school, work_wage, disable, mobile, mobile_owner, maritial_status, marriage_reg, maritial_duration, child_any, child_num, pregnant_currently) VALUES(nextval('plan_adolescents_profile_id_seq'::regclass), " + str(
                    hh_id) + ", '" + str(adolescent_name) + "', '" + str(id_adolescent) + "', " + str(sex) + ", " + str(
                    age) + ", " + str(have_birth_reg) + "," + str(relation) + ", " + str(going_school) + ", " + str(
                    work_wage) + ", " + str(disable) + ", '" + str(mobile) + "', " + str(mobile_owner) + ", " + str(
                    maritial_status) + ", " + str(marriage_reg) + "," + str(maritial_duration) + ", " + str(
                    child_any) + ", " + str(child_num) + ", " + str(pregnant_currently) + ") returning id")
    return 0


@csrf_exempt
def get_adolescent_list(request):
    username = request.GET.get('username')
    adolescent_query = " WITH w AS(WITH t AS (SELECT id AS aid, hh_id, adolescent_name, id_adolescent, sex, age, have_birth_reg, relation, going_school, work_wage, disable, mobile, mobile_owner, maritial_status, marriage_reg, maritial_duration, child_any, child_num, pregnant_currently FROM plan_adolescents_profile), s AS (SELECT id, district, upazila, union_name, mouza, village, para, hh_head, hh_no, pngo_id FROM plan_household_profile) SELECT * FROM t, s WHERE t.hh_id = s.id) SELECT DISTINCT ON (id_adolescent) aid, pngo_id, district, upazila, union_name, mouza, village, para, hh_head, hh_no, adolescent_name, id_adolescent, sex, age, have_birth_reg, relation, going_school, work_wage, disable, mobile, mobile_owner, maritial_status, marriage_reg, maritial_duration, child_any, child_num, pregnant_currently, (select person_name from plan_hh_living_person where person_type = 1 and hh_id = hh_id limit 1) as father_name, (select person_name from plan_hh_living_person where person_type = 2 and hh_id = hh_id limit 1) as mother_name, (select person_name from plan_hh_living_person where person_type = 3 and hh_id = hh_id limit 1) as husband_wife_name, (select person_name from plan_hh_living_person where person_type = 4 and hh_id = hh_id limit 1) as father_in_law_name, (select person_name from plan_hh_living_person where person_type = 5 and hh_id = hh_id limit 1) as mother_in_law_name FROM w WHERE union_name :: text = (SELECT (SELECT geocode FROM geo_data WHERE id = geoid) FROM usermodule_catchment_area WHERE user_id = (SELECT id FROM auth_user WHERE username = '" + str(
        username) + "'))"
    adolescent_data = __db_fetch_values_dict(adolescent_query)
    return HttpResponse(json.dumps(adolescent_data))


@csrf_exempt
def get_cmp_list(request):
    username = request.GET.get('username')
    cmp_query = "SELECT pngo, district, upazila, union_name, mouza, village, para, adolescent_name, id_adolescent, sex, father_name, mother_name, date_birth, birth_place, birth_reg, date_chilc_marriage_prevented, date_proposed_marriage, person_involved_prevent, username,null as vigilance_one_mon,null as vigilance_three_mon,null as status_at_eighteen FROM public.vw_cmp_registration where union_name :: text = (SELECT (SELECT geocode FROM geo_data WHERE id = geoid) FROM usermodule_catchment_area WHERE user_id = (SELECT id FROM auth_user WHERE username = '" + str(
        username) + "'))"
    cmp_data = __db_fetch_values_dict(cmp_query)
    return HttpResponse(json.dumps(cmp_data))


@csrf_exempt
def get_lse_group_list(request):
    username = request.GET.get('username')
    lse_grp_list_query = "SELECT row_number() OVER () as serial_no,data_id as group_id ,pngo, district, upazila, union_name, mouza, village, para, group_no, group_type,maritial_status, username,(select count(*) from vw_grp_reg_sessions where group_id::int = data_id) as no_of_sessions,((with t as(select group_id, unnest(string_to_array(adolescent_name, ' ')) as adolescent_name from vw_lse_grp_members) select count(*) from t where group_id::int = data_id)) as no_of_adols FROM public.vw_grp_registration where union_name :: text = (SELECT (SELECT geocode FROM geo_data WHERE id = geoid) FROM usermodule_catchment_area WHERE user_id = (SELECT id FROM auth_user WHERE username = '" + str(
        username) + "'))"
    lse_grp_list_data = __db_fetch_values_dict(lse_grp_list_query)
    return HttpResponse(json.dumps(lse_grp_list_data))


@csrf_exempt
def get_comm_orientation_list(request):
    username = request.GET.get('username')
    comm_orientation_query = "SELECT date, case orientation_type When '1' then 'কমিউনিটি ওরিয়েন্টেশন' When '2' then 'ধর্মীয় নেতা' When '3' then 'বিবাহিত কিশোরী / দম্পত্তি ওরিয়েন্টেশন' When '4' then 'ইস্যুভিত্তিক মিটিং' end as orientation_type, count(data_id) as no_of_participants FROM public.vw_comm_orientation where union_name :: text =(SELECT (SELECT geocode FROM geo_data WHERE id = geoid) FROM usermodule_catchment_area WHERE user_id = (SELECT id FROM auth_user WHERE username = '" + str(
        username) + "')) group by data_id,orientation_type,date order by date(date) DESC"
    comm_orientation_data = __db_fetch_values_dict(comm_orientation_query)
    return HttpResponse(json.dumps(comm_orientation_data))


@csrf_exempt
def get_csa_list(request):
    username = request.GET.get('username')
    csa_list_query = "select vcr.id_adolescent,(select adolescent_name from plan_adolescents_profile where id_adolescent = vcr.id_adolescent) as adolescent_name,to_char(business_start_month::date, 'Mon YYYY') as business_start_month from vw_csa_registration vcr where vcr.union_name :: text =(SELECT (SELECT geocode FROM geo_data WHERE id = geoid) FROM usermodule_catchment_area WHERE user_id = (SELECT id FROM auth_user WHERE username = '" + str(
        username) + "'))"
    csa_list_data = __db_fetch_values_dict(csa_list_query)
    return HttpResponse(json.dumps(csa_list_data))


@csrf_exempt
def get_adolescent_list_by_group(request):
    group_id = request.GET.get('group_id')
    # adolescent_list_query = "with t as(select group_id, unnest(string_to_array(adolescent_name, ' ')) as id_adolescent from vw_lse_grp_members) select t.id_adolescent,(select adolescent_name from plan_adolescents_profile where id_adolescent = t.id_adolescent) as adolescent_name from t where group_id::int = "+str(group_id)
    # adolescent_list_data = __db_fetch_values_dict(adolescent_list_query)
    # return HttpResponse(json.dumps(adolescent_list_data))

    curated_data = []
    group_attendance_data = __db_fetch_values_dict(
        "with v as(with t as(select session_date,group_id, unnest(string_to_array(adolescent_name, ' ')) as id_adolescent,session,'1' as session_type from vw_grp_reg_sessions union all select session_date,group_id, unnest(string_to_array(adolescent_name, ' ')) as id_adolescent,session,'2' as session_type from vw_grp_mkp_sessions) select distinct on (id_adolescent,session) * from t), n as(with m as(select group_id, unnest(string_to_array(adolescent_name, ' ')) as id_adolescent from vw_lse_grp_members) select m.id_adolescent,m.group_id,(select adolescent_name from plan_adolescents_profile where id_adolescent = m.id_adolescent) as adolescent_name from m) select n.id_adolescent,(select adolescent_name from plan_adolescents_profile where id_adolescent = n.id_adolescent) as adolescent_name,session,session_type from v,n where v.group_id = n.group_id and v.id_adolescent = n.id_adolescent and v.group_id::int = " + str(
            group_id))
    group_all_session_list = list(sum(__db_fetch_values(
        "with q as( select json_array_elements((json::json->'choices')->'session') as choices from logger_xform where id = 558) select choices->>'name' as name from q where choices->>'myfilter' =(select group_type from vw_grp_registration where data_id = " + str(
            group_id) + ")"), ()))

    adolescent_sessions = {}
    listed_adols = []
    for gad in group_attendance_data:
        if not adolescent_sessions.has_key(gad['id_adolescent']):
            adolescent_sessions[gad['id_adolescent']] = [{gad['session']:gad['session_type']}]
        else:
            adolescent_sessions[gad['id_adolescent']].append({gad['session']:gad['session_type']})

    for adol in adolescent_sessions:
        sessions = []
        for gasl in group_all_session_list:
            if gasl in [y for x in [s.keys() for s in adolescent_sessions[adol]] for y in x]:
                merged_sessions = {}
                for k in adolescent_sessions[adol]:
                    merged_sessions.update(k)
                sessions_type = merged_sessions[gasl]
                if sessions_type == '1':
                    sessions.append({'sessions': gasl, 'is_present': 1})
                else:
                    sessions.append({'sessions': gasl, 'is_present': 2})
            else:
                sessions.append({'sessions': gasl, 'is_present': 0})

        if adol not in listed_adols:
            listed_adols.append(adol)
            new_od = [d for d in group_attendance_data if d['id_adolescent'] == adol][0]
            del new_od['session']
            del new_od['session_type']
            new_od.update({'sessions': sessions})
            curated_data.append(new_od)
    return HttpResponse(json.dumps(curated_data))


@csrf_exempt
def get_monthly_cf_form_list(request):
    username = request.GET.get('username')
    monthly_cf_query = "SELECT data_id, date, activity_name, no_of_activity, married_boy, married_girl, unmarried_boy, unmarried_girl, ir3_2c_42, boy_10_14, girl_10_14, boy_15_19, girl_15_19, comments, username FROM public.vw_cf_miscellaneous_activity where username = '" + str(
        username) + "'"
    monthly_cf_data = __db_fetch_values_dict(monthly_cf_query)
    return HttpResponse(json.dumps(monthly_cf_data))


def get_session_list_group(request):
    group_id = request.GET.get('group_id')
    session_list_query = "select session as sess_name,session_label as sess_label from vw_grp_reg_sessions where group_id::int = " + str(
        group_id)
    session_list_data = __db_fetch_values(session_list_query)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + str(group_id) + '_sessions.csv"'
    writer = csv.writer(response)
    writer.writerow(['sess_name', 'sess_label'])
    for data in session_list_data:
        writer.writerow([data[0].encode('utf-8'), data[1].encode('utf-8')])
    return response


def get_makeup_session_data(request):
    group_id = request.GET.get('group_id')
    makeup_session_query = "with g as(with s as(with d as(with v as(select name,label from vw_sessions_list where myfilter =(select group_type from vw_grp_registration where data_id = " + str(group_id) + ")) select * from v cross join (with n as(select unnest(string_to_array(adolescent_name, ' ')) as id_adolescent from vw_lse_grp_members where group_id::int = " + str(group_id) + ") select distinct id_adolescent from n) p) select name as session,id_adolescent from d), w as(with c as(with a as(select unnest(string_to_array(adolescent_name, ' ')) as id_adolescent,session from vw_grp_mkp_sessions where group_id::int = " + str(group_id) + ") select distinct on (id_adolescent) session,id_adolescent from a union all (with b as(select unnest(string_to_array(adolescent_name, ' ')) as id_adolescent,session from vw_grp_reg_sessions where group_id::int = " + str(group_id) + ") select distinct on (id_adolescent) session,id_adolescent from b)) select distinct session,id_adolescent from c) select session,id_adolescent from s except (select * from w)) select (select label from vw_sessions_list where name = session limit 1) as sessionname,session as sessionid,(select adolescent_name from plan_adolescents_profile where id_adolescent = g.id_adolescent) as adolescent_name,id_adolescent from g"
    makeup_session_data = __db_fetch_values(makeup_session_query)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + str(group_id) + '_makeup_sessions.csv"'
    writer = csv.writer(response)
    writer.writerow(['sessionname', 'sessionid','adolescent','adolescentid'])
    for data in makeup_session_data:
        writer.writerow([data[0].encode('utf-8'), data[1].encode('utf-8'),data[2].encode('utf-8'), data[3].encode('utf-8')])
    return response
