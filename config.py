import os
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

def load_config(mode:str):
    if mode == 'PRODUCTION':
        print("PRODUCTION MODE ACTIVATED")
        oauth_register = OAuth2Session("GoUtPaQPdHOMDRVgh4DDXRjXKDOh0DCcSR084oVG",
                      redirect_uri='https://thelocker.io/register/ion',
                      scope=["read","write"])

        oauth_login = OAuth2Session("9aREwccz0FMYNx94QJl8SlUd6usCw1LeCWdnh824",
                            redirect_uri='https://thelocker.io/login/ion',
                            scope=["read","write"])
        return oauth_register, oauth_login
    elif mode == 'DEBUG':
        print("DEBUG MODE ACTIVATED")
        oauth_register = OAuth2Session("wpHYY2aXgZdm68bFj3h8QlG9mWPvb0Wwqvo2qPZF",
                      redirect_uri='http://127.0.0.1:5000/register/ion',
                      scope=["read","write"])

        oauth_login = OAuth2Session("EDdTDiVb8gTQ34WGScGELsppMjI8S8w8MsSCphWu",
                            redirect_uri='http://127.0.0.1:5000/login/ion',
                            scope=["read","write"])
        load_dotenv(".env")

        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        return oauth_register, oauth_login
