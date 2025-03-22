from datetime import timezone
from django.views import View
from brilink_app.models import Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


class UserViews(View):
    def get(self, request):
        user = Master_User.objects.all()
        data ={
            'user' : user,
            }
        return render(request, 'user/userview.html',data)

#create user
class CreateViews(View):
    def get(self, request):
        data = {
            'edit': False,
        }
        return render(request, 'user/userview.html', data)
    def post(self, request):
        frm_nama_lengkap = request.POST.get('full_name')
        frm_username = request.POST.get('username')
        frm_email = request.POST.get('email')
        frm_phone = request.POST.get('phone')
        frm_password = request.POST.get('password')

        try:
            
            with transaction.atomic():
                insert = Master_User.objects.create_user(
                    email=frm_email,
                    username=frm_username,
                    phone=frm_phone,
                    password=frm_password,
                    full_name=frm_nama_lengkap,
                )
                messages.success(request, f"Akun berhasil ditambahkan")
                return redirect('app:index_user')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan akun")
            return redirect('app:index_user')
        
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
        
class HapusViews(View):
    def get(self, request, id_akun):
        try:
            akun = Master_User.objects.get(user_id=id_akun)
            akun.deleted_at = timezone.now() #bikin arsip data, filter by deleted_at nya
            akun.save() 
            # akun.delete()
            messages.success(request, f"{akun.full_name} berhasil dihapus")
        except Master_User.DoesNotExist:
            messages.error(request, "Akun tidak ditemukan")
        return redirect('app:index_user')