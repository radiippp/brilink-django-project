from django.urls import path, include
from .views import *

app_name = 'app'

urlpatterns = [
    path('login/', auth.LoginViews.as_view(), name='login_page'),
    path('logout/', auth.LogoutViews.as_view(), name='logout_page'),
    path('registration/', auth.RegisterView.as_view(), name='register'),


    path('', home.HomeViews.as_view(), name='index_home'),

    path('user/', include([
       path('', user_list.UserViews.as_view(), name='index_user'),
       path('tambah/', user_list.CreateViews.as_view(), name='tambah_user'),
       path('edit/<str:id_akun>/', user_list.EditViews.as_view(), name='edit_user'),
       path('hapus/<str:id_akun>/', user_list.HapusViews.as_view(), name='hapus_user'),
       path('profile/<str:id_akun>/', user_list.ProfileViews.as_view(), name='profile_user'),
       ])),

    path('rekening/',include([
        path('', rekening.RekViews.as_view(), name='index_rekening'),
        path('tambah/', rekening.RekCreateViews.as_view(), name='tambah_rekening'),
        path('hapus/<str:id_rek>/', rekening.RekHapusViews.as_view(), name='hapus_rekening'),
    ]) ),
    # path('transaksi/', include([
    #     path('',transaksi.TransaksiViews.as_view(), name='index_transaksi'),
    #     path('tambah/',transaksi.TransCreateViews.as_view(), name='tambah_transaksi'),
    #     path('hapus/<str:id_trans>/',transaksi.TransHapusViews.as_view(), name='hapus_transaksi'),
    # ]))
    
]
