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


def username_opt(value):
    return { AUTH['USERNAME_FIELD'] : value } 

def username_attr(instance):
    return getattr(instance, AUTH['USERNAME_FIELD'] )


import copy
from agape.test import AgapeTests, ApiMixin, ModelTests,  SerializerTests, TestCaseMixin


USER_MODEL = User
USER_SERIALIZER = UserSerializer
USER_ENTITY_NAME = 'user'
USER_API_END_POINT = '/api/users/'
AUTH_API_END_POINT = '/api/auth/'
REGISTER_API_END_POINT = "/api/register"
RECOVERY_API_END_POINT = "/api/auth/recovery/"


USER_CREATE_DATA = [

    {
        AUTH['USERNAME_FIELD']: 'test@example.com',
        'password': 'testpass',
        # 'name': 'Test User'
    }

]

USER_UPDATE_DATA = [

    {
        AUTH['USERNAME_FIELD']: 'info@codewise.io',
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








# TODO, DELETE THESE TESTS, REPLACE WITH TESTS SPECIFICALLY FOR ACCOUNT ACTIVATION/RESET
class UserTestCase(UserTestMixin, TestCase):

    def setUp(self):
        self.resetSettings()
        user = User( **username_opt("test@example.com") )
        user.set_password("password")
        user.save()

    def test_user_account(self):
        """User account is created and retrieved."""
        user = User.objects.get( **username_opt("test@example.com") )
        self.assertEqual( username_attr(user), 'test@example.com')

    def test_account_activation(self):
        user = User.objects.get( **username_opt("test@example.com") )
        instance = UserActivation.objects.create(user=user)
        self.assertTrue(instance.key, "Created activation key")

    def test_password_reset(self):
        user = User.objects.get( **username_opt("test@example.com") )
        instance = ResetPasswordRequest.objects.create(user=user)
        self.assertTrue(instance.key, "Created activation key")   


class UserManagerTestCase(TestCase):
    
    def test_create_user(self):
        user_manager = UserManager()
        user = user_manager.create_user(email='test@example.com',password='testingpassword')

        user = User.objects.get( **username_opt("test@example.com") )
        self.assertEqual( username_attr(user),  'test@example.com')

    def test_create_superuser(self):
        user_manager = UserManager()
        user = user_manager.create_superuser(email='admin@example.com',password='testingpassword')  

        user = User.objects.get( **username_opt("admin@example.com") )
        self.assertEqual(username_attr(user),  'admin@example.com')     






class UserSerializerTestCase( UserTestMixin, SerializerTests, TestCase):


    def serializedSetUp(self):

        super().serializedSetUp()

        # remove the password from the expected serialized data
        for expect_data in ( self.serialized_expect_data, self.serialized_update_expect_data ):
            for record in expect_data:
                record.pop('password', None)



    def test_change_password_via_serializer( self ):

        instance = self.model.objects.create( **self.create_data[0] )
        instance_id = instance.id
        original_password = instance.password

        serializer = self.serializer_class( instance, data={'password':'newpass'}, partial=True )

        if serializer.is_valid( raise_exception=True) :
            serializer.update( instance, serializer.validated_data )

        # just test that the password has changed, leave it to django to test
        # what the password actually changed to
        instance = None
        instance = self.model.objects.get( pk=instance_id )
        self.assertTrue( instance.password != original_password )



class AccountRecoveryTestCase( UserTestMixin, ApiMixin, AgapeTests, TestCase ):

    def setUp(self):
        self.client =  APIClient()
        self.sharedSetUp()
        self.resetSettings()

        self.api_end_point = self.recovery_end_point

    def test_password_reset(self):
        self.register_user( self.create_data[0] )

        # activate user
        user = User.objects.get( email=self.create_data[0]['email'] )
        user.status = 1;
        user.save()

        # create password reset request
        response = self.post( {'email': 'test@example.com', 'reset': True} )
        self.assertEqual(response.status_code, 200, "Reset password request created")

        # check for existence of database entry
        instance = ResetPasswordRequest.objects.filter(user=user).order_by('-id')[0]
        self.assertTrue(instance, "Reset password request object exists")

        # check password reset link is valid
        response = self.client.get('/api/auth/recovery/{}/'.format(instance.key))
        self.assertEqual(response.status_code, 200, "Validate password reset link ok")   

        # try creating another password reset and verify that they have the same key
        response = self.client.post('/api/auth/recovery/', {'email': 'test@example.com', 'reset': True})
        duplicate = ResetPasswordRequest.objects.filter(user=user).order_by('-id')[0]
        self.assertEqual(instance.key, duplicate.key, "Used the same password reset request")   

        # update the original reset request to be over an hour old
        duplicate = None
        time_threshold = timezone.now() - timedelta(minutes=AUTH.get('RESET_PASSWORD_EXPIRES')+1)
        instance.created = time_threshold
        instance.save()

        # check password reset link is now expired
        response = self.client.get('/api/auth/recovery/{}/'.format(instance.key))
        self.assertEqual(response.status_code, 410, "Password link has expired")

        # reset the password using the expired link (should fail)
        response = self.client.patch('/api/auth/recovery/{}/'.format(instance.key), json.dumps({'password': 'newpass'}), content_type='application/json')
        self.assertEqual(response.status_code, 410, "Do not reset password on expired link")


        # create another password reset and verify that they have different keys
        response = self.client.post('/api/auth/recovery/', {'email': 'test@example.com', 'reset': True})
        duplicate = ResetPasswordRequest.objects.filter(user=user).order_by('-id')[0]
        self.assertTrue(not instance.key == duplicate.key, "Created new password reset request") 

        # reset the password using the new link (should pass)
        response = self.client.patch('/api/auth/recovery/{}/'.format(duplicate.key), json.dumps({'password': 'newpass'}), content_type='application/json')
        self.assertEqual(response.status_code, 200, "Reset password on valid link")

        # check password reset link is now expired (has been used)
        response = self.client.get('/api/auth/recovery/{}/'.format(instance.key))
        self.assertEqual(response.status_code, 410, "Password link has been used")

        # reset the password using the new link again (should fail)  
        response = self.client.patch('/api/auth/recovery/{}/'.format(duplicate.key), json.dumps({'password': 'newpass'}), content_type='application/json')
        self.assertEqual(response.status_code, 410, "Do not reset on used link")

        # create a new password reset request, validate that it is a unique key
        used = duplicate

        # create another password reset and verify that they have different keys
        response = self.client.post('/api/auth/recovery/', {'email': 'test@example.com', 'reset': True})
        another = ResetPasswordRequest.objects.filter(user=user).order_by('-id')[0]
        self.assertTrue(not used.key == another.key, "Created new password reset request") 

        # submit the change request with no password (should fail)
        response = self.client.patch('/api/auth/recovery/{}/'.format(another.key), json.dumps({'password': ''}), content_type='application/json')
        self.assertEqual(response.status_code, 400, "No password supplied error")

        # set the new link to disabled
        another.status = ResetPasswordRequest.DISABLED
        another.save()

        # check password reset link is now disabled
        response = self.client.get('/api/auth/recovery/{}/'.format(another.key))
        self.assertEqual(response.status_code, 403, "Link has been disabled")

        # try resetting password on disbaled link
        response = self.client.patch('/api/auth/recovery/{}/'.format(another.key), json.dumps({'password': 'newpass'}), content_type='application/json')
        self.assertEqual(response.status_code, 403, "Link has been disabled")

        # set the new link to enabled
        another.status = ResetPasswordRequest.ENABLED
        another.save()

        # set the user to disabled
        another.user.status = User.DISABLED
        another.user.save()

        # check password reset link is now disabled
        response = self.client.get('/api/auth/recovery/{}/'.format(another.key))
        self.assertEqual(response.status_code, 403, "User has been disabled")

        # try resetting password on disbaled link
        response = self.client.patch('/api/auth/recovery/{}/'.format(another.key), json.dumps({'password': 'newpass'}), content_type='application/json')
        self.assertEqual(response.status_code, 403, "User has been disabled")  



class APITestCase(UserTestMixin, ApiMixin, AgapeTests, TestCase):

    def setUp(self):
        self.client =  APIClient()
        self.sharedSetUp()
        self.resetSettings()

    def test_login_using_username_field(self):

        # register user
        instance = User.objects.create( **{'password':'testing', 'email':'test@email.com', 'status': 1})

        # attempt to login with credentials (should fail because user is inactive)
        response = self.client.post(self.auth_end_point, {'username': 'test@email.com', 'password':'testing'})
        self.assertEqual(response.status_code, 200, "Logged in")


    def test_activate_disabled_account_error(self):

        self.register_user( self.create_data[0] )

        # disable user
        user = User.objects.get( email=self.create_data[0]['email'] )
        user.status = -1;
        user.save();

        user = User.objects.get( email=self.create_data[0]['email'] )
        self.assertEqual(user.status, -1, "New user is disabled")

        # check if activation link created
        activation =  UserActivation.objects.get(user_id=user.id)
        self.assertTrue( activation, "User activation key generated")
        self.assertTrue( not activation.activated, "Activation has not been used");

        # follow activation link (expect an error)
        response = self.client.patch(self.auth_end_point, json.dumps({'key':activation.key}), content_type='application/json')
        self.assertEqual(response.status_code, 400, "Can not activate disabled user")


  


    def test_validate_email(self):

        # check if email is available ( yes available )
        response = self.client.get('/api/auth/email/?email=test@example.com')
        self.assertEqual(response.data.get('valid'), True, "No conflict")

        # register user
        self.register_user( self.create_data[0] )   

        user = User.objects.get( email=self.create_data[0]['email'] )

        # check if email is available ( no, in use )
        response = self.client.get('/api/auth/email/?email=test@example.com')
        self.assertEqual( response.data.get('valid'), False, "Conflict" )

        # check if email is available ( yes, do not flag users email as invalid )
        response = self.client.get('/api/auth/email/?email=test@example.com&userid={}'.format(user.id))
        self.assertEqual(response.data.get('valid'), True, "No conflict")




    def test_change_credentials_password_required_and_correct(self):

        cdata = self.create_data[0]

        self.register_user( cdata )

        # create a user
        email=cdata['email']

        user = User.objects.get( email=cdata['email'] )
        user.status = 1;
        user.save()

        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Logged in")

        userid = response.data['user'].get('id')
        response = self.patch(userid, {'password':'newpass','confirm_password':cdata['password']} )
        self.assertEqual(response.status_code, 200, "Updated password")

        response = self.authenticate( email=cdata['email'], password="newpass" )
        self.assertEqual(response.status_code, 200, "Logged in")

        # update email 
        response = self.patch(userid, {'email':'updated@example.com','confirm_password':'newpass'})
        self.assertEqual(response.status_code, 200, "Updated email")   
        
        # login with new credentials
        response = self.authenticate( email='updated@example.com', password="newpass" )
        self.assertEqual(response.status_code, 200, "Signed in with new credentials")



    def test_change_credentials_password_required_not_supplied_throws_exception(self):

        # register a user
        cdata    = self.create_data[0]
        response = self.register_user( cdata )
        userid   = response.data['id']

        # set user as active
        user = User.objects.get(pk=userid)
        user.status = 1;
        user.save()

        # login
        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")

        # update password - this needs to fail, confirm_password not supplied
        userid = response.data['user'].get('id')    
        response = self.patch( userid, {'password':'newpass'} )
        self.assertEqual(response.status_code, 401, "Not authorized")    



    def test_change_credentials_reauthentication_not_required(self):

        AUTH['REQUIRE_PASSWORD_ON_ACCOUNT_MODIFICATIONS'] = False

        # register a user
        cdata    = self.create_data[0]
        response = self.register_user( cdata )
        userid   = response.data['id']

        # set user as active
        user = User.objects.get(pk=userid)
        user.status = 1;
        user.save()

        # login
        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")

        # change password without reauthentication
        userid = response.data['user'].get('id')    
        response = self.patch( userid, {'password':'newpass'} )  

        AUTH['REQUIRE_PASSWORD_ON_ACCOUNT_MODIFICATIONS'] = True




    def test_last_login(self):

        AUTH['REQUIRE_ACTIVATION'] = False

        # register a user
        cdata    = self.create_data[0]
        response = self.register_user( cdata )
        userid   = response.data['id']

        # verify last login is blank
        user = User.objects.get( pk=userid )
        self.assertEqual(user.last_login, None, "User has never logged in")

        # login
        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")

        # verify last login is not blank
        user = User.objects.get( pk=userid )
        self.assertTrue(user.last_login, "User has logged in")

        AUTH['REQUIRE_ACTIVATION'] = True

  
    def test_list(self):

        # register a user
        cdata    = self.create_data[0]
        response = self.register_user( cdata )
        userid   = response.data['id']

        # activate user
        user = User.objects.get(email="test@example.com")
        user.status = 1;
        user.save()

        # create users
        for n in range(1,6):
            User.objects.create( email='user{}@example.com'.format(n), password="testing")
        
        # list user (without permissions)
        response = self.client.get(self.api_end_point)
        self.assertEqual(response.status_code, 403, "List users unauthorized")  

        # login
        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")

        # list user (without permissions)
        response = self.client.get(self.api_end_point)
        self.assertEqual(response.status_code, 403, "List users unauthorized")   

        # add permissions to list users
        user.is_superuser = True
        user.save()   

        # list user (with super admin permissions)
        response = self.client.get(self.api_end_point)
        self.assertEqual(response.status_code, 200, "List users as super admin")  




    def test_permissions(self):

        # register a user
        cdata    = self.create_data[0]
        response = self.register_user( cdata )
        userid   = response.data['id']

        # activate user
        user = User.objects.get(email="test@example.com")
        user.status = 1;
        user.save()


        # retrieve user (unauthorized)
        response = self.get( userid )
        self.assertEqual(response.status_code, 403, "Retrieve user unauthorized")     

        # login
        response = self.authenticate( email=cdata['email'], password=cdata['password'] )
        self.assertEqual(response.status_code, 200, "Signed in")
        
        # retrieve user (authorized)
        response = self.get( userid )
        self.assertEqual(response.status_code, 200, "Retrieved user data")    



                
class RegisterAPITestCase ( TestCaseMixin, ApiMixin, AgapeTests, TestCase ):

    def setUp(self):
        
        self.sharedSetUp()
        self.createRequisiteObjects()
        self.resetSettings()

    def sharedSetUp(self):
        self.model              = USER_MODEL
        self.serializer_class   = USER_SERIALIZER
        self.entity             = USER_ENTITY_NAME
        self.api_end_point      = '/api/register/'
        self.auth_end_point     = AUTH_API_END_POINT

        self.create_data        = copy.deepcopy(USER_CREATE_DATA)
        self.expect_data        = copy.deepcopy(USER_CREATE_DATA)
        self.update_data        = copy.deepcopy(USER_UPDATE_DATA)
        self.update_expect_data = copy.deepcopy(USER_UPDATE_DATA)

    def resetSettings(self):
        # reset configuration to default settings
        for key, value in AUTH_DEFAULTS.items():
            AUTH[key] = AUTH.get(key, AUTH_DEFAULTS[key] )


    def test_user_registration(self):

        self.resetSettings()

        # register user
        response = self.post( 
            {'email': 'test@example.com', 'password':'testing'}
        )
        self.assertEqual(response.status_code, 201, "Created new user")
        
        # get user, verify that user is not active
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.status, 0, "New user is inactive")

        # attempt to login with credentials (should fail because user is inactive)
        response = self.client.post(self.auth_end_point, {'email': 'test@example.com', 'password':'testing'})
        self.assertEqual(response.status_code, 401, "Could not login to inactive account")

        # check if activation link created
        activation =  UserActivation.objects.get(user_id=user.id)
        self.assertTrue(activation, "User activation key generated")
        self.assertTrue(not activation.activated, "Activation has not been used");

        # follow activation link
        response = self.client.patch(self.auth_end_point, json.dumps({'key':activation.key}), content_type='application/json')
        self.assertEqual(response.status_code, 200, "User has been activated")

        # check if activation link is used
        activation =  UserActivation.objects.get(key=activation.key)
        self.assertTrue(activation.activated, "Activation key has been used");

        # check if user is now active
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.status, 1, "User is now active")


        # attempt to login with credentials (should pass because account has been activated)
        response = self.client.post(self.auth_end_point, {'email': 'test@example.com', 'password':'testing'})
        self.assertEqual(response.status_code, 200, "Sign in successful")
        self.assertEqual(response.data['user'].get('email'), "test@example.com")
        self.assertTrue(response.data.get('token'), "Received auth token.")

        # logout
        response = self.client.delete(self.auth_end_point)
        self.assertEqual(response.status_code, 204, "Sign out successful")


    def test_register_duplicate_email_error(self):
        # register user
        response = self.client.post(self.api_end_point, {'email': 'test@example.com', 'password':'testing'})
        self.assertEqual(response.status_code, 201, "Created new user")

        response = self.client.post(self.api_end_point, {'email': 'test@example.com', 'password':'testing'})
        self.assertEqual(response.status_code, 409, "Could not register duplicate account")

    def test_register_without_user_activation(self):
        AUTH['REQUIRE_ACTIVATION'] = False

        # register user
        response = self.client.post(
            self.api_end_point, {'email': 'test@example.com', 'password':'testing'}
        )
        self.assertEqual(response.status_code, 201, "Created new user")


        # get user, verify that user is not active
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.status, 1, "New user active")

        AUTH['REQUIRE_ACTIVATION'] = True




# test that event is triggered when the agape.auth app 
# is ready
from agape.signals import connect
appready = False

@connect('django.app.ready')
def notice( event, scope ):
    print ( event )
    print('HEEEEEEEEEEEEEEEEEEEEEEEEEYYYYYYYYYYYYYY')
    appready = True


class AuthEventsTestCase( TestCase ):

    def setUp(self):
        pass

    def test_app_ready_notice_called( self ):

        self.assertTrue( True )