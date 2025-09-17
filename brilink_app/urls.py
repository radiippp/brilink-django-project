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
        path('edit/<str:id_rek>/', rekening.RekEditViews.as_view(), name='edit_rekening'),
        path('saldo/<str:id_rek>/', rekening.TambahSaldoViews.as_view(), name='tambah_saldo'),
        path('hapus/<str:id_rek>/', rekening.RekHapusViews.as_view(), name='hapus_rekening'),
    ]) ),

    path('barang/',include([
        path('', barang.BarangViews.as_view(), name='index_barang'),
        path('tambah/', barang.BarangCreateViews.as_view(), name='tambah_barang'),
        path('edit/<str:id_barang>/', barang.BarangEditViews.as_view(), name='edit_barang'),
        path('hapus/<str:id_barang>/', barang.BarangHapusViews.as_view(), name='hapus_barang'),
        path('restok/<str:id_barang>/', barang.TambahStokViews.as_view(), name='restok'),
    ]) ),

    path('jenis/',include([
        path('', jenis.JenisViews.as_view(), name='index_jenis'),
        path('tambah/', jenis.JenisCreateViews.as_view(), name='tambah_jenis'),
        path('edit/<str:id_jenis>/', jenis.JenisEditViews.as_view(), name='edit_jenis'),
        path('hapus/<str:id_jenis>/', jenis.JenisHapusViews.as_view(), name='hapus_jenis'),
    ]) ),

    path('transaksi/', include([
        path('',transaksi.TransaksiViews.as_view(), name='index_transaksi'),
        path('export/',transaksi.ExportTransaksiExcelView.as_view(), name='export_transaksi'),
        path('tambah/',transaksi.TransaksiCreateViews.as_view(), name='tambah_transaksi'),
        path('hapus/<str:id_transaksi>/',transaksi.TransaksiHapusViews.as_view(), name='hapus_transaksi'),
    ])),
    
]
