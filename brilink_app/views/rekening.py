from datetime import timezone
from django.views import View
from brilink_app.models import Rekening, Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.decorators import *

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class RekViews(View):
    def get(self, request):
        if hasattr(request.user, "role") and request.user.role == "developer":
            rekening = Rekening.objects.all().order_by("-created_at")
        elif request.user.role == "admin":
            rekening = Rekening.objects.filter(pemilik=request.user.user_id).order_by("-created_at")
        else:
            rekening = Rekening.objects.none()
        data ={
            'rekening' : rekening,
            }
        return render(request, 'rekening/rekening.html',data)

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class RekCreateViews(View):
    def post(self, request):
        frm_id_pemilik = request.POST.get('id_pemilik')
        frm_nama_rek = request.POST.get('nama_rek')
        frm_saldo = request.POST.get('saldo_awal')

        try:
            tmp_user = get_object_or_404(Master_User, user_id=frm_id_pemilik)
            with transaction.atomic():
                insert = Rekening.objects.create(
                    pemilik=tmp_user,
                    nama_rek=frm_nama_rek,
                    saldo=frm_saldo,
                )
                messages.success(request, f"Rekening berhasil ditambahkan")
                return redirect('app:index_rekening')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan Rekening")
            return redirect('app:index_rekening')
        
@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class RekEditViews(View):
    def get(self, request, id_rek):
        try:
            rek = Rekening.objects.get(rek_id=id_rek)
            data = {
                'rek_id': id_rek,
                'rek': rek,
            }
            return render(request, 'rekening/rekening.html', data)
        except Rekening.DoesNotExist:
            messages.error(request, "rekening tidak ditemukan")
            return redirect('app:index_rekening')
    def post(self, request,  id_rek):
        frm_nama_rek = request.POST.get('nama_rek')
        frm_saldo = request.POST.get('saldo_awal')
        try:
            
            with transaction.atomic():
                rek = Rekening.objects.get(rek_id=id_rek)
                rek.nama_rek = frm_nama_rek
                rek.saldo = frm_saldo
                rek.save()

                messages.success(request, "Rekening berhasil diedit")
                return redirect('app:index_rekening')

        except rek.DoesNotExist:
            messages.error(request, "rekening tidak ditemukan")
            return redirect('app:index_rekening')

        except Exception as e:
            print('Error:', e)
            messages.error(request, "Gagal mengubah rekening")
            return redirect('app:index_rekening')

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')      
class RekHapusViews(View):
    def get(self, request, id_rek):
        try:
            rek = Rekening.objects.get(rek_id=id_rek)
            rek.delete()
            # akun.deleted_at = timezone.now() #bikin arsip data, filter by deleted_at nya
            # akun.save() 
            # akun.delete()
            messages.success(request, f"{rek.nama_rek} berhasil dihapus")
        except Rekening.DoesNotExist:
            messages.error(request, "Rekening tidak ditemukan")
        return redirect('app:index_rekening')

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class TambahSaldoViews(View):
    def post(self, request,  id_rek):
        rek = get_object_or_404(Rekening, pk=id_rek)
        try:
            saldo_baru = int(request.POST.get("saldo_baru", 0))
        except ValueError:
            messages.error(request, "Input saldo tidak valid!")
            return redirect('app:index_rekening')

        # Validasi biar tidak minus atau nol
        if saldo_baru < 1:
            messages.error(request, "Jumlah saldo harus lebih dari 0!")
            return redirect('app:index_rekening')

        # Update saldo
        rek.saldo += saldo_baru
        rek.save()

        messages.success(
    request,
    f"Saldo untuk {rek.nama_rek} berhasil ditambah Rp. {saldo_baru:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
        return redirect('app:index_rekening')