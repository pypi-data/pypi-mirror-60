from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.db import models
from .settings import AUTH

from django.contrib.sites.shortcuts import get_current_site


# for random string generation
import string
import random

# for dispatching emails after creating new activation and password reset links
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from agape.entity import entity

from agape.models import DynamicModel

class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for
    auth instead of usernames. This replaces the default "UserManager".
    """
    def create_user(self, **args ):
        """
        Creates and saves a User with the given email and password.
        """


        if not args.get( AUTH['USERNAME_FIELD'], None ):
            raise ValueError('The username must be set.')

        if not args.get( 'password', None ):
            raise ValueError('The password must be set.')

        # normalize email field
        if AUTH['USERNAME_FIELD'] == 'email':
            args[ AUTH['USERNAME_FIELD'] ] = self.normalize_email( args[ AUTH['USERNAME_FIELD'] ] )

        # get the password
        password = args.pop('password', None)

        # get the User set in the settings file
        UserModel = get_user_model()

        # set the user
        user = UserModel.objects.create( **args )
        user.set_password(password)
        user.save() 
        return user
    

    def create_superuser(self, **args ):
        args.setdefault('is_superuser',True)
        args.setdefault('status',1)

        return self.create_user(**args)

    def create( self, **fields ):

        set_password = False
        
        if 'password' in fields:
            set_password = True
            password = fields.pop('password', None)

        instance = super().create(**fields)

        if set_password:
            instance.set_password( password )
            instance.save()

        return instance





def email_required():

    return ( AUTH['USERNAME_FIELD'] == 'email'  or AUTH['EMAIL_REQUIRED'] )

def username_required():

    return  AUTH['USERNAME_FIELD'] == 'username' 

@entity
class User(DynamicModel, AbstractBaseUser, PermissionsMixin):
    """
    A custom user class which uses emails as unique identifiers instead
    of usernames. This replaces the default "User" supplied by Django.
    """
    DISABLED = -1
    INACTIVE = 0
    ACTIVE = 1
    STATUS_CHOICES = (
        ("", '-- select --'),
        (DISABLED, 'Disabled'),
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active')
    )

    entity = "user"
    
    email        = models.EmailField( unique=True, blank=not email_required(), null=not email_required() )
    # name         = models.CharField( max_length=64, blank=True, null=True )
    username     = models.CharField( max_length=32, unique=username_required(), blank=not username_required(), null=not username_required() )

    is_superuser = models.BooleanField(default=False,help_text="Designates whether user can log into the backend.")
    status       = models.SmallIntegerField(choices=STATUS_CHOICES,blank=False,null=False,default=0 )
    last_login   = models.DateTimeField(blank=True,null=True)
    
    created      = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    created_by   = models.ForeignKey('User', on_delete=models.PROTECT, blank=True, null=True, related_name="created_user")
    modified     = models.DateTimeField(auto_now=True,blank=True,null=True)
    modified_by  = models.ForeignKey('User', on_delete=models.PROTECT, blank=True, null=True, related_name="modified_user")    

    USERNAME_FIELD = AUTH['USERNAME_FIELD']
    REQUIRED_FIELDS = AUTH['REQUIRED_FIELDS']
    objects = UserManager()
    
    @property
    def is_admin(self):
      return self.is_superuser
    
    @property
    def is_staff(self):
      return self.is_superuser

    @property
    def is_active(self):
        return True if self.status == 1 else False;

    @property
    def display_name(self):
        
        if self.username:
            return self.username

        else:
            return self.email
    
    
    def get_short_name(self):
        self.email;
    
    def get_long_name(self):
        self.email;
    
    def __unicode__(self):
        return 'user:{}'.format( self.display_name )

    def __str__(self):
        return 'user:{}'.format( self.display_name )


    def clean_email(self):
        return self.cleaned_data['email'] or None



class UserActivation(models.Model):
    """ Provide activation links for new users.
    
    Generates a random key which is used to activate a new user account. Emails can
    then be sent to users with a link containing the key. Once this link has been
    followed the account will be set to active.
    
    Extends:
        models.Model
    
    Variables:
        user (models.ForeignKey): User account to activate
        key  (models.StringField): Randomly generated string of eight uppercase letters and numbers
        created (models.DateTimeField): Time activation link was created
        activated (models.DateTimeField): Time account was activated
    """

    entity = "user-activation"

    def generate_key():
        """Generate a random string of 8 uppercase letters and numbers

        Returns:
            string: Random string of 8 uppercase letters and numbers

        """
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

    user      = models.ForeignKey('User', on_delete=models.CASCADE, blank=False, null=False)    
    key       = models.CharField(max_length=8,unique=True,blank=False,null=False,default=generate_key)
    created   = models.DateTimeField(auto_now_add=True,blank=True,null=False)
    activated = models.DateTimeField(blank=True,null=True)



    def send_activation_email( self, request ):
        """ Send the self email to the user """


        current_site = get_current_site(request)
        protocol     = 'https' if request.is_secure() else 'http' 

        # create an self link using information from the 'sites' app
        def create_activation_link():

            link = '{}://{}/activate/{}'
            return link.format( protocol, current_site.domain, self.key )


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
        body    = 'Please activate your account by following this link \n\n{}\n\n'

        try:
            send_mail(
                    subject.format( current_site.name ),
                    body.format( link ),
                    from_email,
                    [ self.user.email ],
                    fail_silently=False
                )
        except Exception as error:

            # raise Exception(
            #    "Error sending email in send_activation_email function: "
            # )
            # TODO: Log this error somewhere! 
            # We need to know if the self email is failing.
            print( "Error sending email in send_activation_email function: ")
            print( error )



class ResetPasswordRequest(models.Model):
    """ Provide password reset links for new users.
    
    Generates a random key which is used to reset user account passwords. Emails can
    then be sent to users with a link containing the key. Once this link has been
    followed the user can set a new password.
    
    Extends:
        models.Model
    
    Variables:
        user (models.ForeignKey): User account to activate
        key  (models.StringField): Randomly generated string of 16 uppercase letters and numbers
        created (models.DateTimeField): Time reset link was created
        activated (models.DateTimeField): Time reset link was followed
    """

    entity = "reset-password-request"

    def generate_key():
        """Generate a random string of 16 uppercase letters and numbers

        Returns:
            string: Random string of 16 uppercase letters and numbers

        """
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(16))


    DISABLED = -1
    ENABLED = 1
    USED = 2
    STATUS_CHOICES = (
        ("", '-- select --'),
        (DISABLED, 'Disabled'),
        (ENABLED, 'Active'),
        (USED, 'Used'),
    )

    user      = models.ForeignKey('User', on_delete=models.CASCADE, blank=False, null=False) 
    key       = models.CharField(max_length=16,unique=True,blank=False,null=False,default=generate_key)
    created   = models.DateTimeField(auto_now_add=True,blank=True,null=False)
    status    = models.SmallIntegerField(choices=STATUS_CHOICES,blank=False,null=False,default=1)
    used      = models.DateTimeField(blank=True,null=True)
