from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.views import View
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
import shutil,os
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count
from brilink_app.models import Master_User as m_user, ROLE_CHOICES
from django.db import transaction
import re

def check_is_email(email):
    """
    Fungsi untuk memeriksa apakah input adalah email atau bukan.

    Args:
        email (str): String input yang ingin dicek.

    Returns:
        bool: True jika input adalah email valid, False jika bukan.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))

class LoginViews(View):
    """docstring for LoginViews"""
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'auth/login.html')
        else:
            return redirect('app:index_home')

    def post(self, request):
        if not request.user.is_authenticated:
            email = request.POST.get('frm_email')
            pwd = request.POST.get('frm_pwd')

            is_email = check_is_email(email)
            
            if is_email:
                user = authenticate(request, email=email, password=pwd)
            else:
                try:
                    user = m_user.objects.get(username = email, is_active = True)
                    if not user.check_password(pwd):
                        user = None
                except Exception as e:
                    user = None
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Selamat datang {user.username}")
                if request.GET.get('next') is not None:
                    return redirect(request.GET.get('next'))
                else:
                    return redirect('app:index_home')
            else:
                messages.error(request, "Login gagal, silahkan masukkan data dengan benar")
                return redirect('app:login_page')
        else:
            return redirect('app:index_home')

@method_decorator(login_required(), name='dispatch')
class LogoutViews(View):
    def get(self, request):
        logout_message = request.GET.get('logout_message', None)
        if logout_message is not None:
            messages.info(request, logout_message)
        
        logout(request)
        return redirect('app:login_page')