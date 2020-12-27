#!/usr/bin/env python3

usage_mesg= """

Options:
    --lvls              : print member levels and exit
    --mlvls             : print members and their level and exit
    --mfn  field_id     : print members and value of a particular field name
    --cfs               : print contact fields and exit
    --cfav field_id     : print field allowed values
    --chk               : perform consistency check and report
    --sos               : print signoffs
    --mig field         : migrate field from spaceman
    --ema email_addr    : specify email address to operate on
    --update            : actually perform update to WA
    --fso signoff_label : find everyone w/a given signoff
                        : --fso '[nlgroup] GO_New Member Orientation'

"""

"""
adapted from spaceman2apricot.py by https://github.com/azagh
"""

import os
import sys
from dotenv import load_dotenv
from WaApi import WaApiClient
import pprint
import getopt
import urllib
import pandas
from pdb import set_trace as dbg
import requests
import csv

sys.exit_code_fail = 1
sys.exit_code_ok   = 0

pp = pprint.PrettyPrinter(stream=sys.stderr)

load_dotenv(override=True)

# Connect to WA and get all the contacts from WA
api                = WaApiClient(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
api.authenticate_with_apikey(os.getenv("API_KEY"))

accounts           = api.execute_request("/accounts")
account            = accounts[0]
contactsUrl        = account.Url + '/Contacts'
contactfieldsUrl   = account.Url + '/contactfields'
contactsignoffsUrl = contactfieldsUrl + '/12472413'

def p(s):
    # write to stdout
    sys.stdout.write(s)

def perr(s):
    # write to stderr
    sys.stderr.write(s)

def update_signoffs(contact_id,signoffs,signoffs_ids_by_name):
    #pp.pprint(get_contacts_signoffs_by_email('bob@cogwheel.com'))
    """
      how we do it in js
      wa_put_data = 
        {
          'Id' : this_contact_id ,
          'FieldValues' : 
          [{ 
            'FieldName' : 'EquipmentSignoffs',
            'SystemCode' : window.wautils_equipment_signoff_systemcode,
            'Value' : 
            indiv_signoff_ids

          }]
        }

    What they look like in a get

    {   'FieldName': 'NL Signoffs and Categories',

    'SystemCode': 'custom-12472413',
    'Value': [   {"Id": 13925244, "Label": "[equipment] *GREEN"},
                 {"Id": 13925245, "Label": "[equipment] *Minor or Supervised Access Only"}]}

    """
    # build individual list of signoffs 
    soc = []
    for sos in signoffs:
        soc.append({'Id': int(signoffs_ids_by_name[sos]), 'Label': sos})
    """
    soc should look something like this now:

            [{'Id': 13948202, 'Label': '[equipment] WW_Rikon_Bandsaw Red'},
             {'Id': 13948213, 'Label': '[equipment] WWR_SawStop_Table Saw'},
             {'Id': 13948153, 'Label': '[signoff] GREEN ORIENTATION'},
             {'Id': 13948228, 'Label': '[novapass] WWR_SawStop_Table Saw'},
             {'Id': 13948200, 'Label': '[equipment] WW_General_Bandsaw Red'},
             {'Id': 13948238, 'Label': '[category] members'}]
    """


    # fill in the rest of the request
    data = {}
    data['Id'] = str(contact_id)
    data['FieldValues'] = [] 
    data['FieldValues'].append({'FieldName':'NL Signoffs and Categories',
                                'SystemCode':'custom-12472413',
                                'Value': soc 
                                })
        
    """
    The completed request:

    {   'FieldValues': [   {   'FieldName': 'NL Signoffs and Categories',
                           'SystemCode': 'custom-12472413',
                           'Value': [   {   'Id': 13948202,
                                            'Label': '[equipment] '
                                                     'WW_Rikon_Bandsaw Red'},
                                        {   'Id': 13948213,
                                            'Label': '[equipment] '
                                                     'WWR_SawStop_Table Saw'},
                                        {   'Id': 13948153,
                                            'Label': '[signoff] GREEN '
                                                     'ORIENTATION'},
                                        {   'Id': 13948228,
                                            'Label': '[novapass] '
                                                     'WWR_SawStop_Table Saw'},
                                        {   'Id': 13948200,
                                            'Label': '[equipment] '
                                                     'WW_General_Bandsaw Red'},
                                        {   'Id': 13948238,
                                            'Label': '[category] members'}]}],
    'Id': '56825441'}

    """

    #pp.pprint("---------")
    #pp.pprint(data)
    #pp.pprint("---------")
    result = api.execute_request_raw(contactsUrl + "/" + str(contact_id), api_request_object=data, method='PUT')
    #import pdb;pdb.set_trace() # stop and debug
    return result


def print_all_signoffs():
    cfs = api.execute_request(contactfieldsUrl)
    for f in cfs:
        if f.FieldName == "NL Signoffs and Categories":
            for so in f.AllowedValues:
                o = '' 
                o += '%-10.10s' % (so.Id)
                o += '  %s' % ('"' + so.Label + '"')
                o += '\n' 
                p(o)


def get_contacts_signoffs_by_email(email):
    #wa_contact  = get_contactfields_by_email('bob@cogwheel.com')
    wa_contact  = get_contact_by_email(email)
    wa_contact  = vars(wa_contact[0])

    for f in wa_contact['FieldValues']:
        #import pdb;pdb.set_trace() # stop and debug
        f = vars(f) # convert from object to dict
        if f['FieldName'] == "NL Signoffs and Categories":
            #pp.pprint(f)
            return(f)

def get_contactfields_by_email(emailAddress):
    params = {'$filter': 'Email eq ' + emailAddress,
              '$async': 'false'}
    request_url = contactsignoffsUrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    response = api.execute_request(request_url)
    return response


def get_all_contacts():
    params = {'$async': 'false'}
    request_url = contactsUrl + '?' + urllib.parse.urlencode(params)
    #print(request_url)
    return api.execute_request(request_url).Contacts

def get_contact_by_email(emailAddress):
    params = {'$filter': 'Email eq ' + emailAddress,
              '$async': 'false'}
    request_url = contactsUrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    response =  api.execute_request(request_url)
    return response.Contacts


def create_member(email, fname, lname, phone, spaceman_id, badge_number):
    data = {
        'Email': email,
        'FirstName': fname,
       'LastName': lname,
        'FieldValues': [
            {
                'FieldName': 'Phone',
                'Value': phone},
            {
                'FieldName': 'Spaceman ID',
                'Value': '' + str(spaceman_id) + ''},
            {
                'FieldName': 'Badge Number',
                'Value': '' + str(badge_number) + ''},
        ],
        'MembershipEnabled': 'true',
        'Status': 'Active',
        "MembershipLevel": {
            "Id": 1207614
        }
    }
    return api.execute_request(contactsUrl, api_request_object=data, method='POST')





def update_member(contact_id, spaceman_id, badge_number,signoffs):
    data = {
        'Id': str(contact_id),
        'FieldValues': [
            {
                'FieldName': 'Spaceman ID',
                'Value': '' + str(spaceman_id) + ''
            },
            {
                'FieldName': 'Badge Number',
                'Value': '' + str(badge_number) + ''
            },
        ],
        'MembershipEnabled': 'true',
        'Status': 'Active',
        "MembershipLevel": {
            "Id": 1207614
        }

    }
    return api.execute_request(contactsUrl + "/" + str(contact_id), api_request_object=data, method='PUT')


def parse_fullname(name_string):
    names = name_string.split(" ", 1)
    firstName = names[0]
    if len(names) > 1:
        lastName = names[1]
    else:
        lastName = ''
    return firstName, lastName


def get_membershiplevels():
    return api.execute_request(account.Url + "/membershiplevels") 


def set_membershiplevel(member_id,new_level_id):
    data = {
        'Id': str(member_id),
        "MembershipLevel": {
            "Id": new_level_id 
        }
    }
    try:
        result = api.execute_request(contactsUrl + "/" + str(member_id), api_request_object=data, method='PUT')
    except:
        p("set_membershiplevel(): member_id:%s,new_level_id:%s: FAIL\n" % (member_id, new_level_id))

def get_field_name(contact_record, field_name):
    # usage x = get_field_name(, 'Primary Member Email')
    for fv in contact_record['FieldValues']:
        fv = vars(fv)
        """
        {"FieldName": "Primary Member ID", "Value": "", "SystemCode": "custom-12487369"},
        {"FieldName": "Primary Member Name", "Value": null, "SystemCode": "custom-12513742"},
        {"FieldName": "Primary Member Email", "Value": null, "SystemCode": "custom-12513743"},
        """
        if fv['FieldName'] == field_name:
            return fv

    return None

def get_field_value(contact_record,field_name):
    fv = get_field_name(contact_record, field_name)
    if (fv == None):
        return ''
    if 'Value' in fv:
        return str(fv['Value'])
    else:
        return ''


def get_field_val_by_system_code(contact_record,system_code):
    # {"FieldName": "_legacy_sponsor_id", "Value": "4", "SystemCode": "custom-12509995"},
    for fv in contact_record['FieldValues']:
        fv = vars(fv)
        if fv['SystemCode'] == system_code:
            return fv
    return ''


def sm_info_collect(sm):
    sm_inf_by_id = {}
    for rec in sm:
        """
        rec:
        OrderedDict([('card_id', ''), ('user_name', 'Aadi'), ('auths', '[equipment]-*GREEN:[equipment]-LC_Rabbit_Laser-Cutter:[novapass]-LC_Hurricane_Laser-Cutter:[equipment]-3D_Printers:[novapass]-LC_Rabbit_Laser-Cutter:[equipment]-LC_Hurricane_Laser-Cutter'), ('username', 'aadi'), ('email_address', '03idaa@gmail.com'), ('person_record_id', '11389'), ('member_type', 'Attendee'), ('posix_uid', '981'), ('created_timestamp', '2017-12-13 20:05:20.816841'), ('sponsor_id', ''), ('joined_date', '2017-12-13'), ('waiver_date', ''), ('safety_date', ''), ('laser_date', ''), ('notes', ''), ('full_member_date', ''), ('member_aspiration', ''), ('meetup_id', ''), ('family_primary_member_id', ''), ('last_login_epoch', '1532831720'), ('phone', '7038701218')])

        ./watool.py --update --mig sponsor --ema bob@cogwheel.com

        """

        inf = {}
        inf['user_name'] = rec['user_name']
        inf['email_address'] = rec['email_address']
        sm_inf_by_id[ rec['person_record_id'] ] = inf
        """
        o = '' 
        o += '%-32.32s' % (rec['email_address'])
        o += '%-32.32s' % (rec['sponsor_id'])
        o += '%-32.32s' % (type(rec['sponsor_id']))
        o += '\n' 
        p(o)
        dbg()
        """

    return sm_inf_by_id 

def update_sponsor_name_and_email(contact_id, sponsor_name,sponsor_email):
    """
    We use this value from spaceman:
       *custom-12509995          "_legacy_sponsor_id"
    To set these values:
       *custom-12606082          "Sponsor Name"
       *custom-12606083          "Sponsor Email"
    """
    data = {
        'Id': str(contact_id),
        'FieldValues': [
            {
                # Sponsor Name
                'SystemCode': 'custom-12606082',
                'Value': sponsor_name, 
            },
        ]
    }
    try:
        result = api.execute_request(contactsUrl + "/" + str(contact_id), api_request_object=data, method='PUT')
    except:
        return False

    data = {
        'Id': str(contact_id),
        'FieldValues': [
            {
                # Sponsor Email
                'SystemCode': 'custom-12606083',
                'Value': sponsor_email, 
            },
        ]
    }
    try:
        result = api.execute_request(contactsUrl + "/" + str(contact_id), api_request_object=data, method='PUT')
    except:
        return False
        

    return True

# -----------------------------------------------
if __name__ == '__main__':

    try:
        # get command line options
        opts,args = getopt.getopt(sys.argv[1:],'',[
            'lvls',
            'mlvls',
            'mfn=',
            'cfs',
            'chk',
            'sos',
            'update',
            'ema=',
            'mig=',
            'fso=',
            'cfav='
            ])

    except getopt.GetoptError as err:
        perr(str(err) +'\n')
        perr(usage_mesg)
        sys.exit(sys.exit_code_fail)

    if len(opts) == 0:
        perr(usage_mesg)             
        sys.exit(sys.exit_code_fail)

    wa_lvls_by_name = {}
    wa_member_id_by_email = {}

    run_update = False
    email_addr  = ''
    for opt,arg in opts:
        if opt == '--update': 
            run_update = True
        if opt == '--ema': 
            email_addr = arg

    for opt,arg in opts:

        if opt == '--lvls':
            # print levels and exit
            wa_levels = get_membershiplevels()
            for lvl in wa_levels:
                wa_lvls_by_name[lvl.Name] = lvl.Id
                print('%d "%s"' %( int(lvl.Id),lvl.Name))
            sys.exit(sys.exit_code_ok)

        if opt == '--mlvls':
            # print members and exit
            wa_contacts = get_all_contacts()
            for cobj in wa_contacts:
                cvars = vars(cobj)
                if 'MembershipLevel' in cvars:
                    print('%d %-32.32s %s' % (cobj.Id,'"'+ cobj.MembershipLevel.Name+'"', cobj.Email))
            sys.exit(sys.exit_code_ok)


        if opt == '--mfn':
            # print members and a particular field name
            """
            print legacy user name
            ./watool.py --mfn '_legacy_username' 
            """
            wa_contacts = get_all_contacts()
            for cto in wa_contacts:
                ctv = vars(cto)
                if 'MembershipLevel' in ctv:
                    for fv in ctv['FieldValues']:
                        if fv.FieldName == arg:
                            print('%d %-32.32s %s' % (ctv['Id'],'"'+ ctv['DisplayName']+'"', fv.Value))

            sys.exit(sys.exit_code_ok)
            
        if opt == '--cfs':
            # print contact fields and exit
            cfs = api.execute_request(contactfieldsUrl, method='GET')
            for cf in cfs:
                o = '' 
                o += '%-16.16s' % (cf.Id)
                o += '  %-32.32s' % ('"' + cf.FieldName + '"')
                if 'AllowedValues' in vars(cf) and len(cf.AllowedValues) != 0:
                    o += ' AV'
                else:
                    o += '   '

                if 'Description' in vars(cf):
                    o += '  "%s"' % (cf.Description)
                o += '\n'
                p(o)
            sys.exit(sys.exit_code_ok)

        if opt == '--cfav':
            # print field allowed values
            cfs = api.execute_request(contactfieldsUrl + '/' + arg, method='GET')
            if len(cfs.AllowedValues):
                for cf in cfs.AllowedValues:
                    o = '' 
                    o += '%-16.16s' % (cf.Id)
                    if cf.Label != None:
                        o += '  %s' % ('"' + cf.Label+ '"')
                    o += '\n'
                    p(o)
            sys.exit(sys.exit_code_ok)

        if opt == '--sos':
            print_all_signoffs()
            sys.exit(sys.exit_code_ok)

        if opt == '--fso':
            wa_contacts = get_all_contacts()
            for cto in wa_contacts:
                ctv = vars(cto)
                if 'MembershipLevel' in ctv:
                    # if they are a member 
                    for fv in ctv['FieldValues']:
                        # look for their signoffs
                        if fv.FieldName == "NL Signoffs and Categories":
                            if fv.Value == None:
                                continue
                            for so in fv.Value:
                                # do they have this particular signoff ?
                                if so.Label == arg:
                                    o = '' 
                                    o += '%-10.10s' % (cto.Id)
                                    o += '  %-32.32s' % ('"' + cto.DisplayName + '"')
                                    o += '%-32.32s' % (cto.Email)
                                    o += '\n' 
                                    p(o)
                            
            
            sys.exit(sys.exit_code_ok)

        if opt == '--chk':
            wa_contacts = get_all_contacts()
            for cobj in wa_contacts:
                v = vars(cob)
                if 'MembershipEnabled' in v:
                    """
                    *family* must be associated with paying members

                      1206421 "Associate (legacy-billing)"
                      1206426 "Key"
                      1207614 "Attendee"
                    * 1208566 "Key (family)"
                      1214364 "Key (legacy-billing)"
                      1214383 "Associate"
                      1214385 "Associate (onboarding)"
                    * 1214629 "Key (family-minor-16-17)"
                    """
                    if (v['MembershipLevel'].Id == 1208566) or \
                       (v['MembershipLevel'].Id == 1214629):   
                        """
                        {"FieldName": "Primary Member ID", "Value": "", "SystemCode": "custom-12487369"},
                        {"FieldName": "Primary Member Name", "Value": null, "SystemCode": "custom-12513742"},
                        {"FieldName": "Primary Member Email", "Value": null, "SystemCode": "custom-12513743"},
                        """
                    
                        """
                        if (get_field_value(v, 'Primary Member Email') == '') or \
                           (get_field_value(v, 'Primary Name') == '') or \
                           (get_field_value(v, 'Primary Member ID') == ''):
                         """
                        if (get_field_value(v, 'Primary Member ID') == ''):
                                o = '' 
                                o += '%-10.10s' % (v['Id'])
                                o += '  %-32.32s' % ('"' + v['DisplayName'] + '"')
                                o += '%-32.32s' % (v['Email'])
                                o += '\n' 
                                p(o)

            sys.exit(sys.exit_code_ok)

        if opt == '--mig':
            # migrate fields from spaceman

            # dry run
            # ./watool.py --mig sponsor --ema bob.coggshall@gmail.com

            # update one person
            # ./watool.py --update --mig sponsor --ema bob.coggshall@gmail.com
            
            # update everyone
            # ./watool.py --update  --mig sponsor 

            #
            #
            # get info from spaceman
            resp = requests.get(os.environ['SPACEMAN_URL'])
            sm = csv.DictReader(resp.text.splitlines())
            sm_inf_by_id = sm_info_collect(sm)
            sm = csv.DictReader(resp.text.splitlines())
            """
            sm_inf_by_id['6434']
            {'user_name': 'Zach Sturgeon', 'email_address': 'me@ke4fox.net'}
            """
            wa_contacts = get_all_contacts() # get wa contact info
            for cobj in wa_contacts:
                cv = vars(cobj)

                if 'MembershipLevel' not in cv:
                    continue

                if email_addr != '' and cv['Email'] != email_addr:
                    # if email option not given OR email option given and not the right one then skip
                    continue

                # {"FieldName": "_legacy_sponsor_id", "Value": "4", "SystemCode": "custom-12509995"},
                #                                                                   ^^^^^^^^^^^^^^
                # find '_legacy_sponsor_id' for this record
                fv = get_field_val_by_system_code(cv, "custom-12509995")
        
                if (fv.get('Value') and 
                    'Value' in fv and fv['Value'] != None and fv['Value'] != ''):
                    o = ''
                    o += '%-16.16s' % (cv['Id'] )
                    o += '%-30.30s' % ('"' + cv['FirstName'] + ' ' + cv['LastName'] + '" ' )
                    o += '%-30.30s' % (cv['Email'] + ' ')
                    if sm_inf_by_id.get( fv['Value'] ) != None:
                        o += '%-30.30s' % ('"' + sm_inf_by_id[ fv['Value'] ]['user_name'] + '"' )
                        o += '%-30.30s' % (sm_inf_by_id[ fv['Value'] ]['email_address'] )
                    else:
                        o += '%-30.30s' % ('')
                        o += '%-30.30s' % ('')
                        

                    if run_update and sm_inf_by_id.get( fv['Value'] ) != None:

                        if update_sponsor_name_and_email( 
                            cv['Id'],
                            sm_inf_by_id[ fv['Value'] ]['user_name'],
                            sm_inf_by_id[ fv['Value'] ]['email_address'] ):
                            o += ' OK' 
                        else:
                            o += ' FAIL' 

                    o += '\n' 
                    p(o)


                    sys.stdout.flush()

            sys.exit(sys.exit_code_ok)
                
    perr(usage_mesg)             
    sys.exit(sys.exit_code_fail)
                    
    
