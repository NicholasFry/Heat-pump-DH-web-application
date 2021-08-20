from django.urls import path, include 
from .views import *
# from .models import *
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='base'),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home')
]
