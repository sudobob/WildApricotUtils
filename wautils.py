#!/usr/bin/env python3

"""

wautils 

    A set of web-based tools for Wild Apricot Integration  
    
    o Accepts your Wild Apricot Credentials via Wild Apricot OAuth
    o Determines if you are have Wild Apricot admin credentials
    o Give you further access only if you have admin credentials

"""

usage_mesg = """

usage:

    wautils [--debug]

        Start up wautils web server


"""
from flask import Flask, redirect, url_for, render_template, flash, g, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_bootstrap import Bootstrap
from flask_restful import Resource as FlaskRestResource
from flask_restful import reqparse as FlaskRestReqparse
from flask_restful import Api as FlaskRestAPI
from flask_restful import request as FlaskRestRequest

import WaApi
import urllib
import os,sys,requests
from dotenv import load_dotenv
from oauth import OAuthSignIn
import getopt
import json

# for debugging
import pprint

ex_code_fail    = 1 # used with sys.exit()
ex_code_success = 0

# get keys and config info from .env 
load_dotenv() 

wa_uri_prefix          = "https://api.wildapricot.org/v2.1/"
wa_uri_prefix_accounts = wa_uri_prefix + "Accounts/"


app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' 

app.config['OAUTH_CREDENTIALS'] = {
    'wildapricot' : {
        'account'     : os.environ['WA_ACCOUNT'],
        'id'          : os.environ['OAUTH_ID'],
        'api_key'     : os.environ['OAUTH_API_KEY'],
        'secret'      : os.environ['OAUTH_SECRET']
    }
}

# rest api support
restapi = FlaskRestAPI(app) 

# bootstrap framework support
Bootstrap(app)

# allow cross-site origin
CORS(app)

# tell bootstrap NOT to fetch from CDNs
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# login manager setup
lm            = LoginManager(app)
lm.login_view = 'utils'


# database setup
db = SQLAlchemy(app)

# for debugging
pp = pprint.PrettyPrinter(stream=sys.stderr)


def wapi_init():
    # setup the WA API
    creds    = app.config['OAUTH_CREDENTIALS']['wildapricot']
    wapi     = WaApi.WaApiClient(creds['id'],creds['secret'])
    wapi.authenticate_with_apikey(creds['api_key'])
    return wapi,creds



class User(UserMixin, db.Model):
    # define table entry in db for logged-in user
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(64), nullable = False)
    last_name  = db.Column(db.String(64), nullable = False)
    email      = db.Column(db.String(64), nullable = True)


@lm.user_loader
def load_user(id):
    # required by flask_login
    return User.query.get(int(id))


@app.route('/')
def index():
    # browse to /
    if current_user.is_anonymous:
        # users not logged in get NONE !
        flash('You are not logged in','warning')
    else:
        # user is logged in. 
        flash('Hi, ' +  current_user.first_name + ' !','success')
        # retrieve users credentials
        wapi,creds = wapi_init()

        global g  # things in g object can be accessed in jinja templates
        g.wa_accounts_contact_me = wapi.execute_request(
                wa_uri_prefix_accounts + creds['account'] + "/contacts/" + str(current_user.id))

        if g.wa_accounts_contact_me.IsAccountAdministrator:
            # if they are a WA admin congratulate them
            flash("Congrats ! You are a Wild Apricot Account Administrator",'success')

    return render_template('index.html')

@app.route('/signoffs')
@login_required
def signoffs():
    wapi,creds = wapi_init()

    global g  
    # things in g object can be accessed in jinja templates
    g.wa_accounts_contact_me = wapi.execute_request(
                wa_uri_prefix_accounts + creds['account'] + "/contacts/" + str(current_user.id))


    # render signoff html. 
    # see templates/signoff.html to see what happens
    return render_template('signoffs.html')



@app.route('/utils')
@login_required
def utils():
    # retrieve users credentials
    wapi,creds = wapi_init()

    global g  # things in g object can be accessed in jinja templates
    g.wa_accounts_contact_me = wapi.execute_request(
            wa_uri_prefix_accounts + creds['account'] + "/contacts/" + str(current_user.id))

    if g.wa_accounts_contact_me.IsAccountAdministrator:
        flash("Congrats ! You are a Wild Apricot Account Administrator",'success')

    return render_template('utils.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    # oauth calls us once we've been granted a token
    # from oauth provider
    if not current_user.is_anonymous:
        # not logged in
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    
    me  = oauth.callback()

    '''
    oauth.callback() returns:

    {
    'FirstName'              : 'John',
    'LastName'               : 'Bigbooty',
    'Email'                  : 'john.bigbooty@gmail.com',
    'DisplayName'            : 'Bigbooty, John',
    'Organization'           : 'Yoyodyne',
    'MembershipLevel'        : 
       {
        'Id'                     : 5059174,
        'Url'                    : 'https://api.wildapricot.org/v2/accounts/123456/MembershipLevels/1059174',
        'Name'                   : 'Key (Legacy)'
       },
    'Status'                 : 'Active',
    'Id'                     : 90534910,
    'Url'                    : 'https://api.wildapricot.org/v2/accounts/123456/Contacts/50534910',
    'IsAccountAdministrator' : True,
    'TermsOfUseAccepted'     : True
    }
    '''


    if not('Email' in me):
        flash("ERROR oauth_callback(): " + me['Message'],'error')
        return redirect(url_for('index')) 

    # is this user in the DB ?
    user = User.query.filter_by(email=me['Email']).first()
    if not user:
       # if not, add them
       user = User(
               first_name = me['FirstName'],
               last_name  = me['LastName'],
               email      = me['Email'],
               id         = me['Id']
               )
       db.session.add(user)
       db.session.commit()

    # officially login them into flask_login system
    login_user(user, True)
    return redirect(url_for('index'))

def wa_get_contacts():
    # get WA contacts
    # returns them formatted on screen
    # for testing only
    wapi,creds = wapi_init()
    response =   wapi.execute_request_raw(wa_uri_prefix_accounts + 
                 creds['account'] + 
                 "/contacts/?$async=false")

    wa_accounts_contact_me = wapi.execute_request(
            wa_uri_prefix_accounts + creds['account'] + "/contacts/" + str(current_user.id))

    return('<pre>' + json.dumps(
        response.read().decode(),
        indent=4,sort_keys=True
        ) + '</pre>')

################################################################################
# REST API STUFF
###
class WAGetAnyEndpointREST(FlaskRestResource):
    """
    REST API for our js in the browser to call us on
    """
    def get(self):
        return wa_get_any_endpoint_rest()

restapi.add_resource(WAGetAnyEndpointREST,'/api/v1/wa_get_any_endpoint')


def wa_get_any_endpoint_rest():
    """
    respond passed endpoint up to WA, return response to requestor
    """
    pp.pprint('------wa_get_any_endpoint_rest()--------')
    rp = FlaskRestReqparse.RequestParser()

    rp.add_argument('endpoint',type=str)
    rp.add_argument('$asyncfalse',type=str)
    args = rp.parse_args()
  
    wapi,creds = wapi_init()


    # typical raw queries
    # '/accounts/accountid/contacts?$async=false'


    ep = args['endpoint'].replace('$accountid', creds['account'])


    wa_accounts_contact_me = wapi.execute_request(
            wa_uri_prefix_accounts + creds['account'] + "/contacts/" + str(current_user.id))

    if wa_accounts_contact_me.IsAccountAdministrator:
        pp.pprint(ep)
        try:
            response =   wapi.execute_request_raw(wa_uri_prefix +  ep)

        except urllib.error.HTTPError as e:
            return {"error":1,"error_message": ep + ':' + str(e) }

        except WaApi.ApiException as e:
            return {"error":1,"error_message": ep + ':' + str(e) }


        decoded = json.loads(response.read().decode())
        result = []
        if isinstance(decoded, list):
            for item in decoded:
                result.append(item)
        elif isinstance(decoded, dict):
                result.append(decoded)

        pp.pprint(f'------END wa_get_any_endpoint_rest() ({ep})--------')
        return result
    else:
        return {"error":1,"error_message":"You are not a WA account admin"}
###
class WAPutAnyEndpointREST(FlaskRestResource):
    """
    REST API for our js in the browser to call us on
    """
    def put(self):
        return wa_put_any_endpoint_rest()

restapi.add_resource(WAPutAnyEndpointREST,'/api/v1/wa_put_any_endpoint')

def wa_put_any_endpoint_rest():
    """
    send PUT endpoint rq up to WA, return response to requestor
    """
    rp = FlaskRestReqparse.RequestParser()

    wapi,creds = wapi_init()


    rq = FlaskRestRequest.json
    ep = rq['endpoint']
    pd  = rq['put_data']

    ep = ep.replace('$accountid', creds['account'])

    wa_accounts_contact_me = wapi.execute_request(
            wa_uri_prefix_accounts + creds['account'] + "/contacts/" + str(current_user.id))

    if wa_accounts_contact_me.IsAccountAdministrator:

        try:
            response =   wapi.execute_request_raw(wa_uri_prefix +  ep, data=pd, method="PUT")

        except urllib.error.HTTPError as e:
            return {"error":1,"error_message": ep + ':' + str(e) }

        except WaApi.ApiException as e:
            return {"error":1,"error_message": ep + ':' + str(e) }


        decoded = json.loads(response.read().decode())

        result = []

        if isinstance(decoded, list):
            for item in decoded:
                result.append(item)
        elif isinstance(decoded, dict):
                result.append(decoded)

        return result
    else:
        return {"error":1,"error_message":"You are not a WA account admin"}

def run_app():
  db.create_all()
  app.run(port=7000,debug=False)
            
################################################################################
# Execution starts here
if __name__ == '__main__':


  # parse cmd line args and perform operations
  try:
    # parse cmd line args
    ops,args = getopt.getopt(sys.argv[1:],"c:",["webserver","cmd="])
  except getopt.GetoptError as err:
    sys.stderr.write(str(err) + '\n')
    sys.stderr.write(usage_mesg)
    sys.exit(ex_code_fail)
    
  for o,a in ops:

    if (o == '--debug'):
      db.create_all()
      app.run(port=8080,debug=True)

    if (o == '--cmd' or o == '-c'):
      cmd = a
      wapi,creds = wapi_init()
      response =   wapi.execute_request_raw(wa_uri_prefix_accounts + 
                   creds['account'] + 

                   "/contacts/?$async=false")

      sys.stderr.write(json.dumps( response.read().decode(), indent=4,sort_keys=True))

      """
      wapi,creds = wapi_init()
      response =   wapi.execute_request_raw("https://api.wildapricot.org/v2.1/",  method="GET")
      """
      sys.exit(ex_code_success)

  # run production on local port that apache proxy's to

  sys.stderr.write("Starting web server\n")
  db.create_all()
  app.run(port=7000,debug=False)

  # no options given. print usage and exit
  sys.stderr.write(usage_mesg)
  sys.exit(ex_code_fail)




