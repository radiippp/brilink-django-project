from django.urls import path, include
from .views import *

app_name = 'app'

urlpatterns = [
    path('', home.HomeViews.as_view(), name='index_home'),
    path('login/', auth.LoginViews.as_view(), name='login_page'),
]
