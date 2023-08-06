

# This file contains the default settings for the application. First we look in the 
# global application settings.py file for any settings that are defined there. Then
# we set any default values.

# To use these settings, you must:
# from .settings import AUTH

# If you instead defer to the settings.py file, you will not have the default values
# which are defined in this file.

from django.conf import settings


defaults = {
    # TODO: Change require activation to False
    'REQUIRE_ACTIVATION': True,
    'RESET_PASSWORD_EXPIRES': 20,
    'REQUIRE_PASSWORD_ON_ACCOUNT_MODIFICATIONS': True,
    'USERNAME_FIELD': 'email',
    'LOGIN_WITH_FIELDS': ['email'],
    'LOGIN_WITH_PARAM': 'username',
    'EMAIL_REQUIRED': True,
    'REQUIRED_FIELDS': [],

    'RESET_PASSWORD_REQUEST_ALWAYS_OK': True,

    # TODO: Implement open registration
    'OPEN_REGISTRATION': True,

    'FROM_EMAIL_ADDRESS': 'admin'
}


# get the section from the app settings.py file
AUTH = getattr(settings, 'AUTH', {})

# set the defaults defined above
for key, value in defaults.items():
    AUTH[key] = AUTH.get(key, defaults[key] )

# modify the "LOGIN_WITH_FIELDS" array to always include the USERNAME_FIELD
if not AUTH['USERNAME_FIELD'] in AUTH['LOGIN_WITH_FIELDS']:
    AUTH['LOGIN_WITH_FIELDS'] = AUTH['LOGIN_WITH_FIELDS'].insert(0, AUTH['USERNAME_FIELD'] )

