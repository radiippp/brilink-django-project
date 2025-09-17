from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.models import Master_User, Rekening, Transaksi,Barang,JenisTransaksi

@method_decorator(login_required(), name='dispatch')
class HomeViews(View):
    def get(self, request):
        if hasattr(request.user, "role") and request.user.role == "developer":
            rekening = Rekening.objects.all()
        elif request.user.role == "admin":
            rekening = Rekening.objects.filter(pemilik=request.user.user_id)
        elif request.user.role == "staff":
            rekening = Rekening.objects.filter(pemilik=request.user.created_by)
        else:
            rekening = Rekening.objects.none()

        # barang sesuai role
        if hasattr(request.user, "role") and request.user.role == "developer":
            barang = Barang.objects.all()
        elif request.user.role == "admin":
            barang = Barang.objects.filter(pemilik=request.user.user_id)
        elif request.user.role == "staff":
            barang = Barang.objects.filter(pemilik=request.user.created_by)
        else:
            barang = Barang.objects.none()

        if hasattr(request.user, "role") and request.user.role == "developer":
            jenis = JenisTransaksi.objects.all()
        elif request.user.role == "admin":
            jenis = JenisTransaksi.objects.filter(created_by=request.user.user_id)
        elif request.user.role == "staff":
            jenis = JenisTransaksi.objects.filter(created_by=request.user.created_by)
        else:
            jenis = JenisTransaksi.objects.none()
        # if rekening:
        #     total_masuk = rekening.total_saldo_masuk()
        #     total_keluar = rekening.total_saldo_keluar()
        # else:
        #     total_masuk = 0
        #     total_keluar = 0

        data={
             'rekening' : rekening,
             "barang": barang,
            "jenis": jenis,
        }
        return render(request, 'home/index_home.html',data)
        