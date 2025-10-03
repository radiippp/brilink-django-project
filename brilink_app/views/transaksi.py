from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import redirect, get_object_or_404, render
from django.db import transaction
from django.contrib import messages
from brilink_app.models import Transaksi, Rekening, Barang, Master_User, JenisTransaksi
from decimal import Decimal
from django.utils.timezone import now, timedelta
from django.contrib import messages
from brilink_app.decorators import *
import openpyxl
from django.http import HttpResponse

@method_decorator(login_required(), name='dispatch')
class ExportTransaksiExcelView(View):
    def get(self, request):
        user = request.user
        filter_range = request.GET.get("filter_range")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        # Ambil queryset sesuai filter (samakan dengan list transaksi kamu)
        transaksi = Transaksi.objects.none()

        # role filtering (sama persis dengan TransaksiViews)
        if user.is_superuser:
            transaksi = Transaksi.objects.all().order_by("-created_at")
        elif user.role == "admin":
            staff_ids = Master_User.objects.filter(created_by=user).values_list("pk", flat=True)
            transaksi = Transaksi.objects.filter(dibuat_oleh__in=[user.pk, *staff_ids]).order_by("-created_at")
        elif user.role == "staff":
            if user.created_by:
                transaksi = Transaksi.objects.filter(dibuat_oleh__in=[user.pk, user.created_by]).order_by("-created_at")
            else:
                transaksi = Transaksi.objects.filter(dibuat_oleh=user).order_by("-created_at")
        else:
            transaksi = Transaksi.objects.filter(created_by=user).order_by("-created_at")
        if filter_range:
            # logika filter sama persis dengan list transaksi
            pass  

        # Buat workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transaksi"

        # Header
        ws.append([
            "No", "Jenis", "Rekening Sumber", "Rekening Tujuan", "Barang",
            "Qty", "Jumlah", "Keterangan", "Tanggal", "Dibuat Oleh"
        ])

        # Data
        for idx, trx in enumerate(transaksi, start=1):
            ws.append([
                idx,
                trx.jenis.nama,
                trx.rekening_sumber.nama_rek if trx.rekening_sumber else "-",
                trx.rekening_tujuan.nama_rek,
                trx.barang.nama if trx.barang else "-",
                trx.qty,
                trx.jumlah,
                trx.keterangan,
                trx.created_at.strftime("%d-%m-%Y %H:%M"),
                trx.dibuat_oleh.full_name
            ])

        # 🔹 Tentukan nama file berdasarkan filter
        if start_date and end_date:
            filename_date = f"{start_date}-{end_date}"
        elif start_date:
            filename_date = start_date
        elif filter_range == "today":
            filename_date = now().strftime("%d-%m-%Y")
        elif filter_range == "7days":
            start = (now() - timedelta(days=7)).strftime("%d-%m-%Y")
            end = now().strftime("%d-%m-%Y")
            filename_date = f"{start}-{end}"
        elif filter_range == "1month":
            start = (now() - timedelta(days=30)).strftime("%d-%m-%Y")
            end = now().strftime("%d-%m-%Y")
            filename_date = f"{start}-{end}"
        else:
            filename_date = now().strftime("%d-%m-%Y")

        filename = f"transaksi_{filename_date}.xlsx"

        # Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename={filename}'
        wb.save(response)
        return response

@method_decorator(login_required(), name='dispatch')
class TransaksiViews(View):
    def get(self, request):
        user = request.user

        # default queryset
        transaksi = Transaksi.objects.none()
        filtered = False

        # role filtering
        if user.is_superuser:
            transaksi = Transaksi.objects.all().order_by("-created_at")
        elif user.role == "admin":
            staff_ids = Master_User.objects.filter(created_by=user).values_list("pk", flat=True)
            transaksi = Transaksi.objects.filter(dibuat_oleh__in=[user.pk, *staff_ids]).order_by("-created_at")
        elif user.role == "staff":
            if user.created_by:
                transaksi = Transaksi.objects.filter(dibuat_oleh__in=[user.pk, user.created_by]).order_by("-created_at")
            else:
                transaksi = Transaksi.objects.filter(dibuat_oleh=user).order_by("-created_at")
        else:
            transaksi = Transaksi.objects.filter(created_by=user).order_by("-created_at")

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

        if hasattr(request.user, "role") and request.user.role == "developer":
            jenis = JenisTransaksi.objects.all()
        elif request.user.role == "admin":
            jenis = JenisTransaksi.objects.filter(created_by=request.user.user_id)
        elif request.user.role == "staff":
            jenis = JenisTransaksi.objects.filter(created_by=request.user.created_by)
        else:
            jenis = JenisTransaksi.objects.none()

        if filter_range == "today":
            transaksi = transaksi.filter(created_at__date=now().date())
            filtered = True
        elif filter_range == "7days":
            transaksi = transaksi.filter(created_at__gte=now() - timedelta(days=7))
            filtered = True
        elif filter_range == "1month":
            transaksi = transaksi.filter(created_at__gte=now() - timedelta(days=30))
            filtered = True
        elif start_date and end_date:
            from datetime import datetime
            try:
                start = datetime.strptime(start_date, "%d/%m/%Y").date()
                end = datetime.strptime(end_date, "%d/%m/%Y").date()
                if (end - start).days > 31:
                    messages.warning(request, "Rentang tanggal maksimal 1 bulan")
                else:
                    transaksi = transaksi.filter(created_at__date__range=[start, end])
                    filtered = True
            except ValueError:
                messages.error(request, "Format tanggal tidak valid")

        data = {
            "transaksi": transaksi,
            "rekening": rekening,
            "barang": barang,
            "jenis": jenis,
            "filtered": filtered,  # kirim ke template
        }
        return render(request, "transaksi/transaksi.html", data)


@method_decorator(login_required(), name='dispatch')
class TransaksiCreateViews(View):
    def post(self, request):
        frm_jenis = request.POST.get("jenis")  # transfer / barang
        frm_rekening_sumber = request.POST.get("rekening_sumber")
        frm_rekening_tujuan = request.POST.get("rekening_tujuan")
        frm_rekening_tax = request.POST.get("rekening_tax")
        frm_barang = request.POST.get("barang")
        frm_jumlah = request.POST.get("jumlah")
        frm_qty = request.POST.get("qty")
        frm_tax = request.POST.get("tax")
        frm_keterangan = request.POST.get("keterangan")
        frm_dibuat = request.POST.get("dibuat_oleh")

        try:
            if not frm_rekening_tax:
                frm_rekening_tax = frm_rekening_tujuan


            with transaction.atomic():
                tmp_user = get_object_or_404(Master_User, pk=frm_dibuat)
                rekening_sumber = None
                if frm_rekening_sumber:
                    rekening_sumber = get_object_or_404(Rekening, pk=frm_rekening_sumber)

                rekening_tujuan = get_object_or_404(Rekening, pk=frm_rekening_tujuan)
                rekening_tax = get_object_or_404(Rekening, pk=frm_rekening_tax)
                tmp_jenis =  get_object_or_404(JenisTransaksi, pk=frm_jenis)

                barang = None
                if frm_barang:  # transaksi barang
                    barang = get_object_or_404(Barang, pk=frm_barang)
                    transaksi = Transaksi.objects.create(
                        jenis=tmp_jenis,
                        rekening_sumber=rekening_sumber,
                        rekening_tujuan=rekening_tujuan,
                        barang=barang,
                        qty=int(frm_qty) if frm_qty else 0,
                        keterangan=frm_keterangan,
                        dibuat_oleh=tmp_user,
                    )
                else :
                    transaksi = Transaksi.objects.create(
                        jenis=tmp_jenis,
                        tax=Decimal(frm_tax),
                        rekening_tax=rekening_tax,
                        rekening_sumber=rekening_sumber,
                        rekening_tujuan=rekening_tujuan,
                        jumlah=Decimal(frm_jumlah),
                        keterangan=frm_keterangan,
                        dibuat_oleh=tmp_user,
                    )
                transaksi.proses()

                messages.success(request, "Transaksi berhasil dibuat")
                return redirect("app:index_transaksi")

        except Exception as e:
            print("error transaksi:", e)
            messages.error(request, f"Gagal membuat transaksi: {e}")
            return redirect("app:index_transaksi")

@method_decorator(login_required(), name='dispatch')
@method_decorator(role_required(allowed_roles=['admin', 'developer']), name='dispatch')
class TransaksiHapusViews(View):
    def get(self, request, id_transaksi):
        try:
            trans = Transaksi.objects.get(transaksi_id=id_transaksi)
            trans.delete()
            messages.success(request, f"Transaksi berhasil dihapus")
        except Transaksi.DoesNotExist:
            messages.error(request, "Transaksi tidak ditemukan")
        return redirect('app:index_transaksi')