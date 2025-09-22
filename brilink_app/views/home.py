from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from brilink_app.models import Master_User, Rekening, Transaksi,Barang,JenisTransaksi, Transaksi

from django.db.models import Count
from django.utils.safestring import mark_safe
import json
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta


@method_decorator(login_required(), name='dispatch')
class HomeViews(View):
    def get(self, request):
        user = request.user

        


        # default queryset
        transaksi = Transaksi.objects.none()

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

        today = now()
        bulan = int(request.GET.get("bulan", today.month))
        tahun = int(request.GET.get("tahun", today.year))

        # filter transaksi sesuai bulan & tahun
        transaksi = transaksi.filter(
            created_at__month=bulan,
            created_at__year=tahun
        ).order_by("-created_at")

        # hitung per jenis
        transaksi_per_jenis = transaksi.values("jenis__nama").annotate(total=Count("transaksi_id"))
        labels = [item["jenis__nama"] for item in transaksi_per_jenis]
        datachart = [item["total"] for item in transaksi_per_jenis]

        allowed_months = []
        for i in range(3):
            month_obj = (today.replace(day=1) - relativedelta(months=i))
            allowed_months.append({
                "month": month_obj.month,
                "year": month_obj.year,
                "label": month_obj.strftime("%B %Y")
            })
        

        data={
             'rekening' : rekening,
             "barang": barang,
            "jenis": jenis,
            "chart_labels": mark_safe(json.dumps(labels)),
            "chart_data": mark_safe(json.dumps(datachart)),
            "bulan": bulan,
            "tahun": tahun,
            "allowed_months": allowed_months,
        }
        return render(request, 'home/index_home.html',data)
        