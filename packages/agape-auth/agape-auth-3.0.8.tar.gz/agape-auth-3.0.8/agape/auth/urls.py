from django.conf.urls import url, include
from .views import UserViewSet, AuthView, ResetPasswordRequestView, ValidateEmailView


from .views import RegisterView
from .views import SendUserActivationView

# build router
from rest_framework.routers import DefaultRouter

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    url(r'^',include(router.urls)),

    url(r'^auth/$', AuthView.as_view(), name='auth'),
    url(r'^auth/recovery/((?P<key>[A-Z0-9_]+)/)?$', ResetPasswordRequestView.as_view(), name='reset-password'),

    url(r'^register/?$'  , RegisterView.as_view() ),
    
    url(r'^auth/email/?$', ValidateEmailView.as_view(), name='validate-email'),

    url(r'^auth/token-auth/', obtain_jwt_token),
    url(r'^auth/token-verify/', verify_jwt_token),
    url(r'^auth/token-refresh/', refresh_jwt_token),


    url(r'^users/(?P<pk>[0-9]+)/send-activation-email/', SendUserActivationView.as_view(), name="send-activation-email"),
]

    # users/
    #   - GET: list
    #   - POST: register
    #   - PATCH: update
    
    # auth/
    #   - POST: login
    #   - DELETE: logout
    #   - PATCH: activate account

    # auth/password
    #   - POST: create password reset request
    #   - PATCH: modify password
        
    # auth/email
    #   - GET: verify email
    #       - parameters:
    #           email
    #           userid