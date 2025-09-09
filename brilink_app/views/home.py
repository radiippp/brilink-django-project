from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.models import Master_User, Rekening

@method_decorator(login_required(), name='dispatch')
class HomeViews(View):
    def get(self, request):
        user = request.user

    # kalau dia staff, ambil rekening dari created_by (pemilik)
        if user.created_by:
            rekening_list = Rekening.objects.filter(pemilik_id=user.created_by)
        else:
        # kalau dia pemilik, ambil rekening miliknya
            rekening_list = Rekening.objects.filter(pemilik=user)

        # if rekening:
        #     total_masuk = rekening.total_saldo_masuk()
        #     total_keluar = rekening.total_saldo_keluar()
        # else:
        #     total_masuk = 0
        #     total_keluar = 0

        data={
             'rekening_list': rekening_list,
        #      'rekening' : rekening,
        #      'total_masuk' : total_masuk,
        #      'total_keluar' : total_keluar,
        }
        return render(request, 'home/index_home.html',data)
        