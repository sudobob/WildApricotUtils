#!/usr/bin/env python3
usage_mesg= """

Options

    --lvls              : print member levels and exit
    --mlvls             : print members and their level and exit
    --cfs               : print contact fields and exit
    --cfav field_id     : print field allowed values
    --chk               : perform consistency check and report
    --sos               : print signoffs
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

    What it a they look like in a get

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
                sys.stdout.write(o)


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
        sys.stdout.write("set_membershiplevel(): member_id:%s,new_level_id:%s: FAIL\n" % (member_id, new_level_id))

def get_field_name(contact_record, field_name):
    # usaage x = get_field_name(, 'Primary Member Email')
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

if __name__ == '__main__':


    try:
        opts,args = getopt.getopt(sys.argv[1:],'',[
            'lvls',
            'mlvls',
            'cfs',
            'chk',
            'sos',
            'fso=',
            'cfav='
            ])

    except getopt.GetoptError as err:
        sys.stdout.write(str(err) +'\n')
        sys.stdout.write(usage_mesg)
        sys.exit(sys.exit_code_fail)

    if len(opts) == 0:
        sys.stdout.write(usage_mesg)             
        sys.exit(sys.exit_code_fail)

    wa_lvls_by_name = {}
    wa_member_id_by_email = {}
    
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


        if opt == '--cfs':
            cfs = api.execute_request(contactfieldsUrl, method='GET')
            for cf in cfs:
                o = '' 
                o += '%-16.16s' % (cf.Id)
                o += '  %-32.32s' % ('"' + cf.FieldName + '"')
                if 'Description' in vars(cf):
                    o += '  %s' % (cf.Description)
                o += '\n'
                sys.stdout.write(o)
            sys.exit(sys.exit_code_ok)

        if opt == '--cfav':

            cfs = api.execute_request(contactfieldsUrl + '/' + arg, method='GET')
            for cf in cfs.AllowedValues:
                o = '' 
                o += '%-16.16s' % (cf.Id)
                o += '  %s' % ('"' + cf.Label+ '"')
                o += '\n'
                sys.stdout.write(o)
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
                                    sys.stdout.write(o)
                            
            
            sys.exit(sys.exit_code_ok)

        if opt == '--chk':
            wa_contacts = get_all_contacts()
            for cobj in wa_contacts:
                v = vars(cobj)
                """
                1206421 "Associate (legacy-billing)"
                1206426 "Key"
                1207614 "Attendee"
                1208566 "Key (family)"
                1214364 "Key (legacy-billing)"
                1214383 "Associate"
                1214385 "Associate (onboarding)"
                1214629 "Key (family-minor-16-17)"
                """
                if 'MembershipEnabled' in v:
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
                                sys.stdout.write(o)

            sys.exit(sys.exit_code_ok)
                
    sys.stdout.write(usage_mesg)             
    sys.exit(sys.exit_code_fail)
                    
    
