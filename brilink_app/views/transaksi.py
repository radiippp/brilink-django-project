from datetime import timezone
from django.views import View
from brilink_app.models import Transaksi, Master_User, Rekening
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from decimal import Decimal
from django.utils import timezone

@method_decorator(login_required(), name='dispatch')
class TransaksiViews(View):
    def get(self, request):
        rekening = Rekening.objects.filter(akun=request.user).first()

        transaksi = []
        if rekening:  # Hanya jalankan query jika rekening ditemukan
            transaksi = Transaksi.objects.filter(rek=rekening, deleted_at__isnull=True).order_by('-created_at')

        data = {
            'transaksi': transaksi,
        }
        return render(request, 'transaksi/transaksi.html',data)

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0
#create transaksi
@method_decorator(login_required(), name='dispatch')
class TransCreateViews(View):
    def post(self, request):
        frm_saldo_keluar = to_float(request.POST.get("saldo_keluar", "0"))
        frm_saldo_masuk = to_float(request.POST.get("saldo_masuk", "0"))
        frm_jenis = request.POST.get('jenis_transaksi')
        frm_tujuan = request.POST.get('tujuan_transaksi')
        frm_ewallet = request.POST.get('ewalle_tujuan')
        frm_bank = request.POST.get('bank_tujuan')
        frm_golongan = request.POST.get('golongan')
        print(frm_tujuan)
        print(frm_saldo_keluar)
        print(frm_jenis)

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
                    elif frm_jenis == "tiket_ferizy":
                        data_transaksi["saldo_keluar"] = frm_saldo_keluar
                        if frm_tujuan == "kendaraan":
                            data_transaksi["tujuan"] = frm_golongan
                        else:
                            data_transaksi["tujuan"] = frm_tujuan
                    elif frm_jenis == "isi_saldo":
                        data_transaksi["tujuan"] = "Rekening"
                        data_transaksi["saldo_masuk"] = frm_saldo_masuk
                    else:
                        messages.error(request, "Data Tidak boleh kosong, Gagal menambahkan Transaksi")
                        return redirect('app:index_transaksi')

                    # Simpan transaksi ke database
                    Transaksi.objects.create(**data_transaksi)
                messages.success(request, f"Transaksi berhasil ditambahkan")
                return redirect('app:index_transaksi')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan Transaksi")
            return redirect('app:index_transaksi')
        
 #Edit Data
@method_decorator(login_required(), name='dispatch')      
class TransEditViews(View):
    def get(self, request, id_trans):
        try:
            transaksi = Transaksi.objects.get(trans_id=id_trans)
            data = {
                'trans_id': id_trans,
                'transaksi' : transaksi,
            }
            return render(request, 'transaksi/transaksi.html', data)     
        except Transaksi.DoesNotExist:
            messages.error(request, "Transaksi tidak ditemukan")
            return redirect('app:index_transaksi')
        
@method_decorator(login_required(), name='dispatch')       
class TransHapusViews(View):
    def get(self, request, id_trans):
        trans = get_object_or_404(Transaksi, trans_id=id_trans)
        trans.deleted_at = timezone.now()  # Tandai sebagai dihapus
        trans.save()  # Jalankan logika soft delete
        messages.success(request, "Transaksi berhasil dibatalkan.")
        return redirect('app:index_transaksi')