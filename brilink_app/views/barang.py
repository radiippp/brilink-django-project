from datetime import timezone
from django.views import View
from brilink_app.models import Barang,Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from brilink_app.decorators import *
from django.utils.decorators import method_decorator

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class BarangViews(View):
    def get(self, request):
        if hasattr(request.user, "role") and request.user.role == "developer":
            barang = Barang.objects.all().order_by("-created_at")
        elif request.user.role == "admin":
            barang = Barang.objects.filter(pemilik=request.user.user_id).order_by("-created_at")
        else:
            barang = Barang.objects.none()
        
        data ={
            'barang' : barang,
            }
        return render(request, 'barang/barang.html',data)
    
@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class BarangCreateViews(View):
    def post(self, request):
        frm_id_pemilik = request.POST.get('id_pemilik')
        frm_nama_barang = request.POST.get('nama_barang')
        frm_harga = request.POST.get('harga')
        frm_stok = request.POST.get('stok_awal')

        try:
            tmp_user = get_object_or_404(Master_User, user_id=frm_id_pemilik)
            with transaction.atomic():
                insert = Barang.objects.create(
                    pemilik=tmp_user,
                    nama=frm_nama_barang,
                    harga=frm_harga,
                    stok=frm_stok,
                )
                messages.success(request, f"Barang berhasil ditambahkan")
                return redirect('app:index_barang')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan Barang")
            return redirect('app:index_barang')
        
@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class BarangEditViews(View):
    def get(self, request, id_barang):
        try:
            barang = Barang.objects.get(barang_id=id_barang)
            data = {
                'barang_id': id_barang,
                'barang': barang,
            }
            return render(request, 'barang/barang.html', data)
        except Barang.DoesNotExist:
            messages.error(request, "Barang tidak ditemukan")
            return redirect('app:index_barang')
    def post(self, request,  id_barang):
        frm_nama_barang = request.POST.get('nama_barang')
        frm_harga = request.POST.get('harga')
        frm_stok = request.POST.get('stok_awal')
        try:
            
            with transaction.atomic():
                barang = Barang.objects.get(barang_id=id_barang)
                barang.nama = frm_nama_barang
                barang.harga = frm_harga
                barang.stok = frm_stok
                barang.save()

                messages.success(request, "Baranng berhasil diedit")
                return redirect('app:index_barang')

        except Barang.DoesNotExist:
            messages.error(request, "Barang tidak ditemukan")
            return redirect('app:index_barang')

        except Exception as e:
            print('Error:', e)
            messages.error(request, "Gagal mengubah Barang")
            return redirect('app:index_barang')
        
@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class BarangHapusViews(View):
    def get(self, request, id_barang):
        try:
            barang = Barang.objects.get(barang_id=id_barang)
            barang.delete()
            # akun.deleted_at = timezone.now() #bikin arsip data, filter by deleted_at nya
            # akun.save() 
            # akun.delete()
            messages.success(request, f"{barang.nama} berhasil dihapus")
        except Barang.DoesNotExist:
            messages.error(request, "Barang tidak ditemukan")
        return redirect('app:index_barang')

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class TambahStokViews(View):
    def post(self, request,  id_barang):
        barang = get_object_or_404(Barang, pk=id_barang)
        try:
            stok_baru = int(request.POST.get("stok_baru", 0))
        except ValueError:
            messages.error(request, "Input stok tidak valid!")
            return redirect('app:index_barang')

        # Validasi biar tidak minus atau nol
        if stok_baru < 1:
            messages.error(request, "Jumlah stok harus lebih dari 0!")
            return redirect('app:index_barang')

        # Update stok
        barang.stok += stok_baru
        barang.save()

        messages.success(request, f"Stok untuk {barang.nama} berhasil ditambah {stok_baru} unit!")
        return redirect('app:index_barang')