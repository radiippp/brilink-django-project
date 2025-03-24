from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.models import Rekening, Master_User

@method_decorator(login_required(), name='dispatch')
class HomeViews(View):
    def get(self, request):
        rekening_exists = Rekening.objects.filter(akun=request.user).exists()  # Cek apakah user punya rekening
        rekening = Rekening.objects.filter(akun=request.user).first()

        if rekening:
            total_masuk = rekening.total_saldo_masuk()
            total_keluar = rekening.total_saldo_keluar()
        else:
            total_masuk = 0
            total_keluar = 0

        data={
             'rekening_exists': rekening_exists,
             'rekening' : rekening,
             'total_masuk' : total_masuk,
             'total_keluar' : total_keluar,
        }
        return render(request, 'home/index_home.html', data)
        