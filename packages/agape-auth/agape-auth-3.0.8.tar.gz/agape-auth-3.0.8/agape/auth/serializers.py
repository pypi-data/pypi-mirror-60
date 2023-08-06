from rest_framework import serializers

from django.contrib.auth import get_user_model

from agape.serializers import DynamicSerializer
from .models import UserManager
from .settings import AUTH

User = get_user_model()

from copy import deepcopy


class UserSerializer( DynamicSerializer ):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    email = serializers.CharField(required=False)
    # name  = serializers.CharField(required=False)

    class Meta:
        model = User
        
        fields = [
            'id', 
            'email', 
            # 'name',
            'password', 
            'confirm_password', 
            'status',
            'is_superuser',
            'last_login',
            'display_name'
        ]

        read_only_fields = ['id', 'display_name' ]

        # add the username field if it is not already included as the "email"
        if not AUTH['USERNAME_FIELD'] == 'email':
            fields.append( AUTH['USERNAME_FIELD'] )
            



        



    # def create(self, validated_data):


    #     validated_data = deepcopy(validated_data)
    #     password = validated_data.pop('password', None)

    #     # create the instance
    #     instance = User( **validated_data )

    #     # set the password
    #     instance.set_password( password )

    #     # save
    #     instance.save()            

    #     return instance


    def update(self, instance, validated_data):

        # make a copy of the validated data 
        # validated_data = deepcopy(validated_data)

        # remove the password from the validated database
        password = validated_data.pop('password', None)

        # update the values on the instance
        super().update( instance, validated_data )

        # set the password on the instance if a password was supplied
        if password != None:
            instance.set_password( password )
            instance.save()

        return instance
