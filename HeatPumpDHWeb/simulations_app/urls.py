from django.urls import path
from .views import *
# from .models import *
urlpatterns = [
    path('', RunSimulation.as_view(template_name='home.html'), name='home')
]
