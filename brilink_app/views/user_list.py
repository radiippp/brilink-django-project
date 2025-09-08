from datetime import timezone
from django.forms import ValidationError
from django.views import View
from brilink_app.models import Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@method_decorator(login_required(), name='dispatch')
class UserViews(View):
    def get(self, request):
        if hasattr(request.user, "role") and request.user.role == "developer":
            user = Master_User.objects.all()
        elif request.user.role == "admin":
            user = Master_User.objects.filter(created_by=request.user.user_id)
        else:
            user = Master_User.objects.none()
        data ={
            'user' : user,
            }
        return render(request, 'user/userview.html',data)

@method_decorator(login_required(), name='dispatch')
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
        frm_created_by = request.POST.get('created_by')
        frm_role = request.POST.get('role')

        try:
            
            with transaction.atomic():
                insert = Master_User.objects.create_user(
                    email=frm_email,
                    username=frm_username,
                    phone=frm_phone,
                    password=frm_password,
                    full_name=frm_nama_lengkap,
                    role=frm_role,
                    created_by = frm_created_by
                )
                messages.success(request, f"Akun berhasil ditambahkan")
                return redirect('app:index_user')

        except Exception as e:
            print('error akun:', e)
            messages.error(request, "Gagal menambahkan akun")
            return redirect('app:index_user')
        
@method_decorator(login_required(), name='dispatch')
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

@method_decorator(login_required(), name='dispatch')        
class HapusViews(View):
    def get(self, request, id_akun):
        try:
            akun = Master_User.objects.get(user_id=id_akun)
            # akun.deleted_at = timezone.now() #bikin arsip data, filter by deleted_at nya
            # akun.save() 
            akun.delete()
            messages.success(request, f"{akun.full_name} berhasil dihapus")
        except Master_User.DoesNotExist:
            messages.error(request, "Akun tidak ditemukan")
        return redirect('app:index_user')
@method_decorator(login_required(), name='dispatch')        
class PermanenHapusViews(View):
    def get(self, request, id_akun):
        try:
            akun = Master_User.objects.get(user_id=id_akun) 
            akun.delete()
            messages.success(request, f"{akun.full_name} berhasil dihapus")
        except Master_User.DoesNotExist:
            messages.error(request, "Akun tidak ditemukan")
        return redirect('app:index_user')
    
@method_decorator(login_required(), name='dispatch')    
class ProfileViews(View):
    def get(self, request, id_akun):
        try:
            akun = Master_User.objects.get(user_id=id_akun)  
            data = {
                'akun_id': id_akun,
                'akun': akun,
            }
            return render(request, 'user/profile.html', data)
        except Master_User.DoesNotExist:
            messages.error(request, "Akun Tidak Ditemukan")
            return redirect('app:index_home')
    def post(self, request, id_akun):
        # Mengambil data dari POST untuk pembaruan profil
        frm_nama_lengkap = request.POST.get('full_name')
        frm_email = request.POST.get('email')
        frm_phone = request.POST.get('phone')
        frm_alamat = request.POST.get('alamat')
        # frm_avatar = request.FILES.get('avatar')
        
        # Mengambil data dari POST untuk pembaruan password
        frm_old_password = request.POST.get('old_password')
        frm_new_password = request.POST.get('new_password')
        frm_confirm_password = request.POST.get('confirm_password')

        try:
            with transaction.atomic():
                # Ambil data akun yang akan diupdate
                akun = get_object_or_404(Master_User, user_id=id_akun)

                # Update informasi profil pengguna
                akun.full_name = frm_nama_lengkap
                akun.email = frm_email
                akun.phone = frm_phone
                akun.alamat = frm_alamat
                # if frm_avatar:
                #     akun.avatar = frm_avatar

                # Validasi dan pembaruan password
                if frm_old_password and frm_new_password:
                    if not akun.check_password(frm_old_password):
                        messages.error(request, "Old password is incorrect.")
                    elif frm_new_password != frm_confirm_password:
                        messages.error(request, "New password and confirm password do not match.")
                    else:
                        # Jika validasi berhasil, set password baru
                        akun.set_password(frm_new_password)
                        update_session_auth_hash(request, akun)  # Menjaga sesi login tetap aktif

                # Simpan perubahan
                akun.save()
                messages.success(request, "Profile Telah Diubah.")
                return redirect('app:profile_user', id_akun=id_akun)

        except Master_User.DoesNotExist:
            messages.error(request, "Akun Tidak Ditemukan.")
            return redirect('app:index_home')

        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('app:index_home')

        except Exception as e:
            print("Error:", e)
            messages.error(request, "Gagal Mengubah Profil.")
            return redirect('app:index_home')