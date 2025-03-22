from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.models import Rekening, Master_User

@method_decorator(login_required(), name='dispatch')
class HomeViews(View):
    def get(self, request):
        rekening_exists = Rekening.objects.filter(akun=request.user).exists()  # Cek apakah user punya rekening
        return render(request, 'home/index_home.html', {"rekening_exists": rekening_exists})
        