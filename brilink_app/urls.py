from django.urls import path, include
from .views import *

app_name = 'app'

urlpatterns = [
    path('login/', auth.LoginViews.as_view(), name='login_page'),
    path('logout/', auth.LogoutViews.as_view(), name='logout_page'),


    path('', home.HomeViews.as_view(), name='index_home'),

    path('user/', include([
       path('', user_list.UserViews.as_view(), name='index_user'),
       path('tambah/', user_list.CreateViews.as_view(), name='tambah_user'),
       path('edit/<str:id_akun>/', user_list.EditViews.as_view(), name='edit_user'),
       path('hapus/<str:id_akun>/', user_list.HapusViews.as_view(), name='hapus_user'),
       path('profile/<str:id_akun>/', user_list.ProfileViews.as_view(), name='profile_user'),
       ])),

    path('rekening/', rekening.RekCreateViews.as_view(), name='tambah_rekening'),
    
]
