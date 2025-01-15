from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# @method_decorator(login_required(), name='dispatch')
class HomeViews(View):
    def get(self, request):
        return render(request, 'home/index_home.html')