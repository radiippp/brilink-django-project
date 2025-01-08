from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

class HomeViews(View):
    def get(self, request):
        return render(request, 'home/index_home.html')