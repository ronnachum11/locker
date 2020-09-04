import os
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

def load_config():
    # if mode == 'PRODUCTION':
    #     print("PRODUCTION MODE ACTIVATED")
    #     oauth_register = OAuth2Session(os.environ['REGISTER_CLIENT_ID'],
    #                   redirect_uri='https://thelocker.io/register/ion',
    #                   scope=["read","write"])

    #     oauth_login = OAuth2Session(os.environ['LOGIN_CLIENT_ID'],
    #                         redirect_uri='https://thelocker.io/login/ion',
    #                         scope=["read","write"])
    #     return oauth_register, oauth_login
    # elif mode == 'DEBUG':
    if os.path.exists("debug.env"):
        print("DEBUG MODE ACTIVATED")

        load_dotenv("debug.env")

        oauth_login = OAuth2Session(os.environ['LOGIN_CLIENT_ID'],
                            redirect_uri='http://127.0.0.1:5000/ion',
                            scope=["read","write"])

        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        return oauth_login
    else:

        oauth_login = OAuth2Session(os.environ['LOGIN_CLIENT_ID'],
                            redirect_uri='https://thelocker.io/ion',
                            scope=["read","write"])
        return oauth_login