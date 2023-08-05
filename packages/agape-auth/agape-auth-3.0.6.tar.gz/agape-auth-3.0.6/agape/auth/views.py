from rest_framework import permissions,status,views,viewsets
from rest_framework.response import Response
from rest_framework import generics

from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from rest_framework_jwt.settings import api_settings



from django.utils import timezone
from datetime import timedelta

from .permissions import IsAccountOwner
from .serializers import UserSerializer
from .models import UserActivation, ResetPasswordRequest
from .settings import AUTH

from agape import auth
from agape.auth import username_field, username_opt, username_value
from agape.proxies import ModelProxy
from agape.signals import trigger
from agape.viewsets import CrudViewSet

# update the session auth hash when modifying a logged in users credentials
from django.contrib.auth import update_session_auth_hash


class RegisterView( views.APIView ): # , ScopedViewMixin

	# context = "user"
	# serializer_class = UserSerializer

	def post( self, request, *args, **kwargs ):

		proxy = ModelProxy( ['user', 'user.register'], User, UserSerializer )

		proxy.create( **kwargs, request=request )

		return proxy.response


		
class UserViewSet( CrudViewSet ):

	context = "user"
	model = User
	serializer_class = UserSerializer

	
	def get_permissions(self):
		""" Set permission restrictions """

		# allow super admin to access all methods
		if self.request.user.is_superuser:
			return(permissions.AllowAny(),)

		if self.action == "list":
			return (permissions.IsAdminUser(),)

		else:
			return(permissions.IsAuthenticated(), IsAccountOwner() )

			
class SendUserActivationView( views.APIView ):

	def get_permissions(self):

		if self.request.user.is_superuser:
			return(permissions.AllowAny(),)
		else:
			return (permissions.IsAdminUser(),)

	def get( self, request, *args, **kwargs ):

		userid = kwargs.get('pk')

		user = User.objects.get( pk=userid )

		instance = UserActivation.objects.create( user=user )

		instance.send_activation_email( request )

		return Response('ok')

	



class AuthView(views.APIView):
	""" Handles auth (logging in and out)
	"""

	serializer_class = UserSerializer

	def post(self, request, format=None):
		""" Sign in to a user account .

		Returns a response with an auth token
		"""


		data = request.data
		user = None

		# TODO: Maybe LOGIN_WITH_PARAM should only make one call to the database
		# by using an OR query

		# Find the user, using all the possible login fields
		for field in AUTH['LOGIN_WITH_FIELDS']:
			if field in data:
				login_with_value = data.get(field)

			# the login_with_field can be used to sign in to any of the 'LOGIN_WITH_FIELDS' fields
			elif AUTH['LOGIN_WITH_PARAM']:
				login_with_value = data.get( AUTH['LOGIN_WITH_PARAM'] )

			try:
				lookup_opt = { field: login_with_value }
				user = User.objects.get( **lookup_opt )
			except:
				pass



		# return unauthorized response if the user was not found
		if user == None:
			return Response({
				'status': 'unauthorized',
				'message': 'Invalid credentials.'
			}, status=status.HTTP_401_UNAUTHORIZED)            
		
		# return unauthorized if the user is disabled
		if not user.is_active:
			return Response({
				'status': 'unauthorized',
				'message': 'This user has been disabled.'
			}, status=status.HTTP_401_UNAUTHORIZED)


		# we found a matching user, authenticate
		password = data.get('password', None)
		user = authenticate( **username_opt( username_value(user) ), password=password)


		# invalid credentials
		if user == None:
			return Response({
				'status': 'unauthorized',
				'message': 'Invalid credentials.'
			}, status=status.HTTP_401_UNAUTHORIZED)   


		# user authenticated successfully
		else:

			# login
			login(request, user)
			user.last_login = timezone.now()
			user.save()

			# create an auth token
			jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
			jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
			
			payload = jwt_payload_handler(user)
			token = jwt_encode_handler(payload)

			# create the response
			response = {
				'user': self.serializer_class(user).data,
				'token': token 
				}
			return Response( response, status=status.HTTP_200_OK );



	def delete(self, request, *args, **kwargs):
		""" Destroy a users auth token, effectively signing out.
		"""

		# If a user is signed in
		if request.user.is_authenticated:
			# sign out
			logout(request)
			return Response({}, status=status.HTTP_204_NO_CONTENT) 
		
		# otherwise respond with bad request
		else:
			# Do something for anonymous users.
			return Response({
				'status': 'Bad request',
				'message': 'There is no authenticated user to sign out.'
			}, status=status.HTTP_400_BAD_REQUEST)  


	def patch(self,request,*args,**kwargs):
		""" Activate a user account
		"""

		key = request.data.get('key')
		if key == None:
			return Response({
					'status': 'fail',
					'message': 'No activation key given.',
				},  status=status.HTTP_400_BAD_REQUEST);

		# perform key lookup
		results = UserActivation.objects.filter(key=key).all()

		# no activation key found in database
		if len(results) == 0:
			return Response({
					'status': 'fail',
					'message': 'Could not activate account',
				},  status=status.HTTP_400_BAD_REQUEST);

		# user has been banned
		# TODO: Replace this user status check with enumerated package variable
		elif results[0] and results[0].user.status < 0:
			return Response({
					'status': 'fail',
					'message': 'This account has been disabled.',
				},  status=status.HTTP_400_BAD_REQUEST);              

		# found activation key, but user is already activated
		elif results[0] and results[0].activated:
			return Response({
					'status': 'fail',
					'message': 'This account has already been activated.',
				},  status=status.HTTP_409_CONFLICT);   


		# found activation key, activate account
		else:
			activation = results[0]
			activation.activated = timezone.now()
			activation.save()

			activation.user.status = 1;
			activation.user.save();
			return Response({
					'status': 'succes',
					'message': 'This account is now active.',
				},  status=status.HTTP_200_OK); 



	

class ResetPasswordRequestView(views.APIView):
	""" Send a password reset link to a user via email
	
	Will send a password reset link if no other request has been issued in the 
	past X minutes. Password reset links are only valid for the number of minutes
	specified in the configuration file. Defaults to 30.

	Extends:
		views.APIView    
	"""
	@transaction.atomic
	def post(self,request,*args, **kwargs):
		""" Create a new reset password request. 

		Generates a new unique key which can be used to reset a users password. Sends
		an email containing a password reset link to the specified user.
		"""

		# TODO: Get the user via username or password
		# get key from uri
		email = request.data.get('email')

		# find user with given email
		user = User.objects.filter(email=email).all()

		# user does not exist- return response
		if len(user) == 0:

			if AUTH['RESET_PASSWORD_REQUEST_ALWAYS_OK']:

				return Response({
						'status': 'succes',
						'message': 'A link to reset your password has been sent to this email address.',
					},  status=status.HTTP_200_OK); 

			else:
				
				return Response({
						'status': 'fail',
						'message': 'No user with this email address.',
					},  status=status.HTTP_404_NOT_FOUND);


		# user does exist
		else:
			user = user[0]

		# if user has been disabled, throw an error
		if user.status == User.DISABLED:
			return Response({
					'status': 'fail',
					'message': 'This user has been disabled.',
				},  status=status.HTTP_400_BAD_REQUEST);
		
		# check if there is another password reset request sent in the past 30 minutes
		time_threshold = timezone.now() - timedelta(minutes=AUTH.get('RESET_PASSWORD_EXPIRES'))
		results = ResetPasswordRequest.objects.filter(user=user,status=ResetPasswordRequest.ENABLED, created__gt=time_threshold).order_by('-id')
				
		# if active request, use the same request link
		if len(results) > 0:
			instance = results[0]

		# if no active request, create a new request link
		else:
			instance = ResetPasswordRequest.objects.create(user=user)

		# create password reset instance
		self.dispatch_email(instance, request)

		return Response({
				'status': 'succes',
				'message': 'A link to reset your password has been sent to this email address.',
			},  status=status.HTTP_200_OK); 




	def get(self,request,*args, **kwargs):
		""" Check a reset password request for valididy and expiration
		"""

		# get key from uri
		key = self.kwargs.get('key')

		# check key for validity
		response = self.validate_key(key)

		# if received Response, invalid key
		if isinstance(response, Response):
			# return the response
			return response
		# otherwise, confirm password reset link is valid
		else:
			return Response({
					'status': 'success',
					'message': 'Password reset key is valid.'
				}, status=status.HTTP_200_OK);


	@transaction.atomic
	def patch(self,request,*args, **kwargs):
		"""Peform the password reset.
		
		Decorators:
			transaction.atomic
		
		Request Data:
			password (string): Email address of registered user

		Status:
			200: Success
			400: No password provided
			401: Link is no longer valid or has been used
			404: Reset code not found   
		"""

		# get key from uri
		key = self.kwargs.get('key')

		# check key for validity
		response = self.validate_key(key)

		# if received Response, invalid key
		if isinstance(response, Response):
			# return the response
			return response
		# otherwise, we have a ResetPasswordRequest
		else:
			instance = response

		# return error if user did not supply a password
		if request.data.get('password', None) == None or request.data.get('password') == "":
			return Response({
					'status': 'fail',
					'message': 'No password set.'
				}, status=status.HTTP_400_BAD_REQUEST);
 

		# set the password
		user = instance.user
		user.set_password(request.data.get('password'))
		user.save()

		instance.used = timezone.now()
		instance.status = ResetPasswordRequest.USED
		instance.save()


		return Response({
				'status': 'success',
				'message': 'Password has been changed.'
			}, status=status.HTTP_200_OK);


	def validate_key(self,key):
		""" Check a key for validity.

		Checks that key exists, has not been disabled, and is not expired.

		Returns:
			Response object for invalid keys
			ResetPasswordRequest for valid keys
		"""

		# get user from password reset items
		try:
			instance = ResetPasswordRequest.objects.get(key=key)
		except:
			# return 404 if no matching reset request
			return Response({
					'status': 'fail',
					'message': 'This password reset key is not valid.'
				}, status=status.HTTP_404_NOT_FOUND);

		# return error if link has been used already or is disabled
		if instance.status == ResetPasswordRequest.USED:
			return Response({
					'status': 'fail',
					'message': 'This password reset key has expired.'
				}, status=status.HTTP_410_GONE);

		elif instance.status == ResetPasswordRequest.DISABLED:
			return Response({
					'status': 'used',
					'message': 'This password reset key has been disabled.'
				}, status=status.HTTP_403_FORBIDDEN);

		# return error if link has expired
		elif instance.created < timezone.now() - timedelta(minutes=AUTH.get('RESET_PASSWORD_EXPIRES')):
			return Response({
					'status': 'fail',
					'message': 'This password reset key has expired.'
				}, status=status.HTTP_410_GONE);

		# check that user is not disabled
		elif instance.user.status == User.DISABLED:
			return Response({
					'status': 'fail',
					'message': 'This account has been disabled.',
				},  status=status.HTTP_403_FORBIDDEN);

		else:
			return instance

	def dispatch_email(self, instance, request):
		""" Send an email to the user containing a link to reset their password.

		Args:
			instance (object): The ResetPasswordRequest instance
			request (object): The request object
		"""

		# create the link
		current_site = get_current_site(request)
		protocol = 'https' if request.is_secure() else 'http' 
		link = '{}://{}/reset-password/{}'.format(protocol, current_site.domain, instance.key)

		# dispatch the email
		send_mail(
			'Password Reset',
			'Reset your password by following this link \n\n{}\n\n-'.format(link),
			'test@example.com',
			[instance.user.email],
			fail_silently=False
			)

class ValidateEmailView(views.APIView):
	""" Determine if an email is already registered with a user account."""


	def get(self,request):

		email = request.GET.get('email')
		userid = request.GET.get('userid')

		# check for existing account with given email
		duplicates = User.objects.filter(email=email)

		# exclude the account already registered with this email
		if userid:
			duplicates = duplicates.exclude(id=userid)

		results = duplicates.all()
		if len(results) > 0:
			return Response({
				'valid': False,
				'message': 'This email is already in use.'
			}, status=status.HTTP_200_OK)
		else:
			return Response({
				'valid': True
			}, status=status.HTTP_200_OK)
