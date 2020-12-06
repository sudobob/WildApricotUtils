#!/usr/bin/env python3
"""

"""

usage= """

"""

import os
import sys
from dotenv import load_dotenv
from WaApi import WaApiClient
from prettyprinter import pprint
import getopt
import urllib

sys.exit_code_fail = 1
sys.exit_code_ok   = 0

load_dotenv(override=True)

# Connect to WA and get all the contacts from WA

api                = WaApiClient(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
api.authenticate_with_apikey(os.getenv("API_KEY"))

accounts           = api.execute_request("/accounts")
account            = accounts[0]
contactsUrl        = account.Url + '/Contacts'
contactfieldsUrl   = account.Url + '/contactfields'
contactsignoffsUrl = contactfieldsUrl + '/12472413'

def pp(v):
    pprint(v)

load_dotenv(override=True)
# Connect to WA and get all the contacts from WA

api                = WaApiClient(os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
api.authenticate_with_apikey(os.getenv("API_KEY"))

accounts           = api.execute_request("/accounts")
account            = accounts[0]
contactsUrl        = account.Url + '/Contacts'
contactfieldsUrl   = account.Url + '/contactfields'
contactsignoffsUrl = contactfieldsUrl + '/12472413'


def get_contact_by_email(emailAddress):
    params = {'$filter': 'Email eq ' + emailAddress,
              '$async': 'false'}
    request_url = contactsUrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    response =  api.execute_request(request_url)
    return response.Contacts

def get_contact_by_foo(foo):
    params = {'$filter': "'Badge Number' eq 15130472",
              '$async': 'false'}
    request_url = contactsUrl + '?' + urllib.parse.urlencode(params)
    print(request_url)
    response =  api.execute_request(request_url)
    return response.Contacts


if __name__ == '__main__':

    rq = get_contact_by_foo('')
    pp(rq)
    import pdb;pdb.set_trace()

