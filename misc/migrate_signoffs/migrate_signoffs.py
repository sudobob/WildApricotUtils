#!/usr/bin/env python3
"""

migrate_signoffs.py

Copies nova-labs signoffs from spaceman to wild apricot

adapted from spaceman2apricot.py by https://github.com/azagh

"""
import argparse
import datetime
import pandas as pd
import numpy as np
import os
import sys
import traceback
import urllib.parse
import signoffs
from dotenv import load_dotenv
from WaApi import WaApiClient
import pprint
pp = pprint.PrettyPrinter(stream=sys.stdout,indent=4)
import time

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
        soc.append({'Id': int(signoffs_ids_by_name[sos]),
                    'Label': sos})
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



if __name__ == '__main__':
    # Make a dictionary of WA contacts using the spaceman person record id as the key
    # Use this key to sync the two databases
    wa_id_dictionary = {}
    wa_email_dictionary = {}
    contacts = get_all_contacts()
    for contact in contacts:
        wa_email_dictionary[contact.Email] = contact
        for value in contact.FieldValues:
            if value.FieldName == "Spaceman ID":
                wa_id_dictionary[value.Value] = contact
    
    # Make sure we got a list of contacts from WA.  If the length is zero
    # something bad happened and we shouldn't try to repopulate the entire db
    if(len(contacts) < 1):
        print("No WA contacts found; exiting")
        sys.exit()

    # Read in all the users from the legacy system Spaceman
    spacemanDump = pd.read_csv(os.getenv("SPACEMAN_URL"))
    
    # loop through the spaceman rows
    for sm_row in spacemanDump.itertuples(index = True, name ='Pandas'):

        # Skip Attendees for now
        if getattr(sm_row, "member_type") == "Attendee":
            continue

        # determine this user's signoffs
        found_signoffs = signoffs.process(getattr(sm_row,"auths"))
    

        # get their spaceman record
        sm_record_id = str(getattr(sm_row, "person_record_id"))

        # if they have an entry wa.. 
        if sm_record_id in wa_id_dictionary:
            spacemanId   = getattr(sm_row, "person_record_id")
            emailAddress = getattr(sm_row, "email_address").lower().rstrip('.').strip()
            badgeNumber  = getattr(sm_row, "card_id")

            get_contacts_signoffs_by_email(emailAddress)

            # get all possible contact fields and their ID
            contactfields  = get_contactfields_by_email(emailAddress)
            signoffs_ids_by_name = {}
            for cf in contactfields.AllowedValues:
                cfs = vars(cf)
                signoffs_ids_by_name[ cfs['Label'] ] = cfs['Value']

            
            sys.stdout.write(datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"))
            sys.stdout.write(f' Updating member: email:[{emailAddress}] spaceman_id:[{spacemanId}] badge_number:[{badgeNumber}] ')
            sys.stdout.write('signoffs:(')
            for s in found_signoffs:
                sys.stdout.write(s)
            sys.stdout.write(')\n')

            updated_member = update_signoffs(wa_email_dictionary[emailAddress].Id,found_signoffs,signoffs_ids_by_name)
            time.sleep(.25) # make sure we don't step over the max rate limit


