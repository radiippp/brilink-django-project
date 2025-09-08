from datetime import timezone
from django.views import View
from brilink_app.models import  Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# @method_decorator(login_required(), name='dispatch')
# class RekViews(View):
#     def get(self, request):
#         rekening = Rekening.objects.all()
#         data ={
#             'rekening' : rekening,
#             }
#         return render(request, 'home/index_home.html',data)

# @method_decorator(login_required(), name='dispatch')
# class RekCreateViews(View):
#     def post(self, request):
#         frm_id_pemilik = request.POST.get('id_pemilik')
#         frm_saldo = request.POST.get('saldo_awal')

#         try:
#             tmp_user = get_object_or_404(Master_User, user_id=frm_id_pemilik)
#             with transaction.atomic():
#                 insert = Rekening.objects.create(
#                     akun=tmp_user,
#                     saldo=frm_saldo,
#                 )
#                 messages.success(request, f"Rekening berhasil ditambahkan")
#                 return redirect('app:index_home')

#         except Exception as e:
#             print('error akun:', e)
#             messages.error(request, "Gagal menambahkan Rekening")
#             return redirect('app:index_home')
        
# #  #Edit Data       
# # class EditViews(View):
# #     def get(self, request, id_akun):
# #         try:
# #             akun = Master_User.objects.get(user_id=id_akun)
# #             data = {
# #                 'akun_id': id_akun,
# #                 'akun': akun,
# #             }
# #             return render(request, 'user/userview.html', data)
# #         except Master_User.DoesNotExist:
# #             messages.error(request, "Akun tidak ditemukan")
# #             return redirect('app:index_user')
# #     def post(self, request,  id_akun):
# #         frm_nama_lengkap = request.POST.get('full_name')
# #         frm_username = request.POST.get('username')
# #         frm_email = request.POST.get('email')
# #         frm_phone = request.POST.get('phone')
# #         frm_password = request.POST.get('password')

# #         try:
            
# #             with transaction.atomic():
# #                 akun = Master_User.objects.get(user_id=id_akun)
# #                 akun.full_name = frm_nama_lengkap
# #                 akun.username = frm_username
# #                 akun.email = frm_email
# #                 akun.phone = frm_phone


# #                 # Hanya set password jika password diinput
# #                 if frm_password:
# #                     akun.set_password(frm_password)

# #                 akun.save()

# #                 messages.success(request, "Akun berhasil diubah")
# #                 return redirect('app:index_user')

# #         except Master_User.DoesNotExist:
# #             messages.error(request, "Akun tidak ditemukan")
# #             return redirect('app:index_user')

# #         except Exception as e:
# #             print('Error:', e)
# #             messages.error(request, "Gagal mengubah akun")
# #             return redirect('app:index_user')
        
# # class HapusViews(View):
# #     def get(self, request, id_akun):
# #         try:
# #             akun = Master_User.objects.get(user_id=id_akun)
# #             akun.deleted_at = timezone.now() #bikin arsip data, filter by deleted_at nya
# #             akun.save() 
# #             # akun.delete()
# #             messages.success(request, f"{akun.full_name} berhasil dihapus")
# #         except Master_User.DoesNotExist:
# #             messages.error(request, "Akun tidak ditemukan")
# #         return redirect('app:index_user')