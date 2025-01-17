from django.views import View
from brilink_app.models import Master_User
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404


class UserViews(View):
    def get(self, request):
        user = Master_User.objects.all()
        data ={
            'user' : user,
            }
        return render(request, 'user/userview.html',data)
