from datetime import timezone
from django.views import View
from brilink_app.models import JenisTransaksi,Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.decorators import *

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class JenisViews(View):
    def get(self, request):
        if hasattr(request.user, "role") and request.user.role == "developer":
            jenis = JenisTransaksi.objects.all()
        elif request.user.role == "admin":
            jenis = JenisTransaksi.objects.filter(created_by=request.user.user_id)
        else:
            jenis = JenisTransaksi.objects.none()
        
        data ={
            'jenis' : jenis,
            }
        return render(request, 'jenis/jenis.html',data)
    
@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class JenisCreateViews(View):
    def post(self, request):
        frm_id_pemilik = request.POST.get('id_pemilik')
        frm_nama = request.POST.get('nama')
        frm_kategori = request.POST.get('kategori')

        try:
            tmp_user = get_object_or_404(Master_User, user_id=frm_id_pemilik)
            with transaction.atomic():
                insert = JenisTransaksi.objects.create(
                    created_by=tmp_user,
                    nama=frm_nama,
                    kategori=frm_kategori,
                )
                messages.success(request, f"Jenis berhasil ditambahkan")
                return redirect('app:index_jenis')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan Jenis")
            return redirect('app:index_jenis')
        
@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class JenisEditViews(View):
    def get(self, request, id_jenis):
        try:
            jenis = JenisTransaksi.objects.get(jenis_id=id_jenis)
            data = {
                'jenis_id': id_jenis,
                'jenis': jenis,
            }
            return render(request, 'jenis/jenis.html', data)
        except JenisTransaksi.DoesNotExist:
            messages.error(request, "Jenis tidak ditemukan")
            return redirect('app:index_Jenis')
    def post(self, request,  id_jenis):
        frm_nama = request.POST.get('nama')
        frm_kategori = request.POST.get('kategori')
        try:
            
            with transaction.atomic():
                jenis = JenisTransaksi.objects.get(jenis_id=id_jenis)
                jenis.nama = frm_nama
                jenis.kategori = frm_kategori
                jenis.save()

                messages.success(request, "jenis berhasil diedit")
                return redirect('app:index_jenis')

        except JenisTransaksi.DoesNotExist:
            messages.error(request, "jenis tidak ditemukan")
            return redirect('app:index_jenis')

        except Exception as e:
            print('Error:', e)
            messages.error(request, "Gagal mengubah jenis")
            return redirect('app:index_jenis')

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class JenisHapusViews(View):
    def get(self, request, id_jenis):
        try:
            jenis = JenisTransaksi.objects.get(jenis_id=id_jenis)
            jenis.delete()
            messages.success(request, f"{jenis.nama} berhasil dihapus")
        except JenisTransaksi.DoesNotExist:
            messages.error(request, "jenis tidak ditemukan")
        return redirect('app:index_jenis')