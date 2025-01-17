from django.urls import path, include
from .views import *

app_name = 'app'

urlpatterns = [
    path('login/', auth.LoginViews.as_view(), name='login_page'),


    path('', home.HomeViews.as_view(), name='index_home'),

    path('user/', include([
       path('', user_list.UserViews.as_view(), name='index_user'),
    #    path('tambah/', master_user.CreateViews.as_view(), name='tambah_user'),
    #    path('edit/<str:id_akun>/', master_user.EditViews.as_view(), name='edit_user'),
    #    path('hapus/<str:id_akun>/', master_user.HapusViews.as_view(), name='hapus_user'),
    #    path('profile/<str:id_akun>/', master_user.ProfileViews.as_view(), name='profile_user'),
       ])),
    
]
