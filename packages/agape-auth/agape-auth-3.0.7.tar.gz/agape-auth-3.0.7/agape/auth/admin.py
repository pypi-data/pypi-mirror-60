from django.contrib import admin


from .models import User,UserActivation,ResetPasswordRequest

admin.site.register(User)
admin.site.register(UserActivation)
admin.site.register(ResetPasswordRequest)