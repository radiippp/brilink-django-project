from datetime import timezone
from django.views import View
from brilink_app.models import Transaksi, Master_User, Rekening
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


class TransaksiViews(View):
    def get(self, request):
        rekening = Rekening.objects.filter(akun=request.user).first()

        # Ambil semua transaksi yang terkait dengan rekening user
        transaksi = Transaksi.objects.filter(rek=rekening).order_by('-created_at') if rekening else []
        data ={
            'transaksi' : transaksi,
            }
        return render(request, 'transaksi/transaksi.html',data)

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0
#create transaksi
class TransCreateViews(View):
    def get(self, request):
        data = {
            'edit': False,
        }
        return render(request, 'user/userview.html', data)
    def post(self, request):
        frm_saldo_keluar = to_float(request.POST.get("saldo_keluar", "0"))
        frm_saldo_masuk = to_float(request.POST.get("saldo_masuk", "0"))
        frm_jenis = request.POST.get('jenis')
        frm_tujuan = request.POST.get('tujuan')
        frm_ewallet = request.POST.get('ewallet')
        frm_bank = request.POST.get('bank')

        try:
            rekening = Rekening.objects.filter(akun=request.user).first()
            if rekening:
                with transaction.atomic():
                    # Siapkan data yang akan disimpan
                    data_transaksi = {
                        "rek": rekening,
                        "jenis": frm_jenis
                    }

                    if frm_jenis == "transfer":
                        data_transaksi["saldo_keluar"] = frm_saldo_keluar
                        if frm_tujuan == "ewallet":
                            data_transaksi["tujuan"] = frm_ewallet
                        elif frm_tujuan == "bank":
                            data_transaksi["tujuan"] = frm_bank
                    elif frm_jenis == "tarik_tunai":
                        data_transaksi["saldo_keluar"] = frm_saldo_keluar
                    else:
                        data_transaksi["saldo_masuk"] = frm_saldo_masuk

                    # Simpan transaksi ke database
                    Transaksi.objects.create(**data_transaksi)
                messages.success(request, f"Transaksi berhasil ditambahkan")
                return redirect('app:index_transaksi')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan Transaksi")
            return redirect('app:index_transaksi')
        
 #Edit Data       
class EditViews(View):
    def get(self, request, id_akun):
        try:
            akun = Master_User.objects.get(user_id=id_akun)
            data = {
                'akun_id': id_akun,
                'akun': akun,
            }
            return render(request, 'user/userview.html', data)
        except Master_User.DoesNotExist:
            messages.error(request, "Akun tidak ditemukan")
            return redirect('app:index_user')
    def post(self, request,  id_akun):
        frm_nama_lengkap = request.POST.get('full_name')
        frm_username = request.POST.get('username')
        frm_email = request.POST.get('email')
        frm_phone = request.POST.get('phone')
        frm_password = request.POST.get('password')

        try:
            
            with transaction.atomic():
                akun = Master_User.objects.get(user_id=id_akun)
                akun.full_name = frm_nama_lengkap
                akun.username = frm_username
                akun.email = frm_email
                akun.phone = frm_phone


                # Hanya set password jika password diinput
                if frm_password:
                    akun.set_password(frm_password)

                akun.save()

                messages.success(request, "Akun berhasil diubah")
                return redirect('app:index_user')

        except Master_User.DoesNotExist:
            messages.error(request, "Akun tidak ditemukan")
            return redirect('app:index_user')

        except Exception as e:
            print('Error:', e)
            messages.error(request, "Gagal mengubah akun")
            return redirect('app:index_user')
        
class TransHapusViews(View):
    def get(self, request, id_trans):
        try:
            trans = Rekening.objects.get(trans_id=id_trans)
            trans.deleted_at = timezone.now() #bikin arsip data, filter by deleted_at nya
            trans.save() 
            # trans.delete()
            messages.success(request, f"Transaksi berhasil dihapus")
        except Master_User.DoesNotExist:
            messages.error(request, "Transaksi tidak ditemukan")
        return redirect('app:index_transaksi')