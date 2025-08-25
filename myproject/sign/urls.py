from tempfile import template

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import BaseRegisterView, Account, upgrade_me


urlpatterns = [
    path('login/',
         LoginView.as_view(template_name = 'login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name = 'logout.html'),
         name='logout'),
    path('signup/',
         BaseRegisterView.as_view(template_name = 'signup.html'),
         name='signup'),
    path('account/', Account.as_view()),
    path('', Account.as_view(template_name = 'index.html')),
    path('upgrade/', upgrade_me, name = 'upgrade')
]