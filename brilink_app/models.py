from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import uuid
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import random , string
from decimal import Decimal




class CreateUpdateTime(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    archive_at = models.DateTimeField(default = None, null=True)
    deleted_at = models.DateTimeField(default = None, null=True)
    class Meta:
        abstract = True
        
class Tahun(models.Model):
    tahun = models.IntegerField(default=2024)
    class Meta:
        abstract = True

class Master_UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, phone, password, **extra_fields):
        values = [email, username, phone,]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))
        for field_name, value in field_value_map.items():
            if not value:
                raise ValueError('The {} value must be set'.format(field_name))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_verified', False)
        return self._create_user(email, username, phone, password, **extra_fields)

    def create_superuser(self, email, username, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_verified') is not True:
            raise ValueError('Superuser must have is_verified=True.')

        return self._create_user(email, username, phone, password, **extra_fields)
    
ROLE_CHOICES = [
    ('developer', 'Developer'),
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ]
    
"""TABEL AKUN UNTUK SELAIN BAWAANNYA DJANGO YANG DIPAKAI"""
class Master_User(AbstractBaseUser, CreateUpdateTime):
    user_id = models.TextField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, max_length=50)
    full_name = models.CharField(max_length=50)
    alamat = models.TextField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    # avatar = models.ImageField(blank=True, null=True, upload_to='images/avatar/', default='images/avatar/default_avatar.png')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='admin')
    created_by = models.CharField(max_length=255, blank=True, null=True)
    
    objects = Master_UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'role', 'is_superuser']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name
    

class Rekening(CreateUpdateTime):
    rek_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_rek = models.CharField(max_length=50)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    pemilik = models.ForeignKey(Master_User, on_delete=models.CASCADE, related_name="rekening")

    def __str__(self):
        return f"{self.nama_rek} - {self.pemilik.full_name}"
    
    

