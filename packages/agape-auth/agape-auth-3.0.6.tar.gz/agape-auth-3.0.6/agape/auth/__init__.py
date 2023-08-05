# enable app initialization events by using the AgapeAppConfig
from agape.django.config import DjangoAppConfig 

class AppConfig( DjangoAppConfig ):
	name = "agape.auth"
	label = "agapeAuth"

# This line prevents this error:  django.core.exceptions.ImproperlyConfigured: Application labels aren't unique, duplicates: auth
default_app_config = 'agape.auth.AppConfig'





from agape.signals import connect
from agape.auth.settings import AUTH
from agape.errors import ErrorResponse

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site

from django.contrib.auth import authenticate



# Enumerated option values
USER_STATUS_ENABLED = 1;
USER_STATUS_DISABLED = 0;


# get the name of the username field from the configuration
def username_field():
	return  AUTH['USERNAME_FIELD']

# get a dictionary with username key/value
def username_opt(value):
	return { AUTH['USERNAME_FIELD'] : value } 

# get the value of the 
def username_value(instance):
	return getattr(instance, AUTH['USERNAME_FIELD'] )



@connect('user.create:before')
def on_user_create_before_check_unique_username( event,  scope ):
	""" Check that the username field is unique. """
	User = get_user_model()

	username_value = scope.data.get( username_field() )

	existing 	   = User.objects.filter( **username_opt( username_value ) )

	if existing.count() > 0:

		message  = 'This {} is already in use.'

		scope.error = ErrorResponse('409', message.format( username_field() ) )

		raise scope.error



# @connect('user.create(register):before')
@connect('user.register.create:before')
def on_user_create_before_set_status( event,  scope ):
	""" Set the status of the user based on user configuration. Status will
	be enabled if accounts do not require activation."""

	#TODO: if scope.premise == 'register':

	scope.data['status'] = USER_STATUS_DISABLED \
								if AUTH['REQUIRE_ACTIVATION'] \
								else USER_STATUS_ENABLED




@connect('user.register.create:success')
def on_user_create_success( event, scope ):

	from agape.auth.models import UserActivation

	# if account requires activation
	if AUTH['REQUIRE_ACTIVATION']:

		activation = UserActivation.objects.create( user=scope.instance )

		send_activation_email( activation, scope.request )




def send_activation_email( activation, request ):
	""" Send the activation email to the user """


	current_site = get_current_site(request)
	protocol     = 'https' if request.is_secure() else 'http' 

	# create an activation link using information from the 'sites' app
	def create_activation_link():

		link = '{}://{}/activate/{}'
		return link.format( protocol, current_site.domain, activation.key )


	# get the from email address from the settings, if there is no domain
	# specified then attach the domain based on information from the 'sites' app
	def get_from_email():

		if not AUTH['FROM_EMAIL_ADDRESS']:
			raise Exception("No from email in settings file. Set the AUTH['FROM_EMAIL_ADDRESS'] value. ")

		elif '@' in AUTH['FROM_EMAIL_ADDRESS']:
			return AUTH['FROM_EMAIL_ADDRESS']

		else:
			return '@'.join( (AUTH['FROM_EMAIL_ADDRESS'], current_site.domain) )


	# create the email
	link = create_activation_link()
	from_email = get_from_email()
	subject = 'Activate your account at {}'
	body 	= 'Please activate your account by following this link \n\n{}\n\n'

	try:
		send_mail(
				subject.format( current_site.name ),
				body.format( link ),
				from_email,
				[ activation.user.email ],
				fail_silently=False
			)
	except Exception as error:

		# raise Exception(
		# 	 "Error sending email in send_activation_email function: "
		# )
		# TODO: Log this error somewhere! 
		# We need to know if the activation email is failing.
		print( "Error sending email in send_activation_email function: ")
		print( error )



@connect('user.update:before')
def on_user_update_authenticate_on_modify_credentials( event, scope ):

	scope.modifying_current_user = str(scope.pk) == str( scope.request.user.id )

	if AUTH['REQUIRE_PASSWORD_ON_ACCOUNT_MODIFICATIONS'] and scope.modifying_current_user:

		# error no password supplied
		if not 'confirm_password' in scope.data:

			raise ErrorResponse('401', 'Confirm your password to make account changes.')

		# authenticate the current user with the confirm_password option
		user = authenticate( 
			# this line retrieves the "username" field and value using the app configuration 
			**username_opt( username_value(scope.request.user) ), 
			password=scope.data.get('confirm_password')
		) 

		if user is None:
			raise ErrorResponse('401', 'Password incorrect.')

		elif user.is_active == False:
			raise ErrorResponse('401', 'Account disabled.')

@connect('user.update:before')
def on_user_update_before_get_new_password( event, scope ):

	if 'password' in scope.data:
		scope.new_password = scope.data.get('password', None)
		scope.data.pop('password')
	else:
		scope.new_password = None



@connect('user.update:success')
def on_user_update_success_set_password( event, scope ):

	if scope.new_password:
	    scope.instance.set_password( scope.new_password )
	    scope.instance.save()
	    

@connect('user.update:success')
def on_user_update_success( event, scope ):
	if scope.new_password and hasattr( scope, 'modifiying_current_user' ):
		update_session_auth_hash( scope.request, scope.instance )

