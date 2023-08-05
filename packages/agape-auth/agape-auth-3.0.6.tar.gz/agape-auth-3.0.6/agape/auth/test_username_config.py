from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
import json
from django.utils import timezone
from datetime import timedelta

# Create your tests here.
from .models import User, UserManager, UserActivation, ResetPasswordRequest
from .serializers import UserSerializer

from .settings import AUTH, defaults as AUTH_DEFAULTS

from agape.auth import username_opt, username_value, username_field
AUTH['USERNAME_FIELD']="username"

import copy
from agape.test import AgapeTests, ApiMixin, ApiTests, ModelTests, SerializerTests, TestCaseMixin
from django.conf import settings



from .test_default import USER_MODEL, USER_SERIALIZER, USER_ENTITY_NAME, USER_API_END_POINT

USER_ENTITY_NAME = 'user'
USER_API_END_POINT = '/api/users/'
AUTH_API_END_POINT = '/api/auth/'
REGISTER_API_END_POINT = "/api/register"
RECOVERY_API_END_POINT = "/api/auth/recovery/"

USER_CREATE_DATA = [

    {
        'username': 'ajones',
        'password': 'testpass',
        'email': 'testing@example.com'
    },
    {
        'username': 'jsmith',
        'password': 'foobar12',

    }
]


USER_UPDATE_DATA = [
    
    {
        'username': 'achandler'
    },
    {
        'password': 'barfood12'
    }

]

class UserTestMixin( TestCaseMixin ):

    def sharedSetUp(self):
        self.resetSettings()

        self.model              = USER_MODEL
        self.serializer_class   = USER_SERIALIZER
        self.entity             = USER_ENTITY_NAME
        self.api_end_point      = USER_API_END_POINT
        self.auth_end_point     = AUTH_API_END_POINT
        self.register_end_point = REGISTER_API_END_POINT
        self.recovery_end_point = RECOVERY_API_END_POINT

        self.create_data        = copy.deepcopy(USER_CREATE_DATA)
        self.expect_data        = copy.deepcopy(USER_CREATE_DATA)
        for record in self.expect_data:
            record.pop('password')
            
        self.update_data        = copy.deepcopy(USER_UPDATE_DATA)
        self.update_expect_data = copy.deepcopy(USER_UPDATE_DATA)
        for record in self.update_expect_data:
            record.pop('password', None)

    def resetSettings(self):
        # reset configuration to default settings
        for key, value in AUTH_DEFAULTS.items():
            AUTH[key] = AUTH.get(key, AUTH_DEFAULTS[key] )

    def register_user( self, data ):
        response = self.client.post( self.register_end_point, data )
        self.assertEqual(response.status_code, 201, "Registered user")
        return response


class ModelTestCase( UserTestMixin, ModelTests, TestCase ):
    pass

class ModelSerializerCase( UserTestMixin, SerializerTests, TestCase ):
    pass



class APITestCase(UserTestMixin, ApiMixin, AgapeTests, TestCase):

    def setUp(self):
        self.sharedSetUp()
        self.createRequisiteObjects();
        self.serializedSetUp()
        self.maxDiff = None
        self.client =  APIClient()

    def test_user_registration(self):

        i=0
        while i < len(self.serialized_create_data):

            cdata = self.create_data[i]
            response = self.register_user( cdata )
            self.assertEqual( response.status_code, 201, "Registered new user")

            # verify the response data
            self.assertSerializedInstanceEqual( response.data, self.serialized_expect_data[i] )

            self.assertEqual( response.data['username'], cdata['username'] )

            # verify actual database record was created
            instance = self.model.objects.get(id=response.data.get('id'))
            self.assertTrue(instance)

            i+=1

    def test_login(self):

        cdata = self.create_data[0]
        instance = self.model.objects.create( **cdata, status=1 )

        # login
        response = self.authenticate( username=cdata['username'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")
        self.assertTrue(response.data.get('token'), "Received auth token.")


    def test_login_with_email(self):

        cdata = self.create_data[0]

        instance = self.model.objects.create( **cdata, status=1 )

        # login
        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")
        self.assertTrue(response.data.get('token'), "Received auth token.")


    def test_login_with_email_as_username(self):


        cdata = self.create_data[0]

        instance = self.model.objects.create( **cdata, status=1 )

        # login
        response = self.authenticate( username=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")
        self.assertTrue(response.data.get('token'), "Received auth token.")
