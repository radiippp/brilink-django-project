from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import redirect, get_object_or_404, render
from django.db import transaction
from django.contrib import messages
from brilink_app.models import Transaksi, Rekening, Barang, Master_User
from decimal import Decimal
from django.utils.timezone import now, timedelta
from django.contrib import messages

class TransaksiViews(View):
    def get(self, request):
        user = request.user

        # default queryset
        transaksi = Transaksi.objects.none()

        # role filtering
        if user.is_superuser:
            transaksi = Transaksi.objects.all()
        elif user.role == "admin":
            staff_ids = Master_User.objects.filter(created_by=user).values_list("pk", flat=True)
            transaksi = Transaksi.objects.filter(dibuat_oleh__in=[user.pk, *staff_ids])
        elif user.role == "staff":
            if user.created_by:
                transaksi = Transaksi.objects.filter(dibuat_oleh__in=[user.pk, user.created_by])
            else:
                transaksi = Transaksi.objects.filter(dibuat_oleh=user)
        else:
            transaksi = Transaksi.objects.filter(created_by=user)

        # filter tanggal
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        filter_range = request.GET.get("filter_range")

        if filter_range == "today":
            transaksi = transaksi.filter(created_at__date=now().date())
        elif filter_range == "7days":
            transaksi = transaksi.filter(created_at__gte=now() - timedelta(days=7))
        elif filter_range == "1month":
            transaksi = transaksi.filter(created_at__gte=now() - timedelta(days=30))
        elif start_date and end_date:
            from datetime import datetime

            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()

                # validasi max 1 bulan
                if (end - start).days > 31:
                    messages.warning(request, "Rentang tanggal maksimal 1 bulan")
                else:
                    transaksi = transaksi.filter(created_at__date__range=[start, end])
            except ValueError:
                messages.error(request, "Format tanggal tidak valid")

        # rekening sesuai role
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

        data = {
            "transaksi": transaksi,
            "rekening": rekening,
            "barang": barang,
        }
        return render(request, "transaksi/transaksi.html", data)


@method_decorator(login_required(), name='dispatch')
class TransaksiCreateViews(View):
    def post(self, request):
        frm_jenis = request.POST.get("jenis")  # transfer / barang
        frm_rekening_sumber = request.POST.get("rekening_sumber")
        frm_rekening_tujuan = request.POST.get("rekening_tujuan")
        frm_barang = request.POST.get("barang")
        frm_jumlah = request.POST.get("jumlah")
        frm_qty = request.POST.get("qty")
        frm_keterangan = request.POST.get("keterangan")
        frm_dibuat = request.POST.get("dibuat_oleh")

        try:
            with transaction.atomic():
                tmp_user = get_object_or_404(Master_User, pk=frm_dibuat)
                rekening_sumber = None
                if frm_rekening_sumber:
                    rekening_sumber = get_object_or_404(Rekening, pk=frm_rekening_sumber)

                rekening_tujuan = get_object_or_404(Rekening, pk=frm_rekening_tujuan)

                barang = None
                if frm_barang:
                    barang = get_object_or_404(Barang, pk=frm_barang)

                transaksi = Transaksi.objects.create(
                    jenis=frm_jenis,
                    rekening_sumber=rekening_sumber,
                    rekening_tujuan=rekening_tujuan,
                    barang=barang,
                    jumlah=Decimal(frm_jumlah),
                    qty=int(frm_qty) if frm_qty else 0,
                    keterangan=frm_keterangan,
                    dibuat_oleh=tmp_user,  # siapa yang buat transaksi
                )

                # jalankan proses update saldo / stok
                transaksi.proses()

                messages.success(request, "Transaksi berhasil dibuat")
                return redirect("app:index_transaksi")

        except Exception as e:
            print("error transaksi:", e)
            messages.error(request, f"Gagal membuat transaksi: {e}")
            return redirect("app:index_transaksi")

class TransaksiHapusViews(View):
    def get(self, request, id_transaksi):
        try:
            trans = Transaksi.objects.get(transaksi_id=id_transaksi)
            trans.delete()
            messages.success(request, f"Transaksi berhasil dihapus")
        except Transaksi.DoesNotExist:
            messages.error(request, "Transaksi tidak ditemukan")
        return redirect('app:index_transaksi')